"""
笔记生成与入库 — 全工具清单

从原始材料到结构化笔记、到知识图谱入库、到云盘同步的全流程。
"""

from __future__ import annotations

from pathlib import Path

from runtime_support import ensure_directory, render_note_markdown, resolve_notes_root, stable_note_id

class NoteGenerator:
    """笔记生成 — 采集→笔记→入库→同步 全链路"""

    PIPELINE = {
        "step1_collect": {
            "title": "采集原始材料",
            "description": "从网页/视频/文章/其他源获取原始内容",
            "tools": ["WebCollector", "VideoCollector", "ArticleCollector", "AnalysisTools"],
        },
        "step2_process": {
            "title": "LLM 结构化提炼",
            "description": "调用 LLM 从原始材料中提取核心论点、数据、关联",
            "method": "LLM Agent 分析（DeepSeek/OpenAI 三层fallback）",
            "output_fields": [
                "核心论点",
                "关键数据/引用",
                "时间线/背景",
                "关联阅读",
                "个人思考/质疑",
            ],
        },
        "step3_note_storage": {
            "title": "写入本地笔记目录",
            "description": "按目录协议写入结构化 Markdown 笔记",
            "directory": "$AGENT_HOME/knowledge/notes/",
            "structure": "<domain>/<note-id>/<note-id>.md",
            "template": "标准 YAML frontmatter + Markdown 正文",
        },
        "step4_knowledge_graph": {
            "title": "gbrain 知识图谱入库",
            "description": "创建知识图谱节点，自动嵌入，链接关联页面",
            "tools": ["gbrain MCP"],
            "operations": [
                "gbrain_put_page — 创建/更新页面",
                "gbrain_add_link — 链接关联页面",
                "gbrain_add_tag — 添加分类标签",
                "gbrain_add_timeline_entry — 时间线记录",
            ],
            "naming": "note-{slug} 格式",
        },
        "step5_cloud_sync": {
            "title": "云盘同步",
            "description": "将本地笔记同步到云端（自动或手动触发）",
            "engine": "CloudSyncEngine (rclone)",
            "target": "example_remote:知识库/笔记/",
            "schedule": "cron: */30 * * * *",
        },
        "chain_summary": {
            "采集": "WebCollector / VideoCollector / ArticleCollector",
            "分析": "AnalysisTools (web_search/交叉验证/NLI)",
            "笔记": "LLM 结构化 → 本地 Markdown 文件",
            "图谱": "gbrain 页面 + 链接 + 标签 + 时间线",
            "同步": "rclone → OneDrive / 其他云盘",
        },
    }

    def generate(self, material, source_type="article", note_title=None):
        """从原始材料生成结构化笔记并完成全链路入库

        自动执行：
        1. LLM 分析 → 结构化要点
        2. 写入本地笔记目录
        3. gbrain 创建知识图谱节点
        4. 触发云盘同步
        """
        payload = dict(material or {})
        title = note_title or payload.get("title") or f"{source_type}-note"
        content = payload.get("content") or payload.get("material") or payload.get("text") or ""
        if not content.strip():
            raise ValueError("material content is required")
        domain = payload.get("domain") or "personal"
        source_ref = payload.get("source_ref") or payload.get("url") or ""
        metadata = payload.get("metadata") or {}
        note_id = stable_note_id(title, content)
        note_dir = ensure_directory(resolve_notes_root() / domain / note_id)
        note_path = note_dir / f"{note_id}.md"
        note_path.write_text(
            render_note_markdown(
                title=title,
                content=content,
                domain=domain,
                source_type=source_type,
                source_ref=source_ref,
                tags=payload.get("tags") or (),
                metadata=metadata,
            ),
            encoding="utf-8",
        )
        return {
            "note_id": note_id,
            "note_path": str(note_path),
            "domain": domain,
            "title": title,
        }


def generate_note(material, template="article", note_title=None):
    return NoteGenerator().generate(material, source_type=template, note_title=note_title)
