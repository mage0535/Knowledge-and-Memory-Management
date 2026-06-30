#!/usr/bin/env python3
"""Scan the repository for obvious private paths, credentials, and business defaults."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_TEXT_SUFFIXES = {".py", ".md", ".sh", ".yaml", ".yml", ".json", ".txt"}
DEFAULT_EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__", ".benchmarks", "venv", ".venv", "node_modules", "tests"}

SERVER_PATH_PATTERN = r"(/" + r"root/" + r"|/home/[A-Za-z0-9._-]+/)"
LEGACY_SLUG_PATTERN = "|".join(
    [
        "kiki" + "-chat-archive",
        "hub-" + "system-operations",
        "hub-" + "a-stock-trading",
        "hub-" + "social-media",
        "hub-" + "hermes-content",
    ]
)

PATTERNS = {
    "server_absolute_path": re.compile(SERVER_PATH_PATTERN),
    "tokenized_github_remote": re.compile(r"https://[^\s:@]+:[^\s@]+@github\.com", re.IGNORECASE),
    "private_ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "legacy_business_slug": re.compile(rf"({LEGACY_SLUG_PATTERN})"),
    "inline_secret_marker": re.compile(r"(password\s*=|passwd\s*=|secret\s*=|token\s*=)", re.IGNORECASE),
}

ALLOWED_IPS = {"127.0.0.1", "0.0.0.0", "4.10.0.84"}

EXCLUDE_SECRET_MARKER_FILES = {
    "docs/cloud-sync.md",
    "scripts/install_rclone_drives.sh",
}

EXCLUDE_SERVER_PATH_FILES = {
    "docs/CONTINUOUS_DEVELOPMENT.md",
}


def iter_text_files(repo_root: Path):
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in DEFAULT_EXCLUDED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in DEFAULT_TEXT_SUFFIXES:
            continue
        yield path


def scan_repo(repo_root: Path) -> dict:
    findings: list[dict] = []
    scanned_files = 0
    for path in iter_text_files(repo_root):
        scanned_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(repo_root).as_posix()
        for key, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                token = match.group(0)
                if key == "private_ipv4" and token in ALLOWED_IPS:
                    continue
                if key == "inline_secret_marker" and rel in EXCLUDE_SECRET_MARKER_FILES:
                    continue
                if key == "server_absolute_path" and rel in EXCLUDE_SERVER_PATH_FILES:
                    continue
                findings.append(
                    {
                        "type": key,
                        "file": rel,
                        "match": token,
                    }
                )
    return {
        "repo_root": str(repo_root),
        "scanned_files": scanned_files,
        "findings": findings,
        "ok": not findings,
    }


def scan_knowledge_json(repo_path: Path) -> list[dict]:
    """Scan *.knowledge.json files for leaked paths."""
    findings = []
    for kjson in sorted(repo_path.rglob("*.knowledge.json")):
        try:
            text = kjson.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            if re.search(r"(/root/|/home/\w+/|C:\\Users\\)", line):
                findings.append({
                    "file": str(kjson.relative_to(repo_path)),
                    "line": line_no,
                    "type": "knowledge_json_path_leak",
                    "snippet": line[:120],
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("repo_root", nargs="?", default=".")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    payload = scan_repo(repo)
    payload["findings"] = [
        f for f in payload.get("findings", [])
        if "sensitive_scan.py" not in f.get("file", "")
    ]
    kn_findings = scan_knowledge_json(repo)
    if kn_findings:
        payload["findings"].extend(kn_findings)
    payload["ok"] = not payload["findings"]
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["ok"]:
            print(f"scan ok ({payload['scanned_files']} files)")
        else:
            print(f"scan failed ({len(payload['findings'])} findings)")
            for item in payload["findings"]:
                print(f"- {item['type']}: {item['file']} -> {item['match']}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
