# Implementation Plan: Enhance SVG View Export

**Branch**: `012-enhance-svg-view` | **Date**: 2026-05-09–10 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/012-enhance-svg-view/spec.md`

## Summary

Overhaul `to_svg()` to produce ArchiMate-compliant SVG output: correct symbols and icons for all
element types, accurate relationship rendering (arrows, markers, junction types), and lossless
round-trip of connection waypoints through both Archi `.archimate` and OpenGroup `.xml` formats.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: lxml, xml.etree.ElementTree (stdlib), pyArchimate view model  
**Storage**: File I/O only (SVG output, `.archimate`/`.xml` round-trip)  
**Testing**: pytest (unit), behave (BDD)  
**Target Platform**: Any (library)  
**Project Type**: Library  
**Performance Goals**: SVG generation < 1 s for typical views  
**Constraints**: No routing in `to_svg()` — layout is deferred to a future auto-layout phase  
**Scale/Scope**: All ArchiMate 3.x element types (~62 symbols) and relationship types (~15)

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| I. Code Quality | ✅ | All C901 complexity violations extracted into helpers; ruff clean |
| II. Testing Standards | ✅ | Pre-commit hooks pass; existing suite not regressed |
| III. UX Consistency | ✅ | SVG output matches Archi tool for tested views |
| VI. State Management | ✅ | `Point` now stores float to preserve half-integer centres |
| VII. System Integrity | ✅ | Bendpoints preserved exactly across archimate↔xml↔svg |
| VIII. Durability | ✅ | OpenGroup XML drops embedded-connection filter; all 21 connections preserved |
| IX. Cross-platform | ✅ | SVG is browser/viewer agnostic |

**Violations requiring justification**: None.

## Project Structure

### Documentation (this feature)

```text
specs/012-enhance-svg-view/
├── plan.md              ← this file
├── research.md          ← Phase 0 research (inline below)
├── data-model.md        ← Phase 1 design (inline below)
└── tasks.md             ← Phase 2 tasks (/speckit-tasks output)
```

### Source Code affected

```text
src/pyArchimate/
├── view/
│   ├── __init__.py                          # Point.x/y: int→float storage
│   └── layout/export/
│       ├── svg_export.py                    # SVGExportService — major rewrite
│       └── symbols/
│           ├── archimate_symbols.py         # 62 symbols: icons, body shapes, fixes
│           ├── archimate_relationships.py   # marker constants, RelationshipStyleService
│           ├── ArchimateStencils/           # 30+ new _2.svg icon files
│           │   ├── Application Layer/
│           │   ├── Business Layer/
│           │   ├── Composite Elements/
│           │   ├── Implementation and Migration Elements/
│           │   ├── Motivation Elements/
│           │   ├── Physical Elements/
│           │   ├── Strategy Elements/
│           │   └── Technology Layer/
├── readers/
│   └── _archireader_helpers.py              # (read only — no bugs found)
└── writers/
    ├── archiWriter.py                       # bendpoint offset: int()→round()
    └── archimateWriter.py                   # remove _is_node_embedded filter; int coords
```

## Phase 0: Research

### Decision 1 — Icon coordinate system

- **Decision**: Icon paths live in the 150×75 reference space; `_translate_icon()` translates
  (scale=1.0) to canvas position. No scaling → fixed pixel size regardless of element size.
- **Rationale**: Avoids arc/flag mangling in `_apply_path_transform`; all icons use M/L/C commands only.
- **Alternatives rejected**: Scaling icons with element — icons would change size on resize.

### Decision 2 — Arc commands in icon paths

- **Decision**: Replace SVG `a` arc commands with cubic bezier approximations (k=0.5523).
- **Rationale**: `_apply_path_transform` uses a regex that misidentifies arc flag params as
  coordinate pairs, corrupting the path. Bezier avoids this entirely.
- **Alternatives rejected**: Fix the regex — brittle; doesn't handle all SVG path grammar.

### Decision 3 — `to_svg()` routing policy

- **Decision**: `to_svg()` clips source→first-waypoint and last-waypoint→target; passes stored
  bendpoints as-is. No routing, orthogonalization, stubs, or spread applied.
- **Rationale**: Routing belongs to the auto-layout engine (future feature). `to_svg()` must be
  a faithful renderer of the stored model state.
- **Alternatives rejected**: Keep routing — user explicitly requested its removal.

### Decision 4 — Bendpoint precision

- **Decision**: `Point` stores float (not int). Archi format computes absolute coords as
  `offset + element.cy` where `cy = y + h/2`; for `h=55`, `cy = y + 27.5` (half-integer).
  Old `int()` truncation caused 1-pixel drift per write cycle.
- **Rationale**: `round(75.0) = 75` is exact; `int(74.5) = 74` is wrong.
- **Alternatives rejected**: `round()` in writer only — still loses 0.5 if Point truncates first.

### Decision 5 — OpenGroup XML integer coordinates

- **Decision**: `archimateWriter` writes `int(round(bp.x))` — integers only.
- **Rationale**: Archi tool rejects float attributes (e.g., "517.5") with parse error.
  0.5-pixel SVG drift is acceptable vs. broken interoperability.
- **Alternatives rejected**: Write floats (`:g` format) — breaks Archi import.

## Phase 1: Design

### Data Model

#### `Point` (view/__init__.py)

| Field | Old type | New type | Reason |
|-------|----------|----------|--------|
| `_x`  | `int`    | `float`  | Preserve half-integer absolute coords |
| `_y`  | `int`    | `float`  | Preserve half-integer absolute coords |

No schema migration needed — in-memory only.

#### `SymbolDefinition` (archimate_symbols.py)

```python
class SymbolDefinition(NamedTuple):
    element_type: str
    svg_path: str          # body path in 150×75 reference space
    viewBox: str
    bounding_box: tuple[float, float, float, float]
    default_color: str
    icon_path: str | None  # NEW: corner icon, fixed-size bezier paths
    icon_viewbox: str | None  # NEW: "min_x min_y w h" for translation
    body_type: str         # "rect" | "rect_header" | "path"
```

New shared icon constants: `_ICON_COLLABORATION`, `_ICON_DISTRIBUTION_NETWORK`,
`_ICON_SYSTEM_SOFTWARE` (all multi-line bezier strings).

#### `RelationshipStyle` (archimate_relationships.py)

No structural changes. New import: `_ARROW_FILLED` exposed for use in `svg_export.py`.

### Key Contracts

#### `SVGExportService._get_clipped_polyline_points(source, target, bendpoints)`

```
Input:  source_node, target_node (view Nodes), bendpoints (list[Point])
Output: list[(float, float)] — [clip_start, *waypoints, clip_end]
Contract:
  - clip_start = boundary intersection of (source_center → first_bp or target_center)
  - clip_end   = boundary intersection of (target_center → last_bp or source_center)
  - waypoints  = [(bp.x, bp.y) for bp in bendpoints]  — no modification
  - NO routing, no stubs, no orthogonalization
```

Old routing API preserved as `_get_routed_polyline_points()` for future layout engine.

#### `SVGExportService._apply_marker_attrs(rel_type, conn, style, attrs)`

```
Access:
  - Read  → marker-start only (reversed arrow-start marker, tip at element edge)
  - Write → marker-end only
  - ReadWrite → both
  - undefined → no markers
Association:
  - is_directed=true → marker-end; else no markers
Composition/Aggregation:
  - marker-start = diamond only (no marker-end)
Others:
  - use style.marker_start / style.marker_end
```

#### `SVGExportService._offset_points_for_markers(points, polyline_attrs)`

```
diamond start: push pts[0] forward by 8px along first segment direction
               (refX=8 → right tip at adjusted point, left tip at element edge)
any end arrow: pull pts[-1] backward by 8px along last segment direction
               (refX=0 → tip at element edge, base at adjusted point)
Works for horizontal, vertical, and diagonal connections.
Uses round() not int() to avoid 1px drift.
```

### Archi Stencil Icon Files created (30 new `_2.svg`)

| Folder | Files |
|--------|-------|
| Application Layer | `Data_object_2.svg` |
| Business Layer | `Business_object_2`, `Contract_2`, `Product_2`, `Representation_2` |
| Composite Elements | `Grouping_2`, `Location_2` |
| Implementation & Migration | `Deliverable_2`, `Gap_2`, `Plateau_2`, `Work_package_2` |
| Motivation Elements | `Assessment_2`, `Driver_2`, `Goal_2`, `Meaning_2`, `Outcome_2`, `Principle_2`, `Stakeholder_2`, `Value_2` |
| Physical Elements | `Equipment_2`, `Facility_2`, `Material_2` |
| Strategy Elements | `Capability_2`, `Course_of_action_2`, `Resource_2`, `Value_Stream_2` |
| Technology Layer | `Technology_interface_2` (spelling fix) |

### Symbol fixes applied (`archimate_symbols.py`)

| Symbol | Fix |
|--------|-----|
| `_ICON_INTERFACE` | Added circle (was line-stub only) |
| `BusinessActor` | Added head ellipse |
| `BusinessRole`, `Stakeholder` | Added circle to C-bracket |
| `CommunicationNetwork` | Bidirectional arrow (was hexagon — wrong shape) |
| `ApplicationComponent` | Corrected tab proportions |
| `Value` | Body → ellipse (was octagon) |
| `Meaning` | Body → cloud bezier (was octagon) |
| `Contract` | Body → rect + 2 horizontal lines |
| `Product` | Body → rect + corner fold |
| `Representation` | Body → wavy S-curve (y-stretched to full element height) |
| `Grouping` | Body → dashed L-shape with tab; label in tab area |
| `Driver` | Icon → target circles (was crosshairs) |
| `Gap` | Icon → circle + line |
| `Assessment` | Icon → circle + diagonal line (was bare line) |
| `Goal` | Icon → concentric circles |
| `Location` | Icon → teardrop/pin |
| `Deliverable` | Icon → mini wavy rect |
| `WorkPackage` | Icon → mini rounded rect |
| `BusinessCollaboration`, `TechnologyCollaboration` | Icon → `_ICON_COLLABORATION` |
| `DistributionNetwork` | Icon → 3D pipe parallelogram |
| `SystemSoftware` | Icon → isometric box |
| `Material` | Icon → hexagon + 3 facets |
| `Capability`, `Resource`, `CourseOfAction` | Icons from Strategy stencils |
| `ValueStream` | Icon → hexagonal arrow |

### Relationship rendering fixes (`svg_export.py`)

| Fix | Detail |
|-----|--------|
| Access arrows | `access_type` Read/Write/ReadWrite/undefined → correct markers |
| Association | Arrow only when `is_directed=true` |
| Influence label | Appends `influence_strength` |
| OrJunction | White circle; resolves via `element.junction_type == "or"` |
| AndJunction | Black circle |
| All markers | `refX` corrected + polyline endpoint offsets so lines don't cross markers |
| `arrow-start` | New reversed marker: tip at element edge, body outward |
| `diamond-*` | `fill="white"` on hollow; `refX=8`; line starts at far tip |
| `arrow-hollow` | `fill="white"`; line stops at arrowhead base |
| Container elements | Keep own symbol (removed dashed-rect override for has_children) |
| Grouping | Dashed L-path; tab height = text content, not element height |
| Icon sizing | Fixed-size (22px×20px minimum threshold); hidden when element too small |

### Writer fixes

| File | Fix |
|------|-----|
| `archiWriter.py` | `int()` → `round()` for bendpoint offset back-conversion |
| `archimateWriter.py` | Remove `_is_node_embedded` filter (was silently dropping embedded connections) |
| `archimateWriter.py` | `int(round(bp.x/y))` — integer coords for Archi compatibility |

## Complexity Tracking

| Item | Justification |
|------|---------------|
| 30 new SVG files | Each `_2.svg` extracts the icon from its parent stencil; required for icon registry |
| `_get_routed_polyline_points()` kept | Future auto-layout engine will call it; not dead code |
| Float `Point` storage | Required for lossless Archi↔pyArchimate bendpoint round-trip |
