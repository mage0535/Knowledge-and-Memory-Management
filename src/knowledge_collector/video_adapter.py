"""Video platform adapter framework."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class VideoMetadata:
    platform: str
    video_id: str
    title: str
    url: str
    author: str = ""
    duration: float = 0.0
    published_at: str = ""
    description: str = ""
    thumbnail_url: str = ""


@dataclass
class VideoTimeline:
    timestamp_start: float
    timestamp_end: float
    text: str
    summary: str = ""
    keyframe_path: str = ""
    ocr_text: str = ""


@dataclass
class VideoContent:
    metadata: VideoMetadata = field(default_factory=lambda: VideoMetadata("", "", "", ""))
    subtitles: list[dict[str, Any]] = field(default_factory=list)
    transcript: str = ""
    timeline_blocks: list[VideoTimeline] = field(default_factory=list)
    keyframes: list[str] = field(default_factory=list)
    extraction_quality: str = "unknown"


class VideoAdapter(ABC):
    platform: str = "generic"

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        ...

    @abstractmethod
    def fetch_metadata(self, url: str) -> VideoMetadata:
        ...

    def fetch_subtitles(self, video_id: str, languages: list[str] | None = None) -> list[dict[str, Any]]:
        return []

    def fetch_audio_path(self, url: str) -> Path | None:
        return None

    def collect(self, url: str) -> VideoContent:
        metadata = self.fetch_metadata(url)
        subtitles = self.fetch_subtitles(metadata.video_id)
        transcript = "\n".join(
            sub.get("text", "") for sub in subtitles if isinstance(sub, dict)
        )
        return VideoContent(
            metadata=metadata,
            subtitles=subtitles,
            transcript=transcript,
        )


VIDEO_ADAPTERS: dict[str, VideoAdapter] = {}


def register_video_adapter(adapter: VideoAdapter) -> None:
    VIDEO_ADAPTERS[adapter.platform] = adapter


def resolve_video_adapter(url: str) -> VideoAdapter | None:
    for adapter in VIDEO_ADAPTERS.values():
        if adapter.can_handle(url):
            return adapter
    return None
