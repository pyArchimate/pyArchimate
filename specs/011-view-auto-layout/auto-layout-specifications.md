# Auto-Layout and Auto-Format Technical Specifications

**Version**: 1.0-beta.1 | **Date**: 2026-05-05 | **Status**: BETA

---

## Executive Summary

This document provides detailed technical specifications for the View Auto-Layout and Auto-Format feature in pyArchimate. It covers layout algorithms, connection routing, element formatting, SVG export, and configuration options.

**Audience**: Developers integrating the feature, contributors, and advanced users.

---

## 1. Feature Overview

### Scope

The auto-layout feature automatically repositions and formats ArchiMate view elements to improve readability and reduce manual work. It includes:

- **Layout algorithms**: Force-directed (general-purpose) and hierarchical (tree-like structures)
- **Element formatting**: Standardize sizes, fonts, and alignment
- **Connection routing**: Orthogonal polylines with intelligent label placement
- **SVG export**: Render views as self-contained SVG images with ArchiMate symbols
- **Configuration**: Customize behavior via `LayoutConfig` parameters

### Core API

```python
from pyArchimate.view.layout import apply_layout, apply_format, undo_layout

# Load a view
view = load_view("architecture.archimate")

# Apply layout
layout_result = apply_layout(view, config=LayoutConfig(algorithm="force_directed"))

# Apply formatting
format_result = apply_format(view, config=LayoutConfig(alignment="grid"))

# Export as SVG
svg_string = view.to_svg()
view.to_svg(filepath="output.svg")  # Also write to file

# Undo last operation
undo_result = undo_layout(view)
```

---

## 2. Layout Algorithms

### 2.1 Force-Directed Layout

**Algorithm**: Spring-Embedder physics simulation

**How it Works**:
1. Treat each node as a point mass with repulsive forces
2. Treat each connection as a spring with attractive forces
3. Iteratively update node positions to reach equilibrium
4. Enforce ArchiMate layer constraints as soft forces

**Parameters**:
- `spacing` (float, default=50): Desired distance between nodes
- `margin` (float, default=20): Canvas margin
- `layer_priority` (enum): "mandatory" or "soft"

**Performance**:
- <2 seconds for 300 elements
- <5 seconds for 500 elements
- Convergence: Typically 50-200 iterations

**Best For**:
- Mixed relationships (non-hierarchical)
- Exploring element connections
- General-purpose layout

**Limitations**:
- May create overlapping connection labels (edge case)
- Extreme size variance (>10x ratio) may affect layout quality

### 2.2 Hierarchical Layout

**Algorithm**: Sugiyama layer-based layout

**How it Works**:
1. Assign nodes to layers based on graph structure
2. Enforce ArchiMate natural layers (Business > Application > Technology)
3. Minimize edge crossings using barycentric ordering
4. Position nodes within each layer

**Parameters**:
- `spacing` (float): Distance between nodes in same layer
- `margin` (float): Canvas margins
- `layer_priority` (enum): "mandatory" (default) or "soft"

**Performance**:
- <1 second for 300 elements
- <2 seconds for 500 elements

**Best For**:
- Tree-like structures (parent-child relationships)
- Organizational hierarchies
- Dependency diagrams

**Limitations**:
- Requires connected graph structure
- Circular dependencies may increase crossing count

---

## 3. Element Formatting

### 3.1 Standard Sizes

All ArchiMate element types use uniform dimensions:
- **Width**: 120 pixels
- **Height**: 55 pixels

Custom sizes can be set via `node.w` and `node.h` properties or through `node_size_constraints` in `LayoutConfig`.

### 3.2 Fonts

**Standard Font**:
- Family: Segoe UI (fallback: system sans-serif)
- Size: 9pt
- Style: Normal
- Weight: Normal

**Customization**: Per-element font properties can be set before formatting.

### 3.3 Alignment Options

- **Free** (default): Elements retain arbitrary positions
- **Grid**: Snap to grid with configurable cell size (default 10px)

---

## 4. Connection Routing

### 4.1 Routing Strategy

**Primary**: Orthogonal (0°, ±90° angles)
**Fallback**: ±45° angles only if orthogonal routing creates >10 crossings

### 4.2 Bendpoint Management

Connections store bendpoints as intermediate coordinates. Example:

```python
connection.add_bendpoint(Point(100, 150))
connection.add_bendpoint(Point(100, 200))
connection.remove_all_bendpoints()  # Reset routing
```

### 4.3 Crossing Minimization

**Barycentric ordering**: Reorder nodes within layers to minimize edge crossings.

**Crossing detection**: Implemented for quality metrics.

### 4.4 Label Placement

Connection labels are positioned:
1. On the longest segment of the polyline
2. Perpendicular to the segment direction
3. In a white background rectangle

**Label Content**: Short relationship type name (e.g., "Serving" instead of "ServingRelationship")

---

## 5. SVG Export

### 5.1 Output Format

Valid SVG 1.1 with:
- Element definitions as `<symbol>` elements in `<defs>`
- White background rectangle covering canvas
- Orthogonal polylines for connections
- ArchiMate-standard colors for elements
- Text labels with word wrapping

### 5.2 Element Symbols

All 30+ ArchiMate element types have dedicated SVG symbol definitions:

**Business Layer**:
- BusinessActor, BusinessRole, BusinessService, BusinessProcess, etc.

**Application Layer**:
- ApplicationComponent, ApplicationService, ApplicationInterface, etc.

**Technology Layer**:
- TechnologyNode, TechnologyDevice, TechnologyService, etc.

**Other Layers**:
- Motivation elements, Implementation elements, Other elements

**Standard Colors**: Per ArchiMate 3.x specification

### 5.3 Color Overrides

Per-element colors can override standard palette:

```python
node.fill_color = "#FF0000"  # Red
node.line_color = "#000000"  # Black border
svg = view.to_svg()  # Uses custom colors
```

### 5.4 Performance

- <200ms for 500 elements
- File size: ~50-200 KB depending on complexity

---

## 6. Configuration Options

### 6.1 LayoutConfig Parameters

```python
config = LayoutConfig(
    algorithm="force_directed",           # "force_directed" or "hierarchical"
    spacing=50,                           # Distance between elements (pixels)
    margin=20,                            # Canvas margin (pixels)
    alignment="free",                     # "free" or "grid"
    grid_size=10,                         # Grid cell size if alignment="grid"
    routing_style="orthogonal",           # "orthogonal" or "mixed_45"
    layer_priority="mandatory",           # "mandatory" or "soft"
    excluded_element_ids=[],              # Element IDs to exclude from layout
    node_size_constraints={               # Optional size constraints
        "min_width": 80,
        "max_width": 200,
        "min_height": 50,
        "max_height": 150,
    }
)
```

### 6.2 Validation

All parameters are validated:
- `spacing`: Must be 0 < spacing ≤ 500
- `margin`: Must be 0 ≤ margin ≤ 500
- `grid_size`: Must be 0 < grid_size ≤ 100 (if alignment="grid")
- `algorithm`: Must be "force_directed" or "hierarchical"
- `alignment`: Must be "free" or "grid"
- `routing_style`: Must be "orthogonal" or "mixed_45"
- `layer_priority`: Must be "mandatory" or "soft"

---

## 7. ArchiMate Layer Constraints

### 7.1 Mandatory Layer Ordering

All layouts enforce Business > Application > Technology ordering:

```
Business Layer (top)
    ↓
Application/Element Layer
    ↓
Technology Layer (bottom)
```

### 7.2 Mixed-Layer Elements

Elements spanning multiple layers are positioned in zones representing their primary layer.

### 7.3 Cross-Layer Connections

Connections between layers are expected and permitted. Layer positioning is not violated to avoid cross-layer connections.

---

## 8. Edge Cases & Handling

### 8.1 Single-Element Views

**Behavior**: Element is not repositioned; returns layout success with no changes.

**Test**: Single node at (10, 10) remains at (10, 10) after layout.

### 8.2 No-Connections Views

**Behavior**: Elements arranged in grid pattern with configured spacing.

**Test**: Isolated nodes are positioned non-overlapping on a grid.

### 8.3 Circular Dependencies

**Behavior**: Layout detects cycles and produces readable result without hanging.

**Test**: Graph with A→B→C→A produces valid layout with prioritized layer constraints.

### 8.4 Extreme Size Variance

**Behavior**: Layouts accommodate >10x size ratios without clustering small elements.

**Test**: Mix of tiny (20x20) and large (200x200) elements are positioned with proportional spacing.

### 8.5 Locked/Fixed Elements

**Status**: DEFERRED TO PHASE 8 (not yet implemented)

### 8.6 Very Large Views (>500 elements)

**Performance**: >5 seconds (exceeds target but completes successfully)

**Recommendation**: Use hierarchical layout for better performance on large views.

---

## 9. Quality Metrics

Each layout operation returns `LayoutResult` with metrics:

```python
result = apply_layout(view, config)

# Metrics
result.elements_processed          # Number of elements laid out
result.connections_processed       # Number of connections routed
result.layout_time_ms             # Execution time in milliseconds
result.quality_metrics            # Dictionary with algorithm-specific metrics
  - crossing_count                # Number of edge crossings
  - average_edge_length           # Average connection length
  - element_overlap_count         # Overlapping elements (should be 0)
  - size_variance                 # Standard deviation of element sizes
  - spacing_actual                # Actual spacing between elements
  - algorithm_used                # Name of algorithm applied
```

---

## 10. Undo/Rollback

### 10.1 API

```python
# Apply layout
result = apply_layout(view)

# Undo last operation
undo_result = undo_layout(view)

# Verify undo succeeded
assert undo_result.success
assert undo_result.algorithm_used == "undo"
```

### 10.2 Behavior

- Reverts view to state before last `apply_layout()` or `apply_format()` call
- Uses pyArchimate transaction system (not yet integrated in beta)
- Multiple undo calls supported (each reverts one step)

---

## 11. Error Handling

### 11.1 Common Errors

| Error | Cause | Resolution |
|-------|-------|-----------|
| Invalid algorithm | Unknown algorithm name | Use "force_directed" or "hierarchical" |
| Spacing validation failed | spacing ≤ 0 or > 500 | Set 0 < spacing ≤ 500 |
| Grid size validation failed | grid_size ≤ 0 or > 100 | Set 0 < grid_size ≤ 100 |
| View has no nodes | Empty view passed | Ensure view has at least one element |
| MockConnection has no method | Using mock in production | Use real Connection objects |

### 11.2 Graceful Degradation

- **Single element**: Returns success without repositioning
- **No connections**: Returns success with grid arrangement
- **Extreme variance**: Includes warning in quality metrics
- **Timeout**: Returns partial result with error message

---

## 12. Performance Characteristics

### 12.1 Benchmark Results

| Test Case | Algorithm | Time | Status |
|-----------|-----------|------|--------|
| 10 elements | Force-Directed | <50ms | ✅ |
| 100 elements | Force-Directed | <200ms | ✅ |
| 300 elements | Force-Directed | <2s | ✅ (target met) |
| 500 elements | Force-Directed | <5s | ⚠️ (exceeds target) |
| 300 elements | Hierarchical | <500ms | ✅ |
| 500 elements | Hierarchical | <1s | ✅ |

### 12.2 Bottlenecks

1. **Force-Directed Physics**: Iteration count scales with element count
2. **Orthogonal Routing**: Crossing detection is O(m²) where m = connections
3. **Label Placement**: Finding non-overlapping positions

---

## 13. Known Limitations (Beta)

1. **Connection label overlap**: Not prevented in dense diagrams
2. **Locked elements**: Not yet supported (Phase 8)
3. **Performance**: Exceeds target for >500 elements
4. **Circular dependencies**: May increase crossing count
5. **Extreme size variance**: Layout quality degrades with >10x ratios

---

## 14. Testing

### 14.1 Test Coverage

- **Unit Tests**: 1000+ tests covering algorithms, utilities, formatting
- **Integration Tests**: 20+ tests for round-trip fidelity
- **BDD Scenarios**: 30+ acceptance tests for user stories
- **Overall**: 91% code coverage

### 14.2 Test Categories

| Category | Count | Status |
|----------|-------|--------|
| Algorithm tests | 150+ | ✅ Passing |
| Routing tests | 100+ | ✅ Passing |
| Format tests | 50+ | ⚠️ Need assertion updates |
| SVG export tests | 80+ | ✅ Passing |
| Configuration tests | 40+ | ✅ Passing |
| Edge case tests | 50+ | ⏳ In progress |

---

## 15. Future Roadmap (Post-Beta)

### Planned Features

1. **Locked/fixed elements**: Respect lock states during layout
2. **Performance optimization**: Target <2s for 500 elements
3. **Connection label collision avoidance**: Automatic repositioning
4. **Additional algorithms**: Grid-based, spline-based layouts
5. **Interactive refinement**: Manual adjustment hooks
6. **Undo/rollback integration**: Full transaction system integration

### Feedback Welcome

Users are encouraged to report issues and suggestions via GitHub issues (with "beta" label) or email.

---

## References

- [spec.md](./spec.md) — Feature specification
- [plan.md](./plan.md) — Implementation plan
- [research.md](./research.md) — Technical research and decisions
- [quickstart.md](./quickstart.md) — Quick start guide
- ArchiMate 3.x Specification — Visual notation standards

---

**Last Updated**: 2026-05-05 | **Beta Status**: 1.0-beta.1 | **Feedback**: xavier.mayeur@gmail.com
