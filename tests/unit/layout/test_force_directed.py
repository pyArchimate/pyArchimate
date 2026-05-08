"""Tests for force-directed layout algorithm."""

from src.pyArchimate.view.layout.algorithms.force_directed import ForceDirectedLayout
from src.pyArchimate.view.layout.core import LayoutConfig, LayoutResult
from src.pyArchimate.view.layout.utils.geometry import Point


class MockNode:
    """Mock node for testing."""

    def __init__(self, node_id: int, x: float = 100, y: float = 100) -> None:
        """Create a mock node."""
        self.id = node_id
        self.x = x
        self.y = y
        self.type = "ApplicationComponent"


class MockView:
    """Mock view for testing."""

    def __init__(self, num_nodes: int = 5, num_edges: int = 3) -> None:
        """Create a mock view."""
        self.id = "test_view"
        self.nodes = [MockNode(i) for i in range(num_nodes)]
        # Only create edges if there are nodes to connect
        if num_nodes > 0:
            self.edges = [(i, (i + 1) % num_nodes) for i in range(min(num_edges, num_nodes))]
        else:
            self.edges = []


def test_force_directed_instantiation() -> None:
    """Test force-directed layout instantiation."""
    layout = ForceDirectedLayout()
    assert layout.k_attraction == 0.01
    assert layout.k_repulsion == 2000.0
    assert layout.damping == 0.8


def test_force_directed_empty_view() -> None:
    """Test force-directed layout with empty view."""
    layout = ForceDirectedLayout()
    view = MockView(num_nodes=0)
    result = layout.apply(view, LayoutConfig())

    assert isinstance(result, LayoutResult)
    assert result.success is True
    assert result.elements_processed == 0


def test_force_directed_single_node() -> None:
    """Test force-directed layout with single node."""
    layout = ForceDirectedLayout()
    view = MockView(num_nodes=1, num_edges=0)
    result = layout.apply(view, LayoutConfig())

    assert result.success is True
    assert result.elements_processed == 1


def test_force_directed_small_view() -> None:
    """Test force-directed layout with small view."""
    layout = ForceDirectedLayout()
    view = MockView(num_nodes=5, num_edges=4)
    result = layout.apply(view, LayoutConfig())

    assert result.success is True
    assert result.elements_processed == 5
    assert result.connections_processed == 4
    assert "converged" in result.quality_metrics
    assert "iterations" in result.quality_metrics


def test_iteration_limit_small() -> None:
    """Test iteration limit for small graphs."""
    layout = ForceDirectedLayout()
    assert layout._get_iteration_limit(10) == 500
    assert layout._get_iteration_limit(30) == 500


def test_iteration_limit_medium() -> None:
    """Test iteration limit for medium graphs."""
    layout = ForceDirectedLayout()
    assert layout._get_iteration_limit(100) == 300
    assert layout._get_iteration_limit(150) == 300


def test_iteration_limit_large() -> None:
    """Test iteration limit for large graphs."""
    layout = ForceDirectedLayout()
    assert layout._get_iteration_limit(300) == 150
    assert layout._get_iteration_limit(500) == 150


def test_initialize_positions_with_existing() -> None:
    """Test position initialization preserving existing positions."""
    layout = ForceDirectedLayout()
    nodes = [MockNode(0, x=50, y=75), MockNode(1, x=200, y=300)]
    positions = layout._initialize_positions(nodes, LayoutConfig())

    assert positions[0].x == 50
    assert positions[0].y == 75
    assert positions[1].x == 200
    assert positions[1].y == 300


def test_force_calculation() -> None:
    """Test force calculation."""
    layout = ForceDirectedLayout()

    # Create simple positions: two nodes
    positions = {0: Point(0, 0), 1: Point(100, 0)}
    edges = [(0, 1)]

    from src.pyArchimate.view.layout.routing.layer_constraints import ArchiMateLayer, LayerConstraint
    layer_constraint = LayerConstraint()
    layer_constraint.assign_layer(0, ArchiMateLayer.BUSINESS)
    layer_constraint.assign_layer(1, ArchiMateLayer.APPLICATION)

    forces = layout._calculate_forces(positions, edges, layer_constraint)

    assert 0 in forces
    assert 1 in forces


def test_apply_with_config() -> None:
    """Test force-directed layout with custom config."""
    layout = ForceDirectedLayout()
    view = MockView(num_nodes=10, num_edges=8)
    config = LayoutConfig(algorithm="force_directed", spacing=100)

    result = layout.apply(view, config)

    assert result.success is True
    assert result.algorithm_used == "force_directed"
    assert result.layout_time_ms >= 0
