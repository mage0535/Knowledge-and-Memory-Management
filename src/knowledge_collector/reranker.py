"""Optional reranker integration for retrieval result refinement.

Supports: Jina AI reranker API
Env: KMM_RERANKER_API_KEY, KMM_RERANKER_MODEL
"""

from __future__ import annotations

import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

RERANKER_API_KEY = os.environ.get("KMM_RERANKER_API_KEY", "")
RERANKER_MODEL = os.environ.get("KMM_RERANKER_MODEL", "jina-reranker-v2-base-multilingual")
RERANKER_URL = "https://api.jina.ai/v1/rerank"


def rerank(query: str, documents: list[dict], top_n: int | None = None) -> list[dict]:
    if not RERANKER_API_KEY:
        return _localfallback_rerank(query, documents)

    payload = json.dumps({
        "model": RERANKER_MODEL,
        "query": query,
        "documents": [doc.get("content", doc.get("title", ""))[:512] for doc in documents],
        "top_n": top_n or len(documents),
    }).encode("utf-8")

    request = Request(
        RERANKER_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {RERANKER_API_KEY}",
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError):
        return _localfallback_rerank(query, documents)

    results = data.get("results", [])
    reranked = []
    for item in results:
        idx = item.get("index", 0)
        if idx < len(documents):
            doc = dict(documents[idx])
            doc["rerank_score"] = round(item.get("relevance_score", 0), 4)
            doc["retrieval_score"] = doc.pop("score", 0)
            reranked.append(doc)
    return reranked


def _localfallback_rerank(query: str, documents: list[dict]) -> list[dict]:
    query_lower = query.lower()
    for doc in documents:
        content = (doc.get("content") or doc.get("title", "")).lower()
        keyword_hits = sum(1 for word in query_lower.split() if word in content)
        doc["rerank_score"] = doc.get("score", 0.5) * (1 + 0.2 * keyword_hits)
        doc["retrieval_score"] = doc.pop("score", 0.5)
    documents.sort(key=lambda d: d.get("rerank_score", 0), reverse=True)
    return documents
