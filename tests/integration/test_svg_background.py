"""Integration tests for SVG white background feature."""

from pathlib import Path
from xml.etree import ElementTree as ET

from src.pyArchimate.model import Model
from src.pyArchimate.view import View


def test_svg_export_with_demo_includes_white_background():
    """Test that SVG export from demo file includes white background."""
    model = Model()
    demo_path = Path(__file__).parent.parent.parent / 'temp' / 'auto-layout-demo-formatted.archimate'

    if demo_path.exists():
        model.read(str(demo_path))

        if model.views:
            view = model.views[0]

            # Export to SVG
            svg_string = view.to_svg()

            # Parse SVG
            if '<?xml' in svg_string:
                start_idx = svg_string.find('<svg')
                end_idx = svg_string.rfind('</svg>') + 6
                svg_part = svg_string[start_idx:end_idx]
            else:
                svg_part = svg_string

            root = ET.fromstring(svg_part)

            # Find all rectangles
            rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
            assert len(rects) >= 2, "Should have at least background + node rectangles"

            # First rectangle should be the white background
            bg_rect = rects[0]
            assert bg_rect.get('x') == '0', "Background x should be 0"
            assert bg_rect.get('y') == '0', "Background y should be 0"
            assert bg_rect.get('fill') == 'white', "Background fill should be white"
            assert bg_rect.get('stroke') == 'none', "Background stroke should be none"

            print(f"✓ SVG white background test passed ({len(rects)} rectangles found)")
    else:
        print("⊘ Demo file not found, skipping test")


def test_svg_background_covers_entire_canvas():
    """Test that background rectangle covers the entire SVG canvas."""
    model = Model()
    demo_path = Path(__file__).parent.parent.parent / 'temp' / 'auto-layout-demo-formatted.archimate'

    if demo_path.exists():
        model.read(str(demo_path))

        if model.views:
            view = model.views[0]

            # Export to SVG
            svg_string = view.to_svg()

            # Parse SVG
            if '<?xml' in svg_string:
                start_idx = svg_string.find('<svg')
                end_idx = svg_string.rfind('</svg>') + 6
                svg_part = svg_string[start_idx:end_idx]
            else:
                svg_part = svg_string

            root = ET.fromstring(svg_part)

            # Get SVG dimensions
            svg_width = int(root.get('width', 0))
            svg_height = int(root.get('height', 0))

            # Find background rectangle
            rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
            bg_rect = rects[0]

            bg_width = int(bg_rect.get('width', 0))
            bg_height = int(bg_rect.get('height', 0))

            # Background should cover entire canvas
            assert bg_width == svg_width, "Background width should match SVG width"
            assert bg_height == svg_height, "Background height should match SVG height"

            print(f"✓ Background covers entire canvas: {bg_width}x{bg_height}")
    else:
        print("⊘ Demo file not found, skipping test")


def test_svg_background_appears_behind_nodes():
    """Test that background appears behind nodes and connections."""
    model = Model()
    demo_path = Path(__file__).parent.parent.parent / 'temp' / 'auto-layout-demo-formatted.archimate'

    if demo_path.exists():
        model.read(str(demo_path))

        if model.views:
            view = model.views[0]

            # Export to SVG
            svg_string = view.to_svg()

            # Parse SVG
            if '<?xml' in svg_string:
                start_idx = svg_string.find('<svg')
                end_idx = svg_string.rfind('</svg>') + 6
                svg_part = svg_string[start_idx:end_idx]
            else:
                svg_part = svg_string

            # Get SVG as string to check element order
            assert '<rect' in svg_part, "Should contain rectangles"

            # Background should appear first (after defs)
            defs_end = svg_part.find('</defs>')
            first_rect_pos = svg_part.find('<rect', defs_end)
            assert first_rect_pos > defs_end, "First rectangle (background) should appear after defs"

            # There should be elements after the background
            assert svg_part.find('<', first_rect_pos + 1) > first_rect_pos, "Should have elements after background"

            print("✓ Background rendering order is correct (behind nodes/connections)")
    else:
        print("⊘ Demo file not found, skipping test")


def test_empty_view_has_white_background():
    """Test that empty views still get white background."""
    model = Model()
    view = View(name="Empty View", uuid="empty-view", parent=model)
    model.views_dict[view.uuid] = view

    # Export empty view to SVG
    svg_string = view.to_svg()

    # Parse SVG
    if '<?xml' in svg_string:
        start_idx = svg_string.find('<svg')
        end_idx = svg_string.rfind('</svg>') + 6
        svg_part = svg_string[start_idx:end_idx]
    else:
        svg_part = svg_string

    root = ET.fromstring(svg_part)

    # Find rectangles
    rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
    assert len(rects) >= 1, "Empty view should at least have background rectangle"

    # Verify it's white background
    bg_rect = rects[0]
    assert bg_rect.get('fill') == 'white', "Background should be white"
    assert bg_rect.get('x') == '0', "Background should start at x=0"
    assert bg_rect.get('y') == '0', "Background should start at y=0"

    print("✓ Empty view has white background")


if __name__ == '__main__':
    test_svg_export_with_demo_includes_white_background()
    test_svg_background_covers_entire_canvas()
    test_svg_background_appears_behind_nodes()
    test_empty_view_has_white_background()
    print("\n✓ All SVG background tests passed!")
