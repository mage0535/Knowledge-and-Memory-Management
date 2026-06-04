#!/usr/bin/env bash
set -euo pipefail

# 卸载插件
echo "移除知识采集和云同步模块..."
rm -rf "${HOME}/.hermes/knowledge-plugin" 2>/dev/null || true
rm -rf "${HOME}/.hermes/knowledge" 2>/dev/null || true

# 清理 cron
crontab -l 2>/dev/null | grep -v "knowledge-sync" | crontab -

echo "卸载完成。笔记文件未被删除（如需删除请手动: rm -rf ~/.hermes/knowledge）"
