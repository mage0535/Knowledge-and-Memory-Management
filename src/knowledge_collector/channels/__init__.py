"""Channel adapter framework for defended-platform content ingestion.

Every adapter emits normalized ContentBlock lists so downstream
processing (analysis, note generation, retrieval) remains channel-agnostic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ChannelContent:
    source_platform: str
    source_url: str
    title: str
    author: str = ""
    published_at: str = ""
    language: str = "unknown"
    content_blocks: list[dict[str, Any]] = field(default_factory=list)
    image_assets: list[str] = field(default_factory=list)
    extraction_quality: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


class ChannelAdapter(ABC):
    """Base class for platform-specific content adapters."""

    platform: str = "generic"

    @abstractmethod
    def can_handle(self, url_or_id: str) -> bool:
        """Check if this adapter can handle the given URL or identifier."""
        ...

    @abstractmethod
    def fetch(self, url_or_id: str) -> ChannelContent:
        """Fetch and normalize content from the platform."""
        ...

    def normalize(self, content: ChannelContent) -> list[dict[str, Any]]:
        """Convert ChannelContent to normalized ContentBlock list."""
        return content.content_blocks


CHANNEL_REGISTRY: dict[str, ChannelAdapter] = {}


def register_adapter(adapter: ChannelAdapter) -> None:
    CHANNEL_REGISTRY[adapter.platform] = adapter


def resolve_adapter(platform: str) -> ChannelAdapter | None:
    return CHANNEL_REGISTRY.get(platform)


def collect_from_channel(platform: str, url_or_id: str) -> ChannelContent | None:
    adapter = resolve_adapter(platform)
    if adapter and adapter.can_handle(url_or_id):
        return adapter.fetch(url_or_id)
    return None


def list_supported_platforms() -> list[str]:
    return list(CHANNEL_REGISTRY.keys())


# Auto-register built-in adapters
import knowledge_collector.channels.hackernews  # noqa: E402, F401
import knowledge_collector.channels.wechat  # noqa: E402, F401
