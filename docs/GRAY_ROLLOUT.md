# KMM Gray Rollout

## Purpose

Use this process when replacing server-side KMM runtime scripts with repository-managed installed scripts.

## Steps

1. Backup repository checkout and current KMM-managed runtime scripts.
2. Deploy the repository revision to the server checkout.
3. Run:

```bash
AGENT_HOME=<server-agent-home> \
KMM_NONINTERACTIVE=1 \
KMM_SKIP_CRON=1 \
bash install.sh
```

4. Validate:

```bash
<server-agent-home>/scripts/verify_plugin.sh
python3 <server-agent-home>/scripts/gray_validation_suite.py
```

5. Compare outputs from:
- `lightweight_recall.py`
- `knowledge_discovery.py`
- `onedrive_bidirectional_sync.sh --dry-run` or `KMM_SYNC_DRY_RUN=true`

6. If validation passes, update cron if needed and record the cutover in `docs/CONTINUOUS_DEVELOPMENT.md`.

## Stop conditions

Stop the rollout if:

- install output misses managed scripts
- validation shows missing imports or missing note paths
- sync behavior changes unexpectedly
- recall output regresses materially
