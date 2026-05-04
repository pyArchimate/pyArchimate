"""Utilities for edge/connection handling in layout algorithms."""

from typing import Any, Dict, List, Tuple


def normalize_edges(edges: Any, nodes: List[Any]) -> List[Tuple[int, int]]:
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
    node_uuid_to_index: Dict[str, int] = {}
    for i, node in enumerate(nodes):
        node_uuid = getattr(node, 'uuid', None)
        if node_uuid:
            node_uuid_to_index[node_uuid] = i

    normalized = []

    for edge in edges:
        source_idx = None
        target_idx = None

        # Handle tuple format (source_index, target_index)
        if isinstance(edge, tuple) and len(edge) == 2:
            source_idx, target_idx = edge

        # Handle Connection objects
        elif hasattr(edge, '_source') and hasattr(edge, '_target'):
            source_uuid = edge._source
            target_uuid = edge._target
            source_idx = node_uuid_to_index.get(source_uuid)
            target_idx = node_uuid_to_index.get(target_uuid)

        # Handle dictionary format
        elif isinstance(edge, dict):
            source_key = edge.get('source') or edge.get('_source')
            target_key = edge.get('target') or edge.get('_target')

            if isinstance(source_key, int):
                source_idx = source_key
            elif isinstance(source_key, str):
                source_idx = node_uuid_to_index.get(source_key)

            if isinstance(target_key, int):
                target_idx = target_key
            elif isinstance(target_key, str):
                target_idx = node_uuid_to_index.get(target_key)

        # Add if both indices found and valid
        if source_idx is not None and target_idx is not None:
            if 0 <= source_idx < len(nodes) and 0 <= target_idx < len(nodes):
                normalized.append((source_idx, target_idx))

    return normalized
