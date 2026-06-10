"""Tests for core Pydantic models."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from smart_testgen.core.models import (
    TestCase,
    TestCategory,
    TestPriority,
    TestStep,
    TestSuite,
)


class TestTestStep:
    def test_create_step(self) -> None:
        step = TestStep(step_number=1, action="Click button", expected_result="Page loads")
        assert step.step_number == 1
        assert step.action == "Click button"

    def test_step_serialization(self) -> None:
        step = TestStep(step_number=1, action="Test", expected_result="OK")
        data = step.model_dump()
        assert data == {"step_number": 1, "action": "Test", "expected_result": "OK"}


class TestTestCase:
    def test_create_minimal(self) -> None:
        tc = TestCase(
            id="TC-001",
            title="Test",
            description="Desc",
            priority=TestPriority.LOW,
            category=TestCategory.FUNCTIONAL,
            steps=[TestStep(step_number=1, action="Do", expected_result="Done")],
            expected_results=["Works"],
        )
        assert tc.id == "TC-001"
        assert tc.preconditions == []
        assert tc.tags == []

    def test_create_full(self, sample_test_case: TestCase) -> None:
        assert sample_test_case.id == "TC-001"
        assert len(sample_test_case.steps) == 3
        assert len(sample_test_case.preconditions) == 2
        assert sample_test_case.priority == TestPriority.HIGH

    def test_enum_serializes_as_string(self, sample_test_case: TestCase) -> None:
        data = sample_test_case.model_dump()
        assert data["priority"] == "high"
        assert data["category"] == "functional"

    def test_json_round_trip(self, sample_test_case: TestCase) -> None:
        json_str = sample_test_case.model_dump_json()
        data = json.loads(json_str)
        restored = TestCase(**data)
        assert restored == sample_test_case

    def test_invalid_priority_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TestCase(
                id="TC-001",
                title="T",
                description="D",
                priority="urgent",  # invalid
                category=TestCategory.FUNCTIONAL,
                steps=[TestStep(step_number=1, action="A", expected_result="R")],
                expected_results=["E"],
            )


class TestTestSuite:
    def test_summary(self, sample_test_suite: TestSuite) -> None:
        assert sample_test_suite.summary == {"functional": 1}

    def test_priority_summary(self, sample_test_suite: TestSuite) -> None:
        assert sample_test_suite.priority_summary == {"high": 1}

    def test_to_dict(self, sample_test_suite: TestSuite) -> None:
        d = sample_test_suite.to_dict()
        assert isinstance(d, dict)
        assert d["title"] == "Login Feature Test Suite"
        assert len(d["test_cases"]) == 1

    def test_multiple_categories_summary(self) -> None:
        suite = TestSuite(
            title="Test",
            source_requirements="Req",
            generated_at="2026-01-01T00:00:00Z",
            provider_used="test",
            model_used="test",
            test_cases=[
                TestCase(
                    id="TC-001",
                    title="F",
                    description="D",
                    priority=TestPriority.HIGH,
                    category=TestCategory.FUNCTIONAL,
                    steps=[TestStep(step_number=1, action="A", expected_result="R")],
                    expected_results=["E"],
                ),
                TestCase(
                    id="TC-002",
                    title="B",
                    description="D",
                    priority=TestPriority.MEDIUM,
                    category=TestCategory.BOUNDARY,
                    steps=[TestStep(step_number=1, action="A", expected_result="R")],
                    expected_results=["E"],
                ),
                TestCase(
                    id="TC-003",
                    title="N",
                    description="D",
                    priority=TestPriority.HIGH,
                    category=TestCategory.NEGATIVE,
                    steps=[TestStep(step_number=1, action="A", expected_result="R")],
                    expected_results=["E"],
                ),
            ],
        )
        summary = suite.summary
        assert summary["functional"] == 1
        assert summary["boundary"] == 1
        assert summary["negative"] == 1
