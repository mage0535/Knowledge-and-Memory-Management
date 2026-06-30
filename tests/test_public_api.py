from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import sqlite3


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from cloud_sync import on_pre_sync
from knowledge_collector import analyze_material, collect_article, collect_book, collect_document, collect_video, generate_note, on_collect
from notes_rag import create_note, search_notes
from knowledge_collector import web as web_module
from knowledge_augmentation import AugmentationConfig
from knowledge_augmentation.augmented_search import AugmentedSearch


class DummyResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        return None


def test_public_hooks_are_importable():
    assert on_collect({})["module"] == "knowledge_collector"
    assert on_pre_sync({})["status"] == "ready"


def test_plugin_manifest_uses_runtime_import_paths():
    manifest = (REPO / "plugin.yaml").read_text(encoding="utf-8")
    assert 'post-collect: "knowledge_collector.on_collect"' in manifest
    assert 'pre-sync: "cloud_sync.on_pre_sync"' in manifest


def test_generate_and_search_note_round_trip(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("KMM_NOTES_DIR", str(tmp_path / "notes"))

    note = create_note("Agent Memory Architecture", "Layered memory design", domain="shared")
    results = search_notes("layered memory", domains=["shared"])

    assert Path(note["note_path"]).exists()
    assert results
    assert results[0]["source"] == "local_note"


def test_knowledge_analysis_layer_extracts_useful_objects():
    analysis = analyze_material(
        {
            "title": "Layered Recall",
            "content": (
                "Layered recall is a memory architecture. "
                "It should preserve source provenance and reduce missing context risk. "
                "Next, index claims and concepts for retrieval in 2026."
            ),
            "source_ref": "memory://example",
        },
        source_type="note",
    )

    assert analysis["schema_version"] == "kmm.knowledge_object.v1"
    assert analysis["object_id"].startswith("ko-layered-recall-")
    assert "layered" in analysis["keywords"]
    assert analysis["claims"]
    assert analysis["action_items"]
    assert analysis["risks"]
    assert analysis["timeline"]
    assert analysis["quality"]["confidence"] in {"medium", "high"}


def test_augmented_search_honors_local_first_false(monkeypatch):
    cfg = AugmentationConfig(local_first=False, anysearch_api_key="dummy")
    searcher = AugmentedSearch(config=cfg)
    monkeypatch.setattr(searcher, "_search_web", lambda query, domain="", domains=None, local_hint=None: [{"source": "anysearch/finance", "title": "web", "content": "remote", "score": 0.7, "url": "x"}])

    result = searcher.search("earnings", domain="finance")

    assert result["source"] == "web"
    assert result["augmented"] is True
    assert result["results"][0]["source"] == "anysearch/finance"


def test_augmented_search_uses_domain_mapping(monkeypatch):
    cfg = AugmentationConfig(anysearch_api_key="dummy")
    searcher = AugmentedSearch(config=cfg)
    captured = []

    def fake_search(query, domain="", max_results=10, **kwargs):
        captured.append(domain)
        return []

    monkeypatch.setattr(searcher, "_search_local", lambda query: [])
    monkeypatch.setattr(searcher, "_score_local", lambda results: 0.0)
    monkeypatch.setattr(searcher, "_get_anysearch", lambda: type("Client", (), {"search": staticmethod(fake_search)})())

    searcher.search("policy memo", domain="policy")

    assert captured == ["legal"]


def test_notes_rag_prefers_fts_when_available(monkeypatch, tmp_path: Path):
    state_db = tmp_path / "state.db"
    conn = sqlite3.connect(str(state_db))
    try:
        conn.execute("CREATE TABLE sessions (id TEXT PRIMARY KEY, title TEXT, started_at REAL)")
        conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, session_id TEXT, content TEXT)")
        conn.execute("CREATE VIRTUAL TABLE messages_fts USING fts5(content)")
        conn.execute("INSERT INTO sessions VALUES ('s1', 'Session One', 1.0)")
        conn.execute("INSERT INTO messages VALUES (1, 's1', 'agent memory architecture details')")
        conn.execute("INSERT INTO messages_fts(rowid, content) VALUES (1, 'agent memory architecture details')")
        conn.commit()
    finally:
        conn.close()

    monkeypatch.setenv("AGENT_HOME", str(tmp_path))
    sys.path.insert(0, str(REPO / "src"))
    from notes_rag import NotesRAGManager

    results = NotesRAGManager()._search_state_db("agent memory architecture")

    assert results
    assert results[0]["source"] == "state_db"


def test_notes_rag_search_parallel_fusion(monkeypatch):
    sys.path.insert(0, str(REPO / "src"))
    from notes_rag import NotesRAGManager

    manager = NotesRAGManager()
    monkeypatch.setattr(manager, "_search_local_markdown", lambda query, domains=None: [{"title": "local", "content": "a", "score": 1.0, "url": "u1", "source": "local_note"}])
    monkeypatch.setattr(manager, "_search_state_db", lambda query: [{"title": "state", "content": "b", "score": 0.7, "url": "u2", "source": "state_db"}])
    monkeypatch.setattr(manager, "_search_hindsight", lambda query: [{"title": "hs", "content": "c", "score": 0.4, "url": "u3", "source": "hindsight"}])
    monkeypatch.setattr(manager, "_search_gbrain", lambda query: [{"title": "gb", "content": "d", "score": 0.3, "url": "u4", "source": "gbrain"}])

    results = manager.search("agent memory")

    assert [item["source"] for item in results[:4]] == ["local_note", "state_db", "hindsight", "gbrain"]


def test_collect_web_uses_structured_note_pipeline(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("KMM_NOTES_DIR", str(tmp_path / "notes"))
    monkeypatch.setattr(
        web_module.requests,
        "get",
        lambda url, timeout=20, headers=None: DummyResponse(
            "<html><head><title>Example</title></head><body><article>Useful public content for collection.</article></body></html>"
        ),
    )

    result = web_module.collect_web("https://example.com/test")

    assert result.title == "Example"
    assert Path(result.note_path).exists()
    note_text = Path(result.note_path).read_text(encoding="utf-8")
    assert "Useful public content" in note_text
    assert "## Executive Summary" in note_text
    knowledge_path = Path(result.note_path).with_suffix(".knowledge.json")
    assert knowledge_path.exists()


def test_collect_article_supports_url_and_keyword_modes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("KMM_NOTES_DIR", str(tmp_path / "notes"))
    monkeypatch.setattr(
        web_module.requests,
        "get",
        lambda url, timeout=20, headers=None: DummyResponse(
            "<html><head><title>Article</title></head><body><p>Collected article body.</p></body></html>"
        ),
    )

    from_url = collect_article("wechat", "https://example.com/a")
    from_keyword = collect_article("wechat", "weekly digest")

    assert from_url.source_type == "article"
    assert Path(from_url.note_path).exists()
    assert from_keyword.source_type == "article"
    assert "weekly digest" in Path(from_keyword.note_path).read_text(encoding="utf-8")


def test_collect_video_creates_structured_capture_note(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("KMM_NOTES_DIR", str(tmp_path / "notes"))

    result = collect_video("https://www.youtube.com/watch?v=abc123")

    assert result.metadata["video_id"] == "abc123"
    assert Path(result.note_path).exists()


def test_collect_document_falls_back_to_local_content(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("KMM_NOTES_DIR", str(tmp_path / "notes"))
    doc = tmp_path / "sample.md"
    doc.write_text("Structured document content\n", encoding="utf-8")

    result = collect_document(str(doc))

    assert result.source_type == "document"
    assert Path(result.note_path).exists()


def test_collect_book_reports_missing_refinement_script(monkeypatch, tmp_path: Path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("fake", encoding="utf-8")
    monkeypatch.setenv("BOOK_TO_SKILL", str(tmp_path / "missing.py"))

    result = collect_book(str(pdf_path))

    assert "book_to_skill" in result["error"]


def test_generate_note_requires_content(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("KMM_NOTES_DIR", str(tmp_path / "notes"))

    try:
        generate_note({"title": "Empty", "content": ""})
    except ValueError as exc:
        assert "content" in str(exc)
    else:
        raise AssertionError("empty content should fail")


def test_generate_note_writes_knowledge_sidecar(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("KMM_NOTES_DIR", str(tmp_path / "notes"))

    note = generate_note(
        {
            "title": "Structured Capture",
            "content": "KMM should extract claims, concepts, and action items from source content.",
            "tags": ["kmm"],
        },
        template="note",
    )

    note_path = Path(note["note_path"])
    knowledge_path = Path(note["knowledge_path"])
    assert note_path.exists()
    assert knowledge_path.exists()
    assert note["analysis"]["schema_version"] == "kmm.knowledge_object.v1"
    text = note_path.read_text(encoding="utf-8")
    assert "## Claims And Evidence" in text
    assert "knowledge_object" in text


def test_uninstall_preserves_knowledge_data():
    uninstall = REPO / "uninstall.sh"
    content = uninstall.read_text(encoding="utf-8")

    assert 'rm -rf "${HOME}/.hermes/knowledge"' not in content
    assert "知识数据默认保留" in content


def test_refinement_reports_missing_book_to_skill(monkeypatch, tmp_path: Path):
    sys.path.insert(0, str(REPO / "src"))
    from knowledge_collector.refinement import refine_pdf

    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("fake", encoding="utf-8")
    monkeypatch.setenv("BOOK_TO_SKILL", str(tmp_path / "missing.py"))

    result = refine_pdf(str(pdf_path), slug="sample")

    assert "book_to_skill" in result["error"]
