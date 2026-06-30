"""Reddit structured thread channel adapter.

Uses Reddit's JSON API (no auth required for read-only public content).
"""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from . import ChannelAdapter, ChannelContent, register_adapter


class RedditAdapter(ChannelAdapter):
    platform = "reddit"

    def can_handle(self, url_or_id: str) -> bool:
        return (
            "reddit.com" in url_or_id
            or url_or_id.startswith("r/")
            or url_or_id.startswith("/r/")
        )

    def fetch(self, url_or_id: str, max_comments: int = 30) -> ChannelContent:
        post_url = url_or_id
        if not post_url.startswith("http"):
            post_url = f"https://www.reddit.com{post_url}" if post_url.startswith("/") else f"https://www.reddit.com/r/{post_url}"
        json_url = post_url.rstrip("/") + ".json"

        try:
            req = Request(json_url, headers={"User-Agent": "KMM/0.1.0"})
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            return ChannelContent(
                source_platform="reddit",
                source_url=post_url,
                title="Reddit Thread",
                extraction_quality="failed",
                metadata={"error": str(exc)},
            )

        try:
            post_data = data[0]["data"]["children"][0]["data"]
            comments_data = data[1]["data"]["children"]
        except (IndexError, KeyError):
            return ChannelContent(
                source_platform="reddit",
                source_url=post_url,
                title="Reddit Thread",
                extraction_quality="failed",
                metadata={"error": "unexpected JSON structure"},
            )

        title = post_data.get("title", "reddit-thread")
        author = post_data.get("author", "")
        subreddit = post_data.get("subreddit", "")
        body = post_data.get("selftext", "")
        score = post_data.get("score", 0)
        num_comments = post_data.get("num_comments", 0)
        created_utc = post_data.get("created_utc")
        published_at = _format_utc(created_utc)

        blocks = [{
            "type": "text",
            "text": f"# {title}\nr/{subreddit} | u/{author} | Score: {score} | Comments: {num_comments}\n\n{body}",
            "order": 0,
            "source_ref": post_url,
        }]

        top_comments = _extract_comments(comments_data, max_comments)
        for i, comment in enumerate(top_comments):
            if comment.get("body"):
                blocks.append({
                    "type": "comment",
                    "text": f"**u/{comment.get('author', 'unknown')}** ({comment.get('score', 0)} pts): {comment['body'][:300]}",
                    "order": i + 1,
                    "metadata": {"score": comment.get("score", 0)},
                })

        return ChannelContent(
            source_platform="reddit",
            source_url=post_url,
            title=title,
            author=f"u/{author}",
            published_at=published_at,
            language="en",
            content_blocks=blocks,
            extraction_quality="high",
            metadata={
                "subreddit": subreddit,
                "score": score,
                "num_comments": num_comments,
                "comment_count": len(top_comments),
            },
        )


def _extract_comments(children: list[dict], max_count: int, depth: int = 0) -> list[dict]:
    comments = []
    for child in children:
        if len(comments) >= max_count:
            break
        if child.get("kind") != "t1":
            continue
        data = child.get("data", {})
        if data.get("stickied") or data.get("body") in (None, "[deleted]", "[removed]"):
            continue
        comments.append({
            "author": data.get("author", ""),
            "body": data.get("body", ""),
            "score": data.get("score", 0),
            "depth": depth,
        })
        if "replies" in data and isinstance(data["replies"], dict):
            nested = data["replies"]["data"]["children"]
            comments.extend(_extract_comments(nested, max_count - len(comments), depth + 1))
    return comments


def _format_utc(ts: float | None) -> str:
    if not ts:
        return ""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


register_adapter(RedditAdapter())
