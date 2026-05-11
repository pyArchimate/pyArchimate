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

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| P2-T01 | Investigate remaining ~6 U-turns: identify which connections and which cluster combination causes them; add a debug assertion in the test | — | P1 |
| P2-T02 | Fix displacement: for connections in multiple clusters, apply only the dominant-axis displacement (skip secondary axis) or detect the double-shift and merge | — | P1 |
| P2-T03 | Add `_merge_collinear_adjacent()` to `segment_separation.py` | — | P1 |
| P2-T04 | Wire `_merge_collinear_adjacent()` into `auto_route` after `remove_uturn_waypoints` | — | P1 |
| P2-T05 | Update `test_tutorial_svg_requirements.py`: add test `test_no_redundant_bendpoints` verifying zero consecutive-collinear segments | — | P2 |
| P2-T06 | Update `test_tutorial_svg_requirements.py`: strengthen U-turn check to zero | — | P2 |

### Phase 2B — Layout improvements (RQ-05, RQ-06) — medium risk

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| P2-T07 | Change `LayoutConfig.grid_size` default from 160 to 240; update all tests | — | P1 |
| P2-T08 | Add `LayoutConfig.high_degree_threshold: int = 5` field | — | P2 |
| P2-T09 | Implement high-degree node row isolation in `assign_grid_cells` | — | P2 |
| P2-T10 | Unit test: `grid_size=240` — all nodes snapped to 240px grid | — | P1 |
| P2-T11 | Unit test: high-degree node (degree ≥ 5) gets at least 1 grid-cell isolation | — | P2 |

### Phase 2C — Multi-pass routing (RQ-03, RQ-04) — high complexity

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| P2-T12 | Add `ObstacleMap.unmark_routed_segment(p1, p2)` method | — | P1 |
| P2-T13 | Extract current routing loop into `_route_pass(conns, om, config, warnings)` | — | P1 |
| P2-T14 | Add `_detect_node_crossings(waypoints, nodes_dict) -> set[int]` | — | P1 |
| P2-T15 | Add `_detect_double_crossings(waypoints) -> set[int]` | — | P1 |
| P2-T16 | Implement multi-pass outer loop in `auto_route` (max 3 passes) | — | P1 |
| P2-T17 | Add `RoutingConfig.max_routing_passes: int = 3` | — | P2 |
| P2-T18 | Unit test: connection initially crossing a node is re-routed around it after multi-pass | — | P1 |
| P2-T19 | Unit test: double-crossing pair is resolved (one connection re-routed) | — | P2 |
| P2-T20 | Integration test: tutorial topology has zero node crossings after multi-pass (SC-006 always green) | — | P1 |
| P2-T21 | Performance test: 500 nodes / 1000 connections still routes in < 5s with multi-pass | — | P1 |

---

## Recommended execution order

1. **P2-T07** (grid_size default) — single-line change, instant improvement, unblocks routing quality
2. **P2-T03, P2-T04** (merge collinear adjacent) — easy, eliminates RQ-02
3. **P2-T01, P2-T02** (fix remaining U-turns) — diagnose first, then fix
4. **P2-T12 through P2-T16** (multi-pass) — highest complexity, implement last
5. **P2-T08, P2-T09** (high-degree layout) — independent, can be done in parallel with multi-pass

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
