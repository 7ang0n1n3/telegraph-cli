"""Config management — ~/.config/telegraph/config.json."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "telegraph"
CONFIG_FILE = CONFIG_DIR / "config.json"


class ConfigError(Exception):
    pass


def _load() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))
    CONFIG_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600


def get_config() -> dict[str, Any]:
    return _load()


def require_token() -> str:
    cfg = _load()
    token = cfg.get("access_token")
    if not token:
        raise ConfigError(
            "No access token found. Run `telegraph account create` first."
        )
    return token


def save_account(result: dict[str, Any]) -> None:
    cfg = _load()
    cfg.update(result)
    _save(cfg)


def clear_token() -> None:
    cfg = _load()
    cfg.pop("access_token", None)
    _save(cfg)
