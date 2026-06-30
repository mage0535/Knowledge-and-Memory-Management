"""Performance regression test — compares current benchmarks against stored baselines.

Run: python3 tests/bench_kmm_performance.py --save tests/baselines/bench-v0.2.0.json
CI:   python3 tests/bench_kmm_performance.py --compare tests/baselines/bench-v0.2.0.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
BASELINE_DIR = REPO / "tests" / "baselines"
BASELINE_FILE = BASELINE_DIR / "bench-v0.2.0.json"

# Regression thresholds: fail if metric degrades beyond these limits
THRESHOLDS = {
    "recall_warm.p50_ms": 1.5,
    "ingestion.notes_per_second": 0.3,
    "query_preprocessing.queries_per_second": 0.3,
    "knowledge_analysis.avg_ms_per_analysis": 3.0,
    "memory.rss_mb": 2.0,
}

LOWER_IS_BETTER = {"recall_warm.p50_ms", "knowledge_analysis.avg_ms_per_analysis", "memory.rss_mb"}


def run_benchmarks() -> dict:
    sys.path.insert(0, str(REPO / "tests"))
    from bench_kmm_performance import run_all_benchmarks
    return run_all_benchmarks()


def save_baseline(path: Path) -> None:
    results = run_benchmarks()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"Baseline saved to {path}")


def compare_to_baseline(baseline_path: Path) -> tuple[bool, list[str]]:
    """Returns (passed, violations)."""
    if not baseline_path.exists():
        return True, [f"no baseline at {baseline_path}"]

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current = run_benchmarks()

    violations = []
    checks = {
        "recall_warm.p50_ms": _get(current, ["recall_warm", "p50_ms"], 0),
        "ingestion.notes_per_second": _get(current, ["ingestion", "notes_per_second"], 0),
        "query_preprocessing.queries_per_second": _get(current, ["query_preprocessing", "queries_per_second"], 0),
        "knowledge_analysis.avg_ms_per_analysis": _get(current, ["knowledge_analysis", "avg_ms_per_analysis"], 0),
        "memory.rss_mb": _get(current, ["memory", "rss_mb"], 0),
    }

    for metric, current_val in checks.items():
        baseline_val = _get_nested(baseline, metric.split("."), 0)
        if baseline_val <= 0 or current_val <= 0:
            continue
        threshold = THRESHOLDS.get(metric, 1.0)
        ratio = _ratio(metric, baseline_val, current_val)
        is_lower_better = metric in LOWER_IS_BETTER
        failed = (is_lower_better and ratio > threshold) or (not is_lower_better and ratio < threshold)
        if failed:
            violations.append(
                f"[REGRESSION] {metric}: baseline={baseline_val:.1f} current={current_val:.1f} ratio={ratio:.2f}x (threshold={threshold}x)"
            )
        else:
            print(f"  OK  {metric}: {baseline_val:.1f} -> {current_val:.1f} ({ratio:.2f}x)")

    return len(violations) == 0, violations


def _get(d, keys, default):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
    return d if not isinstance(d, dict) else default


def _get_nested(d, keys, default):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
    return d if isinstance(d, (int, float)) else default


def _ratio(metric, baseline, current):
    """For latency/memory metrics: current/baseline (higher=worse).
    For throughput metrics: baseline/current (higher=worse)."""
    if "per_second" in metric:
        return baseline / max(current, 0.001)
    return current / max(baseline, 0.001)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", type=Path, help="Save current benchmarks as baseline")
    parser.add_argument("--compare", type=Path, help="Compare against a stored baseline")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    if args.save:
        save_baseline(args.save)
        return 0

    if args.compare:
        passed, violations = compare_to_baseline(args.compare)
        if args.json:
            print(json.dumps({"passed": passed, "violations": violations}, indent=2))
        else:
            for v in violations:
                print(v)
        return 0 if passed else 1

    # Default: just print current results
    results = run_benchmarks()
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
