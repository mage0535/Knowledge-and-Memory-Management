"""
文章/内容采集 — 全工具清单

覆盖微信、微博、新闻、RSS/博客等内容源的采集。
"""

from __future__ import annotations

from runtime_support import CollectionResult
from .note_generator import generate_note
from .web import collect_web

class ArticleCollector:
    """文章内容采集 — 12 种采集源"""

    SOURCES = {
        # ─── 微信生态 ───
        "wechat_article": {
            "type": "skill",
            "level": "⭐⭐⭐⭐⭐",
            "description": "微信公众号文章抓取与保存",
            "skill": "wechat-article-fetcher",
            "features": [
                "公众号文章全文抓取",
                "Markdown 格式输出",
                "图片/排版保留",
            ],
            "status": "已部署 · 生产中",
        },
        "wechat_search": {
            "type": "skill",
            "level": "⭐⭐⭐⭐",
            "description": "微信搜一搜文章搜索",
            "skill": "wechat-article-search",
            "features": [
                "关键词文章搜索",
                "标题/概要/来源/时间",
                "原文链接获取",
            ],
            "status": "已部署",
        },
        "wechat_text_intake": {
            "type": "script",
            "level": "⭐⭐⭐⭐",
            "description": "微信图文统一摄入 — 验证感知式采集",
            "script": "scripts/wechat_text_intake.py",
            "features": [
                "验证码自动检测与处理",
                "opencli weixin 路由",
                "可判定状态返回",
            ],
            "status": "已部署",
        },

        # ─── 微博 ───
        "weibo": {
            "type": "skill",
            "level": "⭐⭐⭐⭐⭐",
            "description": "微博内容搜索、热搜查看、用户动态及评论读取",
            "skill": "weibo-skill",
            "features": [
                "热搜榜实时获取",
                "关键词内容搜索",
                "用户动态与评论",
                "免账号 API（m.weibo.cn 移动端接口）",
            ],
            "status": "已部署 · 生产中",
        },

        # ─── 新闻 ───
        "newsnow": {
            "type": "script",
            "level": "⭐⭐⭐⭐",
            "description": "实时新闻聚合 — 多源新闻采集",
            "script": "newsnow-aggregation (MCP 工具)",
            "features": [
                "多新闻源实时聚合",
                "分类过滤",
            ],
            "status": "已部署 · 生产中",
        },
        "news_discover": {
            "type": "skill",
            "level": "⭐⭐⭐⭐",
            "description": "每日新闻简报 — 全球/本地/科技/财经/体育",
            "skill": "news-discover",
            "features": [
                "多类别新闻",
                "摘要生成",
            ],
            "status": "已部署",
        },
        "tech_news": {
            "type": "skill",
            "level": "⭐⭐⭐⭐",
            "description": "科技新闻聚合 — Hacker News + GitHub Trending + 多源",
            "skill": "tech-news",
            "features": [
                "Hacker News 热门",
                "GitHub Trending",
                "中文科技日报生成",
            ],
            "status": "已部署",
        },
        "ai_news_zh": {
            "type": "skill",
            "level": "⭐⭐⭐⭐",
            "description": "中文 AI 科技日报 — The Verge/Wired/TechCrunch 等英译中",
            "skill": "ai-news-zh",
            "features": [
                "多英文源抓取",
                "自动翻译为中文",
                "Telegram 每日推送",
            ],
            "status": "已部署",
        },

        # ─── RSS/博客 ───
        "blogwatcher": {
            "type": "tool",
            "level": "⭐⭐⭐",
            "description": "RSS/Atom 博客监控 — 通过 blogwatcher-cli 工具",
            "tool": "blogwatcher",
            "features": [
                "多 feed 订阅",
                "增量更新检测",
                "新内容推送",
            ],
            "status": "已部署",
        },

        # ─── GitHub ───
        "github_trending": {
            "type": "script",
            "level": "⭐⭐⭐",
            "description": "GitHub 热门项目采集 — 多源扫描（wangchujiang + githubcn × 2）",
            "script": "scripts/github_trending_collector.py",
            "features": [
                "6 路并行采集",
                "交叉引用去重",
                "已有 Skill 覆盖检查",
            ],
            "status": "已部署 · 生产中",
        },

        # ─── 通用网络文档 ───
        "network_doc_intake": {
            "type": "script",
            "level": "⭐⭐⭐⭐",
            "description": "统一网络文档采集入口 — 微信与通用网页统一路由",
            "script": "scripts/network_doc_intake.py",
            "routing": [
                "微信 → wechat_text_intake",
                "通用 → opencli web → knowledge_fetch_router",
            ],
            "status": "已部署",
        },
        "doc_parse_router": {
            "type": "script",
            "level": "⭐⭐⭐⭐",
            "description": "文档解析路由 — 多格式文档统一解析入口",
            "script": "scripts/doc_parse_router.py",
            "formats": [
                "PDF (Magic-PDF/MinerU)",
                "HTML",
                "Markdown",
                "Office 文档",
            ],
            "status": "已部署",
        },
    }

    def collect(self, source: str, keyword: str) -> CollectionResult:
        if keyword.startswith("http://") or keyword.startswith("https://"):
            result = collect_web(keyword, strategy="auto")
            result.source_type = "article"
            result.metadata["source"] = source
            return result

        title = f"{source}: {keyword}"
        body = (
            f"Source: {source}\n"
            f"Keyword: {keyword}\n\n"
            "This public KMM package stores the article collection request as a structured note. "
            "Use server-side source adapters for provider-specific ingestion."
        )
        note = generate_note(
            {
                "title": title,
                "content": body,
                "source_type": "article",
                "source_ref": keyword,
                "metadata": {"source": source},
            },
            template="article",
        )
        return CollectionResult(
            source_type="article",
            title=title,
            content_preview=body[:500],
            note_path=note["note_path"],
            gbrain_slug=note["note_id"],
            metadata={"source": source},
        )


def collect_article(source: str, keyword: str) -> CollectionResult:
    return ArticleCollector().collect(source, keyword)
