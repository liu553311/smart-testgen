"""Shared test fixtures for smart-testgen tests."""

from __future__ import annotations

import pytest

from smart_testgen.core.models import (
    TestCase,
    TestCategory,
    TestPriority,
    TestStep,
    TestSuite,
)


@pytest.fixture
def sample_step() -> TestStep:
    """A single test step."""
    return TestStep(step_number=1, action="Navigate to login page", expected_result="Login form is displayed")


@pytest.fixture
def sample_test_case() -> TestCase:
    """A fully populated test case."""
    return TestCase(
        id="TC-001",
        title="Valid login with correct credentials",
        description="Verify that a registered user can log in with valid email and password",
        priority=TestPriority.HIGH,
        category=TestCategory.FUNCTIONAL,
        preconditions=["User account exists", "User is on login page"],
        steps=[
            TestStep(step_number=1, action="Enter valid email", expected_result="Email field accepts input"),
            TestStep(step_number=2, action="Enter valid password", expected_result="Password field masks input"),
            TestStep(step_number=3, action="Click Login button", expected_result="User is redirected to dashboard"),
        ],
        expected_results=["User is logged in", "Dashboard is displayed with user name"],
        tags=["login", "smoke"],
    )


@pytest.fixture
def sample_test_suite(sample_test_case: TestCase) -> TestSuite:
    """A test suite with one test case."""
    return TestSuite(
        title="Login Feature Test Suite",
        source_requirements="The system shall allow registered users to log in using email and password.",
        generated_at="2026-06-10T12:00:00+00:00",
        provider_used="openai",
        model_used="gpt-4o",
        test_cases=[sample_test_case],
    )
