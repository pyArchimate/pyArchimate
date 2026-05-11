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

### RoutingConfig (new)

```python
@dataclass
class RoutingConfig:
    min_segment_gap: float = 10.0        # min px between collinear segments of diff connections
    corner_clearance_pct: float = 0.10   # fraction of edge length reserved at each corner
    corner_clearance_min: float = 4.0    # absolute floor for corner clearance (px)
    crossing_penalty: float = 1.0        # relative weight applied to crossing count in path cost
```

**Validation rules**:
- `min_segment_gap` ≥ 0
- `0.0 < corner_clearance_pct ≤ 0.50` (cannot consume more than 50% of edge per corner)
- `corner_clearance_min` ≥ 0
- `crossing_penalty` ≥ 0

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

### ObstacleMap (new internal type)

```python
@dataclass
class ObstacleMap:
    cells: set[tuple[int, int]]   # blocked grid cells (col, row)
    resolution: float             # px per cell (default 10.0)
    canvas_width: float
    canvas_height: float

    def is_blocked(self, x: float, y: float) -> bool: ...
    def segment_blocked(self, p1: Point, p2: Point) -> bool: ...
    def find_corridor(self, start: Point, end: Point) -> list[Point] | None: ...
```

**Construction**: Each node bounding box inflated by 2px, rasterized to grid cells.

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

### auto_route flow

```
View (nodes at any positions, connections at any waypoints)
  → build ObstacleMap from node bounding boxes
  → compute corner clearance per edge
  → for each connection:
      → compute departure/arrival anchors with spread
      → find_corridor(src_anchor, tgt_anchor, obstacle_map)
      → if None: skip + add warning
      → else: write waypoints to connection
  → post-process: detect + displace collinear segment overlaps
  → return LayoutResult (warnings for skipped connections)
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