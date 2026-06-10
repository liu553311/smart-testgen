"""OpenAI (GPT) LLM provider implementation."""

from __future__ import annotations

import openai

from smart_testgen.llm.base import LLMProvider, LLMProviderError
from smart_testgen.llm.factory import register_provider


@register_provider("openai")
class OpenAIProvider(LLMProvider):
    """OpenAI GPT API provider."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        max_tokens: int = 4096,
        base_url: str | None = None,
    ):
        super().__init__(api_key, model, max_tokens)
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    @classmethod
    def default_model(cls) -> str:
        return "gpt-4o"

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content or ""
        except openai.AuthenticationError as e:
            raise LLMProviderError(
                f"OpenAI authentication failed. Check your API key: {e}"
            ) from e
        except openai.APIError as e:
            raise LLMProviderError(f"OpenAI API error: {e}") from e
