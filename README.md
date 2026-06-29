# Knowledge and Memory Management（知识和记忆体管理）

超越「记住」——**知识采集 → 笔记生成 → 语义检索 → 云盘同步** 全链路插件扩展。

> 📦 **定位**：[hermes-memory-installer](https://github.com/mage0535/hermes-memory-installer) 的能力扩展层。
> 底座解决「记住」，KMM 解决「知识从哪来、如何用」。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![yt-dlp 2026.3](https://img.shields.io/badge/yt--dlp-2026.3-green)](https://github.com/yt-dlp/yt-dlp)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://github.com/mage0535/Knowledge-and-Memory-Management/pulls)

[**English**](README_EN.md) | [**采集管线**](docs/collection-pipeline.md)

---

## 架构总览

```
采集层（40+ 工具）  →  分析层（AI 处理）  →  存储层（三层记忆）
   │                        │                       │
   ├─ 网页引擎(9)           ├─ 笔记自动生成        ├─ Hot(Memory tool)
   ├─ 视频引擎(12)          ├─ 知识图谱提取        ├─ Warm(Hindsight, 10K节点)
   ├─ 文章/内容(10)         ├─ NLI 事实核查        └─ Cold(gbrain, 11K页)
   ├─ 文档/OCR(10)          ├─ 知识发现与召回
   ├─ 知识检索/分析(7)      └─ 书籍自动精炼
   └─ 知识管理(4)
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
| **知识采集器** | `src/knowledge_collector/` | 9 个子模块覆盖网页/视频/文章/文档/分析/笔记生成/知识精炼/知识管理 |
| **笔记 RAG** | `src/notes_rag/` | 语义搜索、向量检索、三层上下文召回 |
| **云盘同步** | `src/cloud_sync/` | rclone 统一驱动，12+ 云盘双向同步 |
| **文档采集** | `src/knowledge_collector/document.py` | MarkItDown 统一文档转换 + KMM 文档采集包装 |
| **知识增广** | `src/knowledge_augmentation/` | 本地笔记优先 + AnySearch 全网回落 |
| **采集管线** | `docs/collection-pipeline.md` | **40+ 工具**详细说明和链路图 |
| **工具版本** | `docs/tool-versions.md` | 已验证工具链版本表 |
| **快速开始** | `docs/quick-start.md` | 安装和第一个采集 |

---

## 40+ 采集分析工具全集

### 🌐 网页采集（9 引擎）

| 工具 | 类型 | 能力 | 适用场景 |
|------|------|------|----------|
| **Scrapling** | MCP | ⭐⭐⭐⭐⭐ | 反检测采集，Cloudflare 绕过，stealthy/dynamic/http 三模式 |
| **Chrome DevTools** | MCP | ⭐⭐⭐⭐⭐ | 浏览器自动化，JS 执行，网络分析，性能追踪 |
| **GStack Browser** | 内置 | ⭐⭐⭐⭐⭐ | Hermes 内置浏览器 + 视觉分析 |
| **knowledge_fetch_router** | 脚本 | ⭐⭐⭐⭐ | 智能路由（trafilatura→readability→Crawl4AI） |
| **knowledge_site_crawler** | 脚本 | ⭐⭐⭐⭐ | Crawlee 同域名批量爬取 |
| **obscura_fetch_bridge** | 桥接 | ⭐⭐⭐ | 动态网页 Markdown 提取 |
| **opensquilla_bridge** | 桥接 | ⭐⭐⭐ | 轻量侧车采集 |
| **web_extract** | 内置 | ⭐⭐ | 纯 HTTP 内容提取 |
| **ripgrep_kb_scan** | 脚本 | ⭐⭐ | 知识库预筛去重 |

### 🎬 视频采集（12 工具）

| 工具 | 类型 | 能力 | 适用场景 |
|------|------|------|----------|
| **douyin_video_intake** | 脚本 | ⭐⭐⭐⭐⭐ | 抖音元数据+字幕+ASR |
| **douyin_batch_transcriber** | 脚本 | ⭐⭐⭐⭐⭐ | 抖音批量多视频并发转录 |
| **social_video_intake** | 脚本 | ⭐⭐⭐⭐⭐ | 通用社交视频统一入口 |
| **universal-video-analyzer** | Skill | ⭐⭐⭐⭐⭐ | 多语言OCR/人脸/质量/BGM/情感 |
| **media_transcriber_wrapper** | 脚本 | ⭐⭐⭐⭐ | 通用媒体转录包装器 |
| **yt-dlp** | CLI | ⭐⭐⭐⭐ | 1000+网站视频下载 |
| **Whisper ASR** | 引擎 | ⭐⭐⭐⭐ | 99+语言语音转文字 |
| **EasyOCR** | 引擎 | ⭐⭐⭐ | 视频关键帧文字提取 |
| **PaddleOCR** | 引擎 | ⭐⭐⭐⭐ | 70k⭐ 高精度 OCR |
| **FFmpeg** | CLI | ⭐⭐⭐ | 视频切分/转码/音频提取 |
| **Tesseract OCR** | CLI | ⭐⭐⭐ | 开源 OCR（中文支持） |
| **YouTube Analytics** | Skill | ⭐⭐⭐⭐ | 频道/视频数据分析 |

### 📄 文档/OCR（10 工具）—— MarkItDown + SenseNova 兼容

| 工具 | 能力 | 说明 |
|------|------|------|
| **MarkItDown** | ⭐⭐⭐⭐⭐ | 统一转换 PDF / Office / HTML / CSV / JSON / XML / 图片 / 邮件等公开格式 |
| **SenseNova PDF 分析** | ⭐⭐⭐⭐⭐ | 文字型+扫描型 PDF，表格/图表/多页全量提取 |
| **SenseNova PPT 分析** | ⭐⭐⭐⭐⭐ | 全 Slide 文本/表格/图表/嵌入图片提取 |
| **SenseNova Word 分析** | ⭐⭐⭐⭐⭐ | 正文/表格/高亮/格式/多文档对比 |
| **umi_ocr_bridge** | ⭐⭐⭐⭐ | 中文 OCR 增强桥接 |
| **doc_parse_router** | ⭐⭐⭐⭐ | 多格式路由（PDF/HTML/MD/Office） |
| **Magic-PDF** | ⭐⭐⭐⭐ | PDF → Markdown 转换 |
| **MinerU** | ⭐⭐⭐⭐ | 文档内容智能提取 |
| **PaddleOCR** | ⭐⭐⭐⭐ | 70k⭐ 百度开源高精度 OCR |
| **book_cache_manager** | ⭐⭐⭐⭐ | 710+书索引+按需缓存+自动精炼 |

### 📝 文章/内容（10 来源）

微信公众号 / 微博 / 新闻聚合 / 科技新闻 / AI 中文日报 / RSS/博客 / GitHub 热门 / 通用网络文档 / 多格式文档解析

### 🔬 知识分析（7 工具）

web_search / web_extract / NLI 事实核查 / 评论摘要 / 新闻丰富 / 关键词提取 / 交叉验证

### 🧠 知识管理（4 工具）—— 全新

| 工具 | 能力 | 说明 |
|------|------|------|
| **knowledge_discovery** | ⭐⭐⭐⭐⭐ | 每周日自动扫描 OneDrive→本地→gbrain 录入 |
| **lightweight_recall** | ⭐⭐⭐⭐⭐ | 三层跨层召回（FTS5 + Hindsight语义 + gbrain关键词） |
| **onedrive_bidirectional_sync** | ⭐⭐⭐⭐⭐ | OneDrive 双向增量同步（每4小时） |
| **nightly_maintenance** | ⭐⭐⭐⭐⭐ | 凌晨维护母脚本（含知识发现+孤页链接+compact） |

### 📚 知识精炼（6 工具）

| 工具 | 能力 | 说明 |
|------|------|------|
| **book_to_skill 管线** | ⭐⭐⭐⭐⭐ | PDF/EPUB → 结构化 Skill + KMM 笔记 |
| **pdfplumber 引擎** | ⭐⭐⭐⭐ | 表格保留提取（技术书首选） |
| **pdftotext 引擎** | ⭐⭐⭐⭐ | 快速文本提取 |
| **双引擎降级链** | ⭐⭐⭐⭐ | pdfplumber→pdftotext→pdfminer 自动降级 |
| **章节自动分割** | ⭐⭐⭐⭐ | 三层分割策略 |
| **自动触发管线** | ⭐⭐⭐⭐⭐ | `book_cache_manager` 下载后自动精炼 |

---

## 快速安装

```bash
# 可选：如已安装 hermes-memory-installer，可先指向 agent home
export AGENT_HOME="${AGENT_HOME:-$HOME/.hermes}"

# 克隆仓库
git clone https://github.com/mage0535/Knowledge-and-Memory-Management.git
cd Knowledge-and-Memory-Management

# 运行安装程序
bash install.sh
```

安装程序自动完成：
1. 检测 Agent 环境（`AGENT_HOME` / `HERMES_HOME`、gbrain、Hindsight）
2. 安装/升级 Python 依赖（yt-dlp、scrapling、paddleocr 等）
3. 检测系统工具（ffmpeg、tesseract、rclone）
4. 配置云盘双向同步规则
5. 注册定时知识采集 cron 任务
6. 配置知识发现自动管线

---

## 使用指南

### 1. 快速采集

```bash
# 采集网页，自动提取重点并生成笔记
python3 -c "
from knowledge_collector import collect_web
result = collect_web('https://example.com/article')
print(f'笔记已生成: {result.note_path}')
print(f'gbrain 页面: {result.gbrain_slug}')
"

# 采集视频（自动字幕+OCR+ASR）
python3 -c "
from knowledge_collector import collect_video
result = collect_video('https://www.youtube.com/watch?v=xxx')
print(f'字幕已提取: {len(result.subtitles)} 条')
print(f'关键帧截图: {result.frames}')
"

# 采集微信公众号文章
python3 $AGENT_HOME/scripts/network_doc_intake.py "https://mp.weixin.qq.com/s/xxx"
```

### 2. 文档智能分析

```bash
# MarkItDown 统一文档采集（推荐）
python3 -m knowledge_collector.document report.pdf
python3 -m knowledge_collector.document --batch ./docs/ --progress

# SenseNova PDF 分析 — 如服务器环境提供对应脚本
python3 $AGENT_HOME/scripts/sensenova_dispatcher.py pdf report.pdf

# SenseNova PPT 分析 — 全Slide提取
python3 $AGENT_HOME/scripts/sensenova_dispatcher.py ppt presentation.pptx

# SenseNova Word 分析 — 正文+表格+格式
python3 $AGENT_HOME/scripts/sensenova_dispatcher.py word document.docx
```

### 3. 书籍自动精炼

```bash
# 方式一：手动触发
python3 $AGENT_HOME/scripts/book_to_skill.py all book.pdf --name machine-learning

# 方式二：通过缓存管理器（自动触发精炼）
python3 $AGENT_HOME/scripts/book_cache_manager.py cache book.pdf
# → 自动触发 book_to_skill.py all → Skill + KMM 笔记
```

### 4. 知识检索

```bash
# 三层召回（FTS5 + Hindsight + gbrain）
python3 $AGENT_HOME/scripts/lightweight_recall.py --query "Agent 记忆系统设计" --limit 10

# gbrain 语义搜索
gbrain search "知识图谱构建" --limit 5

# 笔记全文搜索
python3 $AGENT_HOME/scripts/ripgrep_kb_scan.py "深度学习"
```

### 5. 知识发现（自动化）

每周日凌晨自动执行，也可手动触发：

```bash
# 扫描本地笔记 → 自动录入 gbrain
python3 $AGENT_HOME/scripts/knowledge_discovery.py
```

### 6. 云盘双向同步

```bash
# 自动（每4小时 cron）
# 手动：
bash $AGENT_HOME/scripts/onedrive_bidirectional_sync.sh
```

---

## 知识增广（Knowledge Augmentation）

**当本地笔记不够用，自动走 AnySearch 垂直搜索补全。**

```
用户搜索 → search_notes("比亚迪 2026Q1 财报")
    │
    ├─ 本地命中 (score ≥ 0.6) → 直接返回笔记结果
    │
    └─ 本地不足 (score < 0.6) → AnySearch 垂直搜索
         ├─ domain=finance (财务数据)
         ├─ domain=academic (论文)
         └─ 结果自动标注来源 web，可导入笔记库
```

```bash
# 安装后即可使用
export ANYSEARCH_API_KEY="as_sk_xxxx"
python -c "
from knowledge_augmentation import AugmentedSearch
s = AugmentedSearch()
r = s.search('中国 2026 年 GDP 预测', domain='finance')
print(r['source'], '-', len(r['results']), '条结果')
"
```

---

## 云盘同步

支持 12+ 云盘驱动，全部通过 rclone 统一接口：

| 云盘 | 认证方式 | 同步模式 |
|------|----------|----------|
| OneDrive | OAuth | 双向增量（每4h） |
| Google Drive | OAuth | 单向 + 按需 |
| 阿里云盘 | Token | 单向备份 |
| 百度网盘 | OAuth | 单向备份 |
| Dropbox / Mega / pCloud / 天翼云 / 123云盘 / S3 / WebDAV | 按 rclone 标准 | 可配置 |

---

## 采集编排

采集不是孤立的——它与记忆体、知识图谱、笔记、云盘形成闭环：

```
采集 → 处理 → 笔记 → gbrain 知识图谱 → 云盘双向同步
  │                                              │
  └──────────── 下次采集先去重 ────────────────┘
```

### 自动化调度（10 cron 体系）

| 调度 | 模块 | 频率 |
|------|------|------|
| 凌晨维护(含知识发现) | nightly_maintenance.py | 每日 03:30 |
| OneDrive 双向同步 | onedrive_bidirectional_sync.sh | 每 4 小时 |
| 知识图谱孤页修复 | gbrain_link_orphans.py | 每日 03:30 |
| 书籍缓存清理 | book_cache_cleanup.sh | 每周日 03:30 |
| 知识图谱压缩 | gbrain_compact.py | 每周日 03:30 |
| 渠道内容总管线 | channel_publish.sh | 每日 13 次 |

### Skill 链路

```
knowledge-intake-collector
  → knowledge-carrier-extraction
    → knowledge-refinery-graph-ingest
      → 笔记成品 + gbrain 节点 + 云盘双向同步

knowledge-discovery（自动化）
  → OneDrive 扫描 → 本地匹配 → gbrain 自动录入
```

---

## API 接口

### knowledge_collector

| 函数 | 功能 |
|------|------|
| `collect_web(url)` | 采集网页内容并入库 |
| `collect_video(url)` | 采集视频内容（OCR+ASR） |
| `collect_article(source, keyword)` | 采集文章内容 |
| `generate_note(material, template)` | 生成结构化笔记 |

### notes_rag

| 函数 | 功能 |
|------|------|
| `create_note(title, content, domain)` | 创建笔记 |
| `search_notes(query, domains)` | 跨域检索（三层召回） |
| `sync_notes_to_cloud()` | 同步笔记到云盘 |

### cloud_sync

| 函数 | 功能 |
|------|------|
| `list_cloud_drives()` | 列出已配置云盘 |
| `sync_to_cloud(local, remote)` | 本地→云盘 |
| `sync_from_cloud(remote, local)` | 云盘→本地 |

### knowledge_augmentation

| 函数 | 功能 |
|------|------|
| `augmented_search(query, domain)` | 本地优先 + AnySearch 回落 |
| `augmented_search.list_domains()` | 查询 AnySearch 全部垂直领域 |

---

## 更新日志

### 2026-06-16

- **统一公开基线**：本地、GitHub、服务器仓库收敛到同一公开 KMM 代码树
- **MarkItDown 文档采集**：公开仓库内置统一文档转换能力
- **知识管理模块**：自动发现 + 三层召回 + 双向云同步
- **视频采集扩展**：douyin_batch_transcriber + media_transcriber_wrapper
- **10 cron 精简体系**：34→10，凌晨维护母脚本统管所有维护任务
- **知识精炼自动触发**：`book_cache_manager` 下载后自动走精炼管线

### 2026-06-07

- **知识增广模块**：AnySearch 垂直搜索集成，本地笔记优先+全网回落
- 新增 `src/knowledge_augmentation/` 目录

### 2026-06-06

- **方法论蒸馏管线**：cron 每日自动从 Horizon trending 知识蒸馏
- **4 个外部工具集成**：PaddleOCR / Trivy / Spec-Kit / Copilot-SDK

### 2026-06-05

- **知识精炼管线**：book_cache_manager 缓存后自动分析提取结构化知识

### 2026-06-04

- 初始发布 — 知识采集、笔记 RAG、云盘同步全链路
- 30+ 采集分析工具全景
- rclone 12+ 云盘驱动统一接口

---

## 许可证

MIT License © 2026

---

## 相关项目

- **[hermes-memory-installer](https://github.com/mage0535/hermes-memory-installer)** — 记忆体底座。gbrain + Hindsight + 三层召回。agent-agnostic 外挂记忆系统，负责「记住」。KMM 在其上扩展知识能力。
- [hermes-agent](https://github.com/nousresearch/hermes-agent) — Hermes Agent 框架
- [gbrain](https://github.com/nousresearch/gbrain) — 知识图谱引擎
- [book-to-skill](https://github.com/virgiliojr94/book-to-skill) — 知识结构化理念（借鉴来源）
