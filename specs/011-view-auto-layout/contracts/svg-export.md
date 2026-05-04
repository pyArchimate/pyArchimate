# Contract: SVG Export API

**Version**: 1.0  
**Date**: 2026-05-04  
**Feature**: User Story 5 — Export View as SVG Diagram

## Overview

The SVG export contract defines the interface and expected behavior for exporting pyArchimate views as self-contained SVG images. This document is the authoritative specification for how `View.to_svg()` should behave.

---

## API Signature

```python
def to_svg(self, filepath: Optional[str] = None) -> str:
    """Export view to SVG string and optionally write to file.
    
    Args:
        filepath (Optional[str]): Path to write SVG file. If provided, SVG is 
                                  written to this path in addition to being returned.
        
    Returns:
        str: Valid SVG 1.1 XML string with <svg> root element.
        
    Raises:
        IOError: If filepath is provided but file cannot be written.
    """
```

---

## Functional Requirements

### FR-012: Method Signature and Behavior

- **Method**: `View.to_svg(filepath=None) -> str`
- **Returns**: Valid SVG 1.1 XML string with `<?xml version="1.0" encoding="UTF-8"?>` declaration
- **Side effect**: If `filepath` is provided, writes SVG to file with UTF-8 encoding
- **Idempotent**: Multiple calls with same view produce identical SVG output
- **No state mutation**: View object is not modified by SVG export

### FR-013: Node Rendering

Each node in the view renders as:
- **Element**: `<rect>` with attributes:
  - `x`: Integer pixel position (exact node.x)
  - `y`: Integer pixel position (exact node.y)
  - `width`: Integer pixels (exact node.w)
  - `height`: Integer pixels (exact node.h)
  - `fill`: "white" (required for background visibility)
  - `stroke`: "black" (required for definition)
  - `stroke-width`: "1" (1 pixel border)

- **Label**: `<text>` element containing node name/label:
  - Position: Centered at `(x + w/2, y + h/2)`
  - Font: Arial, sans-serif (with fallback chain)
  - Font size: 10px
  - Color: black (`fill="black"`)
  - Text anchor: middle (`text-anchor="middle"`)
  - Word-wrapped to fit within rectangle width
  - Vertically centered within rectangle height

**Example**:
```xml
<g class="node">
  <rect x="50" y="100" width="120" height="55" fill="white" stroke="black" stroke-width="1"/>
  <text x="110" y="125" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="black">
    <tspan x="110">Application</tspan>
    <tspan x="110" dy="12">Component</tspan>
  </text>
</g>
```

### FR-014: Connection Rendering

Each connection renders as:
- **Element**: `<polyline>` with attributes:
  - `points`: Space-separated x,y pairs representing polyline path
  - `fill`: "none" (polylines don't fill)
  - `stroke`: "black" (connection line)
  - `stroke-width`: "1"
  - `marker-end`: "url(#arrowhead)" (arrowhead at target end)

- **Arrowhead**: Defined in `<defs>` block as `<marker>` with ID "arrowhead":
  - Type: Filled triangle polygon
  - Size: 8x8 pixels
  - Color: black (`fill="black"`)
  - Orient: auto (rotates to match line direction)

- **Polyline Points**:
  - Start: Clipped at source node boundary edge (nearest edge intersection)
  - Middle: Bendpoints from `connection.bendpoints` (if any)
  - End: Clipped at target node boundary edge (nearest edge intersection)

**Coordinate Clipping**:
- Line from source center to first bendpoint (or target if no bendpoints) is clipped at source rectangle edge
- Line from last bendpoint (or source if no bendpoints) to target center is clipped at target rectangle edge
- Intermediate bendpoints are used as-is (no clipping)

**Example**:
```xml
<defs>
  <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
    <polygon points="0 0, 8 4, 0 8" fill="black"/>
  </marker>
</defs>
...
<polyline points="110,125 110,200 200,200 200,275" fill="none" stroke="black" stroke-width="1" marker-end="url(#arrowhead)"/>
```

### FR-015: Connection Labels

Each connection with a relationship type renders a label:
- **Element**: `<g class="connection-label">` containing:
  - `<rect>`: White background (no border)
    - Width: Approximately `len(label_text) * 6` pixels
    - Height: 12 pixels
    - `fill="white"`, `stroke="none"`
  - `<text>`: Label text
    - Content: Short relationship type name (trailing "Relationship" stripped)
    - Position: Centered on the longest segment of the polyline
    - Font: Arial, sans-serif; 9px
    - Color: black (`fill="black"`)
    - Text anchor: middle

**Label Text Generation**:
- Example: "ServingRelationship" → "Serving"
- Example: "RealizationRelationship" → "Realization"
- Example: "Association" → "Association" (no "Relationship" suffix, unchanged)

**Placement Algorithm**:
1. Find longest polyline segment (by Euclidean distance)
2. Compute midpoint: `((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)`
3. Position label at midpoint with white background

**Example**:
```xml
<g class="connection-label">
  <rect x="145" y="193" width="48" height="12" fill="white" stroke="none"/>
  <text x="169" y="204" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="black">Serving</text>
</g>
```

### FR-016: Background and Canvas

- **Background rectangle**: White rectangle covering entire SVG canvas
  - Position: (0, 0)
  - Size: Full SVG viewBox width and height
  - Attributes: `fill="white"`, `stroke="none"`
  - Order: Rendered first (appears behind all content)

- **ViewBox and Dimensions**:
  - Calculated from bounding box of all nodes plus margin (default 20px)
  - Format: `viewBox="0 0 {width} {height}"`
  - Width attribute: Integer pixels
  - Height attribute: Integer pixels

**Example**:
```xml
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="640" height="480" viewBox="0 0 640 480">
  <rect x="0" y="0" width="640" height="480" fill="white" stroke="none"/>
  <!-- nodes and connections follow -->
</svg>
```

---

## Data Structures

### View Object

```python
class View:
    nodes: List[Node]           # Visual nodes (elements)
    conns: List[Connection]     # Visual connections (relationships)
    nodes_dict: Dict[str, Node] # UUID → Node mapping
```

### Node Object

```python
class Node:
    uuid: str          # Unique identifier
    x: float           # Canvas X position (pixels)
    y: float           # Canvas Y position (pixels)
    w: float           # Width (pixels)
    h: float           # Height (pixels)
    name: str          # Display name (from element or label)
    label: str         # Alternative label (if name not available)
```

### Connection Object

```python
class Connection:
    uuid: str                          # Unique identifier
    _source: str                       # Source node UUID
    _target: str                       # Target node UUID
    type: str                          # Relationship type (e.g., "ServingRelationship")
    bendpoints: List[Point]            # Intermediate points for polyline routing
```

### Point Object

```python
class Point:
    x: float           # X coordinate (pixels)
    y: float           # Y coordinate (pixels)
```

---

## Edge Cases and Error Handling

### Empty View

- **View with no nodes and no connections**
  - Output: Valid SVG with default 100×100 viewBox
  - Content: White background rectangle only
  - No error raised

### Single Node

- **View with one node, no connections**
  - Output: SVG with single rectangle and text
  - No connections rendered

### Missing Source or Target

- **Connection with missing source or target node UUID**
  - Behavior: Connection skipped silently (no error)
  - Logging: Debug-level log entry (not in output)
  - Impact: No polyline rendered for this connection

### Text Overflow

- **Element name longer than node rectangle width**
  - Behavior: Text wrapped to multiple lines
  - Algorithm: Word-wrap on space characters; ~6 pixels per character
  - Vertical centering: Total text height centered in rectangle

### Very Long Labels

- **Connection label longer than available space**
  - Behavior: Label rendered with estimated width; may overlap if very long
  - Future enhancement: Dynamic repositioning to avoid overlaps

---

## Performance Constraints

- **Max elements**: 500 nodes + 500 connections
- **Expected time**: <200ms on standard hardware (2022 MacBook Pro)
- **Memory**: Proportional to element count; no unnecessary buffering

---

## Validation and Testing

### SVG Validity

- Generated SVG must be valid SVG 1.1 XML
- Must parse successfully in `xml.etree.ElementTree`
- Must render without errors in Firefox, Chrome, Safari, Edge

### Round-Trip Testing

```python
from pyArchimate.view import load_view

# Load view
view = load_view("model.archimate")

# Export SVG
svg_string = view.to_svg()

# Validate structure
import xml.etree.ElementTree as ET
root = ET.fromstring(svg_string)
assert root.tag == '{http://www.w3.org/2000/svg}svg'
assert root.find('{http://www.w3.org/2000/svg}rect') is not None  # Background
```

### Acceptance Scenarios

From `spec.md`, User Story 5:

1. ✓ Given a view with positioned nodes, when `to_svg()` is called, then the SVG contains one white rectangle with black border for each node at correct x/y/w/h
2. ✓ Given a view with connections carrying bendpoints, when `to_svg()` is called, then each connection renders as an orthogonal polyline clipped at node boundaries with a filled-triangle arrowhead
3. ✓ Given a view with connections, when `to_svg()` is called, then each connection has a label showing the short relationship type name on the longest segment
4. ✓ Given `to_svg(filepath="out.svg")` is called, then the SVG is written to the specified file
5. ✓ Given an element name exceeding node width, when `to_svg()` is called, then the name wraps and is vertically centered
6. ✓ Given a view with positioned nodes and connections, when `to_svg()` is called, then the SVG contains a white background rectangle covering the entire canvas

---

## Implementation Notes

- **Location**: `src/pyArchimate/view/layout/export/svg_export.py`
- **Service class**: `SVGExportService`
- **View integration**: `View.to_svg()` delegates to `SVGExportService.to_svg()`
- **Dependencies**: `xml.etree.ElementTree` (stdlib), `math` (stdlib)
- **No external SVG libraries**: Pure lxml/ElementTree implementation

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-04 | Initial contract specification |
