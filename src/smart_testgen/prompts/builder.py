"""Prompt builder for assembling LLM prompts from templates."""

from __future__ import annotations

from jinja2 import Template

from smart_testgen.core.models import TestCategory
from smart_testgen.prompts.templates import TEMPLATES


class PromptBuilder:
    """Builds LLM prompts from Jinja2 templates."""

    def __init__(self, template_name: str = "default"):
        if template_name not in TEMPLATES:
            available = ", ".join(TEMPLATES.keys())
            raise ValueError(
                f"Unknown template: '{template_name}'. Available: {available}"
            )
        self.template = Template(TEMPLATES[template_name])

    def build(
        self,
        requirements: str,
        num_cases: int = 10,
        focus_categories: list[str] | None = None,
    ) -> str:
        """Build a prompt from requirements.

        Args:
            requirements: The raw requirements text.
            num_cases: Number of test cases to generate.
            focus_categories: Specific categories to focus on, or None for all.

        Returns:
            The rendered prompt string ready to send to an LLM.
        """
        categories = focus_categories or [c.value for c in TestCategory]
        return self.template.render(
            requirements=requirements,
            num_cases=num_cases,
            categories=categories,
        )
