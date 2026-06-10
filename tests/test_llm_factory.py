"""Tests for LLM provider factory and registration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from smart_testgen.llm import LLMProvider, LLMProviderFactory
from smart_testgen.llm.base import ConfigError
from smart_testgen.llm.factory import _REGISTRY


class TestProviderRegistration:
    def test_anthropic_registered(self) -> None:
        assert "anthropic" in _REGISTRY

    def test_openai_registered(self) -> None:
        assert "openai" in _REGISTRY

    def test_available_providers(self) -> None:
        providers = LLMProviderFactory.available_providers()
        assert "anthropic" in providers
        assert "openai" in providers


class TestLLMProviderFactory:
    def test_create_openai(self) -> None:
        provider = LLMProviderFactory.create("openai", api_key="sk-test")
        assert isinstance(provider, LLMProvider)
        assert provider.model == "gpt-4o"

    def test_create_with_custom_model(self) -> None:
        provider = LLMProviderFactory.create("openai", api_key="sk-test", model="gpt-4o-mini")
        assert provider.model == "gpt-4o-mini"

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ConfigError, match="Unknown LLM provider"):
            LLMProviderFactory.create("gemini", api_key="test")

    def test_case_insensitive(self) -> None:
        provider = LLMProviderFactory.create("OpenAI", api_key="sk-test")
        assert isinstance(provider, LLMProvider)

    def test_max_tokens_passed(self) -> None:
        provider = LLMProviderFactory.create("openai", api_key="sk-test", max_tokens=8192)
        assert provider.max_tokens == 8192


class TestAnthropicProvider:
    @patch("smart_testgen.llm.anthropic_provider.anthropic.Anthropic")
    def test_generate_calls_api(self, mock_anthropic_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Test response")]
        mock_client.messages.create.return_value = mock_message

        provider = LLMProviderFactory.create("anthropic", api_key="sk-ant-test")
        result = provider.generate("Hello")

        assert result == "Test response"
        mock_client.messages.create.assert_called_once()


class TestOpenAIProvider:
    @patch("smart_testgen.llm.openai_provider.openai.OpenAI")
    def test_generate_calls_api(self, mock_openai_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="GPT response"))]
        mock_client.chat.completions.create.return_value = mock_response

        provider = LLMProviderFactory.create("openai", api_key="sk-test")
        result = provider.generate("Hello")

        assert result == "GPT response"
        mock_client.chat.completions.create.assert_called_once()

    def test_default_model(self) -> None:
        from smart_testgen.llm.openai_provider import OpenAIProvider

        assert OpenAIProvider.default_model() == "gpt-4o"
