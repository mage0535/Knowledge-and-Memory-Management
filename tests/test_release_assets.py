from __future__ import annotations

from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


def test_release_docs_exist():
    for name in (
        "RELEASE_CHECKLIST.md",
        "GRAY_ROLLOUT.md",
        "ROLLBACK.md",
        "SERVER_SCRIPT_MAPPING.md",
        "CONTINUOUS_DEVELOPMENT.md",
    ):
        assert (REPO / "docs" / name).exists()


def test_ci_workflow_exists():
    workflow = REPO / ".github" / "workflows" / "ci.yml"
    assert workflow.exists()
    content = workflow.read_text(encoding="utf-8")
    assert "pytest -q" in content
    assert "python scripts/sensitive_scan.py" in content
