#!/usr/bin/env python3
"""
每日方法论蒸馏工具 (Daily Methodology Distiller)
从 Horizon 管线的 filtered/enriched 数据中提取可复用的方法论，写入 gbrain 知识图谱。

三步：
1. 读取 Horizon 最新 run 的 filtered stage（有则用，无则降级到 scored/raw）
2. 输出结构化方法论 JSON 到 stdout（供 cron agent 消费）
3. 输出方法论日报缓存到固定路径（供内容管线引用）

用法:
  python3 distill_methodologies.py                    # 输出方法论 JSON 到 stdout
  python3 distill_methodologies.py --summary           # 输出中文日报到 stdout
  python3 distill_methodologies.py --cache             # 写入缓存文件 + gbrain

依赖: horizon MCP (通过 cron agent 调用), gbrain MCP
"""
import json, os, sys, datetime, glob, time

AGENT_HOME = os.path.expanduser(os.environ.get("AGENT_HOME", os.environ.get("HERMES_HOME", "~/.hermes")))
HORIZON_PATH = os.path.join(AGENT_HOME, "skills", "external", "Horizon", "data", "mcp-runs")
CACHE_FILE = os.path.join(AGENT_HOME, "data", "methodology_cache.json")
SUMMARY_FILE = os.path.join(AGENT_HOME, "data", "methodology_daily.md")

def get_latest_run():
    """获取 Horizon 最新 run 的 artifact 路径"""
    if not os.path.isdir(HORIZON_PATH):
        return None, None
    runs = sorted([d for d in os.listdir(HORIZON_PATH) if d.startswith("run-")])
    if not runs:
        return None, None
    latest = runs[-1]
    return latest, os.path.join(HORIZON_PATH, latest)

def load_stage(run_dir, stage):
    """加载 Horizon run 的某个 stage artifact"""
    path = os.path.join(run_dir, f"{stage}_items.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    return data

def prioritize_stage(run_dir):
    """按优先级返回数据: enriched > filtered > scored > raw"""
    for stage, label in [("enriched", "enriched"), ("filtered", "filtered"),
                          ("scored", "scored"), ("raw", "raw")]:
        data = load_stage(run_dir, stage)
        if data and (isinstance(data, list) or "items" in data or (isinstance(data, dict) and data.get("count", 0) > 0)):
            items = data if isinstance(data, list) else data.get("items", data.get("data", []))
            if items and len(items) > 0:
                return label, items
    return None, []

def extract_methodology_summary(run_id, stage, item_count):
    """生成方法论摘要元数据"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "run_id": run_id,
        "stage": stage,
        "item_count": item_count,
        "distilled_at": now,
        "distill_date": datetime.datetime.now().strftime("%Y-%m-%d"),
    }

def generate_gbrain_page(methodologies, meta):
    """生成 gbrain 页面 markdown（供 cron agent 通过 MCP 写入）"""
    title = f"方法论日报 - {meta['distill_date']}"
    lines = [
        f"---",
        f"title: 方法论日报 {meta['distill_date']}",
        f"tags: [methodology-distillation, daily, horizon]",
        f"---",
        f"",
        f"# 方法论日报 - {meta['distill_date']}",
        f"",
        f"**数据源**: Horizon (`{meta['run_id']}`, stage={meta['stage']}, {meta['item_count']} items)",
        f"**蒸馏时间**: {meta['distilled_at']}",
        f"",
    ]
    if not methodologies:
        lines.append("> 今日无方法论产出（数据不足或未达阈值）")
    else:
        for m in methodologies:
            lines.append(f"## {m.get('methodology', '未命名方法论')}")
            lines.append(f"")
            lines.append(f"**领域**: {m.get('domain', '通用')}")
            lines.append(f"**模式**: {m.get('pattern', 'N/A')}")
            lines.append(f"**适用场景**: {m.get('apply_scenario', 'N/A')}")
            if m.get("source_articles"):
                lines.append(f"**来源**: {', '.join(m['source_articles'][:3])}")
            lines.append(f"")
    return "\n".join(lines)

def cache_report(methodologies, meta):
    """写入缓存文件"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({"meta": meta, "methodologies": methodologies}, f, ensure_ascii=False, indent=2)

    # 生成中文日报
    md = [
        f"## 📊 今日方法论日报 - {meta['distill_date']}",
        f"",
        f"数据来源: {meta.get('stage','N/A')} ({meta.get('item_count',0)} 条)",
        f"",
    ]
    if not methodologies:
        md.append("今日无方法论产出。")
    else:
        for i, m in enumerate(methodologies, 1):
            md.append(f"**{i}. {m.get('methodology','')}** — {m.get('domain','')}")
            md.append(f"> {m.get('pattern','')}")
            if m.get('apply_scenario'):
                md.append(f"> 适用: {m['apply_scenario']}")
            md.append(f"")
    md_content = "\n".join(md)
    with open(SUMMARY_FILE, "w") as f:
        f.write(md_content)
    return CACHE_FILE, SUMMARY_FILE

def main():
    mode = "json"  # default
    if "--summary" in sys.argv:
        mode = "summary"
    elif "--cache" in sys.argv:
        mode = "cache"

    run_id, run_dir = get_latest_run()
    if not run_dir:
        print(json.dumps({"error": "no_horizon_runs", "meta": extract_methodology_summary(None, None, 0)}, ensure_ascii=False))
        return 0

    stage, items = prioritize_stage(run_dir)
    meta = extract_methodology_summary(run_id, stage, len(items) if items else 0)
    meta["stage"] = stage

    if mode == "summary":
        # Cron agent 负责做实际的 LLM 分析，此脚本只准备数据结构
        preview = [{"title": i.get("title","")[:80], "url": i.get("url",""),
                     "source": i.get("source_type",""), "hn_score": i.get("metadata",{}).get("score",0)}
                    for i in (items or [])[:10]]
        result = {"meta": meta, "items_preview": preview, "note": "由 cron agent 调用 LLM 完成实际方法论提取"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Standard JSON output
        preview = [{"title": i.get("title","")[:80], "url": i.get("url",""),
                     "source": i.get("source_type",""), "hn_score": i.get("metadata",{}).get("score",0)}
                    for i in (items or [])[:10]]
        result = {"meta": meta, "items": (items or [])[:20], "items_preview": preview[:10]}
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0

if __name__ == "__main__":
    sys.exit(main())
