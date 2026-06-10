"""Abstract base class for LLM providers and exception hierarchy."""

from __future__ import annotations

from abc import ABC, abstractmethod


class SmartTestGenError(Exception):
    """Base exception for all smart-testgen errors."""


class LLMProviderError(SmartTestGenError):
    """Error communicating with an LLM provider."""


class ConfigError(SmartTestGenError):
    """Configuration error."""


class ParseError(SmartTestGenError):
    """Error parsing LLM response."""


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Subclasses must implement `generate()` and `default_model()`.
    Use `@register_provider("name")` to auto-register with the factory.
    """

    def __init__(self, api_key: str, model: str, max_tokens: int = 4096):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send a prompt to the LLM and return the raw text response."""
        ...

    @classmethod
    @abstractmethod
    def default_model(cls) -> str:
        """Return the default model identifier for this provider."""
        ...
