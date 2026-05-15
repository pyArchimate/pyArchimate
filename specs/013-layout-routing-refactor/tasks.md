# Tasks: Auto-Layout and Auto-Routing Separation

**Type**: Enhancement / Refactor | **Date**: 2026-05-11 | **Branch**: `013-layout-routing-refactor`

**Phase 1 complete** — all 61 original tasks done. Phase 2 tasks are in [phase2-routing-quality.md](phase2-routing-quality.md).

## Phase 2 task summary

| Range | Fix | FRs | Priority |
|-------|-----|-----|----------|
| P2-T01 – P2-T06 | Path cleanup: U-turns + redundant bendpoints (RQ-01, RQ-02) | — | P1/P2 |
| P2-T07 – P2-T11 | Layout: grid_size default 240px, high-degree node isolation (RQ-05, RQ-06) | — | P1/P2 |
| P2-T12 – P2-T21 | Multi-pass routing: eliminate node crossings + double crossings (RQ-03, RQ-04) | FR-013 | P1/P2 |
| P2-T22 – P2-T31 | Routing-driven node repositioning (FR-023) | FR-023 | P1/P2 |
| P2-T32 – P2-T37 | Node avoidance zone 25px (FR-013 updated) | FR-013 | P1/P2 |
| P2-T38 – P2-T42 | Min segment gap 20px default (FR-015 updated) | FR-015 | P1/P2 |
| P2-T43 – P2-T49 | Post-L-turn min segment 40px (FR-024 new) | FR-024 | P1/P2 |
| P2-T50 – P2-T54 | View.duplicate() deep copy (FR-025 new) | FR-025 | P1/P2 |

**Total Phase 2 tasks**: 55 (P2-T01 → P2-T55, including new P2-T55 for ObstacleMap rebuild)

**Status**: P2-T01–T31 complete (Phase 2A–D). P2-T32–T55 pending (Phase 2E–H).

**TDD-compliant execution order for pending tasks**:
1. P2-T34/T36 (tests) → P2-T32/T33/T35 (impl) — node clearance 25px; **must complete before P2-T14 can be verified**
2. P2-T40/T41 (tests) → P2-T38/T39 (impl) — segment gap 20px
3. P2-T46/T47/T48 (tests) → P2-T43/T44/T45 (impl) — turn segment 40px
4. P2-T51/T52/T53 (tests) → P2-T50/T54 (impl+BDD) — View.duplicate [parallel track]
5. P2-T55 (impl) — ObstacleMap rebuild for node-move [add after P2-T33]

## Phase 2 quick-reference (see phase2-routing-quality.md for full detail)

### 2A — Path cleanup

- [X] P2-T01: Diagnose remaining U-turns — result: 0 U-turns, 1 redundant collinear bendpoint found
- [X] P2-T02: Fix displacement double-shift — N/A: U-turns already 0; `remove_uturn_waypoints` sufficient
- [X] P2-T03: Add `_merge_collinear_adjacent()` to `segment_separation.py`
- [X] P2-T04: Wire `_merge_collinear_adjacent()` into `auto_route`
- [X] P2-T05: Test `test_no_redundant_bendpoints`
- [X] P2-T06: Strengthen U-turn test to zero

### 2B — Layout improvements
- [X] P2-T07: Change `LayoutConfig.grid_size` default 120 → 240
- [X] P2-T08: Add `LayoutConfig.high_degree_threshold = 5`
- [X] P2-T09: Implement high-degree node row isolation in `assign_grid_cells`
- [X] P2-T10: Unit test for 240px grid snap
- [X] P2-T11: Unit test for high-degree isolation

### 2C — Multi-pass routing
- [X] P2-T12: `ObstacleMap.unmark_routed_segment()`
- [X] P2-T13: Extract `_route_pass()` helper
- [X] P2-T14: `_detect_node_crossings()`
- [X] P2-T15: `_detect_double_crossings()`
- [X] P2-T16: Multi-pass outer loop in `auto_route` (max 3 passes)
- [X] P2-T17: `RoutingConfig.max_routing_passes = 3`
- [X] P2-T18–P2-T21: Tests and performance validation

### 2D — Routing-driven node repositioning (FR-023, opt-in)
- [X] P2-T22: `NodeMove` dataclass; `LayoutResult.node_moves` field
- [X] P2-T23: `RoutingConfig.allow_node_move = False`, `max_node_displacement = 1`
- [X] P2-T24: `_find_candidate_node_moves()` — returns candidate (node/block, delta) pairs
- [X] P2-T25: `_apply_node_move()` — tentative move with no-overlap check
- [X] P2-T26: Wire node-move fallback into multi-pass (after Pass 2, before skip+warn)
- [X] P2-T27: Test `allow_node_move=False` → SC-010 preserved
- [X] P2-T28: Test single blocking node moved 1 cell to open corridor
- [X] P2-T29: Test move rejected when it would cause overlap
- [X] P2-T30: Test rigid block moves together (`_find_candidate_node_moves` tests)
- [X] P2-T31: Integration test — `NodeMove` entries in result

---

## Phase 2E: Node Avoidance Zone 25px (FR-013 / SC-006) — PENDING

**Goal**: Routing avoids a 25px zone around each node side (not just the bounding box itself).

**Independent Test**: Route a connection in a view where a straight path would pass 20px from a node side. Verify the routed path detours ≥ 25px from that node side.

- [ ] P2-T34 [P] [US2] [TEST-FIRST] Write unit tests `tests/unit/test_node_clearance.py`: (a) segment passing 0px from node side now blocked; (b) segment at 24px blocked; (c) segment at 26px passes — confirm all FAIL before P2-T32/T33
- [ ] P2-T36 [P] [US2] [TEST-FIRST] Write unit test: `RoutingConfig(node_clearance=10)` produces 10px inflation (not 25px default) — confirm FAIL
- [ ] P2-T32 [US2] Add `node_clearance: int = 25` to `RoutingConfig` in `src/pyArchimate/layout/routing_config.py`; add `__post_init__` validation: `node_clearance ≥ 0`
- [ ] P2-T33 [US2] Update `ObstacleMap.__init__` in `src/pyArchimate/layout/auto_route.py` to inflate each node AABB by `config.node_clearance` px on all four sides — P2-T34/T36 should now pass
- [ ] P2-T35 [US2] Update SC-006 + SC-007 assertions in `tests/integration/test_tutorial_svg_requirements.py`: check inflated AABB (25px); also verify label clearance still passes after inflation
- [ ] P2-T37 [P] [US4] Write BDD scenario `features/routing/node_clearance.feature`: Given `node_clearance=25`, When `auto_route` called, Then 0 segments within 25px of any node side

**Checkpoint**: `RoutingConfig.node_clearance` working; `_detect_node_crossings` (P2-T14) must use inflated AABB — verify this dependency is satisfied.

---

## Phase 2F: Min Segment Gap 20px (FR-015 / SC-008) — PENDING

**Goal**: Default parallel-segment separation raised from 10px to 20px.

**Independent Test**: Route two connections that share a corridor. Verify they are separated by ≥ 20px (not 10px) with default `RoutingConfig`.

- [ ] P2-T40 [P] [US2] [TEST-FIRST] Write unit test `tests/unit/test_segment_separation.py`: two collinear connections separate to ≥ 20px with default config — confirm FAIL (current default is 10px)
- [ ] P2-T41 [P] [US2] [TEST-FIRST] Write unit test: `RoutingConfig(min_segment_gap=5)` → separation ≥ 5px — confirm FAIL
- [ ] P2-T38 [US2] Change `min_segment_gap` default from `10.0` to `20.0` in `RoutingConfig` — P2-T40/T41 should now pass
- [ ] P2-T39 [US2] Update all existing unit/integration tests that hardcode `min_segment_gap=10` or assert `≥ 10px` separation — change thresholds to 20px
- [ ] P2-T42 [P] [US4] Write BDD scenario `features/routing/segment_gap.feature`: Given default config, When `auto_route` called, Then parallel segments ≥ 20px

---

## Phase 2G: Post-L-Turn Minimum Segment 40px (FR-024 / SC-012) — PENDING

**Goal**: Every segment following a 90° bend is ≥ 40px (except the terminal arrival segment).

**Independent Test**: Route an L-shaped connection where the post-turn segment would naturally be 10px. Verify `auto_route` produces a path where that segment is 40px. Verify the final arrival segment is not extended.

**Pipeline order** (two enforce passes required by M6): `_merge_collinear_adjacent → _enforce_min_turn_segment (pass 1) → _fix_u_turns → _enforce_min_turn_segment (pass 2) → _displace_collinear_overlaps`

- [ ] P2-T46 [P] [US2] [TEST-FIRST] Write unit tests `tests/unit/test_geometry.py` for `_enforce_min_turn_segment`: (a) L-shape with 10px post-turn segment extended to 40px; (b) conforming path unchanged; (c) two consecutive L-turns both enforced; (d) terminal arrival segment NOT extended; (e) single-segment path is no-op — confirm all FAIL
- [ ] P2-T47 [P] [US2] [TEST-FIRST] Write unit test: `min_turn_segment=20` → 20px floor, not 40px — confirm FAIL
- [ ] P2-T48 [P] [US2] [TEST-FIRST] Write integration test in `tests/integration/test_tutorial_svg_requirements.py`: SC-012 assertion — all non-terminal post-turn segments ≥ 40px in tutorial view — confirm FAIL
- [ ] P2-T43 [US2] Add `min_turn_segment: int = 40` to `RoutingConfig`; add `__post_init__` validation: `0 < min_turn_segment ≤ 500`
- [ ] P2-T44 [US2] Implement `_enforce_min_turn_segment(waypoints, min_len)` in `src/pyArchimate/layout/geometry.py`: skip terminal arrival segment (last segment before target attachment); extend other short post-turn segments by push-out — P2-T46/T47 should pass
- [ ] P2-T45 [US2] Wire `_enforce_min_turn_segment` twice in `auto_route` post-processing: pass 1 after `_merge_collinear_adjacent`; pass 2 after `_fix_u_turns` — P2-T48 should pass
- [ ] P2-T49 [P] [US4] Write BDD scenario `features/routing/turn_segment.feature`: Given `min_turn_segment=60`, When `auto_route` called, Then all non-terminal post-turn segments ≥ 60px

---

## Phase 2H: View.duplicate() (FR-025 / SC-013) — PENDING

**Goal**: `View.duplicate(name=None)` returns independent deep copy registered in same model.

**Independent Test**: Call `view.duplicate("copy")`; verify new view has same node + connection count; mutate a node position in the copy; verify original unchanged; verify `view.model is None` raises `ValueError`.

*This phase is fully independent of routing changes — can be parallelised with 2E/2F/2G.*

- [ ] P2-T51 [P] [US6] [TEST-FIRST] Write unit tests `tests/unit/test_view_duplicate.py`: (a) node count equal; (b) connection count equal; (c) waypoint deep-copy (mutate copy → original unchanged); (d) name override; (e) default name suffix " (copy)"; (f) duplicate registered in model.views — confirm all FAIL
- [ ] P2-T52 [P] [US6] [TEST-FIRST] Write edge-case tests: (a) empty view; (b) view with no connections; (c) duplicate-of-duplicate; (d) zero-waypoint connections; (e) `model=None` → `ValueError` raised — confirm FAIL
- [ ] P2-T53 [P] [US6] [TEST-FIRST] Write integration test `tests/integration/test_view_duplicate.py`: load `.archimate`, duplicate a view, save, reload — both views present with correct element counts (round-trip) — confirm FAIL
- [ ] P2-T50 [US6] Implement `View.duplicate(self, name: str | None = None) -> "View"` in `src/pyArchimate/view.py`: raise `ValueError("View has no parent model; cannot register duplicate")` if `self.model is None`; deep-copy nodes + connections (waypoints + labels); assign new UUID; set name or append " (copy)"; register in `self.model.views` — P2-T51/T52/T53 should pass
- [ ] P2-T54 [P] [US6] Write BDD scenario `features/view/view_duplicate.feature`: Given view with 5 nodes + 4 connections, When `view.duplicate("test")` called, Then new view has 5 nodes + 4 connections + name "test"

---

## Phase 2I: ObstacleMap Rebuild for Node Move (M3) — PENDING

**Goal**: After a tentative node repositioning (FR-023), the `ObstacleMap` is updated to reflect the node's new position before re-routing affected connections.

*Depends on Phase 2E (P2-T33) being complete — ObstacleMap already uses node_clearance inflation.*

- [ ] P2-T55 [US5] Implement `ObstacleMap.rebuild_for_moved_nodes(moved_nodes: list[Node], config: RoutingConfig) -> None` in `src/pyArchimate/layout/auto_route.py`: for each moved node, remove old inflated AABB cells from `cells`; compute new inflated AABB at new position; add new cells. Update `_apply_node_move` (P2-T25) to call this before re-routing affected connections. Write unit test: after a 1-cell node move, old AABB cells cleared and new AABB cells present in `ObstacleMap.cells`.

---

## Overview (Phase 1)

Separate node-arrangement (`auto_layout`) and connection-routing (`auto_route`) into independent public functions. Enhance grid snapping (coarse 120px), layer ordering, obstacle avoidance, segment separation, proportional corner clearance, and skip-and-warn for unroutable connections.

**Total Tasks**: 61 tasks across 7 phases
**Estimated Duration**: ~3–4 days
**Scope**: All phases required for full feature delivery; US1 alone is a usable MVP

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: User story this task belongs to
- TDD: write test first (stub), confirm it fails, implement, confirm it passes

---

## Implementation Strategy

### MVP Scope
**US1 only** (phases 1–3): Delivers `auto_layout()` with coarse grid + layer ordering. Independently verifiable without routing.

### Phase Execution Order

```
Phase 1 (setup)
    ↓
Phase 2 (foundational: RoutingConfig, LayoutResult.warnings, ObstacleMap)
    ↓
Phase 3 (US1: auto_layout)  ←—can start after Phase 2
Phase 4 (US2: auto_route)   ←—depends on Phase 2 + obstacle map (T012)
    ↓
Phase 5 (US3: chain + independence tests)
    ↓
Phase 6 (US4: config validation + customization)
    ↓
Phase 7 (polish: backward-compat, BDD, docs)
```

### Parallel Execution within Phases

- **Phase 3**: T021–T025 (test stubs) can run in parallel with each other; T026–T031 can run in parallel after test stubs
- **Phase 4**: T033–T037 (test stubs) in parallel; T038–T043 in parallel after stubs
- **Phase 6**: T047–T049 all parallelizable

---

## Phase 1: Setup

**Purpose**: Verify repo structure matches plan; create new empty files.

- [x] T001 Create empty `src/pyArchimate/view/layout/layout_engine.py` with module docstring
- [x] T002 [P] Create empty `src/pyArchimate/view/layout/routing/obstacle_map.py` with module docstring
- [x] T003 [P] Create empty `src/pyArchimate/view/layout/routing/segment_separation.py` with module docstring
- [x] T004 [P] Create empty `tests/unit/view/layout/test_auto_layout.py`
- [x] T005 [P] Create empty `tests/unit/view/layout/test_auto_route.py`
- [x] T006 [P] Create empty `tests/unit/view/layout/test_routing_config.py`
- [x] T007 [P] Create empty `tests/unit/view/layout/test_result_warnings.py`
- [x] T008 [P] Create empty `tests/integration/test_layout_route_independence.py`
- [x] T009 [P] Create empty `tests/integration/test_layout_route_chain.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Data model changes and `ObstacleMap` that all user story phases depend on.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

### 2A — RoutingConfig and LayoutResult.warnings

- [x] T010 Write failing tests for `RoutingConfig` in `tests/unit/view/layout/test_routing_config.py`: valid defaults, validation rejects `min_segment_gap < 0`, rejects `corner_clearance_pct > 0.50`, rejects `corner_clearance_pct <= 0`, rejects `corner_clearance_min < 0`
- [x] T011 Write failing tests for `LayoutResult.warnings` in `tests/unit/view/layout/test_result_warnings.py`: field exists with default `[]`, can append warning strings, does not mutate across instances
- [x] T012 Add `RoutingConfig` dataclass to `src/pyArchimate/view/layout/core.py` with fields: `min_segment_gap: float = 10.0`, `corner_clearance_pct: float = 0.10`, `corner_clearance_min: float = 4.0`, `crossing_penalty: float = 1.0`; add `__post_init__` validation per data-model.md rules
- [x] T013 Add `warnings: list[str] = field(default_factory=list)` to `LayoutResult` in `src/pyArchimate/view/layout/core.py`
- [x] T014 Change `LayoutConfig.grid_size` default from `10.0` to `120.0` and `alignment` default from `"free"` to `"grid"` in `src/pyArchimate/view/layout/core.py`
- [x] T015 Add `layer_direction: str = "vertical"` field to `LayoutConfig` in `src/pyArchimate/view/layout/core.py`; validate: only `"vertical"` or `"horizontal"` accepted
- [x] T016 Export `RoutingConfig` from `src/pyArchimate/view/layout/__init__.py` `__all__` list
- [x] T017 Verify T010–T011 tests now pass; fix any issues

### 2B — ObstacleMap

- [x] T018 Write failing tests for `ObstacleMap` in `tests/unit/view/layout/test_obstacle_map.py` (create file): (a) node bounding box cells are blocked after construction; (b) `segment_blocked` returns `True` when segment passes through node; (c) `find_corridor` returns `None` when no orthogonal path exists; (d) `find_corridor` returns valid orthogonal waypoint list when path exists; (e) `find_corridor` path does not pass through any blocked cell
- [x] T019 Implement `ObstacleMap` class in `src/pyArchimate/view/layout/routing/obstacle_map.py`: constructor takes list of `Rectangle` (node bboxes) + `resolution=10.0`; inflates each by 2px; rasterizes to `cells: set[tuple[int,int]]`; implement `is_blocked(x,y)`, `segment_blocked(p1,p2)`, `find_corridor(start,end)` using BFS on grid (orthogonal moves only)
- [x] T020 Verify T018 tests pass; fix any issues

**Checkpoint**: Foundation complete — US1 and US2 phases can begin.

---

## Phase 3: User Story 1 — Auto-Layout (Priority: P1) 🎯 MVP

**Goal**: `auto_layout(view, config=None)` repositions nodes in ArchiMate layer order on coarse grid; never touches connection waypoints.

**Independent Test**: Call `auto_layout` on a view with Business, Application, and Technology nodes at random positions. Verify: (a) all node (x,y) origins are multiples of `grid_size`; (b) max Business Y < min Application Y < min Technology Y; (c) no two nodes share a grid cell; (d) all connection waypoints are identical to pre-call state.

- [x] T021 Write failing test: `auto_layout` snaps all node origins to multiples of `LayoutConfig.grid_size` in `tests/unit/view/layout/test_auto_layout.py`
- [x] T022 [P] Write failing test: `auto_layout` vertical mode — all Business nodes Y < all Application nodes Y < all Technology nodes Y
- [x] T023 [P] Write failing test: `auto_layout` horizontal mode — all Business nodes X < all Application nodes X < all Technology nodes X
- [x] T024 [P] Write failing test: no two nodes overlap (bounding boxes do not intersect) after `auto_layout`
- [x] T025 [P] Write failing test: `auto_layout` does not modify any connection waypoints (SC-010); capture all waypoints before call, compare after
- [x] T026 Implement layer classification helper in `src/pyArchimate/view/layout/layout_engine.py`: `get_layer_priority(element_type: str) -> int` using ArchiMate category lookup; returns 0–6 per data-model.md layer table; unknown types return 6
- [x] T027 [P] Implement grid-cell assignment in `src/pyArchimate/view/layout/layout_engine.py`: `assign_grid_cells(nodes, grid_size, layer_direction) -> dict[node_id, tuple[int,int]]`; groups nodes by layer priority; assigns cells in row-major order within each layer band; resolves collisions by advancing to next free cell in row-major order
- [x] T028 [P] Implement `apply_node_positions(view, cell_assignments, grid_size, margin)` in `src/pyArchimate/view/layout/layout_engine.py`: writes (x, y) to each node from cell assignment; adds `margin` offset; does not touch width/height
- [x] T029 Add `auto_layout(view, config: LayoutConfig | None = None) -> LayoutResult` to `src/pyArchimate/view/layout/__init__.py`: builds config if None; calls `assign_grid_cells` then `apply_node_positions`; returns `LayoutResult` with `algorithm_used="auto_layout"`, correct counts, empty warnings if no issues
- [x] T030 [P] Write failing test: `auto_layout` idempotent — calling twice produces same node positions
- [x] T031 [P] Write failing test: `auto_layout` on empty view returns success with zero counts and no error
- [x] T032 Verify all Phase 3 tests pass (T021–T031); fix any issues; confirm SC-001 (< 2s for 500 nodes) with a perf smoke test using a programmatically generated fixture of 500 `BusinessObject` nodes in `tests/unit/view/layout/test_auto_layout.py` (generate nodes with `mock_node(id, layer)` helper, assert completion under 2000ms)

---

## Phase 4: User Story 2 — Auto-Routing (Priority: P1)

**Goal**: `auto_route(view, config=None)` recomputes all connection paths as obstacle-avoiding orthogonal polylines; never touches node positions; skips unroutable connections with warning.

**Independent Test**: Call `auto_route` on a view with connections passing through nodes. Verify: (a) no segment intersects any node bounding box; (b) no segment overlaps any connection label bbox; (c) collinear segments of different connections separated ≥ 10px; (d) skipped connection has preserved waypoints + warning in result; (e) no node position changed.

- [x] T033 Write failing test: no connection segment intersects any node bounding box after `auto_route` in `tests/unit/view/layout/test_auto_route.py`
- [x] T033b [P] Write failing test: no connection segment overlaps any connection label bounding box after `auto_route` (SC-007 / FR-014) in `tests/unit/view/layout/test_auto_route.py`; use a fixture connection with a label bbox that overlaps a naive straight-line path
- [x] T034 [P] Write failing test: `auto_route` does not modify any node position (SC-010)
- [x] T035 [P] Write failing test: collinear segments from different connections displaced ≥ `min_segment_gap` (default 10px)
- [x] T036 [P] Write failing test: unroutable connection — waypoints preserved, warning added to result, other connections still routed
- [x] T037 [P] Write failing test: endpoint corner clearance — no endpoint within `max(edge × 0.10, 4px)` of corner
- [x] T038 Implement `compute_corner_clearance(edge_length, pct, min_px) -> float` in `src/pyArchimate/view/layout/utils/geometry.py`
- [x] T039 [P] Implement `detect_collinear_overlaps(segments: list) -> list[tuple]` in `src/pyArchimate/view/layout/routing/segment_separation.py`: returns pairs of segments that are collinear and overlapping
- [x] T040 [P] Implement `displace_collinear_segments(overlapping_pairs, min_gap) -> dict[segment_id, offset]` in `src/pyArchimate/view/layout/routing/segment_separation.py`: computes perpendicular offset for each segment in each overlapping pair
- [x] T041 Refactor `_route_single_connection` in `src/pyArchimate/view/layout/__init__.py` to use `ObstacleMap.find_corridor` for path finding; if `find_corridor` returns `None`: preserve existing waypoints, return `(skipped=True, conn_id)`; also check each routed segment against all connection label bboxes and re-route if overlap found
- [x] T041b Implement crossing-aware path cost in `ObstacleMap.find_corridor` in `src/pyArchimate/view/layout/routing/obstacle_map.py`: track already-routed connection segments in a `routed_segments` set; when BFS evaluates a cell, add `crossing_penalty` (from `RoutingConfig`) to its cost if that cell crosses a routed segment; BFS therefore prefers paths with fewer crossings (FR-016)
- [x] T042 Add `auto_route(view, config: RoutingConfig | None = None) -> LayoutResult` to `src/pyArchimate/view/layout/__init__.py`: builds config if None; builds `ObstacleMap` from view nodes; calls routing per connection passing `config.crossing_penalty`; collects skipped connections as warnings; runs segment separation post-pass; returns `LayoutResult` with `algorithm_used="auto_route"`, correct counts, warnings list
- [x] T043 Write failing test: `auto_route` on view with no connections returns success, zero connections processed, empty warnings; node positions unchanged
- [x] T044 Verify all Phase 4 tests pass (T033–T043b); fix any issues; confirm SC-005 (< 3s for 500 nodes / 1000 connections) with a perf smoke test using a programmatically generated fixture of 500 nodes and 1000 connections in `tests/unit/view/layout/test_auto_route.py` (generate with `mock_node` + `mock_connection` helpers, assert completion under 3000ms)

---

## Phase 5: User Story 3 — Chain Layout then Routing (Priority: P2)

**Goal**: Calling `auto_layout(view)` then `auto_route(view)` produces a view satisfying both US1 and US2 criteria simultaneously. Functions compose correctly.

**Independent Test**: Apply `auto_layout` then `auto_route` to a view with 50+ nodes and 100+ connections. Verify all US1 and US2 acceptance criteria simultaneously. Then call `auto_layout` again and verify node positions are stable (idempotent).

- [x] T045 [US3] Write integration test: chain `auto_layout` + `auto_route` on a realistic fixture view; assert all SC-001–SC-010 criteria in `tests/integration/test_layout_route_chain.py`
- [x] T046 [P] [US3] Write integration test: non-interference — call `auto_layout` only and capture waypoints; call `auto_route` only and capture node positions; verify neither function touched the other's domain in `tests/integration/test_layout_route_independence.py`
- [x] T047 [P] [US3] Write integration test: idempotency — call `auto_layout` twice; node positions identical on both calls
- [x] T048 [US3] Verify T045–T047 pass; fix composition issues if any (e.g., stale obstacle map after layout)

---

## Phase 6: User Story 4 — Configure Layout and Routing Behavior (Priority: P3)

**Goal**: Both functions accept optional config objects; custom `grid_size`, `layer_direction`, `min_segment_gap`, `corner_clearance_pct` behave as specified.

**Independent Test**: Pass `LayoutConfig(grid_size=80)` to `auto_layout`; verify all node origins are multiples of 80. Pass `RoutingConfig(min_segment_gap=20)` to `auto_route`; verify all parallel segments separated ≥ 20px.

- [x] T049 [P] [US4] Write unit test: `auto_layout` with `grid_size=80` snaps all nodes to multiples of 80 in `tests/unit/view/layout/test_auto_layout.py`
- [x] T050 [P] [US4] Write unit test: `auto_layout` with `layer_direction="horizontal"` — Business X < Application X < Technology X
- [x] T051 [P] [US4] Write unit test: `auto_route` with `RoutingConfig(min_segment_gap=20)` — parallel segments separated ≥ 20px
- [x] T052 [US4] Verify T049–T051 pass; fix config propagation if needed

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Backward compatibility, BDD acceptance tests, `__all__` exports, docstrings, existing test suite regression check.

- [x] T053 Update `apply_layout()` in `src/pyArchimate/view/layout/__init__.py` to call `auto_layout(view, config)` then `auto_route(view, routing_config)` internally; construct `routing_config = RoutingConfig()` using `LayoutConfig` fields where applicable (e.g., preserve `routing_style` from config via a `min_segment_gap` default mapping); merge both `LayoutResult` objects (sum counts, merge warnings); return combined result
- [x] T054 Verify existing `tests/integration/test_layout_api.py` and `tests/integration/test_layout_round_trip.py` pass without modification (backward compat)
- [x] T055 [P] Export `auto_layout`, `auto_route`, `RoutingConfig` in `src/pyArchimate/view/layout/__init__.py` `__all__`
- [x] T056 [P] Add Google-style docstrings to `auto_layout`, `auto_route`, `RoutingConfig`, `ObstacleMap` public methods
- [x] T057 [P] Create BDD feature file `tests/features/layout/auto_route.feature` with scenarios for: obstacle avoidance, segment separation, skip-and-warn, endpoint corner clearance
- [x] T058 [P] Implement BDD step definitions in `tests/features/layout/auto_route_steps.py`
- [x] T059 Run full test suite (`pytest` + `behave`); fix any regressions; confirm all 61 tasks complete

---

## Dependencies (User Story completion order)

```
Phase 2 (Foundation)
    ├── Phase 3 (US1 — auto_layout)
    ├── Phase 4 (US2 — auto_route, needs ObstacleMap from Phase 2B)
    └── (US1 + US2 both complete)
            ↓
        Phase 5 (US3 — chain + independence)
            ↓
        Phase 6 (US4 — config customization)
            ↓
        Phase 7 (Polish)
```

**US1 and US2 can be developed in parallel** once Phase 2 is complete.

---

## Summary

| Phase | Tasks | Story | Parallelizable |
|-------|-------|-------|----------------|
| 1 — Setup | T001–T009 | — | 8 of 9 |
| 2 — Foundation | T010–T020 | — | partial |
| 3 — US1 Auto-Layout | T021–T032 | US1 (P1) | 8 of 12 |
| 4 — US2 Auto-Routing | T033–T044 (+T033b, T041b) | US2 (P1) | 9 of 14 |
| 5 — US3 Chain | T045–T048 | US3 (P2) | 4 of 4 |
| 6 — US4 Config | T049–T052 | US4 (P3) | 3 of 4 |
| 7 — Polish | T053–T059 | — | 4 of 7 |

**Total**: 61 tasks | **MVP** (US1 only): T001–T032