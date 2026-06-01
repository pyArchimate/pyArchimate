"""Diagram helper wrappers exposed as module-level utilities."""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..view import Node, View


def get_or_create_node(owner, *args, **kwargs):
    """Delegate node creation to Model/View helper methods."""
    return owner.get_or_create_node(*args, **kwargs)


def get_or_create_connection(owner, *args, **kwargs):
    """Delegate connection creation to View helper methods."""
    return owner.get_or_create_connection(*args, **kwargs)


def _iter_nodes(node_owner: View | Node) -> Generator[Node, None, None]:
    for node in node_owner.nodes:
        yield node
        yield from _iter_nodes(node)


def apply_profile_styles(view: View, mapping: dict[str, str | dict[str, str]]) -> None:
    """Apply fill colours to view nodes based on their element's profile name.

    Walks all nodes recursively, including nodes nested inside other nodes.
    *mapping* keys are profile names; values are either a hex colour string
    (applied to ``fill_color``) or a dict with any of ``fill_color``,
    ``line_color``, ``font_color`` keys.
    """
    for node in _iter_nodes(view):
        profile = node.concept.profile_name if node.concept else None
        if profile not in mapping:
            continue
        value = mapping[profile]
        if isinstance(value, str):
            node.fill_color = value
        else:
            if "fill_color" in value:
                node.fill_color = value["fill_color"]
            if "line_color" in value:
                node.line_color = value["line_color"]
            if "font_color" in value:
                node.font_color = value["font_color"]


__all__ = ["get_or_create_node", "get_or_create_connection", "apply_profile_styles"]
