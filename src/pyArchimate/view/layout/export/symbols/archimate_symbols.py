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
    svg_path: str  # SVG path data
    viewBox: str  # ViewBox dimensions
    bounding_box: tuple[float, float, float, float]  # (x, y, width, height)
    default_color: str  # HEX RGB color code


# Symbol Registry: Comprehensive mapping of all ArchiMate element types
ARCHIMATE_SYMBOLS = {
    "ApplicationCollaboration": SymbolDefinition(
        element_type="ApplicationCollaboration",
        svg_path="M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#B3E5FC"
    ),
    "ApplicationComponent": SymbolDefinition(
        element_type="ApplicationComponent",
        svg_path="M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z M 134.25 5 L 144.0 5 L 144.0 20.0 L 134.25 20.0 Z M 131 8.75 L 137.5 8.75 L 137.5 11.0 L 131 11.0 Z M 131 14 L 137.5 14 L 137.5 16.25 L 131 16.25 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#87CEEB"
    ),
    "ApplicationEvent": SymbolDefinition(
        element_type="ApplicationEvent",
        svg_path="M 140.5 8 C 142.99 8 145 10.01 145 12.5 C 145 14.99 142.99 17 140.5 17 L 130 17 L 134.5 12.5 L 130 8 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#81D4FA"
    ),
    "ApplicationFunction": SymbolDefinition(
        element_type="ApplicationFunction",
        svg_path="M 137.5 5 L 145 8 L 145 20 L 137.5 17 L 130 20 L 130 8 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#29B6F6"
    ),
    "ApplicationInteraction": SymbolDefinition(
        element_type="ApplicationInteraction",
        svg_path="M 138.25 5 C 141.98 5 145 8.36 145 12.5 C 145 16.64 141.98 20 138.25 20 Z M 136.75 5 C 133.02 5 130 8.36 130 12.5 C 130 16.64 133.02 20 136.75 20 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#039BE5"
    ),
    "ApplicationInterface": SymbolDefinition(
        element_type="ApplicationInterface",
        svg_path="M 130 12.5 L 137.5 12.5 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#4FC3F7"
    ),
    "ApplicationProcess": SymbolDefinition(
        element_type="ApplicationProcess",
        svg_path="M 130 10.7 L 139 10.7 L 139 8 L 145 12.5 L 139 17 L 139 14.3 L 130 14.3 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#81D4FA"
    ),
    "ApplicationService": SymbolDefinition(
        element_type="ApplicationService",
        svg_path="M 140.5 8 C 142.99 8 145 10.01 145 12.5 C 145 14.99 142.99 17 140.5 17 L 134.5 17 C 132.01 17 130 14.99 130 12.5 C 130 10.01 132.01 8 134.5 8 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#81D4FA"
    ),
    "Artifact": SymbolDefinition(
        element_type="Artifact",
        svg_path="M 132 5 L 139.7 5 L 143 8.3 L 143 20 L 132 20 Z M 139.7 5 L 139.7 8.3 L 143 8.3 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#2E7D32"
    ),
    "Assessment": SymbolDefinition(
        element_type="Assessment",
        svg_path="M 0 10 L 10 0 L 140 0 L 150 10 L 150 65 L 140 75 L 10 75 L 0 65 Z M 130 20 L 134.8 15.2",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FF5252"
    ),
    "BusinessActor": SymbolDefinition(
        element_type="BusinessActor",
        svg_path="M 137.5 9.5 L 137.5 16.25 M 133 11.75 L 142 11.75 M 133 20 L 137.5 16.25 L 142 20 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FFD700"
    ),
    "BusinessCollaboration": SymbolDefinition(
        element_type="BusinessCollaboration",
        svg_path="M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FFE4B5"
    ),
    "BusinessEvent": SymbolDefinition(
        element_type="BusinessEvent",
        svg_path="M 140.5 8 C 142.99 8 145 10.01 145 12.5 C 145 14.99 142.99 17 140.5 17 L 130 17 L 134.5 12.5 L 130 8 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FFD180"
    ),
    "BusinessFunction": SymbolDefinition(
        element_type="BusinessFunction",
        svg_path="M 137.5 5 L 145 8 L 145 20 L 137.5 17 L 130 20 L 130 8 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FFE4B5"
    ),
    "BusinessInteraction": SymbolDefinition(
        element_type="BusinessInteraction",
        svg_path="M 138.25 5 C 141.98 5 145 8.36 145 12.5 C 145 16.64 141.98 20 138.25 20 Z M 136.75 5 C 133.02 5 130 8.36 130 12.5 C 130 16.64 133.02 20 136.75 20 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FFD180"
    ),
    "BusinessInterface": SymbolDefinition(
        element_type="BusinessInterface",
        svg_path="M 130 12.5 L 137.5 12.5 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FFDB58"
    ),
    "BusinessObject": SymbolDefinition(
        element_type="BusinessObject",
        svg_path="M 0 15 L 150 15 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FFAB91"
    ),
    "BusinessProcess": SymbolDefinition(
        element_type="BusinessProcess",
        svg_path="M 130 10.7 L 139 10.7 L 139 8 L 145 12.5 L 139 17 L 139 14.3 L 130 14.3 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FFE4B5"
    ),
    "BusinessRole": SymbolDefinition(
        element_type="BusinessRole",
        svg_path="M 142 9 L 133 9 C 131.34 9 130 10.57 130 12.5 C 130 14.43 131.34 16 133 16 L 142 16 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FFC700"
    ),
    "BusinessService": SymbolDefinition(
        element_type="BusinessService",
        svg_path="M 140.5 8 C 142.99 8 145 10.01 145 12.5 C 145 14.99 142.99 17 140.5 17 L 134.5 17 C 132.01 17 130 14.99 130 12.5 C 130 10.01 132.01 8 134.5 8 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FFDB58"
    ),
    "CommunicationNetwork": SymbolDefinition(
        element_type="CommunicationNetwork",
        svg_path="M 136 9.2 L 142.75 9.2 L 139 15.8 L 132.25 15.8 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#388E3C"
    ),
    "Constraint": SymbolDefinition(
        element_type="Constraint",
        svg_path="M 0 10 L 10 0 L 140 0 L 150 10 L 150 65 L 140 75 L 10 75 L 0 65 Z M 133.75 9 L 145 9 L 141.25 16 L 130 16 Z M 136.75 9 L 133 16",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#AD1457"
    ),
    "DataObject": SymbolDefinition(
        element_type="DataObject",
        svg_path="M 0 15 L 150 15 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#0288D1"
    ),
    "Device": SymbolDefinition(
        element_type="Device",
        svg_path="M 0 10 L 10 0 L 150 0 L 150 65 L 140 75 L 0 75 Z M 0 10 L 140 10 L 140 75 M 150 0 L 140 10 M 121.5 28.2 L 120 30 L 135 30 L 133.5 28.2 M 120 15 L 135.0 15 L 135.0 28.2 L 120 28.2 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#7CFC00"
    ),
    "Driver": SymbolDefinition(
        element_type="Driver",
        svg_path="M 0 10 L 10 0 L 140 0 L 150 10 L 150 65 L 140 75 L 10 75 L 0 65 Z M 130 12.5 L 145 12.5 M 137.5 5 L 137.5 20 M 132.18 7.17 L 142.82 17.82 M 132.18 17.82 L 142.82 7.17",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FF7043"
    ),
    "Equipment": SymbolDefinition(
        element_type="Equipment",
        svg_path="M 0 10 L 10 0 L 150 0 L 150 65 L 140 75 L 0 75 Z M 0 10 L 140 10 L 140 75 M 150 0 L 140 10 M 130.8 20.7 C 131.7 20.7 132.75 20.1 132.75 18.9 C 132.75 17.7 131.7 17.1 130.95 17.1 C 129.6 17.1 128.85 18 128.85 18.9 C 128.85 19.95 129.75 20.7 130.8 20.7 Z M 130.2 22.8 L 130.05 21.75 L 129.15 21.45 L 128.4 22.2 L 127.5 21.3 L 128.1 20.4 L 127.8 19.65 L 126.75 19.65 L 126.75 18.3 L 127.8 18.15 L 128.1 17.4 L 127.5 16.65 L 128.4 15.75 L 129.3 16.35 L 130.05 16.05 L 130.2 15 L 131.55 15 L 131.7 16.05 L 132.45 16.35 L 133.35 15.75 L 134.25 16.65 L 133.65 17.4 L 133.95 18.15 L 135 18.3 L 135 19.65 L 133.95 19.65 L 133.65 20.4 L 134.25 21.15 L 133.35 22.05 L 132.45 21.45 L 131.7 21.75 L 131.55 22.8 L 130.2 22.8 Z M 125.4 27.15 C 126.6 27.15 127.8 26.25 127.8 25.05 C 127.8 23.85 126.75 22.65 125.25 22.65 C 124.05 22.65 122.85 23.7 122.85 25.05 C 122.85 26.1 124.05 27.3 125.4 27.15 Z M 123.15 29.7 L 123.3 28.35 L 122.4 27.75 L 121.2 28.2 L 120.3 26.85 L 121.35 26.1 L 121.2 25.05 L 120 24.45 L 120.45 22.95 L 121.8 23.1 L 122.4 22.2 L 121.95 21 L 123.3 20.25 L 124.2 21.3 L 125.4 21.15 L 125.85 19.95 L 127.5 20.4 L 127.35 21.75 L 128.25 22.35 L 129.45 21.75 L 130.35 23.1 L 129.3 24 L 129.45 25.05 L 130.65 25.5 L 130.2 27 L 128.85 26.85 L 128.25 27.75 L 128.85 26.85 L 128.25 27.75 L 128.85 28.95 L 127.35 29.7 L 126.45 28.65 L 125.4 28.8 L 124.8 30 L 123.15 29.7 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#1B5E20"
    ),
    "Facility": SymbolDefinition(
        element_type="Facility",
        svg_path="M 0 10 L 10 0 L 150 0 L 150 65 L 140 75 L 0 75 Z M 0 10 L 140 10 L 140 75 M 150 0 L 140 10 M 120 30 L 120 15 L 121.95 15 L 121.95 25.5 L 126.3 23.25 L 126.3 25.5 L 130.65 23.25 L 130.65 25.5 L 135 23.25 L 135 30 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#76FF03"
    ),
    "Gap": SymbolDefinition(
        element_type="Gap",
        svg_path="M 0 0 L 150 0 L 150 51 C 140.13 46.97 126.61 44.7 112.5 44.7 C 98.39 44.7 84.87 46.97 75 51 C 65.13 55.03 51.61 57.3 37.5 57.3 C 23.39 57.3 9.87 55.03 0 51 Z M 130 10.85 L 145 10.85 M 130 14.15 L 145 14.15",
        viewBox="-0.5 -0.5 151 61",
        bounding_box=(-0.5, -0.5, 151.0, 61.0),
        default_color="#424242"
    ),
    "Goal": SymbolDefinition(
        element_type="Goal",
        svg_path="M 0 10 L 10 0 L 140 0 L 150 10 L 150 65 L 140 75 L 10 75 L 0 65 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#FF1744"
    ),
    "ImplementationEvent": SymbolDefinition(
        element_type="ImplementationEvent",
        svg_path="M 140.5 8 C 142.99 8 145 10.01 145 12.5 C 145 14.99 142.99 17 140.5 17 L 130 17 L 134.5 12.5 L 130 8 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#7B1FA2"
    ),
    "Node": SymbolDefinition(
        element_type="Node",
        svg_path="M 130 8.75 L 133.75 5 L 145 5 L 145 16.25 L 141.25 20 L 130 20 Z M 130 8.75 L 141.25 8.75 L 141.25 20 M 145 5 L 141.25 8.75 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#90EE90"
    ),
    "Outcome": SymbolDefinition(
        element_type="Outcome",
        svg_path="M 0 10 L 10 0 L 140 0 L 150 10 L 150 65 L 140 75 L 10 75 L 0 65 Z M 136 14 L 143.5 6.5 M 136.3 11 L 136 14 L 139 13.7 M 142 5 L 141.25 8.75 L 145 8",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#D32F2F"
    ),
    "Path": SymbolDefinition(
        element_type="Path",
        svg_path="M 133 15 L 130 12.5 L 133 10 M 142 15 L 145 12.5 L 142 10 M 130 12.5 L 145 12.5 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#45A049"
    ),
    "Plateau": SymbolDefinition(
        element_type="Plateau",
        svg_path="M 0 10 L 10 0 L 150 0 L 150 65 L 140 75 L 0 75 Z M 0 10 L 140 10 L 140 75 M 150 0 L 140 10 M 126 15 L 135.0 15 L 135.0 18.0 L 126 18.0 Z M 123 21 L 132.0 21 L 132.0 24.0 L 123 24.0 Z M 120 27 L 129.0 27 L 129.0 30.0 L 120 30.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#6A1B9A"
    ),
    "Principle": SymbolDefinition(
        element_type="Principle",
        svg_path="M 0 10 L 10 0 L 140 0 L 150 10 L 150 65 L 140 75 L 10 75 L 0 65 Z M 130.75 5.75 C 135.21 4.86 139.79 4.86 144.25 5.75 C 145.14 10.21 145.14 14.79 144.25 19.25 C 139.79 20.14 135.21 20.14 130.75 19.25 C 129.86 14.79 129.86 10.21 130.75 5.75 Z M 136.75 15.5 L 136.3 7.25 L 138.7 7.25 L 138.25 15.5 Z M 136.75 16.25 L 138.25 16.25 L 138.25 17.75 L 136.75 17.75 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#C62828"
    ),
    "Requirement": SymbolDefinition(
        element_type="Requirement",
        svg_path="M 0 10 L 10 0 L 140 0 L 150 10 L 150 65 L 140 75 L 10 75 L 0 65 Z M 133.75 9 L 145 9 L 141.25 16 L 130 16 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#B71C1C"
    ),
    "Stakeholder": SymbolDefinition(
        element_type="Stakeholder",
        svg_path="M 0 10 L 10 0 L 140 0 L 150 10 L 150 65 L 140 75 L 10 75 L 0 65 Z M 142 9 L 133 9 C 131.34 9 130 10.57 130 12.5 C 130 14.43 131.34 16 133 16 L 142 16",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#E64A19"
    ),
    "SystemSoftware": SymbolDefinition(
        element_type="SystemSoftware",
        svg_path="M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#76FF03"
    ),
    "TechnologyFunction": SymbolDefinition(
        element_type="TechnologyFunction",
        svg_path="M 137.5 5 L 145 8 L 145 20 L 137.5 17 L 130 20 L 130 8 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#66BB6A"
    ),
    "TechnologyInteraction": SymbolDefinition(
        element_type="TechnologyInteraction",
        svg_path="M 138.25 5 C 141.98 5 145 8.36 145 12.5 C 145 16.64 141.98 20 138.25 20 Z M 136.75 5 C 133.02 5 130 8.36 130 12.5 C 130 16.64 133.02 20 136.75 20 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#039BE5"
    ),
    "TechnologyInterface": SymbolDefinition(
        element_type="TechnologyInterface",
        svg_path="M 130 12.5 L 137.5 12.5 M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#4CAF50"
    ),
    "TechnologyProcess": SymbolDefinition(
        element_type="TechnologyProcess",
        svg_path="M 130 10.7 L 139 10.7 L 139 8 L 145 12.5 L 139 17 L 139 14.3 L 130 14.3 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#66BB6A"
    ),
    "TechnologyService": SymbolDefinition(
        element_type="TechnologyService",
        svg_path="M 140.5 8 C 142.99 8 145 10.01 145 12.5 C 145 14.99 142.99 17 140.5 17 L 134.5 17 C 132.01 17 130 14.99 130 12.5 C 130 10.01 132.01 8 134.5 8 Z M 0 0 L 150.0 0 L 150.0 75.0 L 0 75.0 Z",
        viewBox="-0.5 -0.5 151 76",
        bounding_box=(-0.5, -0.5, 151.0, 76.0),
        default_color="#66BB6A"
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
            assert symbol.viewBox.startswith("0 0") or symbol.viewBox.startswith("-")
            assert len(symbol.bounding_box) == 4
            assert symbol.default_color.startswith("#") and len(symbol.default_color) == 7
            valid += 1
        except AssertionError:
            print(f"Invalid symbol: {element_type}")
            invalid += 1

    return valid, invalid
