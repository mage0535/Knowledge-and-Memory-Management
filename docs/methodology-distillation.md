# 方法论蒸馏管线

## 概述

受 AI樟榆树「自进化知识库」理念启发，实现每日从 trending 知识中自动蒸馏可复用方法论的闭环：

```
Horizon (采集 HN + TechCrunch + ArsTechnica)
  → LLM 方法论提取 (03:00 cron agent)
  → gbrain 持久化 (methodology-daily-* 页面)
  → 晨报「今日方法论」板块
  → 渠道内容方向参考
```

## 依赖

- Horizon MCP (MCP server，提供 hz_fetch_items / hz_score_items / hz_get_run_stage)
- gbrain MCP (知识图谱持久化)
- 记忆体系统 (Hindsight + gbrain)

## 使用

```bash
# 查看 Horizon 最新采集数据预览
python3 /path/to/hermes/scripts/distill_methodologies.py --summary

# 写入方法论缓存
python3 /path/to/hermes/scripts/distill_methodologies.py --cache
```

## 工作原理

1. **Horizon 采集**：每日 02:00 cron 运行 `hz_fetch_items` 获取昨日 24h 的 HN/RSS 数据
2. **LLM 方法论蒸馏**：cron agent 分析采集内容，提取可复用的模式/框架/工具
3. **gbrain 持久化**：每条方法论作为独立知识图谱节点，标记为 methodology-daily
4. **晨报集成**：05:30 晨报读取缓存文件，增加「今日方法论」板块
5. **内容方向**：09:00 渠道内容发布前读取方法论方向提示

## 扩展

- 加 RSS 源：编辑 `~/.hermes/skills/external/Horizon/data/config.json` 的 `sources.rss` 数组
- 调评分阈值：修改 `filtering.ai_score_threshold` (默认 3.0)
- 加 GitHub Trending：在 config.json 的 `sources.github` 中添加 repo
