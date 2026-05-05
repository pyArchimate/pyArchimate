"""Integration tests for layout API functions."""

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view.layout import (
    LayoutConfig,
    LayoutResult,
    _apply_orthogonal_routing,
    apply_format,
    apply_layout,
    undo_layout,
)


class MockView:
    """Mock view object for testing."""

    def __init__(self, view_id: str, num_nodes: int = 10, num_edges: int = 5) -> None:
        """Create a mock view."""
        self.id = view_id
        self.nodes = [f"node_{i}" for i in range(num_nodes)]
        self.edges = [f"edge_{i}" for i in range(num_edges)]


def test_apply_layout_with_defaults() -> None:
    """Test apply_layout with default configuration."""
    view = MockView("test_view")
    result = apply_layout(view)

    assert isinstance(result, LayoutResult)
    assert result.success is True
    assert result.view_id == "test_view"
    assert result.algorithm_used == "force_directed"
    assert result.elements_processed == 10
    assert result.connections_processed == 5
    assert result.layout_time_ms >= 0


def test_apply_layout_with_custom_config() -> None:
    """Test apply_layout with custom configuration."""
    view = MockView("test_view", num_nodes=20, num_edges=15)
    config = LayoutConfig(algorithm="hierarchical", spacing=75.0)
    result = apply_layout(view, config)

    assert result.success is True
    assert result.algorithm_used == "hierarchical"
    assert result.elements_processed == 20
    assert result.connections_processed == 15


def test_apply_layout_error_handling() -> None:
    """Test apply_layout error handling with view that raises exception."""
    # Create a mock view that will cause an error when accessed
    class BadView:
        id = "bad_view"

        @property
        def nodes(self) -> None:
            raise RuntimeError("Simulated error reading nodes")

    view = BadView()  # type: ignore
    result = apply_layout(view)

    assert result.success is False
    assert result.error_message is not None
    assert "Simulated error reading nodes" in result.error_message
    assert result.layout_time_ms >= 0


def test_apply_format_with_defaults() -> None:
    """Test apply_format with default configuration."""
    view = MockView("test_view", num_nodes=15)
    result = apply_format(view)

    assert isinstance(result, LayoutResult)
    assert result.success is True
    assert result.view_id == "test_view"
    assert result.algorithm_used == "format"
    assert result.elements_processed == 15
    assert result.connections_processed == 0


def test_apply_format_with_custom_config() -> None:
    """Test apply_format with custom configuration."""
    view = MockView("test_view", num_nodes=25)
    config = LayoutConfig(alignment="grid")
    result = apply_format(view, config)

    assert result.success is True
    assert result.elements_processed == 25


def test_undo_layout_success() -> None:
    """Test undo_layout successful operation."""
    view = MockView("test_view")
    result = undo_layout(view)

    assert isinstance(result, LayoutResult)
    assert result.success is True
    assert result.algorithm_used == "undo"
    assert result.layout_time_ms >= 0


def test_layout_result_attributes() -> None:
    """Test LayoutResult has all required attributes."""
    view = MockView("test_view", num_nodes=5, num_edges=3)
    result = apply_layout(view)

    assert hasattr(result, "success")
    assert hasattr(result, "view_id")
    assert hasattr(result, "algorithm_used")
    assert hasattr(result, "elements_processed")
    assert hasattr(result, "connections_processed")
    assert hasattr(result, "layout_time_ms")
    assert hasattr(result, "quality_metrics")
    assert hasattr(result, "error_message")


def test_orthogonal_routing_places_same_row_source_anchor_on_edge() -> None:
    """Same-row routed connections should start at the source edge, not the center."""
    model = Model("routing-test")
    view = model.add(ArchiType.View, "V")

    source = model.add(ArchiType.ApplicationComponent, "Source")
    target = model.add(ArchiType.ApplicationComponent, "Target")
    source_node = view.add(source, x=40, y=40, w=120, h=60)
    target_node = view.add(target, x=260, y=40, w=120, h=60)
    rel = model.add_relationship(ArchiType.Serving, source=source, target=target)
    conn = view.add_connection(ref=rel.uuid, source=source_node, target=target_node)

    _apply_orthogonal_routing(view)

    bendpoints = conn.get_all_bendpoints()
    assert len(bendpoints) >= 2
    assert bendpoints[0].x == source_node.x + source_node.w
    assert bendpoints[-1].x == target_node.x


def test_orthogonal_routing_places_vertical_target_anchor_on_edge() -> None:
    """Vertical routing should end at the target edge, not the center."""
    model = Model("routing-target-test")
    view = model.add(ArchiType.View, "V")

    source = model.add(ArchiType.ApplicationComponent, "Source")
    target = model.add(ArchiType.ApplicationComponent, "Target")
    source_node = view.add(source, x=40, y=40, w=120, h=60)
    target_node = view.add(target, x=40, y=220, w=120, h=60)
    rel = model.add_relationship(ArchiType.Serving, source=source, target=target)
    conn = view.add_connection(ref=rel.uuid, source=source_node, target=target_node)

    _apply_orthogonal_routing(view)

    bendpoints = conn.get_all_bendpoints()
    assert len(bendpoints) >= 2
    assert bendpoints[-1].y == target_node.y
