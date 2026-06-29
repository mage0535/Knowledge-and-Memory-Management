#!/usr/bin/env python3
"""Public Linux-first book-to-skill pipeline."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import sys


HERMES_SKILLS_DIR = Path(os.environ.get("HERMES_SKILLS_DIR", os.path.expanduser("~/.hermes/skills")))
KMM_STRUCTURED_DIR = Path(os.environ.get("KMM_NOTES_DIR", os.path.expanduser("~/knowledge/structured")))
CACHE_DIR = Path(tempfile.gettempdir()) / "kmm_book_to_skill"


def emit_json(payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
    sys.stdout.buffer.write(b"\n")


def extract_pdfplumber(path: str) -> str:
    try:
        import pdfplumber
    except ImportError:
        return ""
    parts = []
    with pdfplumber.open(path) as pdf:
        for idx, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if text.strip():
                parts.append(f"--- Page {idx + 1} ---\n{text}")
    return "\n\n".join(parts)


def extract_pdftotext(path: str) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", path, "-"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def extract_text(path: str) -> dict:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        text = extract_pdfplumber(path)
        if text.strip():
            return {"text": text, "engine": "pdfplumber"}
        text = extract_pdftotext(path)
        if text.strip():
            return {"text": text, "engine": "pdftotext"}
    elif ext in {".md", ".txt", ".rst", ".html"}:
        return {"text": Path(path).read_text(encoding="utf-8", errors="replace"), "engine": "direct"}
    return {"text": "", "engine": ""}


def slugify(value: str) -> str:
    text = (value or "").strip().lower()
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "book"


def analyze_chapters(text: str, title: str) -> dict:
    sections = [chunk.strip() for chunk in re.split(r"\n{4,}", text) if chunk.strip()]
    chapters = []
    if not sections:
        sections = [text.strip()]
    for idx, section in enumerate(sections[:20]):
        heading = section.splitlines()[0][:60] or f"Section {idx + 1}"
        chapters.append({"title": heading, "text": section[:5000]})
    return {
        "title": title,
        "total_chapters": len(chapters),
        "chapters": chapters,
        "word_count": len(text.split()),
    }


def generate_hermes_skill(analysis: dict, slug: str) -> dict:
    skill_dir = HERMES_SKILLS_DIR / f"book-{slug}"
    chapters_dir = skill_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    index_lines = [f"- `{item['title']}` -> `chapters/ch{idx + 1:02d}.md`" for idx, item in enumerate(analysis["chapters"])]
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                f"name: book-{slug}",
                f"description: Knowledge refinement for {analysis['title']}",
                f"generated: {datetime.now(timezone.utc).isoformat()}",
                "---",
                "",
                f"# {analysis['title']}",
                "",
                "## Chapter Index",
                *index_lines,
                "",
            ]
        ),
        encoding="utf-8",
    )
    for idx, chapter in enumerate(analysis["chapters"]):
        (chapters_dir / f"ch{idx + 1:02d}.md").write_text(
            f"# {chapter['title']}\n\n{chapter['text']}\n",
            encoding="utf-8",
        )
    return {"skill_dir": str(skill_dir), "chapters": len(analysis["chapters"])}


def generate_kmm_notes(analysis: dict, slug: str) -> dict:
    notes_dir = KMM_STRUCTURED_DIR / slug
    notes_dir.mkdir(parents=True, exist_ok=True)
    (notes_dir / "index.md").write_text(
        "\n".join(
            [
                f"# {analysis['title']}",
                "",
                "## Chapters",
                *[f"- {item['title']}" for item in analysis["chapters"]],
                "",
            ]
        ),
        encoding="utf-8",
    )
    for name in ("glossary.md", "patterns.md", "cheatsheet.md"):
        (notes_dir / name).write_text(f"# {name.replace('.md', '').title()}\n", encoding="utf-8")
    for idx, chapter in enumerate(analysis["chapters"]):
        (notes_dir / f"ch{idx + 1:02d}.md").write_text(
            f"# {chapter['title']}\n\n{chapter['text']}\n",
            encoding="utf-8",
        )
    return {"notes_dir": str(notes_dir)}


def run_pipeline(file_path: str, slug: str) -> dict:
    extracted = extract_text(file_path)
    if not extracted["text"].strip():
        return {"ok": False, "error": "text extraction failed"}
    analysis = analyze_chapters(extracted["text"], Path(file_path).stem)
    skill_info = generate_hermes_skill(analysis, slug)
    notes_info = generate_kmm_notes(analysis, slug)
    return {
        "ok": True,
        "engine": extracted["engine"],
        "analysis": {"title": analysis["title"], "total_chapters": analysis["total_chapters"], "word_count": analysis["word_count"]},
        "skill": skill_info,
        "notes": notes_info,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("extract", "analyze", "forge", "refine", "all"))
    parser.add_argument("file")
    parser.add_argument("--name", "-n", default="")
    args = parser.parse_args()

    slug = slugify(args.name or Path(args.file).stem)
    if args.command == "extract":
        emit_json(extract_text(args.file))
        return 0
    extracted = extract_text(args.file)
    if not extracted["text"].strip():
        emit_json({"ok": False, "error": "text extraction failed"})
        return 1
    analysis = analyze_chapters(extracted["text"], args.name or Path(args.file).stem)
    if args.command == "analyze":
        emit_json(analysis)
        return 0
    if args.command == "forge":
        emit_json(generate_hermes_skill(analysis, slug))
        return 0
    if args.command == "refine":
        emit_json(generate_kmm_notes(analysis, slug))
        return 0
    emit_json(run_pipeline(args.file, slug))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
