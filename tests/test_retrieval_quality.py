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
