# Data Model: View Auto-Layout and Auto-Format

**Phase 1 Output** | **Date**: 2026-05-03

## Overview

This document defines the data entities involved in the auto-layout and auto-format feature. Most entities (View,
Element, Connection) are existing pyArchimate model classes; new entities are introduced for layout configuration and
results.

## Existing Entities (Unchanged)

### View

**Location**: `src/pyArchimate/view/model.py`

- **Purpose**: Container holding elements and connections; target of auto-layout operation
- **Key Attributes**:
    - `id`: Unique identifier
    - `name`: View name
    - `elements`: List[Element] — visual elements in the view
    - `connections`: List[Connection] — visual connections between elements
    - `metadata`: Dict — view-level metadata (zoom, pan offset, etc.)

**Lifecycle**: View is loaded from .archimate XML file, potentially modified by layout operation, and serialized back to
XML.

### Element

**Location**: `src/pyArchimate/view/model.py`

- **Purpose**: Individual ArchiMate element with position, size, and visual properties
- **Key Attributes**:
    - `id`: Unique identifier (link to model element)
    - `position`: (x: float, y: float) — canvas position
    - `size`: (width: float, height: float) — element dimensions
    - `name`: String
    - `type`: ArchiMate element type (e.g., "ApplicationComponent", "BusinessActor")
    - `layer`: ArchiMate layer ("Business", "Application", "Technology", or compound)
    - `properties`: Dict — user-set visual properties (color, font, line style, etc.)
    - `documentation`: String — element documentation

**Validation Rules**:

- `position` must be finite (not NaN, not infinity)
- `size` must be positive (width > 0, height > 0)
- `layer` must be a valid ArchiMate layer (Business, Application/Element, Technology, or combination)

**State Transitions**:

- Created → Positioned → Formatted (during layout) → Persisted

### Connection

**Location**: `src/pyArchimate/view/model.py`

- **Purpose**: Visual representation of a relationship between elements
- **Key Attributes**:
    - `id`: Unique identifier
    - `source_element_id`: ID of source element
    - `target_element_id`: ID of target element
    - `label`: String — connection label (e.g., "realizes", "accesses")
    - `waypoints`: List[(x: float, y: float)] — polyline path for connection rendering
    - `routing_style`: String — "orthogonal" (default) or "mixed" (allows 45°)
    - `relationship_type`: String — ArchiMate relationship type
    - `properties`: Dict — visual properties (color, line style, etc.)

**Validation Rules**:

- `source_element_id` and `target_element_id` must reference existing elements
- `waypoints` must form a valid polyline (no duplicate consecutive points)
- `waypoints` must not pass through non-source/target elements (collision-free)
- `label` text must not overlap with any connection lines or other labels

**State Transitions**:

- Created → Routed (during layout) → Labeled → Persisted

---

## New Entities (Introduced by This Feature)

### LayoutConfig

**Location**: `src/pyArchimate/view/layout/core.py`

Configuration object controlling auto-layout behavior.

```python
class LayoutConfig:
    """Configuration for auto-layout operation."""
    
    # Algorithm selection
    algorithm: str = "force_directed"  # "force_directed" or "hierarchical"
    
    # Spacing & alignment
    spacing: float = 50.0  # Minimum distance between element centers (pixels)
    margin: float = 20.0   # Padding around canvas boundary (pixels)
    alignment: str = "grid"  # "grid" (snap to grid), "none" (free positioning)
    grid_size: float = 10.0  # Grid cell size if alignment="grid"
    
    # Element filtering
    excluded_element_ids: Set[str] = field(default_factory=set)
    
    # Constraint enforcement
    respect_archimate_layers: bool = True  # Enforce Business→App→Tech ordering
    layer_priority: bool = True  # Prioritize layer constraints over crossing reduction
    
    # Connection routing
    routing_style: str = "orthogonal"  # "orthogonal" or "mixed" (allows 45°)
    max_crossings_for_orthogonal: int = 10  # Threshold for 45° fallback
    minimize_label_overlap: bool = True  # Position labels to avoid overlaps
    
    # Performance tuning
    max_iterations: int = None  # Auto-calculated if None
    convergence_threshold: float = 0.1  # Stop iteration if movement < threshold (px)
```

**Validation Rules**:

- `spacing` > 0
- `margin` >= 0
- `algorithm` must be registered in layout registry
- `excluded_element_ids` must reference existing elements
- `routing_style` must be "orthogonal" or "mixed"
- `grid_size` > 0 if `alignment="grid"`

### LayoutResult

**Location**: `src/pyArchimate/view/layout/core.py`

Result of a layout operation, containing the modified view and metadata.

```python
class LayoutResult:
    """Result of a layout operation."""
    
    view: View  # Modified view with repositioned elements and routed connections
    config: LayoutConfig  # Configuration used for this layout
    metadata: Dict = field(default_factory=dict)
    
    # Metrics for quality assessment
    total_elements: int  # Number of elements laid out
    total_connections: int  # Number of connections routed
    total_crossings: int  # Actual crossing count
    max_crossing_ratio: float  # max_crossings / expected_crossings (Quality metric)
    layout_time_ms: float  # Time taken (milliseconds)
    algorithm_used: str  # Which algorithm was selected
    
    # Quality indicators
    layout_quality: str  # "good", "acceptable", "poor" (heuristic)
    issues: List[str] = field(default_factory=list)  # Any warnings/issues encountered
```

**Validation Rules**:

- All numeric metrics must be non-negative
- `layout_quality` must be one of: "good", "acceptable", "poor"
- `algorithm_used` must match `config.algorithm`

### LayerConstraint

**Location**: `src/pyArchimate/view/layout/layer_constraints.py`

Represents ArchiMate layer ordering constraints.

```python
class Layer(Enum):
    BUSINESS = "Business"
    APPLICATION = "Application"
    TECHNOLOGY = "Technology"

class LayerConstraint:
    """Enforces ArchiMate layer ordering."""
    
    elements_by_layer: Dict[Layer, List[Element]]  # Sorted elements per layer
    ordering: str = "vertical"  # "vertical" (y-axis) or "horizontal" (x-axis)
    
    def get_layer(element_id: str) -> Layer:
        """Determine which ArchiMate layer an element belongs to."""
        
    def apply_ordering(positions: Dict[str, Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """Adjust positions to respect layer ordering."""
```

**Validation Rules**:

- Each element can belong to at most one primary layer
- Layer ordering must be preserved: Business > Application > Technology

### RoutingResult

**Location**: `src/pyArchimate/view/layout/routing/orthogonal.py`

Result of connection routing operation.

```python
class RoutingResult:
    """Result of connection routing."""
    
    connection_id: str
    waypoints: List[Tuple[float, float]]  # Routed polyline
    crossing_count: int  # Number of crossings with other connections
    routing_style_used: str  # "orthogonal" or "45°_mixed"
    label_position: Optional[Tuple[float, float]]  # Offset position for label
    conflicts: List[str] = field(default_factory=list)  # Any unresolved issues
```

**Validation Rules**:

- `waypoints` must be a valid polyline (at least 2 points)
- `crossing_count` >= 0
- `routing_style_used` must match attempted routing method

### LabelPlacement

**Location**: `src/pyArchimate/view/layout/routing/label_placement.py`

Represents a positioned label with collision information.

```python
class LabelPlacement:
    """Label positioning result."""
    
    connection_id: str
    label_text: str
    position: Tuple[float, float]  # (x, y) of label center
    bounds: Rectangle  # Bounding box for collision detection
    offset_direction: str  # "above", "below", "left", "right", "center"
    overlap_conflicts: List[str] = field(default_factory=list)  # IDs of overlapping elements/labels
    truncated: bool = False  # True if label was abbreviated
```

**Validation Rules**:

- `bounds` must be non-negative width/height
- `position` must be within reasonable canvas bounds

---

## Relationships

```
View
├── elements: List[Element]
│   └── layer: str (Business, Application, Technology)
└── connections: List[Connection]
    ├── source_element_id → Element
    └── target_element_id → Element

LayoutConfig
└── excluded_element_ids: Set[str] → Element

LayoutResult
├── view: View
├── config: LayoutConfig
└── metadata: Dict

RoutingResult
└── connection_id → Connection

LabelPlacement
└── connection_id → Connection
```

---

## Entity Lifecycle

### Layout Operation Workflow

1. **Input**: View + LayoutConfig
2. **Layer Assignment** (if hierarchical): Assign elements to Sugiyama layers respecting ArchiMate layers
3. **Position Assignment**: Run force-directed or hierarchical algorithm
4. **Layer Constraint Enforcement**: Adjust positions if layer ordering violated
5. **Connection Routing**: Route connections (orthogonal, with 45° fallback if needed)
6. **Crossing Minimization**: Reorder waypoints to minimize crossings
7. **Label Placement**: Position labels without overlaps
8. **Output**: LayoutResult containing modified View

### State Consistency

- **Before layout**: All positions are user-set or default; may contain overlaps
- **During layout**: Intermediate positions are calculated; transient overlaps allowed
- **After layout**: All positions finalized; guaranteed no overlaps (except intentional grouping); all connections
  routed; all labels positioned
- **After serialization**: View saved to .archimate XML; positions and routing preserved

---

## Validation Rules Summary

| Entity          | Field           | Constraint                            |
|-----------------|-----------------|---------------------------------------|
| Element         | position        | Finite (x, y) values                  |
| Element         | size            | width > 0, height > 0                 |
| Element         | layer           | Valid ArchiMate layer                 |
| Connection      | waypoints       | Valid polyline, collision-free        |
| Connection      | label           | No overlap with connections or labels |
| LayoutConfig    | spacing         | > 0                                   |
| LayoutConfig    | algorithm       | Registered in layout_registry         |
| LayoutResult    | total_crossings | >= 0                                  |
| LayoutResult    | layout_time_ms  | >= 0                                  |
| LayerConstraint | ordering        | "vertical" or "horizontal"            |
| RoutingResult   | waypoints       | Valid polyline                        |
| RoutingResult   | crossing_count  | >= 0                                  |
| LabelPlacement  | bounds          | Non-negative dimensions               |

---

## Extensibility Points

1. **Algorithm Registry**: New layout algorithms can be registered without modifying core code
2. **Routing Strategies**: New routing algorithms (e.g., spline, free-form) can be added
3. **Constraint Handlers**: Custom constraint types can be added (e.g., group constraints, alignment zones)
4. **Quality Metrics**: New quality assessment heuristics can be plugged into LayoutResult

