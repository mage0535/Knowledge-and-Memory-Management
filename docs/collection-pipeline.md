# 知识采集管线 — 全工具清单

## 总览

本插件集成了 Hermes Agent 环境中 **30+ 采集和分析工具**，按源类型分为 8 大模块。

## 1. 网页采集（6 种引擎）

| # | 工具 | 类型 | 能力等级 | 适用场景 |
|---|------|------|----------|----------|
| 1 | **Scrapling** | MCP | ⭐⭐⭐⭐⭐ | 反检测采集，Cloudflare绕过，3种模式(stealthy/dynamic/http) |
| 2 | **Chrome DevTools** | MCP | ⭐⭐⭐⭐⭐ | 完整浏览器自动化，JS执行，网络分析，性能追踪 |
| 3 | **GStack Browser** | 内置 | ⭐⭐⭐⭐⭐ | Hermes内置浏览器，截图+视觉分析+AI驱动交互 |
| 4 | **knowledge_fetch_router** | 脚本 | ⭐⭐⭐⭐ | 智能路由：trafilatura→readability→Crawl4AI→YouTube字幕 |
| 5 | **knowledge_site_crawler** | 脚本 | ⭐⭐⭐⭐ | Crawlee 同域名批量爬虫 |
| 6 | **obscura_fetch_bridge** | 桥接 | ⭐⭐⭐ | 动态网页Markdown提取 |
| 7 | **opensquilla_bridge** | 桥接 | ⭐⭐⭐ | 低Token轻量侧车采集 |
| 8 | **web_extract** | 内置 | ⭐⭐ | 纯HTTP内容提取（最简单的页面首选） |
| 9 | **ripgrep_kb_scan** | 脚本 | ⭐⭐ | 知识库预筛去重 |

**采集策略（自动降级）：**

```
简单页面 → web_extract → knowledge_fetch_router → scrapling_http
动态页面 → scrapling_dynamic → chrome_devtools → gstack_browser
反爬页面 → scrapling_stealthy → chrome_devtools
批量采集 → knowledge_site_crawler → scrapling_bulk
```

## 2. 视频采集（8 种引擎/工具）

| # | 工具 | 类型 | 能力等级 | 适用场景 |
|---|------|------|----------|----------|
| 1 | **douyin_video_intake** | 脚本 | ⭐⭐⭐⭐⭐ | 抖音视频元数据+字幕+ASR |
| 2 | **social_video_intake** | 脚本 | ⭐⭐⭐⭐⭐ | 通用社交视频统一入口 |
| 3 | **universal-video-analyzer** | 技能 | ⭐⭐⭐⭐⭐ | 多语言OCR/人脸/质量/BGM/情感分析 |
| 4 | **yt-dlp** | CLI | ⭐⭐⭐⭐ | 视频/音频下载（YouTube/抖音/B站等数千网站）目前版本 **2026.3.17** |
| 5 | **Whisper ASR** | 引擎 | ⭐⭐⭐⭐ | 99+语言语音转文字 |
| 6 | **EasyOCR** | 引擎 | ⭐⭐⭐ | 视频关键帧画面文字提取 |
| 7 | **FFmpeg** | CLI | ⭐⭐⭐ | 视频切分/截图/转码/音频提取 |
| 8 | **Tesseract OCR** | CLI | ⭐⭐⭐ | 开源OCR（中文chi_sim） |
| 9 | **youtube-analytics** | 技能 | ⭐⭐⭐⭐ | YouTube 频道/视频数据分析 |
| 10 | **douyin-hot** | 技能 | ⭐⭐⭐ | 抖音热榜/热搜采集 |

## 3. 文章/内容采集（10+ 来源）

| # | 来源 | 工具 | 能力等级 |
|---|------|------|----------|
| 1 | **微信公众号** | wechat-article-fetcher | ⭐⭐⭐⭐⭐ |
| 2 | **微信搜一搜** | wechat-article-search | ⭐⭐⭐⭐ |
| 3 | **微信图文摄入** | wechat_text_intake.py | ⭐⭐⭐⭐ |
| 4 | **微博** | weibo-skill | ⭐⭐⭐⭐⭐ |
| 5 | **新闻聚合** | newsnow-aggregation | ⭐⭐⭐⭐ |
| 6 | **科技新闻** | tech-news | ⭐⭐⭐⭐ |
| 7 | **AI 中文日报** | ai-news-zh | ⭐⭐⭐⭐ |
| 8 | **RSS/博客** | blogwatcher | ⭐⭐⭐ |
| 9 | **GitHub 热门** | github_trending_collector.py | ⭐⭐⭐ |
| 10 | **通用网络文档** | network_doc_intake.py | ⭐⭐⭐⭐ |

## 4. 文档/OCR（5 种）

| # | 工具 | 能力等级 | 说明 |
|---|------|----------|------|
| 1 | **umi_ocr_bridge** | ⭐⭐⭐⭐ | 中文OCR增强桥接 |
| 2 | **doc_parse_router** | ⭐⭐⭐⭐ | 多格式文档解析路由（PDF/HTML/MD/Office） |
| 3 | **Magic-PDF** | ⭐⭐⭐⭐ | PDF 转 Markdown |
| 4 | **MinerU** | ⭐⭐⭐⭐ | 文档内容提取 |
| 5 | **book_cache_manager** | ⭐⭐⭐⭐ | 710+本书索引+按需缓存分析 |

## 5. 知识分析（7 种）

| # | 工具 | 能力等级 | 说明 |
|---|------|----------|------|
| 1 | **web_search** | ⭐⭐⭐⭐⭐ | 多后端搜索引擎（知识扩展+交叉验证） |
| 2 | **web_extract** | ⭐⭐⭐⭐ | URL内容验证提取 |
| 3 | **nli_fact_check** | ⭐⭐⭐ | NLI 事实一致性核查 |
| 4 | **comment_summary** | ⭐⭐⭐ | 评论观点摘要 |
| 5 | **enrich_news** | ⭐⭐⭐ | 新闻背景知识补充 |
| 6 | **keyword_analysis** | ⭐⭐⭐⭐ | 关键词自动提取分析 |
| 7 | **cross_validate** | ⭐⭐⭐⭐⭐ | 多源交叉验证工作流 |

## 6. 笔记生成与入库

| 步骤 | 工具 | 说明 |
|------|------|------|
| 结构化提炼 | LLM (DeepSeek/OpenAI) | 原始材料→结构化要点 |
| 本地写入 | 文件系统 | `其他笔记/[笔记名]/[笔记名].md` |
| 知识图谱 | gbrain MCP | `gbrain_put_page` + `add_link` + `add_tag` |
| 云盘同步 | rclone | OneDrive/Google Drive等12+云盘 |

## 7. 知识精炼（新增）

从原始文档中提取结构化知识，输出为可加载的 Hermes Skill + KMM 精炼笔记。

| # | 工具 | 能力等级 | 说明 |
|---|------|----------|------|
| 1 | **book_to_skill 管线** | ⭐⭐⭐⭐⭐ | PDF/EPUB → 结构化输出（glossary + patterns + cheatsheet + 章节索引） |
| 2 | **pdfplumber 引擎** | ⭐⭐⭐⭐ | 表格保留提取（技术书首选） |
| 3 | **pdftotext 引擎** | ⭐⭐⭐⭐ | 快速文本提取（极速，适合纯文字书） |
| 4 | **双引擎降级链** | ⭐⭐⭐⭐ | pdfplumber → pdftotext → pdfminer 自动降级 |
| 5 | **章节自动分割** | ⭐⭐⭐⭐ | 章节标题识别 + 页分割 + 字符分割三层策略 |

**输出架构：**

```
采集（原始 PDF）  →  提取（双引擎）  →  分析（章节分割）
                                          ↓
                              ┌─────────────────────┐
                              │ Hermes Skill         │  →  按需加载章节
                              │ KMM 精炼笔记          │  →  glossary + patterns + cheatsheet
                              └─────────────────────┘
```

**使用方式：**

```bash
# 完整管线（推荐）
python3 /root/.hermes/scripts/book_to_skill.py all <file.pdf> --name <slug>

# 仅 Hermes Skill
python3 /root/.hermes/scripts/book_to_skill.py forge <file.pdf> --name <slug>

# 仅 KMM 精炼笔记
python3 /root/.hermes/scripts/book_to_skill.py refine <file.pdf> --name <slug>

# 查看已精炼的知识
python3 -c "from src.knowledge_collector.refinement import list_refined; print(list_refined())"
```

**借鉴来源：** [virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill) — 编译时知识结构化理念。

## 7. 知识图谱（gbrain 集成）

| 操作 | MCP 工具 | 说明 |
|------|----------|------|
| 创建页面 | gbrain_put_page | 写入Markdown+YAML frontmatter |
| 搜索 | gbrain_query | 向量+关键词混合检索 |
| 链接 | gbrain_add_link | 页面间建立关联 |
| 标签 | gbrain_add_tag / remove_tag | 页面分类标签 |
| 时间线 | gbrain_add_timeline_entry | 记录事件时间线 |
| 图遍历 | gbrain_traverse_graph | 关联关系探索 |
| 文件上传 | gbrain_file_upload | 附件存储 |
| 批量链接 | gbrain-link-orphans.py | 基于共享标签批量链接孤页 |

## 8. 采集编排

采集不是孤立的——它与记忆体、知识图谱、笔记、云盘形成闭环：

```
采集 → 处理 → 笔记 → gbrain → 云盘同步
  │                                    │
  └──────── 下次采集先去重 ──────────┘
```

### 定时调度

| 调度 | 模块 | 频率 |
|------|------|------|
| GitHub 热门采集 | github_trending_collector.py | 每日 18:00, 21:00 |
| 笔记→OneDrive 同步 | rclone | 每 30 分钟 |
| 书籍缓存清理 | book_cache_cleanup.sh | 每周日 03:00 |
| 知识图谱链接修复 | gbrain-link-orphans.py | 手动/按需 |

### 技能链路

```
knowledge-intake-collector
  → knowledge-carrier-extraction
    → knowledge-refinery-graph-ingest
      → 笔记成品 + gbrain 节点 + 云盘同步
```
