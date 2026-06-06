"""
知识增广配置 — 读取环境变量 / .env 文件
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AugmentationConfig:
    """知识增广全量配置"""

    # ── AnySearch 连接 ──
    anysearch_api_key: str = ""
    anysearch_endpoint: str = "https://api.anysearch.com/mcp"

    # ── 搜索行为 ──
    local_first: bool = True
    fallback_threshold: float = 0.6       # 本地相似度低于此值走 web
    max_local_results: int = 5
    max_web_results: int = 8

    # ── 垂直域映射 ──
    # 笔记域 → AnySearch domain 自动匹配
    domain_mapping: dict = field(default_factory=lambda: {
        "finance":    "finance",
        "academic":   "academic",
        "tech":       "code",
        "code":       "code",
        "security":   "security",
        "legal":      "legal",
        "medical":    "health",
        "policy":     "legal",
        "news":       "news",
        "默认":       "",   # 通用搜索
    })


def load_config() -> AugmentationConfig:
    """从环境变量 / .env 加载配置"""
    cfg = AugmentationConfig()

    # 1) 环境变量
    cfg.anysearch_api_key = os.environ.get("ANYSEARCH_API_KEY", "")

    if ep := os.environ.get("ANYSEARCH_ENDPOINT"):
        cfg.anysearch_endpoint = ep
    if val := os.environ.get("KNA_FALLBACK_THRESHOLD"):
        cfg.fallback_threshold = float(val)
    if val := os.environ.get("KNA_LOCAL_FIRST", "true").lower():
        cfg.local_first = val != "false"

    # 2) .env 文件（非 Hermes 环境）
    if not cfg.anysearch_api_key:
        env_paths = [
            Path.cwd() / ".env",
            Path.home() / ".env",
            Path.home() / ".hermes" / ".env",
        ]
        for p in env_paths:
            if p.exists():
                for line in p.read_text().splitlines():
                    line = line.strip()
                    if line.startswith("ANYSEARCH_API_KEY="):
                        cfg.anysearch_api_key = line.split("=", 1)[1].strip().strip("\"'")
                        break

    return cfg
