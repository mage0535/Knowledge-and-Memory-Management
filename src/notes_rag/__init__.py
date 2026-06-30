"""
Notes & RAG Manager — 笔记和 RAG 知识库管理

管理个人/部门/公司三级知识域，与 gbrain + Hindsight 集成。
"""

from __future__ import annotations

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import os
import re
import sqlite3
from urllib.error import URLError
from urllib.request import Request, urlopen
import json
import subprocess

from cloud_sync import CloudSyncEngine
from runtime_support import resolve_agent_home, resolve_notes_root
from knowledge_collector.note_generator import generate_note
from knowledge_collector.query_rewrite import preprocess_query

class NotesRAGManager:
    """笔记与 RAG 管理器"""
    
    KNOWLEDGE_DOMAINS = {
        "personal": {"path": "notes/personal", "access": "private"},
        "shared": {"path": "notes/shared", "access": "team"},
        "archive": {"path": "notes/archive", "access": "readonly"},
    }
    
    def create_note(self, title, content, domain="personal", tags=None):
        """创建笔记并自动索引"""
        return generate_note(
            {
                "title": title,
                "content": content,
                "domain": domain,
                "tags": tags or [],
            },
            template="note",
            note_title=title,
        )
    
    def search(self, query, domains=None):
        """跨域检索笔记，融合本地笔记、state.db 和可选外部记忆层。"""
        qinfo = preprocess_query(query)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(self._search_local_markdown, query, domains),
                executor.submit(self._search_state_db, query),
                executor.submit(self._search_hindsight, query),
                executor.submit(self._search_gbrain, query),
            ]
            sources = [future.result() for future in futures]
        fused = []
        seen = set()
        for batch in sources:
            for row in batch:
                key = (row.get("source"), row.get("url", row.get("title", "")), row.get("content", ""))
                if key in seen:
                    continue
                seen.add(key)
                fused.append(row)
        fused.sort(key=lambda item: item.get("score", 0.0), reverse=True)

        try:
            from knowledge_collector.hybrid_search import hybrid_search
            fused = hybrid_search(fused, query, limit=max(len(fused), 10))
        except ImportError:
            pass

        try:
            from knowledge_collector.reranker import rerank
            fused[:20] = rerank(query, fused[:20])
        except ImportError:
            pass

        return fused

    def _search_local_markdown(self, query, domains=None):
        """跨域检索 Markdown 笔记。"""
        domains = list(domains or self.KNOWLEDGE_DOMAINS.keys())
        roots = []
        notes_root = resolve_notes_root()
        for domain in domains:
            roots.append(notes_root / domain)
        results = []
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        for root in roots:
            if not root.exists():
                continue
            for path in sorted(root.rglob("*.md")):
                text = path.read_text(encoding="utf-8", errors="replace")
                match = pattern.search(text)
                if not match:
                    continue
                start = max(0, match.start() - 80)
                end = min(len(text), match.end() + 120)
                results.append(
                    {
                        "title": path.stem,
                        "content": text[start:end].strip(),
                        "score": 1.0,
                        "url": str(path),
                        "source": "local_note",
                    }
                )
        return results

    def _search_state_db(self, query: str) -> list[dict]:
        state_db = resolve_agent_home() / "state.db"
        if not state_db.exists():
            return []
        try:
            conn = sqlite3.connect(str(state_db))
            conn.row_factory = sqlite3.Row
            has_fts = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='messages_fts' LIMIT 1"
            ).fetchone()
            if has_fts:
                terms = " ".join(part for part in re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}", query)[:6] if part)
                rows = conn.execute(
                    """
                    SELECT s.id AS session_id, COALESCE(s.title, s.id) AS title, m.content
                    FROM messages_fts f
                    JOIN messages m ON f.rowid = m.id
                    JOIN sessions s ON s.id = m.session_id
                    WHERE messages_fts MATCH ?
                    ORDER BY rank
                    LIMIT 5
                    """,
                    (terms or query,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT s.id AS session_id, COALESCE(s.title, s.id) AS title, m.content
                    FROM messages m
                    JOIN sessions s ON s.id = m.session_id
                    WHERE lower(m.content) LIKE lower(?)
                    ORDER BY s.started_at DESC
                    LIMIT 5
                    """,
                    (f"%{query}%",),
                ).fetchall()
        except sqlite3.Error:
            return []
        finally:
            conn.close()
        return [
            {
                "title": row["title"],
                "content": (row["content"] or "")[:240],
                "score": 0.7,
                "url": f"state:{row['session_id']}",
                "source": "state_db",
            }
            for row in rows
        ]

    def _search_hindsight(self, query: str) -> list[dict]:
        url = os.environ.get(
            "KMM_HINDSIGHT_RECALL_URL",
            "http://127.0.0.1:8890/v1/default/banks/hermes/memories/recall",
        )
        timeout_seconds = float(os.environ.get("KMM_HINDSIGHT_TIMEOUT", "3"))
        payload = json.dumps({"query": query, "limit": 5}).encode("utf-8")
        request = Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8", errors="replace"))
        except (URLError, TimeoutError, ValueError):
            return []
        results = data.get("results") or data.get("memories") or []
        return [
            {
                "title": item.get("id", "hindsight"),
                "content": (item.get("content") or item.get("text") or "")[:240],
                "score": float(item.get("score", 0.45) or 0.45),
                "url": f"hindsight:{item.get('id', '')}",
                "source": "hindsight",
            }
            for item in results[:5]
        ]

    def _search_gbrain(self, query: str) -> list[dict]:
        try:
            proc = subprocess.run(
                ["gbrain", "search", query, "--limit", "5"],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
        if proc.returncode != 0:
            return []
        results = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            results.append(
                {
                    "title": line[:80],
                    "content": line[:240],
                    "score": 0.35,
                    "url": f"gbrain:{line[:80]}",
                    "source": "gbrain",
                }
            )
        return results[:5]

    def search_notes(self, query, domains=None):
        return self.search(query, domains=domains)

    def sync_notes_to_cloud(self, remote: str | None = None):
        remote = remote or os.environ.get("KMM_SYNC_REMOTE", "")
        if not remote:
            return {"status": "skipped", "reason": "KMM_SYNC_REMOTE not configured"}
        engine = CloudSyncEngine()
        remote_name, _, remote_path = remote.partition(":")
        result = engine.sync_to(str(resolve_notes_root()), remote_name, remote_path or "notes")
        return {"status": "ok" if result.returncode == 0 else "error", "returncode": result.returncode}


def create_note(title, content, domain="personal", tags=None):
    return NotesRAGManager().create_note(title, content, domain=domain, tags=tags)


def search_notes(query, domains=None):
    return NotesRAGManager().search(query, domains=domains)


def sync_notes_to_cloud(remote: str | None = None):
    return NotesRAGManager().sync_notes_to_cloud(remote=remote)


__all__ = [
    "NotesRAGManager",
    "create_note",
    "search_notes",
    "sync_notes_to_cloud",
]
