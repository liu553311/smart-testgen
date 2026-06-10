"""Configuration management: env vars, .env file, and defaults."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel
from dotenv import load_dotenv


class Settings(BaseModel):
    """Application settings loaded from environment and config."""

    # LLM Provider
    llm_provider: str = "openai"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = ""
    anthropic_base_url: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    openai_model: str = "gpt-4o"
    max_tokens: int = 4096

    # Generation defaults
    default_num_cases: int = 10
    default_categories: list[str] = []

    # Export defaults
    default_export_format: str = "markdown"
    output_directory: str = "./output"

    @classmethod
    def load(cls, env_file: Path | None = None) -> "Settings":
        """Load settings with priority: env vars > .env file > defaults.

        Args:
            env_file: Path to .env file. If None, searches in cwd and parents.
        """
        if env_file:
            load_dotenv(env_file, override=True)
        else:
            load_dotenv(override=True)

        def env(key: str, default: str = "") -> str:
            return os.environ.get(f"SMARTTESTGEN_{key}", os.environ.get(key, default))

        provider = env("PROVIDER", "openai").lower()

        return cls(
            llm_provider=provider,
            anthropic_api_key=env("ANTHROPIC_API_KEY"),
            openai_api_key=env("OPENAI_API_KEY"),
            openai_base_url=env("OPENAI_BASE_URL", ""),
            anthropic_base_url=env("ANTHROPIC_BASE_URL", ""),
            anthropic_model=env("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            openai_model=env("OPENAI_MODEL", "gpt-4o"),
            max_tokens=int(env("MAX_TOKENS", "4096")),
            default_num_cases=int(env("NUM_CASES", "10")),
            default_export_format=env("FORMAT", "markdown").lower(),
            output_directory=env("OUTPUT_DIR", "./output"),
        )

    def get_api_key(self, provider: str | None = None) -> str:
        """Get the API key for the specified (or default) provider.

        Raises:
            ValueError: If no API key is configured for the provider.
        """
        prov = (provider or self.llm_provider).lower()
        if prov == "anthropic":
            key = self.anthropic_api_key
        elif prov == "openai":
            key = self.openai_api_key
        else:
            raise ValueError(f"Unknown provider: {prov}")

        if not key:
            raise ValueError(
                f"No API key configured for {prov}. "
                f"Set {'ANTHROPIC_API_KEY' if prov == 'anthropic' else 'OPENAI_API_KEY'} "
                "in your environment or .env file. "
                "Run 'smart-testgen configure' for interactive setup."
            )
        return key

    def get_model(self, provider: str | None = None) -> str:
        """Get the default model for the specified (or default) provider."""
        prov = (provider or self.llm_provider).lower()
        if prov == "anthropic":
            return self.anthropic_model
        elif prov == "openai":
            return self.openai_model
        raise ValueError(f"Unknown provider: {prov}")

    def get_base_url(self, provider: str | None = None) -> str | None:
        """Get the custom base URL for the specified (or default) provider."""
        prov = (provider or self.llm_provider).lower()
        if prov == "anthropic":
            url = self.anthropic_base_url
        elif prov == "openai":
            url = self.openai_base_url
        else:
            return None
        return url or None
