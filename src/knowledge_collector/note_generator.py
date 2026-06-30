"""Note generation and knowledge-object persistence for KMM."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json

from runtime_support import ensure_directory, render_note_markdown, resolve_notes_root, stable_note_id

from .analysis import analyze_material, dumps_knowledge, render_knowledge_note


class NoteGenerator:
    """Generate readable Markdown notes plus machine-readable knowledge objects."""

    PIPELINE = {
        "step1_collect": {
            "title": "Collect source material",
            "description": "Acquire raw content from web, video, article, document, or other source adapters.",
            "tools": ["WebCollector", "VideoCollector", "ArticleCollector", "DocumentCollector"],
        },
        "step2_analyze": {
            "title": "Analyze knowledge object",
            "description": "Normalize source content and extract concepts, claims, actions, questions, risks, timeline hints, and quality signals.",
            "output": "kmm.knowledge_object.v1",
        },
        "step3_render": {
            "title": "Render readable note",
            "description": "Turn the knowledge object into Markdown while preserving source content.",
        },
        "step4_store": {
            "title": "Store note and knowledge JSON",
            "description": "Write Markdown and JSON under the KMM notes root for sidecar indexing and sync.",
        },
    }

    def generate(self, material: dict[str, Any] | str | None, source_type: str = "article", note_title: str | None = None) -> dict[str, Any]:
        """Generate a structured note and sidecar knowledge object."""

        payload = dict(material or {}) if not isinstance(material, str) else {"content": material}
        if note_title:
            payload["title"] = note_title
        payload.setdefault("source_type", source_type)

        title = str(payload.get("title") or f"{source_type}-note").strip()
        content = str(payload.get("content") or payload.get("material") or payload.get("text") or "")
        if not content.strip():
            raise ValueError("material content is required")

        domain = str(payload.get("domain") or "personal")
        source_ref = str(payload.get("source_ref") or payload.get("url") or payload.get("path") or "")
        tags = list(payload.get("tags") or ())
        metadata = dict(payload.get("metadata") or {})

        knowledge = analyze_material(payload, source_type=source_type)
        knowledge["title"] = title
        knowledge["source_ref"] = source_ref
        if tags:
            knowledge.setdefault("metadata", {})["tags"] = tags

        rendered_content = render_knowledge_note(knowledge)
        note_id = stable_note_id(title, rendered_content)
        notes_root = resolve_notes_root()
        dedup_result = _find_existing_note(notes_root, note_id, content)
        if dedup_result:
            return dedup_result

        note_dir = ensure_directory(notes_root / domain / note_id)
        note_path = note_dir / f"{note_id}.md"
        knowledge_path = note_dir / f"{note_id}.knowledge.json"

        metadata["knowledge_object"] = {
            "schema_version": knowledge["schema_version"],
            "object_id": knowledge["object_id"],
            "path": str(knowledge_path),
            "quality": knowledge.get("quality", {}),
            "keywords": knowledge.get("keywords", []),
        }

        note_path.write_text(
            render_note_markdown(
                title=title,
                content=rendered_content,
                domain=domain,
                source_type=source_type,
                source_ref=source_ref,
                tags=tags,
                metadata=metadata,
            ),
            encoding="utf-8",
        )
        knowledge_path.write_text(dumps_knowledge(knowledge), encoding="utf-8")

        return {
            "note_id": note_id,
            "note_path": str(note_path),
            "knowledge_path": str(knowledge_path),
            "domain": domain,
            "title": title,
            "analysis": knowledge,
        }


def generate_note(material, template="article", note_title=None):
    return NoteGenerator().generate(material, source_type=template, note_title=note_title)

def _find_existing_note(notes_root: Path, note_id: str, content: str) -> dict[str, str] | None:
    """Return existing note if content-hash matches, else None."""
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    for md_path in sorted(notes_root.rglob(f"{note_id}.md")):
        existing = md_path.read_text(encoding="utf-8", errors="replace")
        if hashlib.sha256(existing.encode("utf-8")).hexdigest() == content_hash:
            knowledge_path = md_path.with_suffix(".knowledge.json")
            return {
                "note_id": note_id,
                "note_path": str(md_path),
                "knowledge_path": str(knowledge_path),
                "domain": md_path.parent.parent.name if md_path.parent.parent.resolve() != notes_root.resolve() else "personal",
                "title": note_id,
                "analysis": json.loads(knowledge_path.read_text(encoding="utf-8")) if knowledge_path.exists() else {},
                "dedup": True,
            }
    return None

