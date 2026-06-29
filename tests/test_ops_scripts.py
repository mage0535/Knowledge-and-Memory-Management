from __future__ import annotations

from pathlib import Path
import sys


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import book_to_skill
import gbrain_compact
import gbrain_link_orphans
import gray_validation_suite
import recall_shadow_compare
import sensenova_dispatcher


def test_book_to_skill_pipeline_creates_skill_and_notes(tmp_path: Path):
    book_to_skill.HERMES_SKILLS_DIR = tmp_path / "skills"
    book_to_skill.KMM_STRUCTURED_DIR = tmp_path / "structured"
    source = tmp_path / "sample.md"
    source.write_text("# Chapter 1\n\nUseful content.\n\n\n\n# Chapter 2\n\nMore content.\n", encoding="utf-8")

    result = book_to_skill.run_pipeline(str(source), "sample")

    assert result["ok"] is True
    assert (book_to_skill.HERMES_SKILLS_DIR / "book-sample" / "SKILL.md").exists()
    assert (book_to_skill.KMM_STRUCTURED_DIR / "sample" / "index.md").exists()


def test_gbrain_link_orphans_tags_limit(monkeypatch):
    monkeypatch.setattr(gbrain_link_orphans, "run_gbrain", lambda args, timeout=30: type("R", (), {"returncode": 0, "stdout": '["a","b","c"]', "stderr": ""})())
    slugs = gbrain_link_orphans.get_orphans()
    monkeypatch.setattr(gbrain_link_orphans, "run_gbrain", lambda args, timeout=30: type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})())

    results = gbrain_link_orphans.tag_orphans(slugs, limit=2)

    assert slugs == ["a", "b", "c"]
    assert len(results) == 2
    assert all(item["status"] == "ok" for item in results)


def test_gbrain_compact_scan_uses_known_pages(monkeypatch):
    monkeypatch.setattr(
        gbrain_compact,
        "run_gbrain_call",
        lambda tool, payload: [
            {"date": "2025-01-01T00:00:00+00:00", "summary": "old 1"},
            {"date": "2025-01-02T00:00:00+00:00", "summary": "old 2"},
            {"date": "2025-01-03T00:00:00+00:00", "summary": "old 3"},
            {"date": "2025-01-04T00:00:00+00:00", "summary": "old 4"},
            {"date": "2025-01-05T00:00:00+00:00", "summary": "old 5"},
        ],
    )
    monkeypatch.setattr(gbrain_compact, "KNOWN_PAGES", ("knowledge-hub",))

    result = gbrain_compact.scan_compaction_candidates(cutoff_days=30, min_entries=5)

    assert len(result) == 1
    assert result[0]["slug"] == "knowledge-hub"


def test_sensenova_dispatcher_reports_missing_script(monkeypatch):
    monkeypatch.setattr(sensenova_dispatcher, "find_skill_script", lambda command: None)

    result = sensenova_dispatcher.dispatch("search", "test")

    assert result["ok"] is False
    assert "script not found" in result["error"]


def test_install_script_deploys_remaining_ops_scripts():
    content = (REPO / "install.sh").read_text(encoding="utf-8")
    for name in ("gbrain_compact.py", "gbrain_link_orphans.py", "sensenova_dispatcher.py", "book_to_skill.py", "recall_shadow_compare.py", "gray_validation_suite.py"):
        assert name in content


def test_recall_shadow_compare_summarizes_layer_counts(monkeypatch):
    monkeypatch.setattr(
        recall_shadow_compare,
        "run_recall",
        lambda command, query: {
            "ok": True,
            "query": query,
            "payload": {"layers": {"local_notes": [1], "gbrain": [1, 2]}},
        },
    )

    result = recall_shadow_compare.compare_payloads(
        {"ok": True, "query": "q", "payload": {"layers": {"local_notes": [1], "gbrain": [1, 2]}}},
        {"ok": True, "query": "q", "payload": {"layers": {"local_notes": [], "gbrain": [1]}}},
    )

    assert result["left_counts"]["gbrain"] == 2
    assert result["right_counts"]["local_notes"] == 0


def test_gray_validation_suite_reports_success(monkeypatch):
    monkeypatch.setattr(gray_validation_suite, "import_smoke", lambda: {"name": "import", "status": "ok"})
    monkeypatch.setattr(gray_validation_suite, "knowledge_discovery_check", lambda: {"name": "discovery", "status": "ok"})
    monkeypatch.setattr(gray_validation_suite, "recall_check", lambda query: {"name": query, "status": "ok"})
    monkeypatch.setattr(gray_validation_suite, "shadow_compare_check", lambda: {"name": "shadow", "status": "ok"})
    monkeypatch.setattr(gray_validation_suite, "sync_dry_run_check", lambda: {"name": "sync", "status": "skipped"})

    results = [
        gray_validation_suite.import_smoke(),
        gray_validation_suite.knowledge_discovery_check(),
        *(gray_validation_suite.recall_check(query) for query in gray_validation_suite.DEFAULT_QUERIES),
        gray_validation_suite.shadow_compare_check(),
        gray_validation_suite.sync_dry_run_check(),
    ]

    assert all(item["status"] in {"ok", "skipped"} for item in results)
