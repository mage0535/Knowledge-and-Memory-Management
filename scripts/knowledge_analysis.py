#!/usr/bin/env python3
"""Analyze local text or files into KMM knowledge objects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from knowledge_collector.analysis import analyze_material, render_knowledge_note


def read_input(args: argparse.Namespace) -> tuple[str, str]:
    if args.text:
        return args.title or "Text input", args.text
    if args.file:
        path = Path(args.file)
        return args.title or path.stem, path.read_text(encoding="utf-8", errors="replace")
    return args.title or "stdin", sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze content with the KMM Knowledge Analysis Layer.")
    parser.add_argument("file", nargs="?", help="Optional text/markdown file to analyze")
    parser.add_argument("--text", help="Inline text to analyze")
    parser.add_argument("--title", help="Override title")
    parser.add_argument("--source-type", default="article", help="Source type label")
    parser.add_argument("--markdown", action="store_true", help="Render a readable Markdown note body instead of JSON")
    args = parser.parse_args()

    title, content = read_input(args)
    knowledge = analyze_material({"title": title, "content": content, "source_ref": args.file or ""}, source_type=args.source_type)
    if args.markdown:
        print(render_knowledge_note(knowledge), end="")
    else:
        print(json.dumps(knowledge, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
