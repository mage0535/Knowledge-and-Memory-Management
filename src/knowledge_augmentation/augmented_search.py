"""
增强搜索（Augmented Search）— 本地笔记优先，AnySearch 垂直搜索自动回落

使用流程:
  from knowledge_augmentation import AugmentedSearch

  searcher = AugmentedSearch()
  results = searcher.search("比亚迪 2026Q1 财报")

返回结果会自动标注来源: local / web
"""

import logging
from pathlib import Path
from typing import Any, Optional

from .config import load_config, AugmentationConfig
from .anysearch_client import AnySearchClient, AnySearchError

logger = logging.getLogger("kmm.augmentation.search")


class AugmentedSearch:
    """搜索增广器 — 本地优先 + web 回落"""

    def __init__(self, config: Optional[AugmentationConfig] = None):
        self.cfg = config or load_config()
        self._anysearch: Optional[AnySearchClient] = None

    # ── 公开接口 ──────────────────────────────────────────

    def search(
        self,
        query: str,
        domain: str = "",
        domains: Optional[list[str]] = None,
        local_only: bool = False,
        web_only: bool = False,
    ) -> dict:
        """
        核心搜索方法

        参数:
          query:    搜索关键词
          domain:   指定垂直域（finance/academic/code 等），空=自动判断
          domains:  多域同时搜索（覆盖 > domain）
          local_only: 只搜本地，不走 web
          web_only:   只搜 web，不走本地

        返回:
          {
            "query": "...",
            "source": "local" | "web" | "hybrid",
            "local_weight": 0.0-1.0,
            "results": [...],
            "augmented": True/False,
          }
        """
        # ── 模式 A: 只搜本地 ──
        if web_only:
            return self._search_web(query, domain, domains)

        local_results = self._search_local(query)
        local_weight = self._score_local(local_results)

        # 本地命中足够 || 只搜本地
        if local_weight >= self.cfg.fallback_threshold or local_only:
            return {
                "query": query,
                "source": "local",
                "local_weight": local_weight,
                "results": local_results,
                "augmented": False,
            }

        # ── 模式 B: 本地不足 → 走 AnySearch ──
        web_results = self._search_web(query, domain, domains, local_hint=local_results)

        return {
            "query": query,
            "source": "web" if not local_results else "hybrid",
            "local_weight": local_weight,
            "results": local_results + web_results,
            "augmented": True,
        }

    def list_domains(self) -> list[dict]:
        """查询 AnySearch 支持的全部垂直领域"""
        client = self._get_anysearch()
        try:
            return client.list_domains()
        except AnySearchError as e:
            logger.warning("list_domains 失败: %s", e)
            return []

    # ── 内部 ──────────────────────────────────────────────

    def _get_anysearch(self) -> AnySearchClient:
        """懒加载 AnySearch 客户端"""
        if self._anysearch is None:
            self._anysearch = AnySearchClient(
                api_key=self.cfg.anysearch_api_key,
                endpoint=self.cfg.anysearch_endpoint,
            )
        return self._anysearch

    def _search_local(self, query: str) -> list[dict]:
        """搜本地笔记库 — 聚合 gbrain + notes_rag + Hindsight"""
        results = []

        # 1) gbrain 语义搜索（Hermes 环境可用时）
        try:
            from gbrain_bridge import search_gbrain as _gbrain_search
            gbrain_results = _gbrain_search(query, limit=self.cfg.max_local_results)
            for r in gbrain_results:
                results.append({
                    "source": "gbrain",
                    "title": r.get("title", r.get("slug", "")),
                    "content": r.get("summary", "")[:300],
                    "score": r.get("score", 0.5),
                    "url": r.get("slug", ""),
                })
        except ImportError:
            pass  # gbrain 不可用时静默降级

        # 2) 本地文件全文搜索
        import subprocess
        try:
            notes_dir = Path.home() / "knowledge" / "notes"
            if notes_dir.exists():
                grep = subprocess.run(
                    ["rg", "-l", "-i", query, "--max-count", "3", "-g", "*.md", str(notes_dir)],
                    capture_output=True, text=True, timeout=10,
                )
                for fp in grep.stdout.strip().split("\n"):
                    if not fp:
                        continue
                    fpath = Path(fp)
                    results.append({
                        "source": "local_file",
                        "title": fpath.stem,
                        "content": fpath.read_text(encoding="utf-8", errors="replace")[:200],
                        "score": 0.4,
                        "url": str(fpath),
                    })
        except Exception:
            pass

        # 按分数排序
        results.sort(key=lambda r: r.get("score", 0), reverse=True)
        return results[:self.cfg.max_local_results]

    def _score_local(self, results: list[dict]) -> float:
        """评估本地结果覆盖率，返回 [0, 1]"""
        if not results:
            return 0.0
        scores = [r.get("score", 0) for r in results]
        return max(scores)

    def _search_web(
        self,
        query: str,
        domain: str = "",
        domains: Optional[list[str]] = None,
        local_hint: Optional[list] = None,
    ) -> list[dict]:
        """走 AnySearch 垂直搜索"""
        client = self._get_anysearch()
        results = []

        try:
            # 多域搜索
            target_domains = domains or ([domain] if domain else [""])

            for d in target_domains:
                raw = client.search(
                    query=query,
                    domain=d,
                    max_results=self.cfg.max_web_results,
                )
                for item in (raw if isinstance(raw, list) else []):
                    title = ""
                    content = ""
                    url = ""
                    if isinstance(item, dict):
                        title = item.get("title", item.get("name", ""))
                        content = item.get("content", item.get("description", ""))
                        url = item.get("url", item.get("link", ""))
                    elif isinstance(item, str):
                        content = item[:300]

                    results.append({
                        "source": f"anysearch/{d}" if d else "anysearch",
                        "title": title[:200] if title else "",
                        "content": (content or "")[:500],
                        "score": 0.7,
                        "url": url,
                        "domain": d,
                    })

        except AnySearchError as e:
            logger.warning("AnySearch web 搜索失败: %s", e)

        return results[:self.cfg.max_web_results]
