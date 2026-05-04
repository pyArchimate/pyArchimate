"""ArchiMate standard color palette for SVG export.

This module provides the ArchiMate 3.x specification color palette, mapping each element
type to its standard color code. Supports per-element color overrides via element properties.
"""

from typing import Optional


# ArchiMate 3.x Standard Color Palette
# Colors extracted directly from symbol definitions for consistency
ARCHIMATE_PALETTE = {
    # ===== BUSINESS LAYER =====
    "BusinessActor": "#FFD700",
    "BusinessCollaboration": "#FFE4B5",
    "BusinessEvent": "#FFD180",
    "BusinessFunction": "#FFE4B5",
    "BusinessInteraction": "#FFD180",
    "BusinessInterface": "#FFDB58",
    "BusinessObject": "#FFAB91",
    "BusinessProcess": "#FFE4B5",
    "BusinessRole": "#FFC700",
    "BusinessService": "#FFDB58",
    "Contract": "#FF9800",
    "Location": "#FF6F00",
    "Product": "#FF7043",

    # ===== APPLICATION LAYER =====
    "ApplicationCollaboration": "#B3E5FC",
    "ApplicationComponent": "#87CEEB",
    "ApplicationEvent": "#81D4FA",
    "ApplicationFunction": "#29B6F6",
    "ApplicationInteraction": "#039BE5",
    "ApplicationInterface": "#4FC3F7",
    "ApplicationProcess": "#81D4FA",
    "ApplicationService": "#81D4FA",
    "DataObject": "#0288D1",

    # ===== TECHNOLOGY LAYER =====
    "Artifact": "#2E7D32",
    "CommunicationNetwork": "#388E3C",
    "Device": "#7CFC00",
    "Equipment": "#1B5E20",
    "Facility": "#76FF03",
    "Node": "#90EE90",
    "Path": "#45A049",
    "SystemSoftware": "#76FF03",
    "TechnologyFunction": "#66BB6A",
    "TechnologyInteraction": "#039BE5",
    "TechnologyInterface": "#4CAF50",
    "TechnologyProcess": "#66BB6A",
    "TechnologyService": "#66BB6A",

    # ===== MOTIVATION LAYER =====
    "Assessment": "#FF5252",
    "Constraint": "#AD1457",
    "Driver": "#FF7043",
    "Goal": "#FF1744",
    "Outcome": "#D32F2F",
    "Principle": "#C62828",
    "Requirement": "#B71C1C",
    "Stakeholder": "#E64A19",

    # ===== IMPLEMENTATION LAYER =====
    "DeliverableComponent": "#8E24AA",
    "ImplementationComponent": "#9C27B0",
    "ImplementationEvent": "#7B1FA2",
    "Plateau": "#6A1B9A",

    # ===== OTHER =====
    "Gap": "#424242",
    "Grouping": "#616161",

    # ===== JUNCTION TYPES =====
    "AndJunction": "#455A64",
    "OrJunction": "#546E7A",
    "XorJunction": "#607D8B",
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

    def get_color(self, element_type: str, element_id: Optional[str] = None) -> str:
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
            return False
        if not color.startswith("#"):
            return False
        if len(color) != 7:
            return False
        try:
            int(color[1:], 16)
        except ValueError:
            return False
        return True


# Singleton instance for easy access
default_palette = ColorPalette()


def get_element_color(element_type: str, element_id: Optional[str] = None) -> str:
    """Convenience function to get element color from default palette.

    Args:
        element_type: ArchiMate element type
        element_id: Optional element UUID for override lookup

    Returns:
        HEX color code
    """
    return default_palette.get_color(element_type, element_id)