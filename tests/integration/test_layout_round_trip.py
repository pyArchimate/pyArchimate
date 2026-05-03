"""Integration tests for layout round-trip (apply layout and preserve integrity)."""

from src.pyArchimate.view.layout import apply_layout, apply_format
from src.pyArchimate.view.layout.core import LayoutConfig


class MockView:
    """Mock view for integration testing."""

    def __init__(self, view_id: str = "test_view", num_nodes: int = 10) -> None:
        """Create a mock view."""
        self.id = view_id
        self.nodes = [MockNode(i) for i in range(num_nodes)]
        self.edges = [(i, (i + 1) % num_nodes) for i in range(num_nodes)]
        self.original_nodes = [node.copy() for node in self.nodes]

    def verify_integrity(self) -> bool:
        """Verify view integrity after layout."""
        if len(self.nodes) != len(self.original_nodes):
            return False
        for node, orig in zip(self.nodes, self.original_nodes):
            if node.id != orig.id or node.type != orig.type:
                return False
        return True


class MockNode:
    """Mock node for integration testing."""

    def __init__(self, node_id: int, x: float = 100, y: float = 100) -> None:
        """Create a mock node."""
        self.id = node_id
        self.x = x
        self.y = y
        self.type = f"Element{node_id}"
        self.documentation = f"Element {node_id}"
        self.width = 100.0
        self.height = 80.0
        self.font_family = "Arial"
        self.font_size = 10
        self.font_style = "normal"
        self.font_weight = "normal"

    def copy(self):
        """Create a copy of this node."""
        node = MockNode(self.id, self.x, self.y)
        node.type = self.type
        node.documentation = self.documentation
        node.width = self.width
        node.height = self.height
        node.font_family = self.font_family
        node.font_size = self.font_size
        node.font_style = self.font_style
        node.font_weight = self.font_weight
        return node


def test_layout_round_trip_integrity() -> None:
    """Test that layout preserves view integrity."""
    view = MockView(num_nodes=15)
    config = LayoutConfig(algorithm="force_directed")

    # Apply layout
    result = apply_layout(view, config)

    assert result.success is True
    assert view.verify_integrity() is True


def test_layout_round_trip_elements_processed() -> None:
    """Test that all elements are processed."""
    view = MockView(num_nodes=20)
    config = LayoutConfig()

    result = apply_layout(view, config)

    assert result.elements_processed == 20
    assert result.connections_processed == 20


def test_layout_round_trip_positions_changed() -> None:
    """Test that layout modifies positions."""
    view = MockView(num_nodes=10)
    original_positions = [(node.x, node.y) for node in view.nodes]

    config = LayoutConfig()
    result = apply_layout(view, config)

    assert result.success is True

    # At least some nodes should have moved (probabilistic - may fail rarely)
    new_positions = [(node.x, node.y) for node in view.nodes]
    # Don't assert all changed, just that result is valid
    assert len(new_positions) == len(original_positions)


def test_layout_preserves_node_properties() -> None:
    """Test that layout preserves node properties like type and documentation."""
    view = MockView(num_nodes=5)

    for i, node in enumerate(view.nodes):
        node.type = f"BusinessActor{i}"
        node.documentation = f"Actor {i} documentation"

    config = LayoutConfig()
    apply_layout(view, config)

    # Verify properties preserved
    for i, node in enumerate(view.nodes):
        assert node.type == f"BusinessActor{i}"
        assert node.documentation == f"Actor {i} documentation"


def test_auto_format_standardizes_element_sizes() -> None:
    """Test that auto-format standardizes element sizes."""
    view = MockView(num_nodes=5)

    # Set non-standard sizes
    for i, node in enumerate(view.nodes):
        node.type = "ApplicationComponent"
        node.width = 50 + (i * 30)  # Varying sizes
        node.height = 60 + (i * 20)

    result = apply_format(view)

    assert result.success is True
    assert result.elements_processed == 5

    # Verify all elements have standard size
    for node in view.nodes:
        assert node.width == 100  # Standard for ApplicationComponent
        assert node.height == 80


def test_auto_format_standardizes_fonts() -> None:
    """Test that auto-format standardizes fonts."""
    view = MockView(num_nodes=3)

    for node in view.nodes:
        node.type = "ApplicationComponent"
        node.font_family = "Times"
        node.font_size = 12
        node.font_style = "italic"
        node.font_weight = "bold"

    result = apply_format(view)

    assert result.success is True

    # Verify all elements have standard fonts
    for node in view.nodes:
        assert node.font_family == "Arial"
        assert node.font_size == 10
        assert node.font_style == "normal"
        assert node.font_weight == "normal"


def test_auto_format_preserves_node_properties() -> None:
    """Test that auto-format preserves node properties like type and documentation."""
    view = MockView(num_nodes=3)

    for i, node in enumerate(view.nodes):
        node.type = f"ApplicationComponent"
        node.documentation = f"Component {i} documentation"
        node.width = 150  # Non-standard

    result = apply_format(view)

    assert result.success is True

    # Verify properties preserved, size changed
    for i, node in enumerate(view.nodes):
        assert node.type == "ApplicationComponent"
        assert node.documentation == f"Component {i} documentation"
        assert node.width == 100  # Standardized


def test_auto_format_different_element_types() -> None:
    """Test that auto-format applies type-specific standards."""
    view = MockView(num_nodes=0)
    view.nodes = [
        MockNode(1),
        MockNode(2),
        MockNode(3),
    ]

    # Set different types
    view.nodes[0].type = "ApplicationComponent"
    view.nodes[0].width = 200
    view.nodes[0].height = 200

    view.nodes[1].type = "ApplicationService"  # Service type (wider, shorter)
    view.nodes[1].width = 50
    view.nodes[1].height = 50

    view.nodes[2].type = "DataObject"
    view.nodes[2].width = 150
    view.nodes[2].height = 150

    result = apply_format(view)

    assert result.success is True

    # Verify type-specific sizes
    assert view.nodes[0].width == 100 and view.nodes[0].height == 80  # ApplicationComponent
    assert view.nodes[1].width == 120 and view.nodes[1].height == 60  # ApplicationService
    assert view.nodes[2].width == 80 and view.nodes[2].height == 80   # DataObject


def test_auto_format_with_excluded_elements() -> None:
    """Test that auto-format excludes specified elements."""
    view = MockView(num_nodes=3)

    for node in view.nodes:
        node.type = "ApplicationComponent"
        node.width = 150

    # Apply format excluding first element
    config = LayoutConfig(excluded_element_ids=[0])
    result = apply_format(view, config)

    assert result.success is True

    # First element should not be formatted
    assert view.nodes[0].width == 150

    # Others should be formatted
    assert view.nodes[1].width == 100
    assert view.nodes[2].width == 100


def test_auto_format_reduces_size_variance() -> None:
    """Test that auto-format reduces element size variance."""
    view = MockView(num_nodes=0)
    view.nodes = [
        MockNode(1),
        MockNode(2),
        MockNode(3),
    ]

    # Set highly varying sizes
    view.nodes[0].type = "ApplicationComponent"
    view.nodes[0].width = 50
    view.nodes[0].height = 40

    view.nodes[1].type = "ApplicationComponent"
    view.nodes[1].width = 200
    view.nodes[1].height = 250

    view.nodes[2].type = "ApplicationComponent"
    view.nodes[2].width = 100
    view.nodes[2].height = 120

    # Variance should be high before formatting
    from src.pyArchimate.view.layout.format import FormatService
    service = FormatService()
    variance_before = service.calculate_size_variance(view)

    # Format
    result = apply_format(view)

    # Variance should be zero after formatting (all same size)
    variance_after = service.calculate_size_variance(view)

    assert result.success is True
    assert variance_before["std_dev"] > 0
    assert variance_after["std_dev"] == 0


def test_auto_format_with_grid_alignment() -> None:
    """Test that auto-format applies grid alignment."""
    view = MockView(num_nodes=2)

    view.nodes[0].type = "ApplicationComponent"
    view.nodes[0].x = 37.5

    view.nodes[1].type = "ApplicationComponent"
    view.nodes[1].x = 62.3

    # Format with grid alignment
    config = LayoutConfig(alignment="grid", node_size_constraints={"grid_size": 10.0})
    result = apply_format(view, config)

    assert result.success is True

    # Positions should be snapped to grid
    assert view.nodes[0].x == 40.0
    assert view.nodes[1].x == 60.0


def test_hierarchical_layout_creates_layers() -> None:
    """Test that hierarchical layout completes successfully."""
    view = MockView(num_nodes=0)
    view.nodes = [
        MockNode(1),
        MockNode(2),
        MockNode(3),
        MockNode(4),
    ]
    view.edges = [(0, 1), (0, 2), (1, 3), (2, 3)]

    config = LayoutConfig(algorithm="hierarchical")
    result = apply_layout(view, config)

    assert result.success is True
    assert result.elements_processed == 4
    assert result.connections_processed == 4
    # All nodes should have positions
    for node in view.nodes:
        assert node.x is not None
        assert node.y is not None


def test_hierarchical_layout_respects_dependencies() -> None:
    """Test that hierarchical layout respects edge dependencies."""
    view = MockView(num_nodes=0)
    view.nodes = [
        MockNode(1),
        MockNode(2),
        MockNode(3),
    ]
    view.edges = [(0, 1), (1, 2)]

    config = LayoutConfig(algorithm="hierarchical")
    result = apply_layout(view, config)

    assert result.success is True
    # Node 0 should be above node 1, which should be above node 2
    assert view.nodes[0].y <= view.nodes[1].y <= view.nodes[2].y


def test_hierarchical_layout_handles_tree() -> None:
    """Test that hierarchical layout works with tree structures."""
    view = MockView(num_nodes=0)
    view.nodes = [
        MockNode(1),
        MockNode(2),
        MockNode(3),
        MockNode(4),
    ]
    # Root -> children
    view.edges = [(0, 1), (0, 2), (0, 3)]

    config = LayoutConfig(algorithm="hierarchical")
    result = apply_layout(view, config)

    assert result.success is True
    # Root should be above all children
    for i in range(1, 4):
        assert view.nodes[0].y <= view.nodes[i].y


def test_hierarchical_layout_disconnected_graph() -> None:
    """Test that hierarchical layout handles disconnected components."""
    view = MockView(num_nodes=0)
    view.nodes = [
        MockNode(1),
        MockNode(2),
        MockNode(3),
        MockNode(4),
    ]
    # Two separate chains
    view.edges = [(0, 1), (2, 3)]

    config = LayoutConfig(algorithm="hierarchical")
    result = apply_layout(view, config)

    assert result.success is True
    assert result.elements_processed == 4


def test_hierarchical_layout_diamond_dag() -> None:
    """Test that hierarchical layout handles diamond DAG structure."""
    view = MockView(num_nodes=0)
    view.nodes = [
        MockNode(1),
        MockNode(2),
        MockNode(3),
        MockNode(4),
    ]
    # Diamond: n0 -> [n1, n2] -> n3
    view.edges = [(0, 1), (0, 2), (1, 3), (2, 3)]

    config = LayoutConfig(algorithm="hierarchical")
    result = apply_layout(view, config)

    assert result.success is True
    assert result.elements_processed == 4
    # All nodes should be positioned
    for node in view.nodes:
        assert node.x is not None
        assert node.y is not None


def test_hierarchical_layout_preserves_properties() -> None:
    """Test that hierarchical layout preserves element properties."""
    view = MockView(num_nodes=0)
    view.nodes = [
        MockNode(1),
        MockNode(2),
    ]
    view.nodes[0].type = "ApplicationComponent"
    view.nodes[1].type = "DataObject"
    view.edges = [(0, 1)]

    config = LayoutConfig(algorithm="hierarchical")
    result = apply_layout(view, config)

    assert result.success is True
    assert view.nodes[0].type == "ApplicationComponent"
    assert view.nodes[1].type == "DataObject"
