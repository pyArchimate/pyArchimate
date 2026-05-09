#!/usr/bin/env python3
"""Extract ArchiMate symbols from marcelomg/archimate-symbols repository.

This script fetches official ArchiMate symbol SVGs from:
https://github.com/marcelomg/archimate-symbols

And generates symbol definitions with proper paths and colors.
"""

import ssl
from urllib.parse import quote
from urllib.request import urlopen
from xml.etree import ElementTree as ET

# Mapping of repository file names to element type names
SYMBOL_MAPPING = {
    "Business Actor": "BusinessActor",
    "Business Collaboration": "BusinessCollaboration",
    "Business Event": "BusinessEvent",
    "Business Function": "BusinessFunction",
    "Business Interaction": "BusinessInteraction",
    "Business Interface": "BusinessInterface",
    "Business Object": "BusinessObject",
    "Business Process": "BusinessProcess",
    "Business Role": "BusinessRole",
    "Business Service": "BusinessService",
    "Application Collaboration": "ApplicationCollaboration",
    "Application Component": "ApplicationComponent",
    "Application Event": "ApplicationEvent",
    "Application Function": "ApplicationFunction",
    "Application Interaction": "ApplicationInteraction",
    "Application Interface": "ApplicationInterface",
    "Application Process": "ApplicationProcess",
    "Application Service": "ApplicationService",
    "Data Object": "DataObject",
    "Artifact": "Artifact",
    "Communication Network": "CommunicationNetwork",
    "Device": "Device",
    "Equipment": "Equipment",
    "Facility": "Facility",
    "Infrastructure Function": "InfrastructureFunction",
    "Infrastructure Interface": "InfrastructureInterface",
    "Infrastructure Service": "InfrastructureService",
    "Node": "Node",
    "Path": "Path",
    "System Software": "SystemSoftware",
    "Technology Function": "TechnologyFunction",
    "Technology Interaction": "TechnologyInteraction",
    "Technology Interface": "TechnologyInterface",
    "Technology Object": "TechnologyObject",
    "Technology Process": "TechnologyProcess",
    "Technology Service": "TechnologyService",
    "Assessment": "Assessment",
    "Constraint": "Constraint",
    "Driver": "Driver",
    "Goal": "Goal",
    "Outcome": "Outcome",
    "Principle": "Principle",
    "Requirement": "Requirement",
    "Stakeholder": "Stakeholder",
    "And Junction": "AndJunction",
    "Or Junction": "OrJunction",
    "Xor Junction": "XorJunction",
    "Deliverable Component": "DeliverableComponent",
    "Implementation Component": "ImplementationComponent",
    "Implementation Event": "ImplementationEvent",
    "Plateau": "Plateau",
    "Gap": "Gap",
    "Grouping": "Grouping",
}

# Standard ArchiMate colors from the specification
ARCHIMATE_COLORS = {
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
    "ApplicationCollaboration": "#B3E5FC",
    "ApplicationComponent": "#87CEEB",
    "ApplicationEvent": "#81D4FA",
    "ApplicationFunction": "#29B6F6",
    "ApplicationInteraction": "#039BE5",
    "ApplicationInterface": "#4FC3F7",
    "ApplicationProcess": "#81D4FA",
    "ApplicationService": "#81D4FA",
    "DataObject": "#0288D1",
    "Artifact": "#2E7D32",
    "CommunicationNetwork": "#388E3C",
    "Device": "#7CFC00",
    "Equipment": "#1B5E20",
    "Facility": "#76FF03",
    "InfrastructureFunction": "#66BB6A",
    "InfrastructureInterface": "#4CAF50",
    "InfrastructureService": "#66BB6A",
    "Node": "#90EE90",
    "Path": "#45A049",
    "SystemSoftware": "#76FF03",
    "TechnologyFunction": "#66BB6A",
    "TechnologyInteraction": "#039BE5",
    "TechnologyInterface": "#4CAF50",
    "TechnologyObject": "#388E3C",
    "TechnologyProcess": "#66BB6A",
    "TechnologyService": "#66BB6A",
    "Assessment": "#FF5252",
    "Constraint": "#AD1457",
    "Driver": "#FF7043",
    "Goal": "#FF1744",
    "Outcome": "#D32F2F",
    "Principle": "#C62828",
    "Requirement": "#B71C1C",
    "Stakeholder": "#E64A19",
    "AndJunction": "#455A64",
    "OrJunction": "#546E7A",
    "XorJunction": "#607D8B",
    "DeliverableComponent": "#8E24AA",
    "ImplementationComponent": "#9C27B0",
    "ImplementationEvent": "#7B1FA2",
    "Plateau": "#6A1B9A",
    "Gap": "#424242",
    "Grouping": "#616161",
}


def fetch_symbol(filename: str) -> dict:
    """Fetch a symbol SVG from the repository.

    Args:
        filename: File name from the repository (e.g., "Business Actor.svg")

    Returns:
        Dictionary with svg_path, viewBox, bounding_box, and color
    """
    # URL encode the filename to handle spaces
    encoded_filename = quote(filename)
    url = f"https://raw.githubusercontent.com/marcelomg/archimate-symbols/master/{encoded_filename}"

    try:
        # Handle SSL certificate verification
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        with urlopen(url, context=ssl_context, timeout=5) as response:
            svg_content = response.read().decode('utf-8')

        # Parse SVG
        root = ET.fromstring(svg_content)  # noqa: S314  # dev-only script, fetches from known upstream source

        # Extract viewBox
        viewBox = root.get('viewBox', '0 0 100 100')

        # Extract fill color from first rectangle or ellipse
        color = "#FFD700"  # Default
        for elem in root.iter():
            fill = elem.get('fill')
            if fill and fill.startswith('#'):
                color = fill.upper()
                break

        # Extract all path data
        paths = []
        for path_elem in root.findall('.//{http://www.w3.org/2000/svg}path'):
            d = path_elem.get('d')
            if d:
                paths.append(d)

        # Also extract rect, circle, ellipse as basic shapes
        for rect in root.findall('.//{http://www.w3.org/2000/svg}rect'):
            x = rect.get('x', '0')
            y = rect.get('y', '0')
            width = rect.get('width', '100')
            height = rect.get('height', '100')
            paths.append(f"M {x} {y} L {float(x) + float(width)} {y} L {float(x) + float(width)} {float(y) + float(height)} L {x} {float(y) + float(height)} Z")

        # Combine all paths
        combined_path = " ".join(paths) if paths else f"M 0 0 L 100 0 L 100 100 L 0 100 Z"

        # Calculate bounding box (simplified: use viewBox bounds)
        vb_parts = viewBox.split()
        bbox = (float(vb_parts[0]), float(vb_parts[1]), float(vb_parts[2]), float(vb_parts[3]))

        return {
            "svg_path": combined_path,
            "viewBox": viewBox,
            "bounding_box": bbox,
            "color": color,
        }
    except Exception as e:
        print(f"Error fetching {filename}: {e}")
        return None


def main() -> dict:
    """Main script to extract all symbols and generate Python definitions."""
    print("Fetching ArchiMate symbols from marcelomg/archimate-symbols...")

    symbols = {}

    for filename, element_type in SYMBOL_MAPPING.items():
        print(f"  Fetching {element_type}...", end=" ")
        symbol_data = fetch_symbol(f"{filename}.svg")

        if symbol_data:
            symbol_data["color"] = ARCHIMATE_COLORS.get(element_type, "#FFD700")
            symbols[element_type] = symbol_data
            print("✓")
        else:
            print("✗")

    # Generate Python code
    print("\nGenerating archimate_symbols.py...")

    code = '''"""ArchiMate symbol registry with SVG path definitions for all element types.

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
'''

    for element_type in sorted(symbols.keys()):
        symbol = symbols[element_type]
        svg_path = symbol["svg_path"].replace('"', '\\"')
        viewBox = symbol["viewBox"]
        bbox = symbol["bounding_box"]
        color = symbol["color"]

        code += f'''    "{element_type}": SymbolDefinition(
        element_type="{element_type}",
        svg_path="{svg_path}",
        viewBox="{viewBox}",
        bounding_box={bbox},
        default_color="{color}"
    ),
'''

    code += '''}


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
'''

    # Write to file
    output_path = "src/pyArchimate/view/layout/export/symbols/archimate_symbols.py"
    with open(output_path, 'w') as f:
        f.write(code)

    print(f"✓ Generated {output_path}")
    print(f"  Total symbols: {len(symbols)}")

    return symbols


if __name__ == "__main__":
    main()