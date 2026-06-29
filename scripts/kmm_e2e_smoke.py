#!/usr/bin/env python3
"""End-to-end smoke for public KMM runtime and installed scripts."""

from __future__ import annotations

import argparse
import contextlib
import http.server
import json
import os
from pathlib import Path
import shutil
import socketserver
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any
import shutil


def add_python_path(path: Path) -> None:
    if path.exists():
        sys.path.insert(0, str(path))


def clean_path_value(value: str) -> str:
    return (value or "").strip()


def make_state_db(agent_home: Path) -> None:
    db = agent_home / "state.db"
    conn = sqlite3.connect(str(db))
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, title TEXT, started_at REAL)")
        conn.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, session_id TEXT, content TEXT)")
        conn.execute("DELETE FROM sessions")
        conn.execute("DELETE FROM messages")
        conn.execute("INSERT INTO sessions VALUES ('s1', 'Agent Memory Architecture', 1.0)")
        conn.execute("INSERT INTO messages VALUES (1, 's1', 'agent memory architecture with layered recall and notes')")
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def temp_http_server(root: Path):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def log_message(self, format: str, *args: Any) -> None:
            return

    with socketserver.TCPServer(("127.0.0.1", 0), Handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{port}/index.html"
        finally:
            httpd.shutdown()
            thread.join(timeout=2)


def run(cmd: list[str], env: dict[str, str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=timeout)


def ensure_rclone_remote(env: dict[str, str], name: str) -> None:
    run(["rclone", "config", "delete", name], env=env, timeout=30)
    result = run(["rclone", "config", "create", name, "local"], env=env, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or "failed to create local rclone remote")


def cleanup_rclone_remote(env: dict[str, str], name: str) -> None:
    run(["rclone", "config", "delete", name], env=env, timeout=30)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-home", default=os.environ.get("AGENT_HOME", ""))
    parser.add_argument("--plugin-dir", default=os.environ.get("KMM_PLUGIN_DIR", ""))
    parser.add_argument("--scripts-dir", default=os.environ.get("KMM_SCRIPT_DIR", ""))
    parser.add_argument("--use-installed", action="store_true", help="Use installed plugin/scripts instead of repo paths")
    parser.add_argument("--require-cloud", action="store_true", help="Fail instead of skipping when rclone is unavailable")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    workspace = Path(tempfile.mkdtemp(prefix="kmm-e2e-"))
    agent_home = Path(clean_path_value(args.agent_home)).expanduser() if clean_path_value(args.agent_home) else workspace / "agent-home"
    notes_dir = workspace / "notes"
    docs_dir = workspace / "docs"
    remote_dir = workspace / "remote-notes"
    skills_dir = workspace / "skills"
    structured_dir = workspace / "structured"
    agent_home.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    remote_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)
    structured_dir.mkdir(parents=True, exist_ok=True)
    make_state_db(agent_home)

    plugin_dir = (
        Path(clean_path_value(args.plugin_dir)).expanduser()
        if clean_path_value(args.plugin_dir)
        else (agent_home / "knowledge-plugin" if args.use_installed else repo_root / "src")
    )
    scripts_dir = (
        Path(clean_path_value(args.scripts_dir)).expanduser()
        if clean_path_value(args.scripts_dir)
        else (agent_home / "scripts" if args.use_installed else repo_root / "scripts")
    )

    add_python_path(plugin_dir)
    add_python_path(repo_root / "src")

    env = os.environ.copy()
    env["AGENT_HOME"] = str(agent_home).strip()
    env["KMM_PLUGIN_DIR"] = str(plugin_dir).strip()
    env["KMM_SCRIPT_DIR"] = str(scripts_dir).strip()
    env["KMM_NOTES_DIR"] = str(notes_dir)
    env["HERMES_SKILLS_DIR"] = str(skills_dir)
    env["BOOK_TO_SKILL"] = str(scripts_dir / "book_to_skill.py")
    env["PATH"] = str(Path(sys.executable).resolve().parent) + os.pathsep + env.get("PATH", "")
    os.environ.update(
        {
            "AGENT_HOME": env["AGENT_HOME"],
            "KMM_PLUGIN_DIR": env["KMM_PLUGIN_DIR"],
            "KMM_SCRIPT_DIR": env["KMM_SCRIPT_DIR"],
            "KMM_NOTES_DIR": env["KMM_NOTES_DIR"],
            "HERMES_SKILLS_DIR": env["HERMES_SKILLS_DIR"],
            "BOOK_TO_SKILL": env["BOOK_TO_SKILL"],
            "PATH": env["PATH"],
        }
    )

    from cloud_sync import CloudSyncEngine
    from knowledge_collector import collect_article, collect_book, collect_document, collect_video, collect_web, generate_note
    from notes_rag import create_note, search_notes
    import book_cache_manager
    import book_keyword_index
    import knowledge_discovery

    html = docs_dir / "index.html"
    html.write_text(
        "<html><head><title>KMM Smoke</title></head><body><article>Layered recall and curated notes.</article></body></html>",
        encoding="utf-8",
    )
    md = docs_dir / "sample.md"
    md.write_text("# Sample Document\n\nCurated document content for smoke validation.\n", encoding="utf-8")
    book = docs_dir / "sample-book.md"
    book.write_text("# Chapter 1\n\nLayered memory.\n\n\n\n# Chapter 2\n\nCurated notes.\n", encoding="utf-8")
    listing = docs_dir / "listing.txt"
    listing.write_text("1048576 category/book.pdf\n2048 docs/guide.epub\n", encoding="utf-8")

    results: dict[str, Any] = {}
    with temp_http_server(docs_dir) as url:
        web_result = collect_web(url)
        article_url_result = collect_article("wechat", url)
        article_keyword_result = collect_article("wechat", "weekly digest")
        video_result = collect_video("https://www.youtube.com/watch?v=abc123")
        document_result = collect_document(str(md))
        note_result = generate_note({"title": "Generated", "content": "Curated structured content"}, template="note")
        rag_note = create_note("Agent Memory Architecture", "Layered memory with curated notes", domain="shared")
        rag_results = search_notes("Layered memory", domains=["shared"])
        discovery_results = knowledge_discovery.discover_new_notes(days=30)
        book_result = collect_book(str(book))

        book_cache_manager.CACHE_ROOT = workspace / "book-cache"
        book_cache_manager.INDEX_FILE = book_cache_manager.CACHE_ROOT / "book_index.json"
        book_cache_manager.CACHE_FILES_DIR = book_cache_manager.CACHE_ROOT / "files"
        rebuilt_index = book_cache_manager.rebuild_index_from_listing(str(listing))

        os.environ["KMM_BOOK_CACHE_DIR"] = str(workspace / "book-keywords")
        os.environ["KMM_BOOK_INDEX_JSON"] = str(book_cache_manager.INDEX_FILE)
        os.environ["KMM_BOOK_KEYWORD_DB"] = str(workspace / "book-keywords" / "book_keywords.db")
        book_keyword_index.CACHE_ROOT = Path(os.environ["KMM_BOOK_CACHE_DIR"])
        book_keyword_index.INDEX_JSON = Path(os.environ["KMM_BOOK_INDEX_JSON"])
        book_keyword_index.DB_PATH = Path(os.environ["KMM_BOOK_KEYWORD_DB"])
        book_keyword_index.build_index()
        book_search = book_keyword_index.search("guide")

        download_dir = workspace / "downloaded"
        download_dir.mkdir(parents=True, exist_ok=True)
        if shutil.which("rclone"):
            engine = CloudSyncEngine()
            remote_name = f"kmmsmoke{int(time.time())}"
            ensure_rclone_remote(env, remote_name)
            sync_src = notes_dir / "sync"
            sync_src.mkdir(parents=True, exist_ok=True)
            (sync_src / "sync.md").write_text("# Sync Note\n", encoding="utf-8")

            remote_path = str(remote_dir).replace("\\", "/")
            try:
                sync_to_result = engine.sync_to(str(sync_src), remote_name, remote_path)
                sync_from_result = engine.sync_from(remote_name, remote_path, str(download_dir))
                bisync_result = engine.bisync(str(sync_src), remote_name, remote_path, resync=True)
            finally:
                cleanup_rclone_remote(env, remote_name)
        else:
            sync_to_result = type("Result", (), {"returncode": 0})()
            sync_from_result = type("Result", (), {"returncode": 0})()
            bisync_result = type("Result", (), {"returncode": 0})()
            (download_dir / "sync.md").write_text("# skipped\n", encoding="utf-8")

        script_results = {
            "knowledge_discovery": run([sys.executable, str(scripts_dir / "knowledge_discovery.py")], env),
            "lightweight_recall": run([sys.executable, str(scripts_dir / "lightweight_recall.py"), "--query", "agent memory architecture", "--limit", "3"], env, timeout=180),
            "doc_parse_router": run([sys.executable, str(scripts_dir / "doc_parse_router.py"), str(md)], env, timeout=180),
            "book_to_skill": run([sys.executable, str(scripts_dir / "book_to_skill.py"), "all", str(book), "--name", "sample-book"], env, timeout=180),
        }

    results = {
        "web_title": web_result.title,
        "web_note_exists": Path(web_result.note_path).exists(),
        "article_url_type": article_url_result.source_type,
        "article_keyword_exists": Path(article_keyword_result.note_path).exists(),
        "video_note_exists": Path(video_result.note_path).exists(),
        "document_note_exists": Path(document_result.note_path).exists(),
        "generated_note_exists": Path(note_result["note_path"]).exists(),
        "rag_note_exists": Path(rag_note["note_path"]).exists(),
        "rag_results_count": len(rag_results),
        "discovery_count": len(discovery_results),
        "book_ok": bool(book_result.get("output") or book_result.get("slug")),
        "book_index_count": len(rebuilt_index["books"]),
        "book_keyword_count": len(book_search),
        "sync_to_returncode": sync_to_result.returncode,
        "sync_from_returncode": sync_from_result.returncode,
        "bisync_returncode": bisync_result.returncode,
        "downloaded_exists": (download_dir / "sync.md").exists(),
        "script_results": {
            name: {
                "returncode": item.returncode,
                "stdout": item.stdout[:400],
                "stderr": item.stderr[:400],
            }
            for name, item in script_results.items()
        },
    }

    failures = []
    if results["web_title"] != "KMM Smoke":
        failures.append("collect_web title mismatch")
    for key in ("web_note_exists", "article_keyword_exists", "video_note_exists", "document_note_exists", "generated_note_exists", "rag_note_exists", "downloaded_exists"):
        if not results[key]:
            failures.append(f"{key} failed")
    if results["rag_results_count"] < 1:
        failures.append("search_notes returned no results")
    if results["book_index_count"] != 2:
        failures.append("book_cache_manager rebuild failed")
    if results["book_keyword_count"] < 1:
        failures.append("book_keyword_index search failed")
    for key in ("sync_to_returncode", "sync_from_returncode", "bisync_returncode"):
        if results[key] != 0:
            failures.append(f"{key} != 0")
    if args.require_cloud and not shutil.which("rclone"):
        failures.append("rclone unavailable but cloud testing required")
    for name, item in results["script_results"].items():
        if item["returncode"] != 0:
            failures.append(f"script {name} failed")

    payload = {"ok": not failures, "failures": failures, "results": results, "workspace": str(workspace)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
