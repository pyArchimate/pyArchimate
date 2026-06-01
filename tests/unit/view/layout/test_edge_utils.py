"""Tests for edge/connection handling utilities."""

from typing import Any

from src.pyArchimate.view.layout.utils.edge_utils import normalize_edges


class MockNode:
    """Mock node object with uuid."""

    def __init__(self, uuid: str) -> None:
        """Initialize mock node."""
        self.uuid = uuid


class MockConnection:
    """Mock connection object with _source and _target."""

    def __init__(self, source_uuid: str, target_uuid: str) -> None:
        """Initialize mock connection."""
        self._source = source_uuid
        self._target = target_uuid


class TestNormalizeEdges:
    """Test edge normalization."""

    def test_empty_edges(self) -> None:
        """Test with empty edge list."""
        nodes = [MockNode("a"), MockNode("b")]
        result = normalize_edges([], nodes)
        assert result == []

    def test_none_edges(self) -> None:
        """Test with None edges."""
        nodes = [MockNode("a"), MockNode("b")]
        result = normalize_edges(None, nodes)
        assert result == []

    def test_tuple_format(self) -> None:
        """Test tuple format (source_index, target_index)."""
        nodes = [MockNode("a"), MockNode("b"), MockNode("c")]
        edges = [(0, 1), (1, 2)]
        result = normalize_edges(edges, nodes)
        assert result == [(0, 1), (1, 2)]

    def test_connection_object_format(self) -> None:
        """Test Connection object format with _source and _target."""
        nodes = [MockNode("uuid-a"), MockNode("uuid-b"), MockNode("uuid-c")]
        edges = [
            MockConnection("uuid-a", "uuid-b"),
            MockConnection("uuid-b", "uuid-c"),
        ]
        result = normalize_edges(edges, nodes)
        assert result == [(0, 1), (1, 2)]

    def test_dict_format_with_int_keys(self) -> None:
        """Test dictionary format with integer source/target keys (non-zero)."""
        nodes = [MockNode("a"), MockNode("b"), MockNode("c")]
        edges = [
            {"source": 1, "target": 2},
        ]
        result = normalize_edges(edges, nodes)
        assert result == [(1, 2)]

    def test_dict_format_with_string_keys(self) -> None:
        """Test dictionary format with UUID string source/target keys."""
        nodes = [MockNode("uuid-a"), MockNode("uuid-b"), MockNode("uuid-c")]
        edges = [
            {"source": "uuid-a", "target": "uuid-b"},
            {"source": "uuid-b", "target": "uuid-c"},
        ]
        result = normalize_edges(edges, nodes)
        assert result == [(0, 1), (1, 2)]

    def test_dict_format_with_underscore_keys(self) -> None:
        """Test dictionary format with _source/_target alternate keys."""
        nodes = [MockNode("uuid-a"), MockNode("uuid-b")]
        edges = [{"_source": "uuid-a", "_target": "uuid-b"}]
        result = normalize_edges(edges, nodes)
        assert result == [(0, 1)]

    def test_mixed_formats(self) -> None:
        """Test mixed edge formats in same list."""
        nodes = [MockNode("uuid-a"), MockNode("uuid-b"), MockNode("uuid-c")]
        edges: list[Any] = [
            (1, 2),  # tuple format
            MockConnection("uuid-b", "uuid-c"),  # Connection object
            {"source": 1, "target": 2},  # dict with int keys
        ]
        result = normalize_edges(edges, nodes)
        assert len(result) == 3
        assert (1, 2) in result

    def test_invalid_indices_out_of_bounds(self) -> None:
        """Test edge with indices out of bounds."""
        nodes = [MockNode("a"), MockNode("b")]
        edges = [(0, 5)]  # 5 is out of bounds
        result = normalize_edges(edges, nodes)
        assert result == []

    def test_unknown_uuid_skipped(self) -> None:
        """Test edge with unknown UUID is skipped."""
        nodes = [MockNode("uuid-a"), MockNode("uuid-b")]
        edges = [{"source": "uuid-unknown", "target": "uuid-b"}]
        result = normalize_edges(edges, nodes)
        assert result == []

    def test_nodes_without_uuid_attribute(self) -> None:
        """Test handling of nodes without uuid attribute."""

        class NodeNoUuid:
            pass

        nodes: list[Any] = [NodeNoUuid(), NodeNoUuid()]
        edges = [{"source": "unknown", "target": "unknown"}]
        result = normalize_edges(edges, nodes)
        assert result == []

    def test_negative_indices_invalid(self) -> None:
        """Test that negative indices are rejected."""
        nodes = [MockNode("a"), MockNode("b")]
        edges = [(-1, 1)]
        result = normalize_edges(edges, nodes)
        assert result == []

    def test_source_equals_target_valid(self) -> None:
        """Test edge where source equals target (self-loop)."""
        nodes = [MockNode("uuid-a"), MockNode("uuid-b")]
        edges = [{"source": 1, "target": 1}]
        result = normalize_edges(edges, nodes)
        assert result == [(1, 1)]

    def test_partial_dict_missing_target(self) -> None:
        """Test dictionary edge missing target key."""
        nodes = [MockNode("uuid-a"), MockNode("uuid-b")]
        edges = [{"source": 0}]
        result = normalize_edges(edges, nodes)
        assert result == []

    def test_partial_dict_missing_source(self) -> None:
        """Test dictionary edge missing source key."""
        nodes = [MockNode("uuid-a"), MockNode("uuid-b")]
        edges = [{"target": 1}]
        result = normalize_edges(edges, nodes)
        assert result == []
