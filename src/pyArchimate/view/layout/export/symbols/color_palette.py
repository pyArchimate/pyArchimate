"""ArchiMate standard color palette for SVG export.

This module provides the ArchiMate 3.x specification color palette, mapping each element
type to its standard color code. Supports per-element color overrides via element properties.
"""


# ArchiMate 3.x Standard Color Palette (Archi tool layer-based colors)
_BUSINESS     = "#fffbdb"
_APPLICATION  = "#daf0f8"
_TECHNOLOGY   = "#daf0e0"
_MOTIVATION   = "#ffe8d0"
_IMPL_MIGR    = "#e8e8d0"
_STRATEGY     = "#f5dbfb"
_GROUP        = "#d9d9d9"

ARCHIMATE_PALETTE = {
    # ===== BUSINESS LAYER =====
    "BusinessActor": _BUSINESS,
    "BusinessCollaboration": _BUSINESS,
    "BusinessEvent": _BUSINESS,
    "BusinessFunction": _BUSINESS,
    "BusinessInteraction": _BUSINESS,
    "BusinessInterface": _BUSINESS,
    "BusinessObject": _BUSINESS,
    "BusinessProcess": _BUSINESS,
    "BusinessRole": _BUSINESS,
    "BusinessService": _BUSINESS,
    "Contract": _BUSINESS,
    "Location": _BUSINESS,
    "Product": _BUSINESS,
    "Representation": _BUSINESS,

    # ===== APPLICATION LAYER =====
    "ApplicationCollaboration": _APPLICATION,
    "ApplicationComponent": _APPLICATION,
    "ApplicationEvent": _APPLICATION,
    "ApplicationFunction": _APPLICATION,
    "ApplicationInteraction": _APPLICATION,
    "ApplicationInterface": _APPLICATION,
    "ApplicationProcess": _APPLICATION,
    "ApplicationService": _APPLICATION,
    "DataObject": _APPLICATION,

    # ===== TECHNOLOGY LAYER =====
    "Artifact": _TECHNOLOGY,
    "CommunicationNetwork": _TECHNOLOGY,
    "Device": _TECHNOLOGY,
    "Equipment": _TECHNOLOGY,
    "Facility": _TECHNOLOGY,
    "Node": _TECHNOLOGY,
    "Path": _TECHNOLOGY,
    "SystemSoftware": _TECHNOLOGY,
    "TechnologyCollaboration": _TECHNOLOGY,
    "TechnologyFunction": _TECHNOLOGY,
    "TechnologyInteraction": _TECHNOLOGY,
    "TechnologyInterface": _TECHNOLOGY,
    "TechnologyProcess": _TECHNOLOGY,
    "TechnologyEvent": _TECHNOLOGY,
    "TechnologyService": _TECHNOLOGY,
    "DistributionNetwork": _TECHNOLOGY,
    "Material": _TECHNOLOGY,

    # ===== MOTIVATION LAYER =====
    "Assessment": _MOTIVATION,
    "Constraint": _MOTIVATION,
    "Driver": _MOTIVATION,
    "Goal": _MOTIVATION,
    "Outcome": _MOTIVATION,
    "Principle": _MOTIVATION,
    "Requirement": _MOTIVATION,
    "Stakeholder": _MOTIVATION,
    "Meaning": _MOTIVATION,
    "Value": _MOTIVATION,

    # ===== STRATEGY LAYER =====
    "Resource": _STRATEGY,
    "Capability": _STRATEGY,
    "ValueStream": _STRATEGY,
    "CourseOfAction": _STRATEGY,

    # ===== IMPLEMENTATION & MIGRATION =====
    "Deliverable": _IMPL_MIGR,
    "DeliverableComponent": _IMPL_MIGR,
    "ImplementationComponent": _IMPL_MIGR,
    "ImplementationEvent": _IMPL_MIGR,
    "Plateau": _IMPL_MIGR,
    "Gap": _IMPL_MIGR,
    "WorkPackage": _IMPL_MIGR,

    # ===== VISUAL GROUPING =====
    "Group": _GROUP,
    "Grouping": "none",  # Transparent (fill="none")

    # ===== JUNCTION TYPES =====
    "AndJunction": "#000000",
    "OrJunction": "#000000",
    "XorJunction": "#000000",
}


class ColorPalette:
    """ArchiMate standard color palette with override support.

    Provides color lookup for element types with support for per-element
    color overrides via element properties (fill_color, line_color).
    """

    def __init__(self, palette_name: str = "archimate_standard"):
        """Initialize color palette.

        Args:
            palette_name: Palette identifier (default: "archimate_standard")
        """
        self.palette_name = palette_name
        self.colors = ARCHIMATE_PALETTE.copy()
        self._overrides: dict[str, str] = {}  # element_id → color_code

    def get_color(self, element_type: str, element_id: str | None = None) -> str:
        """Get color for element type with optional per-element override.

        Args:
            element_type: ArchiMate element type (e.g., "BusinessActor")
            element_id: Optional element UUID for override lookup

        Returns:
            HEX color code (e.g., "#FFD700"). Falls back to gray if type unknown.
        """
        # Check per-element override first
        if element_id and element_id in self._overrides:
            return self._overrides[element_id]

        # Return standard color for type, or fallback to gray for unknown types
        return self.colors.get(element_type, "#808080")

    def set_override(self, element_id: str, color: str) -> None:
        """Set per-element color override.

        Args:
            element_id: Element UUID
            color: HEX color code
        """
        self._overrides[element_id] = color

    def clear_override(self, element_id: str) -> None:
        """Clear per-element color override.

        Args:
            element_id: Element UUID
        """
        if element_id in self._overrides:
            del self._overrides[element_id]

    def get_all_colors(self) -> dict[str, str]:
        """Get complete color mapping (read-only).

        Returns:
            Dictionary of element_type → color_code
        """
        return self.colors.copy()

    def validate_color(self, color: str) -> bool:
        """Validate HEX color code format.

        Args:
            color: HEX color code to validate

        Returns:
            True if valid HEX color, False otherwise
        """
        if not isinstance(color, str):
            return False  # type: ignore[unreachable]
        return (
            color.startswith("#")
            and len(color) == 7
            and self._is_valid_hex(color[1:])
        )

    def _is_valid_hex(self, hex_str: str) -> bool:
        """Check if string is valid hex."""
        try:
            int(hex_str, 16)
            return True
        except ValueError:
            return False


# Singleton instance for easy access
default_palette = ColorPalette()


def get_element_color(element_type: str, element_id: str | None = None) -> str:
    """Convenience function to get element color from default palette.

    Args:
        element_type: ArchiMate element type
        element_id: Optional element UUID for override lookup

    Returns:
        HEX color code
    """
    return default_palette.get_color(element_type, element_id)
