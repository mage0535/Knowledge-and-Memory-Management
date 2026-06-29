#!/usr/bin/env python3
"""Scan gbrain timeline-heavy pages and emit compaction candidates."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
import shutil
import subprocess


GBRAIN_BIN = os.environ.get("GBRAIN_BIN") or shutil.which("gbrain") or "gbrain"
KNOWN_PAGES = tuple(
    item.strip()
    for item in os.environ.get(
        "KMM_GBRAIN_KNOWN_PAGES",
        "",
    ).split(",")
    if item.strip()
)


def run_gbrain_call(tool: str, payload: dict) -> list[dict] | None:
    try:
        result = subprocess.run(
            [GBRAIN_BIN, "call", tool, json.dumps(payload, ensure_ascii=False)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, list) else parsed.get("entries")


def scan_compaction_candidates(cutoff_days: int = 90, min_entries: int = 5) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=cutoff_days)
    candidates = []
    for slug in KNOWN_PAGES:
        entries = run_gbrain_call("get_timeline", {"slug": slug}) or []
        old_entries = []
        for entry in entries:
            date_text = str(entry.get("date", "")).replace("Z", "+00:00")
            try:
                dt = datetime.fromisoformat(date_text)
            except ValueError:
                continue
            if dt < cutoff:
                old_entries.append(entry)
        if len(old_entries) >= min_entries:
            candidates.append(
                {
                    "slug": slug,
                    "old_count": len(old_entries),
                    "total_entries": len(entries),
                    "oldest_date": str(old_entries[0].get("date", ""))[:10],
                    "sample_summaries": [str(item.get("summary", ""))[:100] for item in old_entries[:5]],
                }
            )
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = scan_compaction_candidates()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if not payload:
            print("No compaction candidates")
        for item in payload:
            print(f"{item['slug']}: {item['old_count']} old / {item['total_entries']} total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
