"""Knowledge-object indexing helper for the memory sidecar.

Provides functions that hermes-memory-installer can import to extend
governance indexing from Markdown notes to knowledge JSON objects.
"""

from __future__ import annotations

import json, os, hashlib
from pathlib import Path


def resolve_knowledge_dir() -> Path:
    agent_home = Path(
        os.environ.get("AGENT_HOME") or os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))
    ).expanduser()
    return agent_home / "knowledge"


def build_knowledge_object_rows(notes_dir: Path, indexed_at: float) -> tuple[list[tuple], list[tuple]]:
    rows: list[tuple] = []
    fts_rows: list[tuple] = []

    for kjson in sorted(notes_dir.rglob("*.knowledge.json")):
        try:
            obj = json.loads(kjson.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        object_id = obj.get("object_id", kjson.stem)
        source_path = str(kjson.relative_to(notes_dir)).replace("\\", "/")
        title = obj.get("title", "")[:200]
        summary = obj.get("summary", "")[:800]
        keywords = ", ".join(obj.get("keywords", [])[:20])[:400]
        concepts = json.dumps(obj.get("concepts", [])[:10], ensure_ascii=False)[:2000]
        claims = json.dumps(obj.get("claims", [])[:10], ensure_ascii=False)[:2000]
        action_items = "\n".join(obj.get("action_items", [])[:5])[:500]
        risks = "\n".join(obj.get("risks", [])[:5])[:500]
        quality_score = round(obj.get("quality", {}).get("score", 0), 4)
        schema_version = obj.get("schema_version", "")
        created_at = obj.get("created_at", "")
        language = obj.get("language", "unknown")

        search_text = " ".join(
            part for part in [title, summary, keywords, " ".join(obj.get("action_items", [])[:3])] if part
        )[:4000]

        row = (
            object_id, source_path, schema_version, title, summary, keywords,
            concepts, claims, action_items, risks, quality_score, created_at, language,
            search_text, indexed_at, float(kjson.stat().st_mtime),
        )
        rows.append(row)

        fts_rows.append((
            object_id, source_path, title, summary, keywords, search_text,
        ))

    return rows, fts_rows


def compute_knowledge_objects_signature(notes_dir: Path) -> str:
    if not notes_dir.exists():
        return "missing"
    parts = []
    for kjson in sorted(notes_dir.rglob("*.knowledge.json")):
        rel = str(kjson.relative_to(notes_dir)).replace("\\", "/")
        content_hash = hashlib.sha1()
        with kjson.open("rb") as f:
            for chunk in iter(lambda: f.read(1048576), b""):
                content_hash.update(chunk)
        parts.append(f"{rel}:{content_hash.hexdigest()}")
    return hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS knowledge_object_index (
    object_id TEXT PRIMARY KEY,
    source_path TEXT NOT NULL,
    schema_version TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL DEFAULT '',
    summary TEXT NOT NULL DEFAULT '',
    keywords TEXT NOT NULL DEFAULT '',
    concepts_json TEXT NOT NULL DEFAULT '[]',
    claims_json TEXT NOT NULL DEFAULT '[]',
    action_items TEXT NOT NULL DEFAULT '',
    risks TEXT NOT NULL DEFAULT '',
    quality_score REAL NOT NULL DEFAULT 0.0,
    created_at TEXT NOT NULL DEFAULT '',
    language TEXT NOT NULL DEFAULT 'unknown',
    search_text TEXT NOT NULL DEFAULT '',
    indexed_at REAL NOT NULL DEFAULT 0.0,
    modified_at REAL NOT NULL DEFAULT 0.0
);

CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_object_index_fts USING fts5(
    object_id, source_path, title, summary, keywords, search_text
);
"""


def ensure_object_schema(conn) -> None:
    conn.executescript(SCHEMA_SQL)


def refresh_knowledge_object_index(
    conn,
    *,
    notes_dir: Path,
    indexed_at: float,
    force: bool = False,
) -> dict:
    signature = compute_knowledge_objects_signature(notes_dir)
    try:
        prev = conn.execute(
            "SELECT value FROM governance_meta WHERE key = 'knowledge_objects_signature'"
        ).fetchone()
        previous_signature = str(prev[0]) if prev else None
    except Exception:
        previous_signature = None

    if not force and signature == previous_signature:
        count = conn.execute("SELECT COUNT(*) FROM knowledge_object_index").fetchone()[0]
        return {"reused": True, "count": int(count), "signature": signature}

    ensure_object_schema(conn)
    rows, fts_rows = build_knowledge_object_rows(notes_dir, indexed_at)

    conn.execute("DELETE FROM knowledge_object_index")
    conn.execute("DELETE FROM knowledge_object_index_fts")
    conn.executemany(
        """INSERT INTO knowledge_object_index (
            object_id, source_path, schema_version, title, summary, keywords,
            concepts_json, claims_json, action_items, risks, quality_score,
            created_at, language, search_text, indexed_at, modified_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    for fts_row in fts_rows:
        conn.execute(
            "INSERT INTO knowledge_object_index_fts (object_id, source_path, title, summary, keywords, search_text) VALUES (?, ?, ?, ?, ?, ?)",
            fts_row,
        )

    conn.execute(
        "INSERT INTO governance_meta (key, value) VALUES ('knowledge_objects_signature', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (signature,),
    )
    return {"reused": False, "count": len(rows), "signature": signature}
