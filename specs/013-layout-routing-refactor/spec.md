# Feature Specification: Auto-Layout and Auto-Routing Separation

**Feature Branch**: `013-layout-routing-refactor`  
**Created**: 2026-05-11  
**Status**: Phase 1 complete — Phase 2 (routing quality) planned  
**Input**: Enhance auto-layout and auto-routing as independent functions with precise rules for node arrangement and connection routing.

## Phase 1 Status (2026-05-11)

All 61 original tasks complete. Core functions `auto_layout` and `auto_route` ship and pass 1479 unit/integration tests including a 14-case SVG-level integration suite (`tests/integration/test_tutorial_svg_requirements.py`).

### Known routing quality gaps driving Phase 2

The following issues remain visible in dense diagrams (e.g. the 16-node tutorial topology):

| ID | Category | Description |
|----|----------|-------------|
| RQ-01 | U-turns | ~6 connections still have opposite-direction segments on the same axis after displacement post-processing |
| RQ-02 | Redundant bendpoints | Consecutive collinear segments on the same axis (no direction change) produce unnecessary intermediate waypoints |
| RQ-03 | Node crossings | Some connections still route through node bounding boxes (e.g. CRM → Order API serving connection) |
| RQ-04 | Double crossings | Some connection pairs cross each other twice; a detour path would cross only once or not at all |
| RQ-05 | Layout spacing | Default inter-node gap (grid_size = 160px with 120px nodes → 40px gap) is too tight for routing; dense diagrams saturate BFS corridors |
| RQ-06 | Layout row assignment | Nodes with many connections are not promoted to their own row, forcing many connections through narrow passages |

### Root cause analysis

Single-pass BFS routing with penalty-based separation has fundamental limits:
- By connection N, earlier connections have saturated adjacent corridors; connection N falls back to penalty=0 and shares an existing corridor
- The displacement post-pass fixes zero-separation collinear overlaps but can create secondary 5px near-overlaps via cascading corner shifts
- The BFS does not model the full set of planned routes when making decisions for any individual connection

### Resolution: multi-pass routing (see Phase 2 plan)

A multi-pass approach routes all connections, detects conflicts, then re-routes conflicting connections treating existing routes as soft obstacles. This converges in 2-3 passes for typical diagrams and eliminates the corridor-saturation problem.

## Clarifications

### Session 2026-05-11

- Q: When `auto_route` cannot find a valid path for a connection, what should it do? → A: Skip that connection, preserve its previous waypoints, add a warning entry to the result object
- Q: What is the canonical term for diagram items in view-layer vs model-layer? → A: "Node" = view-layer item (bounding box, position); "element" = ArchiMate model object (type, name, documentation). Both terms used consistently throughout spec.
- Q: When two nodes snap to the same grid cell, how is the conflict resolved? → A: Shift the second node to the next available free cell in row-major order (right first, then next row); all nodes placed deterministically with no node left at an occupied cell
- Q: Should `corner_clearance` for endpoint spreading be absolute pixels or proportional to edge length? → A: Proportional — default 10% of edge length, with a minimum floor of 4px absolute
- Q: When a function exceeds its performance target, should it apply partial results, roll back, or run to completion? → A: Deferred to future release; MVP runs to completion with no hard timeout; documented in Assumptions

## Context

This specification refines and replaces the auto-layout/routing requirements in `011-view-auto-layout`. The key structural change is the **separation** of node-arrangement (auto-layout) and connection-routing (auto-routing) into two independent, independently callable functions. Each function acts on a `View` and produces deterministic, readable results.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Apply Auto-Layout to Reorganize Nodes (Priority: P1)

A developer has an ArchiMate view with nodes at arbitrary positions. They invoke `auto_layout(view)` and the function repositions all nodes in layer order (Business above Application above Technology) aligned to a coarse grid. Connections are not modified.

**Why this priority**: Core value—removes the most tedious manual work. Does not depend on routing; can be validated in isolation.

**Independent Test**: Invoke `auto_layout` on a view with mixed-layer nodes. Verify that all Business-layer nodes have lower Y coordinates than Application-layer, which have lower Y than Technology-layer, and that all node origins snap to multiples of the default node size.

**Acceptance Scenarios**:

1. **Given** a view with Business, Application, and Technology nodes at random positions, **When** `auto_layout` is called, **Then** all Business nodes are positioned above all Application nodes, and all Application nodes above all Technology nodes
2. **Given** a view after `auto_layout`, **When** node positions are inspected, **Then** every node's (x, y) origin is aligned to the nearest grid cell where cell size equals the default node size
3. **Given** a view where only `auto_layout` is called (no routing), **When** the view is inspected, **Then** all existing connection waypoints remain unchanged
4. **Given** a view with nodes of the same ArchiMate layer, **When** `auto_layout` is called, **Then** same-layer nodes are arranged in rows on the grid with adequate spacing
5. **Given** a view with no nodes, **When** `auto_layout` is called, **Then** the function returns without error and the view is unchanged

---

### User Story 2 - Apply Auto-Routing to Reroute Connections (Priority: P1)

A developer has a view (already laid-out or raw) with connections that cross through nodes, overlap each other, and share start/end points. They invoke `auto_route(view)` and the function recomputes all connection paths as orthogonal polylines that avoid nodes, avoid crossing segments of other connections, and spread endpoints across node edges.

**Why this priority**: Core value for readability—overlapping connections are the second-most common complaint. Independent from layout; can run on any view state.

**Independent Test**: Invoke `auto_route` on a view with several connections that currently pass through nodes or share start/end points. Verify: no segment intersects any node bounding box; no two segments of different connections are collinear and overlapping; no two connections start or end at exactly the same point on the same node edge.

**Acceptance Scenarios**:

1. **Given** a view with connections whose paths pass through nodes, **When** `auto_route` is called, **Then** no connection segment intersects any node bounding box
2. **Given** a view with connections that share collinear segment overlap, **When** `auto_route` is called, **Then** overlapping segments are separated by at least 20px
3. **Given** a view with connection labels, **When** `auto_route` is called, **Then** no connection segment overlaps any connection label bounding box
4. **Given** multiple connections leaving from the same edge of a node, **When** `auto_route` is called, **Then** their departure points are evenly spread across the middle portion of that edge, never touching corners
5. **Given** a view with no connections, **When** `auto_route` is called, **Then** the function returns without error and node positions are unchanged
6. **Given** a view where routing cannot fully avoid crossings (dense diagram), **When** `auto_route` is called, **Then** the number of crossings is minimized and each crossing is a clean X-intersection (not a T-overlap or collinear overlap)

---

### User Story 3 - Chain Layout then Routing (Priority: P2)

A developer wants a fully cleaned-up view. They call `auto_layout(view)` followed by `auto_route(view)`. The result is a view with ordered nodes on a grid and clean orthogonal connections.

**Why this priority**: The most common full-cleanup workflow; validates that the two functions compose correctly. Not needed to validate each individually.

**Independent Test**: Apply `auto_layout` then `auto_route` to a messy view. Verify layer ordering, grid alignment, no node-connection overlaps, and spread endpoints.

**Acceptance Scenarios**:

1. **Given** a messy view, **When** `auto_layout` is called then `auto_route` is called, **Then** the result satisfies both the layout acceptance criteria (US1) and the routing acceptance criteria (US2)
2. **Given** the chained result, **When** `auto_layout` is called again without changing node positions, **Then** node positions are stable (idempotent)

---

### User Story 4 - Configure Layout and Routing Behavior (Priority: P3)

A developer wants to override default grid size, layer ordering direction (vertical vs horizontal), or routing clearances. Both functions accept an optional configuration object.

**Why this priority**: Enables adaptation to different diagram styles and sizes. Non-blocking for MVP.

**Independent Test**: Pass a config with `grid_size=80` to `auto_layout`. Verify all node origins are multiples of 80 (uses a non-default value to distinguish from the default 120).

**Acceptance Scenarios**:

1. **Given** a custom `grid_size` in config, **When** `auto_layout` is called, **Then** all node origins snap to that grid size
2. **Given** `layer_direction="horizontal"` in config, **When** `auto_layout` is called, **Then** Business nodes are to the left of Application, which are to the left of Technology
3. **Given** a custom `min_segment_gap` in config, **When** `auto_route` is called, **Then** parallel segments of different connections are separated by at least that value

---

### User Story 5 - Allow Routing-Driven Node Repositioning (Priority: P3)

A developer has a dense view where some connections cannot route around nodes without crossing through them. They enable `allow_node_move=True` in `RoutingConfig`. The router identifies nodes (or coherent blocks of connected nodes) that, if shifted by one grid cell, would open a routing corridor. It moves those nodes within their layer, re-routes the affected connections, and reports the moves in the result.

**Why this priority**: Node moves are a last resort — most views route cleanly without them. When enabled, they can resolve pathological cases (e.g. a node that sits exactly in the only available corridor for multiple connections). Disabled by default so existing callers are unaffected.

**Independent Test**: Create a view where a node sits in the only available corridor between two other nodes. Invoke `auto_route` with `allow_node_move=True`. Verify: (a) the blocking node has moved by exactly one grid cell, (b) it is still in its original layer, (c) it does not overlap any other node, (d) the previously-blocked connection now routes without crossing any node, (e) the result object lists the moved node with old and new position.

**Acceptance Scenarios**:

1. **Given** `allow_node_move=False` (default), **When** `auto_route` is called, **Then** no node position changes regardless of routing difficulty
2. **Given** `allow_node_move=True` and a node blocking the only corridor, **When** `auto_route` is called, **Then** the blocking node is shifted by at most `max_node_displacement` grid cells along the routing axis
3. **Given** a node move is performed, **When** the result is inspected, **Then** it contains a list of `NodeMove(uuid, old_x, old_y, new_x, new_y)` entries
4. **Given** a candidate node move would cause overlap with another node, **When** `auto_route` evaluates it, **Then** the move is rejected and an alternative path or move is tried instead
5. **Given** a block of tightly-coupled nodes (sharing edges in the view), **When** `auto_route` determines one must move, **Then** the whole block moves together as a rigid unit (same delta) to preserve their relative positions
6. **Given** `allow_node_move=True` and no routing conflict can be resolved by a 1-cell move, **When** `auto_route` finishes, **Then** it behaves identically to `allow_node_move=False` for the unresolvable connections (skip + warn)

---

### Edge Cases

- View with only one layer type: layout arranges nodes in a grid, no cross-layer constraints violated
- View with nodes that have no connections: layout still places them on the grid; routing is a no-op
- Connection between nodes on the same grid row: routing finds an orthogonal path that exits from top or bottom edge
- Extremely dense view where segment separation is geometrically impossible for all pairs: minimize violations, document remaining overlaps in routing result metadata
- Node with more connections on one edge than grid positions allow: pack within middle 80% of edge, respect minimum 4px between adjacent exit points
- Connection whose source or target node is completely surrounded (no routing corridor available): skip routing for that connection, preserve existing waypoints, record warning in result; all other connections route normally

## Requirements *(mandatory)*

### Functional Requirements

**Auto-Layout**

- **FR-001**: The library MUST expose an `auto_layout(view, config=None)` function that takes a `View` object and repositions all nodes
- **FR-002**: `auto_layout` MUST NOT modify connection waypoints, connection bendpoints, or any relationship data
- **FR-003**: `auto_layout` MUST arrange nodes in ArchiMate layer order: Business layer nodes have smaller Y (higher on canvas) than Application layer nodes, which have smaller Y than Technology layer nodes (default: vertical ordering)
- **FR-004**: `auto_layout` MUST snap every node's top-left corner to the nearest coarse grid point; default grid cell size equals the default node size (120×55px or configured value)
- **FR-005**: `auto_layout` MUST ensure no two nodes overlap after repositioning; when two nodes snap to the same grid cell, the second node (in processing order) is shifted to the next available free cell in row-major order (right first, then next row), continuing until a free cell is found
- **FR-006**: `auto_layout` MUST preserve all node properties (name, type, documentation, style, width, height) — only (x, y) may change; node dimensions are never modified by `auto_layout`
- **FR-007**: `auto_layout` MUST support `layer_direction` configuration: `"vertical"` (default, Business top) or `"horizontal"` (Business left)
- **FR-008**: `auto_layout` MUST complete in under 2 seconds for views with up to 500 nodes

*(Note: FR-009 intentionally omitted — number reserved for future use.)*

**Auto-Routing**

- **FR-010**: The library MUST expose an `auto_route(view, config=None)` function that takes a `View` object and recomputes all connection paths
- **FR-011**: `auto_route` MUST NOT modify node positions, sizes, or any node properties
- **FR-012**: `auto_route` MUST generate orthogonal (rectilinear) connection paths — all segments are axis-aligned (0° or 90°)
- **FR-013**: `auto_route` MUST ensure no connection segment passes within `node_clearance` pixels of any node side (the avoidance zone); default `node_clearance` is 25px (measured perpendicularly from each side of the node bounding box). No routing through, or within 25px of, any node edge.
- **FR-014**: `auto_route` MUST ensure no connection segment overlaps any connection label bounding box
- **FR-015**: `auto_route` MUST ensure no two connection segments from different connections are collinear and overlapping; parallel collinear segments from different connections MUST be separated by at least `min_segment_gap` (default: 20px)
- **FR-016**: `auto_route` MUST minimize the total number of connection crossings across the view; when crossings are unavoidable, they MUST be clean X-intersections (not T-overlaps, not collinear overlaps)
- **FR-017**: `auto_route` MUST spread connection start and end points across each node edge: departure/arrival points MUST be distributed across the middle portion of the edge, excluding corner zones defined as max(10% of edge length, 4px) from each corner; points are evenly spaced and never coincident
- **FR-018**: `auto_route` MUST complete in under 3 seconds for views with up to 500 nodes and 1000 connections
- **FR-019**: When `auto_route` cannot find any valid orthogonal path for a connection, it MUST skip that connection (preserving its existing waypoints unchanged), and MUST add a warning entry to the result object identifying the skipped connection; it MUST NOT raise an exception or roll back other successfully routed connections
- **FR-024**: After every L-turn (90° direction change) in a routed connection, the following segment MUST be at least `min_turn_segment` px long (default: 40px); this prevents cosmetically degenerate "small steps" near corners. Exception: if the segment after the L-turn is the terminal arrival segment (the final approach to the target node's attachment point), `min_turn_segment` is NOT enforced on that segment to avoid displacing the endpoint away from the target node.
- **FR-025**: The library MUST expose a `View.duplicate(name=None)` method that creates and returns a deep copy of the view — including all nodes, connections, and their waypoints — as a new `View` object registered in the same model; if `name` is provided it becomes the duplicate's display name; the original view is not modified. If the view is not associated with a model (`self.model is None`), `duplicate()` MUST raise `ValueError("View has no parent model; cannot register duplicate")`. Callers with standalone views must explicitly assign the duplicate to a model.

**Shared**

- **FR-020**: Both functions MUST be independently callable — calling one MUST NOT require or implicitly invoke the other
- **FR-021**: Both functions MUST return a result object indicating success, number of nodes and connections processed, and any warnings (e.g., unresolvable overlaps, skipped connections)
- **FR-022**: Both functions MUST support an optional `config` parameter accepting a configuration object with typed fields and documented defaults
- **FR-023**: When `RoutingConfig.allow_node_move = True` (default: `False`), `auto_route` MAY reposition one or more nodes — or a coherent block of nodes that form a subgraph — by at most `RoutingConfig.max_node_displacement` grid cells (default: 1) along the routing axis, in order to open a routing corridor that cannot be satisfied by waypoint manipulation alone. Any node repositioned under this mode MUST remain in its original ArchiMate layer (layer ordering is preserved), MUST NOT overlap any other node after the move, and MUST be snapped to the grid. `auto_route` MUST record each moved node (uuid, old position, new position) in the result object. When `allow_node_move = False` (default), `auto_route` MUST NOT alter any node position (SC-010 unchanged).

### Clarification notes for FR-023

- "Block of nodes" means a set of nodes that move together as a rigid unit (same delta) to preserve their relative layout. The routing algorithm may propose a block move when individual node moves would create new overlaps between members of the block.
- The displacement limit (`max_node_displacement` in grid cells) prevents large layout disruptions; 1 cell means a node may shift by exactly one `grid_size` in one direction.
- The function must attempt routing with `allow_node_move = False` first; node moves are a last resort when the pure routing pass still leaves unresolvable crossings or node-crossing violations.
- This mode interacts with the multi-pass routing architecture (Phase 2): node moves are evaluated during the final pass when conflicts remain unresolved.

### Key Entities

- **View**: Container of nodes and connections; the input/output target of both functions
- **Node**: An ArchiMate element rendered in the view with bounding box (x, y, width, height) and layer membership
- **Connection**: A directed relationship rendered in the view with a polyline path (list of waypoints) and optional label
- **ConnectionLabel**: Bounding box of the label rendered on a connection; must not be overlapped by any segment
- **GridCell**: A discrete canvas position at coordinates (i × grid_size, j × grid_size); nodes snap to cell origins
- **LayoutConfig**: Configuration object for `auto_layout` — grid_size, layer_direction, spacing, margin
- **RoutingConfig**: Configuration object for `auto_route` — node_clearance (default 25px), min_segment_gap (default 20px), corner_clearance_pct (default 10%, proportion of edge length), corner_clearance_min (default 4px absolute floor), crossing_penalty, min_turn_segment (default 40px)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `auto_layout` completes in under 2 seconds for views with up to 500 nodes
- **SC-002**: After `auto_layout`, 100% of nodes have origins that are multiples of the configured grid size (verified programmatically)
- **SC-003**: After `auto_layout`, 0 pairs of nodes overlap (bounding boxes do not intersect)
- **SC-004**: After `auto_layout`, 100% of Business-layer nodes have Y < min(Application-layer Y) and 100% of Application-layer nodes have Y < min(Technology-layer Y) (vertical mode)
- **SC-005**: `auto_route` completes in under 3 seconds for views with up to 500 nodes and 1000 connections (all passes combined; multi-pass re-routes conflicted connections only, adding ≤ 20% overhead in typical diagrams)
- **SC-006**: After `auto_route`, 0 connection segments pass within 25px of any node side (verified by expanding each node bounding box by `node_clearance` and checking zero segment intersections)
- **SC-007**: After `auto_route`, 0 connection segments overlap any connection label bounding box (label clearance must still pass after AABB inflation; P2-T35 verifies both)
- **SC-008**: After `auto_route`, 0 pairs of connection segments from different connections are collinear and overlapping (separation ≥ 20px enforced)
- **SC-009**: After `auto_route`, 0 connections depart or arrive within the corner zone (max(10% of edge length, 4px) from each corner); all endpoints lie within the valid middle portion of the node edge
- **SC-010**: When `allow_node_move = False` (default), calling `auto_route` does not alter any node position — verified by comparing view state before/after each call in isolation. Calling `auto_layout` does not alter any connection waypoints (always).
- **SC-011**: When `allow_node_move = True`, every node moved by `auto_route` (a) remains in its original layer, (b) does not overlap any other node, (c) is snapped to the grid, and (d) is displaced by no more than `max_node_displacement` grid cells. The result object lists all moved nodes with old and new positions.
- **SC-012**: After `auto_route`, every segment immediately following an L-turn is ≥ 40px long (or configured `min_turn_segment`); the terminal arrival segment (the final segment approaching the target node) is excluded from this rule
- **SC-013**: `View.duplicate()` returns a new `View` with identical node count, connection count, and waypoint data; the original view's state is unchanged after the call; the new view is registered in the parent model

## Routing Rules *(mandatory)*

All connections produced by `auto_route` MUST satisfy:

- **Orthogonal segments only**: Every segment of every connection path is either horizontal (Δy=0) or vertical (Δx=0)
- **Node clearance**: No segment passes within `node_clearance` (default 25px) of any node side; the avoidance zone extends ±25px perpendicularly from each edge of the node bounding box
- **Label clearance**: No segment overlaps any connection label bounding box
- **Segment separation**: Two segments from different connections that would be collinear MUST be displaced by at least 20px (or configured `min_segment_gap`)
- **Minimum turn segment**: The segment immediately after each L-turn (90° bend) MUST be at least 40px (or configured `min_turn_segment`) to prevent degenerate micro-steps
- **No collinear overlap**: Two segments may cross (X-intersection) but MUST NOT run parallel at the same coordinate (T-overlap or overlap)
- **Crossing minimization**: The routing algorithm MUST prefer paths with fewer crossings over paths with more segments when both are feasible
- **Endpoint spreading**: On ALL FOUR node edges (left, right, top, bottom), connection attachment points are distributed across the middle portion of each edge. No point is within `corner_clearance` of a corner, where `corner_clearance = max(10% of edge length, 4px)`. Points are equally spaced within the available zone. Never coincident. Spreading is pre-computed per (node, edge) group before routing begins.

## ArchiMate Layer Constraints *(mandatory)*

- **Layer assignment**: Each node's layer is determined by its ArchiMate element type (Business, Application/Element, Technology, Motivation, Implementation & Migration, Physical)
- **Default vertical ordering** (top to bottom): Motivation → Business → Application → Technology → Physical → Implementation
- **Horizontal ordering** (left to right): same sequence as vertical, left to right
- **No inter-layer constraint on routing**: `auto_route` does not enforce layer order; it only routes connections; layer ordering is `auto_layout`'s responsibility
- **Mixed-layer views**: If a view contains elements from only one layer, the layer constraint is satisfied trivially; no error

## Assumptions

- Default node size is 120×55px (width×height); `grid_size` defaults to 120 (the node width)
- `auto_layout` does not need to compute optimal grid packing — a simple row-per-layer arrangement with consistent spacing is acceptable for MVP
- `auto_route` uses an A* or corridor-based algorithm operating on a grid-inflated obstacle map; exact algorithm is an implementation detail
- Both functions operate on in-memory `View` objects; persistence (writing to `.archimate` file) is the caller's responsibility
- The existing `View` API provides read/write access to node bounding boxes and connection waypoint lists
- No undo/rollback is built into these functions; callers are responsible for snapshot/restore if needed
- Performance targets assume standard hardware; very large views (>500 nodes) are out of scope for the initial release
- No hard timeout is enforced in MVP; both functions run to completion; timeout/partial-apply behavior is deferred to a future release pending profiling data

## Deliverables

- `auto_layout(view, config=None)` function in the pyArchimate view module
- `auto_route(view, config=None)` function in the pyArchimate view module
- `LayoutConfig` and `RoutingConfig` typed configuration dataclasses
- Unit tests: grid snapping, layer ordering, no-overlap guarantee, endpoint spreading, segment separation, node clearance zone, min-turn-segment enforcement, View.duplicate() deep copy
- Integration tests: chain layout+routing on realistic views; idempotency tests; duplicate view round-trip
