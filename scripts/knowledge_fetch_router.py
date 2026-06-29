#!/usr/bin/env python3
"""Public knowledge fetch router."""

from __future__ import annotations

import json
import os
from pathlib import Path
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

from knowledge_collector.web import collect_web


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: knowledge_fetch_router.py <url>", file=sys.stderr)
        return 1
    result = collect_web(sys.argv[1])
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
