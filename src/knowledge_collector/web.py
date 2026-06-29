"""
网页采集 — 全工具清单

覆盖从轻量HTTP提取到反检测浏览器采集的全部场景。
"""

from __future__ import annotations

from dataclasses import asdict
from html import unescape
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from runtime_support import CollectionResult
from .note_generator import generate_note

class WebCollector:
    """网页知识采集 — 6 种采集引擎"""

    # ============================================================
    # 工具清单
    # ============================================================

    ENGINES = {
        # ─── MCP 工具（最高级，需 Hermes MCP 环境） ───
        "scrapling": {
            "type": "mcp",
            "level": "⭐⭐⭐⭐⭐",
            "protocol": "MCP (Scrapling)",
            "description": "反检测浏览器采集，内置Cloudflare Turnstile绕过、隐形浏览器指纹、WebGL保护",
            "modes": {
                "stealthy": "最高保护级别 - 反检测浏览器 + CF 验证码绕过",
                "dynamic": "中保护级别 - Playwright 标准浏览器",
                "http": "低保护级别 - 纯 HTTP 请求",
            },
            "features": [
                "Cloudflare 验证码自动求解",
                "WebGL/Canvas 指纹保护",
                "WebRTC 泄露防护",
                "浏览器会话复用（open_session/close_session）",
                "批量 URL 并发采集（bulk_fetch）",
                "Cookie 注入",
                "多代理支持",
                "截图能力（screenshot）",
            ],
            "script": "MCP: mcp_scrapling_*",
            "status": "已部署 · 生产中",
        },
        "chrome_devtools": {
            "type": "mcp",
            "level": "⭐⭐⭐⭐⭐",
            "protocol": "MCP (Chrome DevTools)",
            "description": "完整 Chrome DevTools 协议控制，可操作页面、录制性能、网络请求分析",
            "features": [
                "完整浏览器自动化（导航/点击/填表/拖拽）",
                "JavaScript 执行（evaluate_script）",
                "网络请求拦截与分析",
                "性能追踪（Lighthouse + Tracing）",
                "内存堆快照",
                "Console 日志捕获",
                "截图 + 无障碍树快照",
            ],
            "script": "MCP: mcp_chrome_devtools_*",
            "status": "已部署 · 生产中",
        },
        "gstack_browser": {
            "type": "builtin",
            "level": "⭐⭐⭐⭐⭐",
            "description": "Hermes 内置浏览器工具，支持导航/点击/截图/Console/JavaScript执行",
            "features": [
                "URL 导航",
                "页面截图 + 视觉分析（vision_analyze）",
                "Console 日志读取",
                "JavaScript 执行",
                "AI 驱动交互（browser_click/type等）",
            ],
            "script": "browser_*",
            "status": "已部署 · 生产中",
        },

        # ─── 专用采集脚本 ───
        "knowledge_fetch_router": {
            "type": "script",
            "level": "⭐⭐⭐⭐",
            "protocol": "Python",
            "description": "智能 URL 路由采集器 — 自动选择最优采集策略",
            "script": "scripts/knowledge_fetch_router.py",
            "routing": [
                "→ trafilatura（快速全文提取）",
                "→ readability（内容可读性提取）",
                "→ Crawl4AI（JS渲染+Markdown输出）",
                "→ YouTube transcript（视频标题+字幕优先）",
            ],
            "status": "已部署 · 生产中",
            "note": "首选的普通网页采集入口",
        },
        "knowledge_site_crawler": {
            "type": "script",
            "level": "⭐⭐⭐⭐",
            "protocol": "Node.js (Crawlee)",
            "description": "同域名网站批量爬虫 — 基于 Crawlee 的扩展采集",
            "script": "scripts/knowledge_site_crawler.mjs",
            "wrapper": "scripts/knowledge_site_crawler.sh",
            "features": [
                "同域名递归爬取",
                "预览内容提取",
                "爬取队列管理",
            ],
            "status": "已部署",
        },
        "obscura_fetch_bridge": {
            "type": "bridge",
            "level": "⭐⭐⭐",
            "protocol": "Python → Obscura",
            "description": "动态网页 Markdown 提取桥接器 — 适合中等动态页面",
            "script": "scripts/obscura_fetch_bridge.py",
            "status": "已部署",
        },
        "opensquilla_bridge": {
            "type": "bridge",
            "level": "⭐⭐⭐",
            "protocol": "Python → OpenSquilla",
            "description": "低 Token 侧车采集 — 适合简单页面的高效轻量方案",
            "script": "scripts/opensquilla_bridge.py",
            "status": "已部署",
        },

        # ─── 内置工具（无额外依赖） ───
        "web_extract": {
            "type": "builtin",
            "level": "⭐⭐",
            "description": "Hermes 内置 HTTP 网页内容提取，Markdown 化输出",
            "script": "web_extract (内置)",
            "note": "最简单页面的首选，无JS渲染",
            "status": "已部署 · 生产中",
        },
        "ripgrep_kb_scan": {
            "type": "script",
            "level": "⭐⭐",
            "protocol": "Python + ripgrep",
            "description": "知识库快速预筛 — 通过 ripgrep 快速扫描已索引内容",
            "script": "scripts/ripgrep_kb_scan.py",
            "status": "已部署",
            "note": "适合采集前先去重判断",
        },
    }

    # ============================================================
    # 采集策略
    # ============================================================

    STRATEGY = {
        "simple_page": {
            "description": "简单静态页面",
            "chain": ["web_extract", "knowledge_fetch_router", "scrapling_http"],
        },
        "dynamic_page": {
            "description": "动态渲染页面 (JS/SPA)",
            "chain": ["scrapling_dynamic", "chrome_devtools", "gstack_browser"],
        },
        "anti_bot_page": {
            "description": "反爬/Cloudflare 保护页面",
            "chain": ["scrapling_stealthy", "chrome_devtools"],
        },
        "batch_site": {
            "description": "整站批量采集",
            "chain": ["knowledge_site_crawler", "scrapling_bulk"],
        },
    }

    def collect(self, url, strategy="auto"):
        """采集网页内容，自动按策略链降级

        Args:
            url: 目标 URL
            strategy: auto / simple_page / dynamic_page / anti_bot_page / batch_site
        """
        response = requests.get(url, timeout=20, headers={"User-Agent": "KMM/0.1.0"})
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        text = self._extract_text(soup)
        if not title:
            title = urlparse(url).netloc or "web-note"
        preview = text[:1000]
        note = generate_note(
            {
                "title": title,
                "content": text or preview or url,
                "source_type": "web",
                "source_ref": url,
                "metadata": {"strategy": strategy, "extractor": "requests+bs4"},
            },
            template="web",
        )
        return CollectionResult(
            source_type="web",
            title=title,
            content_preview=preview,
            url=url,
            note_path=note["note_path"],
            gbrain_slug=note["note_id"],
            extractor="requests+bs4",
            metadata={"strategy": strategy},
        )

    @staticmethod
    def _extract_text(soup: BeautifulSoup) -> str:
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text("\n")
        text = unescape(text)
        lines = [line.strip() for line in text.splitlines()]
        cleaned = "\n".join(line for line in lines if line)
        return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def collect_web(url: str, strategy: str = "auto") -> CollectionResult:
    return WebCollector().collect(url, strategy=strategy)
