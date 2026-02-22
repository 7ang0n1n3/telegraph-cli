"""Telegraph CLI entry point."""

from __future__ import annotations

import click

from telegraph.commands.account import account_cmd
from telegraph.commands.post import post_cmd
from telegraph.commands.edit import edit_cmd
from telegraph.commands.list_ import list_cmd
from telegraph.commands.view import view_cmd


@click.group()
@click.version_option(package_name="telegraph")
def main() -> None:
    """Post content to telegra.ph from the command line."""


main.add_command(account_cmd)
main.add_command(post_cmd)
main.add_command(edit_cmd)
main.add_command(list_cmd)
main.add_command(view_cmd)
