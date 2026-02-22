"""Account management commands."""

from __future__ import annotations

import click

from telegraph import api, config, output


@click.group("account")
def account_cmd() -> None:
    """Manage your Telegraph account."""


@account_cmd.command("create")
def create() -> None:
    """Create a new Telegraph account and save the token."""
    short_name = click.prompt("Short name (display name for your account)")
    author_name = click.prompt("Author name (optional, press Enter to skip)", default="")
    try:
        result = api.create_account(short_name, author_name)
        config.save_account(result)
        click.echo(f"Account created. Token saved to {config.CONFIG_FILE}")
        output.print_account_info({
            k: result[k] for k in ("short_name", "author_name", "access_token") if k in result
        })
    except api.APIError as e:
        output.print_error(str(e))
        raise SystemExit(1)


@account_cmd.command("info")
def info() -> None:
    """Show current account details."""
    try:
        token = config.require_token()
        result = api.get_account_info(token)
        output.print_account_info(result)
    except config.ConfigError as e:
        output.print_error(str(e))
        raise SystemExit(1)
    except api.APIError as e:
        output.print_error(str(e))
        raise SystemExit(1)


@account_cmd.command("revoke")
def revoke() -> None:
    """Revoke the current access token."""
    try:
        token = config.require_token()
    except config.ConfigError as e:
        output.print_error(str(e))
        raise SystemExit(1)

    click.confirm(
        "Are you sure you want to revoke your access token? This cannot be undone.",
        abort=True,
    )
    try:
        result = api.revoke_access_token(token)
        new_token = result.get("access_token")
        if new_token:
            config.save_account({"access_token": new_token})
            click.echo("Token revoked. A new token has been saved automatically.")
        else:
            config.clear_token()
            click.echo("Token revoked and removed from config.")
    except api.APIError as e:
        output.print_error(str(e))
        raise SystemExit(1)
