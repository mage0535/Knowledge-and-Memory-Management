from __future__ import annotations

from pathlib import Path
import json
import os
import sys


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from cloud_sync import CloudSyncEngine, bidirectional_sync


def test_cloud_sync_has_non_destructive_bisync(monkeypatch):
    calls = []
    monkeypatch.setattr(CloudSyncEngine, "_check_rclone", lambda self: None)
    monkeypatch.setattr(
        CloudSyncEngine,
        "_run",
        lambda self, cmd: calls.append(cmd) or type("Result", (), {"returncode": 0})(),
    )

    engine = CloudSyncEngine()
    engine.bisync("/tmp/local", "onedrive", "notes/path", resync=False)

    assert calls
    assert calls[0][:3] == ["rclone", "bisync", "/tmp/local"]
    assert "--resync" not in calls[0]


def test_cloud_sync_can_opt_in_to_resync(monkeypatch):
    calls = []
    monkeypatch.setattr(CloudSyncEngine, "_check_rclone", lambda self: None)
    monkeypatch.setattr(
        CloudSyncEngine,
        "_run",
        lambda self, cmd: calls.append(cmd) or type("Result", (), {"returncode": 0})(),
    )

    engine = CloudSyncEngine()
    engine.bisync("/tmp/local", "onedrive", "notes/path", resync=True)

    assert "--resync" in calls[0]


def test_public_bidirectional_sync_parses_remote(monkeypatch):
    calls = []
    monkeypatch.setattr(CloudSyncEngine, "_check_rclone", lambda self: None)
    monkeypatch.setattr(
        CloudSyncEngine,
        "_run",
        lambda self, cmd: calls.append(cmd) or type("Result", (), {"returncode": 0})(),
    )

    bidirectional_sync("onedrive:notes/path", local="/tmp/local")

    assert calls[0][3] == "onedrive:notes/path"


def test_onedrive_sync_script_uses_bisync_and_remote_env():
    content = (REPO / "scripts" / "onedrive_bidirectional_sync.sh").read_text(encoding="utf-8")
    assert "KMM_SYNC_REMOTE" in content
    assert "rclone bisync" in content
    assert "--resync" not in content.splitlines()[0:999] or "RESYNC" in content
    assert "KMM_SYNC_DRY_RUN" in content
    assert "--dry-run" in content


def test_nightly_maintenance_runs_public_scripts():
    content = (REPO / "scripts" / "nightly_maintenance.py").read_text(encoding="utf-8")
    assert "knowledge_discovery.py" in content
    assert "onedrive_bidirectional_sync.sh" in content
    assert "lightweight_recall.py" in content


def test_doc_parse_router_prefers_fast_first_chain():
    content = (REPO / "scripts" / "doc_parse_router.py").read_text(encoding="utf-8")
    assert "parse_with_liteparse" in content
    assert "parse_with_markitdown" in content
    assert "parse_with_pdftotext" in content


def test_lightweight_recall_uses_parallel_layer_execution():
    content = (REPO / "scripts" / "lightweight_recall.py").read_text(encoding="utf-8")
    assert "ThreadPoolExecutor" in content
    assert 'KMM_HINDSIGHT_TIMEOUT' in content
    assert 'KMM_GBRAIN_TIMEOUT' in content


def test_book_cache_manager_can_rebuild_index(tmp_path: Path):
    sys.path.insert(0, str(REPO / "scripts"))
    import book_cache_manager as bcm

    listing = tmp_path / "listing.txt"
    listing.write_text("1048576 category/book.pdf\n2048 docs/guide.epub\n", encoding="utf-8")
    bcm.CACHE_ROOT = tmp_path / "cache"
    bcm.INDEX_FILE = bcm.CACHE_ROOT / "book_index.json"
    bcm.CACHE_FILES_DIR = bcm.CACHE_ROOT / "files"

    payload = bcm.rebuild_index_from_listing(str(listing))

    assert len(payload["books"]) == 2
    assert payload["books"][0]["filename"] == "book.pdf"
    assert bcm.INDEX_FILE.exists()


def test_install_script_deploys_linux_runtime_scripts():
    content = (REPO / "install.sh").read_text(encoding="utf-8")
    assert "configs/managed_scripts.txt" in content
    manifest = (REPO / "configs" / "managed_scripts.txt").read_text(encoding="utf-8")
    for name in (
        "book_cache_manager.py",
        "doc_parse_router.py",
        "nightly_maintenance.py",
        "onedrive_bidirectional_sync.sh",
    ):
        assert name in manifest


def test_install_script_supports_noninteractive_and_skip_cron():
    content = (REPO / "install.sh").read_text(encoding="utf-8")
    assert 'KMM_NONINTERACTIVE="${KMM_NONINTERACTIVE:-0}"' in content
    assert 'KMM_SKIP_CRON="${KMM_SKIP_CRON:-0}"' in content
    assert 'if [ "$KMM_NONINTERACTIVE" = "1" ] || [ ! -t 0 ]; then' in content
    assert 'if [ "$KMM_SKIP_CRON" = "1" ]; then' in content


def test_managed_scripts_manifest_exists():
    manifest = REPO / "configs" / "managed_scripts.txt"
    content = manifest.read_text(encoding="utf-8")
    assert "knowledge_discovery.py" in content
    assert "verify_plugin.sh" in content
