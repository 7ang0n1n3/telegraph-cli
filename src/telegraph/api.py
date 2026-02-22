"""Telegraph HTTP client."""

from __future__ import annotations

import json
from typing import Any

import httpx

BASE_URL = "https://api.telegra.ph"
_TIMEOUT = httpx.Timeout(15.0)


class APIError(Exception):
    pass


def _get(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    encoded: dict[str, str] = {}
    for k, v in (params or {}).items():
        if isinstance(v, (list, dict)):
            encoded[k] = json.dumps(v)
        else:
            encoded[k] = str(v)
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(f"{BASE_URL}/{method}", params=encoded)
        resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise APIError(data.get("error", "Unknown API error"))
    return data.get("result", {})


def _post(method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    filtered = {k: v for k, v in (payload or {}).items() if v is not None}
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.post(f"{BASE_URL}/{method}", json=filtered)
        resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise APIError(data.get("error", "Unknown API error"))
    return data.get("result", {})


# ── Account methods ─────────────────────────────────────────────────────────

def create_account(short_name: str, author_name: str = "", author_url: str = "") -> dict[str, Any]:
    return _post("createAccount", {
        "short_name": short_name,
        "author_name": author_name or None,
        "author_url": author_url or None,
    })


def get_account_info(token: str, fields: list[str] | None = None) -> dict[str, Any]:
    return _get("getAccountInfo", {
        "access_token": token,
        "fields": fields or ["short_name", "author_name", "author_url", "page_count"],
    })


def revoke_access_token(token: str) -> dict[str, Any]:
    return _post("revokeAccessToken", {"access_token": token})


# ── Page methods ─────────────────────────────────────────────────────────────

def create_page(
    token: str,
    title: str,
    content: list[dict[str, Any]],
    author_name: str | None = None,
    author_url: str | None = None,
    return_content: bool = False,
) -> dict[str, Any]:
    return _post("createPage", {
        "access_token": token,
        "title": title,
        "content": content,
        "author_name": author_name,
        "author_url": author_url,
        "return_content": return_content or None,
    })


def edit_page(
    token: str,
    path: str,
    title: str,
    content: list[dict[str, Any]],
    author_name: str | None = None,
    author_url: str | None = None,
    return_content: bool = False,
) -> dict[str, Any]:
    return _post("editPage", {
        "access_token": token,
        "path": path,
        "title": title,
        "content": content,
        "author_name": author_name,
        "author_url": author_url,
        "return_content": return_content or None,
    })


def get_page(path: str, return_content: bool = True) -> dict[str, Any]:
    return _get("getPage", {
        "path": path,
        "return_content": return_content,
    })


def get_page_list(token: str, offset: int = 0, limit: int = 50) -> dict[str, Any]:
    return _get("getPageList", {
        "access_token": token,
        "offset": offset,
        "limit": limit,
    })
