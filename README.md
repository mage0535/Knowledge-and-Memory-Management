# Knowledge and Memory Management（知识和记忆体管理）

超越「记住」——**知识采集 → 笔记生成 → 语义检索 → 云盘同步** 全链路插件扩展。

> 📦 **定位**：[hermes-memory-installer](https://github.com/mage0535/hermes-memory-installer) 的能力扩展层。
> 底座解决「记住」，KMM 解决「知识从哪来、如何用」。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![yt-dlp 2026.3](https://img.shields.io/badge/yt--dlp-2026.3-green)](https://github.com/yt-dlp/yt-dlp)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://github.com/mage0535/Knowledge-and-Memory-Management/pulls)

---

## 架构总览

```
采集层（35+ 工具）  →  分析层（AI 处理）  →  存储层（三层记忆）
   │                        │                       │
   ├─ 网页引擎(9)           ├─ 笔记自动生成        ├─ Hot(Memory)
   ├─ 视频引擎(11)          ├─ 知识图谱提取        ├─ Warm(Hindsight)
   ├─ 文章/内容(10)         ├─ NLI 事实核查        └─ Cold(gbrain)
   ├─ 文档/OCR(6)           └─ 多模态分析
   ├─ 安全审计(1)
   └─ 知识检索/分析(7)
                                            ┌─ OneDrive / Google Drive
                                            ├─ 阿里云盘 / 百度网盘
              云盘同步层（rclone, 12+ 驱动）──┼─ Dropbox / Mega / pCloud
                                            ├─ WebDAV / S3 / 天翼云
                                            └─ 更多 rclone 支持的所有驱动
```

---

## 模块组成

| 模块 | 目录 | 功能 |
|------|------|------|
| **知识采集器** | `src/knowledge_collector/` | 8 个子模块覆盖网页/视频/文章/文档/分析/笔记生成/知识精炼 |
| **笔记 RAG** | `src/notes_rag/` | 语义搜索、向量检索、上下文召回 |
| **云盘同步** | `src/cloud_sync/` | rclone 统一驱动，12+ 云盘 |
| **采集管线** | `docs/collection-pipeline.md` | 详细工具说明和链路图（含知识精炼） |
| **工具版本** | `docs/tool-versions.md` | 已验证工具链版本表 |
| **快速开始** | `docs/quick-start.md` | 安装和第一个采集 |

---

## 30+ 采集分析工具全集

| 模块 | 工具数量 | 核心工具 |
|------|----------|----------|
| **网页采集** | 9 | Scrapling(stealthy/dynamic/http) / Chrome DevTools / GStack Browser / Crawl4AI / knowledge_fetch_router / knowledge_site_crawler / web_extract / obscura_fetch_bridge / opensquilla_bridge |
| **视频采集** | 10 | douyin_video_intake / social_video_intake / universal-video-analyzer / yt-dlp / Whisper ASR / EasyOCR / **PaddleOCR** / FFmpeg / Tesseract / YouTube Analytics / 抖音热榜 |
| **文章/内容** | 10 | 微信公众文章 / 微博 / 新闻聚合(多源) / tech-news / AI中文日报 / blogwatcher / GitHub Trending / 通用网络文档 / 多格式文档解析 |
| **文档/OCR** | 6 | umi_ocr_bridge / doc_parse_router / Magic-PDF / MinerU / book_cache_manager(710+书) / **PaddleOCR**(70k⭐高精度OCR) |
| **知识分析** | 7 | web_search / web_extract / NLI 事实核查 / 评论摘要 / 新闻丰富 / 关键词提取 / 交叉验证 |
| **SDD 开发** | 1 | **Spec-Kit**(Spec-Driven Development 7步工作流) / **Copilot-SDK**(GitHub Copilot Agent集成) |
| **安全审计** | 1 | **trivy**(文件/镜像/仓库安全扫描) |

> 2026-06-06 新增: PaddleOCR(v3.6.0, 70k⭐) 高精度OCR引擎; Trivy(v0.71.0, 24k⭐) 安全扫描器; Spec-Kit 规范驱动开发; Copilot-SDK(v1.0.0, 9.2k⭐) Agent SDK。详见 Hermes tool_manifest.yaml external_tools_2026_06_06 节。

> 详细工具调用链路见 [采集管线](docs/collection-pipeline.md)。

---

## 快速安装

```bash
# 要求：已安装 hermes-memory-installer
# 确保 Hermes 虚拟环境激活
source ~/.hermes/hermes-agent/.venv/bin/activate

# 克隆仓库
git clone https://github.com/mage0535/Knowledge-and-Memory-Management.git
cd Knowledge-and-Memory-Management

# 运行安装程序
bash install.sh
```

安装程序会：
1. 检测 Hermes 环境（venv、gbrain、Hindsight）
2. 安装/升级 Python 依赖（yt-dlp、scrapling 等）
3. 检测系统工具（ffmpeg、tesseract、rclone）
4. 配置云盘同步规则
5. 注册定时知识采集 cron 任务

---

## 云盘同步

支持 12+ 云盘驱动，全部通过 rclone 统一接口：

| 云盘 | 认证方式 | 配置 |
|------|----------|------|
| OneDrive | OAuth | `rclone config` |
| Google Drive | OAuth | `rclone config` |
| 阿里云盘 | Token | `rclone config` |
| 百度网盘 | OAuth | `rclone config` |
| Dropbox | OAuth | `rclone config` |
| Mega | Password | `rclone config` |
| pCloud | OAuth | `rclone config` |
| 天翼云 | Cookie | `rclone config` |
| 123云盘 | Password | `rclone config` |
| S3 | Access Key | `rclone config` |
| WebDAV | Password | `rclone config` |
| 更多 | 详见 rclone 文档 | `rclone config` |

---

## 许可证

MIT License © 2026

---

## 相关项目

- [hermes-memory-installer](https://github.com/mage0535/hermes-memory-installer) — Hermes 三层记忆体安装器（底座）
