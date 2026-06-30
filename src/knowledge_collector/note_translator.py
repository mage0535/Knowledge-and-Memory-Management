"""Optional note translation layer for multi-language knowledge rendering.

Env: KMM_TRANSLATE_PROVIDER=openai|anthropic|deepseek, KMM_TRANSLATE_API_KEY
"""

from __future__ import annotations

import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    provider = os.environ.get("KMM_TRANSLATE_PROVIDER", "")
    if provider == "openai":
        return _translate_openai(text, target_lang)
    if provider == "deepseek":
        return _translate_deepseek(text, target_lang)
    return text


def translate_note_content(content: str, target_lang: str = "en", preserve_original: bool = True) -> str:
    if not os.environ.get("KMM_TRANSLATE_API_KEY"):
        if preserve_original:
            return content + "\n\n> *Translation not available (set KMM_TRANSLATE_API_KEY)*\n"
        return content

    lines = content.splitlines()
    translated = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```") or stripped.startswith("---"):
            translated.append(line)
            continue
        translated.append(translate_text(stripped, target_lang))
    result = "\n".join(translated)
    if preserve_original:
        result += f"\n\n---\n<details>\n<summary>Original ({target_lang} translated)</summary>\n\n{content}\n</details>\n"
    return result


def _translate_openai(text: str, target_lang: str) -> str:
    api_key = os.environ.get("KMM_TRANSLATE_API_KEY", "")
    if not api_key:
        return text
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": f"Translate to {target_lang}. Return only the translation, no explanation:\n\n{text}"}],
        "temperature": 0.1,
    }).encode("utf-8")
    try:
        req = Request("https://api.openai.com/v1/chat/completions", data=payload,
                      headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except (URLError, TimeoutError, KeyError, json.JSONDecodeError):
        return text


def _translate_deepseek(text: str, target_lang: str) -> str:
    api_key = os.environ.get("KMM_TRANSLATE_API_KEY", "")
    if not api_key:
        return text
    endpoint = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": f"Translate to {target_lang}. Return only the translation, no explanation:\n\n{text}"}],
        "temperature": 0.1,
    }).encode("utf-8")
    try:
        req = Request(f"{endpoint}/v1/chat/completions", data=payload,
                      headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except (URLError, TimeoutError, KeyError, json.JSONDecodeError):
        return text
