"""Unit tests for ArchiMate relationship rendering styles.

Tests relationship style definitions, service lookups, and customization.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from pyArchimate.view.layout.export.symbols.archimate_relationships import (
    ARCHIMATE_RELATIONSHIP_STYLES,
    RelationshipStyleService,
    get_relationship_style,
)


class TestRelationshipStyles:
    """Test ArchiMate relationship style definitions."""

    def test_styles_defined_for_structural_relationships(self):
        """Verify structural relationship types have defined styles."""
        structural_types = [
            "Association",
            "Realization",
            "Aggregation",
            "Composition",
        ]
        for rel_type in structural_types:
            assert rel_type in ARCHIMATE_RELATIONSHIP_STYLES
            style = ARCHIMATE_RELATIONSHIP_STYLES[rel_type]
            assert style.stroke_color.startswith("#")
            assert style.marker_end is not None

    def test_styles_defined_for_dependency_relationships(self):
        """Verify dependency relationship types have defined styles."""
        dependency_types = [
            "Access",
            "Serving",
            "Implementation",
            "Assignment",
            "Used By",
        ]
        for rel_type in dependency_types:
            assert rel_type in ARCHIMATE_RELATIONSHIP_STYLES

    def test_styles_defined_for_dynamic_relationships(self):
        """Verify dynamic relationship types have defined styles."""
        dynamic_types = [
            "Influence",
            "Triggering",
            "Flow",
        ]
        for rel_type in dynamic_types:
            assert rel_type in ARCHIMATE_RELATIONSHIP_STYLES

    def test_all_styles_have_valid_colors(self):
        """Verify all styles have valid HEX color codes."""
        for _rel_type, style in ARCHIMATE_RELATIONSHIP_STYLES.items():
            assert style.stroke_color.startswith("#")
            assert len(style.stroke_color) == 7
            # Verify it's valid hex
            int(style.stroke_color[1:], 16)

    def test_realization_has_dashed_line(self):
        """Verify Realization relationship uses dotted line."""
        style = ARCHIMATE_RELATIONSHIP_STYLES["Realization"]
        assert style.stroke_dasharray is not None
        assert style.stroke_dasharray == "5,5"  # Per BDD spec (was "2,2")

    def test_realization_uses_hollow_arrow(self):
        """Verify Realization relationship uses hollow arrow."""
        style = ARCHIMATE_RELATIONSHIP_STYLES["Realization"]
        assert style.marker_end == "url(#arrow-hollow)"
        assert style.arrow_type == "hollow"

    def test_serving_has_solid_line(self):
        """Verify Serving relationship uses solid line."""
        style = ARCHIMATE_RELATIONSHIP_STYLES["Serving"]
        assert style.stroke_dasharray is None

    def test_serving_uses_filled_arrow(self):
        """Verify Serving relationship uses filled arrow."""
        style = ARCHIMATE_RELATIONSHIP_STYLES["Serving"]
        assert style.marker_end == "url(#arrow-filled)"
        assert style.arrow_type == "filled"

    def test_aggregation_uses_hollow_diamond(self):
        """Verify Aggregation uses hollow diamond marker."""
        style = ARCHIMATE_RELATIONSHIP_STYLES["Aggregation"]
        assert style.marker_start == "url(#diamond-hollow)"

    def test_composition_uses_filled_diamond(self):
        """Verify Composition uses filled diamond marker."""
        style = ARCHIMATE_RELATIONSHIP_STYLES["Composition"]
        assert style.marker_start == "url(#diamond-filled)"

    def test_access_uses_dotted_line(self):
        """Verify Access relationship uses dotted line."""
        style = ARCHIMATE_RELATIONSHIP_STYLES["Access"]
        assert style.stroke_dasharray is not None
        assert "2,4" in style.stroke_dasharray


class TestRelationshipStyleService:
    """Test RelationshipStyleService functionality."""

    def test_get_style_exact_match(self):
        """Test retrieving style by exact relationship type."""
        service = RelationshipStyleService()
        style = service.get_style("Serving")
        assert style is not None
        assert style.relationship_type == "Serving"

    def test_get_style_with_relationship_suffix(self):
        """Test retrieving style with 'Relationship' suffix."""
        service = RelationshipStyleService()
        style = service.get_style("ServingRelationship")
        assert style is not None
        assert style.relationship_type == "Serving"

    def test_get_style_unknown_type(self):
        """Test retrieving style for unknown relationship type."""
        service = RelationshipStyleService()
        style = service.get_style("UnknownRelationship")
        assert style is None

    def test_get_all_styles(self):
        """Test retrieving all styles."""
        service = RelationshipStyleService()
        all_styles = service.get_all_styles()
        assert len(all_styles) >= 12
        assert "Serving" in all_styles
        assert "Realization" in all_styles

    def test_validate_styles(self):
        """Test style validation."""
        service = RelationshipStyleService()
        valid, invalid = service.validate_styles()
        assert valid >= 12
        assert invalid == 0

    def test_apply_overrides_color(self):
        """Test applying color override to style."""
        service = RelationshipStyleService()
        base_style = service.get_style("Serving")
        override_color = "#FF0000"

        modified_style = service.apply_overrides(
            base_style,
            color_override=override_color,
        )

        assert modified_style.stroke_color == override_color
        assert modified_style.stroke_width == base_style.stroke_width

    def test_apply_overrides_stroke_width(self):
        """Test applying stroke width override."""
        service = RelationshipStyleService()
        base_style = service.get_style("Serving")
        override_width = 2.0

        modified_style = service.apply_overrides(
            base_style,
            stroke_width_override=override_width,
        )

        assert modified_style.stroke_width == override_width
        assert modified_style.stroke_color == base_style.stroke_color

    def test_apply_overrides_stroke_style(self):
        """Test applying stroke style override."""
        service = RelationshipStyleService()
        base_style = service.get_style("Serving")
        override_style = "5,5"

        modified_style = service.apply_overrides(
            base_style,
            stroke_style_override=override_style,
        )

        assert modified_style.stroke_dasharray == override_style

    def test_apply_overrides_multiple(self):
        """Test applying multiple overrides at once."""
        service = RelationshipStyleService()
        base_style = service.get_style("Serving")

        modified_style = service.apply_overrides(
            base_style,
            color_override="#FF0000",
            stroke_width_override=2.0,
            stroke_style_override="5,5",
        )

        assert modified_style.stroke_color == "#FF0000"
        assert modified_style.stroke_width == 2.0
        assert modified_style.stroke_dasharray == "5,5"
        # Original properties should be preserved
        assert modified_style.marker_end == base_style.marker_end


class TestConvenienceFunctions:
    """Test convenience functions for relationship styles."""

    def test_get_relationship_style_function(self):
        """Test convenience function get_relationship_style()."""
        style = get_relationship_style("Serving")
        assert style is not None
        assert style.relationship_type == "Serving"

    def test_get_relationship_style_with_suffix(self):
        """Test convenience function with 'Relationship' suffix."""
        style = get_relationship_style("ServingRelationship")
        assert style is not None


class TestRelationshipTypeVariations:
    """Test handling of relationship type name variations."""

    def test_lookup_with_and_without_suffix(self):
        """Verify both forms of relationship type names work."""
        service = RelationshipStyleService()

        # Without suffix
        style1 = service.get_style("Serving")

        # With suffix
        style2 = service.get_style("ServingRelationship")

        # Should return same style
        assert style1 == style2

    def test_all_types_accessible_with_and_without_suffix(self):
        """Test all relationship types are accessible both ways."""
        service = RelationshipStyleService()

        for rel_type in ARCHIMATE_RELATIONSHIP_STYLES:
            # Get by exact name
            style1 = service.get_style(rel_type)
            assert style1 is not None

            # Get by name with Relationship suffix
            if not rel_type.endswith("Relationship"):
                style2 = service.get_style(f"{rel_type}Relationship")
                assert style2 is not None
                assert style1 == style2


class TestRelationshipColorDiversity:
    """Test that relationship types have distinct colors for visual differentiation."""

    def test_structural_vs_dependency_colors_different(self):
        """Verify structural and dependency relationships use different color families."""
        structural_serving = ARCHIMATE_RELATIONSHIP_STYLES["Serving"]
        dependency_access = ARCHIMATE_RELATIONSHIP_STYLES["Access"]

        # These should have meaningfully different colors
        assert structural_serving.stroke_color != dependency_access.stroke_color

    def test_all_relationships_have_marker_end(self):
        """Verify all relationships have an end marker for direction indication."""
        for rel_type, style in ARCHIMATE_RELATIONSHIP_STYLES.items():
            assert style.marker_end is not None, f"{rel_type} missing marker_end"
