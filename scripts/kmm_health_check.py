#!/usr/bin/env python3
"""KMM health artifact generator.

Produces: $AGENT_HOME/knowledge/kmm-health.json
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from runtime_support import resolve_agent_home, resolve_notes_root


def collect_health() -> dict:
    agent_home = resolve_agent_home()
    notes_root = resolve_notes_root()

    note_count = sum(1 for _ in notes_root.rglob("*.md")) if notes_root.exists() else 0
    knowledge_count = sum(1 for _ in notes_root.rglob("*.knowledge.json")) if notes_root.exists() else 0

    domains = {}
    for child in notes_root.iterdir() if notes_root.exists() else []:
        if child.is_dir() and not child.name.startswith("."):
            domains[child.name] = sum(1 for _ in child.rglob("*.md"))

    manifest_path = agent_home / "scripts" / "kmm-install-manifest.txt"
    install_info = {}
    if manifest_path.exists():
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                install_info[k.strip()] = v.strip()

    sync_log = Path("/var/log/rclone-sync.log")
    last_sync = None
    if sync_log.exists():
        last_sync = datetime.fromtimestamp(sync_log.stat().st_mtime, tz=timezone.utc).isoformat()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kmm_version": "0.1.0",
        "agent_home": str(agent_home),
        "notes_root": str(notes_root),
        "notes": {
            "total": note_count,
            "knowledge_objects": knowledge_count,
            "by_domain": domains,
        },
        "install": install_info,
        "sync": {
            "last_sync_log_mtime": last_sync,
        },
        "services": {
            "gbrain": _check_port(8787),
            "hindsight": _check_port(8890),
        },
    }


def _check_port(port: int) -> bool:
    import socket
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=2):
            return True
    except OSError:
        return False


def main() -> int:
    health = collect_health()
    output = resolve_agent_home() / "knowledge" / "kmm-health.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(health, ensure_ascii=False, indent=2))
    print(f"kmm-health.json written ({output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
