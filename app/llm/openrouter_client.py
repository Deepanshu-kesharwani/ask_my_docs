from __future__ import annotations

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dataclasses import dataclass
from typing import Any, List, Optional
import structlog

from app.settings import get_settings

log = structlog.get_logger()


@dataclass
class LLMResult:
    content: str
    model: str
    raw: Any


class OpenRouterClient:
    def __init__(self):
        s = get_settings()
        self.settings = s
        self.client = OpenAI(
            base_url=s.openrouter_base_url,
            api_key=s.openrouter_api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-OpenRouter-Title": "Ask My Docs",
            },
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=8),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def chat(self, messages: List[dict], model: Optional[str] = None, temperature: float = 0.2) -> LLMResult:
        models = [model or self.settings.primary_model] + [m for m in self.settings.fallback_models if m != model]
        last_err = None

        for candidate in models:
            try:
                resp = self.client.chat.completions.create(
                    model=candidate,
                    messages=messages,
                    temperature=temperature,
                )
                content = resp.choices[0].message.content or ""
                return LLMResult(content=content, model=candidate, raw=resp)
            except Exception as e:
                last_err = e
                log.warning("llm_call_failed", model=candidate, error=str(e))
                continue

        raise last_err or RuntimeError("LLM call failed")