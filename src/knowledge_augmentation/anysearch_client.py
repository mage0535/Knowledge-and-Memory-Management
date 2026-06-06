"""
AnySearch 直连客户端 — 通过 MCP Streamable HTTP 协议调用 AnySearch 搜索 API

纯 requests 实现，零额外依赖。支持:
  - search()        — 通用 / 垂直搜索
  - batch_search()  — 并行批量
  - list_domains()  — 查询垂直领域
  - extract()       — URL 内容提取

MCP Streamable HTTP 协议:
  POST {endpoint}
  Content-Type: application/json
  Authorization: Bearer {api_key}

  请求体: {"jsonrpc":"2.0","id":1,"method":"tools/call",
           "params":{"name":"<tool>","arguments":{...}}}
  响应体: {"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"..."}]}}
"""

import json
import logging
from typing import Any, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

logger = logging.getLogger("kmm.augmentation.anysearch")


class AnySearchError(Exception):
    pass


class AnySearchClient:
    """AnySearch MCP HTTP 直连客户端"""

    def __init__(self, api_key: str = "", endpoint: str = "https://api.anysearch.com/mcp"):
        self.endpoint = endpoint.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self._initialized = False

    # ── 公开接口 ──────────────────────────────────────────────

    def search(
        self,
        query: str,
        domain: str = "",
        sub_domain: str = "",
        max_results: int = 10,
        freshness: str = "",
        content_types: Optional[list[str]] = None,
    ) -> list[dict]:
        """通用 / 垂直搜索"""
        args = {"query": query, "max_results": max_results}
        if domain:
            args["domain"] = domain
        if sub_domain:
            args["sub_domain"] = sub_domain
        if freshness:
            args["freshness"] = freshness
        if content_types:
            args["content_types"] = content_types
        return self._call_tool("search", args)

    def batch_search(self, queries: list[dict]) -> list[list[dict]]:
        """并行批量搜索，queries = [{"query":..., "domain":..., ...}, ...]"""
        result = self._call_tool("batch_search", {"queries": queries})
        return result if isinstance(result, list) else [result]

    def list_domains(self) -> list[dict]:
        """查询全部垂直领域"""
        return self._call_tool("list_domains", {})

    def extract(self, url: str) -> str:
        """提取 URL 内容（HTML → Markdown）"""
        result = self._call_tool("extract", {"url": url})
        if isinstance(result, list):
            texts = [r.get("text", "") for r in result if isinstance(r, dict)]
            return "\n".join(texts)
        return str(result)

    # ── 内部 ────────────────────────────────────────────────

    def _call_tool(self, tool_name: str, arguments: dict) -> Any:
        """向 MCP 端点发起一次工具调用"""
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }).encode("utf-8")

        req = Request(self.endpoint, data=payload, headers=self.headers, method="POST")
        try:
            with urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            raise AnySearchError(f"HTTP {e.code}: {e.reason}") from e
        except URLError as e:
            raise AnySearchError(f"网络错误: {e.reason}") from e
        except json.JSONDecodeError as e:
            raise AnySearchError(f"响应不是合法 JSON: {e}") from e
        except TimeoutError:
            raise AnySearchError("请求超时 (30s)")

        # 检查 MCP 错误
        if "error" in body:
            err = body["error"]
            raise AnySearchError(f"MCP 错误 [{err.get('code', '?')}]: {err.get('message', '未知')}")

        # 解析 result.content
        result = body.get("result", {})
        content = result.get("content", [])

        # 尝试提取结构化数据
        parsed = self._parse_content(content)
        return parsed or content

    @staticmethod
    def _parse_content(content: list) -> Any:
        """尝试解析 content 中的 JSON 文本"""
        for item in content:
            text = item.get("text", "")
            if not text:
                continue
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                continue
        return None
