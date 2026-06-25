"""
知识采集器 — 全工具清单

整合 Hermes Agent 环境中所有可用的知识采集工具，
按采集源类型分模块组织。
"""

__version__ = "1.0.0"

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
        "title": "文档/OCR 采集",
        "description": "从 PDF、图片、扫描件中提取文字",
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
    "book_index": {
        "title": "书籍关键词索引",
        "description": "从 OneDrive book/ 构建 FTS5 关键词索引，对话中自动匹配推荐相关书籍（search / suggest / cache / analyze / cleanup）",
    },
}
