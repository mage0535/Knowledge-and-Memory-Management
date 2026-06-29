#!/usr/bin/env bash
# 验证插件安装状态

AGENT_HOME_ROOT="${AGENT_HOME:-${HERMES_HOME:-$HOME/.hermes}}"

echo "══════════════ Knowledge Memory Plugin 验证 ══════════════"
echo ""

errors=0

check() {
    if [ $? -eq 0 ]; then
        echo -e "  ✓ $1"
    else
        echo -e "  ✗ $1"
        errors=$((errors+1))
    fi
}

echo "── 记忆体系统 ──"
curl -sf http://localhost:8787/health &>/dev/null && echo "  ✓ gbrain (8787)" || { echo "  - gbrain (未安装/未运行, 可选)"; }
curl -sf http://localhost:8890/health &>/dev/null && echo "  ✓ Hindsight (8890)" || { echo "  - Hindsight (未安装/未运行, 可选)"; }

echo ""
echo "── 系统依赖 ──"
command -v python3 &>/dev/null && echo "  ✓ Python $(python3 --version 2>&1 | awk '{print $2}')" || { echo "  ✗ Python"; errors=$((errors+1)); }
command -v rclone &>/dev/null && echo "  ✓ rclone" || { echo "  - rclone (可选)"; }

echo ""
echo "── 插件目录 ──"
[ -d "${AGENT_HOME_ROOT}/knowledge/notes" ] && echo "  ✓ 笔记目录" || { echo "  ✗ 笔记目录缺失"; errors=$((errors+1)); }
[ -d "${AGENT_HOME_ROOT}/knowledge-plugin" ] && echo "  ✓ Python 模块" || { echo "  - Python 模块 (未安装)"; }

echo ""
echo "── 云存储 ──"
rclone listremotes &>/dev/null && echo "  ✓ 已配置云盘: $(rclone listremotes 2>/dev/null | tr '\n' ' ')" || { echo "  - 无云盘配置"; }

echo ""
if [ $errors -eq 0 ]; then
    echo -e "✅ 所有检查通过"
else
    echo -e "⚠️  $errors 个检查未通过（部分为可选组件）"
fi
