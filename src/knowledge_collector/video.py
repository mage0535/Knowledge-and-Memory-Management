"""Enhanced video collection with subtitle extraction and batch processing.

Uses yt-dlp for metadata and subtitle/transcript extraction.
"""

from __future__ import annotations

from dataclasses import asdict
import json
import subprocess
import sys
from pathlib import Path

from runtime_support import CollectionResult
from .note_generator import generate_note


SUPPORTED_PLATFORMS = {
    "youtube": {"domain": "youtube.com", "subtitle_langs": ["en", "zh-Hans", "ja", "ko"]},
    "bilibili": {"domain": "bilibili.com", "subtitle_langs": ["zh-Hans", "en"]},
    "tiktok": {"domain": "tiktok.com", "subtitle_langs": ["en"]},
    "douyin": {"domain": "douyin.com", "subtitle_langs": ["zh-Hans"]},
}


def detect_platform(url: str) -> str:
    for platform, info in SUPPORTED_PLATFORMS.items():
        if info["domain"] in url:
            return platform
    return "generic"


def extract_metadata(url: str) -> dict:
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-playlist", url],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return {"title": url, "id": _extract_id_from_url(url)}


def _extract_id_from_url(url: str) -> str:
    import re
    match = re.search(r"[?&]v=([^&]+)", url)
    if match:
        return match.group(1)
    match = re.search(r"/([^/]+?)(?:\?|$)", url)
    if match:
        return match.group(1)
    return url
    langs = languages or ["en", "zh-Hans"]
    lang_flag = ",".join(langs)
    try:
        result = subprocess.run(
            ["yt-dlp", "--write-sub", "--sub-lang", lang_flag,
             "--skip-download", "--write-auto-sub",
             "--sub-format", "vtt", "--output", "-",
             "--print-to-file", "after_move:filepath",
             url],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            return []

        import re
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".vtt", delete=False, mode="w") as f:
            result = subprocess.run(
                ["yt-dlp", "--write-auto-sub", "--sub-lang", lang_flag,
                 "--skip-download", "-o", f"{f.name[:-4]}.%(ext)s", url],
                capture_output=True, text=True, timeout=60,
            )
            vtt_path = f"{f.name[:-4]}.en.vtt"
            if Path(vtt_path).exists():
                text = Path(vtt_path).read_text(encoding="utf-8", errors="replace")
                return _parse_vtt(text)

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return []


def extract_subtitles(url: str, languages: list[str] | None = None) -> list[dict]:
    langs = languages or ["en", "zh-Hans"]
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ["yt-dlp", "--write-auto-sub", "--sub-lang", ",".join(langs),
                 "--skip-download", "-o", f"{tmpdir}/%(title)s.%(ext)s", url],
                capture_output=True, text=True, timeout=60,
            )
            for f in Path(tmpdir).rglob("*.vtt"):
                text = f.read_text(encoding="utf-8", errors="replace")
                return _parse_vtt(text)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return []


def _parse_vtt(vtt_text: str) -> list[dict]:
    import re
    subtitles = []
    lines = vtt_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if " --> " in line:
            text_lines = []
            i += 1
            while i < len(lines) and lines[i].strip():
                text_lines.append(lines[i].strip())
                i += 1
            if text_lines:
                subtitles.append({"text": " ".join(text_lines)})
        i += 1
    return subtitles


def enhanced_collect_video(url: str, extract_subtitles_flag: bool = True) -> CollectionResult:
    metadata = extract_metadata(url)
    platform = detect_platform(url)
    video_id = metadata.get("id", url)
    title = metadata.get("title") or f"video-{video_id}"

    subtitles = []
    if extract_subtitles_flag:
        langs = SUPPORTED_PLATFORMS.get(platform, {}).get("subtitle_langs", ["en"])
        subtitles = extract_subtitles(url, languages=langs)

    transcript = "\n".join(sub.get("text", "") for sub in subtitles if isinstance(sub, dict))

    body = f"Source: {url}\nPlatform: {platform}\nDuration: {metadata.get('duration', 'unknown')}\n"
    if transcript:
        body += f"\n--- Transcript ---\n{transcript[:4000]}\n"

    note = generate_note(
        {
            "title": title,
            "content": body,
            "source_type": "video",
            "source_ref": url,
            "metadata": {
                "platform": platform,
                "video_id": video_id,
                "duration": metadata.get("duration"),
                "uploader": metadata.get("uploader", ""),
                "subtitle_count": len(subtitles),
            },
        },
        template="video",
    )

    return CollectionResult(
        source_type="video",
        title=title,
        content_preview=body[:500],
        url=url,
        note_path=note["note_path"],
        gbrain_slug=note["note_id"],
        extractor="yt-dlp",
        metadata={
            "video_id": video_id,
            "platform": platform,
            "subtitle_count": len(subtitles),
        },
        subtitles=[s.get("text", "") for s in subtitles if isinstance(s, dict)],
    )


def collect_video(url: str, strategy: str = "auto") -> CollectionResult:
    return enhanced_collect_video(url, extract_subtitles_flag=(strategy != "metadata_only"))
