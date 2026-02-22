"""HTML → Telegraph nodes via BeautifulSoup."""

from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag

Node = dict[str, Any]

_HEADING_REMAP = {"h1": "h3", "h2": "h3", "h3": "h3", "h4": "h4", "h5": "h4", "h6": "h4"}

_TAG_REMAP = {
    "strong": "b",
    "em": "i",
    "b": "b",
    "i": "i",
    "u": "u",
    "s": "s",
    "del": "s",
    "code": "code",
    "pre": "pre",
    "blockquote": "blockquote",
    "p": "p",
    "br": "br",
    "hr": "hr",
    "ul": "ul",
    "ol": "ol",
    "li": "li",
    "figure": "figure",
    "figcaption": "figcaption",
    "a": "a",
    "img": "img",
}

_ATTR_ALLOWLIST: dict[str, list[str]] = {
    "a": ["href", "target"],
    "img": ["src"],
    "figure": [],
    "figcaption": [],
}

# Tags whose children we keep but whose wrapper we drop
_TRANSPARENT = {
    "div", "span", "section", "article", "header", "footer", "main",
    "nav", "aside", "html", "body",
}


def _convert_element(el: Any, strip_whitespace: bool = False) -> list[Any]:
    if isinstance(el, NavigableString):
        text = str(el)
        if strip_whitespace and not text.strip():
            return []
        return [text] if text else []

    if not isinstance(el, Tag):
        return []

    tag_name = el.name.lower()

    if tag_name in _TRANSPARENT:
        children = _convert_children(el)
        return children

    if tag_name in _HEADING_REMAP:
        new_tag = _HEADING_REMAP[tag_name]
        children = _convert_children(el)
        if not children:
            return []
        return [{"tag": new_tag, "children": children}]

    if tag_name in _TAG_REMAP:
        new_tag = _TAG_REMAP[tag_name]

        # Self-closing
        if new_tag in ("br", "hr"):
            return [{"tag": new_tag}]

        # img
        if new_tag == "img":
            src = el.get("src", "")
            if not src:
                return []
            return [{"tag": "img", "attrs": {"src": src}}]

        # Build filtered attrs
        attrs: dict[str, str] = {}
        allowed = _ATTR_ALLOWLIST.get(new_tag)
        if allowed is not None:
            for attr in allowed:
                val = el.get(attr)
                if val:
                    attrs[attr] = val
        elif new_tag == "a":
            href = el.get("href", "")
            if href:
                attrs["href"] = href
            target = el.get("target")
            if target:
                attrs["target"] = target

        children = _convert_children(el)

        node: Node = {"tag": new_tag}
        if attrs:
            node["attrs"] = attrs
        if children:
            node["children"] = children
        return [node]

    # Unknown tag — transparent fallback
    return _convert_children(el)


_STRIP_WHITESPACE_TAGS = {"ul", "ol", "table", "thead", "tbody", "tr"}


def _convert_children(el: Tag) -> list[Any]:
    strip = el.name.lower() in _STRIP_WHITESPACE_TAGS
    result = []
    for child in el.children:
        result.extend(_convert_element(child, strip_whitespace=strip))
    return result


def html_to_nodes(html: str) -> list[Node]:
    soup = BeautifulSoup(html, "html.parser")

    # Use body if present, else root
    root = soup.body if soup.body else soup

    nodes: list[Any] = []
    for child in root.children:
        converted = _convert_element(child)
        nodes.extend(converted)

    # Strip top-level whitespace-only text nodes
    result: list[Node] = []
    for n in nodes:
        if isinstance(n, str):
            if n.strip():
                result.append({"tag": "p", "children": [n]})
        else:
            result.append(n)

    return result if result else [{"tag": "p", "children": [" "]}]
