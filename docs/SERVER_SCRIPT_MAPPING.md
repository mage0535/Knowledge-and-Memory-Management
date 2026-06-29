# KMM Server Script Mapping

Last reviewed: 2026-06-29

## Covered by repository-managed KMM

- `book_cache_manager.py`
- `book_keyword_index.py`
- `book_to_skill.py`
- `distill_methodologies.py`
- `doc_parse_router.py`
- `gbrain_compact.py`
- `gbrain_link_orphans.py`
- `gray_validation_suite.py`
- `install_rclone_drives.sh`
- `knowledge_discovery.py`
- `knowledge_fetch_router.py`
- `lightweight_recall.py`
- `nightly_maintenance.py`
- `onedrive_bidirectional_sync.sh`
- `recall_shadow_compare.py`
- `sensenova_dispatcher.py`
- `verify_plugin.sh`

## Belongs to sidecar or broader server operations, not KMM

- `session_to_gbrain.py`
- `memory_governance_rebuild.py`
- `memory_guardian.py`
- `memory_maintenance_cycle.py`
- `tiered_context_injector.py`
- `archive_sessions.py`
- `alert_queue.py`
- `alert_webhook_receiver.py`
- `metrics_dashboard.py`
- `openmetrics_exporter.py`

## Private business or channel operations that should stay outside KMM

- channel publishing scripts
- registration scripts
- market/trading scripts
- social distribution scripts
- unrelated automation helpers under the server agent script directory

## Notes

This document is intentionally coarse-grained.
Detailed cutover evidence should be appended to `docs/CONTINUOUS_DEVELOPMENT.md`.
