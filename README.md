# Knowledge and Memory Management （测试版稳定性还有待改进） 

知识和记忆体管理插件 — 为已安装 [Hermes Memory Installer](https://github.com/mage0535/hermes-memory-installer)（或兼容记忆体系统）的 AI Agent 添加**知识采集、笔记/RAG 管理、云盘同步**能力。

> ## 两层关系
>
> | 项目 | 定位 | 功能 |
> |------|------|------|
> | **[hermes-memory-installer](https://github.com/mage0535/hermes-memory-installer)** | 记忆体底座 | Hot/Warm/Cold 三层记忆 + Hindsight + gbrain + 会话持久化 |
> | **本插件** | 能力扩展层 | 知识采集（网页/视频/文章）+ 笔记/RAG + 云盘同步 |
>
> **记忆体底座**解决"记住"的问题，**本插件**解决"知识从哪来、存到哪去"的问题。

---

## 适用场景

你已安装了 [Hermes Memory Installer](https://github.com/mage0535/hermes-memory-installer)（或等效的记忆体系统），现在想进一步：

- ✅ **知识采集** — 从网页、视频、文章、社交媒体自动采集知识，采集即入库
- ✅ **笔记/RAG 管理** — 结构化笔记 + 三级知识域（个人/共享/归档）+ gbrain 自动索引
- ✅ **云盘同步** — 笔记和知识库自动同步到 OneDrive / Google Drive / 阿里云盘等 12+ 云盘
- ✅ **关键词分析扩展** — 自动提取、交叉验证、扩展关联知识
- ✅ **笔记自动生成** — 从原始材料（网页/视频/文章）经 AI 提炼为结构化笔记

## 架构

```
  AI Agent（你的 Hermes / Claude Code / Cursor 等）
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  🔌 本插件：Knowledge and Memory Management              │
│                                                          │
│  ┌──────────────────┐  ┌─────────────┐  ┌──────────┐   │
│  │  知识采集         │  │ 笔记/RAG     │  │ 云盘同步  │   │
│  │  web/video/文章   │  │ 三级知识域   │  │ rclone   │   │
│  │  分析/笔记生成    │  │ gbrain 索引  │  │ 12+ 云盘 │   │
│  └──────────────────┘  └─────────────┘  └──────────┘   │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  记忆体底座：hermes-memory-installer                      │
│  Hot(memory) → Warm(Hindsight) → Cold(gbrain + FTS5)    │
└──────────────────────────────────────────────────────────┘
```

## 快速安装

```bash
# 前提：已安装记忆体底座
git clone https://github.com/mage0535/Knowledge-and-Memory-Management.git
cd Knowledge-and-Memory-Management
chmod +x install.sh
./install.sh
```

安装过程：
1. ✅ 检测记忆体底座（gbrain + Hindsight）是否就绪
2. ✅ 检测运行环境（Python / rclone / ffmpeg / tesseract）
3. ✅ 创建知识库目录结构
4. ✅ 部署知识采集模块（网页/视频/文章/分析/笔记生成）
5. ✅ 部署笔记/RAG 管理模块
6. ✅ 部署云盘同步引擎
7. ✅ 可选：交互式配置云盘
8. ✅ 注册定时同步（每 30 分钟笔记 → 云盘）

### 验证

```bash
./scripts/verify_plugin.sh
```

### 卸载

```bash
./uninstall.sh
```

## 功能模块

### 知识采集 (src/knowledge_collector/)

**30+ 采集分析工具全集：**

| 模块 | 工具数量 | 核心工具 |
|------|----------|----------|
| **网页采集** | 9 | Scrapling(stealthy/dynamic/http) / Chrome DevTools / GStack Browser / Crawl4AI / knowledge_fetch_router / knowledge_site_crawler / web_extract / obscura_fetch_bridge / opensquilla_bridge |
| **视频采集** | 10 | douyin_video_intake / social_video_intake / universal-video-analyzer / yt-dlp / Whisper ASR / EasyOCR / FFmpeg / Tesseract / YouTube Analytics / 抖音热榜 |
| **文章/内容** | 10 | 微信公众文章 / 微博 / 新闻聚合(多源) / tech-news / AI中文日报 / blogwatcher / GitHub Trending / 通用网络文档 / 多格式文档解析 |
| **文档/OCR** | 5 | umi_ocr_bridge / doc_parse_router / Magic-PDF / MinerU / book_cache_manager(710+书) |
| **知识分析** | 7 | web_search(多后端) / web_extract / NLI事实核查 / 评论摘要 / 新闻丰富 / 关键词提取 / 多源交叉验证 |
| **笔记生成** | 全链路 | LLM结构化 → 本地笔记 → gbrain知识图谱 → 云盘同步 |
| **知识图谱** | 8 MCP | gbrain_put_page / gbrain_query / gbrain_add_link / gbrain_add_tag / gbrain_traverse_graph / gbrain_file_upload / gbrain-link-orphans |
| **采集编排** | 统一调度 | 多源并行/去重/避撞/定时同步 |

### 笔记/RAG (src/notes_rag/)

- **三级知识域**：个人(personal) → 共享(shared) → 归档(archive)
- **自动索引**：笔记创建即进入 gbrain，自动链接关联节点
- **混合检索**：语义搜索 + 关键词 + 图遍历

### 云盘同步 (src/cloud_sync/)

基于 **rclone** 统一驱动的 12+ 云盘：

| 云盘 | 配置方式 | 推荐用途 |
|------|----------|----------|
| OneDrive | OAuth ✅ | 笔记主存储 |
| Google Drive | OAuth | 备份/共享 |
| 阿里云盘 | Token | 文件存储 |
| 百度云盘 | OAuth | 存档 |
| 坚果云 | WebDAV ✓ | 轻量同步 |
| Dropbox | OAuth | 国际协作 |
| Mega | 账号密码 | 加密存储 |
| Nextcloud | WebDAV ✓ | 自建私有云 |
| iCloud Drive | OAuth+2FA | Apple 生态 |
| 天翼云盘 | 账号密码 | 国内备份 |
| 115 网盘 | Cookie | 离线下载 |
| 夸克网盘 | WebDAV(桥接) | 大文件 |

## 项目结构

```
├── install.sh                    ← 一键安装入口
├── uninstall.sh                  ← 干净卸载
├── plugin.yaml                   ← 插件元数据
├── AGENTS.md                     ← AI Agent 接入指南
├── requirements.txt              ← Python 依赖
├── docs/
│   ├── quick-start.md            ← 5 分钟上手
│   ├── cloud-sync.md             ← 云盘配置完整指南
│   └── collection-pipeline.md    ← 采集管线配置
├── src/
│   ├── knowledge_collector/      ← 知识采集
│   │   ├── web.py
│   │   ├── video.py
│   │   ├── article.py
│   │   ├── analysis.py
│   │   └── note_generator.py
│   ├── notes_rag/                ← 笔记/RAG 管理
│   └── cloud_sync/               ← 云盘同步引擎
├── scripts/
│   ├── verify_plugin.sh          ← 安装验证
│   └── install_rclone_drives.sh  ← 云盘一键配置
├── config/
│   ├── storage-policy.yaml       ← 存储策略模板
│   └── collection-schedule.yaml  ← 采集调度模板
└── tests/
```

## 内存与磁盘占用（预估）

| 组件 | 占用 |
|------|------|
| Python 模块（源码） | < 1MB |
| 笔记目录（初始） | ~100KB |
| 知识采集缓存 | 按需（可配置上限） |
| 定时同步 | 无驻留进程 |

## 许可证

MIT
