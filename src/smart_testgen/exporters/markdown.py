"""Markdown table exporter."""

from __future__ import annotations

from pathlib import Path

from smart_testgen.core.models import TestSuite
from smart_testgen.exporters.base import BaseExporter


class MarkdownExporter(BaseExporter):
    """Export test cases as a Markdown document with tables."""

    def export(self, test_suite: TestSuite, output_path: Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []
        lines.append(f"# {test_suite.title}")
        lines.append("")
        lines.append(f"**Generated at:** {test_suite.generated_at}")
        lines.append(f"**Provider:** {test_suite.provider_used} ({test_suite.model_used})")
        lines.append(f"**Source:** {test_suite.source_requirements}...")
        lines.append(f"**Total test cases:** {len(test_suite.test_cases)}")
        lines.append("")

        # Summary tables
        if test_suite.summary:
            lines.append("## Summary by Category")
            lines.append("")
            lines.append("| Category | Count |")
            lines.append("|----------|-------|")
            for cat, count in sorted(test_suite.summary.items()):
                lines.append(f"| {cat} | {count} |")
            lines.append("")

        if test_suite.priority_summary:
            lines.append("## Summary by Priority")
            lines.append("")
            lines.append("| Priority | Count |")
            lines.append("|----------|-------|")
            for pri, count in sorted(test_suite.priority_summary.items()):
                lines.append(f"| {pri} | {count} |")
            lines.append("")

        # Detailed test cases
        lines.append("## Test Cases")
        lines.append("")

        for tc in test_suite.test_cases:
            lines.append(f"### {tc.id}: {tc.title}")
            lines.append("")
            lines.append(f"**Priority:** {tc.priority.value} | **Category:** {tc.category.value}")
            lines.append("")
            lines.append(f"**Description:** {tc.description}")
            lines.append("")

            if tc.preconditions:
                lines.append("**Preconditions:**")
                for pre in tc.preconditions:
                    lines.append(f"- {pre}")
                lines.append("")

            lines.append("**Steps:**")
            lines.append("")
            lines.append("| # | Action | Expected Result |")
            lines.append("|---|--------|-----------------|")
            for step in tc.steps:
                lines.append(
                    f"| {step.step_number} | {step.action} | {step.expected_result} |"
                )
            lines.append("")

            if tc.expected_results:
                lines.append("**Expected Results:**")
                for er in tc.expected_results:
                    lines.append(f"- {er}")
                lines.append("")

            if tc.tags:
                lines.append(f"**Tags:** {', '.join(tc.tags)}")
                lines.append("")

            lines.append("---")
            lines.append("")

        content = "\n".join(lines)
        output_path.write_text(content, encoding="utf-8")
        return output_path
