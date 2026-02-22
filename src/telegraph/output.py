"""Rich terminal output helpers."""

from __future__ import annotations

import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table, box
from rich import print as rprint

_out = Console()
_err = Console(stderr=True)


def print_success(url: str, title: str) -> None:
    panel = Panel(
        f"[bold]{title}[/bold]\n[link={url}]{url}[/link]",
        title="[green]Published[/green]",
        border_style="green",
        expand=False,
    )
    _out.print(panel)


def print_account_info(info: dict[str, Any]) -> None:
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")
    for key, val in info.items():
        table.add_row(key.replace("_", " ").title(), str(val))
    _out.print(table)


def print_page_list(pages: list[dict[str, Any]], total: int) -> None:
    table = Table(
        title=f"Pages ({total} total)",
        box=box.ROUNDED,
        show_lines=False,
    )
    table.add_column("Title", style="bold")
    table.add_column("URL", style="cyan")
    table.add_column("Views", justify="right", style="green")
    for page in pages:
        url = f"https://telegra.ph/{page.get('path', '')}"
        table.add_row(
            page.get("title", ""),
            f"[link={url}]{url}[/link]",
            str(page.get("views", 0)),
        )
    _out.print(table)


def print_error(message: str) -> None:
    _err.print(f"[bold red]Error:[/bold red] {message}")
