#!/usr/bin/env python3
"""Lightweight MCP server for KMM workflows.

Binds to configurable port, exposes KMM tools via stdio or HTTP.

Usage:
  KMM_MCP_ENABLED=1 python3 src/mcp_server.py --port 9797
  KMM_MCP_TRANSPORT=stdio python3 src/mcp_server.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from knowledge_collector import collect_web, collect_video, collect_article, analyze_material, generate_note
from notes_rag import search_notes, create_note, sync_notes_to_cloud
from knowledge_collector.query_rewrite import preprocess_query
from cloud_sync import list_cloud_drives

TOOLS = {
    "kmm_collect_web": {
        "description": "Collect web page content and generate a structured note with knowledge object",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target web page URL"},
            },
            "required": ["url"],
        },
    },
    "kmm_search": {
        "description": "Multi-layer fused knowledge search across local notes, state FTS5, Hindsight, and gbrain",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Domains to search: personal, shared, archive",
                },
            },
            "required": ["query"],
        },
    },
    "kmm_analyze": {
        "description": "Analyze text and return structured knowledge object",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "title": {"type": "string"},
                "source_type": {"type": "string", "default": "article"},
            },
            "required": ["text"],
        },
    },
    "kmm_health": {
        "description": "Get KMM health status including note counts, sync state, and service availability",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "kmm_list_drives": {
        "description": "List configured cloud storage drives",
        "inputSchema": {"type": "object", "properties": {}},
    },
}


def handle_tool_call(name: str, arguments: dict) -> dict:
    if name == "kmm_collect_web":
        result = collect_web(arguments["url"])
        return {
            "content": [{"type": "text", "text": json.dumps({
                "title": result.title,
                "note_path": result.note_path,
                "source_type": result.source_type,
            }, ensure_ascii=False)}],
        }
    elif name == "kmm_search":
        query = preprocess_query(arguments["query"])
        results = search_notes(query["original"], domains=arguments.get("domains"))
        return {
            "content": [{"type": "text", "text": json.dumps({
                "query": query,
                "results": results[:10],
            }, ensure_ascii=False, default=str)}],
        }
    elif name == "kmm_analyze":
        knowledge = analyze_material({
            "title": arguments.get("title", "cli-input"),
            "content": arguments["text"],
        }, source_type=arguments.get("source_type", "article"))
        return {
            "content": [{"type": "text", "text": json.dumps(knowledge, ensure_ascii=False)}],
        }
    elif name == "kmm_health":
        from scripts.kmm_health_check import collect_health
        health = collect_health()
        return {
            "content": [{"type": "text", "text": json.dumps(health, ensure_ascii=False, default=str)}],
        }
    elif name == "kmm_list_drives":
        drives = list_cloud_drives()
        return {
            "content": [{"type": "text", "text": json.dumps({"drives": drives}, ensure_ascii=False)}],
        }
    return {"content": [{"type": "text", "text": json.dumps({"error": f"unknown tool: {name}"})}]}


def serve_stdio():
    """Simple JSON-RPC stdio server for MCP."""
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
        except (json.JSONDecodeError, ValueError):
            continue
        method = request.get("method", "")
        rpc_id = request.get("id")
        if method == "tools/list":
            response = {"jsonrpc": "2.0", "id": rpc_id, "result": {"tools": [
                {"name": name, **schema} for name, schema in TOOLS.items()
            ]}}
        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name", "")
            arguments = request.get("params", {}).get("arguments", {})
            response = {"jsonrpc": "2.0", "id": rpc_id, "result": handle_tool_call(tool_name, arguments)}
        else:
            response = {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": f"unknown method: {method}"}}
        print(json.dumps(response, ensure_ascii=False), flush=True)


def main():
    if os.environ.get("KMM_MCP_TRANSPORT") == "stdio":
        serve_stdio()
    else:
        print("MCP server available. Use KMM_MCP_TRANSPORT=stdio for agent integration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
