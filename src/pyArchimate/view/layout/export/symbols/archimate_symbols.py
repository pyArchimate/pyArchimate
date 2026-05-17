"""ArchiMate symbol registry with SVG path definitions for all element types.

This module provides the visual representations of ArchiMate elements for SVG export.
Symbols extracted from: https://github.com/marcelomg/archimate-symbols

Each symbol includes:
- SVG path data
- ViewBox dimensions
- Bounding box for polyline clipping
- Default ArchiMate standard color
"""

from typing import NamedTuple


class SymbolDefinition(NamedTuple):
    """SVG symbol definition for an ArchiMate element type."""

    element_type: str  # e.g., "BusinessActor"
    svg_path: str  # SVG path data (body only, no icon)
    viewBox: str  # ViewBox dimensions  # noqa: N815
    bounding_box: tuple[float, float, float, float]  # (x, y, width, height)
    default_color: str  # HEX RGB color code
    icon_path: str | None = None  # Small icon in top-right corner (optional)
    icon_viewbox: str | None = None  # ViewBox for the icon area (optional)
    body_type: str = "rect"  # "rect" | "rect_header" | "path"


_RECT_PATH = "M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z"
_OCTAGON_PATH = "M 0 10 L 10 0 L 140 0 L 150 10 L 150 65 L 140 75 L 10 75 L 0 65 Z"

# Shared icon constants — all paths in the 150×75 reference coordinate space.
# icon_viewbox format: "min_x min_y width height" — renderer uses min_x/min_y to
# translate the icon to the actual canvas position (top-right corner of each element).

# Event: pentagon with left-pointing chevron notch (ArchiMate standard)
_ICON_EVENT = "M 140.5 8 C 142.99 8 145 10.01 145 12.5 C 145 14.99 142.99 17 140.5 17 L 130 17 L 134.5 12.5 L 130 8 Z"

# Function: bow-tie / elongated hexagon
_ICON_FUNCTION = "M 137.5 5 L 145 8 L 145 20 L 137.5 17 L 130 20 L 130 8 Z"

# Interaction: two back-to-back D-shapes (half-ellipses)
_ICON_INTERACTION = "M 138.25 5 C 141.98 5 145 8.36 145 12.5 C 145 16.64 141.98 20 138.25 20 Z M 136.75 5 C 133.02 5 130 8.36 130 12.5 C 130 16.64 133.02 20 136.75 20 Z"

# Interface: horizontal line stub + circle (lollipop)
# SVG source: Application_interface_2.svg (w=29.52 h=20.49); scale=0.60, offset=(130,5)
_ICON_INTERFACE = "M 130 11.1 L 135.9 11.1 M 141.8 5.2 C 145.1 5.2 147.7 7.9 147.7 11.1 C 147.7 14.4 145.1 17.1 141.8 17.1 C 138.5 17.1 135.9 14.4 135.9 11.1 C 135.9 7.9 138.5 5.2 141.8 5.2 Z"

# Process: rectangle with right-pointing arrowhead
_ICON_PROCESS = "M 130 10.7 L 139 10.7 L 139 8 L 145 12.5 L 139 17 L 139 14.3 L 130 14.3 Z"

# Service: pill / stadium shape
_ICON_SERVICE = "M 140.5 8 C 142.99 8 145 10.01 145 12.5 C 145 14.99 142.99 17 140.5 17 L 134.5 17 C 132.01 17 130 14.99 130 12.5 C 130 10.01 132.01 8 134.5 8 Z"

# Collaboration: two overlapping circles (Venn diagram)
# SVG source: Application_collaboration_2.svg (w=29.55 h=21.03); bezier approximation
_ICON_COLLABORATION = (
    "M 136.5 4.5 C 139.54 4.5 142 7.46 142 10 C 142 12.54 139.54 15.5 136.5 15.5 "
    "C 133.46 15.5 131 12.54 131 10 C 131 7.46 133.46 4.5 136.5 4.5 Z "
    "M 142 4.5 C 145.04 4.5 147.5 7.46 147.5 10 C 147.5 12.54 145.04 15.5 142 15.5 "
    "C 138.96 15.5 136.5 12.54 136.5 10 C 136.5 7.46 138.96 4.5 142 4.5 Z"
)

# Distribution Network: 3D pipe/road parallelogram with corner strokes
# SVG source: Distribution_network_2.svg (w=41.66 h=15.64); scale=0.38, offset=(130,7)
_ICON_DISTRIBUTION_NETWORK = (
    "M 130 10 L 132 8.6 L 143.7 8.6 L 145.8 10.1 L 144 11.3 L 132 11.3 Z "
    "M 132 8.6 L 134.2 7 M 132 11.3 L 134 12.7 M 144 11.3 L 141.7 12.9 M 143.7 8.6 L 141.8 7.2"
)

# System Software: isometric box (like Node but wider proportions)
# SVG source: System_software_2.svg (w=51.02 h=29.76); scale=0.32, offset=(130,4)
_ICON_SYSTEM_SOFTWARE = (
    "M 130 6 L 132 4 L 146.3 4 L 146.3 11.5 L 144.3 13.5 L 130 13.5 Z "
    "M 130 6 L 144.3 6 L 144.3 13.5 M 144.3 6 L 146.3 4"
)


# Symbol Registry: Comprehensive mapping of all ArchiMate element types
ARCHIMATE_SYMBOLS = {
    "ApplicationCollaboration": SymbolDefinition(
        element_type="ApplicationCollaboration",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0f8",
        icon_path=_ICON_COLLABORATION,
        icon_viewbox="129 3 20 15",
        body_type="rect",
    ),
    "ApplicationComponent": SymbolDefinition(
        element_type="ApplicationComponent",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0f8",
        # SVG source: Application_component_2.svg (w=55.28 h=29.76); scale=0.32, offset=(130,5)
        # Main body rect + two left-side tab rectangles
        icon_path="M 132 5 L 147.7 5 L 147.7 14.5 L 132 14.5 Z M 130 6.9 L 134.1 6.9 L 134.1 8.8 L 130 8.8 Z M 130 10.7 L 134.1 10.7 L 134.1 12.6 L 130 12.6 Z",
        icon_viewbox="128 3 22 14",
        body_type="rect",
    ),
    "ApplicationEvent": SymbolDefinition(
        element_type="ApplicationEvent",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0f8",
        icon_path=_ICON_EVENT,
        icon_viewbox="128 5 22 15",
        body_type="rect",
    ),
    "ApplicationFunction": SymbolDefinition(
        element_type="ApplicationFunction",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0f8",
        icon_path=_ICON_FUNCTION,
        icon_viewbox="128 3 22 20",
        body_type="rect",
    ),
    "ApplicationInteraction": SymbolDefinition(
        element_type="ApplicationInteraction",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0f8",
        icon_path=_ICON_INTERACTION,
        icon_viewbox="128 3 22 20",
        body_type="rect",
    ),
    "ApplicationInterface": SymbolDefinition(
        element_type="ApplicationInterface",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0f8",
        icon_path=_ICON_INTERFACE,
        icon_viewbox="128 3 22 16",
        body_type="rect",
    ),
    "ApplicationProcess": SymbolDefinition(
        element_type="ApplicationProcess",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0f8",
        icon_path=_ICON_PROCESS,
        icon_viewbox="128 5 22 15",
        body_type="rect",
    ),
    "ApplicationService": SymbolDefinition(
        element_type="ApplicationService",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0f8",
        icon_path=_ICON_SERVICE,
        icon_viewbox="128 5 22 15",
        body_type="rect",
    ),
    "Artifact": SymbolDefinition(
        element_type="Artifact",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path="M 132 5 L 139.7 5 L 143 8.3 L 143 20 L 132 20 Z M 139.7 5 L 139.7 8.3 L 143 8.3",
        icon_viewbox="128 3 22 20",
        body_type="rect",
    ),
    "Assessment": SymbolDefinition(
        element_type="Assessment",
        svg_path=_OCTAGON_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#ffe8d0",
        # SVG source: Assessment_2.svg (w=7.27 h=7.28); scale=1.65, offset=(130,4)
        # Small circle + diagonal line pointing down-left
        icon_path=(
            "M 142 8.3 C 142 10.7 139.9 12.6 137.4 12.6 C 134.8 12.6 132.8 10.7 132.8 8.3 "
            "C 132.8 5.9 134.8 4 137.4 4 C 139.9 4 142 5.9 142 8.3 Z "
            "M 134.2 11.4 L 130 16"
        ),
        icon_viewbox="128 2 16 16",
        body_type="path",
    ),
    "BusinessActor": SymbolDefinition(
        element_type="BusinessActor",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        # SVG source: Business_actor_2.svg (w=24.69 h=37.75); scale=0.40, offset=(135,3)
        # Head ellipse (bezier) + body line + arms line + two leg lines
        icon_path=(
            "M 143.8 6.2 C 143.8 8 142.1 9.4 139.9 9.4 C 137.8 9.4 136 8 136 6.2 "
            "C 136 4.4 137.8 3 139.9 3 C 142.1 3 143.8 4.4 143.8 6.2 Z "
            "M 139.9 9.4 L 139.9 10.9 M 135 10.9 L 144.9 10.9 "
            "M 139.9 10.9 L 139.9 13.5 M 139.9 13.5 L 135.3 18.1 M 139.9 13.5 L 144.5 18.1"
        ),
        icon_viewbox="133 1 16 19",
        body_type="rect",
    ),
    "BusinessCollaboration": SymbolDefinition(
        element_type="BusinessCollaboration",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        icon_path=_ICON_COLLABORATION,
        icon_viewbox="129 3 20 15",
        body_type="rect",
    ),
    "BusinessEvent": SymbolDefinition(
        element_type="BusinessEvent",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        icon_path=_ICON_EVENT,
        icon_viewbox="128 5 22 15",
        body_type="rect",
    ),
    "BusinessFunction": SymbolDefinition(
        element_type="BusinessFunction",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        icon_path=_ICON_FUNCTION,
        icon_viewbox="128 3 22 20",
        body_type="rect",
    ),
    "BusinessInteraction": SymbolDefinition(
        element_type="BusinessInteraction",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        icon_path=_ICON_INTERACTION,
        icon_viewbox="128 3 22 20",
        body_type="rect",
    ),
    "BusinessInterface": SymbolDefinition(
        element_type="BusinessInterface",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        icon_path=_ICON_INTERFACE,
        icon_viewbox="128 3 22 16",
        body_type="rect",
    ),
    "BusinessObject": SymbolDefinition(
        element_type="BusinessObject",
        svg_path="M 0 15 L 150 15 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        body_type="rect_header",
    ),
    "BusinessProcess": SymbolDefinition(
        element_type="BusinessProcess",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        icon_path=_ICON_PROCESS,
        icon_viewbox="128 5 22 15",
        body_type="rect",
    ),
    "BusinessRole": SymbolDefinition(
        element_type="BusinessRole",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        # SVG source: Business_role_2.svg (w=42.52 h=21.26); scale=0.42, offset=(130,7)
        # C-shaped bracket (open right) + circle at right end
        icon_path=(
            "M 145.2 7 L 132.7 7 C 131.2 7 130 9 130 11.5 C 130 13.9 131.2 15.9 132.7 15.9 L 145.2 15.9 "
            "M 147.9 11.5 C 147.9 13.9 146.7 15.9 145.2 15.9 C 143.7 15.9 142.5 13.9 142.5 11.5 "
            "C 142.5 9 143.7 7 145.2 7 C 146.7 7 147.9 9 147.9 11.5 Z"
        ),
        icon_viewbox="128 5 22 13",
        body_type="rect",
    ),
    "BusinessService": SymbolDefinition(
        element_type="BusinessService",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        icon_path=_ICON_SERVICE,
        icon_viewbox="128 5 22 15",
        body_type="rect",
    ),
    "CommunicationNetwork": SymbolDefinition(
        element_type="CommunicationNetwork",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        # SVG source: Communication_network_2.svg (w=38.48 h=12.76); scale=0.45, offset=(130,8)
        # Bidirectional arrow: horizontal line with open arrowheads on both ends
        icon_path=("M 130 10.9 L 147.2 10.9 M 143.4 8 L 147.2 10.9 L 143.4 13.7 M 133.9 13.7 L 130 10.9 L 133.9 8"),
        icon_viewbox="128 6 22 10",
        body_type="rect",
    ),
    "Constraint": SymbolDefinition(
        element_type="Constraint",
        svg_path=_OCTAGON_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#ffe8d0",
        icon_path="M 133.75 9 L 145 9 L 141.25 16 L 130 16 Z M 136.75 9 L 133 16",
        icon_viewbox="128 5 22 15",
        body_type="path",
    ),
    "DataObject": SymbolDefinition(
        element_type="DataObject",
        svg_path="M 0 15 L 150 15 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0f8",
        body_type="rect_header",
    ),
    "Device": SymbolDefinition(
        element_type="Device",
        svg_path="M 0 10 L 10 0 L 150 0 L 150 65 L 140 75 L 0 75 Z M 0 10 L 140 10 L 140 75 M 150 0 L 140 10 M 121.5 28.2 L 120 30 L 135 30 L 133.5 28.2 M 120 15 L 135.0 15 L 135.0 28.2 L 120 28.2 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        body_type="path",
    ),
    "Driver": SymbolDefinition(
        element_type="Driver",
        svg_path=_OCTAGON_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#ffe8d0",
        # SVG source: Driver_2.svg (w=6.96 h=6.96); scale=1.65, offset=(130,4)
        # Target: outer circle + small centre dot
        icon_path=(
            "M 141.5 9.7 C 141.5 12.9 138.9 15.5 135.7 15.5 C 132.6 15.5 130 12.9 130 9.7 "
            "C 130 6.6 132.6 4 135.7 4 C 138.9 4 141.5 6.6 141.5 9.7 Z "
            "M 137.2 9.7 C 137.2 10.5 136.5 11.2 135.7 11.2 C 134.9 11.2 134.3 10.5 134.3 9.7 "
            "C 134.3 8.9 134.9 8.3 135.7 8.3 C 136.5 8.3 137.2 8.9 137.2 9.7 Z"
        ),
        icon_viewbox="128 2 16 16",
        body_type="path",
    ),
    "Equipment": SymbolDefinition(
        element_type="Equipment",
        svg_path="M 0 10 L 10 0 L 150 0 L 150 65 L 140 75 L 0 75 Z M 0 10 L 140 10 L 140 75 M 150 0 L 140 10 M 130.8 20.7 C 131.7 20.7 132.75 20.1 132.75 18.9 C 132.75 17.7 131.7 17.1 130.95 17.1 C 129.6 17.1 128.85 18 128.85 18.9 C 128.85 19.95 129.75 20.7 130.8 20.7 Z M 130.2 22.8 L 130.05 21.75 L 129.15 21.45 L 128.4 22.2 L 127.5 21.3 L 128.1 20.4 L 127.8 19.65 L 126.75 19.65 L 126.75 18.3 L 127.8 18.15 L 128.1 17.4 L 127.5 16.65 L 128.4 15.75 L 129.3 16.35 L 130.05 16.05 L 130.2 15 L 131.55 15 L 131.7 16.05 L 132.45 16.35 L 133.35 15.75 L 134.25 16.65 L 133.65 17.4 L 133.95 18.15 L 135 18.3 L 135 19.65 L 133.95 19.65 L 133.65 20.4 L 134.25 21.15 L 133.35 22.05 L 132.45 21.45 L 131.7 21.75 L 131.55 22.8 L 130.2 22.8 Z M 125.4 27.15 C 126.6 27.15 127.8 26.25 127.8 25.05 C 127.8 23.85 126.75 22.65 125.25 22.65 C 124.05 22.65 122.85 23.7 122.85 25.05 C 122.85 26.1 124.05 27.3 125.4 27.15 Z M 123.15 29.7 L 123.3 28.35 L 122.4 27.75 L 121.2 28.2 L 120.3 26.85 L 121.35 26.1 L 121.2 25.05 L 120 24.45 L 120.45 22.95 L 121.8 23.1 L 122.4 22.2 L 121.95 21 L 123.3 20.25 L 124.2 21.3 L 125.4 21.15 L 125.85 19.95 L 127.5 20.4 L 127.35 21.75 L 128.25 22.35 L 129.45 21.75 L 130.35 23.1 L 129.3 24 L 129.45 25.05 L 130.65 25.5 L 130.2 27 L 128.85 26.85 L 128.25 27.75 L 128.85 26.85 L 128.25 27.75 L 128.85 28.95 L 127.35 29.7 L 126.45 28.65 L 125.4 28.8 L 124.8 30 L 123.15 29.7 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        body_type="path",
    ),
    "Facility": SymbolDefinition(
        element_type="Facility",
        svg_path="M 0 10 L 10 0 L 150 0 L 150 65 L 140 75 L 0 75 Z M 0 10 L 140 10 L 140 75 M 150 0 L 140 10 M 120 30 L 120 15 L 121.95 15 L 121.95 25.5 L 126.3 23.25 L 126.3 25.5 L 130.65 23.25 L 130.65 25.5 L 135 23.25 L 135 30 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        body_type="path",
    ),
    "Gap": SymbolDefinition(
        element_type="Gap",
        svg_path="M 0 0 L 150 0 L 150 51 C 140.13 46.97 126.61 44.7 112.5 44.7 C 98.39 44.7 84.87 46.97 75 51 C 65.13 55.03 51.61 57.3 37.5 57.3 C 23.39 57.3 9.87 55.03 0 51 Z",
        viewBox="-0.5 -0.5 151 61",
        bounding_box=(-0.5, -0.5, 151.0, 61.0),
        default_color="#e8e8d0",
        # SVG source: Gap_2.svg (w=8.50 h=5.19); scale=1.8, offset=(130,5)
        # Circle with horizontal line through upper portion
        icon_path=(
            "M 142.2 9.7 C 142.2 12.2 140.2 14.3 137.7 14.3 C 135.1 14.3 133.1 12.2 133.1 9.7 "
            "C 133.1 7.1 135.1 5 137.7 5 C 140.2 5 142.2 7.1 142.2 9.7 Z "
            "M 130 8.1 L 145.3 8.1"
        ),
        icon_viewbox="128 3 16 13",
        body_type="path",
    ),
    "Goal": SymbolDefinition(
        element_type="Goal",
        svg_path=_OCTAGON_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#ffe8d0",
        # SVG source: Goal_2.svg (w=7.26 h=7.26); scale=1.65, offset=(130,4)
        # Two concentric circles (bullseye)
        icon_path=(
            "M 142 10 C 142 13.3 139.3 16 136 16 C 132.7 16 130 13.3 130 10 "
            "C 130 6.7 132.7 4 136 4 C 139.3 4 142 6.7 142 10 Z "
            "M 140 10 C 140 12.2 138.2 14 136 14 C 133.8 14 132 12.2 132 10 "
            "C 132 7.8 133.8 6 136 6 C 138.2 6 140 7.8 140 10 Z"
        ),
        icon_viewbox="128 2 16 16",
        body_type="path",
    ),
    "ImplementationEvent": SymbolDefinition(
        element_type="ImplementationEvent",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#e8e8d0",
        icon_path=_ICON_EVENT,
        icon_viewbox="128 5 22 15",
        body_type="rect",
    ),
    "Node": SymbolDefinition(
        element_type="Node",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path="M 130 8.75 L 133.75 5 L 145 5 L 145 16.25 L 141.25 20 L 130 20 Z M 130 8.75 L 141.25 8.75 L 141.25 20 M 145 5 L 141.25 8.75",
        icon_viewbox="128 3 22 22",
        body_type="rect",
    ),
    "Outcome": SymbolDefinition(
        element_type="Outcome",
        svg_path=_OCTAGON_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#ffe8d0",
        icon_path="M 136 14 L 143.5 6.5 M 136.3 11 L 136 14 L 139 13.7 M 142 5 L 141.25 8.75 L 145 8",
        icon_viewbox="128 3 22 18",
        body_type="path",
    ),
    "Path": SymbolDefinition(
        element_type="Path",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path="M 133 15 L 130 12.5 L 133 10 M 142 15 L 145 12.5 L 142 10 M 130 12.5 L 145 12.5",
        icon_viewbox="128 8 22 12",
        body_type="rect",
    ),
    "Plateau": SymbolDefinition(
        element_type="Plateau",
        svg_path="M 0 10 L 10 0 L 150 0 L 150 65 L 140 75 L 0 75 Z M 0 10 L 140 10 L 140 75 M 150 0 L 140 10 M 126 15 L 135.0 15 L 135.0 18.0 L 126 18.0 Z M 123 21 L 132.0 21 L 132.0 24.0 L 123 24.0 Z M 120 27 L 129.0 27 L 129.0 30.0 L 120 30.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#e8e8d0",
        body_type="path",
    ),
    "Principle": SymbolDefinition(
        element_type="Principle",
        svg_path=_OCTAGON_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#ffe8d0",
        icon_path="M 130.75 5.75 C 135.21 4.86 139.79 4.86 144.25 5.75 C 145.14 10.21 145.14 14.79 144.25 19.25 C 139.79 20.14 135.21 20.14 130.75 19.25 C 129.86 14.79 129.86 10.21 130.75 5.75 Z M 136.75 15.5 L 136.3 7.25 L 138.7 7.25 L 138.25 15.5 Z M 136.75 16.25 L 138.25 16.25 L 138.25 17.75 L 136.75 17.75 Z",
        icon_viewbox="128 3 22 20",
        body_type="path",
    ),
    "Requirement": SymbolDefinition(
        element_type="Requirement",
        svg_path=_OCTAGON_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#ffe8d0",
        icon_path="M 133.75 9 L 145 9 L 141.25 16 L 130 16 Z",
        icon_viewbox="128 5 22 15",
        body_type="path",
    ),
    "Stakeholder": SymbolDefinition(
        element_type="Stakeholder",
        svg_path=_OCTAGON_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#ffe8d0",
        # Same C-bracket + circle as BusinessRole (ArchiMate standard)
        icon_path=(
            "M 145.2 7 L 132.7 7 C 131.2 7 130 9 130 11.5 C 130 13.9 131.2 15.9 132.7 15.9 L 145.2 15.9 "
            "M 147.9 11.5 C 147.9 13.9 146.7 15.9 145.2 15.9 C 143.7 15.9 142.5 13.9 142.5 11.5 "
            "C 142.5 9 143.7 7 145.2 7 C 146.7 7 147.9 9 147.9 11.5 Z"
        ),
        icon_viewbox="128 5 22 13",
        body_type="path",
    ),
    "SystemSoftware": SymbolDefinition(
        element_type="SystemSoftware",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path=_ICON_SYSTEM_SOFTWARE,
        icon_viewbox="128 2 20 14",
        body_type="rect",
    ),
    "TechnologyFunction": SymbolDefinition(
        element_type="TechnologyFunction",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path=_ICON_FUNCTION,
        icon_viewbox="128 3 22 20",
        body_type="rect",
    ),
    "TechnologyInteraction": SymbolDefinition(
        element_type="TechnologyInteraction",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path=_ICON_INTERACTION,
        icon_viewbox="128 3 22 20",
        body_type="rect",
    ),
    "TechnologyInterface": SymbolDefinition(
        element_type="TechnologyInterface",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path=_ICON_INTERFACE,
        icon_viewbox="128 3 22 16",
        body_type="rect",
    ),
    "TechnologyProcess": SymbolDefinition(
        element_type="TechnologyProcess",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path=_ICON_PROCESS,
        icon_viewbox="128 5 22 15",
        body_type="rect",
    ),
    "TechnologyService": SymbolDefinition(
        element_type="TechnologyService",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path=_ICON_SERVICE,
        icon_viewbox="128 5 22 15",
        body_type="rect",
    ),
    # ===== MISSING ELEMENTS - Added to complete the palette =====
    "Capability": SymbolDefinition(
        element_type="Capability",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#f5dbfb",
        # SVG source: Capability_2.svg (w=8.30 h=8.30); scale=1.808, offset=(130,3)
        # Three-step staircase (ascending right) + internal grid lines
        icon_path=(
            "M 130 13 L 135 13 L 135 8 L 140 8 L 140 3 L 145 3 L 145 18 L 130 18 Z "
            "M 135 13 L 145 13 M 140 8 L 145 8 M 135 13 L 135 18 M 140 8 L 140 18"
        ),
        icon_viewbox="128 1 18 19",
        body_type="rect",
    ),
    "Contract": SymbolDefinition(
        element_type="Contract",
        # SVG source: Contract.svg (w=72.28 h=29.76); scale=(150/72.28, 75/29.76)
        # Outer rect + header line at 21.4% (y≈16) + footer line at 78.6% (y≈59)
        svg_path="M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z M 0 16 L 150 16 M 0 59 L 150 59",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        body_type="path",
    ),
    "CourseOfAction": SymbolDefinition(
        element_type="CourseOfAction",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#f5dbfb",
        # SVG source: Course_of_action_2.svg (w=12.73 h=9.49); scale=1.4, offset=(129,3)
        # Outer circle + curved arrow + filled dot + inner circle
        icon_path=(
            "M 143.4 11.9 C 145.0 11.4 146.1 10.3 146.6 8.8 C 146.8 8.1 146.8 7.5 146.7 6.9 "
            "C 146.5 5.4 145.6 4.1 144.2 3.5 C 143.4 3.1 142.9 3.0 142.1 3.0 "
            "C 141.3 3.0 140.8 3.1 140.1 3.5 C 139.1 3.9 138.4 4.6 137.9 5.5 "
            "C 137.6 6.3 137.5 6.7 137.5 7.5 C 137.5 8.3 137.6 8.8 137.9 9.5 "
            "C 138.9 11.5 141.2 12.5 143.4 11.9 Z "
            "M 130.6 15.5 C 131.4 14.4 132.2 13.5 133.2 12.9 C 133.7 12.5 133.9 12.4 134.0 12.4 "
            "C 134.0 12.7 134.0 13.2 133.9 13.6 C 133.9 13.9 133.9 14.0 134.0 14.2 "
            "C 134.3 14.4 134.5 14.3 134.6 14.2 C 137.6 10.7 137.6 10.5 137.7 10.3 "
            "C 137.6 10.1 137.5 10.0 137.3 9.9 C 132.8 9.3 132.7 9.3 132.6 9.3 "
            "C 132.5 9.4 132.5 9.5 132.4 9.6 C 132.4 9.8 132.5 9.9 132.7 10.2 "
            "C 133.0 10.5 133.5 11.1 133.5 11.1 C 133.4 11.2 133.2 11.3 132.9 11.5 "
            "C 132.3 11.9 132.0 12.1 131.2 12.8 C 130.4 13.7 129.7 14.5 129.5 14.8 "
            "C 129.0 15.6 129.0 15.7 129.1 15.7 C 129.4 15.8 129.7 16.0 129.9 16.2 "
            "L 130.0 16.3 L 130.2 16.0 C 130.3 15.8 130.5 15.6 130.6 15.5 Z "
            "M 143.3 7.5 C 143.3 8.1 142.8 8.6 142.2 8.6 C 141.6 8.6 141.1 8.1 141.1 7.5 "
            "C 141.1 6.9 141.6 6.4 142.2 6.4 C 142.8 6.4 143.3 6.9 143.3 7.5 Z "
            "M 142.9 10.2 C 143.8 9.9 144.5 9.2 144.8 8.3 C 144.9 7.9 144.9 7.5 144.9 7.1 "
            "C 144.7 6.2 144.2 5.4 143.3 5.0 C 142.9 4.8 142.6 4.7 142.1 4.7 "
            "C 141.7 4.7 141.4 4.8 140.9 5.0 C 140.4 5.3 140.0 5.7 139.7 6.3 "
            "C 139.5 6.7 139.4 7.0 139.4 7.5 C 139.4 8.0 139.5 8.3 139.7 8.7 "
            "C 140.3 9.9 141.6 10.5 142.9 10.2 Z"
        ),
        icon_viewbox="127 1 22 17",
        body_type="rect",
    ),
    "Deliverable": SymbolDefinition(
        element_type="Deliverable",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#e8e8d0",
        # SVG source: Deliverable_2.svg (w=85.04 h=46.77); scale=0.21, offset=(130,8)
        # Mini wavy-bottom rect (S-curve at bottom like Representation)
        icon_path="M 130 8 L 147.9 8 L 147.9 13.8 C 138.9 9.8 138.9 17.8 130 13.8 Z",
        icon_viewbox="128 6 22 12",
        body_type="rect",
    ),
    "DeliverableComponent": SymbolDefinition(
        element_type="DeliverableComponent",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#e8e8d0",
        body_type="rect",
    ),
    "DistributionNetwork": SymbolDefinition(
        element_type="DistributionNetwork",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path=_ICON_DISTRIBUTION_NETWORK,
        icon_viewbox="128 5 20 10",
        body_type="rect",
    ),
    "Group": SymbolDefinition(
        element_type="Group",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#d9d9d9",
        body_type="rect",
    ),
    "Grouping": SymbolDefinition(
        element_type="Grouping",
        # SVG source: Grouping.svg (w=85.04 h=46.77); scale=(150/85.04, 75/46.77)
        # L-shaped outline: tab label area at top-left (75% width) + full body below tab line
        svg_path="M 112.5 20.5 L 112.5 0 L 0 0 L 0 20.5 L 150 20.5 L 150 75 L 0 75 L 0 20.5",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="none",
        # SVG source: Grouping_2.svg; scale=0.212, offset=(130,6) → mini tab-outline icon
        icon_path="M 143.5 8.7 L 143.5 6 L 130 6 L 130 8.7 L 147.9 8.7 L 147.9 15.9 L 130 15.9 L 130 8.7",
        icon_viewbox="128 4 22 14",
        body_type="path",
    ),
    "Location": SymbolDefinition(
        element_type="Location",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        # SVG source: Location_2.svg (w=5.30 h=8.56); scale=1.7, offset=(134,3)
        # Teardrop / map-pin shape
        icon_path=(
            "M 138.5 17.6 C 138.2 15.9 137.6 14.6 136.9 13.3 C 136.4 12.4 135.7 11.5 135.2 10.6 "
            "C 135.0 10.3 134.8 10.0 134.6 9.7 C 134.3 9.1 134.0 8.4 134.0 7.4 "
            "C 134.0 6.5 134.3 5.8 134.7 5.2 C 135.3 4.2 136.4 3.4 137.8 3.2 "
            "C 139.0 3.0 140.1 3.3 140.8 3.7 C 141.5 4.1 142.0 4.6 142.3 5.2 "
            "C 142.7 5.8 143.0 6.5 143.0 7.4 C 143.0 7.9 142.9 8.3 142.8 8.7 "
            "C 142.7 9.1 142.5 9.4 142.4 9.7 C 142.1 10.4 141.7 10.9 141.3 11.5 "
            "C 140.1 13.3 139.0 15.1 138.5 17.6 Z"
        ),
        icon_viewbox="132 1 13 19",
        body_type="rect",
    ),
    "Material": SymbolDefinition(
        element_type="Material",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        # SVG source: Material_2.svg (w=8.63 h=7.60); scale=1.71, offset=(130,4)
        # Hexagon + 3 inner facet lines (crystal/gem icon)
        icon_path=(
            "M 130 10.4 L 133.7 4.1 L 141.2 4 L 144.8 10.4 L 141 16.9 L 133.9 17 Z "
            "M 132.6 11.2 L 135.7 5.8 M 134.4 14.5 L 140.5 14.5 M 139.2 5.8 L 142.2 11.2"
        ),
        icon_viewbox="128 2 18 17",
        body_type="rect",
    ),
    "Meaning": SymbolDefinition(
        element_type="Meaning",
        # SVG source: Meaning_2.svg / Meaning.svg cloud shape scaled to 150×75
        svg_path=(
            "M 19.2 27.4 C 0 14.1 26.9 7.4 42.3 14.1 C 46.2 7.4 69.2 9.6 73.1 14.1 "
            "C 84.6 9.6 119.2 9.6 119.2 14.1 C 142.3 9.6 150 27.4 134.6 31.9 "
            "C 150 31.9 142.6 44.3 134.6 49.7 C 134.6 67.5 103.8 63 88.5 58.6 "
            "C 73.1 63 11.5 67.5 26.9 54.1 C 3.8 54.1 7.7 27.4 19.2 27.4 Z"
        ),
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#ffe8d0",
        body_type="path",
    ),
    "Product": SymbolDefinition(
        element_type="Product",
        # SVG source: Product.svg (w=72.28 h=29.76); scale=(150/72.28, 75/29.76)
        # Outer rect + top-left corner fold: from midpoint top (x=75,y=0) down then left to (0,y=16)
        svg_path="M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z M 75 0 L 75 16 L 0 16",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        body_type="path",
    ),
    "Representation": SymbolDefinition(
        element_type="Representation",
        # SVG source: Representation.svg; y-stretched so wave trough reaches y=75 (full element height).
        # Sides at y=63, S-curve wave: crest≈y=51, trough≈y=75 (touches element bottom).
        # C2_y=107 is an abstract control point beyond bounds — valid bezier usage.
        svg_path="M 0 0 L 150.0 0 L 150.0 63 C 75 19 75 107 0 63 Z M 0 15 L 150 15",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#fffbdb",
        body_type="path",
    ),
    "Resource": SymbolDefinition(
        element_type="Resource",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#f5dbfb",
        # SVG source: Resource_2.svg (w=10.38 h=6.19); scale=1.6, offset=(130,5)
        # USB drive: rounded-rect body + right-side connector tab + 3 vertical pins
        icon_path=(
            "M 130.8 14.8 C 130.6 14.7 130.4 14.5 130.2 14.4 C 130.0 14.1 130.0 13.9 130.0 10.0 "
            "C 130.0 6.0 130.0 5.9 130.2 5.6 C 130.4 5.4 130.7 5.2 130.9 5.2 "
            "C 131.5 5.0 143.5 5.0 144.0 5.2 C 144.7 5.4 144.9 5.8 145.0 7.1 "
            "L 145.0 8.3 L 145.6 8.3 C 146.5 8.3 146.6 8.4 146.6 10.0 "
            "C 146.6 11.6 146.5 11.7 145.6 11.7 L 145.0 11.7 L 145.0 12.7 "
            "C 145.0 13.9 144.8 14.4 144.2 14.7 C 143.8 14.9 143.2 14.9 137.5 14.9 "
            "C 134.0 14.9 131.1 14.8 130.8 14.8 Z "
            "M 145.1 8.3 L 145.0 11.7 "
            "M 133.1 7.4 L 133.1 12.6 M 135.7 7.4 L 135.7 12.6 M 138.4 7.4 L 138.4 12.6"
        ),
        icon_viewbox="128 3 20 14",
        body_type="rect",
    ),
    "TechnologyCollaboration": SymbolDefinition(
        element_type="TechnologyCollaboration",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path=_ICON_COLLABORATION,
        icon_viewbox="129 3 20 15",
        body_type="rect",
    ),
    "TechnologyEvent": SymbolDefinition(
        element_type="TechnologyEvent",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#daf0e0",
        icon_path=_ICON_EVENT,
        icon_viewbox="128 5 22 15",
        body_type="rect",
    ),
    "Value": SymbolDefinition(
        element_type="Value",
        # SVG source: Value_2.svg ellipse scaled to 150×60, centred in 75-unit height
        svg_path=(
            "M 150 37.5 C 150 54.1 116.4 67.5 75 67.5 C 33.6 67.5 0 54.1 0 37.5 "
            "C 0 20.9 33.6 7.5 75 7.5 C 116.4 7.5 150 20.9 150 37.5 Z"
        ),
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#ffe8d0",
        body_type="path",
    ),
    "ValueStream": SymbolDefinition(
        element_type="ValueStream",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#f5dbfb",
        # SVG source: Value_Stream_2.svg (w=15 h=10); scale=1.2, offset=(130,6)
        # Hexagonal arrow (pentagon with indented left side) pointing right
        icon_path="M 130 6 L 142 6 L 148 12 L 142 18 L 130 18 L 136 12 Z",
        icon_viewbox="128 4 22 16",
        body_type="rect",
    ),
    "WorkPackage": SymbolDefinition(
        element_type="WorkPackage",
        svg_path=_RECT_PATH,
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#e8e8d0",
        # SVG source: Work_package_2.svg (w=85.04 h=34.02); scale=0.21, offset=(130,8)
        # Mini rounded-corner rectangle
        icon_path=(
            "M 131.1 8 L 146.7 8 C 147.4 8 147.9 8.5 147.9 9.1 L 147.9 14 "
            "C 147.9 14.6 147.4 15.1 146.7 15.1 L 131.1 15.1 "
            "C 130.5 15.1 130 14.6 130 14 L 130 9.1 C 130 8.5 130.5 8 131.1 8 Z"
        ),
        icon_viewbox="128 6 22 11",
        body_type="rect",
    ),
}


def get_symbol(element_type: str) -> SymbolDefinition | None:
    """Get symbol definition for an element type.

    Args:
        element_type: ArchiMate element type (e.g., "BusinessActor")

    Returns:
        SymbolDefinition if found, None otherwise
    """
    return ARCHIMATE_SYMBOLS.get(element_type)


def get_all_symbols() -> dict[str, SymbolDefinition]:
    """Get all symbol definitions.

    Returns:
        Dictionary of element_type → SymbolDefinition
    """
    return ARCHIMATE_SYMBOLS.copy()


def validate_symbols() -> tuple[int, int]:
    """Validate all symbol definitions.

    Returns:
        Tuple of (valid_count, invalid_count)
    """
    valid = 0
    invalid = 0

    for element_type, symbol in ARCHIMATE_SYMBOLS.items():
        try:
            assert symbol.svg_path and len(symbol.svg_path) > 0
            assert symbol.viewBox.startswith(("0 0", "-"))
            assert len(symbol.bounding_box) == 4
            assert (
                symbol.default_color.startswith("#")
                and len(symbol.default_color) == 7
                or symbol.default_color == "none"
            )
            valid += 1
        except AssertionError:
            print(f"Invalid symbol: {element_type}")
            invalid += 1

    return valid, invalid
