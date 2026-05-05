"""Integration tests for undo_layout functionality (FR-010)."""

from src.pyArchimate.view.layout import apply_layout, undo_layout
from src.pyArchimate.view.layout.core import LayoutConfig


class MockNode:
    """Mock element node for testing."""

    def __init__(self, node_id, x=0, y=0, w=120, h=55, element_type="ApplicationComponent"):
        self.id = node_id
        self._x = x
        self._y = y
        self.w = w
        self.h = h
        self.type = element_type

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def cx(self):
        return self._x + self.w / 2

    @property
    def cy(self):
        return self._y + self.h / 2


class MockView:
    """Mock view for testing."""

    def __init__(self, nodes=None):
        self.id = "test-view"
        self.nodes = nodes or []
        self.nodes_dict = {getattr(n, 'id', i): n for i, n in enumerate(self.nodes)}


class TestUndoLayout:
    """Test undo_layout capability (FR-010)."""

    def test_undo_layout_returns_success(self):
        """Test that undo_layout returns a success result."""
        node1 = MockNode(1, x=10, y=20)
        node2 = MockNode(2, x=100, y=200)
        view = MockView(nodes=[node1, node2])

        # Apply layout first
        config = LayoutConfig(algorithm="force_directed")
        apply_result = apply_layout(view, config)
        assert apply_result.success

        # Undo layout
        undo_result = undo_layout(view)

        assert undo_result.success
        assert undo_result.view_id == "test-view"
        assert undo_result.algorithm_used == "undo"
        assert undo_result.error_message is None

    def test_undo_layout_with_single_element(self):
        """Test undo_layout with single-element view."""
        node1 = MockNode(1, x=50, y=50)
        view = MockView(nodes=[node1])

        # Apply and undo
        config = LayoutConfig(algorithm="force_directed")
        apply_layout(view, config)

        result = undo_layout(view)
        assert result.success
        assert result.algorithm_used == "undo"

    def test_undo_layout_multiple_calls(self):
        """Test that undo_layout can be called multiple times sequentially."""
        nodes = [
            MockNode(1, x=0, y=0),
            MockNode(2, x=200, y=200),
            MockNode(3, x=400, y=400),
        ]
        view = MockView(nodes=nodes)

        # Apply layout
        config = LayoutConfig(algorithm="force_directed")
        apply_layout(view, config)

        # Undo multiple times should all succeed
        result1 = undo_layout(view)
        assert result1.success

        result2 = undo_layout(view)
        assert result2.success

        result3 = undo_layout(view)
        assert result3.success

    def test_undo_layout_with_hierarchical_algorithm(self):
        """Test undo_layout after hierarchical layout."""
        node1 = MockNode(1, element_type="BusinessActor")
        node2 = MockNode(2, element_type="ApplicationComponent")
        view = MockView(nodes=[node1, node2])

        # Apply hierarchical layout
        config = LayoutConfig(algorithm="hierarchical")
        apply_layout(view, config)

        # Undo should succeed
        result = undo_layout(view)
        assert result.success
        assert result.algorithm_used == "undo"
        assert result.view_id == "test-view"

    def test_undo_layout_with_different_configs(self):
        """Test undo_layout after layout with various configuration options."""
        node1 = MockNode(1, x=10, y=10)
        node2 = MockNode(2, x=50, y=50)
        node3 = MockNode(3, x=100, y=100)
        view = MockView(nodes=[node1, node2, node3])

        # Apply layout with custom config
        config = LayoutConfig(
            algorithm="force_directed",
            spacing=100,
            margin=50,
            alignment="grid",
            grid_size=25,
            layer_priority="mandatory",
            excluded_element_ids=[],
        )
        apply_layout(view, config)

        # Undo should succeed regardless of config
        result = undo_layout(view)
        assert result.success
        assert result.algorithm_used == "undo"
        assert result.layout_time_ms >= 0