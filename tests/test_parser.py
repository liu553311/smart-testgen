"""Tests for input parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from smart_testgen.core.parser import ParseError, read_requirements


class TestReadRequirements:
    def test_raw_text(self) -> None:
        result = read_requirements("User can log in with email and password")
        assert "log in" in result

    def test_too_short_text(self) -> None:
        with pytest.raises(ParseError, match="too short"):
            read_requirements("short")

    def test_empty_string(self) -> None:
        with pytest.raises(ParseError, match="cannot be empty"):
            read_requirements("")

    def test_whitespace_only(self) -> None:
        with pytest.raises(ParseError, match="cannot be empty"):
            read_requirements("   ")

    def test_read_txt_file(self, tmp_path: Path) -> None:
        f = tmp_path / "req.txt"
        f.write_text("The system shall support user login.", encoding="utf-8")
        result = read_requirements(f)
        assert "user login" in result

    def test_read_md_file(self, tmp_path: Path) -> None:
        f = tmp_path / "req.md"
        f.write_text("# Requirements\n\nUser must register.", encoding="utf-8")
        result = read_requirements(f)
        assert "register" in result

    def test_unsupported_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "req.pdf"
        f.write_bytes(b"some content")
        with pytest.raises(ParseError, match="Unsupported file type"):
            read_requirements(f)

    def test_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        with pytest.raises(ParseError, match="empty"):
            read_requirements(f)

    def test_nonexistent_path_treated_as_text(self) -> None:
        result = read_requirements("nonexistent/path.txt that is long enough to pass")
        assert "nonexistent" in result

    def test_strips_whitespace(self, tmp_path: Path) -> None:
        f = tmp_path / "req.txt"
        f.write_text("  \n  Requirements here  \n  ", encoding="utf-8")
        result = read_requirements(f)
        assert result == "Requirements here"
