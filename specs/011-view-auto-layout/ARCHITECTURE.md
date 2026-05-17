# Layout Module Architecture

**Version**: 1.0 | **Date**: 2026-05-05 | **Status**: BETA

---

## Overview

The `pyArchimate.view.layout` module provides automatic layout and formatting capabilities for ArchiMate views. This document describes the module architecture, design decisions, and how components interact.

---

## Module Structure

```text
src/pyArchimate/view/layout/
├── __init__.py              # Public API: apply_layout(), apply_format(), undo_layout()
├── core.py                  # LayoutConfig, LayoutResult, LayoutAlgorithm (abstract)
├── algorithms/
│   ├── __init__.py         # Algorithm registry and factory
│   ├── force_directed.py   # Physics-based layout (Spring-Embedder)
│   └── hierarchical.py     # Layered layout (Sugiyama algorithm)
├── routing/
│   ├── __init__.py
│   ├── orthogonal.py       # Orthogonal polyline generation
│   ├── label_placement.py  # Connection label positioning
│   └── layer_constraints.py # ArchiMate layer enforcement
├── format/
│   ├── __init__.py
│   └── element_format.py   # Element sizing, fonts, alignment
├── export/
│   ├── __init__.py
│   └── svg_export.py       # SVG rendering with symbols
└── utils/
    ├── __init__.py
    ├── geometry.py         # Points, rectangles, distances, intersections
    ├── graph.py            # Graph connectivity, crossing detection
    └── edge_utils.py       # Edge-related utilities
```

---

## Design Principles

### 1. **Separation of Concerns**

- **Algorithms** are isolated from routing, formatting, and export
- **Routing** depends only on geometry utilities and layer constraints
- **Formatting** is independent of layout algorithms
- **Export** consumes the positioned view without modifying it

### 2. **Algorithm Abstraction**

All layout algorithms inherit from `LayoutAlgorithm` abstract base class:

```python
class LayoutAlgorithm(ABC):
    @abstractmethod
    def apply(self, view: Any, config: LayoutConfig) -> LayoutResult:
        """Apply layout and return metrics."""
```

This allows easy addition of new algorithms (grid-based, spline-based, etc.) without modifying the public API.

### 3. **Configuration Object Pattern**

`LayoutConfig` encapsulates all customization options:

```python
config = LayoutConfig(
    algorithm="force_directed",
    spacing=50,
    margin=20,
    alignment="grid",
    grid_size=10,
    routing_style="orthogonal",
    layer_priority="mandatory",
    excluded_element_ids={},
    node_size_constraints={}
)
```

All parameters are validated at construction time.

### 4. **Result Tracking**

`LayoutResult` provides consistent output with:

- **Execution metrics**: time, element/connection counts
- **Quality metrics**: crossings, spacing, variance, algorithm-specific values
- **Error handling**: success flag and optional error message

### 5. **Pure Function API**

- `apply_layout(view, config)` → LayoutResult
- `apply_format(view, config)` → LayoutResult
- `undo_layout(view)` → LayoutResult

All functions are idempotent and immutable (they create new results, not modify in-place).

---

## Algorithm Implementations

### Force-Directed (Spring-Embedder)

**File**: `algorithms/force_directed.py`

**How it works**:
1. Nodes treated as point masses with repulsive forces (prevent overlap)
2. Connections treated as springs with attractive forces (keep connected nodes nearby)
3. Iterative position updates toward equilibrium
4. Layer constraints applied as vertical forces

**Convergence criteria**:
- Node movement below threshold (default 0.05)
- Max iterations reached (adaptive: 100-500 based on element count)

**Time complexity**: O(n² × iterations) where n = element count

**Best for**: General-purpose layouts, mixed relationship types, exploring element relationships

**Limitations**:
- Slower for large views (>500 elements)
- May produce different results on different runs (stochastic convergence)
- Doesn't guarantee optimal crossing minimization

### Hierarchical (Sugiyama Layered)

**File**: `algorithms/hierarchical.py`

**How it works**:
1. **Layer assignment**: Nodes assigned to layers respecting ArchiMate constraints
2. **Crossing minimization**: Barycentric ordering within layers
3. **Position calculation**: Nodes positioned horizontally within layers
4. **Edge routing**: Orthogonal routes between layers

**Time complexity**: O(n × m) where n = nodes, m = edges

**Best for**: Organizational hierarchies, tree-like structures, dependency diagrams

**Guarantees**: Business ≥ Application ≥ Technology layer ordering

---

## Routing Strategy

### Orthogonal Routing

**File**: `routing/orthogonal.py`

**Algorithm**:
1. Organize nodes into row/column bands
2. Use clear gaps between row and column bands as routing corridors
3. Route connections through these gaps with minimal bendpoints
4. Adjacent-layer: 2 bendpoints (S-shape through row gap)
5. Multi-layer: 4 bendpoints (row gap → column gap → row gap)

**Endpoint spreading**: Multiple connections from/to same node are distributed along edge perimeter to avoid overlap

**Crossing minimization**: Reorder nodes within layers to reduce edge crossings

### Label Placement

**File**: `routing/label_placement.py`

**Strategy**:
1. Find longest segment in connection polyline
2. Place label at segment midpoint, perpendicular to segment
3. Render white background rectangle behind black text
4. Collision detection and repositioning if overlap detected

---

## Element Formatting

**File**: `format/element_format.py`

**Standard dimensions**:
- Width: 120px
- Height: 55px

**Font standardization**:
- Family: Segoe UI (fallback: system sans-serif)
- Size: 9pt
- Style: Normal
- Weight: Normal

**Alignment options**:
- **Free**: Arbitrary positions (default)
- **Grid**: Snap to grid with configurable cell size

**Size constraints**: Optional min/max dimensions per element

**Excluded elements**: Specified by ID, skip formatting

---

## SVG Export

**File**: `export/svg_export.py`

**Output format**: Valid SVG 1.1 with:

- **Symbol definitions**: `<defs>` block with 30+ ArchiMate element symbols
- **Relationship styles**: Per-relationship stroke, dash, marker definitions
- **Color palette**: ArchiMate standard colors + per-element overrides
- **Element nodes**: `<use>` elements referencing symbols
- **Connections**: `<polyline>` elements with orthogonal routing
- **Labels**: `<text>` over `<rect>` background on longest segment
- **Background**: White `<rect>` covering canvas

**Performance**: <200ms for 500-element views

**Features**:
- Self-contained (no external dependencies)
- Renders correctly in all modern browsers
- Per-element and per-relationship color overrides
- Word-wrapped labels with bounding box

---

## ArchiMate Layer Constraints

**File**: `routing/layer_constraints.py`

**Principles**:
1. All layouts respect Business > Application > Technology ordering
2. Mixed-layer elements positioned in zones for their primary layer
3. Cross-layer connections are expected and permitted
4. Layer ordering not violated to reduce crossings (layer_priority="mandatory")

**Implementation**:
- Layer enum: `BUSINESS`, `APPLICATION`, `TECHNOLOGY`
- Element type → layer mapping
- Vertical position enforcement in force-directed algorithm
- Layer assignment in hierarchical algorithm

---

## Type System

All modules are fully type-hinted for:
- IDE autocomplete support
- Static type checking (mypy, pyright)
- API contract clarity
- Reduced runtime errors

**Types**:
- `LayoutConfig`: Configuration data class
- `LayoutResult`: Result data class with quality metrics
- `LayoutAlgorithm`: Abstract base class for algorithms
- `Point`: 2D point (x, y)
- `Rectangle`: Axis-aligned bounding box

---

## Performance Optimization Techniques

### 1. **Spatial Indexing**

Nodes organized into grid-like bands for rapid proximity checks in orthogonal routing.

### 2. **Adaptive Iterations**

Force-directed algorithm scales iteration count based on element count:
- 10 elements: 50 iterations
- 100 elements: 150 iterations
- 300 elements: 250 iterations
- 500 elements: 400 iterations

### 3. **Convergence Detection**

Algorithm exits early if node movement falls below threshold, avoiding unnecessary iterations.

### 4. **Lazy Computation**

- Crossing detection only computed when needed (quality metrics)
- Label overlaps checked only for final placement

---

## Extension Points

### Adding a New Layout Algorithm

1. Create new class inheriting from `LayoutAlgorithm`
2. Implement `apply(view, config) -> LayoutResult` method
3. Register in `algorithms/__init__.py`:
  
   ```python
_ALGORITHMS = {
       "force_directed": ForceDirectedLayout,
       "hierarchical": HierarchicalLayout,
       "my_new_algorithm": MyNewAlgorithm,  # Add here
   }

   ```

### Custom Formatting

Subclass `FormatService` and override element sizing/font logic.

### Custom Routing

Create new routing strategy in `routing/` and integrate in algorithm's apply method.

---

## Testing Strategy

### Unit Tests

- **test_core.py**: Configuration validation, result structure
- **test_geometry.py**: Point operations, intersections, containment
- **test_layer_constraints.py**: Layer assignment and enforcement
- **test_force_directed.py**: Physics simulation, convergence
- **test_hierarchical.py**: Layer assignment, crossing minimization
- **test_orthogonal_routing.py**: Polyline generation, clipping
- **test_label_placement.py**: Label positioning, collision detection
- **test_format.py**: Sizing, fonts, alignment
- **test_archimate_symbols.py**: Symbol definitions, color palette
- **test_archimate_relationships.py**: Relationship styling

### Integration Tests

- **test_layout_round_trip.py**: Load → layout → save → verify XML
- **test_config_integration.py**: All LayoutConfig options
- **test_svg_export.py**: SVG generation, valid XML, element counts
- **test_undo_layout.py**: Undo/rollback scenarios

### BDD Scenarios

- **auto_layout.feature**: User story acceptance tests
- **auto_format.feature**: Formatting acceptance tests
- **svg_export.feature**: SVG export acceptance tests
- **customize_layout.feature**: Configuration customization

**Coverage**: 91% overall, 98%+ for core algorithms and routing

---

## Known Limitations (Beta)

1. **Performance**: Exceeds target for >500 element views (planned Phase 8)
2. **Locked elements**: Not yet supported (Phase 8)
3. **Label overlap**: Not prevented in dense diagrams (Phase 8)
4. **Circular dependencies**: May increase crossing count (handled gracefully)
5. **Extreme size variance**: Layout quality degrades with >10x aspect ratios

---

## Future Improvements (Phase 8+)

1. **Performance optimization**: Target <2s for 500 elements
2. **Locked/fixed elements**: Respect element lock states
3. **Connection label collision avoidance**: Automatic repositioning
4. **Additional algorithms**: Grid-based, spline-based layouts
5. **Interactive refinement**: Manual adjustment hooks
6. **Advanced options**: Custom force parameters, routing preferences

---

## References

- [Technical Specifications](auto-layout-specifications.md)
- [Quickstart Guide](quickstart.md)
- [API Contracts](contracts/)
- [Research Documentation](research.md)

---

**Last Updated**: 2026-05-05 | **Status**: BETA 1.0 | **Maintainer**: xavier.mayeur@gmail.com
