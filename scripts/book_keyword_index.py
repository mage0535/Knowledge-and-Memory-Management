#!/usr/bin/env python3
"""Build a lightweight searchable keyword index for cached books."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys


CACHE_ROOT = Path(os.environ.get("KMM_BOOK_CACHE_DIR", Path.home() / "knowledge" / "book_cache"))
INDEX_JSON = Path(os.environ.get("KMM_BOOK_INDEX_JSON", CACHE_ROOT / "book_index.json"))
DB_PATH = Path(os.environ.get("KMM_BOOK_KEYWORD_DB", CACHE_ROOT / "book_keywords.db"))
GBRAIN_SLUG = os.environ.get("KMM_BOOK_KEYWORD_SLUG", "note-book-knowledge-base")

STOP_WORDS = set(
    "的 了 在 是 我 有 和 就 不 人 都 一 一个 上 也 很 到 说 要 去 你 会 着 没有 看 好 自己 这 他 她 它 们 那 这个 那个 什么 怎么 如何 为什么 因为 所以 但是 然而 虽然".split()
)


def extract_keywords(text: str) -> list[str]:
    if not text:
        return []
    text = re.sub(r"\.(pdf|epub|mobi|azw3|djvu|chm|doc|docx)$", "", text, flags=re.IGNORECASE)
    parts = re.split(r"[ \-_（）()\[\]【】《》/\\,，.]+", text)
    keywords: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if re.search(r"[\u4e00-\u9fff]", part):
            chars = list(part)
            for start in range(len(chars)):
                for end in range(start + 2, min(start + 7, len(chars) + 1)):
                    phrase = "".join(chars[start:end])
                    if phrase not in STOP_WORDS:
                        keywords.append(phrase)
        for word in re.findall(r"[a-zA-Z][a-zA-Z0-9]{1,}", part):
            lowered = word.lower()
            if lowered not in {"the", "and", "for", "with", "from", "this", "that", "book", "guide", "manual", "introduction", "pdf", "epub"}:
                keywords.append(lowered)
    seen = set()
    unique = []
    for keyword in keywords:
        if keyword in seen:
            continue
        seen.add(keyword)
        unique.append(keyword)
    unique.sort(key=lambda item: (-len(item), item))
    return unique[:30]


def init_db() -> sqlite3.Connection:
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS book_fts USING fts5(filename, category, keywords, tokenize='unicode61')")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            rowid INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            category TEXT,
            ext TEXT,
            size_bytes INTEGER DEFAULT 0,
            size_mb REAL DEFAULT 0,
            remote_path TEXT,
            keywords TEXT,
            keyword_list TEXT,
            UNIQUE(filename, category)
        )
        """
    )
    conn.commit()
    return conn


def build_index() -> int:
    if not INDEX_JSON.exists():
        print(f"index file not found: {INDEX_JSON}", file=sys.stderr)
        return 1
    payload = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    conn = init_db()
    conn.execute("DELETE FROM books")
    conn.execute("DELETE FROM book_fts")
    for book in payload.get("books", []):
        filename = book.get("filename", "")
        category = book.get("category", "")
        keyword_list = list(set(extract_keywords(filename) + extract_keywords(category)))
        keyword_text = " ".join(keyword_list)
        conn.execute(
            """
            INSERT OR IGNORE INTO books (
                filename, category, ext, size_bytes, size_mb, remote_path, keywords, keyword_list
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                filename,
                category,
                book.get("format", ""),
                book.get("size_bytes", 0),
                book.get("size_mb", 0),
                book.get("remote_path", ""),
                keyword_text,
                ", ".join(keyword_list),
            ),
        )
        if conn.execute("SELECT changes()").fetchone()[0] > 0:
            rowid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.execute(
                "INSERT INTO book_fts (rowid, filename, category, keywords) VALUES (?, ?, ?, ?)",
                (rowid, filename, category, keyword_text),
            )
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    conn.close()
    print(f"indexed {total} books")
    return 0


def search(query: str, limit: int = 10) -> list[dict]:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT b.* FROM book_fts
        JOIN books b ON book_fts.rowid = b.rowid
        WHERE book_fts MATCH ?
        LIMIT ?
        """,
        (query, limit),
    ).fetchall()
    if not rows:
        like_query = f"%{query}%"
        rows = conn.execute(
            """
            SELECT * FROM books
            WHERE filename LIKE ? OR category LIKE ? OR keyword_list LIKE ?
            LIMIT ?
            """,
            (like_query, like_query, like_query, limit),
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def format_suggestions(results: list[dict]) -> str:
    if not results:
        return ""
    lines = ["📖 **知识库中查到相关书籍：**"]
    for index, result in enumerate(results[:5], start=1):
        lines.append(f"{index}. **{result['filename']}** [{result.get('category', '')}]")
    lines.append("")
    lines.append("需要缓存其中一本继续分析的话，直接告诉我书名。")
    return "\n".join(lines)


def sync_gbrain() -> int:
    if not DB_PATH.exists():
        print("keyword db not found; build index first", file=sys.stderr)
        return 1
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute("SELECT category, COUNT(*) FROM books GROUP BY category ORDER BY COUNT(*) DESC").fetchall()
    total = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    content = [
        "# 书籍知识库",
        f"总数: {total}",
        f"更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]
    for category, count in rows:
        content.append(f"- {category}: {count}")
    conn.close()
    result = subprocess.run(["gbrain", "put", GBRAIN_SLUG], input="\n".join(content), text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    return 0


def scan_updates() -> int:
    digest = hashlib.md5(str(INDEX_JSON).encode("utf-8")).hexdigest()[:12]
    print(json.dumps({"index_json": str(INDEX_JSON), "cache_root": str(CACHE_ROOT), "fingerprint": digest}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: book_keyword_index.py <build|search|suggest|sync-gbrain|scan-updates> [query]")
        return 1
    command = sys.argv[1]
    if command == "build":
        return build_index()
    if command == "search" and len(sys.argv) >= 3:
        print(json.dumps(search(sys.argv[2]), ensure_ascii=False, indent=2))
        return 0
    if command == "suggest" and len(sys.argv) >= 3:
        print(format_suggestions(search(sys.argv[2], limit=5)))
        return 0
    if command == "sync-gbrain":
        return sync_gbrain()
    if command == "scan-updates":
        return scan_updates()
    print("invalid command", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
