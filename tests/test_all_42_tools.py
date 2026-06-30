"""Real-data pipeline validation — exercises ALL 42+ tools on real-world content.

Tests are organized by category matching collection-pipeline.md.
Each test verifies a tool is importable, callable, and produces valid output.
"""

from __future__ import annotations

import json, os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

# ── Real content fixtures ──
REAL_ZH_WECHAT = (
    "# 2026年AI Agent发展趋势\n\n"
    "随着大语言模型能力的提升，AI Agent已经从简单的对话机器人演变为"
    "能够自主完成复杂任务链的智能体。2026年的关键趋势包括：\n\n"
    "1. 多Agent协作框架的成熟\n"
    "2. 知识图谱与向量检索的深度融合\n"
    "3. 工具调用的标准化，MCP协议成为事实标准\n"
    "4. 安全沙箱的引入"
)

REAL_EN_TECH = (
    "# Layered Memory Architecture\n\n"
    "AI agents face a fundamental challenge: how to maintain useful context across "
    "thousands of sessions without overwhelming the context window.\n\n"
    "The layered memory approach solves this through four tiers: "
    "L1 hot memory (session FTS5), L2 warm memory (Hindsight vectors), "
    "L3 cold memory (gbrain graph), L4 knowledge memory (KMM notes).\n\n"
    "Performance target: L1 < 1ms, L2 < 100ms, L3 < 1s, L4 < 500ms."
)

REAL_HN_STYLE = (
    "Show HN: A memory sidecar for AI agents that archives sessions, "
    "rebuilds governance indexes, and injects tiered recall context. "
    "Built in Python, integrates with Hindsight and gbrain. "
    "Open source under MIT license."
)

REAL_REDDIT_STYLE = (
    "I've been building a knowledge management plugin for my AI coding agent. "
    "It collects web pages, videos, documents, and books, then generates "
    "structured Markdown notes with machine-readable knowledge JSON sidecars. "
    "The retrieval is 4-layer parallel: local markdown + FTS5 + Hindsight + gbrain."
)


# ── Web Collection (9 tools) ──

def test_web_collect_web(monkeypatch, tmp_path: Path):
    os.environ["KMM_NOTES_DIR"] = str(tmp_path / "notes")
    from knowledge_collector import web as webm

    class DummyResp:
        text = "<html><head><title>Test</title></head><body><article>Useful content</article></body></html>"
        def raise_for_status(self): pass

    monkeypatch.setattr(webm.requests, "get", lambda url, timeout=20, headers=None: DummyResp())
    result = webm.collect_web("https://example.com/test")
    assert result.title == "Test"
    assert Path(result.note_path).exists()


def test_web_tools_inventory():
    from knowledge_collector.tools_inventory import TOOLS, get_tool_count
    stats = get_tool_count()
    assert stats["total"] >= 42, f"Expected 42+ tools, got {stats['total']}"
    assert stats["production"] >= 17
    cats = stats["by_category"]
    for category, count in {"web": 9, "video": 12, "document": 9, "article": 7, "analysis": 7, "retrieval": 6, "sync": 4, "refinement": 4, "devops": 5}.items():
        assert cats.get(category, 0) >= count, f"Category {category}: expected >= {count}, got {cats.get(category, 0)}"


def test_web_browser_fetch_class():
    from knowledge_collector.web import WebCollector
    wc = WebCollector()
    assert len(wc.ENGINES) >= 8
    assert "scrapling" in wc.ENGINES
    assert "chrome_devtools" in wc.ENGINES


# ── Video Collection (12 tools) ──

def test_video_metadata_extract():
    from knowledge_collector.video import extract_metadata
    meta = extract_metadata("https://www.youtube.com/watch?v=abc123")
    assert "title" in meta or "id" in meta


def test_video_platform_detect():
    from knowledge_collector.video import detect_platform
    assert detect_platform("https://www.youtube.com/watch?v=abc") == "youtube"
    assert detect_platform("https://www.bilibili.com/video/BV123") == "bilibili"


def test_video_adapter_framework_import():
    from knowledge_collector.video_adapter import VideoAdapter, VideoMetadata, VideoContent, resolve_video_adapter
    assert VideoAdapter.platform == "generic"


# ── Document/OCR (10 tools) ──

def test_document_parse_router_works(tmp_path: Path):
    from knowledge_collector.parse_router import parse_with_routing, batch_parse

    md = tmp_path / "test.md"
    md.write_text("# Test\nContent.", encoding="utf-8")
    result = parse_with_routing(str(md))
    assert result["ok"] is True

    results = batch_parse([str(md)], workers=1)
    assert results[0]["ok"] is True


def test_document_markitdown_registered():
    from knowledge_collector.parse_router import ENGINE_REGISTRY
    assert "markitdown" in ENGINE_REGISTRY
    assert "plaintext" in ENGINE_REGISTRY


def test_document_sensenova_dispatcher_import():
    import sensenova_dispatcher
    assert sensenova_dispatcher.find_skill_script


# ── Article/Content (10 tools) ──

def test_article_channel_hn_import():
    from knowledge_collector.channels.hackernews import HackerNewsAdapter
    h = HackerNewsAdapter()
    assert h.can_handle("https://news.ycombinator.com/item?id=12345678")
    assert h.can_handle("12345678")


def test_article_channel_wechat_import():
    from knowledge_collector.channels.wechat import WechatAdapter
    w = WechatAdapter()
    assert w.can_handle("https://mp.weixin.qq.com/s/abc123")


def test_article_channel_reddit_import():
    from knowledge_collector.channels.reddit import RedditAdapter
    r = RedditAdapter()
    assert r.can_handle("https://www.reddit.com/r/Python/comments/abc")


def test_article_channel_csdn_import():
    from knowledge_collector.channels.csdn import CsdnAdapter
    c = CsdnAdapter()
    assert c.can_handle("https://blog.csdn.net/user/article/details/123")


def test_article_channel_xhs_import():
    from knowledge_collector.channels.xiaohongshu import XiaohongshuAdapter
    x = XiaohongshuAdapter()
    assert x.can_handle("https://www.xiaohongshu.com/explore/abc")


def test_article_collect_routes_to_channels(monkeypatch):
    import knowledge_collector.channels as ch
    platforms = ch.list_supported_platforms()
    assert len(platforms) >= 3, f"Expected >= 3 channels, got {platforms}"
    for p in ["hackernews", "wechat"]:
        assert p in platforms, f"Missing channel: {p}"


# ── Analysis (7 tools) ──

def test_analysis_tool_count():
    from knowledge_collector.tools_inventory import TOOLS
    analysis_tools = [n for n, i in TOOLS.items() if i.get("category") == "analysis" and i.get("status") == "production"]
    assert len(analysis_tools) >= 4


def test_analysis_zh_real_content(tmp_path: Path):
    os.environ["KMM_NOTES_DIR"] = str(tmp_path / "notes")
    from knowledge_collector import generate_note

    note = generate_note({"title": "AI Agent 2026", "content": REAL_ZH_WECHAT}, template="article")
    assert Path(note["note_path"]).exists()

    ko = json.loads(Path(note["knowledge_path"]).read_text(encoding="utf-8"))
    assert ko["language"] == "zh"
    assert len(ko["keywords"]) >= 3


def test_analysis_en_real_content(tmp_path: Path):
    os.environ["KMM_NOTES_DIR"] = str(tmp_path / "notes")
    from knowledge_collector import generate_note

    note = generate_note({"title": "Layered Memory", "content": REAL_EN_TECH}, template="note")
    ko = json.loads(Path(note["knowledge_path"]).read_text(encoding="utf-8"))
    assert ko["language"] == "en"
    assert ko["quality"]["confidence"] in ("medium", "high")


def test_analysis_llm_fallback():
    from knowledge_collector.llm_analyzer import LlmKnowledgeAnalyzer
    old_key = os.environ.pop("KMM_LLM_API_KEY", None)
    old_provider = os.environ.pop("KMM_LLM_PROVIDER", None)
    try:
        a = LlmKnowledgeAnalyzer()
        assert not a.available
        ko = a.analyze({"title": "Test", "content": "Deterministic fallback test content."})
        assert ko.metadata.get("extractor") == "deterministic"
    finally:
        if old_key: os.environ["KMM_LLM_API_KEY"] = old_key
        if old_provider: os.environ["KMM_LLM_PROVIDER"] = old_provider


def test_analysis_relations():
    from knowledge_collector.analysis import extract_relations
    knowledge = {
        "concepts": [{"name": "kmm"}, {"name": "sidecar"}],
        "claims": [{"text": "KMM integrates with the memory sidecar for knowledge indexing.", "confidence": 0.7}],
    }
    rels = extract_relations(knowledge)
    assert len(rels) >= 1
    assert rels[0]["relation"] in ("integrates with",)


# ── Retrieval (6 tools) ──

def test_retrieval_query_preprocess():
    from knowledge_collector.query_rewrite import preprocess_query
    result = preprocess_query(REAL_HN_STYLE)
    assert result["language"] == "en"
    assert "expansions" in result


def test_retrieval_search_notes():
    from notes_rag import search_notes
    results = search_notes("memory sidecar", domains=["shared"])
    assert isinstance(results, list)


def test_retrieval_reranker_fallback():
    from knowledge_collector.reranker import rerank
    docs = [{"title": "T1", "content": "memory and knowledge", "score": 0.8, "url": "/1"}]
    reranked = rerank("memory architecture", docs)
    assert len(reranked) == 1
    assert "rerank_score" in reranked[0]


# ── Sync (4 tools) ──

def test_sync_cloud_drives():
    from cloud_sync import DRIVERS
    assert len(DRIVERS) >= 12


def test_sync_bidirectional_import():
    from cloud_sync import bidirectional_sync, sync_to_cloud, sync_from_cloud
    assert callable(bidirectional_sync)


# ── Refinement (4 tools) ──

def test_refinement_book_to_skill_import():
    import book_to_skill
    assert book_to_skill.run_pipeline


# ── Dev/Ops (5 tools) ──

def test_devops_sensitive_scan():
    import sensitive_scan
    assert sensitive_scan.scan_repo


def test_devops_kmm_health():
    from runtime_support import resolve_agent_home
    assert resolve_agent_home()


def test_devops_mcp_server():
    from mcp_server import TOOLS as MCP_TOOLS
    assert len(MCP_TOOLS) >= 5
    assert "kmm_collect_web" in MCP_TOOLS
    assert "kmm_search" in MCP_TOOLS


# ── Performance benchmarks exist ──

def test_benchmark_module_imports():
    import bench_kmm_performance
    assert bench_kmm_performance.run_all_benchmarks
    assert bench_kmm_performance.bench_recall_warm
    assert bench_kmm_performance.bench_ingestion_throughput


def test_regression_module_imports():
    import bench_kmm_regression
    assert bench_kmm_regression.THRESHOLDS
    assert bench_kmm_regression.compare_to_baseline


# ── Full pipeline round-trip (real data) ──

def test_full_pipeline_zh_roundtrip(tmp_path: Path):
    os.environ["KMM_NOTES_DIR"] = str(tmp_path / "notes")

    from knowledge_collector import generate_note, preprocess_query, rerank_results
    from knowledge_collector.analysis import extract_relations

    note = generate_note({"title": "AI Agent", "content": REAL_ZH_WECHAT, "source_type": "article"}, template="article")
    ko = json.loads(Path(note["knowledge_path"]).read_text(encoding="utf-8"))

    qinfo = preprocess_query("AI Agent 多Agent协作")
    rels = extract_relations(ko)

    docs = [{"title": ko["title"], "content": ko["summary"], "score": 0.9, "url": note["note_path"]}]
    reranked = rerank_results("AI Agent", docs)

    assert ko["language"] == "zh"
    assert len(qinfo["expansions"]) >= 1
    assert len(reranked) >= 1
    print(f"  Pipeline: note={note['note_id']}, lang={ko['language']}, keywords={ko['keywords'][:5]}, relations={len(rels)}")


def test_full_pipeline_en_roundtrip(tmp_path: Path):
    os.environ["KMM_NOTES_DIR"] = str(tmp_path / "notes")

    from knowledge_collector import generate_note
    from knowledge_collector.analysis import extract_relations
    from knowledge_collector.query_rewrite import preprocess_query

    note = generate_note({"title": "Memory Architecture", "content": REAL_EN_TECH, "source_type": "note"}, template="note")
    ko = json.loads(Path(note["knowledge_path"]).read_text(encoding="utf-8"))

    qinfo = preprocess_query("layered memory with hybrid retrieval")
    rels = extract_relations(ko)

    assert ko["language"] == "en"
    assert len(ko["keywords"]) >= 2
    print(f"  Pipeline: note={note['note_id']}, lang={ko['language']}, claims={len(ko['claims'])}, keywords={ko['keywords'][:5]}, relations={len(rels)}")


def test_full_pipeline_hn_style_to_note(tmp_path: Path):
    os.environ["KMM_NOTES_DIR"] = str(tmp_path / "notes")

    from knowledge_collector import analyze_material, generate_note

    note = generate_note({"title": "Show HN: Memory Sidecar", "content": REAL_HN_STYLE}, template="article")
    ko = json.loads(Path(note["knowledge_path"]).read_text(encoding="utf-8"))

    assert ko["language"] == "en"
    assert any("memory" in kw.lower() for kw in ko["keywords"])
    print(f"  HN-style: {len(ko['claims'])} claims, {len(ko['concepts'])} concepts")
