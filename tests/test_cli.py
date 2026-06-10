"""Tests for CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from smart_testgen.cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestCliGroup:
    def test_help(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "smart-testgen" in result.output

    def test_version(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output


class TestGenerateCommand:
    def test_no_args_shows_error(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["generate"])
        assert result.exit_code != 0

    def test_text_and_file_mutually_exclusive(self, runner: CliRunner, tmp_path: Path) -> None:
        f = tmp_path / "req.txt"
        f.write_text("Some requirements that are long enough", encoding="utf-8")
        result = runner.invoke(cli, ["generate", str(f), "--text", "also text"])
        assert result.exit_code != 0

    def test_generate_with_mock_llm(self, runner: CliRunner, tmp_path: Path) -> None:
        mock_response = json.dumps({
            "title": "Test",
            "test_cases": [{
                "id": "TC-001",
                "title": "Test login",
                "description": "Test login feature",
                "priority": "high",
                "category": "functional",
                "preconditions": [],
                "steps": [{"step_number": 1, "action": "Login", "expected_result": "Success"}],
                "expected_results": ["Logged in"],
                "tags": [],
            }],
        })

        with patch("smart_testgen.config.Settings.load") as mock_load, \
             patch("smart_testgen.llm.factory.LLMProviderFactory.create") as mock_create:

            mock_settings = MagicMock()
            mock_settings.llm_provider = "openai"
            mock_settings.get_api_key.return_value = "sk-test"
            mock_settings.get_model.return_value = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.default_num_cases = 10
            mock_settings.default_export_format = "json"
            mock_settings.output_directory = str(tmp_path / "output")
            mock_load.return_value = mock_settings

            mock_provider = MagicMock()
            mock_provider.generate.return_value = mock_response
            mock_provider.__class__.__name__ = "OpenAIProvider"
            mock_provider.model = "gpt-4o"
            mock_create.return_value = mock_provider

            result = runner.invoke(cli, [
                "generate", "--text", "User login with email and password for testing",
                "--format", "json",
                "--output", str(tmp_path / "test_output.json"),
            ])

            assert result.exit_code == 0, f"Output: {result.output}"
            assert (tmp_path / "test_output.json").exists()

    def test_generate_short_text_error(self, runner: CliRunner) -> None:
        with patch("smart_testgen.config.Settings.load") as mock_load:
            mock_settings = MagicMock()
            mock_settings.llm_provider = "openai"
            mock_load.return_value = mock_settings

            result = runner.invoke(cli, ["generate", "--text", "short"])
            assert result.exit_code != 0


class TestConfigureCommand:
    def test_configure_requires_provider(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["configure"])
        assert result.exit_code != 0

    def test_configure_writes_env(self, runner: CliRunner, tmp_path: Path) -> None:
        import os
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(cli, ["configure", "--provider", "openai"], input="sk-test-key\n")
            assert result.exit_code == 0, f"Output: {result.output}"
            env_content = (tmp_path / ".env").read_text(encoding="utf-8")
            assert "OPENAI_API_KEY=sk-test-key" in env_content
        finally:
            os.chdir(old_cwd)
