# Quickstart: Auto-Layout and Auto-Format

**Version**: 1.0 | **Date**: 2026-05-03

## 5-Minute Overview

The auto-layout feature automatically repositions elements in an ArchiMate view to improve readability and reduce manual positioning work. You can choose between two algorithms:

- **Force-Directed** (default): General-purpose layout for mixed relationships
- **Hierarchical**: Optimized for layered/organizational structures

Both algorithms enforce ArchiMate's natural layering (Business above Application above Technology) and produce orthogonal connection routing with clean, collision-free labels.

## Basic Usage

### Apply Default Layout

```python
from pyArchimate.view import load_view, save_view
from pyArchimate.view.layout import apply_layout

# Load a view
view = load_view("architecture.archimate")

# Apply layout with default settings
result = apply_layout(view)

# Check result quality
print(f"Layout quality: {result.layout_quality}")
print(f"Layout time: {result.layout_time_ms}ms")
print(f"Crossings: {result.total_crossings}")

# Save the laid-out view
if result.layout_quality in ["good", "acceptable"]:
    save_view(result.view, "architecture_laid_out.archimate")
```

**Output**:

```
Layout quality: good
Layout time: 245.5ms
Crossings: 3
```

### Choose a Layout Algorithm

```python
from pyArchimate.view.layout import LayoutConfig, apply_layout

config = LayoutConfig(
    algorithm="hierarchical",  # Use hierarchical layout for organizational models
)

result = apply_layout(view, config)
```

### Customize Spacing and Alignment

```python
from pyArchimate.view.layout import LayoutConfig, apply_layout

config = LayoutConfig(
    algorithm="force_directed",
    spacing=80,      # Increase spacing between elements
    margin=40,       # Increase margin around canvas
    alignment="grid",  # Snap elements to 10px grid
    grid_size=10,
)

result = apply_layout(view, config)
```

### Exclude Specific Elements

```python
from pyArchimate.view.layout import LayoutConfig, apply_layout

config = LayoutConfig(
    excluded_element_ids={"elem_1", "elem_2"},  # Keep these elements in place
    spacing=60,
)

result = apply_layout(view, config)
```

## Format Elements Without Repositioning

```python
from pyArchimate.view.layout import apply_format

# Standardize element sizes and fonts without changing positions
result = apply_format(view)

print(f"Formatted {result.total_elements} elements")
save_view(result.view, "architecture_formatted.archimate")
```

## Advanced Configuration

### Fine-Tune Connection Routing

```python
from pyArchimate.view.layout import LayoutConfig, apply_layout

config = LayoutConfig(
    # Allow 45° angles as fallback if orthogonal routing creates >10 crossings
    routing_style="mixed",
    max_crossings_for_orthogonal=10,
    
    # Ensure labels don't overlap
    minimize_label_overlap=True,
)

result = apply_layout(view, config)
```

### Prioritize Layer Constraints

```python
from pyArchimate.view.layout import LayoutConfig, apply_layout

config = LayoutConfig(
    # Strictly enforce Business → Application → Technology ordering
    respect_archimate_layers=True,
    layer_priority=True,  # Layer constraints override crossing reduction
)

result = apply_layout(view, config)
```

### Tune Performance for Large Views

```python
from pyArchimate.view.layout import LayoutConfig, apply_layout

config = LayoutConfig(
    # Auto-calculate iterations based on element count
    # Override if you know the optimal value for your model
    max_iterations=500,
    
    # Stop iteration early if elements move less than this threshold
    convergence_threshold=0.05,  # Tighter threshold = faster convergence
)

result = apply_layout(view, config)
```

## Undo/Rollback

```python
from pyArchimate.view.layout import apply_layout, undo_layout

view = load_view("architecture.archimate")

# Apply layout
result1 = apply_layout(view)

if result1.layout_quality == "poor":
    # Revert to original
    view = undo_layout(result1.view)
    
    # Try again with different settings
    config = LayoutConfig(algorithm="hierarchical", spacing=70)
    result2 = apply_layout(view, config)
```

## Troubleshooting

### Layout Quality is "Poor"

**Symptom**: Result shows `layout_quality="poor"` or many crossings

**Causes**:
- View is very dense (many elements/connections)
- Conflicting constraints (e.g., tight spacing + many large elements)

**Solutions**:

```python
# Increase spacing
config = LayoutConfig(spacing=100)

# Try hierarchical if using force-directed
config = LayoutConfig(algorithm="hierarchical")

# Allow more iterations for convergence
config = LayoutConfig(max_iterations=1000)

# Reduce layer_priority if layers are too constraining
config = LayoutConfig(layer_priority=False)  # Allow crossing reduction to override layers
```

### Layout Takes Too Long

**Symptom**: `layout_time_ms` exceeds performance threshold

**Causes**:
- View has >500 elements
- max_iterations is too high

**Solutions**:

```python
# Reduce iterations (may sacrifice quality)
config = LayoutConfig(max_iterations=100, convergence_threshold=0.5)

# Split large views into multiple smaller views
# (Manual; requires domain knowledge)

# Use hierarchical if view has structure
config = LayoutConfig(algorithm="hierarchical")
```

### Elements Overlap After Layout

**Symptom**: SC-002 violation (elements overlapping)

**Causes**:
- Very large elements with tight spacing
- Conflicting constraints

**Solutions**:

```python
# Increase spacing
config = LayoutConfig(spacing=120)

# Exclude problematic elements
config = LayoutConfig(excluded_element_ids={"problem_elem_id"})

# Use hierarchical layout (typically produces cleaner non-overlapping layouts)
config = LayoutConfig(algorithm="hierarchical")
```

### Connection Labels Overlap

**Symptom**: SC-005 or label readability issues

**Causes**:
- Dense diagram with many long labels
- Labels positioned by fallback strategy

**Solutions**:

```python
# Increase spacing to give labels more room
config = LayoutConfig(spacing=80, margin=40)

# Ensure label overlap minimization is enabled
config = LayoutConfig(minimize_label_overlap=True)

# Manually edit labels in the view after layout
# (Some labels may be truncated or repositioned)
```

## Common Patterns

### Organizational Hierarchy

```python
# Best practice for org charts / hierarchical structures
config = LayoutConfig(
    algorithm="hierarchical",
    spacing=60,
    alignment="grid",
    respect_archimate_layers=True,
)
result = apply_layout(view, config)
```

### Enterprise Architecture (Mixed Relationships)

```python
# Best practice for complex EA models with cross-layer relationships
config = LayoutConfig(
    algorithm="force_directed",
    spacing=70,
    layer_priority=True,  # Keep Business > App > Tech strict
    routing_style="orthogonal",  # Clean orthogonal routing
)
result = apply_layout(view, config)
```

### Dense View (Many Elements)

```python
# Best practice for large, dense diagrams (>200 elements)
config = LayoutConfig(
    algorithm="hierarchical",  # Usually faster convergence
    spacing=100,  # Extra spacing to minimize overlaps
    max_iterations=500,  # Reasonable limit
    convergence_threshold=0.2,  # Relax convergence for speed
)
result = apply_layout(view, config)
```

### Read-Only / Archival Views

```python
# Just format without repositioning
result = apply_format(view)

# Or light layout with large margin
config = LayoutConfig(spacing=50, margin=50, excluded_element_ids=view.all_element_ids)
# (Excluding all elements effectively disables repositioning while formatting connections)
```

## Performance Expectations

| View Size | Algorithm | Expected Time |
|-----------|-----------|----------------|
| <50 elements | force_directed | <100ms |
| 50-150 elements | force_directed | 100-500ms |
| 150-300 elements | force_directed | 500ms-2s |
| 300-500 elements | force_directed | 2-5s |
| <50 elements | hierarchical | <50ms |
| 50-150 elements | hierarchical | 50-200ms |
| 150-300 elements | hierarchical | 200-800ms |
| 300-500 elements | hierarchical | 800ms-3s |

*Times are approximate and depend on hardware and diagram complexity.*

## API Reference

For detailed API documentation, see [contracts/layout-api.md](contracts/layout-api.md).

## Next Steps

1. **Try it**: Apply layout to one of your existing views
2. **Explore algorithms**: Compare force-directed vs. hierarchical on your models
3. **Customize**: Adjust spacing, alignment, and other settings for your use case
4. **Integrate**: Use the API in automated pipelines or tooling

## Support

For issues, questions, or feature requests, refer to the [specification](spec.md) or the [research document](research.md) for design details.
