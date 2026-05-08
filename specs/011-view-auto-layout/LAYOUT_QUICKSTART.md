# Layout & Format Quick Reference

**Quick reference for auto-layout and auto-format features** | [Full Quickstart](specs/011-view-auto-layout/quickstart.md) | [Technical Specs](specs/011-view-auto-layout/auto-layout-specifications.md)

---

## Import & Basic Usage

```python
from pyArchimate.view import load_view, save_view
from pyArchimate.view.layout import apply_layout, apply_format, undo_layout, LayoutConfig

# Load a view
view = load_view("architecture.archimate")

# Apply layout with defaults
result = apply_layout(view)

# Or with custom config
config = LayoutConfig(algorithm="hierarchical", spacing=70)
result = apply_layout(view, config)

# Format without repositioning
result = apply_format(view)

# Undo last operation
result = undo_layout(view)

# Export as SVG
view.to_svg(filepath="diagram.svg")
```

---

## Algorithm Selection

| Algorithm | Use Case | Speed | Best For |
|-----------|----------|-------|----------|
| `"force_directed"` | Mixed relationships | <2s (300 elem) | General-purpose, exploring connections |
| `"hierarchical"` | Tree-like structure | <500ms (300 elem) | Org charts, hierarchies, dependencies |

**Default**: `"force_directed"`

```python
# Force-directed (default)
result = apply_layout(view)

# Hierarchical for org structures
config = LayoutConfig(algorithm="hierarchical")
result = apply_layout(view, config)
```

---

## Configuration Options

```python
config = LayoutConfig(
    # Algorithm selection
    algorithm="force_directed",      # or "hierarchical"
    
    # Spacing and margins
    spacing=50,                       # Distance between elements (px)
    margin=20,                        # Canvas margin (px)
    
    # Element positioning
    alignment="free",                 # or "grid"
    grid_size=10,                     # Grid cell size if alignment="grid"
    
    # Connection routing
    routing_style="orthogonal",       # or "mixed_45"
    
    # Layer constraints
    layer_priority="mandatory",       # or "soft"
    
    # Element control
    excluded_element_ids={"id1", "id2"},  # Keep these in place
    
    # Size constraints
    node_size_constraints={
        "min_width": 80,
        "max_width": 200,
        "min_height": 50,
        "max_height": 150,
    }
)

result = apply_layout(view, config)
```

---

## Common Patterns

### Organizational Hierarchy

```python
config = LayoutConfig(
    algorithm="hierarchical",
    spacing=60,
    alignment="grid",
)
result = apply_layout(view, config)
```

### Enterprise Architecture (Mixed)

```python
config = LayoutConfig(
    algorithm="force_directed",
    spacing=70,
    layer_priority="mandatory",
    routing_style="orthogonal",
)
result = apply_layout(view, config)
```

### Dense View (Many Elements)

```python
config = LayoutConfig(
    algorithm="hierarchical",
    spacing=100,
    grid_size=10,
)
result = apply_layout(view, config)
```

### Format Only (No Repositioning)

```python
result = apply_format(view, LayoutConfig(
    alignment="grid",
    grid_size=10,
))
```

---

## Working with Results

```python
result = apply_layout(view)

# Check success
if result.success:
    print(f"Layout completed in {result.layout_time_ms}ms")
    print(f"Elements: {result.elements_processed}")
    print(f"Connections: {result.connections_processed}")
else:
    print(f"Error: {result.error_message}")

# Quality metrics
metrics = result.quality_metrics
print(f"Crossings: {metrics.get('crossing_count', 0)}")
print(f"Spacing: {metrics.get('spacing_actual', 'N/A')}")
```

---

## SVG Export

```python
# Export as string
svg_string = view.to_svg()
print(svg_string)  # Valid SVG 1.1

# Export to file
view.to_svg(filepath="diagram.svg")

# With custom colors
view.nodes[0].fill_color = "#FF0000"
svg = view.to_svg(filepath="custom.svg")
```

---

## Undo/Rollback

```python
# Apply layout
result1 = apply_layout(view)

# Try different settings
result2 = undo_layout(view)

# Apply again with different config
config = LayoutConfig(algorithm="hierarchical")
result3 = apply_layout(view, config)

# Multiple undo calls revert multiple steps
undo_layout(view)
undo_layout(view)
```

---

## Troubleshooting

### Layout takes too long

```python
# Reduce iterations for faster (lower quality) results
config = LayoutConfig(
    algorithm="hierarchical",  # Usually faster
    spacing=100,              # Larger spacing = fewer iterations
)
result = apply_layout(view, config)
```

### Elements overlap

```python
# Increase spacing
config = LayoutConfig(spacing=100)
result = apply_layout(view, config)

# Or exclude problem elements
config = LayoutConfig(excluded_element_ids={"problem_id"})
result = apply_layout(view, config)
```

### Connection labels overlap

```python
# Increase spacing to give labels room
config = LayoutConfig(spacing=80, margin=40)
result = apply_layout(view, config)
```

### Layout quality is poor

```python
# Try hierarchical algorithm
config = LayoutConfig(algorithm="hierarchical")
result = apply_layout(view, config)

# Or increase spacing
config = LayoutConfig(spacing=100)
result = apply_layout(view, config)
```

---

## Performance Reference

| Elements | Force-Directed | Hierarchical |
|----------|----------------|--------------|
| 50 | <100ms | <50ms |
| 100 | <200ms | <100ms |
| 300 | <2s | <500ms |
| 500 | <5s | <1s |

*Times approximate; depends on diagram complexity and hardware.*

---

## API Reference

### Functions

- **`apply_layout(view, config=None) → LayoutResult`** — Apply layout algorithm
- **`apply_format(view, config=None) → LayoutResult`** — Format elements without repositioning
- **`undo_layout(view) → LayoutResult`** — Revert last operation
- **`view.to_svg(filepath=None) → str`** — Export view as SVG

### Classes

- **`LayoutConfig`** — Configuration data class with validation
- **`LayoutResult`** — Result with metrics and quality data

### Enums

- **`LayoutAlgorithm`** — "force_directed" or "hierarchical"
- **`Alignment`** — "free" or "grid"
- **`RoutingStyle`** — "orthogonal" or "mixed_45"
- **`LayerPriority`** — "mandatory" or "soft"

---

## See Also

- [Full Quickstart Guide](specs/011-view-auto-layout/quickstart.md) — Detailed examples and workflows
- [Technical Specifications](specs/011-view-auto-layout/auto-layout-specifications.md) — Algorithm details, edge cases, performance
- [API Contracts](specs/011-view-auto-layout/contracts/) — Detailed API documentation
- [Architecture](specs/011-view-auto-layout/ARCHITECTURE.md) — Module structure and design decisions

---

**Version**: 1.0 | **Status**: BETA | **Last Updated**: 2026-05-05
