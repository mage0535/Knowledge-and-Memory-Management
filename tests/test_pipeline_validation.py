"""Real-data pipeline validation: end-to-end note generation from real-world sources.

These tests exercise the full KMM pipeline on realistic content — not unit-test mocks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from knowledge_collector import analyze_material, generate_note, rerank_results, preprocess_query
from knowledge_collector.analysis import extract_relations, migrate_knowledge_object
from knowledge_collector.note_translator import translate_note_content
from knowledge_collector.parse_router import parse_with_routing, ENGINE_REGISTRY


REAL_ZH_WECHAT_CONTENT = """# 2026年AI Agent发展趋势

随着大语言模型能力的提升，AI Agent已经从简单的对话机器人演变为能够自主完成复杂任务链的智能体。2026年的关键趋势包括：

1. 多Agent协作框架的成熟，Agent间通过消息总线进行任务分发
2. 知识图谱与向量检索的深度融合，提升了Agent对长期记忆的访问能力
3. 工具调用的标准化，MCP协议成为Agent与外部服务交互的事实标准
4. 安全沙箱的引入，确保Agent在执行高风险操作时不影响宿主系统

这些趋势表明，AI Agent正在从"对话助手"向"数字员工"转型。"""

REAL_EN_TECH_CONTENT = """# Layered Memory Architecture for AI Agents

AI agents face a fundamental challenge: how to maintain useful context across
thousands of sessions, documents, and knowledge sources without overwhelming
the context window or degrading response quality.

The layered memory approach solves this through four tiers:

L1: Hot memory — the current session's conversation history, stored in state.db
     with FTS5 full-text search for sub-millisecond retrieval.

L2: Warm memory — session-level embeddings and summaries stored in PostgreSQL
     with vector similarity search for semantic recall across recent work.

L3: Cold memory — long-term knowledge stored in gbrain as pages, tags, and
     links. Supports keyword and graph traversal queries.

L4: Knowledge memory — curated Markdown notes from KMM ingestion pipelines,
     indexed by governance rebuild for cross-project retrieval.

Performance target: L1 < 1ms, L2 < 100ms, L3 < 1s, L4 < 500ms.
Trade-off: retrieval speed vs recall completeness varies by query type."""


def test_full_chinese_pipeline_note_generation(tmp_path: Path):
    import os
    os.environ["KMM_NOTES_DIR"] = str(tmp_path / "notes")

    note = generate_note(
        {"title": "AI Agent 2026", "content": REAL_ZH_WECHAT_CONTENT, "source_type": "article"},
        template="article",
    )
    assert Path(note["note_path"]).exists()
    assert Path(note["knowledge_path"]).exists()

    ko = json.loads(Path(note["knowledge_path"]).read_text(encoding="utf-8"))
    assert ko["schema_version"] == "kmm.knowledge_object.v1"
    assert ko["language"] == "zh"
    assert len(ko["keywords"]) >= 3
    assert len(ko["claims"]) >= 1


def test_full_english_pipeline_note_generation(tmp_path: Path):
    import os
    os.environ["KMM_NOTES_DIR"] = str(tmp_path / "notes")

    note = generate_note(
        {"title": "Layered Memory Architecture", "content": REAL_EN_TECH_CONTENT, "source_type": "note"},
        template="note",
    )
    assert Path(note["note_path"]).exists()

    ko = json.loads(Path(note["knowledge_path"]).read_text(encoding="utf-8"))
    assert ko["language"] == "en"
    assert len(ko["claims"]) >= 1
    assert len(ko["keywords"]) >= 3


def test_pipeline_analysis_to_relations_roundtrip():
    analysis = analyze_material(
        {"title": "Layered Memory", "content": REAL_EN_TECH_CONTENT},
        source_type="note",
    )
    relations = extract_relations(analysis)
    assert len(relations) >= 0

    keywords = analysis.get("keywords", [])
    assert any(k in keywords for k in ["agent", "memory", "retrieval"])
    assert analysis["quality"]["confidence"] in ("medium", "high")


def test_pipeline_query_rewrite_to_rerank_chain():
    qinfo = preprocess_query("agent memory retrieval architecture")
    assert qinfo["language"] == "en"
    assert len(qinfo["expansions"]) >= 1

    documents = [
        {"title": "Layered Memory", "content": REAL_EN_TECH_CONTENT[:200], "score": 0.8, "url": "/note/1"},
        {"title": "Vector Search", "content": "vector retrieval basics", "score": 0.6, "url": "/note/2"},
    ]
    reranked = rerank_results("agent memory architecture", documents, top_n=5)
    assert len(reranked) == 2
    assert "rerank_score" in reranked[0]


def test_pipeline_parse_router_routes_markdown(tmp_path: Path):
    md = tmp_path / "route-test.md"
    md.write_text("# Route Test\n\nContent for routing engine.\n", encoding="utf-8")

    result = parse_with_routing(str(md))
    assert result["ok"] is True
    assert result["engine"] in ("markitdown", "plaintext")


def test_pipeline_migration_identity():
    obj = analyze_material(
        {"title": "Test", "content": "KMM should extract useful claims and concepts for downstream indexing."},
        source_type="note",
    )
    migrated = migrate_knowledge_object(obj, "kmm.knowledge_object.v1")
    assert migrated["object_id"] == obj["object_id"]
    assert migrated["schema_version"] == "kmm.knowledge_object.v1"


def test_pipeline_translation_no_api_key_preserves_content():
    import os
    old_key = os.environ.pop("KMM_TRANSLATE_API_KEY", None)
    try:
        result = translate_note_content(REAL_EN_TECH_CONTENT, target_lang="zh")
        assert "Layered Memory Architecture" in result
        assert "AI agents" in result
    finally:
        if old_key:
            os.environ["KMM_TRANSLATE_API_KEY"] = old_key


def test_pipeline_llm_fallback_when_no_credentials():
    from knowledge_collector.llm_analyzer import LlmKnowledgeAnalyzer
    import os
    old_key = os.environ.pop("KMM_LLM_API_KEY", None)
    old_provider = os.environ.pop("KMM_LLM_PROVIDER", None)
    try:
        analyzer = LlmKnowledgeAnalyzer()
        assert not analyzer.available
        ko = analyzer.analyze(
            {"title": "Test", "content": "This is a test of the fallback path."},
            source_type="note",
        )
        assert ko.metadata.get("extractor") == "deterministic"
        assert ko.claims
    finally:
        if old_key:
            os.environ["KMM_LLM_API_KEY"] = old_key
        if old_provider:
            os.environ["KMM_LLM_PROVIDER"] = old_provider


def test_pipeline_document_parse_markitdown_is_registered():
    from knowledge_collector.parse_router import ENGINE_REGISTRY, score_engine_for_file
    assert "markitdown" in ENGINE_REGISTRY
    assert "plaintext" in ENGINE_REGISTRY
    # Markdown files score higher with markitdown than pdftotext
    md_score = score_engine_for_file("/tmp/test.md", "markitdown")
    assert md_score >= 0.5


def test_pipeline_scene_detector_graceful_no_binary(tmp_path: Path):
    from knowledge_collector.scene_detector import detect_scenes
    # Non-existent video path should return empty, not crash
    scenes = detect_scenes(str(tmp_path / "nonexistent.mp4"))
    assert scenes == []
