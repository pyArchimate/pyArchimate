# Tasks: Enhance SVG View Export

**Input**: Design documents from `/specs/012-enhance-svg-view/`  
**Branch**: `012-enhance-svg-view`  
**Status**: ✅ All tasks DONE (retro-engineered from commits fef987b, 131426c, 6c0d0df, e9e5598)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no deps on same-phase incomplete tasks)
- **[Story]**: Which user story (US1=Element rendering, US2=Relationship rendering, US3=Labels, US4=BDD)
- All tasks marked ✅ = completed

---

## Phase 1: Setup & Symbol Registry Foundation

**Purpose**: Establish correct symbol definitions and stencil icon files before rendering logic.

- [x] T001 [P] Audit all 62 symbols in `archimate_symbols.py` — identify missing icons, wrong body shapes, bad icon_viewbox values
- [x] T002 [P] Audit all `_2.svg` stencil icon files in `ArchimateStencils/` subdirs — identify missing files per element type
- [x] T003 Extract icons from `Material.svg` → `Physical Elements/Material_2.svg` (hexagon + 3 facets, normalized to origin)
- [x] T004 [P] Extract icons from `Strategy Elements/Capability.svg`, `Resource.svg`, `Course_of_action.svg` → `*_2.svg` files
- [x] T005 Normalize `Strategy Elements/Value_Stream.svg` (Batik→libvisio2svg format, remove text) + extract `Value_Stream_2.svg`
- [x] T006 [P] Create all missing `_2.svg` files across all stencil folders (20 new files: Business Layer, Composite, Implementation, Motivation, Physical)
- [x] T007 Fix `Technology_interface_2.svg` filename typo (was `Technology_iterface_2.svg`)

---

## Phase 2: Foundational — Icon Coordinate System

**Purpose**: Establish the icon translation pipeline before adding individual icons.

- [x] T008 Diagnose `_apply_path_transform` arc-command corruption — arc params (`rx,ry`, flags) misread as coordinate pairs
- [x] T009 Establish rule: all icon paths use M/L/C only (no `a` arcs); replace circles with 4-segment cubic bezier (k=0.5523)
- [x] T010 Define `_ARROW_FILLED` constant in `archimate_relationships.py` and expose via import in `svg_export.py`
- [x] T011 Add `_ICON_COLLABORATION` constant (two overlapping bezier circles) to `archimate_symbols.py`
- [x] T012 [P] Add `_ICON_DISTRIBUTION_NETWORK` constant (3D pipe parallelogram) to `archimate_symbols.py`
- [x] T013 [P] Add `_ICON_SYSTEM_SOFTWARE` constant (isometric box) to `archimate_symbols.py`

---

## Phase 3: US1 — Accurate Element Rendering

**Story goal**: Every element renders at correct position/size with correct ArchiMate symbol, fill, icon, and label.

**Independent test**: Load `symbols.archimate`, call `view.to_svg()`, verify each element `<rect>`/`<path>` matches model x/y/w/h and correct body type.

### Phase 3a: Icon fixes (shared constants)

- [x] T014 [US1] Fix `_ICON_INTERFACE`: add bezier circle (was line-stub only) in `archimate_symbols.py`; update all three `*Interface` icon_viewbox to `"128 3 22 16"`
- [x] T015 [US1] Fix `BusinessActor` icon: add head ellipse bezier + body/arms/legs lines in `archimate_symbols.py`
- [x] T016 [US1] Fix `BusinessRole` + `Stakeholder` icons: add circle to C-bracket in `archimate_symbols.py`
- [x] T017 [US1] Fix `CommunicationNetwork` icon: bidirectional arrow (was wrong hexagon shape) in `archimate_symbols.py`
- [x] T018 [US1] Fix `ApplicationComponent` icon: correct tab proportions (tabs were overlapping main rect) in `archimate_symbols.py`
- [x] T019 [US1] Fix `Driver` icon: target circles (outer + dot) replacing incorrect crosshairs in `archimate_symbols.py`
- [x] T020 [US1] Fix `Assessment` icon: small circle + diagonal line in `archimate_symbols.py`

### Phase 3b: New icons from stencil files

- [x] T021 [P] [US1] Add icons for all 3 collaboration types (`ApplicationCollaboration`, `BusinessCollaboration`, `TechnologyCollaboration`) using `_ICON_COLLABORATION`
- [x] T022 [P] [US1] Add `Goal` icon (concentric circles), `Location` icon (teardrop/pin) in `archimate_symbols.py`
- [x] T023 [P] [US1] Add `Gap` icon (circle + horizontal line), `Deliverable` icon (mini wavy rect), `WorkPackage` icon (mini rounded rect)
- [x] T024 [P] [US1] Add `Material` icon (hexagon + facets, scale 1.71, offset (130,4)) in `archimate_symbols.py`
- [x] T025 [P] [US1] Add `Capability`, `Resource`, `CourseOfAction`, `ValueStream` icons from Strategy stencil `_2.svg` files
- [x] T026 [P] [US1] Add `DistributionNetwork` icon using `_ICON_DISTRIBUTION_NETWORK`; `SystemSoftware` using `_ICON_SYSTEM_SOFTWARE`

### Phase 3c: Body shape fixes

- [x] T027 [US1] Fix `Value` body: ellipse bezier scaled to 150×60 centred in 75-unit height (was wrong octagon) in `archimate_symbols.py`
- [x] T028 [US1] Fix `Meaning` body: cloud bezier shape scaled to 150×75 (was wrong octagon) in `archimate_symbols.py`
- [x] T029 [US1] Fix `Contract` body: rect + two horizontal divider lines at y≈16 and y≈59 (body_type="path") in `archimate_symbols.py`
- [x] T030 [US1] Fix `Product` body: rect + corner fold (L-shape from midpoint top) in `archimate_symbols.py`
- [x] T031 [US1] Fix `Representation` body: S-curve wavy bottom (sides at y=63, trough at y=75) to match `Product` height
- [x] T032 [P] [US1] Apply `Grouping.svg` L-shape path as body; icon from `Grouping_2.svg` in `archimate_symbols.py`

### Phase 3d: Icon sizing and container rendering

- [x] T033 [US1] Fix icon suppression: hide icon when element too small (w < 30px or h < 28px) in `svg_export.py`
- [x] T034 [US1] Fix container rendering: remove `has_children` dashed-rect override — containers keep own symbol in `svg_export.py`
- [x] T035 [US1] Fix `Grouping` node rendering: dashed L-shaped path with tab; tab height = text content not element height in `svg_export.py`
- [x] T036 [US1] Extract `_render_junction()` helper (Or=white circle, And=black circle with `element.junction_type` lookup) in `svg_export.py`
- [x] T037 [US1] Extract `_render_grouping()` helper (dashed L-path, text in tab) in `svg_export.py`

---

## Phase 4: US2 — Accurate Relationship Rendering

**Story goal**: Each relationship renders with correct ArchiMate stroke style and arrowhead markers.

**Independent test**: One connection per major type; verify `stroke`, `stroke-dasharray`, `marker-end` attributes match ArchiMate 3.x spec.

### Phase 4a: Marker definitions

- [x] T038 [US2] Add `arrow-start` reversed marker (polygon `8 0,0 4,8 8`; `refX=0`): tip at element edge, body toward target in `svg_export.py` `_add_defs()`
- [x] T039 [US2] Fix `arrow-filled`: `refX=0` (tip at adjusted endpoint, body on line side); polyline end pulled back 8px
- [x] T040 [US2] Fix `arrow-hollow`: `refX=0` + `fill="white"` (covers line inside body); polyline end pulled back 8px
- [x] T041 [US2] Fix `diamond-filled`: `refX=8` (right tip at adjusted point); polyline start pushed forward 8px
- [x] T042 [US2] Fix `diamond-hollow`: `refX=8` + `fill="white"`; polyline start pushed forward 8px

### Phase 4b: Marker offset helper

- [x] T043 [US2] Implement `_offset_points_for_markers(points, polyline_attrs)` in `svg_export.py` — diamond start pushes pts[0] +8px, end arrow pulls pts[-1] -8px; uses `round()` not `int()`; handles vertical, horizontal, diagonal

### Phase 4c: Relationship attribute dispatch

- [x] T044 [US2] Implement `_apply_access_markers(conn, attrs)` — Read→start arrow, Write→end arrow, ReadWrite→both, undefined→none in `svg_export.py`
- [x] T045 [US2] Implement `_apply_marker_attrs(rel_type, conn, style, attrs)` dispatching to access/association/composition-aggregation/others in `svg_export.py`
- [x] T046 [US2] Fix Access: read `conn.access_type` / `conn._access_type`; normalise enum `.value`; use `url(#arrow-start)` for Read direction in `svg_export.py`
- [x] T047 [US2] Fix Association: arrow only when `is_directed=true`; no arrow for undirected in `svg_export.py`
- [x] T048 [US2] Fix Composition/Aggregation: diamond start only (no end arrow) in `svg_export.py`
- [x] T049 [US2] Fix Influence label: append `(influence_strength)` to label text in `svg_export.py`

### Phase 4d: Junction nodes

- [x] T050 [US2] Implement OrJunction rendering: white-filled circle; resolve via `model.elements` → `element.junction_type == "or"` in `svg_export.py` `_render_junction()`
- [x] T051 [US2] Implement AndJunction rendering: black-filled circle; element_type == "Junction" (reader strips Or/And) defaults to And in `svg_export.py`

### Phase 4e: Refactor for C901 compliance

- [x] T052 [US2] Extract `_apply_marker_attrs()` + `_apply_access_markers()` from `_render_relationship()` to reduce complexity below C901 limit (20→<10) in `svg_export.py`
- [x] T053 [US2] Extract `_render_junction()` + `_render_grouping()` from `_render_node_into()` to reduce complexity below C901 limit (13→<10) in `svg_export.py`

---

## Phase 5: US3 — Connection Waypoint Preservation

**Story goal**: Stored bendpoints rendered exactly; no routing applied by `to_svg()`.

**Independent test**: Load `symbols.archimate`, call `view.to_svg()`, verify each polyline passes through stored (x,y) bendpoints unchanged.

- [x] T054 [US3] Rewrite `_get_clipped_polyline_points()`: clip source→first-bp, pass bendpoints as-is, clip target→last-bp; NO routing in `svg_export.py`
- [x] T055 [US3] Preserve old routing in `_get_routed_polyline_points()` for future auto-layout engine in `svg_export.py`
- [x] T056 [US3] Remove `endpoint_spreads` parameter from `_render_relationship()`, `_render_connection()`, and `to_svg()` in `svg_export.py`
- [x] T057 [US3] Remove `_compute_endpoint_spreads()` call from `to_svg()` in `svg_export.py`
- [x] T058 [US3] Fix `Point.__init__`: `int(x)` → `float(x)` to preserve half-integer absolute coords (e.g. offset 75 + cy 69.5 = 144.5) in `view/__init__.py`
- [x] T059 [US3] Fix `archiWriter.py` bendpoint back-conversion: `int(offset)` → `round(offset)` so `round(144.5-69.5) = round(75.0) = 75` (was int(74.5)=74)

---

## Phase 6: US4 — OpenGroup XML Round-trip Fidelity

**Story goal**: Connections preserved correctly when writing/reading OpenGroup `.xml` format.

**Independent test**: `model.write('out.xml')` then re-read; all connection types, counts, and bendpoints match original.

- [x] T060 [US4] Remove `_is_node_embedded()` filter from `_write_connections()` in `archimateWriter.py` — was silently dropping 12/21 connections in Organisation view (all Compositions from containers to embedded children)
- [x] T061 [US4] Fix `archimateWriter.py` bendpoint format: `str(int(round(bp.x)))` — integers only; float format (":g") rejected by Archi tool
- [x] T062 [US4] Verify `archimateReader.py` correctly uses `float(bp.get('x'))` for OpenGroup format (no change needed — already correct)

---

## Phase 7: Polish & Cross-cutting

- [x] T063 [P] Run `ruff check` after each commit; fix all C901/N806/E702 violations introduced by changes in `svg_export.py` and `archimateWriter.py`
- [x] T064 [P] Validate all 62 symbols with `validate_symbols()` — 62 valid, 0 invalid
- [x] T065 [P] Regenerate test SVGs from `symbols.archimate` → verify `Organisation`, `View`, `All Relations` views render correctly
- [x] T066 Commit all changes as two logical commits: `feat: enhance SVG export` (fef987b) + `fix: relationship/junction rendering` (131426c) + `fix: preserve connections` (6c0d0df) + `fix: revert float XML coords` (e9e5598)

---

## Dependencies

```
T001-T007 (stencil audit/creation)
    ↓
T008-T013 (coordinate system + constants)
    ↓
T014-T037 (US1: element rendering)     ← can start T038-T053 in parallel after T008-T013
T038-T053 (US2: relationship rendering)
    ↓
T054-T059 (US3: waypoint preservation) ← depends on nothing except T056 needs svg_export touched
T060-T062 (US4: XML round-trip)
    ↓
T063-T066 (polish)
```

## Parallel Opportunities

- **T001+T002**: Audit symbols vs audit stencils simultaneously
- **T012+T013**: Two icon constants, different strings
- **T021–T026**: All add new icon_path entries to different symbol dict entries
- **T027–T032**: Body shape fixes, each touches a different symbol entry
- **T038–T042**: Five marker definition fixes in `_add_defs()`
- **T044+T045**: Two extract-methods, different dispatch branches
- **T058+T059**: One touches `view/__init__.py`, other touches `archiWriter.py`
- **T060+T061**: Different functions in `archimateWriter.py`

## Statistics

| Phase | Tasks | Status |
|-------|-------|--------|
| Setup + stencils | T001–T007 | ✅ 7 done |
| Icon coord system | T008–T013 | ✅ 6 done |
| US1 Element rendering | T014–T037 | ✅ 24 done |
| US2 Relationship rendering | T038–T053 | ✅ 16 done |
| US3 Waypoint preservation | T054–T059 | ✅ 6 done |
| US4 XML round-trip | T060–T062 | ✅ 3 done |
| Polish | T063–T066 | ✅ 4 done |
| **Total** | **T001–T066** | **✅ 66 done** |
