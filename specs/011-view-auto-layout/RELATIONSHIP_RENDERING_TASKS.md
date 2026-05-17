# User Story 5.1 - SVG Relationship Rendering Enhancement

**Priority**: P2  
**Parent Feature**: User Story 5 (Export View as SVG Diagram)  
**Status**: Specification  
**Date**: 2026-05-04

## Overview

Extend SVG export to render ArchiMate relationship types with their official symbols and styling, similar to element rendering. This enhancement makes exported SVG diagrams visually complete and compliant with ArchiMate notation standards.

## User Goals

As a developer using pyArchimate, I want to export views with ArchiMate relationship symbols and styling so that my exported SVG diagrams match the official ArchiMate visual notation and are immediately recognizable.

## Functional Requirements

### FR-019: Relationship Symbol Definitions

- **Relationship types to support**:
  - Structural: Association, Realization, Aggregation, Composition
  - Dependency: Access, Serving, Implementation, Assignment, Used By
  - Other: Influence, Triggering, Flow

- **Symbol representation**: Each relationship type has:
  - Line style (solid, dashed, dotted)
  - Arrow type (filled, hollow, double)
  - Color code (per ArchiMate standard)
  - Optional decorations (circles, diamonds, etc.)

- **Location**: `src/pyArchimate/view/layout/export/symbols/archimate_relationships.py`

### FR-020: Relationship Styling Service

- **Service**: `RelationshipStyleService` in `svg_export.py`
- **Capabilities**:
  - Lookup relationship style by ArchiMate type
  - Generate SVG path/attributes for relationship rendering
  - Support per-relationship color override
  - Validate relationship styles

### FR-021: SVG Relationship Rendering

Update `SVGExportService` to render relationships:

- **Method**: `_render_relationship()` in `svg_export.py`
  - Input: Connection object with type and bendpoints
  - Output: SVG `<polyline>` with appropriate style attributes
  - Attributes:
    - `stroke`: Color per relationship type
    - `stroke-width`: 1-2px
    - `stroke-dasharray`: Pattern for dashed/dotted (if applicable)
    - `marker-start`, `marker-end`: Arrow markers for relationship type
    - `opacity`: 0.8 (slightly transparent for visual hierarchy)

- **Marker definitions**: Extend `<defs>` to include ArchiMate relationship markers:
  - Filled arrow (standard)
  - Hollow arrow (realization)
  - Double arrow (bidirectional)
  - Circle/diamond endpoints (aggregation, composition)

- **Relationship label styling**:
  - Font: Arial, 9px (same as element names)
  - Background: White box (existing)
  - Color: Black (same as element labels)
  - Position: Longest segment midpoint (existing)

### FR-022: Per-Relationship Customization

- **Override properties** on Connection object:
  - `stroke_color`: Override relationship color
  - `stroke_style`: Override line pattern (solid, dashed, dotted)
  - `stroke_width`: Override line thickness

- **Fallback**: If not set, use standard ArchiMate style

### FR-023: Relationship Rendering Order

- **Layering**:
  1. Background rectangle
  2. Relationships (connections) — rendered first so visible beneath elements
  3. Elements (nodes) — rendered on top
  4. Relationship labels — rendered on top of everything

## Acceptance Scenarios

1. **Given** a view with Realization relationships, **When** exported to SVG, **Then** relationships render with hollow arrows and dashed lines
2. **Given** a view with Serving relationships, **When** exported to SVG, **Then** relationships render with filled arrows and solid lines
3. **Given** a view with mixed relationship types, **When** exported to SVG, **Then** each type is rendered with its distinct visual style
4. **Given** a relationship with a color override, **When** exported to SVG, **Then** the override color is used instead of standard
5. **Given** a view with overlapping relationships, **When** exported to SVG, **Then** relationships are visible and not obscured by elements
6. **Given** an SVG with relationships, **When** opened in a browser, **Then** all relationship lines and arrows are clearly visible

## Tasks

### Phase 6C: US5.1 SVG Relationship Rendering (8 tasks)

#### T119: Create Relationship Symbol Definitions

- **Task**: Define ArchiMate relationship styles in `src/pyArchimate/view/layout/export/symbols/archimate_relationships.py`
- **Description**:
  - Create `RelationshipStyle` NamedTuple with: type, stroke_color, stroke_width, stroke_dasharray, marker_start, marker_end, arrow_type
  - Map 12+ ArchiMate relationship types to styles:
    - Structural: Association (solid, filled arrow), Realization (dashed, hollow arrow), Aggregation (solid, hollow diamond), Composition (solid, filled diamond)
    - Dependency: Access (dotted, filled arrow), Serving (solid, filled arrow), Implementation (dashed, hollow arrow), Assignment (dashed, filled arrow), Used By (dotted, filled arrow)
    - Other: Influence (dotted, filled arrow), Triggering (solid, filled arrow), Flow (solid, filled arrow)
  - Include standard ArchiMate colors per relationship category

#### T120: Create Relationship Styling Service

- **Task**: Implement `RelationshipStyleService` class in `svg_export.py`
- **Methods**:
  - `get_style(relationship_type: str) -> RelationshipStyle` - lookup by type
  - `get_all_styles() -> dict[str, RelationshipStyle]` - return all definitions
  - `validate_styles() -> tuple[int, int]` - validate all definitions
  - `apply_overrides(style, overrides) -> RelationshipStyle` - apply per-relationship customization

#### T121: Extend SVG Defs with Relationship Markers

- **Task**: Update `_add_defs()` method in `SVGExportService` to add relationship markers
- **Description**:
  - Add marker definitions for:
    - Standard filled arrow (id="arrow-filled")
    - Hollow arrow (id="arrow-hollow")
    - Double arrow (id="arrow-double")
    - Diamond fill (id="diamond-filled")
    - Diamond hollow (id="diamond-hollow")
  - Each marker: 8x8px, ref coordinates at center, orient="auto"

#### T122: Implement Relationship Rendering Method

- **Task**: Add `_render_relationship()` method to `SVGExportService`
- **Description**:
  - Input: Connection object, relationship style
  - Output: SVG `<polyline>` with style attributes
  - Apply stroke color, stroke-width, stroke-dasharray
  - Apply marker-end based on relationship type
  - Support opacity=0.8 for visual hierarchy
  - Use existing polyline clipping logic

#### T123: Update Rendering Order

- **Task**: Modify `to_svg()` method rendering loop in `SVGExportService`
- **Description**:
  - Change order to:
    1. Add background rectangle
    2. Render connections/relationships (existing loop)
    3. Render nodes/elements (existing loop)
    4. Relationship labels (existing in connection rendering)
  - Verify no visual conflicts or overlaps

#### T124: Implement Per-Relationship Customization

- **Task**: Support `stroke_color`, `stroke_style`, `stroke_width` properties on Connection objects
- **Description**:
  - Check for override properties in Connection object
  - In `_render_relationship()`, apply overrides to base style
  - Fall back to standard style if not specified
  - Validate override colors are valid HEX codes

#### T125: Create Unit Tests for Relationship Styles

- **Task**: Create `tests/unit/layout/test_archimate_relationships.py`
- **Test coverage**:
  - All 12+ relationship types have defined styles
  - Style definitions have valid attributes (colors, dash patterns, markers)
  - RelationshipStyleService lookup works correctly
  - Override application works correctly
  - Validation catches invalid styles
  - At least 15 unit tests total

#### T126: Expand SVG Relationship BDD Scenarios

- **Task**: Expand `tests/features/layout/svg_export.feature` with relationship rendering scenarios
- **Description**:
  - Scenario: Export view with Realization relationships (dashed, hollow arrows)
  - Scenario: Export view with Serving relationships (solid, filled arrows)
  - Scenario: Export view with mixed relationship types (each renders correctly)
  - Scenario: Export relationship with color override (override applied)
  - Scenario: Export view with overlapping relationships (all visible)
  - At least 5 new BDD scenarios

## Technical Implementation Notes

### Relationship Style Architecture

```python
from typing import NamedTuple, Optional

class RelationshipStyle(NamedTuple):
    """SVG style for ArchiMate relationship type."""
    relationship_type: str      # e.g., "ServingRelationship"
    stroke_color: str           # HEX color code
    stroke_width: float         # Pixels (1.0, 1.5, 2.0)
    stroke_dasharray: Optional[str]  # e.g., "5,5" for dashed
    marker_start: Optional[str]      # e.g., "url(#diamond-hollow)"
    marker_end: str                  # e.g., "url(#arrow-filled)"
    arrow_type: str                  # "filled", "hollow", "double"
```

### Rendering Example

```xml
<defs>
  <marker id="arrow-filled" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
    <polygon points="0 0, 8 4, 0 8" fill="black"/>
  </marker>
  <marker id="arrow-hollow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
    <polygon points="0 0, 8 4, 0 8" fill="none" stroke="black" stroke-width="1"/>
  </marker>
</defs>

<polyline points="110,125 110,200 200,200"
          stroke="#4A90E2"
          stroke-width="1"
          stroke-dasharray="5,5"
          fill="none"
          marker-end="url(#arrow-hollow)"/>
```

## Dependencies

- **Requires**: Phase 6B-Enhancement (Symbol Rendering) - COMPLETE
- **Blocks**: None (enhancement to existing feature)
- **Related**: User Story 5 (SVG Export)

## Performance Impact

- **Expected**: <5% additional rendering time (marker definition parsing)
- **Memory**: Negligible (relationship styles are small static objects)
- **SVG file size**: +2-5KB per diagram (marker definitions + additional path attributes)

## Testing Strategy

- **Unit tests**: 15+ for RelationshipStyleService and style validation
- **Integration tests**: Round-trip fidelity (relationship rendering consistent across exports)
- **BDD scenarios**: 5+ acceptance criteria covering relationship types and customization
- **Visual inspection**: Manual verification of rendered relationship symbols in browser

## Future Enhancements

- Relationship style animation (hover effects, transitions)
- Custom relationship style definitions
- Relationship grouping/bundling for dense diagrams
- Curved paths for aesthetic preference
- Relationship pattern library (user-defined styles)

---

## Estimated Effort

- **T119-T126**: 16-24 hours total
- **Complexity**: Medium (straightforward style definitions, familiar SVG rendering patterns)
- **Risk**: Low (isolated feature, well-tested underlying SVG export system)
