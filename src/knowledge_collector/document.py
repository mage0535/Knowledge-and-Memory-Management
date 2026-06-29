"""
Document collection for public KMM builds.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from runtime_support import CollectionResult

from .note_generator import generate_note
from .refinement import refine_pdf


logger = logging.getLogger("kmm.document")

SUPPORTED_FORMATS = {
    ".pdf": "Adobe PDF",
    ".docx": "Word document",
    ".pptx": "PowerPoint presentation",
    ".xlsx": "Excel workbook",
    ".xls": "Excel 97 workbook",
    ".html": "HTML page",
    ".htm": "HTML page",
    ".csv": "CSV table",
    ".json": "JSON data",
    ".xml": "XML data",
    ".txt": "Plain text",
    ".md": "Markdown",
    ".epub": "EPUB ebook",
    ".zip": "ZIP archive",
    ".jpg": "JPEG image",
    ".jpeg": "JPEG image",
    ".png": "PNG image",
    ".gif": "GIF image",
    ".bmp": "BMP image",
    ".webp": "WebP image",
    ".msg": "Outlook mail",
    ".eml": "Email message",
}

SUPPORTED_EXTENSIONS = set(SUPPORTED_FORMATS.keys())


class DocumentConversionError(RuntimeError):
    """Raised when document conversion fails."""


class DocumentResult:
    """Structured result for converted documents."""

    def __init__(
        self,
        *,
        text_content: str,
        source_path: str,
        source_format: str,
        title: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.text_content = text_content
        self.source_path = source_path
        self.source_format = source_format
        self.title = title or Path(source_path).stem
        self.metadata = metadata or {}

    @property
    def char_count(self) -> int:
        return len(self.text_content)

    @property
    def line_count(self) -> int:
        return self.text_content.count("\n") + 1


class DocumentConverter:
    """Convert public document formats into markdown-like text."""

    def __init__(self) -> None:
        self._engine = None
        self._stats = {"total": 0, "ok": 0, "fail": 0}

    @staticmethod
    def is_supported(path: str) -> bool:
        return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS

    @staticmethod
    def get_format(path: str) -> str:
        return SUPPORTED_FORMATS.get(Path(path).suffix.lower(), "Unknown")

    def _load_engine(self):
        if self._engine is None:
            try:
                from markitdown import MarkItDown
            except ImportError as exc:
                raise DocumentConversionError(
                    "markitdown is not installed. Run: pip install 'markitdown[all]'"
                ) from exc
            self._engine = MarkItDown()
        return self._engine

    def convert(self, path: str) -> DocumentResult:
        self._stats["total"] += 1
        source_path = os.path.abspath(os.path.expanduser(path))
        if not os.path.isfile(source_path):
            self._stats["fail"] += 1
            raise FileNotFoundError(source_path)
        if not self.is_supported(source_path):
            self._stats["fail"] += 1
            raise DocumentConversionError(f"unsupported format: {source_path}")

        try:
            result = self._load_engine().convert(source_path)
        except Exception as exc:
            self._stats["fail"] += 1
            raise DocumentConversionError(str(exc)) from exc

        self._stats["ok"] += 1
        return DocumentResult(
            text_content=result.text_content,
            source_path=source_path,
            source_format=self.get_format(source_path),
            metadata={"engine": "markitdown"},
        )

    def batch_convert(self, paths: list[str], show_progress: bool = False) -> list[DocumentResult | None]:
        results: list[DocumentResult | None] = []
        total = len(paths)
        for index, path in enumerate(paths, start=1):
            if show_progress:
                print(f"[{index}/{total}] {Path(path).name}", end=" ", flush=True)
            try:
                converted = self.convert(path)
            except Exception as exc:
                if show_progress:
                    print(f"FAIL {exc}")
                results.append(None)
                continue
            if show_progress:
                print(f"OK {converted.char_count} chars")
            results.append(converted)
        return results

    def stats(self) -> dict[str, int]:
        return dict(self._stats)


class DocumentCollector:
    """Higher-level document discovery and conversion."""

    def __init__(self, converter: DocumentConverter | None = None) -> None:
        self.converter = converter or DocumentConverter()

    @staticmethod
    def discover_files(paths: list[str], recursive: bool = True, max_size_mb: float = 200.0) -> list[str]:
        discovered: list[str] = []
        for entry in paths:
            candidate = os.path.abspath(os.path.expanduser(entry))
            if os.path.isfile(candidate):
                if DocumentConverter.is_supported(candidate) and os.path.getsize(candidate) <= max_size_mb * 1024 * 1024:
                    discovered.append(candidate)
                continue
            if not os.path.isdir(candidate):
                continue
            for root, dirs, files in os.walk(candidate):
                if not recursive:
                    dirs.clear()
                for file_name in files:
                    path = os.path.join(root, file_name)
                    if not DocumentConverter.is_supported(path):
                        continue
                    if os.path.getsize(path) > max_size_mb * 1024 * 1024:
                        logger.warning("skip oversize file: %s", path)
                        continue
                    discovered.append(path)
        return sorted(discovered)

    def collect(self, path: str, output_dir: str | None = None) -> DocumentResult:
        result = self.converter.convert(path)
        if output_dir:
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{Path(path).stem}.md"
            out_path.write_text(result.text_content, encoding="utf-8")
        return result

    def batch_collect(self, paths: list[str], output_dir: str | None = None, show_progress: bool = False) -> list[DocumentResult | None]:
        results = self.converter.batch_convert(paths, show_progress=show_progress)
        if output_dir:
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            for item in results:
                if item is None:
                    continue
                out_path = out_dir / f"{Path(item.source_path).stem}.md"
                out_path.write_text(item.text_content, encoding="utf-8")
        return results


def collect_document(path: str) -> CollectionResult:
    result = DocumentCollector().collect(path)
    note = generate_note(
        {
            "title": result.title,
            "content": result.text_content,
            "source_type": "document",
            "source_ref": result.source_path,
            "metadata": {
                "source_format": result.source_format,
                **result.metadata,
            },
        },
        template="document",
    )
    return CollectionResult(
        source_type="document",
        title=result.title,
        content_preview=result.text_content[:500],
        note_path=note["note_path"],
        gbrain_slug=note["note_id"],
        metadata={
            "path": result.source_path,
            "source_format": result.source_format,
            **result.metadata,
        },
    )


def collect_book(path: str) -> dict:
    return refine_pdf(path)


def cli() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Convert documents into Markdown-friendly text for KMM.")
    parser.add_argument("files", nargs="*", help="Files or directories to process")
    parser.add_argument("--batch", nargs="+", metavar="PATH", help="Batch process files or directories")
    parser.add_argument("-o", "--out", help="Optional output directory")
    parser.add_argument("--format", action="store_true", help="List supported formats")
    parser.add_argument("--progress", action="store_true", help="Show progress while converting")
    args = parser.parse_args()

    if args.format:
        for ext, description in sorted(SUPPORTED_FORMATS.items()):
            print(f"{ext:8s} {description}")
        return 0

    targets = DocumentCollector.discover_files(args.batch or args.files)
    if not targets:
        parser.print_help()
        return 1

    results = DocumentCollector().batch_collect(targets, output_dir=args.out, show_progress=args.progress)
    return 0 if all(item is not None for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(cli())
