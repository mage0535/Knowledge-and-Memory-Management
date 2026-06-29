#!/usr/bin/env python3
"""Lightweight multi-layer recall for local notes plus optional external stores."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_HOME = Path(
    os.environ.get("AGENT_HOME")
    or os.environ.get("HERMES_HOME")
    or (Path.home() / ".hermes")
).expanduser()
PLUGIN_ROOT = Path(
    os.environ.get("KMM_PLUGIN_DIR")
    or (AGENT_HOME / "knowledge-plugin")
).expanduser()
for candidate in (PLUGIN_ROOT, REPO_ROOT / "src"):
    if candidate.exists():
        sys.path.insert(0, str(candidate))
from notes_rag import search_notes
from runtime_support import resolve_agent_home


STATE_DB = resolve_agent_home() / "state.db"


def l1_fts(query: str, limit: int) -> list[dict]:
    if not STATE_DB.exists():
        return []
    try:
        conn = sqlite3.connect(str(STATE_DB))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT s.id AS session_id, s.title, m.content
            FROM messages m
            JOIN sessions s ON s.id = m.session_id
            WHERE lower(m.content) LIKE lower(?)
            LIMIT ?
            """,
            (f"%{query}%", limit),
        ).fetchall()
        return [
            {
                "layer": "fts5",
                "title": row["title"] or row["session_id"],
                "content": (row["content"] or "")[:240],
                "score": 0.5,
            }
            for row in rows
        ]
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def l2_hindsight(query: str, limit: int) -> list[dict]:
    base = "http://127.0.0.1:8890/v1/default/banks/hermes/memories/recall"
    timeout_seconds = float(os.environ.get("KMM_HINDSIGHT_TIMEOUT", "3"))
    payload = json.dumps({"query": query, "limit": limit}).encode("utf-8")
    request = Request(base, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
    except (URLError, TimeoutError, ValueError):
        return []
    results = data.get("results") or data.get("memories") or []
    return [
        {
            "layer": "hindsight",
            "title": item.get("id", "memory"),
            "content": (item.get("content") or item.get("text") or "")[:240],
            "score": float(item.get("score", 0.4) or 0.4),
        }
        for item in results[:limit]
    ]


def l3_gbrain(query: str, limit: int) -> list[dict]:
    timeout_seconds = float(os.environ.get("KMM_GBRAIN_TIMEOUT", "5"))
    try:
        proc = subprocess.run(
            ["gbrain", "search", query, "--limit", str(limit)],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if proc.returncode != 0:
        return []
    results = []
    for line in proc.stdout.splitlines()[:limit]:
        line = line.strip()
        if not line:
            continue
        results.append({"layer": "gbrain", "title": line[:80], "content": line[:240], "score": 0.3})
    return results


def recall(query: str, limit: int) -> dict:
    started = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_local = executor.submit(lambda: search_notes(query)[:limit])
        future_fts = executor.submit(l1_fts, query, limit)
        future_hindsight = executor.submit(l2_hindsight, query, limit)
        future_gbrain = executor.submit(l3_gbrain, query, limit)
        layers = {
            "local_notes": future_local.result(),
            "fts5": future_fts.result(),
            "hindsight": future_hindsight.result(),
            "gbrain": future_gbrain.result(),
        }
    return {"query": query, "elapsed": round(time.time() - started, 3), "layers": layers}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(recall(args.query, args.limit), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
