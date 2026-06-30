"""Optional LLM-powered knowledge analyzer with deterministic fallback.

Env: KMM_LLM_PROVIDER=openai|deepseek|anthropic, KMM_LLM_API_KEY
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from .analysis import KnowledgeAnalyzer, KnowledgeObject, SCHEMA_VERSION


class LlmKnowledgeAnalyzer:
    """Optional LLM-enhanced analyzer. Falls back to deterministic when credentials absent."""

    def __init__(self):
        self.provider = os.environ.get("KMM_LLM_PROVIDER", "")
        self.api_key = os.environ.get("KMM_LLM_API_KEY", "")
        self.model = os.environ.get("KMM_LLM_MODEL", {
            "openai": "gpt-4o-mini",
            "deepseek": "deepseek-chat",
            "anthropic": "claude-3-5-haiku-latest",
        }.get(self.provider, "gpt-4o-mini"))
        self._deterministic = KnowledgeAnalyzer()

    @property
    def available(self) -> bool:
        return bool(self.provider and self.api_key)

    def analyze(self, material: dict[str, Any] | str | None, source_type: str = "article") -> KnowledgeObject:
        if not self.available:
            return self._deterministic_with_metadata(material, source_type, extractor="deterministic")

        try:
            obj = self._llm_analyze(material, source_type)
            if obj and obj.get("claims"):
                ko = self._deterministic.analyze(material, source_type)
                ko.claims = obj.get("claims", ko.claims)
                ko.concepts = obj.get("concepts", ko.concepts)
                ko.action_items = obj.get("action_items", ko.action_items) or ko.action_items
                ko.risks = obj.get("risks", ko.risks) or ko.risks
                ko.summary = (obj.get("summary") or ko.summary)
                ko.quality["llm_score"] = obj.get("quality_score", 0.8)
                ko.metadata["extractor"] = f"llm/{self.provider}"
                return ko
        except Exception:
            pass

        return self._deterministic_with_metadata(material, source_type, extractor=f"llm/{self.provider}-fallback")

    def _deterministic_with_metadata(self, material, source_type, extractor):
        ko = self._deterministic.analyze(material, source_type)
        ko.metadata["extractor"] = extractor
        return ko

    def _llm_analyze(self, material, source_type) -> dict | None:
        if isinstance(material, dict):
            text = material.get("content", "") or material.get("text", "")
        elif isinstance(material, str):
            text = material
        else:
            text = ""
        if len(text.strip()) < 20:
            return None

        prompt = f"""Analyze this {source_type} text. Return JSON only:
{{
  "summary": "1-3 sentence summary",
  "claims": [{{"text": "claim", "evidence": "supporting text", "confidence": 0.0-1.0}}],
  "concepts": [{{"name": "concept", "description": "brief"}}],
  "action_items": ["action sentence"],
  "risks": ["risk or gap"],
  "quality_score": 0.0-1.0
}}

Text: {text[:4000]}"""

        payload = json.dumps(self._build_request(prompt)).encode("utf-8")
        try:
            req = Request(self._endpoint(), data=payload, headers=self._headers())
            with urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            content = self._extract_content(data)
            return json.loads(content.replace("```json", "").replace("```", "").strip())
        except (URLError, TimeoutError, json.JSONDecodeError, KeyError):
            return None

    def _endpoint(self) -> str:
        return {
            "openai": "https://api.openai.com/v1/chat/completions",
            "deepseek": f"{os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')}/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
        }.get(self.provider, "")

    def _headers(self) -> dict:
        base = {"Content-Type": "application/json"}
        if self.provider == "anthropic":
            base["x-api-key"] = self.api_key
            base["anthropic-version"] = "2023-06-01"
        else:
            base["Authorization"] = f"Bearer {self.api_key}"
        return base

    def _build_request(self, prompt: str) -> dict:
        if self.provider == "anthropic":
            return {
                "model": self.model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            }
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 1024,
        }

    def _extract_content(self, data: dict) -> str:
        if self.provider == "anthropic":
            return data["content"][0]["text"]
        return data["choices"][0]["message"]["content"]


def analyze_material_llm(material, source_type="article") -> dict:
    return LlmKnowledgeAnalyzer().analyze(material, source_type).to_dict()
