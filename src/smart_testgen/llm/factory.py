"""LLM provider factory with decorator-based registration."""

from __future__ import annotations

from smart_testgen.llm.base import ConfigError, LLMProvider

# Global provider registry
_REGISTRY: dict[str, type[LLMProvider]] = {}


def register_provider(name: str):
    """Decorator to register an LLM provider class.

    Usage:
        @register_provider("openai")
        class OpenAIProvider(LLMProvider):
            ...
    """
    def decorator(cls: type[LLMProvider]) -> type[LLMProvider]:
        _REGISTRY[name.lower()] = cls
        return cls
    return decorator


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    @staticmethod
    def create(
        provider: str,
        api_key: str,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> LLMProvider:
        """Create an LLM provider instance.

        Args:
            provider: Provider name (e.g., "anthropic", "openai").
            api_key: API key for the provider.
            model: Model identifier. Uses provider default if None.
            max_tokens: Maximum tokens for generation.

        Returns:
            Configured LLMProvider instance.

        Raises:
            ConfigError: If provider is unknown or not registered.
        """
        provider_lower = provider.lower()
        if provider_lower not in _REGISTRY:
            available = ", ".join(sorted(_REGISTRY.keys()))
            raise ConfigError(
                f"Unknown LLM provider: '{provider}'. "
                f"Available providers: {available or 'none registered'}"
            )

        cls = _REGISTRY[provider_lower]
        resolved_model = model or cls.default_model()
        return cls(api_key=api_key, model=resolved_model, max_tokens=max_tokens)

    @staticmethod
    def available_providers() -> list[str]:
        """Return list of registered provider names."""
        return sorted(_REGISTRY.keys())
