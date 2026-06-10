"""Tests for the core test case generator."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from smart_testgen.core.generator import TestGenerator
from smart_testgen.core.models import TestCase, TestSuite
from smart_testgen.llm.base import LLMProvider, ParseError


# --- Fixtures ---

VALID_LLM_RESPONSE = json.dumps({
    "title": "Login Test Suite",
    "test_cases": [
        {
            "id": "TC-001",
            "title": "Valid login",
            "description": "Test successful login with correct credentials",
            "priority": "high",
            "category": "functional",
            "preconditions": ["User account exists"],
            "steps": [
                {"step_number": 1, "action": "Enter email", "expected_result": "Email accepted"},
                {"step_number": 2, "action": "Enter password", "expected_result": "Password masked"},
                {"step_number": 3, "action": "Click login", "expected_result": "Dashboard shown"},
            ],
            "expected_results": ["User logged in successfully"],
            "tags": ["login", "smoke"],
        },
        {
            "id": "TC-002",
            "title": "Invalid password",
            "description": "Test login with wrong password",
            "priority": "high",
            "category": "negative",
            "preconditions": [],
            "steps": [
                {"step_number": 1, "action": "Enter valid email", "expected_result": "OK"},
                {"step_number": 2, "action": "Enter wrong password", "expected_result": "OK"},
                {"step_number": 3, "action": "Click login", "expected_result": "Error message shown"},
            ],
            "expected_results": ["Error displayed", "User not logged in"],
            "tags": ["login", "security"],
        },
    ],
})


class MockProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self, response: str = VALID_LLM_RESPONSE):
        self._response = response
        super().__init__(api_key="mock", model="mock-v1")

    def generate(self, prompt: str) -> str:
        return self._response

    @classmethod
    def default_model(cls) -> str:
        return "mock-v1"


# --- Tests ---

class TestTestGenerator:
    def test_generate_returns_suite(self) -> None:
        gen = TestGenerator(provider=MockProvider())
        suite = gen.generate("User can log in with email and password")
        assert isinstance(suite, TestSuite)
        assert len(suite.test_cases) == 2

    def test_generate_populates_metadata(self) -> None:
        gen = TestGenerator(provider=MockProvider())
        suite = gen.generate("Login requirements", num_cases=2)
        assert suite.title == "Login Test Suite"
        assert suite.provider_used == "MockProvider"
        assert suite.model_used == "mock-v1"
        assert "2026" in suite.generated_at  # ISO format year

    def test_generate_source_truncated(self) -> None:
        long_req = "A" * 500
        gen = TestGenerator(provider=MockProvider())
        suite = gen.generate(long_req)
        assert len(suite.source_requirements) <= 200

    def test_test_case_fields(self) -> None:
        gen = TestGenerator(provider=MockProvider())
        suite = gen.generate("test")
        tc = suite.test_cases[0]
        assert tc.id == "TC-001"
        assert tc.title == "Valid login"
        assert tc.priority.value == "high"
        assert tc.category.value == "functional"
        assert len(tc.steps) == 3
        assert tc.steps[0].step_number == 1

    def test_generate_with_focus_categories(self) -> None:
        gen = TestGenerator(provider=MockProvider())
        suite = gen.generate("test", focus_categories=["functional", "negative"])
        assert len(suite.test_cases) == 2


class TestExtractJson:
    def test_raw_json(self) -> None:
        result = TestGenerator._extract_json(VALID_LLM_RESPONSE)
        data = json.loads(result)
        assert "test_cases" in data

    def test_markdown_fenced(self) -> None:
        fenced = f"```json\n{VALID_LLM_RESPONSE}\n```"
        result = TestGenerator._extract_json(fenced)
        data = json.loads(result)
        assert "test_cases" in data

    def test_fenced_with_text_around(self) -> None:
        fenced = f"Here are the test cases:\n```json\n{VALID_LLM_RESPONSE}\n```\nDone."
        result = TestGenerator._extract_json(fenced)
        data = json.loads(result)
        assert "test_cases" in data

    def test_json_with_preamble(self) -> None:
        text = f"I'll generate the test cases now.\n\n{VALID_LLM_RESPONSE}"
        result = TestGenerator._extract_json(text)
        data = json.loads(result)
        assert "test_cases" in data

    def test_no_json_raises(self) -> None:
        with pytest.raises(ParseError, match="Could not extract JSON"):
            TestGenerator._extract_json("This is just plain text with no JSON.")


class TestParseResponse:
    def test_missing_test_cases_field(self) -> None:
        gen = TestGenerator(provider=MockProvider())
        with pytest.raises(ParseError, match="missing 'test_cases'"):
            gen._parse_response('{"title": "No cases"}', "test")

    def test_invalid_test_case_data(self) -> None:
        bad = json.dumps({
            "title": "Bad",
            "test_cases": [{"id": "TC-001"}],  # missing required fields
        })
        gen = TestGenerator(provider=MockProvider())
        with pytest.raises(ParseError, match="Failed to validate"):
            gen._parse_response(bad, "test")
