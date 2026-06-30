#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Knowledge and Memory Management Plugin — Installer
# 为已安装记忆体系统的 AI Agent 添加知识采集和云盘同步能力
# ============================================================

VERSION="0.2.0"
PLUGIN_NAME="Knowledge and Memory Management"
PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_HOME_OVERRIDE="${AGENT_HOME:-${HERMES_HOME:-}}"
KMM_SYNC_REMOTE="${KMM_SYNC_REMOTE:-}"
KMM_NONINTERACTIVE="${KMM_NONINTERACTIVE:-0}"
KMM_SKIP_CRON="${KMM_SKIP_CRON:-0}"
MANAGED_SCRIPTS_FILE="${PLUGIN_DIR}/configs/managed_scripts.txt"

# 颜色
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()   { echo -e "${RED}[ERR]${NC} $1"; exit 1; }

resolve_python_installer() {
    if [ -n "${KMM_PYTHON_BIN:-}" ] && [ -x "${KMM_PYTHON_BIN}" ]; then
        echo "${KMM_PYTHON_BIN}"
        return
    fi
    if [ -x "${HERMES_HOME}/hermes-agent/.venv/bin/python3" ]; then
        echo "${HERMES_HOME}/hermes-agent/.venv/bin/python3"
        return
    fi
    if [ -x "${HERMES_HOME}/.venv/bin/python3" ]; then
        echo "${HERMES_HOME}/.venv/bin/python3"
        return
    fi
    echo "python3"
}

# ---- 检测记忆体系统 ----
detect_memory_system() {
    info "检测记忆体系统..."
    MEMORY_INSTALLED=false

    # 检测 gbrain
    if command -v gbrain &>/dev/null || curl -sf http://localhost:8787/health &>/dev/null; then
        ok "gbrain 检测到 (端口 8787)"
        GRAIN_OK=true
    else
        warn "gbrain 未检测到（知识图谱功能受限，其他功能仍可用）"
        GRAIN_OK=false
    fi

    # 检测 Hindsight
    if curl -sf http://localhost:8890/health &>/dev/null; then
        ok "Hindsight 检测到 (端口 8890)"
        HINDSIGHT_OK=true
    else
        warn "Hindsight 未检测到（向量存储功能受限，其他功能仍可用）"
        HINDSIGHT_OK=false
    fi

    # 检测 Hermes Agent 目录
    if [ -n "$AGENT_HOME_OVERRIDE" ]; then
        HERMES_HOME="$AGENT_HOME_OVERRIDE"
        ok "Agent 目录使用环境变量: $HERMES_HOME"
        MEMORY_INSTALLED=true
    elif [ -d "$HOME/.hermes" ]; then
        ok "Hermes Agent 目录检测到 ($HOME/.hermes)"
        HERMES_HOME="$HOME/.hermes"
        MEMORY_INSTALLED=true
    elif [ -d "$HOME/.claude" ]; then
        ok "Claude Code 目录检测到 ($HOME/.claude)"
        HERMES_HOME="$HOME/.claude"
        MEMORY_INSTALLED=true
    else
        warn "未检测到已知 Agent 目录，将使用默认位置"
        HERMES_HOME="$HOME/.hermes"
    fi

    if [ "$MEMORY_INSTALLED" = false ]; then
        warn "未检测到已安装的记忆体系统"
        echo -e "  继续安装将仅部署知识采集和笔记管理模块（无 Warm/Cold 记忆层集成）"
        echo -e "  如需完整功能，请先安装: https://github.com/mage0535/hermes-memory-installer"
    fi
}

# ---- 检测依赖 ----
detect_deps() {
    info "检测系统依赖..."
    
    # Python
    if command -v python3 &>/dev/null; then
        PY_VER="$(python3 --version | cut -d' ' -f2)"
        ok "Python ${PY_VER}"
    else
        err "需要 Python 3.9+"
    fi

    # rclone
    if command -v rclone &>/dev/null; then
        RCLONE_VER=$(rclone version 2>&1 | head -1 | awk '{print $2}')
        ok "rclone $RCLONE_VER"
        RCLONE_OK=true
    else
        warn "rclone 未安装"
        echo "  安装: curl https://rclone.org/install.sh | sudo bash"
        echo "  或: sudo apt install rclone"
        RCLONE_OK=false
    fi

    # FFmpeg（视频分析需要）
    if command -v ffmpeg &>/dev/null; then
        ok "ffmpeg $(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')"
    else
        warn "ffmpeg 未安装（视频分析需要）"
        echo "  安装: sudo apt install ffmpeg"
    fi

    # Tesseract（OCR 需要）
    if command -v tesseract &>/dev/null; then
        TESS_VER=$(tesseract --version 2>&1 | head -1 | awk '{print $2}')
        ok "tesseract ${TESS_VER:-已安装}"
    else
        warn "tesseract 未安装（OCR 需要）"
        echo "  安装: sudo apt install tesseract-ocr tesseract-ocr-chi-sim"
    fi

    # yt-dlp（视频/音频下载引擎）
    if command -v yt-dlp &>/dev/null; then
        YTDLP_VER=$(yt-dlp --version 2>/dev/null || echo "未知")
        ok "yt-dlp $YTDLP_VER"
    else
        warn "yt-dlp 未安装（视频采集需要）"
        echo "  安装: pip install yt-dlp"
    fi
}

# ---- 部署目录结构 ----
deploy_dirs() {
    info "创建笔记和知识库目录结构..."

    KNOWLEDGE_BASE="${HERMES_HOME}/knowledge"
    
    mkdir -p "$KNOWLEDGE_BASE"/{notes,books,cache,raw,config}
    mkdir -p "$KNOWLEDGE_BASE/notes"/{personal,shared,archive}
    mkdir -p "$KNOWLEDGE_BASE/cache"/{web,video,article}

    ok "知识库目录: $KNOWLEDGE_BASE"
}

# ---- 安装 Python 模块 ----
deploy_python_modules() {
    info "部署 Python 模块..."

    TARGET="${HERMES_HOME}/knowledge-plugin"
    INSTALL_PYTHON="$(resolve_python_installer)"
    mkdir -p "$TARGET"

    cp -r "$PLUGIN_DIR/src"/* "$TARGET/"
    
    # 安装依赖
    if [ -f "$PLUGIN_DIR/requirements.txt" ]; then
        "${INSTALL_PYTHON}" -m pip install -r "$PLUGIN_DIR/requirements.txt" --quiet || \
        warn "pip 安装部分依赖失败（可手动安装）"
    fi

    if "${INSTALL_PYTHON}" -c "from markitdown import MarkItDown" >/dev/null 2>&1; then
        ok "markitdown 已可用"
    else
        warn "markitdown 不可用，文档采集能力将受限"
    fi

    ok "Python 模块部署到: $TARGET"
}

# ---- 部署公共脚本 ----
deploy_scripts() {
    info "部署公共脚本..."
    TARGET="${HERMES_HOME}/scripts"
    mkdir -p "$TARGET"
    while IFS= read -r script_name; do
        [ -n "$script_name" ] || continue
        cp "$PLUGIN_DIR/scripts/${script_name}" "$TARGET/${script_name}"
        chmod +x "$TARGET/${script_name}" || true
    done < "$MANAGED_SCRIPTS_FILE"
    printf '%s\n' "commit=${KMM_RELEASE_COMMIT:-unknown}" "installed_at=$(date -Is)" > "${TARGET}/kmm-install-manifest.txt"
    ok "公共脚本部署到: $TARGET"
}

# ---- 配置云同步 ----
configure_cloud_sync() {
    if [ "$RCLONE_OK" = false ]; then
        warn "跳过云同步配置（需要先安装 rclone）"
        return
    fi

    if [ "$KMM_NONINTERACTIVE" = "1" ] || [ ! -t 0 ]; then
        warn "非交互模式，跳过云盘配置"
        return
    fi

    echo ""
    echo -e "${BLUE}┌─────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│  云盘同步配置                              │${NC}"
    echo -e "${BLUE}│  跳过此步可稍后通过 rclone config 配置      │${NC}"
    echo -e "${BLUE}└─────────────────────────────────────────┘${NC}"
    echo ""
    echo "可用云盘: OneDrive / Google Drive / 阿里云盘 / 百度云盘 / 坚果云 / Dropbox / Mega / 天翼云 / iCloud / Nextcloud / 115 / 夸克"
    echo ""
    read -r -p "现在配置云盘? [y/N] " REPLY
    if [[ "$REPLY" =~ ^[Yy] ]]; then
        echo "运行 rclone config 交互式配置..."
        rclone config
    else
        echo "跳过。稍后通过 rclone config 手动配置，或参考:"
        echo "  https://github.com/mage0535/Knowledge-and-Memory-Management/blob/main/docs/cloud-sync.md"
    fi
}

# ---- 部署配置 ----
deploy_config() {
    info "部署配置模板..."

    CONFIG_DST="${HERMES_HOME}/knowledge/config"
    mkdir -p "$CONFIG_DST"

    if [ -d "$PLUGIN_DIR/config" ]; then
        cp -r "$PLUGIN_DIR/config"/* "$CONFIG_DST/" 2>/dev/null || true
        ok "配置模板已部署到: $CONFIG_DST"
    fi
}

# ---- 设置定时任务 ----
setup_cron() {
    info "设置 Linux 定时任务..."

    if [ "$KMM_SKIP_CRON" = "1" ]; then
        warn "KMM_SKIP_CRON=1，跳过定时任务配置"
        return
    fi

    if ! command -v crontab >/dev/null 2>&1; then
        warn "crontab 不可用，跳过定时任务配置"
        return
    fi

    CRON_LINES="$(crontab -l 2>/dev/null | grep -v 'knowledge-sync' | grep -v 'knowledge-discovery' | grep -v 'kmm-nightly' || true)"

    if [ -n "$KMM_SYNC_REMOTE" ] && rclone listremotes 2>/dev/null | grep -q "^${KMM_SYNC_REMOTE%%:*}:"; then
        CRON_LINES="${CRON_LINES}"$'\n'"*/30 * * * * KMM_SYNC_REMOTE=${KMM_SYNC_REMOTE} bash ${HERMES_HOME}/scripts/onedrive_bidirectional_sync.sh # knowledge-sync"
    else
        warn "未配置有效的 KMM_SYNC_REMOTE，跳过双向同步 cron"
    fi

    CRON_LINES="${CRON_LINES}"$'\n'"0 2 * * * python3 ${HERMES_HOME}/scripts/nightly_maintenance.py # kmm-nightly"
    CRON_LINES="${CRON_LINES}"$'\n'"0 4 * * 0 python3 ${HERMES_HOME}/scripts/knowledge_discovery.py # knowledge-discovery"
    printf '%s\n' "$CRON_LINES" | sed '/^$/d' | crontab -
    ok "Linux 定时任务已更新"
}

# ---- 输出摘要 ----
print_summary() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ${PLUGIN_NAME} v${VERSION} 安装完成              ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
    echo ""
    echo "  插件目录: $PLUGIN_DIR"
    echo "  知识库:   ${HERMES_HOME}/knowledge/"
    echo "  模块:     ${HERMES_HOME}/knowledge-plugin/"
    echo ""
    echo "  记忆体集成:"
    echo "    gbrain:    ${GRAIN_OK:-false}"
    echo "    Hindsight: ${HINDSIGHT_OK:-false}"
    echo ""
    echo "  📖 查看文档:"
    echo "    cat ${PLUGIN_DIR}/docs/quick-start.md"
    echo "    cat ${PLUGIN_DIR}/docs/cloud-sync.md"
    echo ""
    echo "  🔧 验证安装:"
    echo "    ${HERMES_HOME}/scripts/verify_plugin.sh"
    echo ""
}

# ---- 主流程 ----
main() {
    echo ""
    echo -e "${BLUE}═══ ${PLUGIN_NAME} v${VERSION} 安装程序 ═══${NC}"
    echo ""

    detect_memory_system
    echo ""
    detect_deps
    echo ""
    deploy_dirs
    deploy_python_modules
    deploy_scripts
    deploy_config
    echo ""
    configure_cloud_sync
    echo ""
    setup_cron
    echo ""
    print_summary
}

main "$@"
