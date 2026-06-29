#!/usr/bin/env bash
set -euo pipefail

LOCAL_NOTES_DIR="${KMM_LOCAL_NOTES_DIR:-${KMM_NOTES_DIR:-${AGENT_HOME:-${HERMES_HOME:-$HOME/.hermes}}/knowledge/notes}}"
REMOTE_TARGET="${KMM_SYNC_REMOTE:-}"
LOCK_FILE="${KMM_SYNC_LOCK:-/tmp/kmm_onedrive_sync.lock}"
RESYNC="${KMM_SYNC_RESYNC:-false}"
DRY_RUN="${KMM_SYNC_DRY_RUN:-false}"
EXTRA_FLAGS="${KMM_SYNC_EXTRA_FLAGS:-}"

log() {
  printf '[kmm-sync] %s\n' "$1"
}

if ! command -v rclone >/dev/null 2>&1; then
  log "rclone not installed; skipping"
  exit 0
fi

if [ -z "$REMOTE_TARGET" ]; then
  log "KMM_SYNC_REMOTE not configured; skipping"
  exit 0
fi

REMOTE_NAME="${REMOTE_TARGET%%:*}"
if ! rclone listremotes 2>/dev/null | grep -q "^${REMOTE_NAME}:"; then
  log "remote ${REMOTE_NAME} not configured; skipping"
  exit 0
fi

mkdir -p "$(dirname "$LOCK_FILE")"
if [ -f "$LOCK_FILE" ]; then
  log "previous sync still locked; skipping"
  exit 0
fi
trap 'rm -f "$LOCK_FILE"' EXIT
touch "$LOCK_FILE"

mkdir -p "$LOCAL_NOTES_DIR"
log "sync start: ${LOCAL_NOTES_DIR} <-> ${REMOTE_TARGET}"

CMD=(rclone bisync "$LOCAL_NOTES_DIR" "$REMOTE_TARGET" --create-empty-src-dirs --checkers 4 --transfers 2)
if [ "$RESYNC" = "true" ]; then
  CMD+=(--resync)
fi
if [ "$DRY_RUN" = "true" ]; then
  CMD+=(--dry-run)
fi
if [ -n "$EXTRA_FLAGS" ]; then
  # shellcheck disable=SC2206
  EXTRA=($EXTRA_FLAGS)
  CMD+=("${EXTRA[@]}")
fi

"${CMD[@]}"
log "sync complete"
