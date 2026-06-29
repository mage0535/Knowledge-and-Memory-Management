# 快速开始

## 前提

已安装记忆体系统（[Hermes Memory Installer](https://github.com/mage0535/hermes-memory-installer) v3.0+）时效果最佳；未安装时也可使用公开采集与笔记能力。

## 安装

```bash
git clone https://github.com/mage0535/Knowledge-and-Memory-Management.git
cd Knowledge-and-Memory-Management
chmod +x install.sh
export AGENT_HOME="${AGENT_HOME:-$HOME/.hermes}"
./install.sh
```

安装过程交互式引导，大约需要 2 分钟。

## 安装后

### 1. 验证安装

```bash
./scripts/verify_plugin.sh
```

### 2. 配置云盘（可选）

```bash
rclone config
# 按提示配置你的云盘
```

或使用预配置模板：

```bash
./scripts/install_rclone_drives.sh
```

### 3. 体验知识采集

你的 Agent 现在可以直接从网页、视频等来源采集知识并自动生成笔记。

### 4. 触发笔记同步

```bash
# 手动同步
rclone copy "${AGENT_HOME:-$HOME/.hermes}/knowledge/notes/" onedrive:知识库/笔记/ --progress

# 查看自动同步状态
crontab -l | grep knowledge-sync
```
