"""Markdown → Telegraph nodes via mistune 3.x AST mode."""

from __future__ import annotations

from typing import Any

import mistune

# Singleton parser in AST mode
_parse = mistune.create_markdown(renderer=None)

_HEADING_REMAP = {1: "h3", 2: "h3", 3: "h3", 4: "h4", 5: "h4", 6: "h4"}

Node = dict[str, Any]


def _children(nodes: list[Any] | None) -> list[Any]:
    if not nodes:
        return []
    result = []
    for n in nodes:
        converted = _convert_node(n)
        if converted is None:
            continue
        if isinstance(converted, list):
            result.extend(converted)
        else:
            result.append(converted)
    return result


def _convert_node(node: Any) -> Any:
    if isinstance(node, str):
        return node

    if not isinstance(node, dict):
        return None

    t = node.get("type", "")
    children = node.get("children")
    attrs = node.get("attrs", {})

    if t == "paragraph":
        inner = _children(children)
        if not inner:
            return None
        return {"tag": "p", "children": inner}

    if t == "block_text":
        # tight list item content — return inline content directly (no wrapping)
        return _children(children)

    if t == "heading":
        level = attrs.get("level", 3)
        if isinstance(level, str):
            level = int(level)
        tag = _HEADING_REMAP.get(level, "h3")
        inner = _children(children)
        return {"tag": tag, "children": inner} if inner else None

    if t == "strong":
        inner = _children(children)
        return {"tag": "b", "children": inner} if inner else None

    if t == "emphasis":
        inner = _children(children)
        return {"tag": "i", "children": inner} if inner else None

    if t == "codespan":
        raw = node.get("raw", "")
        return {"tag": "code", "children": [raw]} if raw else None

    if t == "block_code":
        raw = node.get("raw", "")
        return {"tag": "pre", "children": [{"tag": "code", "children": [raw]}]}

    if t == "link":
        href = attrs.get("url", attrs.get("href", ""))
        inner = _children(children)
        node_out: Node = {"tag": "a"}
        if href:
            node_out["attrs"] = {"href": href}
        if inner:
            node_out["children"] = inner
        return node_out

    if t == "image":
        src = attrs.get("url", attrs.get("src", ""))
        # alt text is in children as text nodes
        alt_parts = _children(children)
        alt = "".join(str(p) for p in alt_parts if isinstance(p, str))
        fig_children: list[Any] = [{"tag": "img", "attrs": {"src": src}}]
        if alt:
            fig_children.append({"tag": "figcaption", "children": [alt]})
        return {"tag": "figure", "children": fig_children}

    if t == "list":
        ordered = attrs.get("ordered", False)
        tag = "ol" if ordered else "ul"
        inner = _children(children)
        return {"tag": tag, "children": inner} if inner else None

    if t == "list_item":
        inner = _children(children)
        # block_text returns a list; flatten one level
        flat: list[Any] = []
        for item in inner:
            if isinstance(item, list):
                flat.extend(item)
            else:
                flat.append(item)
        return {"tag": "li", "children": flat} if flat else None

    if t in ("blockquote", "block_quote"):
        inner = _children(children)
        return {"tag": "blockquote", "children": inner} if inner else None

    if t == "thematic_break":
        return {"tag": "hr"}

    if t in ("softbreak", "linebreak"):
        return {"tag": "br"}

    if t == "text":
        raw = node.get("raw", "")
        if children:
            return _children(children)
        return raw if raw else None

    if t == "raw_text":
        return node.get("raw", "")

    if t == "blank_line":
        return None

    if t in ("block_html", "inline_html", "html_block", "html_inline"):
        # Silently drop — Telegraph can't render raw HTML
        return None

    # Unknown — pass through children if any
    if children:
        return _children(children)

    raw = node.get("raw", "")
    return raw if raw else None


def markdown_to_nodes(text: str) -> list[Node]:
    ast = _parse(text)
    if not ast:
        return [{"tag": "p", "children": [" "]}]

    nodes: list[Any] = []
    for node in ast:
        converted = _convert_node(node)
        if converted is None:
            continue
        if isinstance(converted, list):
            nodes.extend(converted)
        else:
            nodes.append(converted)

    # Wrap any bare top-level strings in paragraphs
    result: list[Node] = []
    for n in nodes:
        if isinstance(n, str):
            if n.strip():
                result.append({"tag": "p", "children": [n]})
        else:
            result.append(n)

    return result if result else [{"tag": "p", "children": [" "]}]
