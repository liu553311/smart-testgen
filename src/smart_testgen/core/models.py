"""Pydantic data models for test cases and test suites."""

from __future__ import annotations

from collections import Counter
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TestPriority(str, Enum):
    """Test case priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestCategory(str, Enum):
    """Test case categories/types."""

    FUNCTIONAL = "functional"
    BOUNDARY = "boundary"
    NEGATIVE = "negative"
    EDGE_CASE = "edge_case"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    ACCESSIBILITY = "accessibility"


class TestStep(BaseModel):
    """A single step within a test case."""

    step_number: int = Field(description="Step sequence number starting from 1")
    action: str = Field(description="Action to perform")
    expected_result: str = Field(description="Expected result after this step")


class TestCase(BaseModel):
    """A single test case with all details."""

    id: str = Field(description="Unique ID, e.g. TC-001")
    title: str = Field(description="Short descriptive title")
    description: str = Field(description="Detailed description of what is tested")
    priority: TestPriority
    category: TestCategory
    preconditions: list[str] = Field(
        default_factory=list,
        description="Prerequisites that must be met before execution",
    )
    steps: list[TestStep] = Field(description="Ordered test steps")
    expected_results: list[str] = Field(
        description="Overall expected outcomes after all steps",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Free-form tags for filtering/grouping",
    )


class TestSuite(BaseModel):
    """A complete set of generated test cases."""

    title: str = Field(description="Suite title derived from requirements")
    source_requirements: str = Field(
        description="First 200 chars of input for traceability",
        max_length=200,
    )
    generated_at: str = Field(description="ISO 8601 timestamp")
    provider_used: str = Field(description="LLM provider name")
    model_used: str = Field(description="LLM model identifier")
    test_cases: list[TestCase]

    @property
    def summary(self) -> dict[str, int]:
        """Count of test cases by category."""
        return dict(Counter(tc.category.value for tc in self.test_cases))

    @property
    def priority_summary(self) -> dict[str, int]:
        """Count of test cases by priority."""
        return dict(Counter(tc.priority.value for tc in self.test_cases))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict (for JSON export)."""
        return self.model_dump(mode="json")
