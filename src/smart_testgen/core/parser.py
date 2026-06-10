"""Input parser for reading requirements from files or raw text."""

from __future__ import annotations

from pathlib import Path


class ParseError(Exception):
    """Raised when input cannot be read or is invalid."""


def read_requirements(source: str | Path) -> str:
    """Read requirements from a file path or raw string.

    Args:
        source: A file path (.txt, .md) or raw requirements text.

    Returns:
        Cleaned requirements text.

    Raises:
        ParseError: If the file doesn't exist, is empty, or can't be read.
    """
    source_str = str(source).strip()

    if not source_str:
        raise ParseError("Input source cannot be empty")

    path = Path(source_str)

    if path.exists() and path.is_file():
        return _read_file(path)

    # Treat as raw text
    text = source_str
    if len(text) < 10:
        raise ParseError(
            f"Requirements text is too short ({len(text)} chars). "
            "Please provide at least 10 characters of requirements."
        )
    return text


def _read_file(path: Path) -> str:
    """Read and validate a requirements file."""
    suffix = path.suffix.lower()
    if suffix not in (".txt", ".md", ".markdown"):
        raise ParseError(
            f"Unsupported file type: {suffix}. "
            "Please use .txt, .md, or .markdown files."
        )

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = path.read_text(encoding="gbk")
        except Exception as e:
            raise ParseError(f"Cannot read file {path}: encoding error: {e}") from e
    except OSError as e:
        raise ParseError(f"Cannot read file {path}: {e}") from e

    text = text.strip()
    if not text:
        raise ParseError(f"File is empty: {path}")

    return text
