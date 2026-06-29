#!/usr/bin/env bash
set -euo pipefail

AGENT_HOME_ROOT="${AGENT_HOME:-${HERMES_HOME:-$HOME/.hermes}}"

# 卸载插件
echo "移除知识采集和云同步模块..."
rm -rf "${AGENT_HOME_ROOT}/knowledge-plugin" 2>/dev/null || true
rm -f "${AGENT_HOME_ROOT}/scripts/knowledge_fetch_router.py" 2>/dev/null || true
rm -f "${AGENT_HOME_ROOT}/scripts/knowledge_discovery.py" 2>/dev/null || true
rm -f "${AGENT_HOME_ROOT}/scripts/lightweight_recall.py" 2>/dev/null || true
rm -f "${AGENT_HOME_ROOT}/scripts/verify_plugin.sh" 2>/dev/null || true
rm -f "${AGENT_HOME_ROOT}/scripts/install_rclone_drives.sh" 2>/dev/null || true
rm -f "${AGENT_HOME_ROOT}/scripts/distill_methodologies.py" 2>/dev/null || true
rm -f "${AGENT_HOME_ROOT}/scripts/book_keyword_index.py" 2>/dev/null || true

# 清理 cron
if command -v crontab >/dev/null 2>&1; then
  crontab -l 2>/dev/null | grep -v "knowledge-sync" | crontab - || true
fi

echo "卸载完成。知识数据默认保留在 ${AGENT_HOME_ROOT}/knowledge"
echo "如需删除数据，请手动确认后执行: rm -rf ${AGENT_HOME_ROOT}/knowledge"
