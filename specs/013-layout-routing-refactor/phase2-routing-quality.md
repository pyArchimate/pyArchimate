# Phase 2: Routing Quality — Multi-Pass Routing and Layout Improvements

**Branch**: `013-layout-routing-refactor`  
**Created**: 2026-05-11  
**Depends on**: Phase 1 complete (all 61 tasks done)  
**Objective**: Eliminate the six routing quality gaps identified in Phase 1 (RQ-01 through RQ-06).

---

## Gap inventory

| ID | Symptom | Root cause | Fix category |
|----|---------|------------|--------------|
| RQ-01 | ~6 U-turn connections (opposite-direction segments on same axis) | Displacement pass modifies shared corner points of the same connection via two independent clusters; the combined offset creates a backtrack | Path cleanup |
| RQ-02 | Redundant bendpoints (consecutive collinear segments, no turn) | BFS path compression misses the case where the L-turn connector and subsequent BFS segment are on the same axis | Path cleanup |
| RQ-03 | Connections crossing through nodes | Single-pass BFS: corridor saturation forces some connections to fall back to penalty=0, which ignores routed-path penalties and may find an obstacle-grazing path | Multi-pass routing |
| RQ-04 | Double crossings (same two connections cross twice) | Single-pass routing makes locally-optimal decisions without awareness of future connections; loop-free detour exists but is not explored | Multi-pass routing |
| RQ-05 | Layout spacing too tight | `grid_size=160` with 120px nodes leaves only 40px gap — 4 BFS cells — far too few for 6-10 connections routing through the same inter-node gap | Layout config |
| RQ-06 | Highly-connected nodes not isolated to own row | `assign_grid_cells` assigns row by layer only; nodes with degree ≥ N connections create bottlenecks when packed into the same row as other nodes | Layout algorithm |

---

## Fix 1 — Path cleanup: remove remaining U-turns (RQ-01)

### Status
`remove_uturn_waypoints()` was added in Phase 1 and eliminates most U-turns. Approximately 6 remain in the tutorial topology.

### Remaining cause
The displacement pass shifts waypoints of a connection that belongs to TWO separate overlap clusters (e.g. a horizontal cluster and a vertical cluster sharing a corner point). The first cluster shifts the corner in y; the second shifts the same corner in x. The `remove_uturn_waypoints` function then sees a diagonal step at that corner and cannot classify it as a U-turn (it is not collinear). The result is a near-diagonal micro-segment.

### Plan
1. Detect connections involved in multiple displacement clusters before applying offsets.
2. For such connections: apply horizontal cluster offsets only; skip vertical cluster displacement for that connection (let the anchor-restoration + safety-check revert if needed). This prevents the double-shift.
3. Alternatively: after applying all displacements, run a "merge collinear adjacent segments" pass that collapses A→B→C into A→C when AB and BC are on the same axis and in the same direction (even if B was introduced by different clusters).

**Acceptance**: zero U-turns in the tutorial topology and in the 500-node performance test.

---

## Fix 2 — Path cleanup: remove redundant intermediate bendpoints (RQ-02)

### Description
After L-turn insertion and displacement, some connections contain three or more consecutive waypoints on the same axis with no direction change, e.g. `(x=180, y=408) → (x=180, y=420) → (x=180, y=450)`. These are valid but wasteful — the middle point carries no geometric information.

### Plan
Add `_merge_collinear_adjacent(wps: list[Point]) -> list[Point]` to `segment_separation.py`. It collapses any run of 3+ waypoints on the same axis into 2 (the first and last of the run). Call it from `auto_route` immediately after `remove_uturn_waypoints`.

```
for i in range(1, len(pts) - 1):
    prev, cur, nxt = result[-1], pts[i], pts[i+1]
    # cur is collinear AND same direction as prev→cur and cur→nxt
    if same_axis(prev, cur, nxt) and same_direction(prev, cur, nxt):
        skip cur
```

**Acceptance**: no connection has two consecutive segments on the same axis in the tutorial topology.

---

## Fix 3 — Multi-pass routing: eliminate node crossings and double crossings (RQ-03, RQ-04)

### Architecture

Replace the current single-pass BFS routing loop with a multi-pass loop:

```
Pass 0: route all connections with penalty=0 (fastest; fills the obstacle map)
Pass 1: re-route connections whose path still crosses a node OR crosses another
        connection more than once, this time with penalty = crossing_penalty
        (now all Pass-0 paths act as soft obstacles)
Pass 2: re-route any connections that still have crossings after Pass 1,
        with higher penalty = crossing_penalty * 3
        (if still unresolvable: accept result, add warning)
Convergence check: stop when no new conflicts are detected or after max_passes=3
```

### Conflict detection

After each pass, classify each connection:
- **Node crossing**: any segment passes strictly through a node bounding box → must re-route
- **Double crossing**: connection A and connection B cross at two distinct points → at least one must re-route (choose the one with the longer detour to fix)
- **Collinear overlap after displacement**: handled by displacement pass (existing)

### Implementation changes

1. Extract current single routing loop into `_route_pass(conns, om, config, warnings) -> list[list[Point]]`.
2. Add `_detect_node_crossings(waypoints, nodes_dict) -> set[int]` (connection indices).
3. Add `_detect_double_crossings(waypoints) -> set[int]` (connection indices to re-route).
4. Add outer loop in `auto_route`:
   ```python
   for pass_num in range(max_passes):
       waypoints = _route_pass(conflict_conns, om, config, warnings)
       conflicts = _detect_node_crossings(...) | _detect_double_crossings(...)
       if not conflicts:
           break
       conflict_conns = [conns[i] for i in conflicts]
       # mark existing paths as obstacles (higher penalty for Pass 2+)
   ```

### Obstacle map management across passes

Between passes, previously routed paths for non-conflicting connections remain in `om._routed`. Conflicting connections have their old paths un-marked (new `om.unmark_routed_segment` method) before re-routing.

### Performance

Multi-pass adds at most 2 extra routing passes for conflicting connections only. In typical diagrams (80-90% conflict-free after Pass 0), total extra work is < 20% overhead.

**Acceptance**: zero node crossings and zero double crossings in the tutorial topology (verified by existing SVG integration tests SC-006, FR-013).

---

## Fix 4 — Layout: increase default inter-node spacing (RQ-05)

### Problem
`LayoutConfig(grid_size=160)` with 120px nodes leaves 40px = 4 BFS cells between adjacent nodes. With 6+ connections per gap, corridor saturation is guaranteed in the application layer.

### Plan
- Increase default `grid_size` from 160 to **240** (120px node + 120px gap → 12 BFS cells per inter-node gap).
- Update `LayoutConfig` default and all tests that rely on the 160px default.
- Document the reasoning: gap should be `≥ max_connections_per_gap × min_segment_gap × 1.5` where `max_connections_per_gap ≈ 8` and `min_segment_gap = 10px` → 120px gap minimum.

**Acceptance**: SC-002 passes with new default; performance test passes; tutorial topology has no corridor saturation.

---

## Fix 5 — Layout: promote high-degree nodes to own row (RQ-06)

### Problem
When a node has connections to/from many other nodes (degree ≥ threshold), routing through the same row creates bottlenecks. These nodes should be placed with extra horizontal isolation.

### Plan
1. In `assign_grid_cells`, compute degree for each node (count of connections in the view).
2. High-degree nodes (degree ≥ `layout_config.high_degree_threshold`, default = 5) are placed in their own sub-row: pad 1 grid column on each side and bump subsequent nodes to the next free slot.
3. Add `LayoutConfig.high_degree_threshold: int = 5` parameter.
4. This is a best-effort heuristic; do not alter layer ordering (Business/Application/Technology constraint is preserved).

**Acceptance**: in the tutorial topology, Order API (degree 5) and CRM (degree 4+) are not adjacent to each other in the same row.

---

## Task list

### Phase 2A — Path cleanup (RQ-01, RQ-02) — low risk, no architecture change

TDD order: diagnose/write failing tests first → implement fixes → verify green

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| P2-T01 | [TEST-FIRST] Investigate remaining ~6 U-turns: identify which connections and cluster combination cause them; add a debug assertion in the test to capture the exact failing cases — confirm FAIL | — | P1 |
| P2-T06 | [TEST-FIRST] Update `test_tutorial_svg_requirements.py`: strengthen U-turn check to zero remaining — confirm FAIL | — | P2 |
| P2-T05 | [TEST-FIRST] Update `test_tutorial_svg_requirements.py`: add `test_no_redundant_bendpoints` verifying zero consecutive-collinear segments — confirm FAIL | — | P2 |
| P2-T02 | Fix displacement: for connections in multiple clusters, apply only the dominant-axis displacement (skip secondary axis) or detect the double-shift and merge — P2-T01/T06 should now pass | — | P1 |
| P2-T03 | Add `_merge_collinear_adjacent()` to `segment_separation.py` — P2-T05 should now pass | — | P1 |
| P2-T04 | Wire `_merge_collinear_adjacent()` into `auto_route` post-processing pipeline | — | P1 |

### Phase 2B — Layout improvements (RQ-05, RQ-06) — medium risk

TDD order: write failing tests → implement default change → verify green

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| P2-T10 | [TEST-FIRST] Write unit test: `grid_size=240` — all nodes snapped to 240px grid — confirm FAIL (current default is 160) | — | P1 |
| P2-T11 | [TEST-FIRST] Write unit test: high-degree node (degree ≥ 5) gets at least 1 grid-cell isolation — confirm FAIL | — | P2 |
| P2-T07 | Change `LayoutConfig.grid_size` default from 160 to 240; update all tests hardcoding 160 — P2-T10 should pass | — | P1 |
| P2-T08 | Add `LayoutConfig.high_degree_threshold: int = 5` field | — | P2 |
| P2-T09 | Implement high-degree node row isolation in `assign_grid_cells` — P2-T11 should pass | — | P2 |

### Phase 2C — Multi-pass routing (RQ-03, RQ-04) — high complexity

TDD order: write failing tests → extract loop → add detection → implement multi-pass → verify green

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| P2-T18 | [TEST-FIRST] Write unit test: connection crossing a node is re-routed around it after multi-pass — confirm FAIL (single-pass may leave node crossing) | — | P1 |
| P2-T19 | [TEST-FIRST] Write unit test: double-crossing pair resolved (one connection re-routed) — confirm FAIL | — | P2 |
| P2-T20 | [TEST-FIRST] Write integration test: tutorial topology has zero node crossings (SC-006 always green) — confirm current state | — | P1 |
| P2-T21 | [TEST-FIRST] Write performance test: 500 nodes / 1000 connections routes in ≤ 3s (SC-005; all passes combined) — confirm FAIL if multi-pass not yet implemented | — | P1 |
| P2-T12 | Add `ObstacleMap.unmark_routed_segment(p1, p2)` method and `_routed` field | — | P1 |
| P2-T13 | Extract current routing loop into `_route_pass(conns, om, config, warnings)` | — | P1 |
| P2-T14 | Add `_detect_node_crossings(waypoints, nodes_dict: dict[str, InflatedAABB]) -> set[int]` — MUST use inflated AABB (depends on P2-T33); `InflatedAABB = raw AABB expanded by node_clearance` | — | P1 |
| P2-T15 | Add `_detect_double_crossings(waypoints) -> set[int]` | — | P1 |
| P2-T16 | Implement multi-pass outer loop in `auto_route` (max `config.max_routing_passes` passes) — P2-T18/T19/T20/T21 should now pass | — | P1 |
| P2-T17 | Add `RoutingConfig.max_routing_passes: int = 3` (implementation detail; no FR; see plan.md Assumptions) | — | P2 |

---

## Fix 6 — Routing-driven node repositioning (FR-023, RQ-07)

### Description

When all three routing passes fail to produce a crossing-free path for a connection (RQ-03), and `RoutingConfig.allow_node_move = True`, the router may shift a node (or a rigid block of nodes) by up to `max_node_displacement` grid cells along the routing axis to open a corridor. This is a last-resort mechanism, off by default.

### Key design decisions

| Decision | Rationale |
|----------|-----------|
| Off by default (`allow_node_move=False`) | Preserves SC-010 for all existing callers; opt-in only |
| Max 1 grid cell displacement | Prevents large layout disruptions; 1 cell ≈ inter-node gap |
| Layer constraint enforced | Moved node stays in original ArchiMate layer row |
| No-overlap check before applying move | Move is rejected if it would create a new node overlap |
| Block moves for tightly-coupled nodes | Nodes that share a sub-layout (e.g. a stack) move together to preserve legibility |
| Moves recorded in result | Caller can audit or undo; `NodeMove(uuid, old_x, old_y, new_x, new_y)` per moved node |

### Algorithm sketch

```
After all routing passes: collect connections still crossing a node (from _detect_node_crossings)
For each such connection:
  candidates = nodes that block the connection's corridor
  For each candidate node (or block):
    For each valid 1-cell direction (preserves layer, no overlap):
      Tentatively apply move
      Re-route the affected connections
      If crossing resolved AND no new node overlaps: accept move, record in result
      Else: undo tentative move
  If no move resolved the crossing: skip + warn (FR-019)
```

### Data model additions

```python
@dataclass
class NodeMove:
    uuid: str
    old_x: float
    old_y: float
    new_x: float
    new_y: float

# RoutingConfig additions:
allow_node_move: bool = False
max_node_displacement: int = 1  # in grid cells
```

The `LayoutResult.node_moves: list[NodeMove]` field records all moves applied.

### Phase 2D task list (TDD order: tests first → implementation → integration)

| ID | Task | Priority |
|----|------|----------|
| P2-T27 | [TEST-FIRST] Write unit test: `allow_node_move=False` (default) → no node position changes; SC-010 preserved — confirm FAIL | P1 |
| P2-T28 | [TEST-FIRST] Write unit test: single blocking node moved 1 cell to resolve corridor — confirm FAIL | P1 |
| P2-T29 | [TEST-FIRST] Write unit test: proposed move rejected when it would cause node overlap — confirm FAIL | P2 |
| P2-T30 | [TEST-FIRST] Write unit test: rigid block of 2 nodes moves together (same delta) — confirm FAIL | P2 |
| P2-T31 | [TEST-FIRST] Write integration test: `NodeMove` entries appear in result with correct old/new positions — confirm FAIL | P1 |
| P2-T22 | Add `NodeMove` dataclass to `core.py`; add `node_moves: list[NodeMove]` to `LayoutResult` | P1 |
| P2-T23 | Add `allow_node_move: bool = False` and `max_node_displacement: int = 1` to `RoutingConfig` | P1 |
| P2-T55 | Implement `ObstacleMap.rebuild_for_moved_nodes(moved_nodes, config)` — patch `cells` in-place: remove old inflated AABB, add new inflated AABB for moved node(s); call before re-routing affected connections after any node repositioning | P1 |
| P2-T24 | Implement `_find_candidate_node_moves(blocked_conn, waypoints, nodes_dict: dict[str, Node], config)` — returns `list[(node_or_block, delta_x, delta_y)]` candidates; uses inflated AABB for overlap check | P1 |
| P2-T25 | Implement `_apply_node_move(nodes_dict, candidate, view)` — shifts node(s), calls `rebuild_for_moved_nodes`, checks no-overlap, returns bool success | P1 |
| P2-T26 | Wire node-move fallback into multi-pass outer loop (after final pass, before skip+warn); run P2-T27–T31 to confirm green | P1 |

### Dependency

P2-T22 through P2-T31 depend on multi-pass routing (P2-T12–P2-T16) being in place, since node moves are triggered only when multi-pass fails to resolve a conflict.

---

## Fix 7 — Node avoidance zone: 25px clearance (FR-013 updated, SC-006)

### Description

FR-013 previously required only that no segment passes through the node bounding box. The updated requirement extends this to a **25px avoidance zone** around each node side: the routing algorithm must treat the AABB inflated by 25px as impassable.

### Implementation

`RoutingConfig` gains `node_clearance: int = 25`. `ObstacleMap` construction inflates each node AABB by `node_clearance` px on all four sides before rasterising grid cells. This is a constructor-time change; no BFS algorithm changes required.

### Phase 2E task list (TDD order: tests first → implementation → BDD)

| ID | Task | Priority |
|----|------|----------|
| P2-T34 | [TEST-FIRST] Write unit test `tests/unit/test_node_clearance.py`: segment grazing node edge (0px gap) blocked; segment at 24px blocked; segment at 26px passes — confirm tests FAIL before implementation | P1 |
| P2-T36 | [TEST-FIRST] Write unit test: `RoutingConfig(node_clearance=10)` produces 10px inflation (not 25px) — confirm FAIL | P2 |
| P2-T32 | Add `node_clearance: int = 25` to `RoutingConfig` in `src/pyArchimate/layout/routing_config.py` | P1 |
| P2-T33 | Update `ObstacleMap.__init__` in `src/pyArchimate/layout/auto_route.py` to inflate each node AABB by `config.node_clearance` on all four sides — P2-T34/T36 should now pass | P1 |
| P2-T35 | Update SC-006 + SC-007 assertions in `tests/integration/test_tutorial_svg_requirements.py`: check inflated AABB (25px) for clearance; verify label clearance still passes after inflation | P1 |
| P2-T37 | BDD scenario `features/routing/node_clearance.feature` — Given `node_clearance=25`, When `auto_route` called, Then 0 segments within 25px of any node side | P2 |

---

## Fix 8 — Increase default min_segment_gap to 20px (FR-015 updated, SC-008)

### Description

The default `min_segment_gap` increases from 10px to **20px** — wider separation is needed for readable diagrams at the default grid size.

### Implementation

Change the field default in `RoutingConfig`. The displacement post-pass already reads `config.min_segment_gap`; no algorithmic change required. Existing tests that assert 10px separation must be updated to 20px.

### Phase 2F task list (TDD order: tests first → implementation → BDD)

| ID | Task | Priority |
|----|------|----------|
| P2-T40 | [TEST-FIRST] Write unit test `tests/unit/test_segment_separation.py`: two collinear connections separate to ≥ 20px with default config — confirm FAIL (current default is 10px) | P1 |
| P2-T41 | [TEST-FIRST] Write unit test: `RoutingConfig(min_segment_gap=5)` → separation ≥ 5px — confirm FAIL | P2 |
| P2-T38 | Change `min_segment_gap` default from `10` to `20` in `RoutingConfig` — P2-T40/T41 should now pass | P1 |
| P2-T39 | Update all existing unit/integration tests that hardcode `min_segment_gap=10` or assert `≥ 10px` separation to use `20px` | P1 |
| P2-T42 | BDD scenario `features/routing/segment_gap.feature` — Given default config, When `auto_route` called, Then parallel segments ≥ 20px | P2 |

---

## Fix 9 — Post-L-turn minimum segment length: 40px (FR-024 new, SC-012)

### Description

After every 90° direction change (L-turn) in a routed connection, the immediately following segment MUST be at least `min_turn_segment` px (default 40px). This prevents cosmetically degenerate micro-steps near bends.

### Implementation

`RoutingConfig` gains `min_turn_segment: int = 40`. A new geometry helper `_enforce_min_turn_segment(waypoints, min_len)` post-processes each connection's waypoint list after BFS routing: if the segment after a 90° bend is shorter than `min_len`, it extends the segment by merging with the next point or inserting a push-out waypoint.

### Algorithm

```
for i in range(1, len(pts) - 1):
    prev, cur, nxt = pts[i-1], pts[i], pts[i+1]
    if direction(prev, cur) != direction(cur, nxt):   # L-turn at cur
        seg_len = dist(cur, nxt)
        if seg_len < min_len:
            # Extend nxt by (min_len - seg_len) in direction(cur, nxt)
            pts[i+1] = push(nxt, direction(cur, nxt), min_len - seg_len)
```

Run after `_merge_collinear_adjacent` and before `_fix_u_turns` to avoid invalidating the U-turn detector.

**⚠️ M6 — Second enforce pass required**: `_fix_u_turns` can shorten a post-turn segment when it reroutes a backward segment. After `_fix_u_turns` completes, run `_enforce_min_turn_segment` a second time to catch any segments that became shorter than `min_turn_segment` as a result of the U-turn fix. The full post-processing pipeline order is:

```
_merge_collinear_adjacent → _enforce_min_turn_segment (pass 1) → _fix_u_turns → _enforce_min_turn_segment (pass 2) → _displace_collinear_overlaps
```

### Phase 2G task list (TDD order: tests first → implementation → BDD)

**Pipeline order** (M6 resolved): `_merge_collinear_adjacent → _enforce_min_turn_segment (pass 1) → _fix_u_turns → _enforce_min_turn_segment (pass 2) → _displace_collinear_overlaps`

**Terminal arrival segment exception** (M2 resolved): `_enforce_min_turn_segment` MUST skip the final segment (the one that terminates at the target node's attachment point) to avoid displacing the endpoint.

| ID | Task | Priority |
|----|------|----------|
| P2-T46 | [TEST-FIRST] Write unit tests `tests/unit/test_geometry.py` for `_enforce_min_turn_segment`: L-shape with 10px post-turn → extended to 40px; conforming path unchanged; two consecutive L-turns both enforced; terminal arrival segment NOT extended; single-segment no-op — confirm all FAIL | P1 |
| P2-T47 | [TEST-FIRST] Write unit test: `min_turn_segment=20` → 20px floor applied — confirm FAIL | P2 |
| P2-T48 | [TEST-FIRST] Write integration test `tests/integration/test_tutorial_svg_requirements.py`: SC-012 — all non-terminal post-turn segments ≥ 40px — confirm FAIL | P1 |
| P2-T43 | Add `min_turn_segment: int = 40` to `RoutingConfig` in `src/pyArchimate/layout/routing_config.py` | P1 |
| P2-T44 | Implement `_enforce_min_turn_segment(waypoints, min_len)` in `src/pyArchimate/layout/geometry.py`; skip terminal arrival segment (last segment); run P2-T46/T47 to confirm green | P1 |
| P2-T45 | Wire `_enforce_min_turn_segment` twice in pipeline (pass 1: after `_merge_collinear_adjacent`; pass 2: after `_fix_u_turns`) in `src/pyArchimate/layout/auto_route.py`; run P2-T48 to confirm green | P1 |
| P2-T49 | BDD scenario `features/routing/turn_segment.feature` — Given `min_turn_segment=60`, When `auto_route` called, Then all non-terminal post-turn segments ≥ 60px | P2 |

---

## Fix 10 — View.duplicate() deep copy (FR-025 new, SC-013)

### Description

A new method `View.duplicate(name=None)` creates an independent deep copy of a view — all nodes, connections, and waypoints — and registers the new view in the same model. The original is never modified.

### Implementation

Added to `src/pyArchimate/view.py`. Deep-copies all nodes and connections using `copy.deepcopy`; assigns new UUIDs to the copy and its child objects; appends the new view to `self.model.views`.

### Phase 2H task list (TDD order: tests first → implementation → BDD)

**M4 resolved**: `View.duplicate()` raises `ValueError` when `self.model is None`; callers with standalone views must assign the result to a model explicitly. P2-T52 covers this edge case.

| ID | Task | Priority |
|----|------|----------|
| P2-T51 | [TEST-FIRST] Write unit tests `tests/unit/test_view_duplicate.py`: node count equality; connection count equality; waypoint deep-copy (mutate copy → original unchanged); name override; default name suffix " (copy)"; duplicate registered in model — confirm all FAIL | P1 |
| P2-T52 | [TEST-FIRST] Write edge-case tests: duplicate of empty view; view with no connections; duplicate-of-duplicate; zero-waypoint connections; `model=None` raises `ValueError` — confirm FAIL | P2 |
| P2-T53 | [TEST-FIRST] Write integration test `tests/integration/test_view_duplicate.py`: load `.archimate`, duplicate, save, reload — both views present with correct element counts — confirm FAIL | P1 |
| P2-T50 | Implement `View.duplicate(self, name: str \| None = None) -> "View"` in `src/pyArchimate/view.py`: raise `ValueError` if `self.model is None`; deep-copy nodes + connections (waypoints + labels); assign new UUID; set `name` or append " (copy)"; register in `self.model.views`; run P2-T51/T52/T53 to confirm green | P1 |
| P2-T54 | BDD scenario `features/view/view_duplicate.feature` — Given view with 5 nodes + 4 connections, When `view.duplicate("test")` called, Then new view has 5 nodes + 4 connections + name "test" | P2 |

---

## Recommended execution order (TDD-compliant)

**Rule**: within each group, write tests (confirm FAIL) → implement → confirm tests green.

1. **P2-T10, P2-T07** (layout grid_size) — write test, change default
2. **P2-T34, P2-T36, P2-T32, P2-T33, P2-T35** (node_clearance) — test → field → inflate AABB → integration check; **prerequisite for P2-T14**
3. **P2-T40, P2-T41, P2-T38, P2-T39** (min_segment_gap) — test → change default → update existing tests
4. **P2-T46, P2-T47, P2-T48, P2-T43, P2-T44, P2-T45** (min_turn_segment) — test → field → implement helper → wire twice
5. **P2-T06, P2-T05, P2-T01, P2-T02, P2-T03, P2-T04** (path cleanup: U-turns + collinear merge) — strengthen tests → diagnose → fix → wire
6. **P2-T18–T21, P2-T12–T17** (multi-pass) — write failing tests → extract loop → detect conflicts → implement passes; **gate for node-move**
7. **P2-T11, P2-T08, P2-T09** (high-degree layout) — independent of routing; parallel with step 6
8. **P2-T51–T53, P2-T50, P2-T54** (View.duplicate) — fully independent; parallel with any step
9. **P2-T27–T31, P2-T22–T26, P2-T55** (node-move) — requires multi-pass (step 6) stable first

---

## Success criteria for Phase 2

| SC | Criterion | Test |
|----|-----------|------|
| SC-P2-01 | Zero U-turns in tutorial topology | `test_no_uturns` (new) |
| SC-P2-02 | Zero redundant intermediate bendpoints | `test_no_redundant_bendpoints` (new) |
| SC-P2-03 | Zero node crossings in tutorial topology | SC-006 / FR-013 (existing, already passing for most cases) |
| SC-P2-04 | Zero double crossings in tutorial topology | `test_no_double_crossings` (new) |
| SC-P2-05 | All existing 1479+ tests still pass | Full test suite |
| SC-P2-06 | Performance: < 5s for 500 nodes + 1000 connections | Existing perf test (limit may be raised from 3s to 5s) |
| SC-P2-07 | `allow_node_move=False` (default): no node position changes (SC-010 preserved) | `test_allow_node_move_false` |
| SC-P2-08 | `allow_node_move=True`: blocking node shifted ≤ 1 cell; result lists the move | `test_node_move_recorded` |
| SC-P2-09 | No segment within 25px of any node side (default config) | SC-006 updated assertion |
| SC-P2-10 | No collinear segment pair < 20px apart (default config) | SC-008 updated assertion |
| SC-P2-11 | All post-L-turn segments ≥ 40px (default config) | SC-012 (new) |
| SC-P2-12 | `View.duplicate()` returns independent deep copy; original unchanged | SC-013 (new) |
