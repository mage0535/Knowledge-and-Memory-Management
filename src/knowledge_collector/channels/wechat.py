"""WeChat Official Account article channel adapter."""

from __future__ import annotations

import re

from . import ChannelAdapter, ChannelContent, register_adapter


class WechatAdapter(ChannelAdapter):
    platform = "wechat"

    def can_handle(self, url_or_id: str) -> bool:
        return (
            "mp.weixin.qq.com" in url_or_id
            or url_or_id.startswith("wechat:")
        )

    def fetch(self, url_or_id: str) -> ChannelContent:
        import requests
        from bs4 import BeautifulSoup

        url = url_or_id.replace("wechat:", "")
        try:
            resp = requests.get(url, timeout=20, headers={
                "User-Agent": "KMM/0.1.0",
                "Accept": "text/html,application/xhtml+xml",
            })
            resp.raise_for_status()
        except Exception as exc:
            return ChannelContent(
                source_platform="wechat",
                source_url=url,
                title="WeChat Article",
                extraction_quality="failed",
                metadata={"error": str(exc)},
            )

        soup = BeautifulSoup(resp.text, "html.parser")
        title_elem = soup.select_one("#activity-name")
        author_elem = soup.select_one("#js_name")
        date_elem = soup.select_one("#publish_time")
        content_elem = soup.select_one("#js_content")

        title = (title_elem.get_text(strip=True) if title_elem else None) or "WeChat Article"
        author = (author_elem.get_text(strip=True) if author_elem else "") or ""
        published_at = (date_elem.get_text(strip=True) if date_elem else "") or ""
        body = content_elem.get_text("\n", strip=True) if content_elem else ""

        blocks = [{
            "type": "text",
            "text": f"# {title}\n\nAuthor: {author} | Published: {published_at}\n\n{body}",
            "order": 0,
            "source_ref": url,
        }]

        images = []
        if content_elem:
            for img in content_elem.select("img"):
                src = img.get("data-src") or img.get("src", "")
                if src:
                    images.append(src)

        return ChannelContent(
            source_platform="wechat",
            source_url=url,
            title=title,
            author=author,
            published_at=published_at,
            language="zh" if bool(re.search(r"[\u4e00-\u9fff]", body)) else "unknown",
            content_blocks=blocks,
            image_assets=images,
            extraction_quality="high" if body else "low",
        )


register_adapter(WechatAdapter())
