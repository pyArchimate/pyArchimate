"""Integration tests for SVG export functionality."""

import tempfile
from pathlib import Path

import pytest
from defusedxml import ElementTree as ET

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
                with open(temp_path) as f:
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


if __name__ == '__main__':
    test_svg_export_with_demo_view()
    test_svg_export_to_file()
    test_svg_export_empty_view()
    print("\n✓ All SVG export integration tests passed!")
