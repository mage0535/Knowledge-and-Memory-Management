#!/usr/bin/env python3
"""Public Linux-first dispatcher for optional SenseNova-related skills."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


AGENT_HOME = Path(
    os.environ.get("AGENT_HOME")
    or os.environ.get("HERMES_HOME")
    or os.path.expanduser("~/.hermes")
)
SKILLS_DIR = Path(os.environ.get("KMM_SKILLS_DIR", str(AGENT_HOME / "skills")))
SCRIPTS_DIR = Path(os.environ.get("KMM_SCRIPT_DIR", str(AGENT_HOME / "scripts")))


def find_skill_script(command: str) -> Path | None:
    if command in {"pdf", "ppt", "word"}:
        candidate = SCRIPTS_DIR / "doc_parse_router.py"
        return candidate if candidate.exists() else None
    skill_map = {
        "search": ("sensenova-sn-search-academic", "arxiv_search.py"),
        "wikipedia": ("sensenova-sn-search-academic", "wikipedia_search.py"),
        "reddit": ("sensenova-sn-search-social-en", "reddit_search.py"),
        "github": ("sensenova-sn-search-code", "github_search.py"),
    }
    skill_name, script_name = skill_map[command]
    for candidate in (
        SKILLS_DIR / skill_name / "scripts" / script_name,
        SKILLS_DIR / skill_name / script_name,
    ):
        if candidate.exists():
            return candidate
    return None


def dispatch(command: str, argument: str | None) -> dict:
    script_path = find_skill_script(command)
    if script_path is None:
        return {"ok": False, "error": f"script not found for command: {command}"}
    if command in {"pdf", "ppt", "word"}:
        cmd = [sys.executable, str(script_path), argument or "", "--json"]
    else:
        cmd = [sys.executable, str(script_path)]
        if argument:
            cmd.append(argument)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {"ok": False, "error": str(exc)}
    return {
        "ok": result.returncode == 0,
        "command": command,
        "script": str(script_path),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("pdf", "ppt", "word", "search", "wikipedia", "reddit", "github"))
    parser.add_argument("argument", nargs="?")
    args = parser.parse_args()
    print(json.dumps(dispatch(args.command, args.argument), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
