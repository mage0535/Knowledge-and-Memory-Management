"""Deterministic knowledge analysis for KMM public runtime.

This module is the boundary between acquisition and note rendering. It does not
require network access or LLM credentials, so public installs and CI can produce
usable knowledge objects consistently.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Iterable

from runtime_support import slugify


SCHEMA_VERSION = "kmm.knowledge_object.v1"

STOPWORDS = {
    "about",
    "after",
    "again",
    "and",
    "also",
    "because",
    "before",
    "between",
    "could",
    "for",
    "from",
    "have",
    "into",
    "more",
    "must",
    "only",
    "should",
    "than",
    "that",
    "the",
    "their",
    "there",
    "these",
    "this",
    "through",
    "with",
    "without",
    "would",
    "your",
}

ACTION_MARKERS = (
    "todo",
    "action",
    "next",
    "should",
    "must",
    "need to",
    "needs to",
    "recommended",
    "建议",
    "需要",
    "下一步",
    "必须",
)

RISK_MARKERS = (
    "risk",
    "issue",
    "problem",
    "fail",
    "missing",
    "blocked",
    "uncertain",
    "limitation",
    "风险",
    "问题",
    "失败",
    "缺失",
    "不确定",
)

CLAIM_MARKERS = (
    " is ",
    " are ",
    " was ",
    " were ",
    " means ",
    " enables ",
    " supports ",
    " should ",
    " must ",
    " can ",
    "为",
    "是",
    "支持",
    "能够",
    "可以",
)


@dataclass
class ContentBlock:
    """Normalized content block from a source adapter."""

    type: str
    text: str
    order: int = 0
    source_ref: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeObject:
    """Machine-readable object shared by note rendering and future indexing."""

    schema_version: str
    object_id: str
    title: str
    source_type: str
    source_ref: str
    language: str
    summary: str
    keywords: list[str]
    concepts: list[dict[str, Any]]
    claims: list[dict[str, Any]]
    action_items: list[str]
    open_questions: list[str]
    risks: list[str]
    timeline: list[dict[str, str]]
    content_blocks: list[dict[str, Any]]
    quality: dict[str, Any]
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_material(material: dict[str, Any] | str | None, source_type: str = "article") -> dict[str, Any]:
    """Normalize caller material into a predictable payload."""

    if material is None:
        payload: dict[str, Any] = {}
    elif isinstance(material, str):
        payload = {"content": material}
    else:
        payload = dict(material)

    content = payload.get("content") or payload.get("material") or payload.get("text") or ""
    title = payload.get("title") or payload.get("name") or f"{source_type}-note"
    payload["title"] = str(title).strip() or f"{source_type}-note"
    payload["content"] = str(content)
    payload["source_type"] = str(payload.get("source_type") or source_type)
    payload["source_ref"] = str(payload.get("source_ref") or payload.get("url") or payload.get("path") or "")
    payload["metadata"] = dict(payload.get("metadata") or {})
    payload["content_blocks"] = _coerce_blocks(payload)
    return payload


def analyze_material(material: dict[str, Any] | str | None, source_type: str = "article") -> dict[str, Any]:
    """Analyze source material and return a JSON-serializable knowledge object."""

    return KnowledgeAnalyzer().analyze(material, source_type=source_type).to_dict()


def render_knowledge_note(knowledge: dict[str, Any], *, include_source: bool = True) -> str:
    """Render a readable Markdown note from a knowledge object."""

    lines = [
        f"# {knowledge['title']}",
        "",
        "## Executive Summary",
        knowledge.get("summary") or "No summary available.",
        "",
        "## Key Concepts",
    ]
    concepts = knowledge.get("concepts") or []
    lines.extend(_bullet(item["name"] for item in concepts) or ["- None detected."])
    lines.extend(["", "## Claims And Evidence"])
    claims = knowledge.get("claims") or []
    if claims:
        for item in claims:
            lines.append(f"- {item['text']}")
            if item.get("evidence"):
                lines.append(f"  Evidence: {item['evidence']}")
    else:
        lines.append("- None detected.")

    lines.extend(["", "## Action Items"])
    lines.extend(_bullet(knowledge.get("action_items") or []) or ["- None detected."])
    lines.extend(["", "## Open Questions"])
    lines.extend(_bullet(knowledge.get("open_questions") or []) or ["- None detected."])
    lines.extend(["", "## Risks And Gaps"])
    lines.extend(_bullet(knowledge.get("risks") or []) or ["- None detected."])

    timeline = knowledge.get("timeline") or []
    if timeline:
        lines.extend(["", "## Timeline"])
        for item in timeline:
            lines.append(f"- {item['date']}: {item['text']}")

    quality = knowledge.get("quality") or {}
    lines.extend(
        [
            "",
            "## Retrieval Metadata",
            f"- Language: {knowledge.get('language', 'unknown')}",
            f"- Keywords: {', '.join(knowledge.get('keywords') or []) or 'none'}",
            f"- Quality score: {quality.get('score', 0)}",
            f"- Extraction confidence: {quality.get('confidence', 'unknown')}",
        ]
    )

    if include_source:
        source_text = "\n\n".join(block.get("text", "") for block in knowledge.get("content_blocks") or [] if block.get("text"))
        lines.extend(["", "## Source Content", source_text.strip()])

    return "\n".join(lines).strip() + "\n"


class KnowledgeAnalyzer:
    """Dependency-light analyzer for source text, transcripts, OCR, and documents."""

    def analyze(self, material: dict[str, Any] | str | None, source_type: str = "article") -> KnowledgeObject:
        payload = normalize_material(material, source_type=source_type)
        blocks = payload["content_blocks"]
        text = "\n\n".join(block.text for block in blocks if block.text).strip()
        sentences = _split_sentences(text)
        language = _detect_language(text)
        keywords = _keywords(text, limit=12)
        concepts = _concepts(keywords, sentences)
        claims = _claims(sentences)
        action_items = _marked_sentences(sentences, ACTION_MARKERS, limit=8)
        questions = [sentence for sentence in sentences if "?" in sentence or "？" in sentence][:8]
        risks = _marked_sentences(sentences, RISK_MARKERS, limit=8)
        timeline = _timeline(sentences)
        summary = _summary(sentences, keywords)
        quality = _quality(text, blocks, claims, keywords)
        object_id = _object_id(payload["title"], text, payload["source_ref"])

        return KnowledgeObject(
            schema_version=SCHEMA_VERSION,
            object_id=object_id,
            title=payload["title"],
            source_type=payload["source_type"],
            source_ref=payload["source_ref"],
            language=language,
            summary=summary,
            keywords=keywords,
            concepts=concepts,
            claims=claims,
            action_items=action_items,
            open_questions=questions,
            risks=risks,
            timeline=timeline,
            content_blocks=[asdict(block) for block in blocks],
            quality=quality,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=payload["metadata"],
        )


def _coerce_blocks(payload: dict[str, Any]) -> list[ContentBlock]:
    raw_blocks = payload.get("content_blocks")
    blocks: list[ContentBlock] = []
    if isinstance(raw_blocks, list):
        for index, item in enumerate(raw_blocks):
            if isinstance(item, ContentBlock):
                blocks.append(item)
                continue
            if isinstance(item, dict):
                text = str(item.get("text") or item.get("content") or "").strip()
                if not text:
                    continue
                blocks.append(
                    ContentBlock(
                        type=str(item.get("type") or "text"),
                        text=text,
                        order=int(item.get("order", index)),
                        source_ref=str(item.get("source_ref") or payload.get("source_ref") or ""),
                        metadata=dict(item.get("metadata") or {}),
                    )
                )
    if not blocks:
        blocks.append(
            ContentBlock(
                type=str(payload.get("source_type") or "text"),
                text=str(payload.get("content") or ""),
                order=0,
                source_ref=str(payload.get("source_ref") or ""),
                metadata=dict(payload.get("metadata") or {}),
            )
        )
    return blocks


def _split_sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?。！？])\s+|\n+", text)
    cleaned = [re.sub(r"\s+", " ", chunk).strip(" -\t") for chunk in chunks]
    return [chunk for chunk in cleaned if len(chunk) >= 8][:80]


def _detect_language(text: str) -> str:
    if not text.strip():
        return "unknown"
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if cjk and cjk >= latin * 0.3:
        return "zh"
    if latin:
        return "en"
    return "unknown"


def _keywords(text: str, limit: int) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u4e00-\u9fff]{2,}", text.lower())
    counts: dict[str, int] = {}
    for token in tokens:
        if token in STOPWORDS:
            continue
        counts[token] = counts.get(token, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [token for token, _ in ranked[:limit]]


def _concepts(keywords: list[str], sentences: list[str]) -> list[dict[str, Any]]:
    concepts = []
    for keyword in keywords[:10]:
        evidence = next((sentence for sentence in sentences if keyword.lower() in sentence.lower()), "")
        concepts.append({"name": keyword, "evidence": evidence[:240], "weight": 1.0})
    return concepts


def _claims(sentences: list[str]) -> list[dict[str, Any]]:
    claims = []
    for sentence in sentences:
        lower = f" {sentence.lower()} "
        if any(marker in lower or marker in sentence for marker in CLAIM_MARKERS):
            claims.append({"text": sentence[:300], "evidence": sentence[:300], "confidence": 0.62})
        if len(claims) >= 10:
            break
    return claims


def _marked_sentences(sentences: list[str], markers: Iterable[str], limit: int) -> list[str]:
    found = []
    for sentence in sentences:
        lower = sentence.lower()
        if any(marker in lower or marker in sentence for marker in markers):
            found.append(sentence[:300])
        if len(found) >= limit:
            break
    return found


def _timeline(sentences: list[str]) -> list[dict[str, str]]:
    results = []
    date_pattern = re.compile(r"\b(?:20\d{2}|19\d{2})(?:[-/.年](?:0?[1-9]|1[0-2]))?(?:[-/.月](?:0?[1-9]|[12]\d|3[01]))?")
    for sentence in sentences:
        match = date_pattern.search(sentence)
        if match:
            results.append({"date": match.group(0), "text": sentence[:240]})
        if len(results) >= 8:
            break
    return results


def _summary(sentences: list[str], keywords: list[str]) -> str:
    if not sentences:
        return "No analyzable source content was provided."
    scored = []
    for index, sentence in enumerate(sentences[:30]):
        keyword_hits = sum(1 for keyword in keywords[:8] if keyword.lower() in sentence.lower())
        scored.append((keyword_hits, -index, sentence))
    selected = [item[2] for item in sorted(scored, reverse=True)[:3]]
    selected.sort(key=lambda sentence: sentences.index(sentence))
    return " ".join(selected)


def _quality(text: str, blocks: list[ContentBlock], claims: list[dict[str, Any]], keywords: list[str]) -> dict[str, Any]:
    char_count = len(text)
    score = 0.0
    if char_count >= 120:
        score += 0.3
    if len(blocks) >= 1:
        score += 0.2
    if claims:
        score += 0.25
    if len(keywords) >= 3:
        score += 0.15
    if char_count >= 1000:
        score += 0.1
    score = round(min(score, 1.0), 2)
    confidence = "high" if score >= 0.75 else "medium" if score >= 0.45 else "low"
    return {
        "score": score,
        "confidence": confidence,
        "char_count": char_count,
        "block_count": len(blocks),
        "claim_count": len(claims),
        "keyword_count": len(keywords),
    }


def _object_id(title: str, text: str, source_ref: str) -> str:
    digest = hashlib.sha256(f"{title}\n{source_ref}\n{text}".encode("utf-8")).hexdigest()[:16]
    return f"ko-{slugify(title)}-{digest}"


def _bullet(items: Iterable[str]) -> list[str]:
    return [f"- {item}" for item in items if str(item).strip()]


def dumps_knowledge(knowledge: dict[str, Any]) -> str:
    """Serialize a knowledge object with stable formatting."""

    return json.dumps(knowledge, ensure_ascii=False, indent=2, sort_keys=True)

def migrate_knowledge_object(obj: dict[str, Any], target_version: str) -> dict[str, Any]:
    """Migrate a knowledge object to a target schema version."""
    current = obj.get("schema_version", "kmm.knowledge_object.v1")
    if current == target_version:
        return obj
    migrations: dict[tuple[str, str], Any] = {
        ("kmm.knowledge_object.v1", "kmm.knowledge_object.v1"): lambda o: o,
    }
    key = (current, target_version)
    if key in migrations:
        result = migrations[key](dict(obj))
        result["schema_version"] = target_version
        return result
    raise ValueError(
        f"No migration path from {current} to {target_version}. "
        f"Supported versions: {sorted(set(k for ks in migrations for k in ks))}"
    )


def _compact_knowledge_object(obj: dict[str, Any]) -> dict[str, Any]:
    """Remove optional empty fields to reduce storage size."""
    optional_empty = ("action_items", "open_questions", "risks", "timeline", "metadata")
    result = dict(obj)
    for key in optional_empty:
        if key in result and not result[key]:
            del result[key]
    return result


SCHEMA_VERSIONS = ["kmm.knowledge_object.v1"]


RELATION_MARKERS = (
    "uses", "depends on", "relates to", "implements", "extends",
    "provides", "requires", "supports", "integrates with",
    "calls", "delegates to", "composes", "contains",
    "references", "links to", "connects to",
    "使用", "依赖", "调用", "集成", "继承", "实现",
)


def extract_relations(knowledge: dict[str, Any]) -> list[dict[str, Any]]:
    concepts = knowledge.get("concepts", [])
    claims = knowledge.get("claims", [])
    relations = []

    concept_names = {c.get("name", "").lower() for c in concepts if c.get("name")}

    for claim in claims:
        text = claim.get("text", "")
        if len(text) < 10:
            continue
        text_lower = text.lower()
        for marker in RELATION_MARKERS:
            idx = text_lower.find(marker)
            if idx < 0:
                continue
            source = _find_nearest_concept(text[:idx], concept_names)
            target = _find_nearest_concept(text[idx + len(marker):], concept_names)
            if source and target and source != target:
                relations.append({
                    "source": source,
                    "target": target,
                    "relation": marker,
                    "evidence": text[:200],
                    "confidence": claim.get("confidence", 0.5),
                })
    return relations[:30]


def _find_nearest_concept(text_segment: str, concept_names: set[str]) -> str | None:
    text_lower = text_segment.lower()
    for name in concept_names:
        if name in text_lower:
            return name
    return next(iter(concept_names), None) if concept_names else None
