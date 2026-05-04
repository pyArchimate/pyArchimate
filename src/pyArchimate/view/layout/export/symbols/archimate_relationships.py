"""ArchiMate relationship type styling for SVG export.

This module defines the visual representation (stroke style, arrow type, color) for each
ArchiMate relationship type, enabling SVG export to render relationships according to
the official ArchiMate 3.x specification.
"""

from typing import NamedTuple, Optional


class RelationshipStyle(NamedTuple):
    """SVG rendering style for an ArchiMate relationship type."""
    relationship_type: str              # e.g., "ServingRelationship"
    stroke_color: str                   # HEX color code (e.g., "#4A90E2")
    stroke_width: float                 # Line width in pixels (1.0, 1.5, 2.0)
    stroke_dasharray: Optional[str]     # Pattern for dashed/dotted (e.g., "5,5" or "2,4")
    marker_start: Optional[str]         # Start marker (e.g., "url(#diamond-hollow)")
    marker_end: str                     # End marker (e.g., "url(#arrow-filled)")
    arrow_type: str                     # "filled", "hollow", "double", "diamond", "circle"


# ArchiMate 3.x Standard Relationship Styles
ARCHIMATE_RELATIONSHIP_STYLES = {
    # ===== STRUCTURAL RELATIONSHIPS =====
    "Association": RelationshipStyle(
        relationship_type="Association",
        stroke_color="#4A4A4A",
        stroke_width=1.0,
        stroke_dasharray=None,
        marker_start=None,
        marker_end="url(#arrow-filled)",
        arrow_type="filled"
    ),

    "Realization": RelationshipStyle(
        relationship_type="Realization",
        stroke_color="#4A4A4A",
        stroke_width=1.0,
        stroke_dasharray="5,5",
        marker_start=None,
        marker_end="url(#arrow-hollow)",
        arrow_type="hollow"
    ),

    "Aggregation": RelationshipStyle(
        relationship_type="Aggregation",
        stroke_color="#4A4A4A",
        stroke_width=1.0,
        stroke_dasharray=None,
        marker_start="url(#diamond-hollow)",
        marker_end="url(#arrow-filled)",
        arrow_type="diamond"
    ),

    "Composition": RelationshipStyle(
        relationship_type="Composition",
        stroke_color="#4A4A4A",
        stroke_width=1.0,
        stroke_dasharray=None,
        marker_start="url(#diamond-filled)",
        marker_end="url(#arrow-filled)",
        arrow_type="diamond"
    ),

    # ===== DEPENDENCY RELATIONSHIPS =====
    "Access": RelationshipStyle(
        relationship_type="Access",
        stroke_color="#FF6B6B",
        stroke_width=1.0,
        stroke_dasharray="2,4",
        marker_start=None,
        marker_end="url(#arrow-filled)",
        arrow_type="filled"
    ),

    "Serving": RelationshipStyle(
        relationship_type="Serving",
        stroke_color="#4ECDC4",
        stroke_width=1.0,
        stroke_dasharray=None,
        marker_start=None,
        marker_end="url(#arrow-filled)",
        arrow_type="filled"
    ),

    "Implementation": RelationshipStyle(
        relationship_type="Implementation",
        stroke_color="#FFB347",
        stroke_width=1.0,
        stroke_dasharray="5,5",
        marker_start=None,
        marker_end="url(#arrow-hollow)",
        arrow_type="hollow"
    ),

    "Assignment": RelationshipStyle(
        relationship_type="Assignment",
        stroke_color="#9B59B6",
        stroke_width=1.0,
        stroke_dasharray="5,5",
        marker_start=None,
        marker_end="url(#arrow-filled)",
        arrow_type="filled"
    ),

    "Used By": RelationshipStyle(
        relationship_type="Used By",
        stroke_color="#3498DB",
        stroke_width=1.0,
        stroke_dasharray="2,4",
        marker_start=None,
        marker_end="url(#arrow-filled)",
        arrow_type="filled"
    ),

    # ===== DYNAMIC RELATIONSHIPS =====
    "Influence": RelationshipStyle(
        relationship_type="Influence",
        stroke_color="#E74C3C",
        stroke_width=1.0,
        stroke_dasharray="2,4",
        marker_start=None,
        marker_end="url(#arrow-filled)",
        arrow_type="filled"
    ),

    "Triggering": RelationshipStyle(
        relationship_type="Triggering",
        stroke_color="#16A085",
        stroke_width=1.0,
        stroke_dasharray=None,
        marker_start=None,
        marker_end="url(#arrow-filled)",
        arrow_type="filled"
    ),

    "Flow": RelationshipStyle(
        relationship_type="Flow",
        stroke_color="#2980B9",
        stroke_width=1.0,
        stroke_dasharray=None,
        marker_start=None,
        marker_end="url(#arrow-filled)",
        arrow_type="filled"
    ),
}


class RelationshipStyleService:
    """Service for looking up and managing ArchiMate relationship styles."""

    def __init__(self):
        """Initialize the relationship style service."""
        self.styles = ARCHIMATE_RELATIONSHIP_STYLES.copy()
        self._overrides: dict[str, RelationshipStyle] = {}  # connection_id → style

    def get_style(self, relationship_type: str) -> Optional[RelationshipStyle]:
        """Get style for a relationship type.

        Args:
            relationship_type: ArchiMate relationship type (e.g., "ServingRelationship")

        Returns:
            RelationshipStyle if found, None otherwise
        """
        # Try exact match first
        if relationship_type in self.styles:
            return self.styles[relationship_type]

        # Try without "Relationship" suffix
        base_type = relationship_type.replace("Relationship", "")
        if base_type in self.styles:
            return self.styles[base_type]

        # Try common variations
        return None

    def get_all_styles(self) -> dict[str, RelationshipStyle]:
        """Get all relationship styles.

        Returns:
            Dictionary of relationship_type → RelationshipStyle
        """
        return self.styles.copy()

    def validate_styles(self) -> tuple[int, int]:
        """Validate all style definitions.

        Returns:
            Tuple of (valid_count, invalid_count)
        """
        valid = 0
        invalid = 0

        for rel_type, style in self.styles.items():
            try:
                assert style.stroke_color.startswith("#") and len(style.stroke_color) == 7
                assert style.stroke_width > 0
                assert style.marker_end is not None
                assert style.arrow_type in ("filled", "hollow", "double", "diamond", "circle")
                valid += 1
            except AssertionError:
                print(f"Invalid style: {rel_type}")
                invalid += 1

        return valid, invalid

    def apply_overrides(
        self,
        style: RelationshipStyle,
        color_override: Optional[str] = None,
        stroke_style_override: Optional[str] = None,
        stroke_width_override: Optional[float] = None,
    ) -> RelationshipStyle:
        """Apply per-relationship customization overrides to a style.

        Args:
            style: Base RelationshipStyle
            color_override: Optional HEX color code override
            stroke_style_override: Optional stroke pattern override (e.g., "5,5")
            stroke_width_override: Optional stroke width override

        Returns:
            RelationshipStyle with overrides applied
        """
        return RelationshipStyle(
            relationship_type=style.relationship_type,
            stroke_color=color_override or style.stroke_color,
            stroke_width=stroke_width_override or style.stroke_width,
            stroke_dasharray=stroke_style_override if stroke_style_override is not None else style.stroke_dasharray,
            marker_start=style.marker_start,
            marker_end=style.marker_end,
            arrow_type=style.arrow_type,
        )


# Singleton instance for easy access
default_relationship_service = RelationshipStyleService()


def get_relationship_style(relationship_type: str) -> Optional[RelationshipStyle]:
    """Convenience function to get relationship style from default service.

    Args:
        relationship_type: ArchiMate relationship type

    Returns:
        RelationshipStyle if found, None otherwise
    """
    return default_relationship_service.get_style(relationship_type)
