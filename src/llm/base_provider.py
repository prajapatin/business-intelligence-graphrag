from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system-level instruction.

        Returns:
            The generated text response.
        """
        ...

    @abstractmethod
    def extract_json(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response expected to be valid JSON.

        Args:
            prompt: The user prompt requesting JSON output.
            system_prompt: Optional system-level instruction.

        Returns:
            The generated JSON string.
        """
        ...
