#!/usr/bin/env python3
"""Discover recently modified notes and optionally mirror them into gbrain."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time
import sys


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

from runtime_support import resolve_notes_root


def discover_new_notes(days: int = 7) -> list[dict]:
    cutoff = time.time() - (days * 86400)
    results = []
    for path in sorted(resolve_notes_root().rglob("*.md")):
        try:
            stat = path.stat()
        except OSError:
            continue
        if stat.st_mtime < cutoff:
            continue
        results.append(
            {
                "title": path.stem,
                "path": str(path),
                "modified_at": stat.st_mtime,
            }
        )
    return results


def ingest_to_gbrain(note: dict) -> dict:
    gbrain = os.environ.get("GBRAIN_BIN", "gbrain")
    content = Path(note["path"]).read_text(encoding="utf-8", errors="replace")[:4000]
    slug = f"note-{Path(note['path']).stem}"
    try:
        result = subprocess.run(
            [gbrain, "put", slug],
            input=content,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"slug": slug, "status": "skipped", "reason": str(exc)}
    return {"slug": slug, "status": "ok" if result.returncode == 0 else "error", "stderr": result.stderr[:200]}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-home", default=os.environ.get("AGENT_HOME", ""))
    parser.add_argument("--days", type=int, default=int(os.environ.get("KMM_DISCOVERY_DAYS", "7")))
    args, _ = parser.parse_known_args()
    if args.agent_home:
        os.environ["AGENT_HOME"] = args.agent_home
    days = args.days
    notes = discover_new_notes(days=days)
    payload = {"notes": notes, "count": len(notes)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
