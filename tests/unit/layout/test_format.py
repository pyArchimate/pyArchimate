"""Unit tests for element formatting functionality."""

from dataclasses import dataclass
from src.pyArchimate.view.layout.format import (
    FormatService,
    ElementFormatRegistry,
    ElementFormatSpec,
    ArchiMateElementCategory,
)


@dataclass
class MockElement:
    """Mock element for testing."""

    id: str
    type: str
    x: float = 0.0
    y: float = 0.0
    width: float = 100.0
    height: float = 80.0
    font_family: str = "Arial"
    font_size: int = 10
    font_style: str = "normal"
    font_weight: str = "normal"


@dataclass
class MockView:
    """Mock view for testing."""

    id: str = "test_view"
    nodes: list = None

    def __post_init__(self):
        if self.nodes is None:
            self.nodes = []


class TestElementFormatRegistry:
    """Tests for ElementFormatRegistry."""

    def test_registry_initialization(self):
        """Test that registry initializes with standard specs."""
        registry = ElementFormatRegistry()
        assert registry is not None

    def test_get_spec_for_known_type(self):
        """Test getting spec for known ArchiMate type."""
        registry = ElementFormatRegistry()
        spec = registry.get_spec("ApplicationComponent")
        assert spec is not None
        assert spec.category == ArchiMateElementCategory.APPLICATION_COMPONENT
        assert spec.default_width == 100
        assert spec.default_height == 80

    def test_get_spec_for_business_actor(self):
        """Test getting spec for BusinessActor."""
        registry = ElementFormatRegistry()
        spec = registry.get_spec("BusinessActor")
        assert spec.category == ArchiMateElementCategory.BUSINESS_ACTOR
        assert spec.default_width == 100
        assert spec.default_height == 80

    def test_get_spec_for_application_service(self):
        """Test getting spec for ApplicationService (service type with bold font)."""
        registry = ElementFormatRegistry()
        spec = registry.get_spec("ApplicationService")
        assert spec.category == ArchiMateElementCategory.APPLICATION_SERVICE
        assert spec.default_width == 120
        assert spec.default_height == 60
        assert spec.font_weight == "bold"

    def test_get_spec_for_technology_node(self):
        """Test getting spec for TechnologyNode (smaller fonts)."""
        registry = ElementFormatRegistry()
        spec = registry.get_spec("TechnologyNode")
        assert spec.category == ArchiMateElementCategory.TECHNOLOGY_NODE
        assert spec.font_size == 9

    def test_get_spec_for_unknown_type(self):
        """Test getting spec for unknown type returns default."""
        registry = ElementFormatRegistry()
        spec = registry.get_spec("UnknownElementType")
        assert spec.category == ArchiMateElementCategory.UNKNOWN
        assert spec.default_width == 100
        assert spec.default_height == 80


class TestFormatService:
    """Tests for FormatService."""

    def test_format_service_initialization(self):
        """Test FormatService initializes correctly."""
        service = FormatService()
        assert service is not None
        assert service.registry is not None

    def test_format_element_applies_standard_size(self):
        """Test that format_element applies standardized size."""
        service = FormatService()
        element = MockElement(id="elem1", type="ApplicationComponent")

        # Modify size from default
        element.width = 150
        element.height = 120

        service.format_element(element)

        # Should be reset to standard
        assert element.width == 100
        assert element.height == 80

    def test_format_element_applies_standard_font(self):
        """Test that format_element applies standardized font."""
        service = FormatService()
        element = MockElement(
            id="elem1",
            type="ApplicationComponent",
            font_family="Times",
            font_size=12,
            font_style="italic",
            font_weight="bold",
        )

        service.format_element(element)

        assert element.font_family == "Arial"
        assert element.font_size == 10
        assert element.font_style == "normal"
        assert element.font_weight == "normal"

    def test_format_element_respects_user_size_override(self):
        """Test that format_element respects user size overrides."""
        service = FormatService()
        element = MockElement(id="elem1", type="ApplicationComponent")

        service.format_element(element, user_size_override=(200, 150))

        assert element.width == 200
        assert element.height == 150

    def test_format_element_respects_user_font_override(self):
        """Test that format_element respects user font overrides."""
        service = FormatService()
        element = MockElement(id="elem1", type="ApplicationComponent")

        user_font = {
            "font_family": "Times",
            "font_size": "14",
            "font_style": "italic",
        }
        service.format_element(element, user_font_override=user_font)

        assert element.font_family == "Times"
        assert element.font_size == 14
        assert element.font_style == "italic"
        # Should still use default for non-overridden properties
        assert element.font_weight == "normal"

    def test_snap_to_grid(self):
        """Test snapping element position to grid."""
        service = FormatService()
        element = MockElement(id="elem1", type="ApplicationComponent", x=37.5, y=62.3)

        service._snap_to_grid(element, grid_size=10.0)

        assert element.x == 40.0
        assert element.y == 60.0

    def test_snap_to_grid_with_custom_size(self):
        """Test snapping with custom grid size."""
        service = FormatService()
        element = MockElement(id="elem1", type="ApplicationComponent", x=33.3, y=66.6)

        service._snap_to_grid(element, grid_size=5.0)

        assert element.x == 35.0
        assert element.y == 65.0

    def test_format_element_with_grid_alignment(self):
        """Test format_element with grid alignment."""
        service = FormatService()
        element = MockElement(
            id="elem1",
            type="ApplicationComponent",
            x=37.5,
            y=62.3,
            width=150,
            height=120,
        )

        service.format_element(element, alignment="grid", grid_size=10.0)

        # Should apply both formatting and snapping
        assert element.width == 100
        assert element.height == 80
        assert element.x == 40.0
        assert element.y == 60.0

    def test_format_view_formats_all_elements(self):
        """Test format_view formats all elements in view."""
        service = FormatService()
        view = MockView()
        view.nodes = [
            MockElement(id="elem1", type="ApplicationComponent", width=150, height=120),
            MockElement(id="elem2", type="BusinessActor", width=200, height=100),
            MockElement(id="elem3", type="TechnologyNode", width=80, height=60),
        ]

        stats = service.format_view(view)

        assert stats["formatted"] == 3
        assert stats["skipped"] == 0
        assert stats["total"] == 3

        # Verify elements were formatted
        for element in view.nodes:
            # All should have standard sizes for their types
            assert element.width > 0
            assert element.height > 0

    def test_format_view_respects_excluded_elements(self):
        """Test format_view excludes specified elements."""
        service = FormatService()
        view = MockView()
        view.nodes = [
            MockElement(id="elem1", type="ApplicationComponent", width=150, height=120),
            MockElement(id="elem2", type="BusinessActor", width=200, height=100),
        ]

        excluded = {"elem2"}
        stats = service.format_view(view, excluded_element_ids=excluded)

        assert stats["formatted"] == 1
        assert stats["skipped"] == 1

        # elem1 should be formatted
        assert view.nodes[0].width == 100

        # elem2 should not be formatted
        assert view.nodes[1].width == 200

    def test_format_view_with_grid_alignment(self):
        """Test format_view with grid alignment."""
        service = FormatService()
        view = MockView()
        view.nodes = [
            MockElement(id="elem1", type="ApplicationComponent", x=37.5, y=62.3),
            MockElement(id="elem2", type="BusinessActor", x=13.7, y=27.9),
        ]

        stats = service.format_view(view, alignment="grid", grid_size=10.0)

        assert stats["formatted"] == 2

        # Positions should be snapped
        assert view.nodes[0].x == 40.0
        assert view.nodes[0].y == 60.0
        assert view.nodes[1].x == 10.0
        assert view.nodes[1].y == 30.0

    def test_calculate_size_variance_empty_view(self):
        """Test calculating variance for empty view."""
        service = FormatService()
        view = MockView(nodes=[])

        variance = service.calculate_size_variance(view)

        assert variance["mean"] == 0
        assert variance["std_dev"] == 0
        assert variance["min"] == 0
        assert variance["max"] == 0

    def test_calculate_size_variance_single_element(self):
        """Test calculating variance with single element."""
        service = FormatService()
        view = MockView()
        view.nodes = [MockElement(id="elem1", type="ApplicationComponent", width=100, height=80)]

        variance = service.calculate_size_variance(view)

        assert variance["mean"] == 8000  # 100 * 80
        assert variance["std_dev"] == 0
        assert variance["min"] == 8000
        assert variance["max"] == 8000

    def test_calculate_size_variance_multiple_elements(self):
        """Test calculating variance with multiple elements of different sizes."""
        service = FormatService()
        view = MockView()
        view.nodes = [
            MockElement(id="elem1", type="ApplicationComponent", width=100, height=80),
            MockElement(id="elem2", type="ApplicationComponent", width=120, height=60),
            MockElement(id="elem3", type="ApplicationComponent", width=80, height=100),
        ]

        variance = service.calculate_size_variance(view)

        # Areas: 8000, 7200, 8000
        # Mean: 7733.33
        assert variance["mean"] > 0
        assert variance["std_dev"] > 0
        assert variance["min"] == 7200
        assert variance["max"] == 8000

    def test_format_view_size_variance_reduction(self):
        """Test that formatting reduces size variance."""
        service = FormatService()
        view = MockView()
        view.nodes = [
            MockElement(id="elem1", type="ApplicationComponent", width=200, height=150),
            MockElement(id="elem2", type="ApplicationComponent", width=50, height=40),
            MockElement(id="elem3", type="ApplicationComponent", width=300, height=200),
        ]

        variance_before = service.calculate_size_variance(view)
        service.format_view(view)
        variance_after = service.calculate_size_variance(view)

        # After formatting, all should be 100x80, so variance should be 0
        assert variance_after["std_dev"] == 0
        assert variance_before["std_dev"] > variance_after["std_dev"]

    def test_format_service_handles_missing_attributes(self):
        """Test that FormatService handles elements with missing attributes."""
        service = FormatService()

        class MinimalElement:
            id = "elem1"

        element = MinimalElement()

        # Should not raise an exception
        service.format_element(element)

    def test_format_different_element_types(self):
        """Test formatting different ArchiMate element types."""
        service = FormatService()

        types_and_expected = [
            ("BusinessActor", 100, 80),
            ("ApplicationComponent", 100, 80),
            ("TechnologyNode", 100, 80),
            ("ApplicationService", 120, 60),
            ("DataObject", 80, 80),
        ]

        for elem_type, expected_width, expected_height in types_and_expected:
            element = MockElement(id="test", type=elem_type)
            element.width = 999
            element.height = 999

            service.format_element(element)

            assert (
                element.width == expected_width
            ), f"{elem_type} width should be {expected_width}"
            assert (
                element.height == expected_height
            ), f"{elem_type} height should be {expected_height}"


class TestElementFormatSpec:
    """Tests for ElementFormatSpec."""

    def test_format_spec_creation(self):
        """Test creating a format spec."""
        spec = ElementFormatSpec(
            category=ArchiMateElementCategory.APPLICATION_COMPONENT,
            default_width=100,
            default_height=80,
            font_family="Arial",
            font_size=10,
            font_style="normal",
            font_weight="normal",
        )

        assert spec.category == ArchiMateElementCategory.APPLICATION_COMPONENT
        assert spec.default_width == 100
        assert spec.default_height == 80
        assert spec.font_family == "Arial"
        assert spec.font_size == 10
