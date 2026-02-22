"""List pages command."""

from __future__ import annotations

import click

from telegraph import api, config, output


@click.command("list")
@click.option("--limit", default=50, show_default=True, help="Max number of pages to return.")
@click.option("--offset", default=0, show_default=True, help="Pagination offset.")
def list_cmd(limit: int, offset: int) -> None:
    """List pages for the current account."""
    try:
        token = config.require_token()
        result = api.get_page_list(token, offset=offset, limit=limit)
        pages = result.get("pages", [])
        total = result.get("total_count", len(pages))
        output.print_page_list(pages, total)
    except config.ConfigError as e:
        output.print_error(str(e))
        raise SystemExit(1)
    except api.APIError as e:
        output.print_error(str(e))
        raise SystemExit(1)
