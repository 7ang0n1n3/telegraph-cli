"""Edit command — update an existing Telegraph page."""

from __future__ import annotations

import click

from telegraph import api, config, output
from telegraph.convert import convert, detect_format
from telegraph.commands.post import _parse_frontmatter, _read_input


@click.command("edit")
@click.argument("path")
@click.argument("file", default="-")
@click.option("-t", "--title", default=None, help="Page title.")
@click.option("-a", "--author", default=None, help="Author name override.")
@click.option("--format", "fmt", default=None, type=click.Choice(["markdown", "html"]), help="Input format.")
def edit_cmd(path: str, file: str, title: str | None, author: str | None, fmt: str | None) -> None:
    """Update an existing Telegraph page at PATH from FILE (use - for stdin)."""
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
        result = api.edit_page(
            token=token,
            path=path,
            title=resolved_title,
            content=nodes,
            author_name=resolved_author,
        )
        url = result.get("url", "")
        output.print_success(url, resolved_title)
    except api.APIError as e:
        output.print_error(str(e))
        raise SystemExit(1)
