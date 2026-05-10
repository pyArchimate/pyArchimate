"""Utilities for edge/connection handling in layout algorithms."""

from typing import Any


def _normalize_tuple_edge(edge: Any) -> tuple[int | None, int | None]:
    source_idx, target_idx = edge
    return source_idx, target_idx


def _normalize_connection_edge(edge: Any, uuid_to_index: dict[str, int]) -> tuple[int | None, int | None]:
    source_idx = uuid_to_index.get(edge._source)
    target_idx = uuid_to_index.get(edge._target)
    return source_idx, target_idx


def _normalize_dict_edge(edge: dict[str, Any], uuid_to_index: dict[str, int]) -> tuple[int | None, int | None]:
    source_key = edge.get('source') or edge.get('_source')
    target_key = edge.get('target') or edge.get('_target')

    if isinstance(source_key, int):
        source_idx: int | None = source_key
    elif isinstance(source_key, str):
        source_idx = uuid_to_index.get(source_key)
    else:
        source_idx = None

    if isinstance(target_key, int):
        target_idx: int | None = target_key
    elif isinstance(target_key, str):
        target_idx = uuid_to_index.get(target_key)
    else:
        target_idx = None

    return source_idx, target_idx


def _normalize_single_edge(
    edge: Any, uuid_to_index: dict[str, int]
) -> tuple[int | None, int | None]:
    if isinstance(edge, tuple) and len(edge) == 2:
        return _normalize_tuple_edge(edge)
    if hasattr(edge, "_source") and hasattr(edge, "_target"):
        return _normalize_connection_edge(edge, uuid_to_index)
    if isinstance(edge, dict):
        return _normalize_dict_edge(edge, uuid_to_index)
    return None, None


def normalize_edges(edges: Any, nodes: list[Any]) -> list[tuple[int, int]]:
    """Convert various edge formats to tuples of (source_index, target_index).

    Handles:
    - List of tuples (source_index, target_index)
    - List of Connection objects with _source and _target UUIDs
    - List of edge dictionaries

    Args:
        edges: List of edges in various formats
        nodes: List of nodes (used to map UUIDs to indices)

    Returns:
        List of (source_index, target_index) tuples
    """
    if not edges:
        return []

    # Build UUID to index mapping
    node_uuid_to_index: dict[str, int] = {}
    for i, node in enumerate(nodes):
        node_uuid = getattr(node, 'uuid', None)
        if node_uuid:
            node_uuid_to_index[node_uuid] = i

    normalized = []
    for edge in edges:
        source_idx, target_idx = _normalize_single_edge(edge, node_uuid_to_index)
        if source_idx is not None and target_idx is not None:
            if 0 <= source_idx < len(nodes) and 0 <= target_idx < len(nodes):
                normalized.append((source_idx, target_idx))
    return normalized
