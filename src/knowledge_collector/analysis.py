"""
关键词分析与知识扩展 — 全工具清单

从采集内容中提取关键信息、交叉验证、扩展关联知识。
"""

class AnalysisTools:
    """知识分析 — 7 种分析工具"""

    TOOLS = {
        "web_search": {
            "type": "builtin",
            "level": "⭐⭐⭐⭐⭐",
            "description": "网络搜索引擎 — 支持多后端，用于知识扩展与交叉验证",
            "tool": "web_search",
            "features": [
                "多后端搜索（Google/Bing/DuckDuckGo/Brave等）",
                "站点限定（site:）",
                "文件类型限定（filetype:）",
                "每次最多 100 条结果",
            ],
            "use_cases": [
                "关键词→搜索扩展关联知识",
                "交叉验证信息准确性",
                "溯源原始出处",
            ],
            "status": "已部署 · 生产中",
        },
        "web_extract": {
            "type": "builtin",
            "level": "⭐⭐⭐⭐",
            "description": "URL 内容提取与 Markdown 化 — 配合搜索做深度验证",
            "tool": "web_extract",
            "features": [
                "URL → Markdown 全文",
                "PDF URL 自动转换",
                "5000字内全文输出",
            ],
            "status": "已部署 · 生产中",
        },
        "nli_fact_check": {
            "type": "script",
            "level": "⭐⭐⭐",
            "description": "NLI 事实核查 — 基于自然语言推理的判断一致性验证",
            "script": "scripts/nli_fact_check.py",
            "features": [
                "声明与源文本的一致性判断",
                "矛盾/中立/支持的自动分类",
            ],
            "status": "已部署",
        },
        "comment_summary": {
            "type": "script",
            "level": "⭐⭐⭐",
            "description": "评论摘要 — 从社交媒体评论中提取关键观点",
            "script": "scripts/comment_summary.py",
            "features": [
                "评论情感分类",
                "关键观点提取",
                "高频词分析",
            ],
            "status": "已部署",
        },
        "enrich_news": {
            "type": "script",
            "level": "⭐⭐⭐",
            "description": "新闻内容丰富 — 自动添加背景信息和关联阅读",
            "script": "scripts/enrich_news.py",
            "features": [
                "实体识别",
                "背景知识自动补充",
                "关联事件链接",
            ],
            "status": "已部署",
        },
        "keyword_analysis": {
            "type": "plugin",
            "level": "⭐⭐⭐⭐",
            "description": "关键词自动提取与分析 — 中英文关键词抽取",
            "features": [
                "TF-IDF 关键词提取",
                "命名实体识别",
                "热词趋势分析",
                "词云生成",
            ],
            "integration": "通过 LLM 调用或独立 NLP 管线",
            "status": "可用",
        },
        "cross_validate": {
            "type": "workflow",
            "level": "⭐⭐⭐⭐⭐",
            "description": "多源交叉验证工作流 — 同一信息经多源反复确认",
            "workflow": [
                "提取声明（claim extraction）",
                "多源搜索（multi-source search）",
                "一致性比对（consistency check）",
                "置信度评分（confidence scoring）",
                "报告输出（verification report）",
            ],
            "example": "FDE 图文笔记交叉验证：3 轮搜索确认 FDE=Forward Deployed Engineer 定义",
            "status": "已验证流程",
        },
    }
