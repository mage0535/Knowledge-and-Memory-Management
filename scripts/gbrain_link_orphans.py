#!/usr/bin/env python3
"""Find orphan gbrain pages and mark them for later review."""

from __future__ import annotations

import json
import os
import shutil
import subprocess


GBRAIN_BIN = os.environ.get("GBRAIN_BIN") or shutil.which("gbrain") or "gbrain"


def run_gbrain(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [GBRAIN_BIN, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def get_orphans() -> list[str]:
    try:
        result = run_gbrain(["find-orphans", "--format", "json"], timeout=60)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    if result.returncode != 0:
        return []
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if isinstance(payload, list):
        return [item if isinstance(item, str) else str(item.get("slug", "")).strip() for item in payload]
    return [str(item.get("slug", "")).strip() for item in payload.get("pages", [])]


def tag_orphans(slugs: list[str], limit: int = 10) -> list[dict]:
    results = []
    for slug in slugs[:limit]:
        if not slug:
            continue
        try:
            result = run_gbrain(["tag", slug, "orphan-review"])
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            results.append({"slug": slug, "status": "error", "reason": str(exc)})
            continue
        results.append(
            {
                "slug": slug,
                "status": "ok" if result.returncode == 0 else "error",
                "stderr": result.stderr[:200],
            }
        )
    return results


def main() -> int:
    slugs = [slug for slug in get_orphans() if slug]
    results = tag_orphans(slugs)
    print(
        json.dumps(
            {
                "orphans_found": len(slugs),
                "review_tagged": sum(1 for item in results if item["status"] == "ok"),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
