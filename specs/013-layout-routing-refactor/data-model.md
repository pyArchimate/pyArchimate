# Data Model: Auto-Layout and Auto-Routing Separation

**Date**: 2026-05-11 | **Branch**: `013-layout-routing-refactor`

## Entities

### LayoutConfig (existing — modified)

```python
@dataclass
class LayoutConfig:
    algorithm: str = "force_directed"   # "force_directed" | "hierarchical"
    spacing: float = 50.0               # minimum gap between nodes (px)
    margin: float = 20.0                # canvas margin (px)
    alignment: str = "grid"             # "free" | "grid"  [default changed to "grid"]
    excluded_element_ids: list[int] = []
    node_size_constraints: dict = {}
    routing_style: str = "orthogonal"   # "orthogonal" | "mixed_45"
    layer_priority: str = "mandatory"
    grid_size: float = 120.0            # [default changed: 10 → 120, coarse grid]
    layer_direction: str = "vertical"   # NEW: "vertical" | "horizontal"
```

**Changes from current**:
- `grid_size` default: `10.0` → `120.0`
- `alignment` default: `"free"` → `"grid"` (coarse grid always active for `auto_layout`)
- `layer_direction` field: new
- `auto_layout` only writes `(x, y)` per node; `width` and `height` are immutable (FR-006 revised)

---

### RoutingConfig (updated — Phase 2)

```python
@dataclass
class RoutingConfig:
    # Obstacle clearance (FR-013, Fix 7)
    node_clearance: int = 25             # avoidance zone around each node side (px)
    # Segment separation (FR-015, Fix 8)
    min_segment_gap: float = 20.0        # min px between collinear segments of diff connections
    # Post-L-turn floor (FR-024, Fix 9)
    min_turn_segment: int = 40           # min segment length after each L-turn (px); not applied to terminal arrival segment
    # Corner clearance (FR-017)
    corner_clearance_pct: float = 0.10   # fraction of edge length reserved at each corner
    corner_clearance_min: float = 4.0    # absolute floor for corner clearance (px)
    # Crossing cost
    crossing_penalty: float = 1.0        # relative weight for crossing count in path cost
    # Multi-pass control (Fix 3)
    max_routing_passes: int = 3          # max BFS passes; note: no corresponding FR — implementation detail
    # Node repositioning (FR-023, Fix 6)
    allow_node_move: bool = False        # enable routing-driven node repositioning
    max_node_displacement: int = 1       # max grid cells a node may be shifted
```

**Validation rules** (`__post_init__`):
- `node_clearance` ≥ 0
- `min_segment_gap` ≥ 0
- `0 < min_turn_segment ≤ 500`
- `0.0 < corner_clearance_pct ≤ 0.50`
- `corner_clearance_min` ≥ 0
- `crossing_penalty` ≥ 0
- `max_routing_passes` ≥ 1
- `max_node_displacement` ≥ 1

**Derived value** (computed at runtime, not stored):

```
corner_clearance(edge_length) = max(edge_length × corner_clearance_pct, corner_clearance_min)
```

---

### LayoutResult (existing — extended)

```python
@dataclass
class LayoutResult:
    success: bool
    view_id: str
    algorithm_used: str
    elements_processed: int
    connections_processed: int
    layout_time_ms: float
    quality_metrics: dict = {}
    error_message: str | None = None
    warnings: list[str] = []             # NEW: e.g. ["Skipped connection abc123: no valid path"]
```

**Warning format for skipped connections**:

```
"auto_route: skipped connection {conn_id} ({source_label} → {target_label}): no valid orthogonal path found; existing waypoints preserved"
```

---

### ObstacleMap (updated — Phase 2)

```python
@dataclass
class ObstacleMap:
    cells: set[tuple[int, int]]          # static blocked cells — node AABBs inflated by node_clearance
    _routed: set[tuple[int, int]]        # dynamic cells — paths routed in previous passes (soft obstacles)
    resolution: float                    # px per cell (default 10.0)
    canvas_width: float
    canvas_height: float

    def is_blocked(self, x: float, y: float) -> bool: ...
    def segment_blocked(self, p1: Point, p2: Point) -> bool: ...
    def find_corridor(self, start: Point, end: Point) -> list[Point] | None: ...
    def mark_routed_segment(self, p1: Point, p2: Point) -> None: ...    # add to _routed
    def unmark_routed_segment(self, p1: Point, p2: Point) -> None: ...  # remove from _routed (needed for multi-pass re-route)
    def rebuild_for_moved_nodes(self, nodes: list[Node], config: RoutingConfig) -> None: ...  # M3: update cells after node repositioning
```

**Construction**: Each node bounding box inflated by `config.node_clearance` px on all four sides, then rasterized to grid cells. `_routed` starts empty and is populated incrementally as each connection is routed.

**Multi-pass usage**: Between passes, `_routed` cells from non-conflicting connections are retained as soft obstacles (higher BFS cost, not hard blocks). Conflicting connections have their segments removed from `_routed` via `unmark_routed_segment` before being re-routed.

**Node-move usage** (FR-023): After a tentative node move, `rebuild_for_moved_nodes` re-inflates the AABB for moved nodes only, patching `cells` in-place before re-routing affected connections.

---

### GridCell (conceptual, not a class)

Discrete canvas coordinates: `(col × grid_size, row × grid_size)` where `col` and `row` are non-negative integers. Used by `auto_layout` for node placement.

**Collision state** (per layout call): `occupied: set[tuple[int, int]]` — tracks which cells are taken. When a new node's preferred cell is in `occupied`, advance in row-major order until a free cell is found.

---

## State Transitions

### auto_layout flow

```
View (arbitrary node positions)
  → group nodes by layer
  → sort layers: Business (0) < App (1) < Tech (2) < other (3)
  → assign grid cells (row-major, collision-free)
  → write (x, y) to each node
  → return LayoutResult (warnings if any nodes skipped)
View (nodes on coarse grid, layer-ordered)
```

### auto_route flow (Phase 2 — multi-pass)

```
View (nodes at any positions, connections at any waypoints)
  → build ObstacleMap: inflate each node AABB by node_clearance; _routed = {}
  → compute corner clearance per edge; assign departure/arrival anchors (FR-017)
  → Pass 0: route all connections; mark paths in _routed
  → for pass_num in 1..max_routing_passes:
      → conflicts = _detect_node_crossings() ∪ _detect_double_crossings()
      → if conflicts empty: break
      → for each conflicted connection:
          → unmark_routed_segment() from _routed
          → re-route with crossing_penalty × (pass_num + 1)
          → mark new path in _routed
  → post-process each connection's waypoints (in order):
      → _merge_collinear_adjacent()        # remove redundant bendpoints (RQ-02)
      → _enforce_min_turn_segment()        # 40px floor post-L-turn; skip terminal arrival segment (FR-024/M2)
      → _fix_u_turns()                     # eliminate backward segments (RQ-01)
      → _enforce_min_turn_segment()        # second pass: fix any segments shortened by U-turn fix (M6)
      → _displace_collinear_overlaps()     # separate parallel segments by min_segment_gap (FR-015)
  → if allow_node_move and conflicts remain:
      → attempt node moves (FR-023); rebuild_for_moved_nodes(); re-route affected connections
  → remaining conflicts: skip + warn (FR-019)
  → return LayoutResult
View (connections rerouted, or preserved if unroutable)
```

## Layer Assignment

| ArchiMate Layer | Priority | Element Type Examples |
|-----------------|----------|-----------------------|
| Motivation | 0 (topmost) | Driver, Goal, Principle, Requirement |
| Business | 1 | BusinessActor, BusinessRole, BusinessProcess |
| Application | 2 | ApplicationComponent, ApplicationService |
| Technology | 3 | TechnologyService, Node, Device, SystemSoftware |
| Physical | 4 | DistributionNetwork, Equipment, Facility |
| Implementation | 5 (bottommost) | WorkPackage, Deliverable, ImplementationEvent |
| Unknown | 6 | Elements whose type cannot be classified |

Layer is determined by ArchiMate element type lookup at layout time. The `ArchiCategory` registry (existing) provides type → layer mapping.
