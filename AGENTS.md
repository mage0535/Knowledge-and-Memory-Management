# AGENTS.md — AI Agent 接入指南

如果你是 AI Agent（Claude Code / Cursor / Copilot 等），请按以下步骤集成本插件。

## 前提条件

你的运行环境中需要已安装记忆体系统：
- `gbrain` (端口 8787) — 知识图谱
- `Hindsight` (端口 8890) — 向量记忆

## 安装后可用能力

插件安装后，你将获得以下新增的工具和技能：

### knowledge_collector (知识采集)

| 函数 | 功能 |
|------|------|
| `collect_web(url)` | 采集网页内容并入库 |
| `collect_video(url)` | 采集视频内容 (OCR+ASR) |
| `collect_article(source, keyword)` | 采集文章内容 |
| `generate_note(material, template)` | 生成结构化笔记 |

### notes_rag (笔记/RAG)

| 函数 | 功能 |
|------|------|
| `create_note(title, content, domain)` | 创建笔记 |
| `search_notes(query, domains)` | 跨域检索 |
| `sync_notes_to_cloud()` | 同步笔记到云盘 |

### cloud_sync (云盘同步)

| 函数 | 功能 |
|------|------|
| `list_cloud_drives()` | 列出已配置云盘 |
| `sync_to_cloud(local, remote)` | 同步到云盘 |
| `sync_from_cloud(remote, local)` | 从云盘同步 |

### knowledge_augmentation (知识增广 - 新增)

| 函数 | 功能 |
|------|------|
| `augmented_search(query, domain)` | 本地优先 + AnySearch 回落搜索 |
| `augmented_search.list_domains()` | 查询 AnySearch 全部垂直领域 |
| `config.load_config()` | 加载 AnySearch 配置 |

## 工作流示例

```
用户问: "帮我整理这篇公众号文章"
  → collect_article("wechat", url)
  → analyze → extract_keywords
  → generate_note → create_note
  → sync_to_cloud
  → 返回结果给用户
```
