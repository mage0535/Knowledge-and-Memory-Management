"""Optional hybrid retrieval with vector search (Qdrant) integration.

Requires: pip install qdrant-client
Env: KMM_QDRANT_URL=http://localhost:6333 KMM_QDRANT_COLLECTION=kmm_notes
"""

from __future__ import annotations

import os
from typing import Any


QDRANT_URL = os.environ.get("KMM_QDRANT_URL", "")
QDRANT_COLLECTION = os.environ.get("KMM_QDRANT_COLLECTION", "kmm_notes")


def _ensure_qdrant():
    try:
        from qdrant_client import QdrantClient
        return QdrantClient(url=QDRANT_URL) if QDRANT_URL else QdrantClient(path=":memory:")
    except ImportError:
        return None


def vector_search(query: str, limit: int = 10, score_threshold: float = 0.5) -> list[dict]:
    client = _ensure_qdrant()
    if client is None:
        return []

    try:
        from qdrant_client.models import SearchRequest
        embedding = _embed_query(query)
        if not embedding:
            return []
        results = client.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=embedding,
            limit=limit,
            score_threshold=score_threshold,
        )
    except Exception:
        return []

    return [
        {
            "source": "qdrant",
            "title": hit.payload.get("title", str(hit.id)),
            "content": (hit.payload.get("content") or hit.payload.get("text", ""))[:240],
            "score": round(hit.score, 4) if hit.score else 0.0,
            "url": hit.payload.get("url", str(hit.id)),
            "id": str(hit.id),
        }
        for hit in results
    ]


def _embed_query(query: str) -> list[float] | None:
    embed_fn = os.environ.get("KMM_EMBED_FN", "")
    if embed_fn == "openai":
        import openai
        client = openai.OpenAI()
        resp = client.embeddings.create(input=[query], model="text-embedding-3-small")
        return resp.data[0].embedding
    elif embed_fn == "sentence_transformers":
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(os.environ.get("KMM_EMBED_MODEL", "all-MiniLM-L6-v2"))
        return model.encode([query]).tolist()[0]
    return None


def rrf_fusion(results_a: list[dict], results_b: list[dict], k: int = 60) -> list[dict]:
    """Reciprocal Rank Fusion between two result lists."""
    scores: dict[str, tuple[dict, float]] = {}
    for rank, item in enumerate(results_a):
        key = item.get("id") or item.get("url") or item.get("title", "")
        if not key:
            continue
        scores[key] = (item, scores.get(key, (item, 0))[1] + 1.0 / (k + rank + 1))
    for rank, item in enumerate(results_b):
        key = item.get("id") or item.get("url") or item.get("title", "")
        if not key:
            continue
        scores[key] = (item, scores.get(key, (item, 0))[1] + 1.0 / (k + rank + 1))
    fused = sorted(scores.values(), key=lambda x: x[1], reverse=True)
    return [item for item, _score in fused]


def hybrid_search(lexical_results: list[dict], query: str, limit: int = 10) -> list[dict]:
    vector_results = vector_search(query, limit=limit)
    if not vector_results:
        return lexical_results
    fused = rrf_fusion(lexical_results, vector_results)
    return fused[:limit]
