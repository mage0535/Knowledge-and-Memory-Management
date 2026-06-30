"""Deterministic query preprocessing for KMM retrieval."""

from __future__ import annotations

import re

SYNONYM_MAP_EN = {
    "memory": ["recall", "remember", "retention", "storage", "context"],
    "retrieval": ["recall", "search", "retrieve", "lookup", "fetch"],
    "agent": ["assistant", "bot", "ai", "llm agent", "copilot"],
    "knowledge": ["information", "data", "content", "facts"],
    "search": ["query", "find", "retrieve", "lookup"],
    "graph": ["network", "knowledge graph", "linked", "relation"],
    "note": ["document", "markdown", "record", "entry", "file"],
    "sync": ["synchronize", "replicate", "mirror", "copy", "backup"],
    "video": ["clip", "recording", "media", "stream"],
    "document": ["file", "pdf", "report", "paper", "article"],
    "book": ["ebook", "publication", "volume", "title"],
    "python": ["code", "script", "program", "module"],
    "api": ["interface", "endpoint", "service"],
    "error": ["bug", "issue", "failure", "exception", "fault"],
    "performance": ["speed", "latency", "throughput", "efficiency", "fast"],
    "security": ["privacy", "safe", "protected", "encryption", "authentication"],
    "install": ["setup", "deploy", "configure", "bootstrap"],
    "pipeline": ["workflow", "process", "chain", "sequence"],
    "model": ["llm", "large language model", "neural", "gpt", "transformer"],
}

SYNONYM_MAP_ZH = {
    "记忆": ["recall", "remember", "memory", "remember", "context"],
    "知识": ["knowledge", "information", "knowledge base", "content"],
    "笔记": ["note", "document", "markdown", "record"],
    "搜索": ["search", "query", "find", "retrieve"],
    "采集": ["collect", "fetch", "capture", "ingest"],
    "视频": ["video", "clip", "media", "recording"],
    "文档": ["document", "file", "paper", "report"],
    "同步": ["sync", "synchronize", "backup", "mirror"],
    "书籍": ["book", "publication", "ebook"],
    "模型": ["model", "llm", "gpt"],
    "管道": ["pipeline", "workflow", "process"],
}

ENTITY_PATTERNS = {
    "url": re.compile(r"https?://[^\s>]+"),
    "file_path": re.compile(r"(?:[A-Za-z]:)?(?:/[^\s:]+)+\.\w{2,5}"),
    "python_module": re.compile(r"\b[a-z_][a-z0-9_]*\.py\b", re.IGNORECASE),
    "version": re.compile(r"\bv?\d+\.\d+(?:\.\d+)*(?:[a-z]\w*)?\b", re.IGNORECASE),
    "date": re.compile(r"\b\d{4}[-/]\d{2}[-/]\d{2}\b|\bQ[1-4]\s*\d{4}\b", re.IGNORECASE),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.IGNORECASE),
}

CJK_RANGES = (
    ("\u4e00", "\u9fff"),
    ("\u3400", "\u4dbf"),
)


def detect_language(query: str) -> str:
    cjk = sum(1 for c in query if any(lo <= c <= hi for lo, hi in CJK_RANGES))
    latin = sum(1 for c in query if c.isascii() and c.isalpha())
    if cjk and cjk >= latin * 0.2:
        return "zh"
    if latin:
        return "en"
    return "unknown"


def expand_query(query: str, max_expansions: int = 6) -> list[str]:
    lang = detect_language(query)
    tokens = _tokenize(query)
    synonym_map = SYNONYM_MAP_ZH if lang == "zh" else SYNONYM_MAP_EN

    expanded = set()
    for token in tokens:
        lower = token.lower()
        if lower in synonym_map:
            for syn in synonym_map[lower][:3]:
                expanded.add(syn)

    if expanded:
        variants = [f"{query} {syn}" for syn in list(expanded)[:max_expansions]]
        return [query] + variants
    return [query]


def extract_entities(query: str) -> list[dict[str, str]]:
    entities = []
    for entity_type, pattern in ENTITY_PATTERNS.items():
        for match in pattern.finditer(query):
            entities.append({
                "type": entity_type,
                "value": match.group(0),
                "start": match.start(),
                "end": match.end(),
            })
    entities.sort(key=lambda e: e["start"])
    return entities


def preprocess_query(query: str, language_hint: str = "") -> dict:
    lang = language_hint or detect_language(query)
    entities = extract_entities(query)
    expansions = expand_query(query)
    return {
        "original": query,
        "language": lang,
        "entities": entities,
        "expansions": expansions,
        "tokens": _tokenize(query),
    }


def _tokenize(query: str) -> list[str]:
    zh_tokens = re.findall(r"[\u4e00-\u9fff]{1,}", query)
    en_tokens = re.findall(r"[A-Za-z][A-Za-z0-9_]*", query)
    return list(dict.fromkeys(zh_tokens + en_tokens))
