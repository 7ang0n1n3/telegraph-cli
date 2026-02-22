"""Format auto-detection and dispatch."""

from __future__ import annotations

import os
from typing import Any


def detect_format(filepath: str | None, fmt: str | None) -> str:
    """Return 'html' or 'markdown' based on flag > extension > default."""
    if fmt:
        return fmt.lower()
    if filepath and filepath != "-":
        _, ext = os.path.splitext(filepath)
        if ext.lower() in (".html", ".htm"):
            return "html"
    return "markdown"


def convert(text: str, fmt: str) -> list[dict[str, Any]]:
    """Convert text in the given format to Telegraph node list."""
    if fmt == "html":
        from telegraph.convert.html import html_to_nodes
        return html_to_nodes(text)
    else:
        from telegraph.convert.markdown import markdown_to_nodes
        return markdown_to_nodes(text)
