"""Unit tests for SVGExportService utility methods — covering previously untested paths."""

from types import SimpleNamespace
from xml.etree import ElementTree as ET

import pytest

from src.pyArchimate.view.layout.export.svg_export import SVGExportService
from src.pyArchimate.view.layout.export.symbols.archimate_relationships import RelationshipStyleService
from src.pyArchimate.view.layout.export.symbols.archimate_symbols import (
    ARCHIMATE_SYMBOLS,
    get_all_symbols,
    get_symbol,
    validate_symbols,
)
from src.pyArchimate.view.layout.export.symbols.color_palette import ColorPalette


@pytest.fixture
def svc() -> SVGExportService:
    return SVGExportService()


# ── helpers ───────────────────────────────────────────────────────────────────

def make_node(uuid="n1", x=0.0, y=0.0, w=120.0, h=55.0, element_type="BusinessActor",
              name="Test", nodes=None, fill_color=None, **kwargs):
    return SimpleNamespace(
        uuid=uuid, x=x, y=y, w=w, h=h,
        type=element_type, name=name, label=name,
        nodes=nodes or [],
        fill_color=fill_color,
        _ref=None,
        **kwargs,
    )


def make_view(nodes=None, conns=None, nodes_dict=None):
    ns = nodes or []
    return SimpleNamespace(
        nodes=ns,
        conns=conns or [],
        nodes_dict={n.uuid: n for n in ns} if nodes_dict is None else nodes_dict,
    )


# ── TestZOrderDuplicateGuard ──────────────────────────────────────────────────

class TestZOrderDuplicateGuard:
    def test_same_node_twice_in_root_list_deduped(self, svc):
        node = SimpleNamespace(uuid="n1", nodes=[])
        view = SimpleNamespace(nodes=[node, node])
        result = svc._sort_nodes_by_hierarchy(view)
        assert len(result) == 1


# ── TestWordWrapText ──────────────────────────────────────────────────────────

class TestWordWrapText:
    def test_empty_string_returns_singleton(self, svc):
        assert svc._word_wrap_text("", 100) == [""]

    def test_short_text_single_line(self, svc):
        assert svc._word_wrap_text("Hello", 100) == ["Hello"]

    def test_wraps_at_width_boundary(self, svc):
        # chars_per_line = int(60/6) = 10; "Hello World" (11) wraps
        lines = svc._word_wrap_text("Hello World Again", 60)
        assert len(lines) >= 2
        assert "Hello" in lines[0]

    def test_each_long_word_on_own_line(self, svc):
        # chars_per_line=1: every word exceeds limit → each word alone
        lines = svc._word_wrap_text("AB CD EF", 6)
        assert lines == ["AB", "CD", "EF"]

    def test_no_wrap_needed_for_large_width(self, svc):
        assert svc._word_wrap_text("Short text here", 1000) == ["Short text here"]

    def test_word_longer_than_limit_still_added(self, svc):
        lines = svc._word_wrap_text("Superlongword", 6)
        assert lines == ["Superlongword"]

    def test_flushed_line_before_new_word(self, svc):
        # "Hello World": "Hello World" > 10, so "Hello" flushed, "World" starts new line
        lines = svc._word_wrap_text("Hello World", 60)
        assert lines[0] == "Hello"
        assert lines[1] == "World"


# ── TestIsContainmentRelationship ─────────────────────────────────────────────

class TestIsContainmentRelationship:
    def test_non_containment_type(self, svc):
        conn = SimpleNamespace(_source="s", _target="t", type="FlowRelationship")
        assert svc._is_containment_relationship(conn, {}) is False

    def test_missing_source_uuid(self, svc):
        conn = SimpleNamespace(_source=None, _target="t", type="CompositionRelationship")
        assert svc._is_containment_relationship(conn, {}) is False

    def test_missing_target_uuid(self, svc):
        conn = SimpleNamespace(_source="s", _target=None, type="CompositionRelationship")
        assert svc._is_containment_relationship(conn, {}) is False

    def test_source_missing_from_dict(self, svc):
        conn = SimpleNamespace(_source="s", _target="t", type="CompositionRelationship")
        assert svc._is_containment_relationship(conn, {"t": make_node("t")}) is False

    def test_target_missing_from_dict(self, svc):
        conn = SimpleNamespace(_source="s", _target="t", type="CompositionRelationship")
        assert svc._is_containment_relationship(conn, {"s": make_node("s")}) is False

    def test_target_not_a_child_of_source(self, svc):
        child = make_node("t")
        parent = make_node("s", nodes=[])
        conn = SimpleNamespace(_source="s", _target="t", type="CompositionRelationship")
        assert svc._is_containment_relationship(conn, {"s": parent, "t": child}) is False

    def test_target_is_child_returns_true(self, svc):
        child = make_node("t")
        parent = make_node("s", nodes=[child])
        conn = SimpleNamespace(_source="s", _target="t", type="CompositionRelationship")
        assert svc._is_containment_relationship(conn, {"s": parent, "t": child}) is True

    def test_aggregation_containment(self, svc):
        child = make_node("t")
        parent = make_node("s", nodes=[child])
        conn = SimpleNamespace(_source="s", _target="t", type="AggregationRelationship")
        assert svc._is_containment_relationship(conn, {"s": parent, "t": child}) is True

    def test_short_type_names_accepted(self, svc):
        child = make_node("t")
        parent = make_node("s", nodes=[child])
        for short in ("Composition", "Aggregation"):
            conn = SimpleNamespace(_source="s", _target="t", type=short)
            assert svc._is_containment_relationship(conn, {"s": parent, "t": child}) is True


# ── TestCalculateBounds ───────────────────────────────────────────────────────

class TestCalculateBounds:
    def test_empty_view_returns_early_with_initial_values(self, svc):
        # Empty nodes → defaults to 100x100
        bounds = svc._calculate_bounds(make_view())
        assert bounds["min_x"] == 0.0
        assert bounds["max_x"] == 100.0
        assert bounds["min_y"] == 0.0
        assert bounds["max_y"] == 100.0

    def test_single_node(self, svc):
        node = make_node(x=10.0, y=20.0, w=100.0, h=50.0)
        bounds = svc._calculate_bounds(make_view(nodes=[node]))
        # With 5% safety margin: span_x=100, span_y=50; margin_x=5, margin_y=2.5
        assert bounds["min_x"] == pytest.approx(5.0)
        assert bounds["min_y"] == pytest.approx(17.5)
        assert bounds["max_x"] == pytest.approx(115.0)
        assert bounds["max_y"] == pytest.approx(72.5)

    def test_multiple_nodes_envelope(self, svc):
        n1 = make_node("n1", x=0.0, y=0.0, w=50.0, h=30.0)
        n2 = make_node("n2", x=100.0, y=80.0, w=60.0, h=40.0)
        bounds = svc._calculate_bounds(make_view(nodes=[n1, n2]))
        # Without margin: min_x=0, max_x=160, min_y=0, max_y=120
        # With 5% safety margin: span_x=160, span_y=120; margin_x=8, margin_y=6
        assert bounds["min_x"] == pytest.approx(-8.0)
        assert bounds["max_x"] == pytest.approx(168.0)
        assert bounds["max_y"] == pytest.approx(126.0)


# ── TestGetNodeBounds ─────────────────────────────────────────────────────────

class TestGetNodeBounds:
    def test_unknown_symbol_falls_back_to_rect(self, svc):
        node = make_node(element_type="UnknownWidget", x=10.0, y=20.0, w=80.0, h=40.0)
        assert svc._get_node_bounds(node) == pytest.approx((10.0, 20.0, 90.0, 60.0))

    def test_known_symbol_returns_scaled_bounds(self, svc):
        node = make_node(element_type="BusinessActor", x=0.0, y=0.0, w=120.0, h=55.0)
        x1, y1, x2, y2 = svc._get_node_bounds(node)
        assert x2 > x1 and y2 > y1

    def test_larger_node_produces_larger_bounds(self, svc):
        small = make_node("s", element_type="BusinessActor", x=0.0, y=0.0, w=60.0, h=30.0)
        large = make_node("l", element_type="BusinessActor", x=0.0, y=0.0, w=240.0, h=110.0)
        sb = svc._get_node_bounds(small)
        lb = svc._get_node_bounds(large)
        assert (lb[2] - lb[0]) > (sb[2] - sb[0])


# ── TestBuildCompleteNodesDict ────────────────────────────────────────────────

class TestBuildCompleteNodesDict:
    def test_flat_view_includes_all_root_nodes(self, svc):
        n1, n2 = make_node("n1"), make_node("n2")
        result = svc._build_complete_nodes_dict(make_view(nodes=[n1, n2]))
        assert "n1" in result and "n2" in result

    def test_nested_child_included(self, svc):
        child = make_node("c")
        parent = make_node("p", nodes=[child])
        view = make_view(nodes=[parent], nodes_dict={"p": parent})
        result = svc._build_complete_nodes_dict(view)
        assert "c" in result

    def test_deeply_nested_included(self, svc):
        gc = make_node("gc")
        child = make_node("c", nodes=[gc])
        parent = make_node("p", nodes=[child])
        view = make_view(nodes=[parent], nodes_dict={"p": parent})
        assert "gc" in svc._build_complete_nodes_dict(view)


# ── TestFindLongestSegment ────────────────────────────────────────────────────

class TestFindLongestSegment:
    def test_empty_list_returns_none(self, svc):
        assert svc._find_longest_segment([]) is None

    def test_single_point_returns_none(self, svc):
        assert svc._find_longest_segment([(0.0, 0.0)]) is None

    def test_two_points_returns_zero(self, svc):
        assert svc._find_longest_segment([(0.0, 0.0), (10.0, 0.0)]) == 0

    def test_returns_index_of_longest_segment(self, svc):
        # segments: 0→1 len=5, 1→2 len=10, 2→3 len=5
        pts = [(0.0, 0.0), (5.0, 0.0), (15.0, 0.0), (20.0, 0.0)]
        assert svc._find_longest_segment(pts) == 1

    def test_all_zero_length_returns_zero(self, svc):
        pts = [(5.0, 5.0), (5.0, 5.0), (5.0, 5.0)]
        assert svc._find_longest_segment(pts) == 0


# ── TestGetShortTypeName ──────────────────────────────────────────────────────

class TestGetShortTypeName:
    def test_strips_relationship_suffix(self, svc):
        assert svc._get_short_type_name("FlowRelationship") == "Flow"

    def test_no_suffix_unchanged(self, svc):
        assert svc._get_short_type_name("Flow") == "Flow"

    def test_influence_relationship(self, svc):
        assert svc._get_short_type_name("InfluenceRelationship") == "Influence"


# ── TestBoundarySide ──────────────────────────────────────────────────────────

BOUNDS = (10.0, 20.0, 110.0, 70.0)


class TestBoundarySide:
    def test_top_edge(self):
        assert SVGExportService._boundary_side(BOUNDS, (50.0, 20.0)) == "top"

    def test_bottom_edge(self):
        assert SVGExportService._boundary_side(BOUNDS, (50.0, 70.0)) == "bottom"

    def test_left_edge(self):
        assert SVGExportService._boundary_side(BOUNDS, (10.0, 45.0)) == "left"

    def test_right_edge(self):
        assert SVGExportService._boundary_side(BOUNDS, (110.0, 45.0)) == "right"

    def test_interior_returns_none(self):
        assert SVGExportService._boundary_side(BOUNDS, (60.0, 45.0)) is None


# ── TestBoundaryStub ──────────────────────────────────────────────────────────

class TestBoundaryStub:
    def test_top_stub_moves_up(self):
        _, y = SVGExportService._boundary_stub((50.0, 20.0), "top")
        assert y == pytest.approx(12.0)

    def test_bottom_stub_moves_down(self):
        _, y = SVGExportService._boundary_stub((50.0, 70.0), "bottom")
        assert y == pytest.approx(78.0)

    def test_left_stub_moves_left(self):
        x, _ = SVGExportService._boundary_stub((10.0, 45.0), "left")
        assert x == pytest.approx(2.0)

    def test_right_stub_moves_right(self):
        x, _ = SVGExportService._boundary_stub((110.0, 45.0), "right")
        assert x == pytest.approx(118.0)

    def test_unknown_side_unchanged(self):
        assert SVGExportService._boundary_stub((50.0, 50.0), "unknown") == (50.0, 50.0)

    def test_custom_length(self):
        _, y = SVGExportService._boundary_stub((50.0, 20.0), "top", length=20.0)
        assert y == pytest.approx(0.0)


# ── TestBoundaryAnchor ────────────────────────────────────────────────────────

class TestBoundaryAnchor:
    def test_top_side_places_y_at_y1(self, svc):
        _, y = svc._boundary_anchor(BOUNDS, "top", (0.0, 0.0))
        assert y == pytest.approx(20.0)

    def test_bottom_side_places_y_at_y2(self, svc):
        _, y = svc._boundary_anchor(BOUNDS, "bottom", (0.0, 0.0))
        assert y == pytest.approx(70.0)

    def test_left_side_places_x_at_x1(self, svc):
        x, _ = svc._boundary_anchor(BOUNDS, "left", (0.0, 0.0))
        assert x == pytest.approx(10.0)

    def test_right_side_places_x_at_x2(self, svc):
        x, _ = svc._boundary_anchor(BOUNDS, "right", (0.0, 0.0))
        assert x == pytest.approx(110.0)

    def test_top_spread_shifts_x(self, svc):
        x_no_spread, _ = svc._boundary_anchor(BOUNDS, "top", (0.0, 0.0))
        x_spread, _ = svc._boundary_anchor(BOUNDS, "top", (10.0, 0.0))
        assert x_spread != x_no_spread

    def test_spread_clamped_by_margin(self, svc):
        x, _ = svc._boundary_anchor(BOUNDS, "top", (9999.0, 0.0))
        assert x <= 110.0 - svc.EDGE_CORNER_MARGIN


# ── TestPreferredBoundarySide ─────────────────────────────────────────────────

class TestPreferredBoundarySide:
    def test_point_right_exits_right(self):
        assert SVGExportService._preferred_boundary_side(BOUNDS, (500.0, 45.0)) == "right"

    def test_point_left_exits_left(self):
        assert SVGExportService._preferred_boundary_side(BOUNDS, (-100.0, 45.0)) == "left"

    def test_point_above_exits_top(self):
        assert SVGExportService._preferred_boundary_side(BOUNDS, (60.0, -200.0)) == "top"

    def test_point_below_exits_bottom(self):
        assert SVGExportService._preferred_boundary_side(BOUNDS, (60.0, 500.0)) == "bottom"

    def test_enter_from_right_gives_left(self):
        side = SVGExportService._preferred_boundary_side(BOUNDS, (500.0, 45.0), exit_from=False)
        assert side == "left"

    def test_enter_from_above_gives_bottom(self):
        side = SVGExportService._preferred_boundary_side(BOUNDS, (60.0, -200.0), exit_from=False)
        assert side == "bottom"


# ── TestInferBoundaryOrientation ──────────────────────────────────────────────

class TestInferBoundaryOrientation:
    def test_left_edge_is_horizontal(self):
        assert SVGExportService._infer_boundary_orientation(BOUNDS, (10.0, 45.0)) == "horizontal"

    def test_right_edge_is_horizontal(self):
        assert SVGExportService._infer_boundary_orientation(BOUNDS, (110.0, 45.0)) == "horizontal"

    def test_top_edge_is_vertical(self):
        assert SVGExportService._infer_boundary_orientation(BOUNDS, (60.0, 20.0)) == "vertical"

    def test_bottom_edge_is_vertical(self):
        assert SVGExportService._infer_boundary_orientation(BOUNDS, (60.0, 70.0)) == "vertical"

    def test_interior_exit_from_true_is_vertical(self):
        assert SVGExportService._infer_boundary_orientation(BOUNDS, (60.0, 45.0), exit_from=True) == "vertical"

    def test_interior_exit_from_false_is_horizontal(self):
        assert SVGExportService._infer_boundary_orientation(BOUNDS, (60.0, 45.0), exit_from=False) == "horizontal"


# ── TestCheckEdgeIntersection ─────────────────────────────────────────────────

class TestCheckEdgeIntersection:
    def test_hits_edge_returns_t_and_coords(self):
        result = SVGExportService._check_edge_intersection(0.0, 40.0, 100.0, 0.0, 50.0, 0.0, 80.0)
        assert result is not None
        t, main, cross = result
        assert t == pytest.approx(0.5)
        assert main == pytest.approx(50.0)
        assert cross == pytest.approx(40.0)

    def test_parallel_line_returns_none(self):
        assert SVGExportService._check_edge_intersection(0.0, 40.0, 0.0, 10.0, 50.0, 0.0, 80.0) is None

    def test_t_beyond_segment_returns_none(self):
        # t = 20/10 = 2.0 → outside [0, 1]
        assert SVGExportService._check_edge_intersection(0.0, 0.0, 10.0, 0.0, 20.0, 0.0, 100.0) is None

    def test_cross_outside_range_returns_none(self):
        # cross=200, range [0, 80]
        assert SVGExportService._check_edge_intersection(0.0, 200.0, 100.0, 0.0, 50.0, 0.0, 80.0) is None

    def test_at_boundary_t_zero_is_valid_closed_interval(self):
        # _check_edge_intersection uses [0, 1] (closed) so t=0 is valid
        result = SVGExportService._check_edge_intersection(50.0, 40.0, 100.0, 0.0, 50.0, 0.0, 80.0)
        assert result is not None
        assert result[0] == pytest.approx(0.0)


# ── TestClipPointToBoundaryDegenerate ────────────────────────────────────────

class TestClipPointToBoundaryDegenerate:
    def test_same_from_and_to_returns_from(self):
        bounds = (0.0, 0.0, 100.0, 80.0)
        result = SVGExportService._clip_point_to_boundary(bounds, (50.0, 40.0), (50.0, 40.0))
        assert result == pytest.approx((50.0, 40.0))


# ── TestRenderTriangleMarker ──────────────────────────────────────────────────

class TestRenderTriangleMarker:
    def test_filled_polygon_attributes(self):
        svg = ET.Element("svg")
        SVGExportService._render_triangle_marker(svg, 100.0, 50.0, 1.0, 0.0, 12, "filled", "#000000")
        p = svg.find("polygon")
        assert p is not None
        assert p.get("fill") == "#000000"
        assert p.get("stroke") == "none"
        assert p.get("stroke-width") == "1"

    def test_hollow_polygon_attributes(self):
        svg = ET.Element("svg")
        SVGExportService._render_triangle_marker(svg, 100.0, 50.0, 1.0, 0.0, 12, "hollow", "#333333")
        p = svg.find("polygon")
        assert p is not None
        assert p.get("fill") == "none"
        assert p.get("stroke") == "#333333"
        assert p.get("stroke-width") == "1.5"

    def test_polygon_has_three_points(self):
        svg = ET.Element("svg")
        SVGExportService._render_triangle_marker(svg, 50.0, 50.0, 0.0, 1.0, 12, "filled", "black")
        points_str = svg.find("polygon").get("points", "")
        assert len(points_str.split()) == 3


# ── TestRenderDiamondMarker ───────────────────────────────────────────────────

class TestRenderDiamondMarker:
    def test_renders_polygon_with_four_points(self):
        svg = ET.Element("svg")
        SVGExportService._render_diamond_marker(svg, 100.0, 50.0, 1.0, 0.0, "black")
        p = svg.find("polygon")
        assert p is not None
        assert len(p.get("points", "").split()) == 4

    def test_fill_is_the_given_color(self):
        svg = ET.Element("svg")
        SVGExportService._render_diamond_marker(svg, 100.0, 50.0, 1.0, 0.0, "#FF0000")
        assert svg.find("polygon").get("fill") == "#FF0000"


# ── TestRenderMarkerShape ─────────────────────────────────────────────────────

class TestRenderMarkerShape:
    def test_zero_distance_renders_nothing(self, svc):
        svg = ET.Element("svg")
        svc._render_marker_shape(svg, (50.0, 50.0), (50.0, 50.0), "filled", "black", "end")
        assert len(list(svg)) == 0

    def test_filled_triangle_rendered(self, svc):
        svg = ET.Element("svg")
        svc._render_marker_shape(svg, (100.0, 50.0), (50.0, 50.0), "filled", "black", "end")
        assert len(list(svg)) == 1

    def test_hollow_triangle_rendered(self, svc):
        svg = ET.Element("svg")
        svc._render_marker_shape(svg, (100.0, 50.0), (50.0, 50.0), "hollow", "black", "start")
        assert len(list(svg)) == 1

    def test_diamond_rendered(self, svc):
        svg = ET.Element("svg")
        svc._render_marker_shape(svg, (100.0, 50.0), (50.0, 50.0), "diamond", "black", "start")
        assert len(list(svg)) == 1

    def test_end_position_flips_direction(self, svc):
        # Verify it renders without error when position="end"
        svg = ET.Element("svg")
        svc._render_marker_shape(svg, (0.0, 50.0), (100.0, 50.0), "filled", "black", "end")
        assert len(list(svg)) == 1


# ── TestOffsetPointsForMarkers ────────────────────────────────────────────────

class TestOffsetPointsForMarkers:
    def test_no_markers_returns_unchanged(self, svc):
        pts = [(0.0, 0.0), (100.0, 0.0)]
        assert svc._offset_points_for_markers(pts, {}) == pts

    def test_single_point_returns_unchanged(self, svc):
        pts = [(50.0, 50.0)]
        assert svc._offset_points_for_markers(pts, {"marker-start": "url(#diamond)"}) == pts

    def test_diamond_start_advances_first_point(self, svc):
        pts = [(0.0, 0.0), (100.0, 0.0)]
        result = svc._offset_points_for_markers(pts, {"marker-start": "url(#diamond)"})
        assert result[0][0] > 0.0

    def test_end_marker_retreats_last_point(self, svc):
        pts = [(0.0, 0.0), (100.0, 0.0)]
        result = svc._offset_points_for_markers(pts, {"marker-end": "url(#arrowhead)"})
        assert result[-1][0] < 100.0

    def test_segment_shorter_than_offset_not_moved(self, svc):
        # Length 3 < marker_offset 8 → no movement
        pts = [(0.0, 0.0), (3.0, 0.0)]
        result = svc._offset_points_for_markers(pts, {"marker-start": "url(#diamond)"})
        assert result[0] == pytest.approx((0.0, 0.0))


# ── TestResolveConnectionNodes ────────────────────────────────────────────────

class TestResolveConnectionNodes:
    def test_missing_source_uuid_returns_none(self, svc):
        conn = SimpleNamespace(_source=None, _target="t")
        assert svc._resolve_connection_nodes(conn, {}) is None

    def test_missing_target_uuid_returns_none(self, svc):
        conn = SimpleNamespace(_source="s", _target=None)
        assert svc._resolve_connection_nodes(conn, {}) is None

    def test_source_not_in_dict_returns_none(self, svc):
        conn = SimpleNamespace(_source="s", _target="t")
        assert svc._resolve_connection_nodes(conn, {"t": make_node("t")}) is None

    def test_target_not_in_dict_returns_none(self, svc):
        conn = SimpleNamespace(_source="s", _target="t")
        assert svc._resolve_connection_nodes(conn, {"s": make_node("s")}) is None

    def test_both_found_returns_pair(self, svc):
        s, t = make_node("s"), make_node("t")
        result = svc._resolve_connection_nodes(
            SimpleNamespace(_source="s", _target="t"), {"s": s, "t": t}
        )
        assert result == (s, t)


# ── TestBuildRelationshipLabel ────────────────────────────────────────────────

class TestBuildRelationshipLabel:
    def test_regular_type_stripped(self, svc):
        conn = SimpleNamespace()
        assert svc._build_relationship_label("FlowRelationship", conn) == "Flow"

    def test_influence_without_strength(self, svc):
        conn = SimpleNamespace(influence_strength=None, _influence_strength=None)
        assert svc._build_relationship_label("InfluenceRelationship", conn) == "Influence"

    def test_influence_with_strength(self, svc):
        conn = SimpleNamespace(influence_strength="+", _influence_strength=None)
        assert svc._build_relationship_label("InfluenceRelationship", conn) == "Influence (+)"

    def test_influence_short_form_with_private_strength(self, svc):
        conn = SimpleNamespace(influence_strength=None, _influence_strength="++")
        assert svc._build_relationship_label("Influence", conn) == "Influence (++)"


# ── TestDistributedSpread ─────────────────────────────────────────────────────

class TestDistributedSpread:
    def test_single_connection_returns_zero(self, svc):
        assert svc._distributed_spread(0, 1, 100.0) == pytest.approx(0.0)

    def test_zero_edge_span_returns_zero(self, svc):
        assert svc._distributed_spread(0, 2, 0.0) == pytest.approx(0.0)

    def test_two_connections_symmetric(self, svc):
        s0 = svc._distributed_spread(0, 2, 100.0)
        s1 = svc._distributed_spread(1, 2, 100.0)
        assert s0 == pytest.approx(-s1)

    def test_three_connections_center_is_zero(self, svc):
        assert svc._distributed_spread(1, 3, 100.0) == pytest.approx(0.0)

    def test_span_smaller_than_two_margins_returns_zero(self, svc):
        # 2 * EDGE_CORNER_MARGIN = 24; edge_span=20 → usable_span ≤ 0
        assert svc._distributed_spread(0, 2, 20.0) == pytest.approx(0.0)


# ── TestOrthogonalizePolylinePoints ──────────────────────────────────────────

class TestOrthogonalizePolylinePoints:
    def test_single_point_returned_as_is(self, svc):
        pts = [(0.0, 0.0)]
        assert svc._orthogonalize_polyline_points(pts) == pts

    def test_horizontal_segment_unchanged(self, svc):
        pts = [(0.0, 0.0), (100.0, 0.0)]
        assert svc._orthogonalize_polyline_points(pts) == pts

    def test_vertical_segment_unchanged(self, svc):
        pts = [(50.0, 0.0), (50.0, 80.0)]
        assert svc._orthogonalize_polyline_points(pts) == pts

    def test_diagonal_gets_corner_inserted(self, svc):
        pts = [(0.0, 0.0), (100.0, 80.0)]
        result = svc._orthogonalize_polyline_points(pts)
        assert len(result) == 3
        for p1, p2 in zip(result, result[1:], strict=False):
            assert p1[0] == pytest.approx(p2[0]) or p1[1] == pytest.approx(p2[1])

    def test_multi_diagonal_all_axis_aligned(self, svc):
        pts = [(0.0, 0.0), (50.0, 40.0), (100.0, 80.0)]
        result = svc._orthogonalize_polyline_points(pts)
        for p1, p2 in zip(result, result[1:], strict=False):
            assert p1[0] == pytest.approx(p2[0]) or p1[1] == pytest.approx(p2[1])


# ── TestChooseCorner ──────────────────────────────────────────────────────────

class TestChooseCorner:
    def test_last_segment_horizontal_target(self):
        result = SVGExportService._choose_corner((0.0, 0.0), (50.0, 40.0), 1, 1, "horizontal", "vertical")
        assert result == (0.0, 40.0)

    def test_last_segment_vertical_target(self):
        result = SVGExportService._choose_corner((0.0, 0.0), (50.0, 40.0), 1, 1, "vertical", "vertical")
        assert result == (50.0, 0.0)

    def test_first_segment_horizontal_source(self):
        result = SVGExportService._choose_corner((0.0, 0.0), (50.0, 40.0), 0, 3, "vertical", "horizontal")
        assert result == (0.0, 40.0)

    def test_first_segment_vertical_source(self):
        result = SVGExportService._choose_corner((0.0, 0.0), (50.0, 40.0), 0, 3, "vertical", "vertical")
        assert result == (50.0, 0.0)

    def test_middle_segment_dx_dominant(self):
        # abs(dx)=50 >= abs(dy)=10 → (cur[0], prev[1])
        result = SVGExportService._choose_corner((0.0, 0.0), (50.0, 10.0), 1, 3, "vertical", "vertical")
        assert result == (50.0, 0.0)

    def test_middle_segment_dy_dominant(self):
        # abs(dx)=10 < abs(dy)=50 → (prev[0], cur[1])
        result = SVGExportService._choose_corner((0.0, 0.0), (10.0, 50.0), 1, 3, "vertical", "vertical")
        assert result == (0.0, 50.0)


# ── TestLookupRelStyle ────────────────────────────────────────────────────────

class TestLookupRelStyle:
    def test_known_short_type_returns_style(self, svc):
        rs = RelationshipStyleService()
        assert SVGExportService._lookup_rel_style("Flow", rs) is not None

    def test_unknown_type_without_suffix_returns_none(self, svc):
        rs = RelationshipStyleService()
        assert SVGExportService._lookup_rel_style("GarbageType", rs) is None

    def test_long_form_falls_back_to_short_via_strip(self, svc):
        rs = RelationshipStyleService()
        # "FlowRelationship" not in registry, falls back to "Flow"
        assert SVGExportService._lookup_rel_style("FlowRelationship", rs) is not None

    def test_unknown_long_form_returns_none(self, svc):
        rs = RelationshipStyleService()
        assert SVGExportService._lookup_rel_style("GarbageRelationship", rs) is None


# ── TestApplyAccessMarkersWithValueAttr ───────────────────────────────────────

class TestApplyAccessMarkersWithValueAttr:
    def test_access_type_with_value_attr_read(self, svc):
        conn = SimpleNamespace(access_type=SimpleNamespace(value="Read"), _access_type=None)
        attrs: dict[str, str] = {}
        svc._apply_access_markers(conn, attrs)
        assert "marker-start" in attrs

    def test_access_type_with_value_attr_write(self, svc):
        conn = SimpleNamespace(access_type=SimpleNamespace(value="Write"), _access_type=None)
        attrs: dict[str, str] = {}
        svc._apply_access_markers(conn, attrs)
        assert "marker-end" in attrs

    def test_access_type_none_no_markers(self, svc):
        conn = SimpleNamespace(access_type=None, _access_type=None)
        attrs: dict[str, str] = {}
        svc._apply_access_markers(conn, attrs)
        assert attrs == {}


# ── TestApplyMarkerAttrsElseBranch ────────────────────────────────────────────

class TestApplyMarkerAttrsElseBranch:
    def test_else_branch_with_marker_start_and_end(self, svc):
        # rel_type not in Access/Association/Composition/Aggregation → else branch
        style = SimpleNamespace(marker_start="url(#test-start)", marker_end="url(#test-end)")
        attrs: dict[str, str] = {}
        svc._apply_marker_attrs("Realization", SimpleNamespace(), style, attrs)
        assert attrs.get("marker-start") == "url(#test-start)"
        assert attrs.get("marker-end") == "url(#test-end)"

    def test_else_branch_no_markers_when_none(self, svc):
        style = SimpleNamespace(marker_start=None, marker_end=None)
        attrs: dict[str, str] = {}
        svc._apply_marker_attrs("Realization", SimpleNamespace(), style, attrs)
        assert attrs == {}


# ── TestRenderConnectionLabel ─────────────────────────────────────────────────

class TestRenderConnectionLabel:
    def test_no_points_returns_early_no_svg_children(self, svc):
        svg = ET.Element("svg")
        svc._render_connection_label(svg, [], "Flow")
        assert len(list(svg)) == 0

    def test_single_point_returns_early(self, svc):
        svg = ET.Element("svg")
        svc._render_connection_label(svg, [(0.0, 0.0)], "Flow")
        assert len(list(svg)) == 0

    def test_two_points_renders_label_group(self, svc):
        svg = ET.Element("svg")
        svc._render_connection_label(svg, [(0.0, 0.0), (100.0, 0.0)], "Flow")
        g = svg.find("g")
        assert g is not None
        assert g.get("class") == "connection-label"


# ── TestRenderWrappedText ─────────────────────────────────────────────────────

class TestRenderWrappedText:
    def test_single_line_no_tspan(self, svc):
        parent = ET.Element("g")
        svc._render_wrapped_text(parent, "Short", 50.0, 50.0, 200.0)
        text = parent.find("text")
        assert text is not None
        assert text.text == "Short"
        assert len(text.findall("tspan")) == 0

    def test_multi_line_creates_tspan_elements(self, svc):
        parent = ET.Element("g")
        # max_width=60 → chars_per_line=10; "Hello World Again" → 3 lines
        svc._render_wrapped_text(parent, "Hello World Again", 50.0, 50.0, 60.0)
        text = parent.find("text")
        assert text is not None
        tspans = text.findall("tspan")
        assert len(tspans) >= 1  # at least one continuation tspan

    def test_centered_text_uses_middle_anchor(self, svc):
        parent = ET.Element("g")
        svc._render_wrapped_text(parent, "Test", 50.0, 50.0, 200.0, is_centered=True)
        assert parent.find("text").get("text-anchor") == "middle"

    def test_left_aligned_text_uses_start_anchor(self, svc):
        parent = ET.Element("g")
        svc._render_wrapped_text(parent, "Test", 10.0, 10.0, 200.0, is_centered=False)
        assert parent.find("text").get("text-anchor") == "start"


# ── TestRenderConnection ──────────────────────────────────────────────────────

class TestRenderConnection:
    def test_missing_source_uuid_renders_nothing(self, svc):
        svg = ET.Element("svg")
        conn = SimpleNamespace(_source=None, _target="t", bendpoints=[])
        svc._render_connection(svg, conn, {})
        assert svg.find("polyline") is None

    def test_missing_target_uuid_renders_nothing(self, svc):
        svg = ET.Element("svg")
        conn = SimpleNamespace(_source="s", _target=None, bendpoints=[])
        svc._render_connection(svg, conn, {})
        assert svg.find("polyline") is None

    def test_source_not_in_dict_renders_nothing(self, svc):
        svg = ET.Element("svg")
        conn = SimpleNamespace(_source="s", _target="t", bendpoints=[])
        t = make_node("t", x=200.0)
        svc._render_connection(svg, conn, {"t": t})
        assert svg.find("polyline") is None

    def test_valid_nodes_renders_polyline(self, svc):
        svg = ET.Element("svg")
        source = make_node("s", x=0.0, y=0.0, w=120.0, h=55.0, element_type="BusinessActor")
        target = make_node("t", x=200.0, y=0.0, w=120.0, h=55.0, element_type="BusinessActor")
        conn = SimpleNamespace(_source="s", _target="t", type="UnknownFutureRel", bendpoints=[])
        svc._render_connection(svg, conn, {"s": source, "t": target})
        assert svg.find("polyline") is not None

    def test_valid_nodes_renders_connection_label(self, svc):
        svg = ET.Element("svg")
        source = make_node("s", x=0.0, y=0.0, w=120.0, h=55.0, element_type="BusinessActor")
        target = make_node("t", x=200.0, y=0.0, w=120.0, h=55.0, element_type="BusinessActor")
        conn = SimpleNamespace(_source="s", _target="t", type="FlowRelationship", bendpoints=[])
        svc._render_connection(svg, conn, {"s": source, "t": target})
        assert svg.find("g[@class='connection-label']") is not None


# ── TestRenderNodeGroup ───────────────────────────────────────────────────────

class TestRenderNodeGroup:
    def test_group_element_renders_rect(self, svc):
        svg = ET.Element("svg")
        node = make_node(element_type="Group", x=10.0, y=20.0, w=200.0, h=100.0, name="My Group")
        svc._render_node_into(svg, node)
        # Group renders as a rect
        g = svg.find("g")
        assert g is not None
        assert g.find("rect") is not None

    def test_group_uses_custom_fill_color(self, svc):
        svg = ET.Element("svg")
        node = make_node(element_type="Group", x=0.0, y=0.0, w=100.0, h=50.0,
                         name="G", fill_color="#AABBCC")
        svc._render_node_into(svg, node)
        rect = svg.find("g/rect")
        assert rect is not None
        assert rect.get("fill") == "#AABBCC"

    def test_group_default_fill_color(self, svc):
        svg = ET.Element("svg")
        node = make_node(element_type="Group", x=0.0, y=0.0, w=100.0, h=50.0, name="G")
        svc._render_node_into(svg, node)
        rect = svg.find("g/rect")
        assert rect.get("fill") == "#d9d9d9"


# ── TestRenderNodeJunctionFromModel ──────────────────────────────────────────

class TestRenderNodeJunctionFromModel:
    def test_junction_with_model_or_type(self, svc):
        svg = ET.Element("svg")
        elem = SimpleNamespace(uuid="elem1", junction_type="or")
        model = SimpleNamespace(elements=[elem])
        node = SimpleNamespace(
            uuid="j1", x=0.0, y=0.0, w=20.0, h=20.0,
            type="Junction", name="", label="",
            nodes=[], fill_color=None,
            _ref="elem1", _model=model,
        )
        svc._render_node_into(svg, node)
        circle = svg.find("g/circle")
        assert circle is not None
        assert circle.get("fill") == "white"  # OrJunction → white

    def test_junction_with_model_and_type(self, svc):
        svg = ET.Element("svg")
        elem = SimpleNamespace(uuid="elem2", junction_type="and")
        model = SimpleNamespace(elements=[elem])
        node = SimpleNamespace(
            uuid="j2", x=0.0, y=0.0, w=20.0, h=20.0,
            type="Junction", name="", label="",
            nodes=[], fill_color=None,
            _ref="elem2", _model=model,
        )
        svc._render_node_into(svg, node)
        circle = svg.find("g/circle")
        assert circle is not None
        assert circle.get("fill") == "black"  # AndJunction → black

    def test_junction_with_missing_ref_defaults_to_and(self, svc):
        svg = ET.Element("svg")
        node = SimpleNamespace(
            uuid="j3", x=0.0, y=0.0, w=20.0, h=20.0,
            type="Junction", name="", label="",
            nodes=[], fill_color=None,
            _ref=None, _model=None,
        )
        svc._render_node_into(svg, node)
        circle = svg.find("g/circle")
        assert circle is not None
        assert circle.get("fill") == "black"  # no ref → defaults to And


# ── TestRenderNodeWithChildren ────────────────────────────────────────────────

class TestRenderNodeWithChildren:
    def test_container_with_name_renders_topleft_text(self, svc):
        svg = ET.Element("svg")
        child = make_node("c", x=10.0, y=10.0, w=80.0, h=40.0)
        parent = make_node("p", x=0.0, y=0.0, w=200.0, h=150.0,
                           element_type="BusinessFunction",
                           name="Container Label", nodes=[child])
        svc._render_node_into(svg, parent)
        g = svg.find("g")
        assert g is not None
        # Text should be present for the container's label
        assert g.find("text") is not None


# ── TestModuleFunctions ───────────────────────────────────────────────────────

class TestArchimateSymbolModuleFunctions:
    def test_get_symbol_known_type(self):
        sym = get_symbol("BusinessActor")
        assert sym is not None
        assert sym.svg_path

    def test_get_symbol_unknown_type_returns_none(self):
        assert get_symbol("DoesNotExist") is None

    def test_get_all_symbols_returns_dict(self):
        result = get_all_symbols()
        assert isinstance(result, dict)
        assert "BusinessActor" in result
        assert result is not ARCHIMATE_SYMBOLS  # copy

    def test_validate_symbols_returns_counts(self):
        valid, invalid = validate_symbols()
        assert valid > 0
        assert isinstance(valid, int)
        assert isinstance(invalid, int)


class TestColorPaletteHelpers:
    def test_get_all_colors_returns_copy(self):
        palette = ColorPalette()
        colors = palette.get_all_colors()
        assert isinstance(colors, dict)
        assert colors is not palette.colors

    def test_invalid_hex_char_returns_false(self):
        palette = ColorPalette()
        assert palette._is_valid_hex("ZZZZZZ") is False

    def test_valid_hex_returns_true(self):
        palette = ColorPalette()
        assert palette._is_valid_hex("FF0080") is True


class TestRelationshipStyleServiceValidate:
    def test_validate_styles_returns_valid_count(self):
        rs = RelationshipStyleService()
        valid, invalid = rs.validate_styles()
        assert valid > 0
        assert invalid == 0
