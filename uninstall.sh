#!/usr/bin/env bash
set -euo pipefail

AGENT_HOME_ROOT="${AGENT_HOME:-${HERMES_HOME:-$HOME/.hermes}}"
SCRIPT_MANIFEST="${AGENT_HOME_ROOT}/scripts/kmm-install-manifest.txt"

# 卸载插件
echo "移除知识采集和云同步模块..."
rm -rf "${AGENT_HOME_ROOT}/knowledge-plugin" 2>/dev/null || true
for script_name in \
  knowledge_fetch_router.py \
  knowledge_discovery.py \
  lightweight_recall.py \
  verify_plugin.sh \
  install_rclone_drives.sh \
  distill_methodologies.py \
  book_keyword_index.py \
  book_cache_manager.py \
  book_to_skill.py \
  doc_parse_router.py \
  gbrain_compact.py \
  gbrain_link_orphans.py \
  gray_validation_suite.py \
  nightly_maintenance.py \
  onedrive_bidirectional_sync.sh \
  recall_shadow_compare.py \
  sensenova_dispatcher.py
do
  rm -f "${AGENT_HOME_ROOT}/scripts/${script_name}" 2>/dev/null || true
done
rm -f "${SCRIPT_MANIFEST}" 2>/dev/null || true

# 清理 cron
if command -v crontab >/dev/null 2>&1; then
  crontab -l 2>/dev/null | grep -v "knowledge-sync" | crontab - || true
fi

echo "卸载完成。知识数据默认保留在 ${AGENT_HOME_ROOT}/knowledge"
echo "如需删除数据，请手动确认后执行: rm -rf ${AGENT_HOME_ROOT}/knowledge"
