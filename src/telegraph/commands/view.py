"""View command — display a Telegraph page in the terminal."""

from __future__ import annotations

from typing import Any

import click

from telegraph import api, output


def _nodes_to_text(nodes: list[Any], indent: int = 0) -> list[tuple[str, str]]:
    """
    Convert Telegraph nodes to a list of (rich_markup, raw_text) lines.
    Returns list of (markup_line,) strings for rich printing.
    """
    lines = []
    for node in nodes:
        if isinstance(node, str):
            lines.append(node)
            continue
        if not isinstance(node, dict):
            continue

        tag = node.get("tag", "")
        children = node.get("children", [])
        attrs = node.get("attrs", {})

        if tag in ("h3", "h4"):
            text = _inline_text(children)
            style = "bold cyan" if tag == "h3" else "bold blue"
            lines.append(f"[{style}]{text}[/{style}]")
            lines.append("")

        elif tag == "p":
            lines.append(_inline_text(children))
            lines.append("")

        elif tag == "blockquote":
            for child in children:
                inner = _inline_text([child]) if isinstance(child, dict) else str(child)
                lines.append(f"[dim]▌ {inner}[/dim]")
            lines.append("")

        elif tag == "pre":
            code_nodes = children
            raw = ""
            if code_nodes and isinstance(code_nodes[0], dict) and code_nodes[0].get("tag") == "code":
                raw = "".join(str(c) for c in code_nodes[0].get("children", []) if isinstance(c, str))
            else:
                raw = "".join(str(c) for c in code_nodes if isinstance(c, str))
            for code_line in raw.rstrip("\n").split("\n"):
                lines.append(f"[dim]  {code_line}[/dim]")
            lines.append("")

        elif tag in ("ul", "ol"):
            for i, item in enumerate(children):
                if not isinstance(item, dict) or item.get("tag") != "li":
                    continue
                bullet = f"{i + 1}." if tag == "ol" else "•"
                text = _inline_text(item.get("children", []))
                lines.append(f"  {bullet} {text}")
            lines.append("")

        elif tag == "figure":
            src = ""
            caption = ""
            for child in children:
                if not isinstance(child, dict):
                    continue
                if child.get("tag") == "img":
                    src = child.get("attrs", {}).get("src", "")
                elif child.get("tag") == "figcaption":
                    caption = _inline_text(child.get("children", []))
            if src:
                lines.append(f"[dim][image: {src}][/dim]")
            if caption:
                lines.append(f"[dim]  {caption}[/dim]")
            lines.append("")

        elif tag == "hr":
            lines.append("[dim]" + "─" * 40 + "[/dim]")
            lines.append("")

        elif tag == "br":
            lines.append("")

        else:
            text = _inline_text(children)
            if text:
                lines.append(text)

    return lines


def _inline_text(nodes: list[Any]) -> str:
    """Recursively render inline nodes to a rich markup string."""
    parts = []
    for node in nodes:
        if isinstance(node, str):
            parts.append(node)
            continue
        if not isinstance(node, dict):
            continue
        tag = node.get("tag", "")
        children = node.get("children", [])
        attrs = node.get("attrs", {})
        inner = _inline_text(children)

        if tag == "b":
            parts.append(f"[bold]{inner}[/bold]")
        elif tag == "i":
            parts.append(f"[italic]{inner}[/italic]")
        elif tag == "u":
            parts.append(f"[underline]{inner}[/underline]")
        elif tag == "s":
            parts.append(f"[strike]{inner}[/strike]")
        elif tag == "code":
            raw = "".join(str(c) for c in children if isinstance(c, str))
            parts.append(f"[bold dim]{raw}[/bold dim]")
        elif tag == "a":
            href = attrs.get("href", "")
            parts.append(f"[cyan][link={href}]{inner}[/link][/cyan]")
        elif tag == "br":
            parts.append("\n")
        else:
            parts.append(inner)
    return "".join(parts)


@click.command("view")
@click.argument("path")
def view_cmd(path: str) -> None:
    """Display a Telegraph page in the terminal."""
    from rich.console import Console
    from rich.rule import Rule

    console = Console()

    try:
        page = api.get_page(path, return_content=True)
    except api.APIError as e:
        output.print_error(str(e))
        raise SystemExit(1)

    title = page.get("title", "")
    author = page.get("author_name", "")
    url = page.get("url", f"https://telegra.ph/{path}")
    views = page.get("views", 0)
    content = page.get("content", [])

    # Header
    console.print()
    console.print(f"[bold]{title}[/bold]")
    meta_parts = []
    if author:
        meta_parts.append(f"[dim]{author}[/dim]")
    meta_parts.append(f"[dim]{views} views[/dim]")
    meta_parts.append(f"[cyan][link={url}]{url}[/link][/cyan]")
    console.print("  ".join(meta_parts))
    console.print(Rule(style="dim"))
    console.print()

    # Body
    lines = _nodes_to_text(content)
    for line in lines:
        console.print(line)
