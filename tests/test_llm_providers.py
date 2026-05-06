import pytest
from unittest.mock import patch, MagicMock

from src.llm.base_provider import BaseLLMProvider
from src.llm.factory import create_llm_provider


class MockProvider(BaseLLMProvider):
    """Concrete mock for testing the abstract interface."""

    def generate(self, prompt, system_prompt=None):
        return f"Mock response to: {prompt}"

    def extract_json(self, prompt, system_prompt=None):
        return '{"entities": [], "relationships": []}'


def test_mock_provider_generate():
    provider = MockProvider()
    result = provider.generate("test")
    assert "Mock response" in result


def test_mock_provider_extract_json():
    provider = MockProvider()
    result = provider.extract_json("test")
    assert "entities" in result


@patch("src.llm.factory.settings")
def test_factory_openai(mock_settings):
    mock_settings.llm_provider = "openai"
    mock_settings.openai_api_key = "test-key"
    mock_settings.openai_model = "gpt-4o-mini"
    mock_settings.temperature = 0.3
    mock_settings.max_tokens = 1024

    with patch("src.llm.openai_provider.OpenAI"):
        provider = create_llm_provider()
        assert provider is not None


@patch("src.llm.factory.settings")
def test_factory_groq(mock_settings):
    mock_settings.llm_provider = "groq"
    mock_settings.groq_api_key = "test-key"
    mock_settings.groq_model = "llama-3.1-8b-instant"
    mock_settings.temperature = 0.3
    mock_settings.max_tokens = 1024

    with patch("src.llm.groq_provider.Groq"):
        provider = create_llm_provider()
        assert provider is not None


@patch("src.llm.factory.settings")
def test_factory_ollama(mock_settings):
    mock_settings.llm_provider = "ollama"
    mock_settings.ollama_base_url = "http://localhost:11434"
    mock_settings.ollama_model = "llama3.1"
    mock_settings.temperature = 0.3
    mock_settings.max_tokens = 1024

    provider = create_llm_provider()
    assert provider is not None


@patch("src.llm.factory.settings")
def test_factory_invalid(mock_settings):
    mock_settings.llm_provider = "nonexistent"
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        create_llm_provider()
