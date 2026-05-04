"""Integration tests for SVG export functionality."""

import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from src.pyArchimate.model import Model
from src.pyArchimate.view import View


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


if __name__ == '__main__':
    test_svg_export_with_demo_view()
    test_svg_export_to_file()
    test_svg_export_empty_view()
    print("\n✓ All SVG export integration tests passed!")
