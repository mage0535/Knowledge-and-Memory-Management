"""Fresh install, upgrade, and uninstall safety tests."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parent.parent


def test_fresh_install_deploys_all_managed_scripts(tmp_path: Path):
    agent_home = tmp_path / "agent-home"
    agent_home.mkdir()

    result = subprocess.run(
        ["bash", str(REPO / "install.sh")],
        capture_output=True, text=True, timeout=120,
        env={**__import__("os").environ, "AGENT_HOME": str(agent_home), "KMM_NONINTERACTIVE": "1", "KMM_SKIP_CRON": "1"},
    )
    assert result.returncode == 0, f"install.sh failed: {result.stderr[-500:]}"

    scripts_dir = agent_home / "scripts"
    assert scripts_dir.is_dir(), "scripts dir not created"

    manifest = (REPO / "configs" / "managed_scripts.txt").read_text(encoding="utf-8")
    for name in manifest.strip().splitlines():
        name = name.strip()
        if not name:
            continue
        script = scripts_dir / name
        assert script.exists(), f"managed script not deployed: {name}"

    plugin_dir = agent_home / "knowledge-plugin"
    assert plugin_dir.is_dir()
    assert (plugin_dir / "__init__.py").exists()

    knowledge_dir = agent_home / "knowledge"
    assert knowledge_dir.is_dir()


def test_upgrade_preserves_existing_notes(tmp_path: Path):
    agent_home = tmp_path / "agent-home"
    agent_home.mkdir()

    notes_dir = agent_home / "knowledge" / "notes" / "shared"
    notes_dir.mkdir(parents=True)
    existing_note = notes_dir / "keep-me.md"
    existing_note.write_text("# Keep Me\n\nexisting note content\n", encoding="utf-8")

    result = subprocess.run(
        ["bash", str(REPO / "install.sh")],
        capture_output=True, text=True, timeout=120,
        env={**__import__("os").environ, "AGENT_HOME": str(agent_home), "KMM_NONINTERACTIVE": "1", "KMM_SKIP_CRON": "1"},
    )
    assert result.returncode == 0, f"install failed: {result.stderr[-500:]}"

    assert existing_note.exists(), "existing note was deleted by upgrade"
    content = existing_note.read_text(encoding="utf-8")
    assert "Keep Me" in content


def test_uninstall_removes_scripts_preserves_data(tmp_path: Path):
    agent_home = tmp_path / "agent-home"
    agent_home.mkdir()

    subprocess.run(
        ["bash", str(REPO / "install.sh")],
        capture_output=True, text=True, timeout=120,
        env={**__import__("os").environ, "AGENT_HOME": str(agent_home), "KMM_NONINTERACTIVE": "1", "KMM_SKIP_CRON": "1"},
    )

    notes_dir = agent_home / "knowledge" / "notes" / "personal"
    notes_dir.mkdir(parents=True, exist_ok=True)
    test_note = notes_dir / "test.md"
    test_note.write_text("# Test Note\n", encoding="utf-8")

    result = subprocess.run(
        ["bash", str(REPO / "uninstall.sh")],
        capture_output=True, text=True, timeout=60,
        env={**__import__("os").environ, "AGENT_HOME": str(agent_home), "KMM_NONINTERACTIVE": "1"},
    )
    assert test_note.exists(), "note data was deleted by uninstall"


def test_uninstall_script_contains_data_preservation_message():
    content = (REPO / "uninstall.sh").read_text(encoding="utf-8")
    assert "知识数据默认保留" in content


def test_install_manifest_created(tmp_path: Path):
    agent_home = tmp_path / "agent-home"
    agent_home.mkdir()

    subprocess.run(
        ["bash", str(REPO / "install.sh")],
        capture_output=True, text=True, timeout=120,
        env={**__import__("os").environ, "AGENT_HOME": str(agent_home), "KMM_NONINTERACTIVE": "1", "KMM_SKIP_CRON": "1"},
    )

    manifest = agent_home / "scripts" / "kmm-install-manifest.txt"
    assert manifest.exists(), "install manifest not created"
    content = manifest.read_text(encoding="utf-8")
    assert "commit=" in content
    assert "installed_at=" in content
