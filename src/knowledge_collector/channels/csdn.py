"""CSDN article channel adapter."""

from __future__ import annotations

from . import ChannelAdapter, ChannelContent, register_adapter


class CsdnAdapter(ChannelAdapter):
    platform = "csdn"

    def can_handle(self, url_or_id: str) -> bool:
        return "csdn.net" in url_or_id

    def fetch(self, url_or_id: str) -> ChannelContent:
        import requests
        from bs4 import BeautifulSoup

        try:
            resp = requests.get(url_or_id, timeout=20, headers={
                "User-Agent": "KMM/0.1.0",
                "Accept": "text/html",
            })
            resp.raise_for_status()
        except Exception as exc:
            return ChannelContent(
                source_platform="csdn",
                source_url=url_or_id,
                title="CSDN Article",
                extraction_quality="failed",
                metadata={"error": str(exc)},
            )

        soup = BeautifulSoup(resp.text, "html.parser")
        title = (soup.select_one("#articleContentId") or soup.select_one("h1") or soup.title)
        title_text = title.get_text(strip=True) if title else "CSDN Article"

        author_elem = soup.select_one(".follow-nickName") or soup.select_one(".name")
        author = author_elem.get_text(strip=True) if author_elem else ""

        main = soup.select_one("#content_views") or soup.select_one("article") or soup.body
        if main:
            for tag in main(["script", "style", "noscript", "aside", "nav", ".recommend-box", ".hide-article-box"]):
                tag.decompose()
            for tag in main.select("pre code"):
                tag.replace_with(f"```\n{tag.get_text()}\n```")
            for tag in main.select("code"):
                tag.replace_with(f"`{tag.get_text()}`")
            body = main.get_text("\n", strip=True)
        else:
            body = ""

        blocks = [{
            "type": "text",
            "text": f"# {title_text}\nAuthor: {author}\n\n{body[:8000]}",
            "order": 0,
            "source_ref": url_or_id,
        }]

        return ChannelContent(
            source_platform="csdn",
            source_url=url_or_id,
            title=title_text,
            author=author,
            content_blocks=blocks,
            extraction_quality="high" if body else "low",
        )


register_adapter(CsdnAdapter())
