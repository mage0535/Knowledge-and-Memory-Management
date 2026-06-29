"""
知识采集器 — 全工具清单

整合 Hermes Agent 环境中所有可用的知识采集工具，
按采集源类型分模块组织。
"""

__version__ = "1.1.0"

from .article import collect_article
from .document import (
    DocumentCollector,
    DocumentConversionError,
    DocumentConverter,
    DocumentResult,
    SUPPORTED_EXTENSIONS,
    SUPPORTED_FORMATS,
    collect_book,
    collect_document,
)
from .note_generator import generate_note
from .video import collect_video
from .web import collect_web

# 工具全集索引
TOOL_INVENTORY = {
    "web": {
        "title": "网页采集",
        "description": "从网页和网站批量采集知识",
    },
    "video": {
        "title": "视频采集",
        "description": "从视频中提取画面文字和语音内容",
    },
    "article": {
        "title": "文章/内容采集",
        "description": "从社交媒体、新闻、RSS 采集文章",
    },
    "document": {
        "title": "文档采集",
        "description": "通过 MarkItDown 统一转换 PDF、Office、HTML、图片和结构化文本格式",
    },
    "analysis": {
        "title": "关键词分析与知识扩展",
        "description": "关键词提取、交叉验证、关联搜索",
    },
    "note": {
        "title": "笔记生成与入库",
        "description": "从原始材料到结构化笔记的自动转化",
    },
    "knowledge_graph": {
        "title": "知识图谱",
        "description": "将采集的内容建立知识图谱链接",
    },
    "orchestration": {
        "title": "采集编排与调度",
        "description": "多源并行采集、去重、避撞",
    },
}


def on_collect(payload: dict | None = None) -> dict:
    """Manifest hook used after collection jobs complete."""
    payload = dict(payload or {})
    payload.setdefault("status", "ok")
    payload.setdefault("module", "knowledge_collector")
    return payload


__all__ = [
    "TOOL_INVENTORY",
    "DocumentCollector",
    "DocumentConversionError",
    "DocumentConverter",
    "DocumentResult",
    "SUPPORTED_EXTENSIONS",
    "SUPPORTED_FORMATS",
    "collect_article",
    "collect_book",
    "collect_document",
    "collect_video",
    "collect_web",
    "generate_note",
    "on_collect",
]
