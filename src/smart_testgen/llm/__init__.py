"""LLM provider module — imports trigger provider registration."""

from smart_testgen.llm.base import LLMProvider, LLMProviderError, ConfigError
from smart_testgen.llm.factory import LLMProviderFactory, register_provider

# Import providers to trigger @register_provider decorators
from smart_testgen.llm import anthropic_provider  # noqa: F401
from smart_testgen.llm import openai_provider  # noqa: F401

__all__ = [
    "LLMProvider",
    "LLMProviderError",
    "ConfigError",
    "LLMProviderFactory",
    "register_provider",
]
