import asyncio
import logging
from typing import List

import httpx

from .base import BaseAgent

logger = logging.getLogger(__name__)


class OpenAICompatibleAgent(BaseAgent):
    """Async agent for OpenAI-compatible APIs (vLLM, DeepSeek, Together, OpenRouter, etc.)."""

    def __init__(
        self,
        model_name: str,
        api_base: str,
        api_key: str = "EMPTY",
        timeout: float = 600.0,
        max_retries: int = 3,
    ):
        super().__init__(model_name)
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries

    def _build_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.api_base,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(self.timeout, connect=10.0),
        )

    async def _call_chat(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
        client: httpx.AsyncClient,
    ) -> str:
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = await client.post("/v1/chat/completions", json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning("Attempt %d/%d failed: %s", attempt, self.max_retries, e)
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(min(2 ** attempt, 10))

    async def generate(
        self,
        prompt: str,
        n: int = 1,
        temperature: float = 1.0,
        max_tokens: int = 32768,
        top_p: float = 0.95,
    ) -> List[str]:
        async with self._build_client() as client:
            tasks = [
                self._call_chat(prompt, temperature, max_tokens, top_p, client)
                for _ in range(n)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        outputs = []
        for r in results:
            if isinstance(r, Exception):
                logger.error("Generation failed: %s", r)
                continue
            outputs.append(r)
        return outputs

    async def generate_batch(
        self,
        prompts: List[str],
        temperature: float = 1.0,
        max_tokens: int = 32768,
        top_p: float = 0.95,
    ) -> List[str]:
        async with self._build_client() as client:
            tasks = [
                self._call_chat(p, temperature, max_tokens, top_p, client)
                for p in prompts
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        outputs = []
        for r in results:
            if isinstance(r, Exception):
                logger.error("Batch generation failed: %s", r)
                outputs.append("")
            else:
                outputs.append(r)
        return outputs
