"""Multi-engine document parsing router with scoring and caching.

Engine registry pattern: each engine self-registers with capability descriptors.
File-hash caching avoids redundant parsing across repeated collection runs.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import subprocess
import time


ENGINE_REGISTRY: dict[str, dict] = {}
CACHE_DIR = Path(os.environ.get("KMM_PARSE_CACHE_DIR", str(Path.home() / ".cache" / "kmm-parsers")))


def register_engine(name: str, capabilities: dict, parser_fn) -> None:
    ENGINE_REGISTRY[name] = {"capabilities": capabilities, "parser": parser_fn}


def get_engine(name: str):
    entry = ENGINE_REGISTRY.get(name)
    return entry["parser"] if entry else None


def _cache_path(source_path: str, engine: str) -> Path:
    file_hash = _file_sha256(source_path)
    return CACHE_DIR / f"{engine}-{file_hash}.json"


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _cached_or_parse(source_path: str, engine: str, parser_fn) -> dict:
    cache_path = _cache_path(source_path, engine)
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    result = parser_fn(source_path)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return result


def score_engine_for_file(file_path: str, engine_name: str) -> float:
    ext = Path(file_path).suffix.lower()
    caps = ENGINE_REGISTRY.get(engine_name, {}).get("capabilities", {})
    score = 0.5
    if ext in caps.get("formats", []):
        score += 0.3
    if caps.get("table_preservation") and ext in (".pdf", ".docx", ".xlsx"):
        score += 0.1
    if caps.get("ocr_support") and ext in (".pdf", ".png", ".jpg", ".jpeg", ".tiff"):
        score += 0.1
    return min(score, 1.0)


def select_engines(file_path: str) -> list[str]:
    ext = Path(file_path).suffix.lower()
    text_formats = {".md", ".txt", ".markdown", ".json", ".csv", ".xml", ".html", ".htm", ".yaml", ".yml"}
    if ext in text_formats:
        return ["markitdown", "plaintext"]
    if ext == ".pdf":
        return ["markitdown", "pdftotext", "plaintext"]
    if ext in (".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls"):
        return ["markitdown", "plaintext"]
    return ["markitdown", "plaintext"]


def parse_with_routing(file_path: str) -> dict:
    ext = Path(file_path).suffix.lower()
    source_path = os.path.abspath(os.path.expanduser(file_path))
    if not os.path.isfile(source_path):
        return {"ok": False, "engine": "none", "error": f"file not found: {file_path}"}

    engines = select_engines(file_path)
    attempts = []

    for engine_name in engines:
        parser_fn = get_engine(engine_name)
        if not parser_fn:
            continue
        try:
            result = _cached_or_parse(source_path, engine_name, parser_fn)
            result["engine"] = engine_name
            result["cache_hit"] = result.get("cache_hit", False)
            attempts.append(result)
            if result.get("ok"):
                return result
        except Exception as exc:
            attempts.append({"engine": engine_name, "ok": False, "error": str(exc)})

    return {
        "ok": False,
        "engine": "none",
        "error": "all engines failed",
        "attempts": attempts,
        "ext": ext,
    }


def batch_parse(paths: list[str], workers: int = 4) -> list[dict]:
    from concurrent.futures import ThreadPoolExecutor
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(parse_with_routing, p): p for p in paths}
        for future in futures:
            results.append(future.result())
    return results


def _engine_markitdown(source_path: str) -> dict:
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(source_path)
        text = result.text_content if hasattr(result, "text_content") else str(result)
        return {"ok": bool(text.strip()), "text": text.strip()}
    except ImportError:
        return {"ok": False, "error": "markitdown not installed"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _engine_plaintext(source_path: str) -> dict:
    ext = Path(source_path).suffix.lower()
    text_formats = {".txt", ".md", ".markdown", ".json", ".csv", ".xml", ".html", ".htm", ".yaml", ".yml"}
    if ext not in text_formats:
        return {"ok": False, "error": f"unsupported format: {ext}"}
    text = Path(source_path).read_text(encoding="utf-8", errors="replace")
    return {"ok": bool(text.strip()), "text": text.strip()}


def _engine_pdftotext(source_path: str) -> dict:
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", source_path, "-"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            return {"ok": False, "error": result.stderr.strip() or "pdftotext failed"}
        return {"ok": True, "text": result.stdout.strip()}
    except FileNotFoundError:
        return {"ok": False, "error": "pdftotext not installed"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "pdftotext timed out"}


register_engine("markitdown", {"formats": [".pdf", ".docx", ".pptx", ".xlsx", ".html", ".csv", ".json", ".xml"], "table_preservation": True, "ocr_support": False}, _engine_markitdown)
register_engine("pdftotext", {"formats": [".pdf"], "table_preservation": False, "ocr_support": False}, _engine_pdftotext)
register_engine("plaintext", {"formats": [".txt", ".md", ".json", ".csv", ".xml", ".html", ".yaml", ".yml"], "table_preservation": False, "ocr_support": False}, _engine_plaintext)
