#!/usr/bin/env python3
"""Fast-first document parsing router for Linux deployments."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


LITEPARSE_BIN = os.environ.get("LITEPARSE_BIN", "liteparse")
MARKITDOWN_BIN = os.environ.get("MARKITDOWN_BIN", "markitdown")
PDFTOTEXT_BIN = os.environ.get("PDFTOTEXT_BIN", "pdftotext")


def run(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def parse_with_liteparse(src: str) -> dict:
    code, out, err = run([LITEPARSE_BIN, "parse", src])
    if code == 0 and out.strip():
        return {"engine": "liteparse", "ok": True, "text": out}
    return {"engine": "liteparse", "ok": False, "error": err.strip() or "no output"}


def parse_with_markitdown(src: str) -> dict:
    code, out, err = run([MARKITDOWN_BIN, src])
    if code == 0 and out.strip():
        return {"engine": "markitdown", "ok": True, "text": out}
    return {"engine": "markitdown", "ok": False, "error": err.strip() or "no output"}


def parse_with_pdftotext(src: str) -> dict:
    code, out, err = run([PDFTOTEXT_BIN, src, "-"])
    if code == 0 and out.strip():
        return {"engine": "pdftotext", "ok": True, "text": out}
    return {"engine": "pdftotext", "ok": False, "error": err.strip() or "no output"}


def parse_document(src: str) -> dict:
    ext = Path(src).suffix.lower()
    if ext == ".pdf":
        candidates = [parse_with_liteparse, parse_with_markitdown, parse_with_pdftotext]
    else:
        candidates = [parse_with_markitdown, parse_with_liteparse]

    attempts = []
    for parser in candidates:
        attempt = parser(src)
        attempts.append({k: v for k, v in attempt.items() if k != "text"})
        if attempt.get("ok"):
            return {
                "ok": True,
                "engine": attempt["engine"],
                "text": attempt["text"],
                "attempts": attempts,
            }
    return {"ok": False, "attempts": attempts}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    source = str(Path(args.source).expanduser())
    if not os.path.exists(source):
        raise SystemExit(f"file not found: {source}")
    result = parse_document(source)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["ok"]:
        print(result["text"])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
