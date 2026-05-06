from typing import Optional

from groq import Groq

from src.llm.base_provider import BaseLLMProvider
from config.settings import settings


class GroqProvider(BaseLLMProvider):
    """Groq cloud LLM provider."""

    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    def _call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        return response.choices[0].message.content.strip()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self._call(prompt, system_prompt)

    def extract_json(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self._call(prompt, system_prompt)
