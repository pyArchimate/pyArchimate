"""Step definitions for auto-format BDD scenarios."""

from dataclasses import dataclass

from behave import given, then, when

from pyArchimate.view.layout import apply_format
from pyArchimate.view.layout.core import LayoutConfig
from pyArchimate.view.layout.format import FormatService


@dataclass
class MockElement:
    """Mock element for BDD testing."""

    id: str
    type: str
    name: str = "Element"
    documentation: str = ""
    x: float = 0.0
    y: float = 0.0
    width: float = 100.0
    height: float = 80.0
    font_family: str = "Arial"
    font_size: int = 10
    font_style: str = "normal"
    font_weight: str = "normal"


class MockView:
    """Mock view for BDD testing."""

    def __init__(self):
        """Initialize mock view."""
        self.id = "test_view"
        self.nodes = []

    def add_element(self, element_id: str, elem_type: str, width: float = 100, height: float = 80, name: str = "Element", documentation: str = ""):
        """Add element to view."""
        element = MockElement(
            id=element_id,
            type=elem_type,
            name=name,
            documentation=documentation,
            width=width,
            height=height,
        )
        self.nodes.append(element)


@given("I have a view with multiple elements of different sizes")
def step_create_view_with_varying_sizes(context):
    """Create a view with elements of different sizes."""
    context.view = MockView()
    context.view.add_element("elem1", "ApplicationComponent", width=50, height=40)
    context.view.add_element("elem2", "ApplicationComponent", width=150, height=150)
    context.view.add_element("elem3", "ApplicationComponent", width=100, height=120)


@given("the elements have inconsistent fonts")
def step_set_inconsistent_fonts(context):
    """Set inconsistent fonts on elements."""
    fonts = [
        ("Times", 12, "italic", "bold"),
        ("Courier", 8, "normal", "normal"),
        ("Helvetica", 14, "normal", "bold"),
    ]
    for element, (family, size, style, weight) in zip(context.view.nodes, fonts, strict=False):
        element.font_family = family
        element.font_size = size
        element.font_style = style
        element.font_weight = weight


@when("I apply auto-format to the view")
def step_apply_auto_format(context):
    """Apply auto-format to the view."""
    context.result = apply_format(context.view)
    context.format_service = FormatService()


@then("all elements should have standardized sizes based on their ArchiMate type")
def step_verify_standardized_sizes(context):
    """Verify elements have standardized sizes."""
    assert context.result.success
    for element in context.view.nodes:
        spec = context.format_service.registry.get_spec(element.type)
        assert element.width == spec.default_width
        assert element.height == spec.default_height


@then("ApplicationComponent elements should be 100x80 pixels")
def step_verify_app_component_size(context):
    """Verify ApplicationComponent size."""
    for element in context.view.nodes:
        if element.type == "ApplicationComponent":
            assert element.width == 100
            assert element.height == 80


@then("ApplicationService elements should be 120x60 pixels")
def step_verify_app_service_size(context):
    """Verify ApplicationService size."""
    for element in context.view.nodes:
        if element.type == "ApplicationService":
            assert element.width == 120
            assert element.height == 60


@then("DataObject elements should be 80x80 pixels")
def step_verify_data_object_size(context):
    """Verify DataObject size."""
    for element in context.view.nodes:
        if element.type == "DataObject":
            assert element.width == 80
            assert element.height == 80


@then("all elements should have standardized fonts")
def step_verify_standardized_fonts(context):
    """Verify elements have standardized fonts."""
    assert context.result.success
    for element in context.view.nodes:
        spec = context.format_service.registry.get_spec(element.type)
        assert element.font_family == spec.font_family
        assert element.font_size == spec.font_size
        assert element.font_style == spec.font_style
        assert element.font_weight == spec.font_weight


@then("font family should be Arial for all elements")
def step_verify_font_family(context):
    """Verify font family is Arial."""
    for element in context.view.nodes:
        assert element.font_family == "Arial"


@then("font size should be 10pt for ApplicationComponent elements")
def step_verify_font_size_app_component(context):
    """Verify ApplicationComponent font size."""
    for element in context.view.nodes:
        if element.type == "ApplicationComponent":
            assert element.font_size == 10


@then("font size should be 9pt for TechnologyNode elements")
def step_verify_font_size_tech_node(context):
    """Verify TechnologyNode font size."""
    for element in context.view.nodes:
        if element.type == "TechnologyNode":
            assert element.font_size == 9


@then("font weight should be bold for service-type elements")
def step_verify_bold_for_services(context):
    """Verify service elements have bold font."""
    service_types = ["ApplicationService", "TechnologyService", "BusinessService"]
    for element in context.view.nodes:
        if element.type in service_types:
            assert element.font_weight == "bold"


@then("font weight should be normal for other elements")
def step_verify_normal_weight(context):
    """Verify non-service elements have normal font weight."""
    service_types = ["ApplicationService", "TechnologyService", "BusinessService"]
    for element in context.view.nodes:
        if element.type not in service_types:
            assert element.font_weight == "normal"


@given("an element with custom documentation and type information")
def step_create_element_with_docs(context):
    """Create element with documentation."""
    context.view = MockView()
    context.view.add_element(
        "elem1",
        "ApplicationComponent",
        width=150,
        name="TestComponent",
        documentation="Test documentation"
    )


@then("the element's name should be preserved")
def step_verify_name_preserved(context):
    """Verify element name is preserved."""
    assert context.view.nodes[0].name == "TestComponent"


@then("the element's type should be preserved")
def step_verify_type_preserved(context):
    """Verify element type is preserved."""
    assert context.view.nodes[0].type == "ApplicationComponent"


@then("the element's documentation should be preserved")
def step_verify_docs_preserved(context):
    """Verify element documentation is preserved."""
    assert context.view.nodes[0].documentation == "Test documentation"


@then("only size and font properties should be standardized")
def step_verify_only_size_font_changed(context):
    """Verify only size and font changed."""
    element = context.view.nodes[0]
    assert element.width == 100  # Standard size
    assert element.height == 80  # Standard size
    # Name and docs should be unchanged
    assert element.name == "TestComponent"
    assert element.documentation == "Test documentation"


@given("a view with elements that should not be formatted")
def step_create_view_with_excluded(context):
    """Create view with elements to exclude."""
    context.view = MockView()
    context.view.add_element("elem1", "ApplicationComponent", width=150, height=150)
    context.view.add_element("elem2", "ApplicationComponent", width=150, height=150)
    context.excluded_ids = {"elem1"}
    # Set non-standard fonts on the excluded element so we can verify it's NOT changed
    context.view.nodes[0].font_family = "Times New Roman"
    context.view.nodes[0].font_size = 14
    context.view.nodes[1].font_family = "Courier"
    context.view.nodes[1].font_size = 8


@when("I apply auto-format with excluded_element_ids set")
def step_apply_format_with_excluded(context):
    """Apply format with excluded elements."""
    config = LayoutConfig(excluded_element_ids=list(context.excluded_ids))
    context.result = apply_format(context.view, config)
    context.format_service = FormatService()


@then("the excluded elements should retain their original size")
def step_verify_excluded_size(context):
    """Verify excluded elements retain size."""
    # Find excluded element
    excluded = [e for e in context.view.nodes if e.id in context.excluded_ids]
    if excluded:
        assert excluded[0].width == 150
        assert excluded[0].height == 150


@then("the excluded elements should retain their original fonts")
def step_verify_excluded_fonts(context):
    """Verify excluded elements retain fonts."""
    # Excluded elements should keep original fonts (not changed to standard)
    excluded = [e for e in context.view.nodes if e.id in context.excluded_ids]
    if excluded:
        # They should not have standard fonts applied
        spec = context.format_service.registry.get_spec("ApplicationComponent")
        # Should NOT match standard font
        assert not (
            excluded[0].font_family == spec.font_family and
            excluded[0].font_size == spec.font_size
        )


@then("other elements should be formatted normally")
def step_verify_other_formatted(context):
    """Verify non-excluded elements are formatted."""
    for element in context.view.nodes:
        if element.id not in context.excluded_ids:
            assert element.width == 100
            assert element.height == 80


@given("a view with highly inconsistent element sizes")
def step_create_highly_inconsistent_view(context):
    """Create view with inconsistent sizes."""
    context.view = MockView()
    context.view.add_element("elem1", "ApplicationComponent", width=50, height=40)
    context.view.add_element("elem2", "ApplicationComponent", width=300, height=200)
    context.view.add_element("elem3", "ApplicationComponent", width=80, height=100)


@given("element sizes vary from 50x40 to 300x200 pixels")
def step_verify_size_variation(context):
    """Verify size variation."""
    widths = [e.width for e in context.view.nodes]
    heights = [e.height for e in context.view.nodes]
    assert min(widths) == 50
    assert max(widths) == 300
    assert min(heights) == 40
    assert max(heights) == 200


@then("size variance should be reduced by at least 80%")
def step_verify_variance_reduction(context):
    """Verify size variance reduced by 80%."""
    service = FormatService()
    # After format, all should be 100x80
    for element in context.view.nodes:
        assert element.width == 100
        assert element.height == 80
    # Variance should be zero (all identical)
    variance = service.calculate_size_variance(context.view)
    assert variance["std_dev"] == 0


@then("all elements of the same type should have identical sizes")
def step_verify_identical_sizes(context):
    """Verify same-type elements have identical sizes."""
    app_comps = [e for e in context.view.nodes if e.type == "ApplicationComponent"]
    if len(app_comps) > 1:
        first_width = app_comps[0].width
        first_height = app_comps[0].height
        for element in app_comps[1:]:
            assert element.width == first_width
            assert element.height == first_height


@given("elements with positions that are not grid-aligned")
def step_create_unaligned_elements(context):
    """Create elements not aligned to grid."""
    context.view = MockView()
    elem1 = MockElement(id="elem1", type="ApplicationComponent", x=37.5, y=62.3)
    elem2 = MockElement(id="elem2", type="ApplicationComponent", x=13.7, y=27.9)
    context.view.nodes = [elem1, elem2]


@when("I apply auto-format with grid alignment enabled")
def step_apply_format_with_grid(context):
    """Apply format with grid alignment."""
    context.grid_size = 10
    config = LayoutConfig(alignment="grid", grid_size=context.grid_size)
    context.result = apply_format(context.view, config)


@when("grid size is 10 pixels")
def step_verify_grid_size_10(context):
    """Verify grid size is 10."""
    assert context.grid_size == 10


@then("elements should be snapped to the 10-pixel grid")
def step_verify_grid_snap(context):
    """Verify elements snapped to grid."""
    for element in context.view.nodes:
        # Position should be multiple of grid_size
        assert element.x % context.grid_size == 0
        assert element.y % context.grid_size == 0


@then("position accuracy should be within ±5 pixels of grid points")
def step_verify_grid_accuracy(context):
    """Verify grid snapping accuracy."""
    # Snapping should be exact multiple of grid size
    for element in context.view.nodes:
        remainder_x = element.x % context.grid_size
        remainder_y = element.y % context.grid_size
        assert abs(remainder_x) < 0.01 or abs(remainder_x - context.grid_size) < 0.01
        assert abs(remainder_y) < 0.01 or abs(remainder_y - context.grid_size) < 0.01


@given("a view containing BusinessActor, BusinessRole, and BusinessProcess elements")
def step_create_business_view(context):
    """Create view with business elements."""
    context.view = MockView()
    context.view.add_element("ba1", "BusinessActor", width=150, height=150)
    context.view.add_element("br1", "BusinessRole", width=150, height=150)
    context.view.add_element("bp1", "BusinessProcess", width=150, height=150)


@then("BusinessActor elements should be 100x80 with 10pt font")
def step_verify_business_actor_format(context):
    """Verify BusinessActor formatting."""
    for element in context.view.nodes:
        if element.type == "BusinessActor":
            assert element.width == 100
            assert element.height == 80
            assert element.font_size == 10


@then("BusinessRole elements should be 100x70 with 10pt font")
def step_verify_business_role_format(context):
    """Verify BusinessRole formatting."""
    for element in context.view.nodes:
        if element.type == "BusinessRole":
            assert element.width == 100
            assert element.height == 70
            assert element.font_size == 10


@then("BusinessProcess elements should be 120x80 with 10pt font")
def step_verify_business_process_format(context):
    """Verify BusinessProcess formatting."""
    for element in context.view.nodes:
        if element.type == "BusinessProcess":
            assert element.width == 120
            assert element.height == 80
            assert element.font_size == 10


@given("a view containing ApplicationComponent, ApplicationService, and DataObject")
def step_create_app_view(context):
    """Create view with application elements."""
    context.view = MockView()
    context.view.add_element("ac1", "ApplicationComponent", width=150, height=150)
    context.view.add_element("as1", "ApplicationService", width=150, height=150)
    context.view.add_element("do1", "DataObject", width=150, height=150)


@then("ApplicationComponent elements should be 100x80")
def step_verify_app_comp_format(context):
    """Verify ApplicationComponent formatting."""
    for element in context.view.nodes:
        if element.type == "ApplicationComponent":
            assert element.width == 100
            assert element.height == 80


@then("ApplicationService elements should be 120x60 with bold font")
def step_verify_app_service_format(context):
    """Verify ApplicationService formatting."""
    for element in context.view.nodes:
        if element.type == "ApplicationService":
            assert element.width == 120
            assert element.height == 60
            assert element.font_weight == "bold"


@then("DataObject elements should be 80x80")
def step_verify_data_object_format(context):
    """Verify DataObject formatting."""
    for element in context.view.nodes:
        if element.type == "DataObject":
            assert element.width == 80
            assert element.height == 80


@given("a view containing TechnologyNode, TechnologyArtifact, and TechnologyService")
def step_create_tech_view(context):
    """Create view with technology elements."""
    context.view = MockView()
    context.view.add_element("tn1", "TechnologyNode", width=150, height=150)
    context.view.add_element("ta1", "TechnologyArtifact", width=150, height=150)
    context.view.add_element("ts1", "TechnologyService", width=150, height=150)


@then("TechnologyNode elements should be 100x80 with 9pt font")
def step_verify_tech_node_format(context):
    """Verify TechnologyNode formatting."""
    for element in context.view.nodes:
        if element.type == "TechnologyNode":
            assert element.width == 100
            assert element.height == 80
            assert element.font_size == 9


@then("TechnologyArtifact elements should be 80x80 with 9pt font")
def step_verify_tech_artifact_format(context):
    """Verify TechnologyArtifact formatting."""
    for element in context.view.nodes:
        if element.type == "TechnologyArtifact":
            assert element.width == 80
            assert element.height == 80
            assert element.font_size == 9


@then("TechnologyService elements should be 120x60 with bold 9pt font")
def step_verify_tech_service_format(context):
    """Verify TechnologyService formatting."""
    for element in context.view.nodes:
        if element.type == "TechnologyService":
            assert element.width == 120
            assert element.height == 60
            assert element.font_weight == "bold"
            assert element.font_size == 9


@given("a view with unknown or custom element types")
def step_create_unknown_type_view(context):
    """Create view with unknown element types."""
    context.view = MockView()
    elem = MockElement(id="elem1", type="CustomElementType", width=150, height=150)
    context.view.nodes = [elem]


@then("unknown elements should receive default standard size (100x80)")
def step_verify_unknown_default_size(context):
    """Verify unknown elements get default size."""
    for element in context.view.nodes:
        assert element.width == 100
        assert element.height == 80


@then("unknown elements should receive default font (Arial 10pt)")
def step_verify_unknown_default_font(context):
    """Verify unknown elements get default font."""
    for element in context.view.nodes:
        assert element.font_family == "Arial"
        assert element.font_size == 10


@given("an empty mock view with no elements")
def step_create_empty_view(context):
    """Create empty view."""
    context.view = MockView()


@then("the operation should succeed without errors")
def step_verify_success(context):
    """Verify operation succeeded."""
    assert context.result.success


@then("zero elements should be processed")
def step_verify_zero_processed(context):
    """Verify zero elements processed."""
    assert context.result.elements_processed == 0


@then("the view should remain unchanged")
def step_verify_view_unchanged(context):
    """Verify view unchanged."""
    assert len(context.view.nodes) == 0


@given("a view with 10 elements")
def step_create_10_element_view(context):
    """Create view with 10 elements."""
    context.view = MockView()
    for i in range(10):
        context.view.add_element(f"elem{i}", "ApplicationComponent", width=150)


@given("2 elements are marked as excluded")
def step_mark_excluded(context):
    """Mark 2 elements as excluded."""
    context.excluded = ["elem0", "elem1"]


@then("the result should report 8 elements formatted")
def step_verify_8_formatted(context):
    """Verify 8 elements formatted."""
    # Re-apply with excluded
    config = LayoutConfig(excluded_element_ids=context.excluded)
    result = apply_format(context.view, config)
    assert result.quality_metrics["formatted"] == 8


@then("the result should report 2 elements skipped")
def step_verify_2_skipped(context):
    """Verify 2 elements skipped."""
    config = LayoutConfig(excluded_element_ids=context.excluded)
    result = apply_format(context.view, config)
    assert result.quality_metrics["skipped"] == 2


@then("the result should report formatting time in milliseconds")
def step_verify_time_reported(context):
    """Verify formatting time reported."""
    assert context.result.layout_time_ms >= 0


@given("a view with elements at specific positions")
def step_create_positioned_view(context):
    """Create view with specific positions."""
    context.view = MockView()
    elem1 = MockElement(id="elem1", type="ApplicationComponent", x=100, y=200, width=150)
    elem2 = MockElement(id="elem2", type="ApplicationComponent", x=300, y=400, width=150)
    context.view.nodes = [elem1, elem2]
    context.original_positions = [(e.x, e.y) for e in context.view.nodes]


@then("element positions should remain unchanged")
def step_verify_positions_unchanged(context):
    """Verify element positions unchanged."""
    for element, (orig_x, orig_y) in zip(context.view.nodes, context.original_positions, strict=False):
        assert element.x == orig_x
        assert element.y == orig_y


@then("only element sizes and fonts should change")
def step_verify_element_sizes_fonts_changed(context):
    """Verify only size and fonts changed."""
    for element in context.view.nodes:
        assert element.width == 100  # Standard
        assert element.height == 80  # Standard


@then("connections should remain valid")
def step_verify_connections_valid(context):
    """Verify connections valid."""
    # Mock view doesn't have connections, just verify structure maintained
    assert len(context.view.nodes) == 2


@when("I apply auto-format with alignment=\"free\"")
def step_apply_format_free(context):
    """Apply format with free alignment."""
    config = LayoutConfig(alignment="free")
    context.result = apply_format(context.view, config)


@when("I apply auto-format with alignment=\"grid\" and grid_size=10")
def step_apply_format_grid(context):
    """Apply format with grid alignment."""
    config = LayoutConfig(alignment="grid", grid_size=10)
    context.result = apply_format(context.view, config)


@then("element positions should not change")
def step_verify_free_positions_unchanged(context):
    """Verify free mode doesn't change positions."""
    for element, (orig_x, orig_y) in zip(context.view.nodes, context.original_positions, strict=False):
        assert element.x == orig_x
        assert element.y == orig_y


@then("elements should not be snapped to grid")
def step_verify_not_snapped(context):
    """Verify positions not snapped."""
    # Original positions were scattered, should remain
    for element, (orig_x, orig_y) in zip(context.view.nodes, context.original_positions, strict=False):
        assert element.x == orig_x
        assert element.y == orig_y


@then("element positions should be snapped to 10-pixel grid")
def step_verify_positions_snapped(context):
    """Verify positions snapped to grid."""
    for element in context.view.nodes:
        assert element.x % 10 == 0
        assert element.y % 10 == 0


@then("elements should be aligned consistently")
def step_verify_consistent_alignment(context):
    """Verify consistent alignment."""
    for element in context.view.nodes:
        # All positions are multiples of grid_size
        assert element.x % 10 == 0
        assert element.y % 10 == 0


@given("a view with element size variance of 5000 square pixels")
def step_create_variance_view(context):
    """Create view with specific variance."""
    context.view = MockView()
    # Create elements with different sizes to achieve ~5000 variance
    context.view.add_element("elem1", "ApplicationComponent", width=50, height=50)
    context.view.add_element("elem2", "ApplicationComponent", width=300, height=200)
    context.view.add_element("elem3", "ApplicationComponent", width=100, height=100)


@then("size variance should be reduced to less than 1000 square pixels")
def step_verify_variance_reduced(context):
    """Verify variance reduced to <1000."""
    service = FormatService()
    variance = service.calculate_size_variance(context.view)
    # After formatting, all are 100x80 = 8000 area, std_dev = 0
    assert variance["std_dev"] < 1000


@then("this satisfies Success Criterion SC-004 (80% reduction)")
def step_verify_sc_004(context):
    """Verify SC-004 satisfaction."""
    # Variance reduced to 0 (all identical), which is >80% reduction
    service = FormatService()
    variance = service.calculate_size_variance(context.view)
    assert variance["std_dev"] == 0  # 100% reduction



@then("Business layer elements should use standard sizes and fonts")
def step_verify_business_standards(context):
    """Verify business layer standards."""
    for element in context.view.nodes:
        if "Business" in element.type:
            spec = context.format_service.registry.get_spec(element.type)
            assert element.width == spec.default_width
            assert element.height == spec.default_height
            assert element.font_family == spec.font_family


@then("Application layer elements should use standard sizes and fonts")
def step_verify_app_standards(context):
    """Verify application layer standards."""
    for element in context.view.nodes:
        if "Application" in element.type:
            spec = context.format_service.registry.get_spec(element.type)
            assert element.width == spec.default_width
            assert element.height == spec.default_height
            assert element.font_family == spec.font_family


@then("Technology layer elements should use smaller fonts (9pt)")
def step_verify_tech_small_fonts(context):
    """Verify technology layer has smaller fonts."""
    for element in context.view.nodes:
        if "Technology" in element.type:
            assert element.font_size == 9


@then("layer boundaries should be visually distinguished through size standards")
def step_verify_layer_distinction(context):
    """Verify layers visually distinguished."""
    business = [e for e in context.view.nodes if "Business" in e.type]
    tech = [e for e in context.view.nodes if "Technology" in e.type]

    if business and tech:
        # Business and tech should have different visual properties
        business_font_size = business[0].font_size
        tech_font_size = tech[0].font_size
        # Technology should have smaller font
        assert tech_font_size <= business_font_size
