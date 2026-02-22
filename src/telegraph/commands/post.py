"""Post command — create a new Telegraph page."""

from __future__ import annotations

import sys
from typing import Any

import click
import yaml

from telegraph import api, config, output
from telegraph.convert import convert, detect_format


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from text. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    _, raw_yaml, body = parts
    try:
        meta = yaml.safe_load(raw_yaml) or {}
        if not isinstance(meta, dict):
            return {}, text
    except yaml.YAMLError:
        return {}, text

    return meta, body.lstrip("\n")


def _read_input(file_arg: str) -> tuple[str, str | None]:
    """Read content from file path or '-' for stdin. Returns (content, filepath)."""
    if file_arg == "-":
        return sys.stdin.read(), None
    try:
        with open(file_arg, "r", encoding="utf-8") as f:
            return f.read(), file_arg
    except OSError as e:
        output.print_error(str(e))
        raise SystemExit(1)


@click.command("post")
@click.argument("file", default="-")
@click.option("-t", "--title", default=None, help="Page title.")
@click.option("-a", "--author", default=None, help="Author name override.")
@click.option("--format", "fmt", default=None, type=click.Choice(["markdown", "html"]), help="Input format.")
def post_cmd(file: str, title: str | None, author: str | None, fmt: str | None) -> None:
    """Create a new Telegraph page from FILE (use - for stdin)."""
    try:
        token = config.require_token()
    except config.ConfigError as e:
        output.print_error(str(e))
        raise SystemExit(1)

    text, filepath = _read_input(file)
    meta, body = _parse_frontmatter(text)

    resolved_title = title or meta.get("title") or ""
    resolved_author = author or meta.get("author") or None

    if not resolved_title:
        raise click.UsageError("Title is required. Use -t/--title or add `title:` to frontmatter.")

    fmt_resolved = detect_format(filepath, fmt)
    try:
        nodes = convert(body, fmt_resolved)
    except Exception as e:
        output.print_error(f"Content conversion failed: {e}")
        raise SystemExit(1)

    cfg = config.get_config()
    fallback_author = cfg.get("author_name")
    resolved_author = resolved_author or fallback_author or None

    try:
        result = api.create_page(
            token=token,
            title=resolved_title,
            content=nodes,
            author_name=resolved_author,
        )
        url = result.get("url", "")
        output.print_success(url, resolved_title)
        click.echo(result.get("path", ""))
    except api.APIError as e:
        output.print_error(str(e))
        raise SystemExit(1)
