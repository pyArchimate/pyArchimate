"""Integration tests for SVG export functionality."""

import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import View
from tests._helpers import model_with_views


def test_svg_export_with_demo_view():
    """Test SVG export with actual demo archimate file."""

    # Load demo model
    model = Model()
    demo_path = Path(__file__).parent.parent.parent / 'temp' / 'auto-layout-demo-formatted.archimate'

    if demo_path.exists():
        model.read(str(demo_path))

        if model.views:
            view = model.views[0]

            # Export to SVG
            svg_string = view.to_svg()

            # Verify SVG structure
            assert '<svg' in svg_string or '<?xml' in svg_string
            assert '</svg>' in svg_string

            # Parse and verify
            if '<?xml' in svg_string:
                # Extract just the SVG part
                start = svg_string.find('<svg')
                end = svg_string.rfind('</svg>') + 6
                svg_part = svg_string[start:end]
            else:
                svg_part = svg_string

            root = ET.fromstring(svg_part)
            assert root.tag == '{http://www.w3.org/2000/svg}svg'

            # Check that we have rectangles for nodes
            rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
            assert len(rects) > 0

            # Check that we have polylines for connections
            polylines = root.findall('.//{http://www.w3.org/2000/svg}polyline')
            # May have 0 if view has no connections

            print(f"✓ SVG export test passed: {len(rects)} nodes, {len(polylines)} connections")
    else:
        print("⊘ Demo file not found, skipping SVG export integration test")


def test_svg_export_to_file():
    """Test SVG export to file."""

    model = Model()
    demo_path = Path(__file__).parent.parent.parent / 'temp' / 'auto-layout-demo-formatted.archimate'

    if demo_path.exists():
        model.read(str(demo_path))

        if model.views:
            view = model.views[0]

            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
                temp_path = f.name

            try:
                # Export to SVG file
                view.to_svg(filepath=temp_path)

                # Verify file exists
                assert Path(temp_path).exists()

                # Verify file contents
                with open(temp_path, 'r') as f:
                    content = f.read()
                    assert '<svg' in content
                    assert '</svg>' in content
                    assert '<?xml' in content

                print(f"✓ SVG file export test passed: {Path(temp_path).stat().st_size} bytes written")

            finally:
                Path(temp_path).unlink(missing_ok=True)
    else:
        print("⊘ Demo file not found, skipping SVG file export test")


def test_svg_export_empty_view():
    """Test SVG export with minimal view."""
    # Create a minimal model and view
    model = Model()
    view = View(name="Empty View", uuid="test-view-1", parent=model)
    model.views_dict[view.uuid] = view

    # Export to SVG
    svg_string = view.to_svg()

    # Verify it's valid SVG
    assert '<svg' in svg_string

    # Parse and verify structure
    root = ET.fromstring(svg_string)
    assert root.tag == '{http://www.w3.org/2000/svg}svg'

    print("✓ Empty view SVG export test passed")


def test_svg_export_does_not_duplicate_relationship_markers():
    """Relationship markers should be rendered via marker defs only, not as standalone polygons."""
    model = model_with_views()
    view = model.views[0]

    svg_string = view.to_svg()
    root = ET.fromstring(svg_string)
    ns = '{http://www.w3.org/2000/svg}'

    # Marker geometry should stay inside <defs>; the root should not contain extra endpoint polygons.
    assert len(root.findall(f'./{ns}polygon')) == 0
    assert len(root.findall(f'.//{ns}polyline')) > 0


def test_svg_export_spreads_connection_endpoints_on_shared_nodes():
    """Repeated connections should not collapse to the same boundary point."""
    model = Model("endpoint-spread")
    view = model.add(ArchiType.View, "V")

    center = model.add(ArchiType.ApplicationComponent, "Center")
    left_1 = model.add(ArchiType.ApplicationComponent, "Left 1")
    left_2 = model.add(ArchiType.ApplicationComponent, "Left 2")
    right_1 = model.add(ArchiType.ApplicationComponent, "Right 1")
    right_2 = model.add(ArchiType.ApplicationComponent, "Right 2")

    center_node = view.add(center, x=200, y=120)
    left_1_node = view.add(left_1, x=20, y=80)
    left_2_node = view.add(left_2, x=20, y=180)
    right_1_node = view.add(right_1, x=420, y=90)
    right_2_node = view.add(right_2, x=420, y=190)

    rel_1 = model.add_relationship(ArchiType.Serving, source=center, target=right_1)
    rel_2 = model.add_relationship(ArchiType.Serving, source=center, target=right_2)
    rel_3 = model.add_relationship(ArchiType.Serving, source=left_1, target=center)
    rel_4 = model.add_relationship(ArchiType.Serving, source=left_2, target=center)

    view.add_connection(ref=rel_1.uuid, source=center_node, target=right_1_node)
    view.add_connection(ref=rel_2.uuid, source=center_node, target=right_2_node)
    view.add_connection(ref=rel_3.uuid, source=left_1_node, target=center_node)
    view.add_connection(ref=rel_4.uuid, source=left_2_node, target=center_node)

    svg_string = view.to_svg()
    root = ET.fromstring(svg_string)
    ns = '{http://www.w3.org/2000/svg}'
    polylines = root.findall(f'.//{ns}polyline')
    assert len(polylines) == 4

    points = []
    for polyline in polylines:
        raw = polyline.get('points')
        assert raw is not None
        coords = [tuple(float(v) for v in pt.split(',')) for pt in raw.split(' ')]
        points.append((coords[0], coords[-1]))

    outgoing_starts = {round(sy, 1) for (sx, sy), _ in points if sx > 250}
    incoming_ends = {round(ey, 1) for _, (ex, ey) in points if ex < 250}

    assert len(outgoing_starts) > 1
    assert len(incoming_ends) > 1


@pytest.mark.xfail(reason="SVG connection routing orthogonalization needs investigation - bendpoint/side computation may need revision")
def test_svg_export_uses_orthogonal_connection_segments():
    """SVG connection segments should be horizontal or vertical only."""
    model = Model("orthogonal-svg")
    view = model.add(ArchiType.View, "V")

    a = model.add(ArchiType.ApplicationComponent, "A")
    b = model.add(ArchiType.ApplicationComponent, "B")
    c = model.add(ArchiType.ApplicationComponent, "C")

    na = view.add(a, x=30, y=30)
    nb = view.add(b, x=250, y=120)
    nc = view.add(c, x=470, y=30)

    rel_ab = model.add_relationship(ArchiType.Serving, source=a, target=b)
    rel_bc = model.add_relationship(ArchiType.Serving, source=b, target=c)
    view.add_connection(ref=rel_ab.uuid, source=na, target=nb)
    view.add_connection(ref=rel_bc.uuid, source=nb, target=nc)

    svg_string = view.to_svg()
    root = ET.fromstring(svg_string)
    ns = '{http://www.w3.org/2000/svg}'

    for polyline in root.findall(f'.//{ns}polyline'):
        raw = polyline.get('points')
        assert raw is not None
        coords = [tuple(float(v) for v in pt.split(',')) for pt in raw.split(' ')]
        assert len(coords) >= 2
        for p1, p2 in zip(coords, coords[1:], strict=False):
            assert p1[0] == p2[0] or p1[1] == p2[1]


def test_svg_export_keeps_horizontal_target_marker_horizontal():
    """A connection entering a vertical edge should end with a horizontal segment."""
    model = Model("marker-orientation")
    view = model.add(ArchiType.View, "V")

    left = model.add(ArchiType.ApplicationComponent, "Left")
    right = model.add(ArchiType.ApplicationComponent, "Right")
    left_node = view.add(left, x=40, y=120)
    right_node = view.add(right, x=260, y=120)
    rel = model.add_relationship(ArchiType.Serving, source=left, target=right)
    view.add_connection(ref=rel.uuid, source=left_node, target=right_node)

    svg_string = view.to_svg()
    root = ET.fromstring(svg_string)
    ns = '{http://www.w3.org/2000/svg}'
    polyline = root.find(f'.//{ns}polyline')
    assert polyline is not None

    coords = [tuple(float(v) for v in pt.split(',')) for pt in polyline.get('points', '').split(' ')]
    assert len(coords) >= 2
    last = coords[-1]
    prev = coords[-2]
    assert last[1] == prev[1]


@pytest.mark.xfail(reason="SVG connection routing orthogonalization needs investigation - source orientation logic may be incorrect")
def test_svg_export_starts_vertically_from_horizontal_source_edge():
    """A connection leaving a vertical source edge should start with a horizontal segment."""
    model = Model("source-stub")
    view = model.add(ArchiType.View, "V")

    source = model.add(ArchiType.ApplicationComponent, "Source")
    target = model.add(ArchiType.ApplicationComponent, "Target")
    source_node = view.add(source, x=40, y=40)
    target_node = view.add(target, x=260, y=180)
    rel = model.add_relationship(ArchiType.Serving, source=source, target=target)
    view.add_connection(ref=rel.uuid, source=source_node, target=target_node)

    svg_string = view.to_svg()
    root = ET.fromstring(svg_string)
    ns = '{http://www.w3.org/2000/svg}'
    polyline = root.find(f'.//{ns}polyline')
    assert polyline is not None

    coords = [tuple(float(v) for v in pt.split(',')) for pt in polyline.get('points', '').split(' ')]
    assert len(coords) >= 2
    assert coords[0][1] == coords[1][1]


def test_svg_export_renders_element_name_inside_rectangle():
    """Element names should be placed inside the element body."""
    model = Model("label-inside")
    view = model.add(ArchiType.View, "V")

    elem = model.add(ArchiType.ApplicationComponent, "Inside Label")
    view.add(elem, x=50, y=60, w=140, h=70)

    svg_string = view.to_svg()
    root = ET.fromstring(svg_string)
    ns = '{http://www.w3.org/2000/svg}'

    texts = root.findall(f'.//{ns}text')
    assert texts, "No text elements rendered"

    text = texts[0]
    assert text.text == 'Inside Label'

    text_y = float(text.get('y', '0'))
    text_x = float(text.get('x', '0'))

    assert 50 < text_x < 190
    assert 60 < text_y < 130


def _parse_polyline_points(polyline):
    return [tuple(float(v) for v in pt.split(',')) for pt in polyline.get('points', '').split(' ') if pt]


@pytest.mark.xfail(reason="SVG connection routing needs investigation - endpoint spreading logic may need revision")
def test_svg_export_spreads_source_connection_points_away_from_corners():
    """Repeated outgoing connections should stay in the middle of the source edge."""
    model = Model("spread-source")
    view = model.add(ArchiType.View, "V")

    source = model.add(ArchiType.ApplicationComponent, "Source")
    source_node = view.add(source, x=40, y=80, w=120, h=60)

    targets = []
    for idx in range(5):
        target = model.add(ArchiType.ApplicationComponent, f"Target {idx}")
        targets.append(view.add(target, x=280, y=20 + idx * 50, w=120, h=60))
        rel = model.add_relationship(ArchiType.Serving, source=source, target=target)
        view.add_connection(ref=rel.uuid, source=source_node, target=targets[-1])

    root = ET.fromstring(view.to_svg())
    ns = '{http://www.w3.org/2000/svg}'
    source_right_x = 40 + 120
    source_y_min = 80 + 12
    source_y_max = 80 + 60 - 12

    polylines = root.findall(f'.//{ns}polyline')
    assert len(polylines) == 5

    first_points = [_parse_polyline_points(polyline)[0] for polyline in polylines]
    assert len({round(pt[1], 1) for pt in first_points}) > 1
    for x, y in first_points:
        assert abs(x - source_right_x) <= 1
        assert source_y_min - 1 <= y <= source_y_max + 1


@pytest.mark.xfail(reason="SVG connection routing needs investigation - endpoint spreading logic may need revision")
def test_svg_export_spreads_target_connection_points_away_from_corners():
    """Repeated incoming connections should stay in the middle of the target edge."""
    model = Model("spread-target")
    view = model.add(ArchiType.View, "V")

    target = model.add(ArchiType.ApplicationComponent, "Target")
    target_node = view.add(target, x=280, y=120, w=120, h=60)

    sources = []
    for idx in range(5):
        source = model.add(ArchiType.ApplicationComponent, f"Source {idx}")
        sources.append(view.add(source, x=40, y=20 + idx * 50, w=120, h=60))
        rel = model.add_relationship(ArchiType.Serving, source=source, target=target)
        view.add_connection(ref=rel.uuid, source=sources[-1], target=target_node)

    root = ET.fromstring(view.to_svg())
    ns = '{http://www.w3.org/2000/svg}'
    target_left_x = 280
    target_y_min = 120 + 12
    target_y_max = 120 + 60 - 12

    polylines = root.findall(f'.//{ns}polyline')
    assert len(polylines) == 5

    last_points = [_parse_polyline_points(polyline)[-1] for polyline in polylines]
    assert len({round(pt[1], 1) for pt in last_points}) > 1
    for x, y in last_points:
        assert abs(x - target_left_x) <= 1
        assert target_y_min - 1 <= y <= target_y_max + 1


# ── Junction rendering ────────────────────────────────────────────────────────

def test_svg_or_junction_renders_white_circle():
    """OrJunction should produce a white-filled circle."""
    model = Model("junctions")
    view = model.add(ArchiType.View, "V")
    elem = model.add(ArchiType.OrJunction, "or")
    view.add(elem, x=50, y=50, w=20, h=20)
    svg = view.to_svg()
    root = ET.fromstring(svg)
    ns = "{http://www.w3.org/2000/svg}"
    circles = root.findall(f".//{ns}circle")
    assert circles, "OrJunction should render a circle"
    assert any(c.get("fill") == "white" for c in circles), "OrJunction circle must be white"


def test_svg_and_junction_renders_black_circle():
    """AndJunction should produce a black-filled circle."""
    model = Model("junctions")
    view = model.add(ArchiType.View, "V")
    elem = model.add(ArchiType.AndJunction, "and")
    view.add(elem, x=50, y=50, w=20, h=20)
    svg = view.to_svg()
    root = ET.fromstring(svg)
    ns = "{http://www.w3.org/2000/svg}"
    circles = root.findall(f".//{ns}circle")
    assert circles, "AndJunction should render a circle"
    assert any(c.get("fill") == "black" for c in circles), "AndJunction circle must be black"


# ── Grouping and Group rendering ─────────────────────────────────────────────

def test_svg_grouping_renders_dashed_path_with_label_in_tab():
    """Grouping should use a dashed L-shaped path and place label in the tab."""
    model = Model("groupings")
    view = model.add(ArchiType.View, "V")
    elem = model.add(ArchiType.Grouping, "MyGroup")
    view.add(elem, x=10, y=10, w=200, h=120)
    svg = view.to_svg()
    root = ET.fromstring(svg)
    ns = "{http://www.w3.org/2000/svg}"
    paths = root.findall(f".//{ns}path[@stroke-dasharray]")
    assert paths, "Grouping should render a dashed path"
    assert any("4,3" in p.get("stroke-dasharray", "") for p in paths)
    texts = root.findall(f".//{ns}text")
    assert any("MyGroup" in (t.text or "") for t in texts)


# ── Access relationship markers ───────────────────────────────────────────────

def _make_access_view(access_type_val):
    model = Model("access")
    view = model.add(ArchiType.View, "V")
    src = model.add(ArchiType.ApplicationComponent, "Src")
    tgt = model.add(ArchiType.DataObject, "Tgt")
    rel = model.add_relationship(ArchiType.Access, source=src, target=tgt)
    rel.access_type = access_type_val
    sn = view.add(src, x=10, y=50)
    tn = view.add(tgt, x=250, y=50)
    view.add_connection(ref=rel.uuid, source=sn, target=tn)
    return ET.fromstring(view.to_svg())


def test_svg_access_read_has_start_marker_only():
    root = _make_access_view("Read")
    ns = "{http://www.w3.org/2000/svg}"
    pls = root.findall(f".//{ns}polyline")
    assert pls
    pl = pls[0]
    assert "arrow-start" in pl.get("marker-start", ""), "Read should have start marker"
    assert "marker-end" not in pl.attrib or not pl.get("marker-end"), "Read should have no end marker"


def test_svg_access_write_has_end_marker_only():
    root = _make_access_view("Write")
    ns = "{http://www.w3.org/2000/svg}"
    pls = root.findall(f".//{ns}polyline")
    assert pls
    pl = pls[0]
    assert "marker-start" not in pl.attrib or not pl.get("marker-start"), "Write should have no start marker"
    assert "arrow-filled" in pl.get("marker-end", ""), "Write should have end marker"


def test_svg_access_readwrite_has_both_markers():
    root = _make_access_view("ReadWrite")
    ns = "{http://www.w3.org/2000/svg}"
    pls = root.findall(f".//{ns}polyline")
    assert pls
    pl = pls[0]
    assert "arrow-start" in pl.get("marker-start", ""), "ReadWrite should have start marker"
    assert "arrow-filled" in pl.get("marker-end", ""), "ReadWrite should have end marker"


def test_svg_access_undefined_has_no_markers():
    root = _make_access_view(None)
    ns = "{http://www.w3.org/2000/svg}"
    pls = root.findall(f".//{ns}polyline")
    assert pls
    pl = pls[0]
    assert not pl.get("marker-start"), "Undefined access should have no start marker"
    assert not pl.get("marker-end"), "Undefined access should have no end marker"


# ── Association directed / undirected ────────────────────────────────────────

def _make_assoc_view(directed: bool):
    model = Model("assoc")
    view = model.add(ArchiType.View, "V")
    a = model.add(ArchiType.ApplicationComponent, "A")
    b = model.add(ArchiType.ApplicationComponent, "B")
    rel = model.add_relationship(ArchiType.Association, source=a, target=b)
    rel.is_directed = directed
    na = view.add(a, x=10, y=50)
    nb = view.add(b, x=250, y=50)
    view.add_connection(ref=rel.uuid, source=na, target=nb)
    return ET.fromstring(view.to_svg())


def test_svg_association_directed_has_end_marker():
    root = _make_assoc_view(True)
    ns = "{http://www.w3.org/2000/svg}"
    pls = root.findall(f".//{ns}polyline")
    assert pls
    assert any("arrow-filled" in pl.get("marker-end", "") for pl in pls), "Directed association needs end marker"


def test_svg_association_undirected_has_no_markers():
    root = _make_assoc_view(False)
    ns = "{http://www.w3.org/2000/svg}"
    pls = root.findall(f".//{ns}polyline")
    assert pls
    pl = pls[0]
    assert not pl.get("marker-start"), "Undirected association: no start marker"
    assert not pl.get("marker-end"), "Undirected association: no end marker"


# ── Influence strength label ─────────────────────────────────────────────────

def test_svg_influence_label_includes_strength():
    model = Model("influence")
    view = model.add(ArchiType.View, "V")
    a = model.add(ArchiType.Driver, "A")
    b = model.add(ArchiType.Goal, "B")
    rel = model.add_relationship(ArchiType.Influence, source=a, target=b)
    rel.influence_strength = "+"
    na = view.add(a, x=10, y=50)
    nb = view.add(b, x=250, y=50)
    view.add_connection(ref=rel.uuid, source=na, target=nb)
    svg = view.to_svg()
    assert "Influence (+)" in svg, "Influence label must include strength"


# ── Composition / Aggregation diamond marker ─────────────────────────────────

def test_svg_composition_has_diamond_start_marker():
    model = Model("comp")
    view = model.add(ArchiType.View, "V")
    a = model.add(ArchiType.ApplicationComponent, "A")
    b = model.add(ArchiType.ApplicationComponent, "B")
    rel = model.add_relationship(ArchiType.Composition, source=a, target=b)
    na = view.add(a, x=10, y=50)
    nb = view.add(b, x=250, y=50)
    view.add_connection(ref=rel.uuid, source=na, target=nb)
    root = ET.fromstring(view.to_svg())
    ns = "{http://www.w3.org/2000/svg}"
    pls = root.findall(f".//{ns}polyline")
    assert pls
    assert any("diamond" in pl.get("marker-start", "") for pl in pls), "Composition needs diamond start"
    assert not any(pl.get("marker-end") for pl in pls), "Composition must have no end marker"


def test_svg_aggregation_has_hollow_diamond_start_marker():
    model = Model("agg")
    view = model.add(ArchiType.View, "V")
    a = model.add(ArchiType.ApplicationComponent, "A")
    b = model.add(ArchiType.ApplicationComponent, "B")
    rel = model.add_relationship(ArchiType.Aggregation, source=a, target=b)
    na = view.add(a, x=10, y=50)
    nb = view.add(b, x=250, y=50)
    view.add_connection(ref=rel.uuid, source=na, target=nb)
    root = ET.fromstring(view.to_svg())
    ns = "{http://www.w3.org/2000/svg}"
    pls = root.findall(f".//{ns}polyline")
    assert pls
    assert any("diamond-hollow" in pl.get("marker-start", "") for pl in pls)


# ── Realization hollow end marker ─────────────────────────────────────────────

def test_svg_realization_has_hollow_arrow_end_marker():
    model = Model("real")
    view = model.add(ArchiType.View, "V")
    a = model.add(ArchiType.ApplicationComponent, "A")
    b = model.add(ArchiType.ApplicationComponent, "B")
    rel = model.add_relationship(ArchiType.Realization, source=a, target=b)
    na = view.add(a, x=10, y=50)
    nb = view.add(b, x=250, y=50)
    view.add_connection(ref=rel.uuid, source=na, target=nb)
    root = ET.fromstring(view.to_svg())
    ns = "{http://www.w3.org/2000/svg}"
    pls = root.findall(f".//{ns}polyline")
    assert pls
    assert any("arrow-hollow" in pl.get("marker-end", "") for pl in pls)


# ── Orthogonal clip branches ──────────────────────────────────────────────────

def test_orthogonal_clip_outside_x_inside_y():
    """Bendpoint left of element: exit left edge at bp.y."""
    from src.pyArchimate.view.layout.export.svg_export import SVGExportService
    bounds = (100.0, 50.0, 200.0, 100.0)
    bp = (50.0, 75.0)  # left of element, inside y-range
    result = SVGExportService._orthogonal_clip(bounds, bp)
    assert result == (100.0, 75.0), f"Expected (100, 75), got {result}"


def test_orthogonal_clip_inside_x_outside_y():
    """Bendpoint below element: exit bottom edge at bp.x."""
    from src.pyArchimate.view.layout.export.svg_export import SVGExportService
    bounds = (100.0, 50.0, 200.0, 100.0)
    bp = (150.0, 150.0)  # inside x-range, below element
    result = SVGExportService._orthogonal_clip(bounds, bp)
    assert result == (150.0, 100.0), f"Expected (150, 100), got {result}"


def test_orthogonal_clip_corner_x_dominates():
    """Bendpoint in corner with larger x-overshoot: exit the x-axis edge."""
    from src.pyArchimate.view.layout.export.svg_export import SVGExportService
    bounds = (100.0, 50.0, 200.0, 100.0)
    bp = (40.0, 110.0)  # left overshoot=60, bottom overshoot=10 → x dominates
    result = SVGExportService._orthogonal_clip(bounds, bp)
    assert result[0] == 100.0, "Should exit left edge"
    assert result[1] == 100.0, "y clamped to element bottom"


def test_orthogonal_clip_corner_y_dominates():
    """Bendpoint in corner with larger y-overshoot: exit the y-axis edge."""
    from src.pyArchimate.view.layout.export.svg_export import SVGExportService
    bounds = (100.0, 50.0, 200.0, 100.0)
    bp = (210.0, 200.0)  # right overshoot=10, bottom overshoot=100 → y dominates
    result = SVGExportService._orthogonal_clip(bounds, bp)
    assert result[1] == 100.0, "Should exit bottom edge"
    assert result[0] == 200.0, "x clamped to element right"


def test_orthogonal_clip_inside_falls_back_to_center_clip():
    """Bendpoint inside element: falls back to centre→waypoint clip.
    If the waypoint is closer than any boundary intersection, the result
    is the waypoint itself (no clipping needed — connection starts there).
    Result must be inside or on the element bounds.
    """
    from src.pyArchimate.view.layout.export.svg_export import SVGExportService
    bounds = (100.0, 50.0, 200.0, 100.0)
    x1, y1, x2, y2 = bounds
    bp = (170.0, 60.0)  # inside element, off-centre toward top-right
    result = SVGExportService._orthogonal_clip(bounds, bp)
    rx, ry = result
    assert x1 - 0.1 <= rx <= x2 + 0.1, f"Result x out of bounds: {rx}"
    assert y1 - 0.1 <= ry <= y2 + 0.1, f"Result y out of bounds: {ry}"


# ── Connection with bendpoints (orthogonal exit) ──────────────────────────────

def test_svg_connection_with_bendpoint_exits_orthogonally():
    """Connection with a bendpoint to the left exits at the left edge at bp.y."""
    model = Model("bend")
    view = model.add(ArchiType.View, "V")
    a = model.add(ArchiType.ApplicationComponent, "A")
    b = model.add(ArchiType.ApplicationComponent, "B")
    rel = model.add_relationship(ArchiType.Serving, source=a, target=b)
    na = view.add(a, x=100, y=50, w=120, h=55)
    nb = view.add(b, x=100, y=200, w=120, h=55)
    conn = view.add_connection(ref=rel.uuid, source=na, target=nb)
    # Manually add a bendpoint to the left of element A at y=90 (within A's y-range)
    from src.pyArchimate.view import Point
    conn.add_bendpoint(Point(30.0, 90.0))  # x=30 < 100=element left
    root = ET.fromstring(view.to_svg())
    ns = "{http://www.w3.org/2000/svg}"
    pls = root.findall(f".//{ns}polyline")
    assert pls
    coords_str = pls[0].get("points", "")
    pts = [tuple(float(v) for v in p.split(",")) for p in coords_str.split()]
    # First point should be at left edge (x≈100) at y≈90 (orthogonal exit)
    assert abs(pts[0][0] - 100) < 2, f"Should exit left edge, got x={pts[0][0]}"
    assert abs(pts[0][1] - 90) < 2, f"Should exit at bp.y=90, got y={pts[0][1]}"


# ── Short type name stripping ─────────────────────────────────────────────────

def test_svg_export_strips_relationship_suffix_from_label():
    model = Model("label-strip")
    view = model.add(ArchiType.View, "V")
    a = model.add(ArchiType.ApplicationComponent, "A")
    b = model.add(ArchiType.ApplicationComponent, "B")
    rel = model.add_relationship(ArchiType.Serving, source=a, target=b)
    na = view.add(a, x=10, y=50)
    nb = view.add(b, x=250, y=50)
    view.add_connection(ref=rel.uuid, source=na, target=nb)
    svg = view.to_svg()
    assert "Serving" in svg
    assert "ServingRelationship" not in svg


# ── icon size threshold ───────────────────────────────────────────────────────

def test_svg_icon_hidden_when_element_too_small():
    """Elements smaller than threshold should not render corner icon."""
    model = Model("tiny")
    view = model.add(ArchiType.View, "V")
    elem = model.add(ArchiType.ApplicationComponent, "tiny")
    view.add(elem, x=10, y=10, w=25, h=20)
    root = ET.fromstring(view.to_svg())
    ns = "{http://www.w3.org/2000/svg}"
    paths = root.findall(f".//{ns}path")
    # Icon path would have fill=none stroke=black; at this size none should appear
    icon_paths = [p for p in paths if p.get("fill") == "none" and p.get("stroke") == "black"]
    assert not icon_paths, "No icon path expected for element below size threshold"


def test_svg_icon_shown_when_element_large_enough():
    """Elements above the threshold should render the corner icon."""
    model = Model("big")
    view = model.add(ArchiType.View, "V")
    elem = model.add(ArchiType.ApplicationComponent, "big")
    view.add(elem, x=10, y=10, w=120, h=55)
    root = ET.fromstring(view.to_svg())
    ns = "{http://www.w3.org/2000/svg}"
    icon_paths = [p for p in root.findall(f".//{ns}path")
                  if p.get("fill") == "none" and p.get("stroke") == "black"]
    assert icon_paths, "Icon path expected for element above size threshold"


if __name__ == '__main__':
    test_svg_export_with_demo_view()
    test_svg_export_to_file()
    test_svg_export_empty_view()
    print("\n✓ All SVG export integration tests passed!")
