#!/usr/bin/env python3
"""Linux-first nightly maintenance entrypoint for KMM."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys


SCRIPT_DIR = Path(os.environ.get("KMM_SCRIPT_DIR", Path(__file__).resolve().parent))


@dataclass(frozen=True)
class Task:
    name: str
    command: list[str]
    timeout: int = 300
    sunday_only: bool = False


def _python_task(script_name: str, *args: str, timeout: int = 300, sunday_only: bool = False) -> Task:
    return Task(
        name=script_name,
        command=[sys.executable, str(SCRIPT_DIR / script_name), *args],
        timeout=timeout,
        sunday_only=sunday_only,
    )


def _shell_task(script_name: str, *args: str, timeout: int = 300, sunday_only: bool = False) -> Task:
    return Task(
        name=script_name,
        command=["bash", str(SCRIPT_DIR / script_name), *args],
        timeout=timeout,
        sunday_only=sunday_only,
    )


TASKS = [
    _python_task("knowledge_discovery.py", timeout=120),
    _shell_task("onedrive_bidirectional_sync.sh", timeout=1800),
    _python_task("lightweight_recall.py", "--query", "recent knowledge health", "--limit", "3", timeout=60),
]


def run_task(task: Task) -> dict:
    if not Path(task.command[1]).exists():
        return {"name": task.name, "status": "skipped", "reason": "script missing"}
    try:
        result = subprocess.run(task.command, capture_output=True, text=True, timeout=task.timeout)
    except subprocess.TimeoutExpired:
        return {"name": task.name, "status": "timeout", "timeout": task.timeout}
    return {
        "name": task.name,
        "status": "ok" if result.returncode == 0 else "error",
        "returncode": result.returncode,
        "stdout": result.stdout[:400],
        "stderr": result.stderr[:400],
    }


def main() -> int:
    sunday = datetime.now().weekday() == 6
    print(f"KMM nightly maintenance @ {datetime.now().isoformat()}")
    exit_code = 0
    for task in TASKS:
        if task.sunday_only and not sunday:
            print(f"- {task.name}: skipped (sunday only)")
            continue
        result = run_task(task)
        print(f"- {task.name}: {result['status']}")
        if result["status"] == "error":
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
