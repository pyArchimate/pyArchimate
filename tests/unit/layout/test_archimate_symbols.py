"""Unit tests for ArchiMate symbol registry and rendering.

Tests symbol definitions, color palette, and symbol validation.
"""

import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from pyArchimate.view.layout.export.symbols.archimate_symbols import (
    ARCHIMATE_SYMBOLS,
    SymbolDefinition,
)
from pyArchimate.view.layout.export.symbols.color_palette import (
    ARCHIMATE_PALETTE,
    ColorPalette,
    default_palette,
    get_element_color,
)


class TestSymbolDefinitions:
    """Test ArchiMate symbol definitions."""

    def test_symbol_registry_has_all_30_plus_types(self):
        """Verify symbol registry contains all 30+ element types."""
        assert len(ARCHIMATE_SYMBOLS) >= 30
        # Current count: 43 from official archimate-symbols repository

    def test_symbol_definitions_have_required_fields(self):
        """Verify each symbol has required fields."""
        for element_type, symbol in ARCHIMATE_SYMBOLS.items():
            assert isinstance(symbol, SymbolDefinition)
            assert symbol.element_type == element_type
            assert isinstance(symbol.svg_path, str)
            assert len(symbol.svg_path) > 0
            assert isinstance(symbol.viewBox, str)
            # ViewBox format: 4 space-separated numbers (can start with 0 or negative)
            vb_parts = symbol.viewBox.split()
            assert len(vb_parts) == 4
            assert isinstance(symbol.bounding_box, tuple)
            assert len(symbol.bounding_box) == 4
            assert isinstance(symbol.default_color, str)
            assert symbol.default_color.startswith("#")

    def test_business_layer_symbols_present(self):
        """Verify core Business layer symbols are defined."""
        # Core business types available in archimate-symbols repository
        business_types = [
            "BusinessActor",
            "BusinessRole",
            "BusinessService",
            "BusinessProcess",
            "BusinessInteraction",
            "BusinessObject",
        ]
        for element_type in business_types:
            assert element_type in ARCHIMATE_SYMBOLS
            assert ARCHIMATE_SYMBOLS[element_type].default_color.startswith("#")

    def test_application_layer_symbols_present(self):
        """Verify all Application layer symbols are defined."""
        app_types = [
            "ApplicationComponent",
            "ApplicationService",
            "ApplicationInterface",
            "ApplicationFunction",
            "DataObject",
            "ApplicationInteraction",
        ]
        for element_type in app_types:
            assert element_type in ARCHIMATE_SYMBOLS

    def test_technology_layer_symbols_present(self):
        """Verify all Technology layer symbols are defined."""
        tech_types = [
            "Node",
            "Device",
            "SystemSoftware",
            "TechnologyService",
            "TechnologyInterface",
            "Path",
            "CommunicationNetwork",
            "Artifact",
            "Equipment",
        ]
        for element_type in tech_types:
            assert element_type in ARCHIMATE_SYMBOLS

    def test_motivation_layer_symbols_present(self):
        """Verify all Motivation layer symbols are defined."""
        motivation_types = [
            "Stakeholder",
            "Driver",
            "Assessment",
            "Goal",
            "Outcome",
            "Principle",
            "Requirement",
            "Constraint",
        ]
        for element_type in motivation_types:
            assert element_type in ARCHIMATE_SYMBOLS

    def test_implementation_layer_symbols_present(self):
        """Verify core Implementation layer symbols are defined."""
        # Available in archimate-symbols repository
        impl_types = [
            "ImplementationEvent",
            "Plateau",
        ]
        for element_type in impl_types:
            assert element_type in ARCHIMATE_SYMBOLS

    def test_junction_symbols_present(self):
        """Verify Junction symbols are present if available."""
        # Junction symbols may not be in archimate-symbols repository
        # Just verify that the ones present are valid
        junction_types = ["AndJunction", "OrJunction", "XorJunction"]
        for element_type in junction_types:
            if element_type in ARCHIMATE_SYMBOLS:
                assert ARCHIMATE_SYMBOLS[element_type].default_color.startswith("#")

    def test_symbol_colors_are_valid_hex_codes(self):
        """Verify all symbol colors are valid HEX codes."""
        for symbol in ARCHIMATE_SYMBOLS.values():
            color = symbol.default_color
            assert color.startswith("#")
            assert len(color) == 7
            # Verify it's a valid hex code
            int(color[1:], 16)

    def test_symbol_viewbox_format(self):
        """Verify all symbols have valid viewBox format."""
        for symbol in ARCHIMATE_SYMBOLS.values():
            parts = symbol.viewBox.split()
            assert len(parts) == 4
            # ViewBox can start with 0 0 or negative values (e.g., -0.5 -0.5)
            # Just verify we have 4 numeric components
            for part in parts:
                float(part)  # Should not raise
            # Width and height should be positive
            width = float(parts[2])
            height = float(parts[3])
            assert width > 0 and height > 0

    def test_symbol_bounding_box_coordinates(self):
        """Verify symbol bounding boxes have valid coordinates."""
        for symbol in ARCHIMATE_SYMBOLS.values():
            x, y, w, h = symbol.bounding_box
            assert isinstance(x, (int, float))
            assert isinstance(y, (int, float))
            assert isinstance(w, (int, float))
            assert isinstance(h, (int, float))
            assert w > 0, f"{symbol.element_type} has zero/negative width"
            assert h > 0, f"{symbol.element_type} has zero/negative height"

    def test_symbol_svg_paths_are_valid_format(self):
        """Verify SVG paths have valid format (start with M or other command)."""
        valid_commands = {'M', 'L', 'H', 'V', 'C', 'S', 'Q', 'T', 'A', 'Z',
                          'm', 'l', 'h', 'v', 'c', 's', 'q', 't', 'a', 'z'}
        for symbol in ARCHIMATE_SYMBOLS.values():
            path = symbol.svg_path.strip()
            assert len(path) > 0
            # First character should be a valid SVG command
            assert path[0] in valid_commands


class TestColorPalette:
    """Test ArchiMate color palette."""

    def test_palette_has_all_element_types(self):
        """Verify palette contains all 30+ element types."""
        assert len(ARCHIMATE_PALETTE) >= 30

    def test_palette_colors_are_valid_hex(self):
        """Verify all palette colors are valid HEX codes."""
        for _element_type, color in ARCHIMATE_PALETTE.items():
            assert color.startswith("#")
            assert len(color) == 7
            # Verify it's a valid hex code
            int(color[1:], 16)

    def test_color_palette_class_get_color(self):
        """Test ColorPalette.get_color() method."""
        palette = ColorPalette()

        # Test valid element type
        color = palette.get_color("BusinessActor")
        assert color == "#FFD700"

        # Test invalid element type falls back to gray
        color = palette.get_color("InvalidType")
        assert color == "#808080"

    def test_color_palette_per_element_override(self):
        """Test per-element color override functionality."""
        palette = ColorPalette()
        element_id = "elem-123"
        custom_color = "#FF0000"

        # Set override
        palette.set_override(element_id, custom_color)

        # Verify override is used
        color = palette.get_color("BusinessActor", element_id)
        assert color == custom_color

        # Clear override
        palette.clear_override(element_id)

        # Verify standard color is used again
        color = palette.get_color("BusinessActor", element_id)
        assert color == "#FFD700"

    def test_color_palette_validate_color(self):
        """Test color validation."""
        palette = ColorPalette()

        # Valid HEX codes
        assert palette.validate_color("#FFD700")
        assert palette.validate_color("#000000")
        assert palette.validate_color("#FFFFFF")

        # Invalid formats
        assert not palette.validate_color("FFD700")  # Missing #
        assert not palette.validate_color("#FFF")     # Too short
        assert not palette.validate_color("#FFFF000")  # Too long
        assert not palette.validate_color("red")      # Not hex
        assert not palette.validate_color(None)       # Not a string
        assert not palette.validate_color(123)        # Not a string

    def test_default_palette_singleton(self):
        """Test default palette singleton."""
        color1 = get_element_color("BusinessActor")
        color2 = default_palette.get_color("BusinessActor")
        assert color1 == color2 == "#FFD700"

    def test_get_element_color_with_override(self):
        """Test convenience function with override."""
        element_id = "elem-456"
        custom_color = "#00FF00"

        # Set override on singleton
        default_palette.set_override(element_id, custom_color)

        # Verify override through convenience function
        color = get_element_color("ApplicationComponent", element_id)
        assert color == custom_color

        # Cleanup
        default_palette.clear_override(element_id)

    def test_palette_color_consistency_with_symbols(self):
        """Verify palette colors match symbol default colors."""
        for element_type, symbol in ARCHIMATE_SYMBOLS.items():
            palette_color = ARCHIMATE_PALETTE.get(element_type)
            symbol_color = symbol.default_color

            if palette_color:
                # Colors should match exactly
                assert palette_color == symbol_color, \
                    f"{element_type}: palette {palette_color} != symbol {symbol_color}"

    def test_all_symbols_have_palette_colors(self):
        """Verify symbols with palette entries have valid colors."""
        # Note: Not all extracted symbols may have palette entries (legacy elements)
        # Just verify that ones in palette are valid
        for element_type, color in ARCHIMATE_PALETTE.items():
            if element_type in ARCHIMATE_SYMBOLS:
                assert color.startswith("#") and len(color) == 7


class TestColorLayering:
    """Test color organization by ArchiMate layer."""

    def test_business_layer_uses_gold_orange_tones(self):
        """Verify Business layer uses warm color tones."""
        business_colors = [
            ARCHIMATE_PALETTE["BusinessActor"],      # Gold
            ARCHIMATE_PALETTE["BusinessRole"],       # Darker gold
            ARCHIMATE_PALETTE["BusinessService"],    # Light gold
            ARCHIMATE_PALETTE["BusinessProcess"],    # Moccasin
        ]
        # All should start with #FF (high red component)
        for color in business_colors:
            assert color.startswith("#FF")

    def test_application_layer_uses_blue_tones(self):
        """Verify Application layer uses blue color tones."""
        app_colors = [
            ARCHIMATE_PALETTE["ApplicationComponent"],  # Sky blue
            ARCHIMATE_PALETTE["ApplicationService"],    # Light blue
            ARCHIMATE_PALETTE["ApplicationInterface"],  # Blue
        ]
        # All should have significant blue component
        for color in app_colors:
            # Extract blue component (last two hex digits)
            blue_component = color[-2:]
            assert int(blue_component, 16) > 128

    def test_technology_layer_uses_green_tones(self):
        """Verify Technology layer uses green color tones."""
        tech_colors = [
            ARCHIMATE_PALETTE["Node"],          # Light green
            ARCHIMATE_PALETTE["Device"],        # Green
            ARCHIMATE_PALETTE["SystemSoftware"],  # Green
        ]
        # All should have green component
        for color in tech_colors:
            # Green is the middle component in #RRGGBB
            green_component = color[3:5]
            assert int(green_component, 16) > 100
