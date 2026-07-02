from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

import httpx

from app.config import get_settings


@dataclass
class LLMResponse:
    answer: str
    cached: bool = False
    latency_ms: int = 0


class OpenRouterClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._cache: dict[str, tuple[float, str]] = {}

    async def generate(self, query: str, profile: dict, contexts: list[dict]) -> LLMResponse:
        started = time.perf_counter()
        cache_key = self._cache_key(query, profile, contexts)
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached[0]) < self.settings.llm_cache_ttl_seconds:
            return LLMResponse(answer=cached[1], cached=True, latency_ms=int((time.perf_counter() - started) * 1000))

        if not self.settings.openrouter_api_key:
            answer = self._fallback_answer(query, contexts)
            return LLMResponse(answer=answer, cached=False, latency_ms=int((time.perf_counter() - started) * 1000))

        messages = [
            {
                "role": "system",
                "content": (
                    "You are YojanaGPT, an Indian government scheme eligibility assistant. "
                    "Use only supplied context. Return concise markdown with sections: "
                    "Eligible schemes, Why, Missing requirements, Documents, Application links, Citations. "
                    "State uncertainty clearly and never invent deadlines."
                ),
            },
            {
                "role": "user",
                "content": f"Profile: {profile}\nQuestion: {query}\nContext: {contexts}",
            },
        ]

        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "YojanaGPT",
                },
                json={"model": self.settings.openrouter_model, "messages": messages, "temperature": 0.2},
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]

        self._cache[cache_key] = (time.time(), answer)
        return LLMResponse(answer=answer, cached=False, latency_ms=int((time.perf_counter() - started) * 1000))

    @staticmethod
    def _cache_key(query: str, profile: dict, contexts: list[dict]) -> str:
        raw = f"{query}|{profile}|{contexts}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _fallback_answer(query: str, contexts: list[dict]) -> str:
        citations = ", ".join(context.get("source_url", "local source") for context in contexts[:3]) or "no indexed sources"
        return (
            "### Eligible schemes\n"
            "I found potentially relevant indexed material, but LLM generation is not configured.\n\n"
            "### Why\n"
            f"The query was matched against local retrieval for: {query}\n\n"
            "### Citations\n"
            f"{citations}"
        )
