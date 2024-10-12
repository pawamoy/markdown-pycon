"""Tests for the extension."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from markdown import Markdown


def test_rendering_pycon_code_blocks(md: Markdown) -> None:
    """Assert pycon code blocks are rendered.

    Parameters:
        md: A Markdown instance (fixture).
    """
    html = md.convert(">>> 1 + 1\n2\n")
    assert "highlight" in html
