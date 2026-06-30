"""KMM performance benchmarks — recall latency, ingestion throughput, memory."""

from __future__ import annotations

import time
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))


def bench_recall_cold(query: str = "agent memory architecture", iterations: int = 5) -> dict:
    from notes_rag import search_notes

    latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        results = search_notes(query)
        elapsed = time.perf_counter() - start
        latencies.append(elapsed)
    latencies.sort()
    return {
        "query": query,
        "iterations": iterations,
        "p50_ms": round(latencies[len(latencies) // 2] * 1000, 2),
        "p99_ms": round(latencies[min(int(len(latencies) * 0.99), len(latencies) - 1)] * 1000, 2),
        "min_ms": round(min(latencies) * 1000, 2),
        "max_ms": round(max(latencies) * 1000, 2),
        "result_count": len(results),
    }


def bench_recall_warm(query: str = "agent memory architecture", warm_iterations: int = 3, bench_iterations: int = 10) -> dict:
    from notes_rag import search_notes

    for _ in range(warm_iterations):
        search_notes(query)

    latencies = []
    for _ in range(bench_iterations):
        start = time.perf_counter()
        search_notes(query)
        elapsed = time.perf_counter() - start
        latencies.append(elapsed)
    latencies.sort()
    return {
        "query": query,
        "warm_iterations": warm_iterations,
        "bench_iterations": bench_iterations,
        "p50_ms": round(latencies[len(latencies) // 2] * 1000, 2),
        "p99_ms": round(latencies[min(int(len(latencies) * 0.99), len(latencies) - 1)] * 1000, 2),
        "avg_ms": round(sum(latencies) / len(latencies) * 1000, 2),
    }


def bench_ingestion_throughput(count: int = 50) -> dict:
    from knowledge_collector.note_generator import generate_note

    start = time.perf_counter()
    for i in range(count):
        generate_note(
            {"title": f"Bench Note {i}", "content": f"Performance test content for note number {i} with some additional text to simulate real-world note generation throughput benchmarks."},
            template="note",
        )
    elapsed = time.perf_counter() - start
    return {
        "notes_generated": count,
        "total_seconds": round(elapsed, 2),
        "notes_per_second": round(count / elapsed, 1),
        "avg_ms_per_note": round(elapsed / count * 1000, 2),
    }


def bench_query_preprocessing(iterations: int = 100) -> dict:
    from knowledge_collector.query_rewrite import preprocess_query

    queries = [
        "agent memory architecture with hybrid retrieval",
        "比亚迪 2026 年第一季度 财报",
        "Python RAG pipeline 性能优化 with Qdrant",
    ]
    start = time.perf_counter()
    for _ in range(iterations // len(queries)):
        for q in queries:
            preprocess_query(q)
    elapsed = time.perf_counter() - start
    return {
        "total_queries": iterations,
        "total_seconds": round(elapsed, 4),
        "queries_per_second": round(iterations / elapsed, 1),
        "avg_us_per_query": round(elapsed / iterations * 1_000_000, 1),
    }


def bench_knowledge_analysis(iterations: int = 20) -> dict:
    from knowledge_collector.analysis import analyze_material

    text = (
        "Layered recall is a memory architecture that combines multiple retrieval strategies. "
        "It should preserve source provenance and reduce context risk. "
        "Next, index claims and concepts for retrieval. "
        "Action: implement hybrid search. Risk: latency may increase with vector search."
    )
    start = time.perf_counter()
    for _ in range(iterations):
        analyze_material({"title": "Layered Recall", "content": text}, source_type="note")
    elapsed = time.perf_counter() - start
    return {
        "iterations": iterations,
        "total_seconds": round(elapsed, 4),
        "avg_ms_per_analysis": round(elapsed / iterations * 1000, 2),
    }


def bench_memory_footprint() -> dict:
    import psutil
    process = psutil.Process()
    mem = process.memory_info()
    return {
        "rss_mb": round(mem.rss / 1024 / 1024, 2),
        "vms_mb": round(mem.vms / 1024 / 1024, 2),
    }


def run_all_benchmarks() -> dict:
    results = {}
    try:
        results["recall_warm"] = bench_recall_warm()
    except Exception as exc:
        results["recall_warm"] = {"error": str(exc)}
    try:
        results["ingestion"] = bench_ingestion_throughput(count=20)
    except Exception as exc:
        results["ingestion"] = {"error": str(exc)}
    try:
        results["query_preprocessing"] = bench_query_preprocessing(iterations=50)
    except Exception as exc:
        results["query_preprocessing"] = {"error": str(exc)}
    try:
        results["knowledge_analysis"] = bench_knowledge_analysis(iterations=10)
    except Exception as exc:
        results["knowledge_analysis"] = {"error": str(exc)}
    try:
        results["memory"] = bench_memory_footprint()
    except Exception:
        results["memory"] = {"note": "psutil not installed"}
    return results


if __name__ == "__main__":
    import json
    print(json.dumps(run_all_benchmarks(), ensure_ascii=False, indent=2))
