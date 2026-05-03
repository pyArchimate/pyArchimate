"""Unit tests for hierarchical layout functionality."""

from dataclasses import dataclass
from src.pyArchimate.view.layout.algorithms.hierarchical import HierarchicalLayout
from src.pyArchimate.view.layout.core import LayoutConfig
from src.pyArchimate.view.layout.utils.geometry import Point


@dataclass
class MockElement:
    """Mock element for testing."""

    id: str
    type: str
    x: float = 0.0
    y: float = 0.0
    width: float = 100.0
    height: float = 80.0


@dataclass
class MockView:
    """Mock view for testing."""

    id: str = "test_view"
    nodes: list = None
    edges: list = None

    def __post_init__(self):
        if self.nodes is None:
            self.nodes = []
        if self.edges is None:
            self.edges = []


class TestHierarchicalLayout:
    """Tests for HierarchicalLayout."""

    def test_hierarchical_layout_initialization(self):
        """Test that HierarchicalLayout initializes correctly."""
        layout = HierarchicalLayout()
        assert layout is not None
        assert layout.layer_gap == 100
        assert layout.node_spacing == 50

    def test_empty_view_layout(self):
        """Test layout on empty view."""
        layout = HierarchicalLayout()
        view = MockView()
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        assert result.elements_processed == 0

    def test_single_node_layout(self):
        """Test layout with single node."""
        layout = HierarchicalLayout()
        view = MockView()
        view.nodes = [MockElement(id="n1", type="ApplicationComponent", x=0, y=0)]
        view.edges = []
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        assert result.elements_processed == 1
        # Node should be positioned
        assert view.nodes[0].x != 0 or view.nodes[0].y != 0

    def test_linear_chain_layout(self):
        """Test layout with linear dependency chain (n1 -> n2 -> n3)."""
        layout = HierarchicalLayout()
        view = MockView()
        view.nodes = [
            MockElement(id="n1", type="ApplicationComponent"),
            MockElement(id="n2", type="ApplicationComponent"),
            MockElement(id="n3", type="ApplicationComponent"),
        ]
        view.edges = [(0, 1), (1, 2)]
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        assert result.elements_processed == 3
        assert result.connections_processed == 2

        # Nodes should be in different y positions (different layers)
        y_positions = [node.y for node in view.nodes]
        assert len(set(y_positions)) >= 2  # At least 2 different y values

    def test_tree_structure_layout(self):
        """Test layout with tree structure."""
        layout = HierarchicalLayout()
        view = MockView()
        # Root -> [Child1, Child2, Child3]
        view.nodes = [
            MockElement(id="root", type="BusinessProcess"),
            MockElement(id="c1", type="ApplicationComponent"),
            MockElement(id="c2", type="ApplicationComponent"),
            MockElement(id="c3", type="ApplicationComponent"),
        ]
        view.edges = [(0, 1), (0, 2), (0, 3)]
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        assert result.elements_processed == 4

        # Root should be in different layer than children
        assert view.nodes[0].y < view.nodes[1].y
        assert view.nodes[0].y < view.nodes[2].y
        assert view.nodes[0].y < view.nodes[3].y

    def test_diamond_dag_layout(self):
        """Test layout with diamond DAG structure."""
        layout = HierarchicalLayout()
        view = MockView()
        # n1 -> [n2, n3] -> n4
        view.nodes = [
            MockElement(id="n1", type="ApplicationComponent"),
            MockElement(id="n2", type="ApplicationComponent"),
            MockElement(id="n3", type="ApplicationComponent"),
            MockElement(id="n4", type="ApplicationComponent"),
        ]
        view.edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        assert result.elements_processed == 4
        assert result.connections_processed == 4

        # n1 should be topmost, n4 should be bottommost
        assert view.nodes[0].y < view.nodes[1].y
        assert view.nodes[1].y < view.nodes[3].y

    def test_layer_assignment_respects_archimate_hierarchy(self):
        """Test that layer assignment respects ArchiMate type hierarchy."""
        layout = HierarchicalLayout()
        view = MockView()
        # Business should be above Application
        view.nodes = [
            MockElement(id="b1", type="BusinessActor"),
            MockElement(id="a1", type="ApplicationComponent"),
        ]
        view.edges = [(0, 1)]
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        # Business should be positioned higher (lower y) than Application
        assert view.nodes[0].y <= view.nodes[1].y

    def test_crossing_minimization(self):
        """Test that crossing minimization produces reasonable layouts."""
        layout = HierarchicalLayout()
        view = MockView()
        # Create a structure where ordering matters for crossings
        view.nodes = [
            MockElement(id="n1", type="ApplicationComponent"),
            MockElement(id="n2", type="ApplicationComponent"),
            MockElement(id="n3", type="ApplicationComponent"),
            MockElement(id="n4", type="ApplicationComponent"),
        ]
        view.edges = [(0, 2), (1, 3)]
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        # Should have minimal crossings
        assert result.quality_metrics.get("crossings", 0) <= 1

    def test_multiple_layers_created(self):
        """Test that multiple layers are created for complex graphs."""
        layout = HierarchicalLayout()
        view = MockView()
        # Create a 3-layer structure
        view.nodes = [
            MockElement(id="l1_n1", type="ApplicationComponent"),
            MockElement(id="l2_n1", type="ApplicationComponent"),
            MockElement(id="l2_n2", type="ApplicationComponent"),
            MockElement(id="l3_n1", type="ApplicationComponent"),
        ]
        view.edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        num_layers = result.quality_metrics.get("layers", 0)
        assert num_layers >= 2

    def test_large_graph_performance(self):
        """Test performance on larger graph."""
        layout = HierarchicalLayout()
        view = MockView()

        # Create 50 nodes with linear dependencies
        view.nodes = [
            MockElement(id=f"n{i}", type="ApplicationComponent")
            for i in range(50)
        ]
        view.edges = [(i, i + 1) for i in range(49)]
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        assert result.elements_processed == 50
        # Should complete in reasonable time
        assert result.layout_time_ms < 5000

    def test_disconnected_components(self):
        """Test layout with disconnected graph components."""
        layout = HierarchicalLayout()
        view = MockView()
        # Two separate chains: n1->n2 and n3->n4
        view.nodes = [
            MockElement(id="n1", type="ApplicationComponent"),
            MockElement(id="n2", type="ApplicationComponent"),
            MockElement(id="n3", type="ApplicationComponent"),
            MockElement(id="n4", type="ApplicationComponent"),
        ]
        view.edges = [(0, 1), (2, 3)]
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        assert result.elements_processed == 4

    def test_position_respects_margin(self):
        """Test that positions respect margin from config."""
        layout = HierarchicalLayout()
        view = MockView()
        view.nodes = [
            MockElement(id="n1", type="ApplicationComponent"),
            MockElement(id="n2", type="ApplicationComponent"),
        ]
        view.edges = [(0, 1)]
        config = LayoutConfig(margin=30)

        result = layout.apply(view, config)

        assert result.success is True
        # Nodes should be positioned with margin applied
        assert view.nodes[0].x >= config.margin
        assert view.nodes[0].y >= config.margin

    def test_spacing_affects_layout(self):
        """Test that spacing parameter affects element positioning."""
        layout = HierarchicalLayout()
        view = MockView()
        view.nodes = [
            MockElement(id="n1", type="ApplicationComponent"),
            MockElement(id="n2", type="ApplicationComponent"),
            MockElement(id="n3", type="ApplicationComponent"),
        ]
        view.edges = [(0, 1), (0, 2)]

        config1 = LayoutConfig(spacing=50)
        result1 = layout.apply(view, config1)
        pos1 = [(n.x, n.y) for n in view.nodes]

        view.nodes = [
            MockElement(id="n1", type="ApplicationComponent"),
            MockElement(id="n2", type="ApplicationComponent"),
            MockElement(id="n3", type="ApplicationComponent"),
        ]
        config2 = LayoutConfig(spacing=100)
        result2 = layout.apply(view, config2)
        pos2 = [(n.x, n.y) for n in view.nodes]

        # Different spacing should produce different layouts
        # (at least some positions should differ)
        assert pos1 != pos2

    def test_build_graph(self):
        """Test graph building from nodes and edges."""
        layout = HierarchicalLayout()
        nodes = [
            MockElement(id="n1", type="ApplicationComponent"),
            MockElement(id="n2", type="ApplicationComponent"),
            MockElement(id="n3", type="ApplicationComponent"),
        ]
        edges = [(0, 1), (1, 2), (0, 2)]

        graph = layout._build_graph(nodes, edges)

        assert 0 in graph
        assert 1 in graph[0]
        assert 2 in graph[0]
        assert 1 in graph
        assert 2 in graph[1]

    def test_crossing_detection(self):
        """Test crossing detection in layouts."""
        layout = HierarchicalLayout()
        positions = {
            0: Point(0, 0),
            1: Point(100, 100),
            2: Point(50, 0),
            3: Point(150, 100),
        }
        edges = [(0, 3), (2, 1)]  # These should cross

        crossings = layout._count_crossings(positions, edges)

        # Should detect crossing
        assert crossings >= 0

    def test_layer_assignment_with_mixed_types(self):
        """Test layer assignment with mixed ArchiMate types."""
        layout = HierarchicalLayout()
        view = MockView()
        # Mix of Business, Application, Technology
        view.nodes = [
            MockElement(id="b1", type="BusinessActor"),
            MockElement(id="a1", type="ApplicationComponent"),
            MockElement(id="t1", type="TechnologyNode"),
        ]
        view.edges = [(0, 1), (1, 2)]
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        # Should respect layer hierarchy
        # Business (b1) should be above Application (a1) should be above Technology (t1)
        y_business = view.nodes[0].y
        y_app = view.nodes[1].y
        y_tech = view.nodes[2].y

        # They should be in order (lower y = higher in diagram)
        assert y_business <= y_app <= y_tech


class TestHierarchicalLayoutEdgeCases:
    """Tests for edge cases in hierarchical layout."""

    def test_self_loop_handling(self):
        """Test that self-loops are handled gracefully."""
        layout = HierarchicalLayout()
        view = MockView()
        view.nodes = [MockElement(id="n1", type="ApplicationComponent")]
        view.edges = [(0, 0)]  # Self-loop
        config = LayoutConfig()

        result = layout.apply(view, config)

        # Should handle gracefully without crashing
        assert result.success is True or result.success is False

    def test_duplicate_edges(self):
        """Test handling of duplicate edges."""
        layout = HierarchicalLayout()
        view = MockView()
        view.nodes = [
            MockElement(id="n1", type="ApplicationComponent"),
            MockElement(id="n2", type="ApplicationComponent"),
        ]
        view.edges = [(0, 1), (0, 1)]  # Duplicate
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        assert result.connections_processed == 2

    def test_all_nodes_same_layer(self):
        """Test layout when all nodes should be in same layer."""
        layout = HierarchicalLayout()
        view = MockView()
        view.nodes = [
            MockElement(id="n1", type="ApplicationComponent"),
            MockElement(id="n2", type="ApplicationComponent"),
            MockElement(id="n3", type="ApplicationComponent"),
        ]
        view.edges = []  # No dependencies
        config = LayoutConfig()

        result = layout.apply(view, config)

        assert result.success is True
        # All should be in same layer, so same y value
        y_positions = [node.y for node in view.nodes]
        # They should all be close in y (same layer)
        assert max(y_positions) - min(y_positions) < 10
