"""Anthropic (Claude) LLM provider implementation."""

from __future__ import annotations

import anthropic

from smart_testgen.llm.base import LLMProvider, LLMProviderError
from smart_testgen.llm.factory import register_provider


@register_provider("anthropic")
class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
    ):
        super().__init__(api_key, model, max_tokens)
        self.client = anthropic.Anthropic(api_key=api_key)

    @classmethod
    def default_model(cls) -> str:
        return "claude-sonnet-4-20250514"

    def generate(self, prompt: str) -> str:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except anthropic.AuthenticationError as e:
            raise LLMProviderError(
                f"Anthropic authentication failed. Check your API key: {e}"
            ) from e
        except anthropic.APIError as e:
            raise LLMProviderError(f"Anthropic API error: {e}") from e
