"""JSON exporter."""

from __future__ import annotations

import json
from pathlib import Path

from smart_testgen.core.models import TestSuite
from smart_testgen.exporters.base import BaseExporter


class JsonExporter(BaseExporter):
    """Export test cases as formatted JSON."""

    def export(self, test_suite: TestSuite, output_path: Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = test_suite.model_dump_json(indent=2)
        output_path.write_text(content, encoding="utf-8")
        return output_path
