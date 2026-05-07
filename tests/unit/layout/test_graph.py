"""Tests for graph analysis utilities."""

from src.pyArchimate.view.layout.utils.graph import Graph, count_crossings, detect_crossings


class TestGraph:
    """Test Graph class."""

    def test_init(self) -> None:
        """Test graph initialization."""
        g = Graph()
        assert g.nodes == set()
        assert g.edges == {}

    def test_add_node(self) -> None:
        """Test adding a node."""
        g = Graph()
        g.add_node("A")
        assert "A" in g.nodes
        assert "A" in g.edges

    def test_add_duplicate_node(self) -> None:
        """Test adding duplicate node (should be idempotent)."""
        g = Graph()
        g.add_node("A")
        g.add_node("A")
        assert len(g.nodes) == 1

    def test_add_edge(self) -> None:
        """Test adding an edge."""
        g = Graph()
        g.add_edge("A", "B")
        assert "A" in g.nodes
        assert "B" in g.nodes
        assert "B" in g.edges["A"]
        assert "A" in g.edges["B"]

    def test_get_neighbors_existing(self) -> None:
        """Test getting neighbors of existing node."""
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        neighbors = g.get_neighbors("A")
        assert "B" in neighbors
        assert "C" in neighbors
        assert len(neighbors) == 2

    def test_get_neighbors_nonexistent(self) -> None:
        """Test getting neighbors of non-existent node returns empty set."""
        g = Graph()
        neighbors = g.get_neighbors("Z")
        assert neighbors == set()

    def test_has_cycle_tree_no_cycle(self) -> None:
        """Test cycle detection on tree (no cycle)."""
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("B", "D")
        assert g.has_cycle() is False

    def test_has_cycle_simple_cycle(self) -> None:
        """Test cycle detection with simple cycle."""
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")
        assert g.has_cycle() is True

    def test_has_cycle_self_loop(self) -> None:
        """Test cycle detection with self-loop (node with edge to itself)."""
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "B")
        assert g.has_cycle() is True

    def test_has_cycle_disconnected(self) -> None:
        """Test cycle detection on disconnected nodes."""
        g = Graph()
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        assert g.has_cycle() is False

    def test_has_cycle_empty_graph(self) -> None:
        """Test cycle detection on empty graph."""
        g = Graph()
        assert g.has_cycle() is False

    def test_get_connected_components_single(self) -> None:
        """Test connected components with single component."""
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        components = g.get_connected_components()
        assert len(components) == 1
        assert components[0] == {"A", "B", "C"}

    def test_get_connected_components_multiple(self) -> None:
        """Test connected components with multiple components."""
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("C", "D")
        components = g.get_connected_components()
        assert len(components) == 2
        component_sets = [set(c) for c in components]
        assert {"A", "B"} in component_sets
        assert {"C", "D"} in component_sets

    def test_get_connected_components_isolated_nodes(self) -> None:
        """Test connected components with isolated nodes."""
        g = Graph()
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        components = g.get_connected_components()
        assert len(components) == 3
        for component in components:
            assert len(component) == 1

    def test_get_connected_components_empty(self) -> None:
        """Test connected components on empty graph."""
        g = Graph()
        components = g.get_connected_components()
        assert components == []


class TestDetectCrossings:
    """Test line crossing detection."""

    def test_crossing_lines(self) -> None:
        """Test detection of crossing lines."""
        line1 = ((0.0, 0.0), (2.0, 2.0))
        line2 = ((0.0, 2.0), (2.0, 0.0))
        assert detect_crossings(line1, line2) is True

    def test_parallel_lines(self) -> None:
        """Test non-crossing parallel lines."""
        line1 = ((0.0, 0.0), (2.0, 0.0))
        line2 = ((0.0, 1.0), (2.0, 1.0))
        assert detect_crossings(line1, line2) is False

    def test_non_crossing_segments(self) -> None:
        """Test non-crossing segments."""
        line1 = ((0.0, 0.0), (1.0, 1.0))
        line2 = ((2.0, 2.0), (3.0, 3.0))
        assert detect_crossings(line1, line2) is False

    def test_touching_endpoints(self) -> None:
        """Test lines touching at endpoints (not crossing)."""
        line1 = ((0.0, 0.0), (1.0, 1.0))
        line2 = ((1.0, 1.0), (2.0, 0.0))
        assert detect_crossings(line1, line2) is False


class TestCountCrossings:
    """Test crossing count."""

    def test_count_single_crossing(self) -> None:
        """Test counting single crossing."""
        edges = [
            ((0.0, 0.0), (2.0, 2.0)),
            ((0.0, 2.0), (2.0, 0.0)),
        ]
        assert count_crossings(edges) == 1

    def test_count_no_crossings(self) -> None:
        """Test counting with no crossings."""
        edges = [
            ((0.0, 0.0), (1.0, 1.0)),
            ((2.0, 2.0), (3.0, 3.0)),
        ]
        assert count_crossings(edges) == 0

    def test_count_multiple_crossings(self) -> None:
        """Test counting multiple crossings."""
        edges = [
            ((0.0, 0.0), (3.0, 3.0)),
            ((0.0, 3.0), (3.0, 0.0)),
            ((1.0, 0.0), (1.0, 3.0)),
        ]
        # First two edges cross, first and third don't, second and third don't
        crossing_count = count_crossings(edges)
        assert crossing_count >= 1

    def test_count_empty_edges(self) -> None:
        """Test with empty edge list."""
        assert count_crossings([]) == 0

    def test_count_single_edge(self) -> None:
        """Test with single edge (no crossings possible)."""
        edges = [((0.0, 0.0), (1.0, 1.0))]
        assert count_crossings(edges) == 0
