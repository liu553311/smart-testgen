"""Abstract base class for exporters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from smart_testgen.core.models import TestSuite


class BaseExporter(ABC):
    """Abstract base for test suite exporters."""

    @abstractmethod
    def export(self, test_suite: TestSuite, output_path: Path) -> Path:
        """Export a test suite to the target format.

        Args:
            test_suite: The test suite to export.
            output_path: Destination file path.

        Returns:
            The actual path the file was written to.
        """
        ...
