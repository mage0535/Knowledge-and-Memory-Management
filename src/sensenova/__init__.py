"""
Optional SenseNova adapter helpers.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def _dispatcher_path() -> Path:
    agent_home = Path(
        os.environ.get("AGENT_HOME")
        or os.environ.get("HERMES_HOME")
        or os.path.expanduser("~/.hermes")
    )
    return agent_home / "scripts" / "sensenova_dispatcher.py"


def _run_dispatch(mode: str, path: str) -> dict:
    dispatcher = _dispatcher_path()
    if not dispatcher.exists():
        return {"error": f"sensenova dispatcher not found: {dispatcher}"}
    result = subprocess.run(
        [sys.executable, str(dispatcher), mode, path],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "mode": mode,
        "path": path,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def analyze_pdf(path: str) -> dict:
    return _run_dispatch("pdf", path)


def analyze_ppt(path: str) -> dict:
    return _run_dispatch("ppt", path)


def analyze_word(path: str) -> dict:
    return _run_dispatch("word", path)
