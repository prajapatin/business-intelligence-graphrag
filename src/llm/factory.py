from src.llm.base_provider import BaseLLMProvider
from config.settings import settings


def create_llm_provider() -> BaseLLMProvider:
    """Create an LLM provider based on the configured settings."""
    provider = settings.llm_provider

    if provider == "openai":
        from src.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif provider == "groq":
        from src.llm.groq_provider import GroqProvider
        return GroqProvider()
    elif provider == "ollama":
        from src.llm.ollama_provider import OllamaProvider
        return OllamaProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Choose from: openai, groq, ollama")
