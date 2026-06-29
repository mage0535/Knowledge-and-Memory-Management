#!/usr/bin/env python3
"""Run a gray-environment validation suite for KMM."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_DIR = Path(os.environ.get("KMM_PLUGIN_DIR", SCRIPT_DIR.parent / "src"))
PYTHON_BIN = os.environ.get("KMM_PYTHON", sys.executable)
DEFAULT_QUERIES = (
    "agent memory architecture",
    "policy memory",
    "recent sessions",
)


def run_command(name: str, command: list[str], timeout: int = 120) -> dict:
    env = os.environ.copy()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, env=env)
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {"name": name, "status": "error", "reason": str(exc)}
    return {
        "name": name,
        "status": "ok" if result.returncode == 0 else "error",
        "returncode": result.returncode,
        "stdout": result.stdout[:800],
        "stderr": result.stderr[:800],
    }


def import_smoke() -> dict:
    command = [
        PYTHON_BIN,
        "-c",
        (
            "import sys; "
            f"sys.path.insert(0, {json.dumps(str(PLUGIN_DIR))}); "
            "import knowledge_collector, notes_rag, cloud_sync; "
            "print('ok')"
        ),
    ]
    return run_command("import_smoke", command)


def knowledge_discovery_check() -> dict:
    return run_command("knowledge_discovery", [PYTHON_BIN, str(SCRIPT_DIR / "knowledge_discovery.py")])


def recall_check(query: str) -> dict:
    return run_command(
        f"recall:{query}",
        [PYTHON_BIN, str(SCRIPT_DIR / "lightweight_recall.py"), "--query", query, "--limit", "5"],
        timeout=180,
    )


def shadow_compare_check() -> dict:
    return run_command(
        "shadow_compare",
        [
            PYTHON_BIN,
            str(SCRIPT_DIR / "recall_shadow_compare.py"),
            "--baseline",
            PYTHON_BIN,
            str(SCRIPT_DIR / "lightweight_recall.py"),
            "--candidate",
            PYTHON_BIN,
            str(SCRIPT_DIR / "lightweight_recall.py"),
        ],
        timeout=240,
    )


def sync_dry_run_check() -> dict:
    remote = os.environ.get("KMM_SYNC_REMOTE", "")
    if not remote:
        return {"name": "sync_dry_run", "status": "skipped", "reason": "KMM_SYNC_REMOTE not configured"}
    env = os.environ.copy()
    env["KMM_SYNC_DRY_RUN"] = "true"
    env["KMM_SYNC_RESYNC"] = env.get("KMM_SYNC_RESYNC", "true")
    try:
        result = subprocess.run(
            ["bash", str(SCRIPT_DIR / "onedrive_bidirectional_sync.sh")],
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {"name": "sync_dry_run", "status": "error", "reason": str(exc)}
    return {
        "name": "sync_dry_run",
        "status": "ok" if result.returncode == 0 else "error",
        "returncode": result.returncode,
        "stdout": result.stdout[:800],
        "stderr": result.stderr[:800],
    }


def main() -> int:
    results = [
        import_smoke(),
        knowledge_discovery_check(),
        *(recall_check(query) for query in DEFAULT_QUERIES),
        shadow_compare_check(),
        sync_dry_run_check(),
    ]
    summary = {
        "ok": all(item["status"] in {"ok", "skipped"} for item in results),
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
