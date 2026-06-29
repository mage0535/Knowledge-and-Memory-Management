#!/usr/bin/env python3
"""Linux-first public cache/index manager for large remote book libraries."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


CACHE_ROOT = Path(os.environ.get("KMM_BOOK_CACHE_DIR", Path.home() / "knowledge" / "book_cache"))
INDEX_FILE = Path(os.environ.get("KMM_BOOK_INDEX_FILE", CACHE_ROOT / "book_index.json"))
CACHE_FILES_DIR = CACHE_ROOT / "files"
REMOTE_ROOT = os.environ.get("KMM_BOOK_REMOTE", "")


def ensure_dirs() -> None:
    CACHE_FILES_DIR.mkdir(parents=True, exist_ok=True)


def load_index() -> dict:
    if not INDEX_FILE.exists():
        return {"books": []}
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


def save_index(payload: dict) -> None:
    ensure_dirs()
    INDEX_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def rebuild_index_from_listing(listing_file: str) -> dict:
    books = []
    for line in Path(listing_file).read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        size_text, path_text = parts
        try:
            size_bytes = int(size_text)
        except ValueError:
            continue
        filename = Path(path_text).name
        books.append(
            {
                "filename": filename,
                "remote_path": path_text,
                "size_bytes": size_bytes,
                "size_mb": round(size_bytes / 1048576, 2),
                "format": Path(filename).suffix.lstrip(".").lower(),
                "category": Path(path_text).parent.name,
            }
        )
    payload = {"books": books, "generated_at": time.time()}
    save_index(payload)
    return payload


def search_books(keyword: str) -> list[dict]:
    keyword_lower = keyword.lower()
    return [
        book
        for book in load_index().get("books", [])
        if keyword_lower in book["filename"].lower() or keyword_lower in book["category"].lower()
    ]


def cache_book(filename: str) -> int:
    if not REMOTE_ROOT:
        print("KMM_BOOK_REMOTE not configured", file=sys.stderr)
        return 1
    matches = search_books(filename)
    if not matches:
        print(f"book not found: {filename}", file=sys.stderr)
        return 1
    ensure_dirs()
    book = matches[0]
    remote_target = f"{REMOTE_ROOT.rstrip(':')}:{book['remote_path']}"
    result = subprocess.run(["rclone", "copyto", remote_target, str(CACHE_FILES_DIR / book["filename"])])
    return result.returncode


def list_cached() -> list[str]:
    ensure_dirs()
    return sorted(item.name for item in CACHE_FILES_DIR.iterdir() if item.is_file())


def main() -> int:
    ensure_dirs()
    if len(sys.argv) < 2:
        print("usage: book_cache_manager.py <search|rebuild-index|list-cached|cache> ...")
        return 1
    command = sys.argv[1]
    if command == "search" and len(sys.argv) >= 3:
        print(json.dumps(search_books(sys.argv[2]), ensure_ascii=False, indent=2))
        return 0
    if command == "rebuild-index" and len(sys.argv) >= 3:
        print(json.dumps(rebuild_index_from_listing(sys.argv[2]), ensure_ascii=False, indent=2))
        return 0
    if command == "list-cached":
        print(json.dumps(list_cached(), ensure_ascii=False, indent=2))
        return 0
    if command == "cache" and len(sys.argv) >= 3:
        return cache_book(sys.argv[2])
    print("invalid command", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
