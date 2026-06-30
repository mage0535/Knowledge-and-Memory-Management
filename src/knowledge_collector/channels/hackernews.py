"""Hacker News API channel adapter."""

from __future__ import annotations

import json
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from . import ChannelAdapter, ChannelContent, register_adapter

HN_BASE = "https://hacker-news.firebaseio.com/v0"
CACHE_TTL = 300


class HackerNewsAdapter(ChannelAdapter):
    platform = "hackernews"

    def can_handle(self, url_or_id: str) -> bool:
        return (
            "news.ycombinator.com" in url_or_id
            or url_or_id.replace("/", "").isdigit()
        )

    def fetch(self, url_or_id: str, max_comments: int = 20) -> ChannelContent:
        item_id = self._extract_id(url_or_id)
        story = self._fetch_json(f"{HN_BASE}/item/{item_id}.json")
        if not story:
            raise ValueError(f"HN story not found: {item_id}")

        title = story.get("title") or f"hn-{item_id}"
        author = story.get("by", "")
        score = story.get("score", 0)
        url = story.get("url", "")
        descendants = story.get("descendants", 0)
        published_at = _format_time(story.get("time"))

        body = story.get("text") or ""
        if url:
            body = f"{body}\n\nSource: {url}"

        kids = story.get("kids", [])[:max_comments]
        comments = []
        for kid_id in kids:
            kid = self._fetch_json(f"{HN_BASE}/item/{kid_id}.json")
            if kid and not kid.get("deleted"):
                comments.append({
                    "by": kid.get("by", ""),
                    "text": (kid.get("text") or "")[:240],
                })

        blocks = [{
            "type": "text",
            "text": f"# {title}\n\nAuthor: {author} | Score: {score} | Comments: {descendants}\n\n{body}",
            "order": 0,
        }]
        for i, comment in enumerate(comments):
            blocks.append({
                "type": "comment",
                "text": f"**{comment['by']}**: {comment['text']}",
                "order": i + 1,
                "source_ref": f"hn:{item_id}#c{i}",
            })

        return ChannelContent(
            source_platform="hackernews",
            source_url=url or f"https://news.ycombinator.com/item?id={item_id}",
            title=title,
            author=author,
            published_at=published_at,
            language="en",
            content_blocks=blocks,
            extraction_quality="high",
            metadata={
                "item_id": item_id,
                "score": score,
                "descendants": descendants,
                "comment_count": len(comments),
            },
        )

    @staticmethod
    def _extract_id(raw: str) -> str:
        import re
        match = re.search(r"(?:id=)?(\d{6,})", raw)
        if match:
            return match.group(1)
        return raw.strip()

    @staticmethod
    def _fetch_json(url: str) -> dict | None:
        try:
            with urlopen(Request(url), timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError):
            return None


def _format_time(ts: float | None) -> str:
    if not ts:
        return ""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


register_adapter(HackerNewsAdapter())
