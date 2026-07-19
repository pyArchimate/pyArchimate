"""Unit tests targeting previously uncovered paths in svg_export.py."""

from __future__ import annotations

import os
import tempfile
from types import SimpleNamespace
from typing import cast

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import View
from src.pyArchimate.view.layout.export.svg_export import SVGExportService
from src.pyArchimate.view.layout.export.symbols.archimate_relationships import RelationshipStyleService

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def make_node(
    uuid="n1",
    x=0.0,
    y=0.0,
    w=120.0,
    h=55.0,
    element_type="BusinessActor",
    name="Test",
    nodes=None,
    fill_color=None,
    **kwargs,
):
    return SimpleNamespace(
        uuid=uuid,
        x=x,
        y=y,
        w=w,
        h=h,
        type=element_type,
        name=name,
        label=name,
        nodes=nodes or [],
        nodes_dict={},
        fill_color=fill_color,
        concept=None,
        _ref=None,
        **kwargs,
    )


def make_conn(uuid="c1", src="n1", tgt="n2", rel_type="ServingRelationship", bendpoints=None, **kwargs):
    return SimpleNamespace(
        uuid=uuid,
        _source=src,
        _target=tgt,
        type=rel_type,
        bendpoints=bendpoints or [],
        stroke_color=None,
        line_color=None,
        stroke_width=None,
        stroke_style=None,
        **kwargs,
    )


def make_view(nodes=None, conns=None):
    ns = nodes or []
    return SimpleNamespace(
        nodes=ns,
        conns=conns or [],
        nodes_dict={n.uuid: n for n in ns},
    )


@pytest.fixture
def svc():
    return SVGExportService()


# ---------------------------------------------------------------------------
# Lines 140-143: nested node parent assignment in _render_nodes
# ---------------------------------------------------------------------------


class TestNestedNodeRendering:
    def test_nested_node_rendered_into_parent_group(self, svc):
        child = make_node("child", x=10, y=10, w=60, h=30, element_type="BusinessActor", name="Child")
        parent = make_node("parent", x=0, y=0, w=200, h=100, element_type="BusinessActor", name="Parent",
                           nodes=[child])
        parent.nodes_dict = {"child": child}
        view = make_view(nodes=[parent, child])
        svg_str = svc.to_svg(view)
        # Both nodes must appear in the SVG output
        assert svg_str.count('class="node"') == 2


# ---------------------------------------------------------------------------
# Lines 207-209: to_svg() with filepath writes <?xml declaration
# ---------------------------------------------------------------------------


class TestToSvgFileWrite:
    def test_file_write_creates_file_with_xml_declaration(self, svc):
        m = Model("T")
        v = cast(View, m.add(ArchiType.View, "V"))
        elem = m.add(ArchiType.BusinessActor, "A")
        v.add(elem, x=10, y=10, w=120, h=55)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            svc.to_svg(v, filepath=path)
            content = open(path).read()
            assert content.startswith('<?xml version="1.0"')
            assert "<svg" in content
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Lines 247-254: _calculate_bounds includes connection bendpoints
# ---------------------------------------------------------------------------


class TestCalculateBoundsWithBendpoints:
    def test_bendpoints_extend_bounds(self, svc):
        node = make_node("n1", x=50, y=50, w=120, h=55)
        bp = SimpleNamespace(x=500.0, y=400.0)
        conn = make_conn(bendpoints=[bp])
        view = make_view(nodes=[node], conns=[conn])
        bounds = svc._calculate_bounds(view)
        assert bounds["max_x"] >= 500.0
        assert bounds["max_y"] >= 400.0


# ---------------------------------------------------------------------------
# Lines 559-574 + 692-693: Grouping element dispatches to _render_grouping
# ---------------------------------------------------------------------------


class TestGroupingElement:
    def test_grouping_renders_dashed_path(self, svc):
        m = Model("T")
        v = cast(View, m.add(ArchiType.View, "V"))
        elem = m.add(ArchiType.Grouping, "MyGroup")
        v.add(elem, x=0, y=0, w=200, h=100)
        svg_str = svc.to_svg(v)
        assert "stroke-dasharray" in svg_str

    def test_grouping_with_name_renders_text(self, svc):
        m = Model("T")
        v = cast(View, m.add(ArchiType.View, "V"))
        elem = m.add(ArchiType.Grouping, "MyGroupLabel")
        v.add(elem, x=0, y=0, w=200, h=100)
        svg_str = svc.to_svg(v)
        assert "MyGroupLabel" in svg_str


# ---------------------------------------------------------------------------
# Lines 607-649: rect_header body type (BusinessObject) and path body type
# ---------------------------------------------------------------------------


class TestBodyTypes:
    def test_rect_header_renders_header_line(self, svc):
        m = Model("T")
        v = cast(View, m.add(ArchiType.View, "V"))
        elem = m.add(ArchiType.BusinessObject, "BizObj")
        v.add(elem, x=10, y=10, w=120, h=55)
        svg_str = svc.to_svg(v)
        # rect_header renders a <line> separator
        assert "<line" in svg_str

    def test_path_body_type_renders_path_element(self, svc):
        m = Model("T")
        v = cast(View, m.add(ArchiType.View, "V"))
        elem = m.add(ArchiType.Constraint, "C")
        v.add(elem, x=10, y=10, w=120, h=55)
        svg_str = svc.to_svg(v)
        assert "<path" in svg_str

    def test_scale_path_called_for_path_body(self, svc):
        from src.pyArchimate.view.layout.export.symbols.archimate_symbols import ARCHIMATE_SYMBOLS
        sym = ARCHIMATE_SYMBOLS.get("Constraint")
        assert sym is not None and sym.body_type == "path"
        result = svc._scale_path(sym.svg_path, 10, 10, 120, 55)
        assert isinstance(result, str) and len(result) > 0


# ---------------------------------------------------------------------------
# Lines 942-943: ReadWrite access marker (both start and end)
# ---------------------------------------------------------------------------


class TestAccessMarkers:
    def test_readwrite_sets_both_markers(self, svc):
        attrs: dict[str, str] = {}
        conn = SimpleNamespace(access_type="ReadWrite", _access_type="ReadWrite")
        svc._apply_access_markers(conn, attrs)
        assert "marker-start" in attrs
        assert "marker-end" in attrs

    def test_read_sets_only_start_marker(self, svc):
        attrs: dict[str, str] = {}
        conn = SimpleNamespace(access_type="Read", _access_type="Read")
        svc._apply_access_markers(conn, attrs)
        assert "marker-start" in attrs
        assert "marker-end" not in attrs

    def test_write_sets_only_end_marker(self, svc):
        attrs: dict[str, str] = {}
        conn = SimpleNamespace(access_type="Write", _access_type="Write")
        svc._apply_access_markers(conn, attrs)
        assert "marker-end" in attrs
        assert "marker-start" not in attrs


# ---------------------------------------------------------------------------
# Lines 949, 951-953: Association directed marker
# ---------------------------------------------------------------------------


class TestAssociationDirectedMarker:
    def test_directed_association_adds_end_marker(self, svc):
        attrs: dict[str, str] = {}
        rel_service = RelationshipStyleService()
        style = rel_service.get_style("Association")
        conn = SimpleNamespace(is_directed=True, _is_directed=True)
        svc._apply_marker_attrs("Association", conn, style, attrs)
        assert "marker-end" in attrs

    def test_undirected_association_no_markers(self, svc):
        attrs: dict[str, str] = {}
        rel_service = RelationshipStyleService()
        style = rel_service.get_style("Association")
        conn = SimpleNamespace(is_directed=False, _is_directed=False)
        svc._apply_marker_attrs("Association", conn, style, attrs)
        assert "marker-end" not in attrs


# ---------------------------------------------------------------------------
# Lines 955-956: CompositionRelationship marker_start applied
# ---------------------------------------------------------------------------


class TestCompositionMarker:
    def test_composition_applies_marker_start(self, svc):
        attrs: dict[str, str] = {}
        rel_service = RelationshipStyleService()
        style = rel_service.get_style("CompositionRelationship")
        if style and style.marker_start:
            conn = SimpleNamespace()
            svc._apply_marker_attrs("CompositionRelationship", conn, style, attrs)
            assert "marker-start" in attrs


# ---------------------------------------------------------------------------
# Lines 1208-1219: _get_clipped_polyline_points with bendpoints
# ---------------------------------------------------------------------------


class TestClippedPolylineWithBendpoints:
    def test_bendpoints_included_in_polyline(self, svc):
        src = make_node("s", x=0, y=0, w=100, h=50)
        tgt = make_node("t", x=300, y=200, w=100, h=50)
        bp = SimpleNamespace(x=200.0, y=100.0)
        pts = svc._get_clipped_polyline_points(src, tgt, [bp])
        # start + bendpoint + end = 3 points
        assert len(pts) == 3
        assert pts[1] == (200.0, 100.0)


# ---------------------------------------------------------------------------
# Lines 1435: _edge_t returns None when cross is outside bounds
# ---------------------------------------------------------------------------


class TestEdgeT:
    def test_returns_none_when_cross_outside_lo(self, svc):
        result = SVGExportService._edge_t(0.0, 0.0, 100.0, 0.0, 100.0, 50.0, 200.0)
        # dy=0, cross=0 which is < cross_lo=50 → None
        assert result is None

    def test_returns_none_when_t_out_of_range(self, svc):
        # edge is behind the from_point → t < 0
        result = SVGExportService._edge_t(100.0, 0.0, -50.0, 0.0, 200.0, 0.0, 100.0)
        assert result is None

    def test_returns_hit_when_valid(self, svc):
        # from (0,50) moving right (+200, 0), edge at x=100 → t=0.5 (strictly inside [0,1))
        result = SVGExportService._edge_t(0.0, 50.0, 200.0, 0.0, 100.0, 0.0, 100.0)
        assert result is not None
        t, _cross = result
        assert abs(t - 0.5) < 0.01


# ---------------------------------------------------------------------------
# Lines 1440, 1445: _exit_x_edge and _exit_y_edge
# ---------------------------------------------------------------------------


class TestExitEdge:
    def test_exit_x_edge_left(self):
        # wx < x1 → returns (x1, clamped_y)
        result = SVGExportService._exit_x_edge(wx=10.0, wy=50.0, x1=20.0, y1=0.0, x2=120.0, y2=55.0)
        assert result == (20.0, 50.0)

    def test_exit_x_edge_right(self):
        # wx > x1 → returns (x2, clamped_y)
        result = SVGExportService._exit_x_edge(wx=200.0, wy=30.0, x1=20.0, y1=0.0, x2=120.0, y2=55.0)
        assert result == (120.0, 30.0)

    def test_exit_y_edge_top(self):
        result = SVGExportService._exit_y_edge(wx=60.0, wy=5.0, x1=20.0, y1=10.0, x2=120.0, y2=65.0)
        assert result == (60.0, 10.0)

    def test_exit_y_edge_bottom(self):
        result = SVGExportService._exit_y_edge(wx=60.0, wy=100.0, x1=20.0, y1=10.0, x2=120.0, y2=65.0)
        assert result == (60.0, 65.0)


# ---------------------------------------------------------------------------
# Lines 1462-1480: _orthogonal_clip branches
# ---------------------------------------------------------------------------


class TestOrthogonalClip:
    def test_outside_x_only(self):
        bounds = (10.0, 10.0, 110.0, 65.0)
        # waypoint left of element, within y range
        pt = SVGExportService._orthogonal_clip(bounds, (0.0, 40.0))
        assert pt[0] == 10.0  # exits left edge

    def test_outside_y_only(self):
        bounds = (10.0, 10.0, 110.0, 65.0)
        # waypoint above element, within x range
        pt = SVGExportService._orthogonal_clip(bounds, (60.0, 0.0))
        assert pt[1] == 10.0  # exits top edge

    def test_corner_outside_both_axes_x_dominates(self):
        bounds = (10.0, 10.0, 110.0, 65.0)
        # x overshoot much larger than y overshoot → exits x edge
        pt = SVGExportService._orthogonal_clip(bounds, (-200.0, 8.0))
        assert pt[0] == 10.0

    def test_corner_outside_both_axes_y_dominates(self):
        bounds = (10.0, 10.0, 110.0, 65.0)
        # y overshoot larger → exits y edge
        pt = SVGExportService._orthogonal_clip(bounds, (8.0, -200.0))
        assert pt[1] == 10.0

    def test_inside_falls_back_to_centre_clip(self):
        bounds = (10.0, 10.0, 110.0, 65.0)
        # Waypoint inside element → falls back to clip from centre toward waypoint.
        # The segment centre→waypoint is entirely inside the rectangle, so the
        # fallback returns the waypoint itself (no edge hit within t∈(0,1)).
        pt = SVGExportService._orthogonal_clip(bounds, (60.0, 40.0))
        assert isinstance(pt, tuple) and len(pt) == 2


# ---------------------------------------------------------------------------
# Lines 1515, 1519: additional _clip_point_to_boundary edge hits
# ---------------------------------------------------------------------------


class TestClipPointToBoundaryEdges:
    def test_clips_going_downward(self, svc):
        bounds = (0.0, 0.0, 100.0, 50.0)
        # from centre going down → should exit bottom
        pt = SVGExportService._clip_point_to_boundary(bounds, (50.0, 25.0), (50.0, 200.0))
        assert abs(pt[1] - 50.0) < 1.0

    def test_clips_going_upward(self, svc):
        bounds = (0.0, 0.0, 100.0, 50.0)
        pt = SVGExportService._clip_point_to_boundary(bounds, (50.0, 25.0), (50.0, -100.0))
        assert abs(pt[1] - 0.0) < 1.0


# ---------------------------------------------------------------------------
# Lines 1531-1589: _spread_source/target_connections with multiple connections
# ---------------------------------------------------------------------------


class TestSpreadConnections:
    def _make_spread_node(self, uuid, x, y, w=120, h=55):
        n = SimpleNamespace(uuid=uuid, x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2)
        return n

    def test_spread_source_multiple_connections(self, svc):
        src = self._make_spread_node("s", 0, 0)
        t1 = self._make_spread_node("t1", 300, 0)
        t2 = self._make_spread_node("t2", 300, 200)
        c1 = make_conn("c1", src="s", tgt="t1")
        c2 = make_conn("c2", src="s", tgt="t2")
        nodes_dict = {"s": src, "t1": t1, "t2": t2}
        spreads: dict = {}
        svc._spread_source_connections("s", src, [c1, c2], nodes_dict, spreads)
        assert len(spreads) == 2

    def test_spread_target_multiple_connections(self, svc):
        tgt = self._make_spread_node("t", 300, 0)
        s1 = self._make_spread_node("s1", 0, 0)
        s2 = self._make_spread_node("s2", 0, 200)
        c1 = make_conn("c1", src="s1", tgt="t")
        c2 = make_conn("c2", src="s2", tgt="t")
        nodes_dict = {"t": tgt, "s1": s1, "s2": s2}
        spreads: dict = {}
        svc._spread_target_connections("t", tgt, [c1, c2], nodes_dict, spreads)
        assert len(spreads) == 2

    def test_spread_source_single_connection_no_spread(self, svc):
        src = self._make_spread_node("s", 0, 0)
        t1 = self._make_spread_node("t1", 300, 0)
        c1 = make_conn("c1", src="s", tgt="t1")
        nodes_dict = {"s": src, "t1": t1}
        spreads: dict = {}
        svc._spread_source_connections("s", src, [c1], nodes_dict, spreads)
        assert len(spreads) == 0  # single connection: no spread needed


# ---------------------------------------------------------------------------
# Lines 1600-1606: _compute_endpoint_spreads via to_svg with multi-connections
# ---------------------------------------------------------------------------


class TestComputeEndpointSpreads:
    def test_spreads_computed_for_multiple_connections_from_same_source(self, svc):
        m = Model("T")
        v = cast(View, m.add(ArchiType.View, "V"))
        src_elem = m.add(ArchiType.ApplicationComponent, "Src")
        t1_elem = m.add(ArchiType.ApplicationComponent, "T1")
        t2_elem = m.add(ArchiType.ApplicationComponent, "T2")
        src_node = v.add(src_elem, x=0, y=0, w=120, h=55)
        t1_node = v.add(t1_elem, x=300, y=0, w=120, h=55)
        t2_node = v.add(t2_elem, x=300, y=200, w=120, h=55)
        r1 = m.add_relationship(ArchiType.Serving, source=src_elem, target=t1_elem)
        r2 = m.add_relationship(ArchiType.Serving, source=src_elem, target=t2_elem)
        v.add_connection(r1, source=src_node, target=t1_node)
        v.add_connection(r2, source=src_node, target=t2_node)
        # to_svg must complete without error and produce SVG
        svg_str = svc.to_svg(v)
        assert "<svg" in svg_str


# ---------------------------------------------------------------------------
# Lines 1837, 1841: _get_short_type_name with ArchiType enum value
# ---------------------------------------------------------------------------


class TestGetShortTypeName:
    def test_archityp_enum_value_attribute(self, svc):
        # Simulate conn.type returning an object with .value
        class FakeEnum:
            value = "ServingRelationship"
        result = svc._get_short_type_name(FakeEnum())
        assert result == "Serving"

    def test_archityp_prefix_stripped(self, svc):
        result = svc._get_short_type_name("ArchiType.FlowRelationship")
        assert result == "Flow"

    def test_plain_string_no_prefix(self, svc):
        result = svc._get_short_type_name("RealizationRelationship")
        assert result == "Realization"

    def test_no_relationship_suffix(self, svc):
        result = svc._get_short_type_name("Serving")
        assert result == "Serving"
