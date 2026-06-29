#!/usr/bin/env python3
"""Compare recall results between the current runtime and an alternate command."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import shlex


DEFAULT_QUERIES = (
    "agent memory architecture",
    "policy memory",
    "recent sessions",
)


def run_recall(command: list[str], query: str) -> dict:
    full_command = [*command, "--query", query, "--limit", "5"]
    if "--json" not in full_command:
        full_command.append("--json")
    result = subprocess.run(full_command, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        return {"ok": False, "query": query, "stderr": result.stderr[:400], "stdout": result.stdout[:400]}
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "query": query, "stderr": "invalid json", "stdout": result.stdout[:400]}
    return {"ok": True, "query": query, "payload": payload}


def compare_payloads(left: dict, right: dict) -> dict:
    left_layers = left.get("payload", {}).get("layers", {})
    right_layers = right.get("payload", {}).get("layers", {})
    return {
        "query": left["query"],
        "left_ok": left["ok"],
        "right_ok": right["ok"],
        "left_counts": {key: len(value) for key, value in left_layers.items()},
        "right_counts": {key: len(value) for key, value in right_layers.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", nargs="+", default=[sys.executable, "scripts/lightweight_recall.py"])
    parser.add_argument("--candidate", nargs="+", required=True)
    parser.add_argument("--queries-file", default="")
    args = parser.parse_args()

    if args.queries_file:
        queries = tuple(line.strip() for line in Path(args.queries_file).read_text(encoding="utf-8").splitlines() if line.strip())
    else:
        queries = DEFAULT_QUERIES

    baseline_cmd = args.baseline
    candidate_cmd = args.candidate
    results = []
    for query in queries:
        left = run_recall(baseline_cmd, query)
        right = run_recall(candidate_cmd, query)
        results.append(compare_payloads(left, right))
    print(json.dumps({"queries": list(queries), "comparisons": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
