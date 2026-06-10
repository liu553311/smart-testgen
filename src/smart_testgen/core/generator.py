"""Core test case generator — orchestrates prompt building, LLM call, and parsing."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from smart_testgen.core.models import TestCase, TestSuite
from smart_testgen.llm.base import LLMProvider, ParseError
from smart_testgen.prompts.builder import PromptBuilder


class TestGenerator:
    """Generates test cases by sending requirements to an LLM."""

    def __init__(self, provider: LLMProvider, prompt_builder: PromptBuilder | None = None):
        self.provider = provider
        self.prompt_builder = prompt_builder or PromptBuilder()

    def generate(
        self,
        requirements: str,
        num_cases: int = 10,
        focus_categories: list[str] | None = None,
    ) -> TestSuite:
        """Generate test cases from requirements text.

        Args:
            requirements: Raw requirements text.
            num_cases: Number of test cases to generate.
            focus_categories: Specific test categories to focus on.

        Returns:
            A populated TestSuite.
        """
        prompt = self.prompt_builder.build(
            requirements=requirements,
            num_cases=num_cases,
            focus_categories=focus_categories,
        )
        raw_response = self.provider.generate(prompt)
        return self._parse_response(raw_response, requirements)

    def _parse_response(self, raw: str, requirements: str) -> TestSuite:
        """Parse LLM JSON response into a TestSuite."""
        json_str = self._extract_json(raw)
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ParseError(f"Failed to parse LLM response as JSON: {e}") from e

        if "test_cases" not in data:
            raise ParseError("LLM response missing 'test_cases' field")

        try:
            test_cases = [TestCase(**tc) for tc in data["test_cases"]]
        except Exception as e:
            raise ParseError(f"Failed to validate test cases: {e}") from e

        return TestSuite(
            title=data.get("title", "Generated Test Suite"),
            source_requirements=requirements[:200],
            generated_at=datetime.now(timezone.utc).isoformat(),
            provider_used=self.provider.__class__.__name__,
            model_used=self.provider.model,
            test_cases=test_cases,
        )

    @staticmethod
    def _extract_json(raw: str) -> str:
        """Extract JSON from LLM response, handling markdown fences and extra text."""
        # Try to find JSON in markdown code fences first
        fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
        if fence_match:
            return fence_match.group(1).strip()

        # Find the first { and last } to extract the JSON object
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return raw[start : end + 1]

        raise ParseError(
            "Could not extract JSON from LLM response. "
            f"Response starts with: {raw[:100]!r}"
        )
