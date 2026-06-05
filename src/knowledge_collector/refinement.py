"""
知识精炼模块 — 知识采集管线 → 结构化输出

将原始采集内容（PDF/网页/视频笔记）精炼为结构化知识：
- Hermes Skill 格式（可加载技能）
- KMM 精炼笔记（glossary + patterns + cheatsheet）
- 术语表 + 模式库 + 速查表

依赖: book_to_skill 管线（/root/.hermes/scripts/book_to_skill.py）
"""

import os
import subprocess
import sys
from pathlib import Path


BOOK_TO_SKILL = "/root/.hermes/scripts/book_to_skill.py"
HERMES_SKILLS = Path(os.environ.get("HERMES_SKILLS_DIR",
    os.path.expanduser("~/.hermes/skills")))
KMM_NOTES = Path(os.environ.get("KMM_NOTES_DIR",
    os.path.expanduser("~/knowledge/structured")))


def refine_pdf(pdf_path: str, slug: str = "") -> dict:
    """
    对 PDF 执行完整精炼管线。
    
    Args:
        pdf_path: PDF 文件路径
        slug: 输出 slug（默认基于文件名）
    
    Returns:
        {hermes_skill_dir, kmm_notes_dir, chapter_count, engine}
    """
    if not os.path.exists(pdf_path):
        return {"error": f"文件不存在: {pdf_path}"}

    if slug is None:
        slug = os.path.splitext(os.path.basename(pdf_path))[0].replace(" ", "-").lower()

    result = subprocess.run(
        [sys.executable, BOOK_TO_SKILL, "all", pdf_path, "--name", slug],
        capture_output=True, text=True, timeout=120
    )

    if result.returncode != 0:
        return {"error": result.stderr or result.stdout}

    return {
        "hermes_skill_dir": str(HERMES_SKILLS / f"book-{slug}"),
        "kmm_notes_dir": str(KMM_NOTES / slug),
        "slug": slug,
        "output": result.stdout,
    }


def list_refined() -> list:
    """列出所有已精炼的知识"""
    results = []
    if HERMES_SKILLS.exists():
        for d in sorted(HERMES_SKILLS.glob("book-*")):
            sk = d / "SKILL.md"
            if sk.exists():
                with open(sk) as f:
                    content = f.read()
                name = d.name.replace("book-", "")
                desc = ""
                for line in content.split("\n"):
                    if "description:" in line:
                        desc = line.split(":", 1)[-1].strip().strip('"')
                        break
                results.append({"slug": name, "type": "hermes-skill", "path": str(d), "description": desc})
    
    if KMM_NOTES.exists():
        for d in sorted(KMM_NOTES.glob("*")):
            idx = d / "index.md"
            if idx.exists():
                results.append({"slug": d.name, "type": "kmm-notes", "path": str(d)})
    
    return results


def glossary_from_notes(slug: str) -> str:
    """从已精炼笔记提取术语表（框架->实际填充）"""
    notes_dir = KMM_NOTES / slug
    glossary_path = notes_dir / "glossary.md"
    if glossary_path.exists():
        with open(glossary_path) as f:
            return f.read()
    return ""
