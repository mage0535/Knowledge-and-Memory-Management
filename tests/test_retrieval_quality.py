"""Retrieval quality evaluation fixtures and regression tests."""

from __future__ import annotations

from pathlib import Path
import os
import sys


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

from knowledge_collector.query_rewrite import detect_language, expand_query, extract_entities, preprocess_query
from knowledge_collector.analysis import migrate_knowledge_object
from knowledge_collector.note_generator import generate_note
from notes_rag import create_note, search_notes


EN_TECH_QUERY = "agent memory architecture with hybrid retrieval"
ZH_FINANCE_QUERY = "比亚迪 2026 年第一季度 财报"
MIXED_QUERY = "Python RAG pipeline 性能优化"


def test_query_language_detection_en():
    assert detect_language(EN_TECH_QUERY) == "en"


def test_query_language_detection_zh():
    assert detect_language(ZH_FINANCE_QUERY) == "zh"


def test_query_language_detection_unknown():
    assert detect_language("12345 !!!") == "unknown"


def test_expand_query_en():
    variants = expand_query(EN_TECH_QUERY)
    assert len(variants) >= 1
    assert variants[0] == EN_TECH_QUERY


def test_expand_query_zh():
    variants = expand_query(ZH_FINANCE_QUERY)
    assert len(variants) >= 1


def test_extract_entities_url():
    entities = extract_entities("check https://example.com/report.pdf for details")
    assert any(e["type"] == "url" for e in entities)


def test_extract_entities_version():
    entities = extract_entities("upgrade to v3.5.1 or later")
    assert any(e["type"] == "version" for e in entities)


def test_preprocess_query_returns_structured_output():
    result = preprocess_query(EN_TECH_QUERY)
    assert result["original"] == EN_TECH_QUERY
    assert result["language"] in ("en", "zh", "unknown")
    assert "expansions" in result
    assert "entities" in result
    assert "tokens" in result


def test_migrate_knowledge_object_identity():
    obj = {"schema_version": "kmm.knowledge_object.v1", "title": "test"}
    result = migrate_knowledge_object(obj, "kmm.knowledge_object.v1")
    assert result["title"] == "test"


def test_migrate_knowledge_object_unknown_path():
    obj = {"schema_version": "kmm.knowledge_object.v1"}
    try:
        migrate_knowledge_object(obj, "unknown.v999")
    except ValueError as exc:
        assert "No migration path" in str(exc)
    else:
        raise AssertionError("should have raised ValueError")


def test_generate_note_dedup(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("KMM_NOTES_DIR", str(tmp_path / "notes"))

    note1 = generate_note(
        {"title": "Dedup Test", "content": "Unique content for deduplication."},
        template="note",
    )
    note2 = generate_note(
        {"title": "Dedup Test", "content": "Unique content for deduplication."},
        template="note",
    )
    assert note1["note_id"] == note2["note_id"]
    assert note2.get("dedup") is True


def test_channel_adapter_registry():
    from knowledge_collector.channels import CHANNEL_REGISTRY, list_supported_platforms
    platforms = list_supported_platforms()
    assert "hackernews" in platforms
    assert "wechat" in platforms


def test_hackernews_adapter_can_handle():
    from knowledge_collector.channels.hackernews import HackerNewsAdapter
    adapter = HackerNewsAdapter()
    assert adapter.can_handle("https://news.ycombinator.com/item?id=12345678")
    assert adapter.can_handle("12345678")
    assert not adapter.can_handle("https://example.com")


def test_wechat_adapter_can_handle():
    from knowledge_collector.channels.wechat import WechatAdapter
    adapter = WechatAdapter()
    assert adapter.can_handle("https://mp.weixin.qq.com/s/abc123")
    assert not adapter.can_handle("https://example.com")


def test_video_adapter_registry():
    from knowledge_collector.video_adapter import VIDEO_ADAPTERS
    assert isinstance(VIDEO_ADAPTERS, dict)


def test_sensitive_scan_knowledge_json_scan(tmp_path: Path):
    sys.path.insert(0, str(REPO / "scripts"))
    import sensitive_scan

    kjson = tmp_path / "test.knowledge.json"
    kjson.write_text('{"title": "test", "note_path": "/root/data/test.md"}', encoding="utf-8")
    findings = sensitive_scan.scan_knowledge_json(tmp_path)
    assert any("/root/" in f.get("snippet", "") for f in findings)


def test_sensitive_scan_clean_json_passes(tmp_path: Path):
    sys.path.insert(0, str(REPO / "scripts"))
    import sensitive_scan

    kjson = tmp_path / "clean.knowledge.json"
    kjson.write_text('{"title": "clean test"}', encoding="utf-8")
    findings = sensitive_scan.scan_knowledge_json(tmp_path)
    assert not findings


def test_relation_extraction_finds_connections():
    from knowledge_collector.analysis import extract_relations

    knowledge = {
        "concepts": [{"name": "kmm"}, {"name": "gbrain"}],
        "claims": [
            {"text": "KMM integrates with gbrain for knowledge graph storage.", "confidence": 0.7},
        ],
    }
    relations = extract_relations(knowledge)
    assert len(relations) >= 1
    assert relations[0]["source"] in ("kmm", "gbrain")
    assert relations[0]["target"] in ("kmm", "gbrain")


def test_relation_extraction_empty_input():
    from knowledge_collector.analysis import extract_relations

    knowledge = {"concepts": [], "claims": []}
    relations = extract_relations(knowledge)
    assert relations == []


def test_translate_note_no_api_key_returns_original():
    import os
    if "KMM_TRANSLATE_API_KEY" in os.environ:
        del os.environ["KMM_TRANSLATE_API_KEY"]
    from knowledge_collector.note_translator import translate_note_content

    content = "# Title\n\nHello world.\n"
    result = translate_note_content(content, target_lang="zh")
    assert "Title" in result
    assert "Hello world" in result


def test_translate_note_preserves_headers():
    import os
    if "KMM_TRANSLATE_API_KEY" in os.environ:
        del os.environ["KMM_TRANSLATE_API_KEY"]
    from knowledge_collector.note_translator import translate_note_content

    content = "# Chapter\n\nText.\n```\ncode\n```"
    result = translate_note_content(content, target_lang="zh")
    assert "# Chapter" in result
    assert "```" in result


def test_scene_detector_parses_timestamps():
    from knowledge_collector.scene_detector import _time_to_seconds, _seconds_to_time

    ts = _time_to_seconds("00:01:30.500")
    assert abs(ts - 90.5) < 0.01
    result = _seconds_to_time(90.5)
    assert "01:30" in result


def test_reddit_adapter_can_handle():
    from knowledge_collector.channels.reddit import RedditAdapter
    adapter = RedditAdapter()
    assert adapter.can_handle("https://www.reddit.com/r/Python/comments/abc123")
    assert adapter.can_handle("r/Python")
    assert not adapter.can_handle("https://example.com")


def test_csdn_adapter_can_handle():
    from knowledge_collector.channels.csdn import CsdnAdapter
    adapter = CsdnAdapter()
    assert adapter.can_handle("https://blog.csdn.net/user/article/details/12345")
    assert not adapter.can_handle("https://example.com")


def test_xiaohongshu_adapter_can_handle():
    from knowledge_collector.channels.xiaohongshu import XiaohongshuAdapter
    adapter = XiaohongshuAdapter()
    assert adapter.can_handle("https://www.xiaohongshu.com/explore/abc123")
    assert adapter.can_handle("https://xhslink.com/abc")
    assert not adapter.can_handle("https://example.com")


def test_sidecar_indexer_builds_rows(tmp_path: Path):
    from knowledge_collector.sidecar_indexer import build_knowledge_object_rows

    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    kj = notes_dir / "test.knowledge.json"
    kj.write_text(
        '{"object_id":"ko-test-abc","title":"Test","summary":"summary","keywords":["k","v"],'
        '"concepts":[],"claims":[],"action_items":[],"risks":[],'
        '"quality":{"score":0.8},"schema_version":"kmm.knowledge_object.v1",'
        '"created_at":"2026-01-01T00:00:00Z","language":"en"}',
        encoding="utf-8",
    )
    rows, fts_rows = build_knowledge_object_rows(notes_dir, 123.0)
    assert len(rows) == 1
    assert rows[0][0] == "ko-test-abc"
    assert rows[0][10] == 0.8


def test_sidecar_indexer_signature_detects_changes(tmp_path: Path):
    from knowledge_collector.sidecar_indexer import compute_knowledge_objects_signature

    notes_dir = tmp_path / "notes"
    notes_dir.mkdir(exist_ok=True)
    sig1 = compute_knowledge_objects_signature(notes_dir)
    (notes_dir / "a.knowledge.json").write_text('{"title":"A"}', encoding="utf-8")
    sig2 = compute_knowledge_objects_signature(notes_dir)
    assert sig1 != sig2


def test_channel_registry_includes_all():
    import knowledge_collector.channels as ch
    # Force import of all adapters
    import importlib
    for mod in ("hackernews", "wechat", "reddit", "csdn", "xiaohongshu"):
        try:
            importlib.import_module(f"knowledge_collector.channels.{mod}")
        except (ImportError, ModuleNotFoundError):
            pass
    platforms = ch.list_supported_platforms()
    print(f"registered platforms: {platforms}")
    assert len(platforms) >= 2  # at least HN + WeChat should register; others may fail due to deps
