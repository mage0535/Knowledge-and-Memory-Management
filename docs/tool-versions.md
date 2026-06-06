# 工具版本参考

KMM 知识采集管线依赖的工具链版本记录。

## 已验证版本（2026-06-06）

### Python 包

| 包名 | 版本 | 说明 | 升级前版本 |
|------|------|------|-----------|
| yt-dlp | **2026.3.17** | 视频/音频下载引擎 | 2024.4.9 🆙 |
| scrapling | **0.4.8** | 反检测网页采集框架 | 0.4.7 🆙 |
| Crawl4AI | 0.8.6 | JS 渲染页面采集 | — |
| easyocr | 1.7.2 | OCR 文字识别 | — |
| **github-copilot-sdk** | **1.0.0** | GitHub Copilot Agent SDK 🆕 | — |
| **paddleocr** | **3.6.0** | 高精度多语言OCR引擎 🆕 | — |
| openai | 2.38.0 | OpenAI API 客户端 | — |
| openai-whisper | 20250625 | 语音识别模型 | — |
| faster-whisper | 1.2.1 | 加速版 Whisper | — |
| beautifulsoup4 | 4.14.3 | HTML 解析 | — |
| markdownify | 1.2.2 | HTML→Markdown 转换 | — |
| trafilatura | 2.0.0 | 网页正文提取 | — |
| sentence-transformers | 5.4.1 | 文本嵌入向量 | — |
| opencv-python | 4.10.0.84 | 图像处理 | — |
| pillow | 12.2.0 | 图像处理 | — |
| jieba | 0.42.1 | 中文分词 | — |
| mutagen | 1.46.0 | 音频元数据处理 | — |

### 系统工具

| 工具 | 版本 | 来源 |
|------|------|------|
| **trivy** | **0.71.0** | /usr/local/bin/trivy 🆕 |
| yt-dlp (CLI) | 2026.3.17 | `/usr/local/bin/yt-dlp` → Hermes venv |
| ffmpeg | 6.1.1 | 系统 apt |
| tesseract | 5.3.4 | 系统 apt |
| rclone | v1.74.1 | 系统安装 |

### 工具桥接脚本

| 脚本 | 来源 | 位置 |
|------|------|------|
| trivy_bridge.py | aquasecurity/trivy (24k⭐) | /root/.hermes/scripts/trivy_bridge.py 🆕 |
| specify_bridge.py | github/spec-kit (15k⭐) | /root/.hermes/scripts/specify_bridge.py 🆕 |
| copilot_sdk_bridge.py | github/copilot-sdk (9.2k⭐) | /root/.hermes/scripts/copilot_sdk_bridge.py 🆕 |
| paddleocr_bridge.py | PaddlePaddle/PaddleOCR (70k⭐) | /root/.hermes/scripts/paddleocr_bridge.py 🆕 |

### 升级记录

| 日期 | 工具 | 旧版本 → 新版本 | 变更类型 |
|------|------|----------------|----------|
| 2026-06-06 | 4 个外部工具桥接 | — → 初版 | 🆕 新增外部工具集成 |
| 2026-06-06 | PaddleOCR | — → 3.6.0 | 🆕 新增高精度 OCR |
| 2026-06-06 | Copilot SDK | — → 1.0.0 | 🆕 新增 Copilot Agent SDK |
| 2026-06-06 | trivy | — → 0.71.0 | 🆕 新增安全扫描器 |
| 2026-06-04 | yt-dlp | 2024.4.9 → 2026.3.17 | 24+ 版本跨越，修复大量网站适配 |
| 2026-06-04 | scrapling | 0.4.7 → 0.4.8 | 反检测引擎更新 |

## 升级方法

### Python 包

```bash
# 进入 Hermes venv
source ~/.hermes/hermes-agent/.venv/bin/activate

# 升级单个包
pip install --upgrade yt-dlp scrapling

# 批量升级所有 KMM 相关包
pip install --upgrade yt-dlp scrapling crawl4ai easyocr openai \
  beautifulsoup4 markdownify pillow opencv-python trafilatura
```

### 系统工具

```bash
# ffmpeg / tesseract
sudo apt update && sudo apt upgrade ffmpeg tesseract-ocr

# rclone
sudo rclone selfupdate

# yt-dlp CLI 包装自动跟随 venv 版本
# 无需单独管理
```

## 版本检测命令

```bash
# Python 包
pip list | grep -iE "yt-dlp|scrapling|crawl4ai"

# 系统工具
yt-dlp --version
ffmpeg -version | head -1
tesseract --version | head -1
rclone version | head -1
```
