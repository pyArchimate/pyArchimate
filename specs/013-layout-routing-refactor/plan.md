# Implementation Plan: Auto-Layout and Auto-Routing Separation

**Branch**: `013-layout-routing-refactor` | **Date**: 2026-05-11 | **Spec**: [spec.md](spec.md)

## Summary

Refactor the existing `apply_layout()` function in `src/pyArchimate/view/layout/` to separate node arrangement (`auto_layout`) and connection routing (`auto_route`) into independent public functions. Enhance `auto_layout` with coarse-grid snapping (120px default) and row-major collision resolution. Enhance `auto_route` with real obstacle avoidance, 10px segment separation, proportional corner clearance, and skip-and-warn for unroutable connections.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: stdlib only (no new external deps); existing `lxml`, `pytest`, `behave`  
**Storage**: N/A (in-memory view objects; no file I/O in these functions)  
**Testing**: pytest (unit + integration), behave (BDD acceptance scenarios)  
**Target Platform**: platform-independent library  
**Project Type**: library  
**Performance Goals**: `auto_layout` < 2s / 500 nodes; `auto_route` < 3s / 500 nodes + 1000 connections  
**Constraints**: No new external dependencies; backward-compat wrapper for existing `apply_layout()` callers  
**Scale/Scope**: Up to 500 nodes, 1000 connections per view

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | ✅ Pass | Functions under 30 lines; SOLID; no magic numbers |
| II. Testing Standards | ✅ Pass | TDD; unit + integration + BDD scenarios required |
| III. UX Consistency | ✅ Pass | Result object pattern preserved; warning field added |
| IV. Performance | ✅ Pass | Explicit time targets in spec (SC-001, SC-005) |
| V. Security | ✅ Pass | Pure computation; no I/O, no user input at boundaries |
| VI. State Management | ✅ Pass | Functions are stateless transforms; no side effects beyond view mutation |
| VII. System Integrity | ✅ Pass | SC-010 verifies non-interference between the two functions |
| VIII. Durability | ✅ Pass | Backward-compat wrapper preserves existing callers |
| IX. Cross-Platform | ✅ Pass | Pure Python stdlib; no platform-specific code |

**Complexity Tracking**: No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/013-layout-routing-refactor/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code

```text
src/pyArchimate/view/layout/
├── __init__.py                  # Add auto_layout(), auto_route(); keep apply_layout() wrapper
├── core.py                      # Add RoutingConfig, add warnings: list[str] to LayoutResult
├── layout_engine.py             # NEW: pure node-arrangement logic (grid snap, layer sort, collision)
├── routing_engine.py            # NEW: pure connection-routing logic (obstacle avoidance, separation)
├── routing/
│   ├── orthogonal.py            # ENHANCE: add obstacle-aware A*/corridor routing
│   ├── obstacle_map.py          # NEW: grid-inflated obstacle map builder
│   ├── segment_separation.py    # NEW: collinear segment detection and displacement
│   └── label_placement.py       # ENHANCE: extend for routing clearance checks
└── utils/
    └── geometry.py              # ENHANCE: add bounding-box intersection, edge-zone helpers

tests/
├── unit/view/layout/
│   ├── test_auto_layout.py      # NEW: grid snapping, layer order, collision resolution
│   ├── test_auto_route.py       # NEW: obstacle avoidance, segment separation, skip-warn
│   ├── test_routing_config.py   # NEW: RoutingConfig validation
│   └── test_result_warnings.py  # NEW: warning accumulation in result object
├── integration/
│   ├── test_layout_route_independence.py  # NEW: SC-010 non-interference test
│   └── test_layout_route_chain.py         # NEW: US3 chained call correctness
└── features/layout/
    ├── auto_layout.feature       # UPDATE: add grid-snap and layer-order scenarios
    └── auto_route.feature        # NEW: obstacle, separation, skip-warn BDD scenarios
```

---

## Phase 0: Research

See [research.md](research.md).

---

## Phase 1: Design & Contracts

See [data-model.md](data-model.md) and [quickstart.md](quickstart.md).

---

## Phase 2: Implementation Phases

### Phase A — Data Model & Config (prerequisite for all other phases)

**Goal**: Extend `LayoutResult` with `warnings`, add `RoutingConfig`, adjust `LayoutConfig` defaults.

**Files**:
- `src/pyArchimate/view/layout/core.py`

**Changes**:
1. Add `warnings: list[str]` field to `LayoutResult` (default `field(default_factory=list)`)
2. Add `RoutingConfig` dataclass:
   ```python
   @dataclass
   class RoutingConfig:
       min_segment_gap: float = 10.0        # px between collinear segments
       corner_clearance_pct: float = 0.10   # 10% of edge length
       corner_clearance_min: float = 4.0    # absolute floor in px
       crossing_penalty: float = 1.0        # relative weight for crossing minimization
   ```
3. Add `__post_init__` validation to `RoutingConfig`
4. Update `LayoutConfig.grid_size` default from `10.0` → `120.0` (coarse grid = node width)
5. Add `layer_direction: str = "vertical"` to `LayoutConfig` (values: `"vertical"`, `"horizontal"`)

**Tests (TDD — write first)**:
- `tests/unit/view/layout/test_routing_config.py`: validation, defaults, invalid values
- `tests/unit/view/layout/test_result_warnings.py`: warnings field exists, accumulates, serializes

---

### Phase B — Auto-Layout Engine (grid snap + layer order + collision)

**Goal**: Extract and enhance node-arrangement logic into `layout_engine.py`.

**Files**:
- `src/pyArchimate/view/layout/layout_engine.py` (new)
- `src/pyArchimate/view/layout/__init__.py` (add `auto_layout()`)

**Algorithm** (row-per-layer, coarse grid):
1. Group nodes by ArchiMate layer (Business → App → Tech → other)
2. Within each layer group, assign nodes to grid cells in reading order
3. Grid cell = (col × grid_size, layer_row × (grid_size + row_gap))
4. Collision: if cell occupied, advance to next cell in row-major order (right then next row)
5. Snap: node.x = col × grid_size, node.y = layer_band_start + row × grid_size

**Public API**:
```python
def auto_layout(view, config: LayoutConfig | None = None) -> LayoutResult
```
- Does NOT call any routing function
- Returns `LayoutResult` with `warnings` for any nodes that could not be placed

**Tests (TDD — write first)**:
- `tests/unit/view/layout/test_auto_layout.py`:
  - Grid snapping: all node origins are multiples of grid_size
  - Layer ordering: Business Y < Application Y < Technology Y (vertical mode)
  - Horizontal mode: Business X < Application X < Technology X
  - Collision resolution: no two nodes occupy same grid cell after layout
  - Row-major fill: second node shifts right, wraps to next row when row full
  - Idempotency: calling twice produces same result
  - No-node view: returns success, empty warnings
  - Waypoints unchanged: connection waypoints not modified by `auto_layout`

---

### Phase C — Obstacle Map (prerequisite for routing enhancement)

**Goal**: Build a rasterized obstacle map from node bounding boxes for use by routing.

**Files**:
- `src/pyArchimate/view/layout/routing/obstacle_map.py` (new)

**Design**:
- Inflate each node bounding box by a small margin (default 2px) to create clearance
- Provide a `is_blocked(segment: tuple) -> bool` query
- Provide a `find_corridor(start, end) -> list[Point] | None` that returns an orthogonal path or `None` if no path found

**Tests**:
- `tests/unit/view/layout/test_obstacle_map.py`:
  - Node bounding box blocks path through it
  - Corridor path returned when clear route exists
  - Returns `None` when no orthogonal path possible

---

### Phase D — Routing Engine (obstacle avoidance + segment separation + skip-warn)

**Goal**: Refactor `_apply_orthogonal_routing` into a public `auto_route()` with real obstacle avoidance and segment separation.

**Files**:
- `src/pyArchimate/view/layout/routing/orthogonal.py` (enhance)
- `src/pyArchimate/view/layout/routing/segment_separation.py` (new)
- `src/pyArchimate/view/layout/__init__.py` (add `auto_route()`)

**Algorithm**:
1. Build obstacle map from all nodes
2. Compute corner clearance per edge: `max(edge_length × 0.10, 4.0)`
3. For each connection:
   a. Determine departure/arrival edge using `_preferred_boundary_side`
   b. Compute spread offset using proportional corner clearance
   c. Call `find_corridor(source_anchor, target_anchor, obstacle_map)` → waypoints
   d. If `None`: skip connection, preserve existing waypoints, add warning to result
4. Post-routing: detect collinear segment overlaps → displace by `min_segment_gap`
5. Return `LayoutResult` with warnings for skipped connections

**Public API**:
```python
def auto_route(view, config: RoutingConfig | None = None) -> LayoutResult
```
- Does NOT move any nodes
- Skips unroutable connections with warning (FR-019)

**Tests (TDD — write first)**:
- `tests/unit/view/layout/test_auto_route.py`:
  - No segment intersects node bounding box after routing
  - No segment overlaps connection label bounding box
  - Collinear segments displaced by ≥ 10px
  - Corner clearance proportional: endpoint not within `max(10% edge, 4px)` of corner
  - Unroutable connection: skipped, waypoints preserved, warning in result
  - No node positions changed after `auto_route`
  - Endpoints evenly spread on edges with multiple connections

---

### Phase E — Backward Compatibility

**Goal**: Keep `apply_layout()` working as before (calls `auto_layout` then `auto_route` internally).

**Files**:
- `src/pyArchimate/view/layout/__init__.py`

**Change**: Update `apply_layout()` to call `auto_layout(view, config)` then `auto_route(view)` and merge results.

**Tests**:
- `tests/integration/test_layout_api.py` (existing): must still pass without modification

---

### Phase F — Integration & BDD

**Goal**: Validate US3 (chain) and SC-010 (non-interference).

**Files**:
- `tests/integration/test_layout_route_independence.py` (new)
- `tests/integration/test_layout_route_chain.py` (new)
- `tests/features/layout/auto_route.feature` (new)

**Key tests**:
- `test_layout_route_independence`: after `auto_layout` only, all waypoints unchanged; after `auto_route` only, all node positions unchanged
- `test_layout_route_chain`: apply both, verify SC-001–SC-010 satisfaction
- BDD scenarios for obstacle avoidance and skip-warn behavior

---

## Execution Order

```
Phase A (config/result model)
    ↓
Phase B (auto_layout)  ←→  Phase C (obstacle map)   [can run in parallel]
    ↓                            ↓
Phase D (auto_route — depends on C)
    ↓
Phase E (backward compat — depends on B + D)
    ↓
Phase F (integration tests — depends on E)
```

## Deferred / Out of Scope

- Timeout/partial-completion behavior (Q5 from clarification, deferred): implement as best-effort with no hard timeout enforcement in MVP; document in Assumptions
- Undo/rollback: callers responsible (per spec Assumptions)
- `apply_format()`: unchanged in this feature
- Views > 500 nodes: out of scope for initial release
