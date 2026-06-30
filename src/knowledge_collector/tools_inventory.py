"""Unified tool inventory — maps all 42+ tools from collection-pipeline.md 
to their actual import/callable interfaces.

This is the SINGLE SOURCE OF TRUTH for KMM tool availability.
"""

from __future__ import annotations

from pathlib import Path

# === Tool Inventory (42 tools across 9 categories) ===

TOOLS = {
    # ── Web Collection (9) ──
    "collect_web": {
        "category": "web",
        "level": 5,
        "import": "knowledge_collector.web.collect_web",
        "description": "HTTP-based web page collection with note generation",
        "status": "production",
    },
    "knowledge_fetch_router": {
        "category": "web",
        "level": 4,
        "script": "knowledge_fetch_router.py",
        "description": "Intelligent URL routing: trafilatura -> readability -> Crawl4AI",
    },
    "browser_fetch": {
        "category": "web",
        "level": 5,
        "import": "knowledge_collector.web.WebCollector",
        "description": "Full browser-based page collection (requests+BS4)",
    },
    "anti_crawl_fetch": {
        "category": "web",
        "level": 5,
        "interface": "scrapling_mcp",
        "description": "Anti-detection browser collection via Scrapling MCP",
    },
    "chrome_devtools_fetch": {
        "category": "web",
        "level": 5,
        "interface": "chrome_devtools_mcp",
        "description": "Chrome DevTools Protocol collection via MCP",
    },
    "gstack_browser": {
        "category": "web",
        "level": 5,
        "interface": "gstack_browser_mcp",
        "description": "Hermes built-in browser with visual analysis",
    },
    "site_crawler": {
        "category": "web",
        "level": 4,
        "script": "knowledge_site_crawler.mjs",
        "description": "Same-domain batch crawling via Crawlee",
    },
    "obscura_fetch": {
        "category": "web",
        "level": 3,
        "script": "obscura_fetch_bridge.py",
        "description": "Dynamic page Markdown extraction bridge",
    },
    "ripgrep_kb_scan": {
        "category": "web",
        "level": 2,
        "script": "ripgrep_kb_scan.py",
        "description": "Knowledge base pre-screening via ripgrep dedup",
    },

    # ── Video Collection (12) ──
    "collect_video": {
        "category": "video",
        "level": 5,
        "import": "knowledge_collector.video.collect_video",
        "description": "Video URL collection with yt-dlp metadata and subtitle extraction",
        "status": "production",
    },
    "video_metadata_extract": {
        "category": "video",
        "level": 5,
        "import": "knowledge_collector.video.extract_metadata",
        "description": "yt-dlp --dump-json metadata extraction",
    },
    "video_subtitle_extract": {
        "category": "video",
        "level": 5,
        "import": "knowledge_collector.video.extract_subtitles",
        "description": "Auto-generated subtitle extraction via yt-dlp VTT",
    },
    "video_scene_detect": {
        "category": "video",
        "level": 4,
        "import": "knowledge_collector.scene_detector.detect_scenes",
        "description": "PySceneDetect scene boundary detection",
    },
    "video_keyframe_extract": {
        "category": "video",
        "level": 4,
        "import": "knowledge_collector.scene_detector.select_keyframes",
        "description": "ffmpeg keyframe extraction at scene midpoints",
    },
    "video_frame_ocr": {
        "category": "video",
        "level": 4,
        "import": "knowledge_collector.scene_detector.ocr_frame",
        "description": "PaddleOCR / Tesseract frame text extraction",
    },
    "video_timeline_chunks": {
        "category": "video",
        "level": 4,
        "import": "knowledge_collector.scene_detector.extract_timeline_chunks",
        "description": "Per-scene timeline blocks with transcript + OCR",
    },
    "video_adapter_framework": {
        "category": "video",
        "level": 4,
        "import": "knowledge_collector.video_adapter",
        "description": "Platform adapter registry (YouTube/Bilibili/TikTok/Douyin)",
    },
    "yt_dlp": {
        "category": "video",
        "level": 5,
        "interface": "cli:yt-dlp",
        "description": "Video/audio download engine (1000+ sites)",
    },
    "whisper_asr": {
        "category": "video",
        "level": 4,
        "interface": "import:whisper",
        "description": "OpenAI Whisper speech-to-text (99+ languages)",
    },
    "ffmpeg": {
        "category": "video",
        "level": 3,
        "interface": "cli:ffmpeg",
        "description": "Video split/transcode/audio extraction",
    },
    "tesseract_ocr": {
        "category": "video",
        "level": 3,
        "interface": "cli:tesseract",
        "description": "Open-source OCR (chi_sim+eng)",
    },

    # ── Document/OCR (10) ──
    "collect_document": {
        "category": "document",
        "level": 5,
        "import": "knowledge_collector.document.collect_document",
        "description": "Document collection via MarkItDown unified converter",
        "status": "production",
    },
    "parse_router": {
        "category": "document",
        "level": 5,
        "import": "knowledge_collector.parse_router.parse_with_routing",
        "description": "Multi-engine document routing with file-hash caching",
        "status": "production",
    },
    "batch_parse": {
        "category": "document",
        "level": 4,
        "import": "knowledge_collector.parse_router.batch_parse",
        "description": "ThreadPoolExecutor parallel batch document processing",
    },
    "doc_parse_router_script": {
        "category": "document",
        "level": 4,
        "script": "doc_parse_router.py",
        "description": "CLI multi-format document parse router",
    },
    "markitdown_engine": {
        "category": "document",
        "level": 5,
        "interface": "import:markitdown",
        "description": "MarkItDown unified conversion (PDF/Office/HTML/CSV/JSON/XML)",
    },
    "sensenova_pdf": {
        "category": "document",
        "level": 5,
        "script": "sensenova_dispatcher.py",
        "description": "SenseNova PDF full analysis (text+scan+tables+charts)",
    },
    "sensenova_ppt": {
        "category": "document",
        "level": 5,
        "script": "sensenova_dispatcher.py",
        "description": "SenseNova PPT full-slide extraction",
    },
    "sensenova_word": {
        "category": "document",
        "level": 5,
        "script": "sensenova_dispatcher.py",
        "description": "SenseNova Word extraction (body+tables+highlights)",
    },
    "book_cache_manager": {
        "category": "document",
        "level": 4,
        "script": "book_cache_manager.py",
        "description": "710+ book index with on-demand cache and auto-refinement",
    },

    # ── Article/Content (10) ──
    "collect_article": {
        "category": "article",
        "level": 5,
        "import": "knowledge_collector.article.collect_article",
        "description": "Article collection with platform routing and channel adapters",
        "status": "production",
    },
    "channel_hackernews": {
        "category": "article",
        "level": 4,
        "import": "knowledge_collector.channels.hackernews",
        "description": "HackerNews official Firebase API adapter",
        "status": "production",
    },
    "channel_wechat": {
        "category": "article",
        "level": 4,
        "import": "knowledge_collector.channels.wechat",
        "description": "WeChat Official Account article adapter",
        "status": "production",
    },
    "channel_reddit": {
        "category": "article",
        "level": 4,
        "import": "knowledge_collector.channels.reddit",
        "description": "Reddit public JSON API thread adapter",
        "status": "production",
    },
    "channel_csdn": {
        "category": "article",
        "level": 3,
        "import": "knowledge_collector.channels.csdn",
        "description": "CSDN article normalization adapter",
        "status": "production",
    },
    "channel_xiaohongshu": {
        "category": "article",
        "level": 4,
        "import": "knowledge_collector.channels.xiaohongshu",
        "description": "Xiaohongshu image-first OCR adapter",
        "status": "production",
    },
    "github_trending": {
        "category": "article",
        "level": 3,
        "script": "github_trending_collector.py",
        "description": "GitHub Trending repository collection",
    },

    # ── Analysis (7) ──
    "analyze_material": {
        "category": "analysis",
        "level": 5,
        "import": "knowledge_collector.analysis.analyze_material",
        "description": "Deterministic knowledge analysis (concepts/claims/actions/risks/timeline)",
        "status": "production",
    },
    "analyze_material_llm": {
        "category": "analysis",
        "level": 5,
        "import": "knowledge_collector.llm_analyzer.analyze_material_llm",
        "description": "LLM-enhanced knowledge analysis (OpenAI/DeepSeek/Anthropic)",
        "status": "production",
    },
    "extract_relations": {
        "category": "analysis",
        "level": 4,
        "import": "knowledge_collector.analysis.extract_relations",
        "description": "GraphRAG relation extraction from concept-claim edges",
        "status": "production",
    },
    "query_rewrite": {
        "category": "analysis",
        "level": 4,
        "import": "knowledge_collector.query_rewrite.preprocess_query",
        "description": "Query preprocessing (language detect + synonym expansion + entity extraction)",
        "status": "production",
    },
    "keyword_analysis": {
        "category": "analysis",
        "level": 5,
        "import": "knowledge_collector.analysis.KnowledgeAnalyzer",
        "description": "Keyword frequency extraction with stopword filtering",
    },
    "cross_validate": {
        "category": "analysis",
        "level": 4,
        "interface": "web_search_mcp",
        "description": "Multi-source cross-validation workflow",
    },
    "generate_note": {
        "category": "analysis",
        "level": 5,
        "import": "knowledge_collector.note_generator.generate_note",
        "description": "Structured note generation with Markdown + knowledge JSON dual output",
        "status": "production",
    },

    # ── Retrieval (6) ──
    "search_notes": {
        "category": "retrieval",
        "level": 5,
        "import": "notes_rag.search_notes",
        "description": "4-layer fused search (local+FTS5+Hindsight+gbrain) + hybrid + rerank",
        "status": "production",
    },
    "hybrid_search": {
        "category": "retrieval",
        "level": 4,
        "import": "knowledge_collector.hybrid_search.hybrid_search",
        "description": "Qdrant vector search + RRF fusion with lexical results",
    },
    "reranker": {
        "category": "retrieval",
        "level": 4,
        "import": "knowledge_collector.reranker.rerank",
        "description": "Jina AI reranker with local keyword fallback",
    },
    "lightweight_recall": {
        "category": "retrieval",
        "level": 5,
        "script": "lightweight_recall.py",
        "description": "CLI multi-layer recall with parallel layer execution",
    },
    "augmented_search": {
        "category": "retrieval",
        "level": 4,
        "import": "knowledge_augmentation.augmented_search.AugmentedSearch",
        "description": "Local-first search with AnySearch vertical domain web fallback",
    },
    "knowledge_discovery": {
        "category": "retrieval",
        "level": 5,
        "script": "knowledge_discovery.py",
        "description": "Auto-discover new notes and ingest into gbrain",
    },

    # ── Sync (4) ──
    "cloud_sync": {
        "category": "sync",
        "level": 5,
        "import": "cloud_sync",
        "description": "rclone 12+ cloud drive bidirectional sync",
        "status": "production",
    },
    "list_cloud_drives": {
        "category": "sync",
        "level": 5,
        "import": "cloud_sync.list_cloud_drives",
        "description": "List configured rclone remotes",
    },
    "bidirectional_sync": {
        "category": "sync",
        "level": 4,
        "script": "onedrive_bidirectional_sync.sh",
        "description": "OneDrive bidirectional incremental sync (4h cron)",
    },
    "nightly_maintenance": {
        "category": "sync",
        "level": 5,
        "script": "nightly_maintenance.py",
        "description": "Nightly maintenance (discovery + orphans + compact)",
    },

    # ── Refinement (4) ──
    "book_to_skill": {
        "category": "refinement",
        "level": 5,
        "script": "book_to_skill.py",
        "description": "PDF/EPUB structured refinement pipeline (Skill + KMM note)",
    },
    "book_keyword_index": {
        "category": "refinement",
        "level": 4,
        "script": "book_keyword_index.py",
        "description": "Book keyword index build and search",
    },
    "distill_methodologies": {
        "category": "refinement",
        "level": 4,
        "script": "distill_methodologies.py",
        "description": "Daily trending knowledge to methodology distillation",
    },
    "recall_shadow_compare": {
        "category": "refinement",
        "level": 3,
        "script": "recall_shadow_compare.py",
        "description": "A/B recall quality comparison between baseline and candidate",
    },

    # ── Dev/Ops (5) ──
    "sensitive_scan": {
        "category": "devops",
        "level": 4,
        "script": "sensitive_scan.py",
        "description": "Repository privacy scan (paths/credentials/knowledge JSON)",
    },
    "gray_validation": {
        "category": "devops",
        "level": 4,
        "script": "gray_validation_suite.py",
        "description": "Gray-environment validation suite",
    },
    "kmm_health_check": {
        "category": "devops",
        "level": 4,
        "script": "kmm_health_check.py",
        "description": "KMM health artifact generation",
    },
    "kmm_e2e_smoke": {
        "category": "devops",
        "level": 4,
        "script": "kmm_e2e_smoke.py",
        "description": "End-to-end real-usage smoke test",
    },
    "mcp_server": {
        "category": "devops",
        "level": 4,
        "import": "mcp_server",
        "description": "MCP stdio server exposing 5 KMM tools to agents",
    },
}


def get_tool(name: str) -> dict | None:
    return TOOLS.get(name)


def get_tools_by_category() -> dict[str, list[str]]:
    cats = {}
    for name, info in TOOLS.items():
        cat = info["category"]
        cats.setdefault(cat, []).append(name)
    return cats


def get_production_tools() -> list[str]:
    return [n for n, i in TOOLS.items() if i.get("status") == "production"]


def get_importable_tools() -> list[str]:
    return [n for n, i in TOOLS.items() if "import" in i]


def get_tool_count() -> dict:
    cats = get_tools_by_category()
    total = len(TOOLS)
    production = len(get_production_tools())
    importable = len(get_importable_tools())
    return {
        "total": total,
        "production": production,
        "importable": importable,
        "by_category": {k: len(v) for k, v in cats.items()},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_tool_count(), indent=2))
