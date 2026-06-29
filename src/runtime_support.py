"""
Shared runtime helpers for the public KMM package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
import re
from typing import Iterable

import yaml


def resolve_agent_home() -> Path:
    raw = os.environ.get("AGENT_HOME") or os.environ.get("HERMES_HOME")
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".hermes"


def resolve_knowledge_root() -> Path:
    raw = os.environ.get("KMM_DATA_DIR")
    if raw:
        return Path(raw).expanduser()
    return resolve_agent_home() / "knowledge"


def resolve_notes_root() -> Path:
    explicit = os.environ.get("KMM_NOTES_DIR")
    if explicit:
        return Path(explicit).expanduser()
    candidates = [
        resolve_knowledge_root() / "notes",
        Path.home() / "knowledge" / "notes",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify(value: str) -> str:
    text = (value or "").strip().lower()
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "note"


def stable_note_id(title: str, content: str) -> str:
    digest = hashlib.sha256(f"{title}\n{content}".encode("utf-8")).hexdigest()[:12]
    return f"note-{slugify(title)}-{digest}"


@dataclass
class CollectionResult:
    source_type: str
    title: str
    content_preview: str
    url: str = ""
    note_path: str = ""
    gbrain_slug: str = ""
    extractor: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
    subtitles: list[str] = field(default_factory=list)
    frames: list[str] = field(default_factory=list)


def render_note_markdown(
    *,
    title: str,
    content: str,
    domain: str,
    source_type: str,
    source_ref: str = "",
    tags: Iterable[str] | None = None,
    metadata: dict[str, object] | None = None,
) -> str:
    frontmatter = {
        "title": title,
        "domain": domain,
        "source_type": source_type,
        "source_ref": source_ref,
        "tags": list(tags or ()),
        "metadata": dict(metadata or {}),
    }
    return f"---\n{yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()}\n---\n\n{content.strip()}\n"

