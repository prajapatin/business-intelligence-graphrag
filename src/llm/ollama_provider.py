from typing import Optional
import json

import httpx

from src.llm.base_provider import BaseLLMProvider
from config.settings import settings


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    def _call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "options": {
                "temperature": settings.temperature,
                "num_predict": settings.max_tokens,
            },
        }

        if system_prompt:
            payload["messages"] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
            endpoint = f"{self.base_url}/api/chat"
        else:
            payload["messages"] = [
                {"role": "user", "content": prompt},
            ]
            endpoint = f"{self.base_url}/api/chat"

        response = httpx.post(endpoint, json=payload, timeout=120.0)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"].strip()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self._call(prompt, system_prompt)

    def extract_json(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self._call(prompt, system_prompt)
