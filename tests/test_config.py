"""Tests for configuration management."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from smart_testgen.config import Settings


class TestSettings:
    def test_defaults(self) -> None:
        s = Settings()
        assert s.llm_provider == "openai"
        assert s.default_num_cases == 10
        assert s.default_export_format == "markdown"
        assert s.max_tokens == 4096

    def test_get_api_key_missing(self) -> None:
        s = Settings(openai_api_key="")
        with pytest.raises(ValueError, match="No API key configured"):
            s.get_api_key("openai")

    def test_get_api_key_present(self) -> None:
        s = Settings(openai_api_key="sk-test-123")
        assert s.get_api_key("openai") == "sk-test-123"

    def test_get_api_key_anthropic(self) -> None:
        s = Settings(anthropic_api_key="sk-ant-test")
        assert s.get_api_key("anthropic") == "sk-ant-test"

    def test_get_api_key_unknown_provider(self) -> None:
        s = Settings()
        with pytest.raises(ValueError, match="Unknown provider"):
            s.get_api_key("gemini")

    def test_get_model_openai(self) -> None:
        s = Settings()
        assert s.get_model("openai") == "gpt-4o"

    def test_get_model_anthropic(self) -> None:
        s = Settings()
        assert s.get_model("anthropic") == "claude-sonnet-4-20250514"

    def test_load_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env-test")
        monkeypatch.setenv("SMARTTESTGEN_PROVIDER", "openai")
        monkeypatch.setenv("SMARTTESTGEN_NUM_CASES", "20")
        s = Settings.load()
        assert s.openai_api_key == "sk-env-test"
        assert s.default_num_cases == 20

    def test_load_from_dotenv(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "OPENAI_API_KEY=sk-dotenv-test\nSMARTTESTGEN_FORMAT=json\n",
            encoding="utf-8",
        )
        s = Settings.load(env_file=env_file)
        assert s.openai_api_key == "sk-dotenv-test"
        assert s.default_export_format == "json"
