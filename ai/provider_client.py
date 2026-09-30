"""
Async Client for External LLM Providers (OpenAI, Anthropic, OpenRouter, Groq, DeepSeek, Ollama, Custom)
"""
import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, List
from config import (
    AI_PROVIDER_OPENROUTER, AI_PROVIDER_OPENAI, AI_PROVIDER_ANTHROPIC,
    AI_PROVIDER_GROQ, AI_PROVIDER_DEEPSEEK, AI_PROVIDER_OLLAMA, AI_PROVIDER_CUSTOM
)

PROVIDER_URLS = {
    AI_PROVIDER_OPENROUTER: "https://openrouter.ai/api/v1/chat/completions",
    AI_PROVIDER_OPENAI: "https://api.openai.com/v1/chat/completions",
    AI_PROVIDER_ANTHROPIC: "https://api.anthropic.com/v1/messages",
    AI_PROVIDER_GROQ: "https://api.groq.com/openai/v1/chat/completions",
    AI_PROVIDER_DEEPSEEK: "https://api.deepseek.com/chat/completions",
    AI_PROVIDER_OLLAMA: "http://localhost:11434/v1/chat/completions",
}

async def call_external_llm(
    provider: str,
    api_key: Optional[str],
    model: str,
    prompt: str,
    system_instruction: Optional[str] = None,
    custom_endpoint: Optional[str] = None,
    temperature: float = 0.7,
    timeout_sec: int = 15
) -> Optional[str]:
    """Sends a completion request to the chosen LLM provider."""
    url = custom_endpoint if (provider == AI_PROVIDER_CUSTOM and custom_endpoint) else PROVIDER_URLS.get(provider)
    if not url:
        return None

    headers = {"Content-Type": "application/json"}
    if api_key and provider != AI_PROVIDER_OLLAMA:
        if provider == AI_PROVIDER_ANTHROPIC:
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
        else:
            headers["Authorization"] = f"Bearer {api_key}"

    if provider == AI_PROVIDER_OPENROUTER:
        headers["HTTP-Referer"] = "https://paxhistoria.co"
        headers["X-Title"] = "Pax Historia Telegram Bot"

    payload: Dict[str, Any] = {}
    if provider == AI_PROVIDER_ANTHROPIC:
        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": model or "claude-3-5-haiku-20241022",
            "messages": messages,
            "max_tokens": 1500,
            "temperature": temperature
        }
        if system_instruction:
            payload["system"] = system_instruction
    else:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or "gpt-4o-mini",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1500
        }

    try:
        timeout = aiohttp.ClientTimeout(total=timeout_sec)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if provider == AI_PROVIDER_ANTHROPIC:
                        content_blocks = data.get("content", [])
                        if content_blocks and isinstance(content_blocks, list):
                            return content_blocks[0].get("text", "")
                    else:
                        choices = data.get("choices", [])
                        if choices and isinstance(choices, list):
                            return choices[0].get("message", {}).get("content", "")
                else:
                    err_text = await resp.text()
                    print(f"External LLM API Error ({provider} - {resp.status}): {err_text[:200]}")
                    return None
    except Exception as e:
        print(f"External LLM Exception ({provider}): {e}")
        return None

    return None
