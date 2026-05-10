# Feature Specification: Enhance SVG View Export

**Feature Branch**: `012-enhance-svg-view`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "create a new branch on develop and a new feature to enhance and finalise a working and
accurate SVG representation of a model view, enhancing the current draft to_svg() function"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accurate Element Rendering (Priority: P1)

A developer exports a pyArchimate view as SVG and sees each element rendered at the correct position, with the correct
ArchiMate symbol shape, fill colour, icon, and label — matching what the Archi desktop tool would display.

**Why this priority**: The primary value of SVG export is visual fidelity. If elements are wrong, the whole feature is
unusable.

**Independent Test**: Load a `.archimate` file, call `view.to_svg()`, parse the SVG, and verify each element's `<rect>`
or `<path>` has position/size matching the model's `x`, `y`, `w`, `h` attributes, and that the correct ArchiMate symbol
body type (rect, rect_header, or path shape) is used for the element type.

**Acceptance Scenarios**:

1. **Given** a view with a `BusinessActor` element at (100, 50) with size 120×55, **When** SVG is exported, **Then** the
   rendered shape appears at exactly (100, 50) with width 120 and height 55.
2. **Given** a view whose elements have custom `fill_color` overrides, **When** SVG is exported, **Then** each shape
   uses the overridden colour instead of the default ArchiMate category colour.
3. **Given** a view whose elements span a non-zero origin (e.g., leftmost element at x=200), **When** SVG is exported, *
   *Then** the SVG canvas is sized to fit all elements without clipping (min/max bounds are honoured).
4. **Given** a view with nested elements (child nodes inside a container), **When** SVG is exported, **Then** the canvas
   bounds account for all nested elements, and nested elements appear inside their container visually.
5. **Given** an element type not listed in the symbol registry, **When** SVG is exported, **Then** a default rectangle
   shape is rendered (no crash) and the element label is shown.

---

### User Story 2 - Accurate Relationship Rendering (Priority: P1)

A developer exports a view containing ArchiMate relationships and sees each relationship rendered as an orthogonal
polyline with the correct ArchiMate stroke style (colour, dash pattern, arrowhead markers) for the relationship type.

**Why this priority**: Relationships are as important as elements in ArchiMate diagrams. Incorrect or missing
relationships make the export misleading.

**Independent Test**: Create a view with one element of each major relationship type (Association, Realization, Serving,
Composition, Aggregation, Access, Influence, Triggering, Flow), export to SVG, and verify each polyline has the expected
`stroke`, `stroke-dasharray`, and `marker-end` attributes per the ArchiMate 3.x specification.

**Acceptance Scenarios**:

1. **Given** a `RealizationRelationship` between two elements, **When** SVG is exported, **Then** the polyline uses a
   dashed stroke pattern and a hollow arrowhead.
2. **Given** a `CompositionRelationship` where the target is visually nested inside the source (containment), **When**
   SVG is exported, **Then** the relationship polyline is suppressed (already conveyed by the visual containment
   boundary).
3. **Given** a relationship with stored bendpoints, **When** SVG is exported, **Then** the polyline passes through all
   bendpoints and each segment is axis-aligned (orthogonal routing).
4. **Given** a relationship with a `stroke_color` override, **When** SVG is exported, **Then** the polyline uses the
   override colour rather than the default type colour.
5. **Given** multiple relationships sharing a source or target node, **When** SVG is exported, **Then** the endpoints
   are spread apart so overlapping lines are distinguishable.

---

### User Story 3 - Faithful Label and Text Rendering (Priority: P2)

A developer reading the exported SVG can identify every element by its label and every relationship by its type
annotation, with labels that are legible and do not overflow their containing shapes.

**Why this priority**: Labels are essential for diagram readability. They are less critical than layout fidelity but
directly affect usability of the output.

**Independent Test**: Export a view with elements having names of various lengths, verify that text is word-wrapped,
vertically centred for leaf elements, top-left aligned for container elements, and that relationship type abbreviations
appear near the midpoint of their polylines.

**Acceptance Scenarios**:

1. **Given** an element with a long name (more than ~15 characters), **When** SVG is exported, **Then** the name is
   word-wrapped into multiple `<tspan>` lines that fit within the element boundary.
2. **Given** a container element (has child nodes), **When** SVG is exported, **Then** the label is placed at the
   top-left of the container boundary (not centred).
3. **Given** a leaf element, **When** SVG is exported, **Then** the label is vertically and horizontally centred within
   the element bounds.
4. **Given** a relationship, **When** SVG is exported, **Then** the relationship type label (with "Relationship" suffix
   stripped) is placed at the midpoint of the longest polyline segment with a white background to avoid overlap.

---

### User Story 4 - Full BDD Acceptance Test Coverage (Priority: P2)

All existing BDD scenarios in `tests/features/layout/svg_export.feature` (currently tagged `@wip`) pass against the
implemented `to_svg()` function.

**Why this priority**: The existing BDD feature file documents the intended contract. Making these scenarios pass
validates completeness.

**Independent Test**: Run `behave tests/features/layout/svg_export.feature` with all `@wip` tags removed; all scenarios
pass.

**Acceptance Scenarios**:

1. **Given** the BDD step definitions in `tests/features/layout/svg_export_steps.py` are complete, **When** `behave`
   runs the SVG export feature, **Then** all scenarios pass with no skipped steps.
2. **Given** the integration test `test_svg_export.py`, **When** `pytest` runs, **Then** all tests pass (no `xfail` or
   skipped tests for SVG export).

---

### Edge Cases

- What happens when a view has zero elements? The SVG must be a valid, minimal SVG with a white background and no error.
- What happens when an element has an empty name? No `<text>` element is rendered; no crash.
- What happens when a relationship references a node UUID not present in the view? The relationship is silently skipped;
  no crash.
- What happens when `w` or `h` is zero or negative? A minimum display size is used to prevent invisible or inverted
  shapes.
- What happens when two elements are at identical positions (exact overlap)? Both are rendered; no crash.
- What happens when a file path provided to `to_svg(filepath=...)` is in a non-existent directory? A clear `IOError` is
  raised.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The export MUST produce valid, well-formed SVG XML with a `<svg>` root element and correct W3C namespace.
- **FR-002**: Each view element MUST be rendered at the position and size stored in the model (`x`, `y`, `w`, `h`), with
  no coordinate offset errors.
- **FR-003**: The SVG canvas MUST be sized to encompass all elements (including nested children) with a configurable
  margin; no element MAY be clipped by the canvas boundary.
- **FR-004**: Each element MUST be rendered using the correct ArchiMate symbol body (rect, rect_header, or custom path)
  for its element type.
- **FR-005**: Each element MUST display its icon in the top-right corner when a symbol icon is defined for its type.
- **FR-006**: Each element MUST display its name as a text label: centred for leaf elements, top-left for containers and
  groups.
- **FR-007**: Long element names MUST be word-wrapped to fit within the element boundary; no text MAY overflow the
  shape.
- **FR-008**: Each relationship MUST be rendered as an orthogonal polyline (axis-aligned segments only) connecting
  source and target boundary edges.
- **FR-009**: Each relationship polyline MUST use the stroke colour, dash pattern, and arrowhead markers defined for its
  ArchiMate relationship type.
- **FR-010**: Containment relationships (Composition/Aggregation where target is visually nested inside source) MUST be
  suppressed to avoid redundancy.
- **FR-011**: Relationships with stored bendpoints MUST route through those points; relationships without bendpoints
  MUST use a direct boundary-to-boundary line.
- **FR-012**: When multiple relationships share an endpoint node, their anchors MUST be spread apart on the node edge so
  they remain visually distinguishable.
- **FR-013**: Each relationship MUST display a short type label (without the "Relationship" suffix) near the midpoint of
  its longest segment.
- **FR-014**: Container elements (those with nested children) MUST visually enclose their children; the container
  boundary MUST surround all child positions.
- **FR-015**: The export MUST accept an optional `filepath` parameter; when provided, the SVG MUST be written to that
  file with a proper `<?xml?>` declaration prepended.
- **FR-016**: The `to_svg()` method MUST return the SVG XML string in all cases.
- **FR-017**: All existing BDD scenarios in `svg_export.feature` MUST have corresponding step implementations and MUST
  pass.
- **FR-018**: When a relationship's source or target UUID is not found in the view, the relationship MUST be silently
  skipped without raising an exception.
- **FR-019**: An element type not present in the symbol registry MUST fall back to a plain rectangle rendering.
- **FR-020**: Element fill colour overrides stored in the model MUST take precedence over default ArchiMate category
  colours.

### Key Entities

- **View**: The ArchiMate diagram view containing nodes and connections; exposes `nodes`, `conns`, `nodes_dict`
  collections.
- **Node**: An element placement on the view; has `x`, `y`, `w`, `h`, `type`, `name`, `uuid`, `fill_color`, and a
  `nodes` list of child nodes.
- **Connection**: A relationship placement; has `_source`, `_target` (UUIDs), `type`, `bendpoints`, `stroke_color`,
  `stroke_width`, and `stroke_style`.
- **SVGExportService**: The internal service that performs the rendering; `to_svg(view, filepath)` is the public API
  surface.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An SVG exported from any well-formed `.archimate` view file renders without errors and is parseable by
  standard XML tooling.
- **SC-002**: All 14 BDD scenarios in `svg_export.feature` pass (0 failures, 0 pending steps).
- **SC-003**: All existing integration tests in `test_svg_export.py` and `test_svg_background.py` pass with no
  regressions.
- **SC-004**: Visual comparison of the exported SVG against the same view opened in Archi desktop shows correct element
  positions, shapes, and relationships (verified by manual inspection of at least 3 representative views from the
  `tests/fixtures/` collection).
- **SC-005**: Elements at non-zero origin coordinates are not clipped — the SVG viewBox accounts for all `min_x`/`min_y`
  offsets.
- **SC-006**: The implementation introduces no new ruff/mypy/pyright violations.

## Assumptions

- ArchiMate symbol definitions in `archimate_symbols.py` already cover all element types; gaps require adding missing
  entries, not redesigning the registry.
- The view model API (`nodes`, `conns`, `nodes_dict`, node attributes) remains stable; no model-layer changes are
  required.
- SVG output targets visual inspection use cases (browser, vector viewer); pixel-perfect match to Archi's proprietary
  renderer is aspirational, not mandatory.
- Text rendering uses a fixed-width estimate (~6px per character) for word wrap; a more accurate font-metrics approach
  is out of scope.
- The `behave` BDD step definitions are the responsibility of this feature; the feature file scenarios are already
  written.
- Relationship routing improvements (e.g., avoiding node intersections) are out of scope; existing orthogonal routing
  logic is retained and corrected where broken.
- Colour scheme follows ArchiMate 3.x category defaults already defined in `color_palette.py`.
