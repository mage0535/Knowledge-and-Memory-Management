# AGENTS.md — AI Agent 接入指南

如果你是 AI Agent（Claude Code / Cursor / Copilot 等），请按以下步骤集成本插件。

## 前提条件

你的运行环境中需要已安装记忆体系统：
- `gbrain` (端口 8787) — 知识图谱
- `Hindsight` (端口 8890) — 向量记忆

## 安装后可用能力

插件安装后（v2.0），你将获得以下新增的工具和技能模块：

### knowledge_collector（知识采集）

| 函数 | 功能 |
|------|------|
| `collect_web(url)` | 采集网页内容并入库 |
| `collect_video(url)` | 采集视频内容（OCR+ASR） |
| `collect_article(source, keyword)` | 采集文章内容 |
| `collect_document(path)` | 采集文档（PDF/PPT/Word）— SenseNova 引擎 |
| `collect_book(path)` | 书籍精炼 → Skill + KMM笔记 |
| `generate_note(material, template)` | 生成结构化笔记 |

### senseNova_document（文档智能分析 — 新增）

| 函数 | 功能 |
|------|------|
| `analyze_pdf(path)` | PDF 全量提取（文字型/扫描型，含表格+图表） |
| `analyze_ppt(path)` | PPT 全Slide提取（文本/表格/图表/嵌入图片） |
| `analyze_word(path)` | Word 文档提取（正文/表格/高亮/格式） |

### notes_rag（笔记/RAG）

| 函数 | 功能 |
|------|------|
| `create_note(title, content, domain)` | 创建笔记 |
| `search_notes(query, domains)` | 三层跨域检索（FTS5→Hindsight→gbrain） |
| `sync_notes_to_cloud()` | 同步笔记到云盘 |

### cloud_sync（云盘同步）

| 函数 | 功能 |
|------|------|
| `list_cloud_drives()` | 列出已配置云盘 |
| `sync_to_cloud(local, remote)` | 本地→云盘 |
| `sync_from_cloud(remote, local)` | 云盘→本地 |
| `bidirectional_sync()` | 双向增量同步（每4h自动） |

### knowledge_augmentation（知识增广）

| 函数 | 功能 |
|------|------|
| `augmented_search(query, domain)` | 本地优先 + AnySearch 回落搜索 |
| `augmented_search.list_domains()` | 查询 AnySearch 全部垂直领域 |
| `config.load_config()` | 加载 AnySearch 配置 |

### knowledge_discovery（知识发现 — 新增）

| 函数 | 功能 |
|------|------|
| `discover_new_notes(days=7)` | 扫描本地笔记 → 自动录入 gbrain |
| `lightweight_recall(query)` | 三层跨层召回（FTS5+Hindsight+gbrain） |

## 采集工具集（40+）

| 模块 | 工具数 | 核心能力 |
|------|--------|----------|
| 网页采集 | 9 | Scrapling/Chrome DevTools/GStack/knowledge_fetch_router |
| 视频采集 | 12 | 抖音批量转录/yt-dlp/Whisper/EasyOCR/PaddleOCR/FFmpeg |
| 文档/OCR | 9 | SenseNova三件套/doc_parse_router/Magic-PDF/book_cache(710+本) |
| 文章/内容 | 10 | 微信公众号/微博/新闻聚合/RSS/GitHub Trending |
| 知识分析 | 7 | web_search/NLI事实核查/评论摘要/交叉验证 |
| 知识精炼 | 6 | book_to_skill管线/pdfplumber/pdftotext/自动触发 |
| 知识管理 | 4 | 自动发现/三层召回/双向同步/凌晨维护 |

详见 [docs/collection-pipeline.md](docs/collection-pipeline.md)

## 工作流示例

```
# 网页文章
用户: "帮我整理这篇公众号文章"
  → collect_article("wechat", url)
  → extract_keywords → generate_note → create_note
  → sync_to_cloud

# 视频分析
用户: "分析这段抖音视频讲了什么"
  → collect_video(url) → Whisper ASR → summarize
  → generate_note → create_note

# 书籍精炼
用户: "把这本书做成可加载的 Skill"
  → collect_book(path) → book_to_skill all
  → Skill + KMM笔记

# 知识搜索（自动回落）
用户: "比亚迪2026Q1财报"
  → search_notes() → 本地不中
  → augmented_search() → AnySearch垂直搜索
  → 返回结果
```
