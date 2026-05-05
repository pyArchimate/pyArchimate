# Contract: Layout API

**Version**: 1.0 | **Date**: 2026-05-03 | **Status**: Specification

## Overview

This document specifies the public API contract for the auto-layout and auto-format feature. These APIs enable
developers to programmatically apply layout and formatting to ArchiMate views.

## Module: `pyArchimate.view.layout`

### Public Classes

#### `LayoutConfig`

Configuration object for layout operations.

```python
class LayoutConfig:
    """Configuration for auto-layout and auto-format operations.
    
    Attributes:
        algorithm: str
            Layout algorithm to use: "force_directed" (default) or "hierarchical"
        spacing: float
            Minimum pixel distance between element centers. Default: 50.0
        margin: float
            Padding around canvas boundary. Default: 20.0
        alignment: str
            Element alignment: "grid" (snap to grid) or "none" (free). Default: "grid"
        grid_size: float
            Grid cell size in pixels (used if alignment="grid"). Default: 10.0
        excluded_element_ids: Set[str]
            Element IDs to exclude from layout. Default: empty set
        respect_archimate_layers: bool
            Enforce Business→Application→Technology ordering. Default: True
        layer_priority: bool
            Prioritize layer constraints over crossing reduction. Default: True
        routing_style: str
            Connection routing: "orthogonal" (default) or "mixed" (allows 45°)
        max_crossings_for_orthogonal: int
            Threshold for using 45° fallback (if routing="mixed"). Default: 10
        minimize_label_overlap: bool
            Position labels to avoid overlaps. Default: True
        max_iterations: Optional[int]
            Maximum iterations for iterative algorithms. Auto-calculated if None.
        convergence_threshold: float
            Stop iteration if element movement < threshold (pixels). Default: 0.1
    """
```

#### `LayoutResult`

Result of a layout operation.

```python
class LayoutResult:
    """Result of applying layout to a view.
    
    Attributes:
        view: View
            Modified view with repositioned elements and routed connections
        config: LayoutConfig
            Configuration used for this layout
        total_elements: int
            Number of elements laid out
        total_connections: int
            Number of connections routed
        total_crossings: int
            Actual crossing count in final layout
        layout_time_ms: float
            Time taken to perform layout (milliseconds)
        algorithm_used: str
            Name of algorithm actually used ("force_directed" or "hierarchical")
        layout_quality: str
            Heuristic quality assessment: "good", "acceptable", or "poor"
        issues: List[str]
            Warnings or issues encountered during layout
    """
```

---

### Public Functions

#### `apply_layout(view: View, config: LayoutConfig = None) -> LayoutResult`

Apply auto-layout to a view.

**Parameters**:

- `view` (View): Target view to layout
- `config` (LayoutConfig, optional): Layout configuration. If None, uses default LayoutConfig.

**Returns**:

- `LayoutResult`: Layout operation result containing modified view and metadata

**Raises**:

- `ValueError`: If view is invalid or config contains invalid parameters
- `RuntimeError`: If layout fails to converge within iteration limits

**Example**:

```python
from pyArchimate.view import View
from pyArchimate.view.layout import LayoutConfig, apply_layout

view = load_view("my_architecture.archimate")

config = LayoutConfig(
    algorithm="hierarchical",
    spacing=60,
    respect_archimate_layers=True
)

result = apply_layout(view, config)

if result.layout_quality == "good":
    save_view(result.view, "my_architecture_laid_out.archimate")
else:
    print(f"Layout quality: {result.layout_quality}")
    print(f"Issues: {result.issues}")
```

**Acceptance Criteria** (from spec):

- SC-001: Layout completes in under 2 seconds for views with up to 300 elements
- SC-002: 100% of elements visible and non-overlapping after layout
- SC-008: 100% of layouts respect ArchiMate layer boundaries

---

#### `apply_format(view: View) -> LayoutResult`

Apply auto-format (element standardization) to a view without repositioning elements.

**Parameters**:

- `view` (View): Target view to format

**Returns**:

- `LayoutResult`: Format operation result containing modified view

**Raises**:

- `ValueError`: If view is invalid

**Example**:

```python
from pyArchimate.view import View
from pyArchimate.view.layout import apply_format

view = load_view("my_architecture.archimate")
result = apply_format(view)
save_view(result.view, "my_architecture_formatted.archimate")
```

**Acceptance Criteria** (from spec):

- SC-004: Auto-format reduces element size variance by 80%

---

#### `undo_layout(view: View) -> View`

Revert a view to its state before the last layout operation.

**Parameters**:

- `view` (View): View to revert

**Returns**:

- `View`: View with layout reverted

**Raises**:

- `RuntimeError`: If no previous layout transaction exists

**Example**:

```python
from pyArchimate.view.layout import apply_layout, undo_layout

view = load_view("my_architecture.archimate")
result = apply_layout(view)

if result.layout_quality == "poor":
    view = undo_layout(result.view)
    # Try again with different config
    config = LayoutConfig(algorithm="hierarchical")
    result = apply_layout(view, config)
```

**Acceptance Criteria** (from spec):

- SC-006: Undo/rollback successfully restores view in 100% of test cases

---

## API Behavior Specifications

### Layout Algorithm Behavior

#### Force-Directed Layout

- **Use case**: General-purpose layouts; works well for organic, mixed-relationship models
- **Algorithm**: Spring-Embedder physics simulation
- **Performance**: O(n²) per iteration, typically converges in 50-200 iterations
- **Layer constraint handling**: Enforced via vertical/horizontal forces
- **Crossing minimization**: Via force repulsion; post-layout barycentric refinement

#### Hierarchical Layout

- **Use case**: Layered/organizational structures; optimal for trees and DAGs
- **Algorithm**: Sugiyama's layered layout method
- **Performance**: O(n log n) for layer assignment; O(n²) for position assignment
- **Layer constraint handling**: Integrated into layer assignment; ArchiMate layers map to Sugiyama layers
- **Crossing minimization**: Built into Sugiyama algorithm

### Connection Routing Behavior

- **Orthogonal routing** (primary): All connections routed using 0°, ±90° angles
- **45° fallback**: If orthogonal routing produces >10 crossings, ±45° angles are allowed as fallback (non-default)
- **Label positioning**: Labels placed perpendicular to connection segments; collision-free positioning guaranteed if
  possible
- **Crossing minimization**: Barycentric method applied post-routing to reduce crossings by at least 60% vs. random
  layout

### Element Formatting

- **Size standardization**: Elements resized to standard dimensions based on ArchiMate type
- **Alignment**: Elements snapped to grid (if `alignment="grid"`) or left free (if `alignment="none"`)
- **Font standardization**: Consistent font family and size per element type
- **Properties preserved**: User-set colors, line styles, and other visual properties not modified

---

## Error Handling

### Invalid Configuration

**Input**: LayoutConfig with `algorithm="unknown"`

**Response**: Raises `ValueError("Unknown algorithm: unknown. Available: force_directed, hierarchical")`

### View Integrity Errors

**Input**: View with missing element reference in connection

**Response**: Raises `ValueError("Connection references non-existent element")`

### Convergence Failures

**Input**: Very large view (e.g., 10,000 elements) with tight iteration limits

**Response**: Returns LayoutResult with `layout_quality="poor"` and `issues=["Convergence not achieved"]`

### Undo Without History

**Input**: Calling `undo_layout()` on a view with no layout transactions

**Response**: Raises `RuntimeError("No layout operation to undo")`

---

## Backward Compatibility

- **Version 1.0**: Initial release; no prior versions to maintain compatibility with
- **Future versions**: Will maintain `apply_layout(view, config)` signature for backward compatibility; new parameters
  will use defaults

---

## Testing Contract

All public functions MUST pass these contract tests before release:

1. **Functional Tests**:
    - `test_apply_layout_default_config()`: Apply layout with default LayoutConfig
    - `test_apply_layout_hierarchical()`: Apply layout with hierarchical algorithm
    - `test_apply_layout_excluded_elements()`: Verify excluded elements retain position
    - `test_apply_format()`: Verify element size standardization
    - `test_undo_layout()`: Verify undo/rollback correctness
    - `test_apply_layout_large_view()`: Verify performance on 500-element view

2. **Contract Tests**:
    - `test_layout_result_contains_modified_view()`: LayoutResult.view must be modified
    - `test_layout_result_respects_archimate_layers()`: SC-008: 100% layer boundary compliance
    - `test_layout_preserves_element_properties()`: Element names, types, docs unchanged
    - `test_layout_preserves_connections()`: All connections remain valid after layout

3. **Error Tests**:
    - `test_invalid_algorithm_raises()`: Invalid algorithm raises ValueError
    - `test_invalid_view_raises()`: Corrupt view raises ValueError
    - `test_undo_without_history_raises()`: Raises RuntimeError

---

## Performance Guarantees

| Metric                        | Target     | Acceptance          |
|-------------------------------|------------|---------------------|
| Layout time (300 elements)    | <2 seconds | SC-001              |
| Layout time (500 elements)    | <5 seconds | Derived from SC-001 |
| Element overlap               | 0%         | SC-002              |
| Connection overlap            | 0%         | FR-007              |
| Label overlap                 | 0%         | FR-007              |
| Layer boundary compliance     | 100%       | SC-008              |
| Crossing reduction vs. random | ≥60%       | SC-005              |
