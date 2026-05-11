# Research: Auto-Layout and Auto-Routing Separation

**Date**: 2026-05-11 | **Branch**: `013-layout-routing-refactor`

## R-001: Layout/Routing Separation Pattern

**Decision**: Expose two independent public functions (`auto_layout`, `auto_route`) with a backward-compat wrapper (`apply_layout` calls both in sequence).

**Rationale**: The current `apply_layout()` is a monolith that runs node positioning then routing in one call. Separating them allows callers to: (1) layout without routing (useful after import when connections are already correct), (2) re-route without repositioning (useful after manual node moves), (3) chain them explicitly.

**Alternatives considered**:
- Single function with a `skip_routing` flag — rejected: violates single responsibility; flag proliferation
- Two separate modules — rejected: fragments the public API; callers would need two imports for the common case

---

## R-002: Coarse Grid Layout Algorithm

**Decision**: Row-per-ArchiMate-layer with coarse grid (default cell = 120px = default node width). Row-major collision resolution (shift right, wrap to next row).

**Rationale**: The current force-directed algorithm is general but non-deterministic across runs and doesn't enforce layer zones with hard boundaries. For the "ordered arrangement" use case in this feature, a simple grid is more predictable and produces immediately readable diagrams with zero configuration.

**Alternatives considered**:
- Keep force-directed as default — rejected: non-deterministic; doesn't guarantee coarse-grid alignment
- Sugiyama hierarchical — rejected: overkill for the coarse-grid goal; already available as `apply_layout(config=LayoutConfig(algorithm="hierarchical"))`
- Bin-packing per layer — rejected: more complex, no user-visible advantage over row-major for ArchiMate diagrams

---

## R-003: Obstacle-Aware Orthogonal Routing

**Decision**: Grid-inflated obstacle map with corridor BFS/A* for path finding. No external graph libraries — pure Python stdlib.

**Rationale**: The current `_apply_orthogonal_routing()` ignores the `_obstacles` parameter entirely. For FR-013 (no segment through any node), real obstacle avoidance is required. A rasterized grid at ~10px resolution over the canvas provides a practical path-finding space without introducing new dependencies.

**Alternatives considered**:
- Visibility graph routing — better theoretical guarantees but O(n²) edge count; complex to implement correctly for orthogonal-only paths
- NetworkX shortest path — would add an external dependency; rejected per project constraints
- Keep current (no obstacle avoidance) — rejected: violates FR-013 and SC-006

---

## R-004: Segment Separation

**Decision**: Post-routing pass: detect collinear overlapping segments across all connections, displace each overlapping segment by `min_segment_gap` (default 10px) perpendicular to the segment direction.

**Rationale**: Collinear overlap is visually indistinguishable from a single line and hides connection count. A post-processing pass is simpler than baking separation into the routing algorithm itself.

**Alternatives considered**:
- Bake separation into routing: route around already-placed segments — rejected: requires routing in dependency order; creates ordering sensitivity
- Only check adjacent connections: order-dependent, misses non-adjacent conflicts

---

## R-005: Corner Clearance — Proportional vs Absolute

**Decision**: `corner_clearance = max(edge_length × 0.10, 4.0px)`. Applied per-edge at endpoint assignment time.

**Rationale**: Fixed 10px disappears on large nodes (120px edge → 8% clearance reasonable; 500px edge → 2% too tight visually) and crowds on small nodes. Proportional scales correctly.

**Alternatives considered**: See clarification Q4 answer.

---

## R-006: Unroutable Connection Handling

**Decision**: Skip + warn (preserve existing waypoints, add warning to result object). No exception, no full rollback.

**Rationale**: Partial success on large views is more useful than all-or-nothing. User can inspect warnings and address blocked connections manually.

**Alternatives considered**: See clarification Q1 answer.

---

## R-007: Timeout / Partial Completion (Deferred)

**Decision**: No hard timeout enforcement in MVP. Functions run to completion. Document in Assumptions.

**Rationale**: The performance targets (2s/3s for 500 nodes) are achievable with the chosen algorithms. Implementing a graceful mid-computation partial-apply would add significant complexity for an edge case that won't arise in typical usage. Defer to a future release with profiling data.