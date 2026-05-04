"""Integration tests for LayoutConfig customization parameters."""

from src.pyArchimate.view.layout import apply_format, apply_layout
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


class MockConnection:
    """Mock connection for testing."""

    def __init__(self, source_id, target_id):
        self._source = source_id
        self._target = target_id


class MockView:
    """Mock view for testing."""

    def __init__(self, nodes=None, conns=None):
        self.id = "test-view"
        self.nodes = nodes or []
        self.conns = conns or []
        self.nodes_dict = {getattr(n, 'id', i): n for i, n in enumerate(self.nodes)}

    def nodes_getter(self):
        return self.nodes

    def conns_getter(self):
        return self.conns


class TestExcludedElementIds:
    """Test excluded_element_ids parameter."""

    def test_format_excludes_elements(self):
        """Test that format respects excluded_element_ids."""
        node1 = MockNode(1, element_type="BusinessActor")
        node2 = MockNode(2, element_type="BusinessRole")
        node3 = MockNode(3, element_type="ApplicationComponent")

        view = MockView(nodes=[node1, node2, node3])

        # Format with node1 and node2 excluded
        config = LayoutConfig(excluded_element_ids=[1, 2])
        result = apply_format(view, config)

        assert result.success
        # Only node3 should be formatted
        assert result.elements_processed == 1
        assert result.quality_metrics["skipped"] == 2

    def test_layout_excludes_elements(self):
        """Test that layout respects excluded_element_ids."""
        node1 = MockNode(0, x=0, y=0, element_type="BusinessActor")
        node2 = MockNode(1, x=100, y=100, element_type="ApplicationComponent")
        node3 = MockNode(2, x=200, y=200, element_type="TechnologyNode")

        conn1 = MockConnection(0, 1)
        conn2 = MockConnection(1, 2)

        view = MockView(nodes=[node1, node2, node3], conns=[conn1, conn2])

        # Layout with node1 excluded - should not be repositioned
        config = LayoutConfig(algorithm="force_directed", excluded_element_ids=[0])
        original_x, original_y = node1.x, node1.y

        result = apply_layout(view, config)

        assert result.success
        # Excluded element should retain original position
        assert node1.x == original_x
        assert node1.y == original_y
        # Should only process 2 elements (node2 and node3)
        assert result.elements_processed == 2


class TestSpacingParameter:
    """Test spacing parameter."""

    def test_custom_spacing(self):
        """Test custom spacing is applied during layout."""
        node1 = MockNode(0, x=0, y=0, element_type="BusinessActor")
        node2 = MockNode(1, x=50, y=50, element_type="ApplicationComponent")

        view = MockView(nodes=[node1, node2])

        # Use large spacing
        config = LayoutConfig(algorithm="force_directed", spacing=150)
        result = apply_layout(view, config)

        assert result.success
        assert result.quality_metrics["spacing"] == 150

    def test_spacing_in_quality_metrics(self):
        """Test that spacing appears in quality metrics."""
        node1 = MockNode(0, element_type="BusinessActor")
        view = MockView(nodes=[node1])

        config = LayoutConfig(spacing=75)
        result = apply_layout(view, config)

        assert result.quality_metrics["spacing"] == 75


class TestAlignmentParameter:
    """Test alignment parameter."""

    def test_free_alignment(self):
        """Test free alignment (no snapping)."""
        node1 = MockNode(0, x=123, y=456, element_type="ApplicationComponent")
        view = MockView(nodes=[node1])

        config = LayoutConfig(alignment="free")
        result = apply_format(view, config)

        assert result.success
        assert result.quality_metrics["alignment"] == "free"

    def test_grid_alignment(self):
        """Test grid alignment (snapping to grid)."""
        node1 = MockNode(0, x=123, y=456, element_type="ApplicationComponent")
        view = MockView(nodes=[node1])

        config = LayoutConfig(alignment="grid", grid_size=50)
        result = apply_format(view, config)

        assert result.success
        # Position should be snapped to grid
        assert node1.x % 50 == 0
        assert node1.y % 50 == 0
        assert result.quality_metrics["alignment"] == "grid"

    def test_grid_size_applied(self):
        """Test grid_size parameter is applied correctly."""
        node1 = MockNode(0, x=75, y=75, element_type="ApplicationComponent")
        view = MockView(nodes=[node1])

        config = LayoutConfig(alignment="grid", grid_size=25)
        result = apply_format(view, config)

        assert result.success
        # 75 snapped to grid of 25 should be 75 (already aligned)
        assert node1.x == 75
        assert node1.y == 75


class TestNodeSizeConstraints:
    """Test node_size_constraints parameter."""

    def test_min_width_constraint(self):
        """Test minimum width constraint."""
        node1 = MockNode(0, w=50, element_type="ApplicationComponent")
        view = MockView(nodes=[node1])

        constraints = {"min_width": 100}
        config = LayoutConfig(node_size_constraints=constraints)
        result = apply_format(view, config)

        assert result.success
        # Width should be at least 100
        assert node1.w >= 100

    def test_max_height_constraint(self):
        """Test maximum height constraint."""
        node1 = MockNode(0, h=200, element_type="ApplicationComponent")
        view = MockView(nodes=[node1])

        constraints = {"max_height": 150}
        config = LayoutConfig(node_size_constraints=constraints)
        result = apply_format(view, config)

        assert result.success
        # Height should not exceed 150
        assert node1.h <= 150

    def test_all_constraints_applied(self):
        """Test all size constraints applied together."""
        node1 = MockNode(0, w=50, h=30, element_type="ApplicationComponent")
        view = MockView(nodes=[node1])

        constraints = {
            "min_width": 100,
            "max_width": 200,
            "min_height": 60,
            "max_height": 120,
        }
        config = LayoutConfig(node_size_constraints=constraints)
        result = apply_format(view, config)

        assert result.success
        assert 100 <= node1.w <= 200
        assert 60 <= node1.h <= 120


class TestLayerPriority:
    """Test layer_priority parameter."""

    def test_mandatory_layer_priority(self):
        """Test mandatory layer priority in layout."""
        # Business layer element
        node1 = MockNode(0, element_type="BusinessActor")
        # Application layer element
        node2 = MockNode(1, element_type="ApplicationComponent")
        # Technology layer element
        node3 = MockNode(2, element_type="TechnologyNode")

        view = MockView(nodes=[node1, node2, node3])

        config = LayoutConfig(algorithm="force_directed", layer_priority="mandatory")
        result = apply_layout(view, config)

        assert result.success
        assert result.quality_metrics["layer_priority"] == "mandatory"

    def test_soft_layer_priority(self):
        """Test soft layer priority in layout."""
        node1 = MockNode(0, element_type="BusinessActor")
        node2 = MockNode(1, element_type="ApplicationComponent")

        view = MockView(nodes=[node1, node2])

        config = LayoutConfig(algorithm="force_directed", layer_priority="soft")
        result = apply_layout(view, config)

        assert result.success


class TestRoutingStyle:
    """Test routing_style parameter."""

    def test_orthogonal_routing(self):
        """Test orthogonal routing style."""
        node1 = MockNode(0, element_type="BusinessActor")
        node2 = MockNode(1, element_type="ApplicationComponent")
        conn = MockConnection(0, 1)

        view = MockView(nodes=[node1, node2], conns=[conn])

        config = LayoutConfig(routing_style="orthogonal")
        result = apply_layout(view, config)

        assert result.success

    def test_mixed_45_routing(self):
        """Test mixed_45 routing style."""
        node1 = MockNode(0, element_type="BusinessActor")
        node2 = MockNode(1, element_type="ApplicationComponent")
        conn = MockConnection(0, 1)

        view = MockView(nodes=[node1, node2], conns=[conn])

        config = LayoutConfig(routing_style="mixed_45")
        result = apply_layout(view, config)

        assert result.success


class TestCombinedConfiguration:
    """Test combined configuration parameters."""

    def test_all_parameters_together(self):
        """Test using all configuration parameters simultaneously."""
        nodes = [
            MockNode(0, x=0, y=0, w=100, element_type="BusinessActor"),
            MockNode(1, x=200, y=200, w=120, element_type="ApplicationComponent"),
            MockNode(2, x=400, y=400, w=80, element_type="TechnologyNode"),
        ]
        conns = [
            MockConnection(0, 1),
            MockConnection(1, 2),
        ]
        view = MockView(nodes=nodes, conns=conns)

        config = LayoutConfig(
            algorithm="hierarchical",
            spacing=100,
            margin=50,
            alignment="grid",
            grid_size=25,
            routing_style="orthogonal",
            layer_priority="mandatory",
            excluded_element_ids=[],
            node_size_constraints={
                "min_width": 80,
                "max_width": 250,
                "min_height": 50,
                "max_height": 200,
            },
        )

        result = apply_layout(view, config)
        assert result.success

        # Also test format with the same config
        result_format = apply_format(view, config)
        assert result_format.success
        assert result_format.quality_metrics["alignment"] == "grid"
        assert result_format.quality_metrics["size_constraints_applied"]
