"""Xiaohongshu (RedNote) image-first channel adapter.

Strategy: download post images, OCR each image via PaddleOCR,
generate image-sequence note with visual content extraction.
"""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from . import ChannelAdapter, ChannelContent, register_adapter


class XiaohongshuAdapter(ChannelAdapter):
    platform = "xiaohongshu"

    def can_handle(self, url_or_id: str) -> bool:
        return (
            "xiaohongshu.com" in url_or_id
            or "xhslink.com" in url_or_id
            or "rednote" in url_or_id.lower()
        )

    def fetch(self, url_or_id: str) -> ChannelContent:
        import requests
        from bs4 import BeautifulSoup

        try:
            resp = requests.get(url_or_id, timeout=20, headers={
                "User-Agent": "KMM/0.1.0",
                "Accept": "text/html",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            })
            resp.raise_for_status()
        except Exception as exc:
            return ChannelContent(
                source_platform="xiaohongshu",
                source_url=url_or_id,
                title="Xiaohongshu Post",
                extraction_quality="failed",
                metadata={"error": str(exc)},
            )

        soup = BeautifulSoup(resp.text, "html.parser")
        title_elem = soup.select_one("title")
        title = title_elem.get_text(strip=True) if title_elem else "Xiaohongshu Post"

        desc_elem = soup.select_one(".desc") or soup.select_one(".note-text") or soup.select_one('[class*="desc"]')
        description = desc_elem.get_text(strip=True)[:2000] if desc_elem else ""

        images = []
        blocks = []

        blocks.append({
            "type": "text",
            "text": f"# {title}\n\n{description}",
            "order": 0,
        })

        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src", "")
            if not src or "data:image" in src:
                continue
            if src.startswith("//"):
                src = f"https:{src}"
            images.append(src)
            ocr_text = ""
            try:
                ocr_text = _ocr_image_url(src)
            except Exception:
                pass
            blocks.append({
                "type": "image",
                "text": f"Image: {src}\nOCR: {ocr_text}",
                "order": len(blocks),
                "metadata": {"url": src},
            })

        return ChannelContent(
            source_platform="xiaohongshu",
            source_url=url_or_id,
            title=title[:200],
            content_blocks=blocks,
            image_assets=images,
            extraction_quality="medium" if images else "low",
            metadata={"image_count": len(images)},
        )


def _ocr_image_url(url: str) -> str:
    try:
        import requests
        with TemporaryDirectory() as tmpdir:
            img_path = Path(tmpdir) / "frame.png"
            resp = requests.get(url, timeout=10, headers={"User-Agent": "KMM/0.1.0"})
            resp.raise_for_status()
            img_path.write_bytes(resp.content)
            return _ocr_image_file(str(img_path))
    except Exception:
        return ""


def _ocr_image_file(path: str) -> str:
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(lang="ch", use_angle_cls=True, show_log=False)
        result = ocr.ocr(path)
        if result and result[0]:
            return " ".join(line[1][0] for line in result[0] if len(line) > 1)
    except ImportError:
        pass
    try:
        import subprocess
        result = subprocess.run(
            ["tesseract", path, "stdout", "-l", "chi_sim+eng"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ""


register_adapter(XiaohongshuAdapter())
