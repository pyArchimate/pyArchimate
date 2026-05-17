# Quickstart: Auto-Layout and Auto-Routing

**Branch**: `013-layout-routing-refactor`

## Two independent functions

```python
from pyArchimate.view.layout import auto_layout, auto_route, LayoutConfig, RoutingConfig

# Load a view (existing API)
view = model.views[0]

# 1. Layout only: reposition nodes in layer order on coarse grid
result = auto_layout(view)
print(f"Laid out {result.elements_processed} nodes in {result.layout_time_ms:.0f}ms")
if result.warnings:
    print("Warnings:", result.warnings)

# 2. Route only: reroute connections avoiding nodes
result = auto_route(view)
print(f"Routed {result.connections_processed} connections")
if result.warnings:
    # Each warning = one skipped connection with reason
    print("Skipped connections:", result.warnings)

# 3. Chain (full cleanup)
auto_layout(view)
auto_route(view)

# 4. Existing apply_layout() still works (calls auto_layout + auto_route internally)
from pyArchimate.view.layout import apply_layout
result = apply_layout(view)
```

## Configuration

```python
# Custom grid size
result = auto_layout(view, LayoutConfig(grid_size=80.0))

# Horizontal layer ordering (Business left → Technology right)
result = auto_layout(view, LayoutConfig(layer_direction="horizontal"))

# Custom routing clearances
result = auto_route(view, RoutingConfig(min_segment_gap=15.0, corner_clearance_pct=0.15))
```

## Result object

```python
result.success             # bool
result.elements_processed  # int: nodes processed
result.connections_processed  # int: connections processed
result.layout_time_ms      # float: wall time
result.warnings            # list[str]: skipped connections or placement issues
result.error_message       # str | None: set only on hard failure
```

## Verification helpers (for tests)

```python
# Check grid alignment
assert all(node.x % config.grid_size == 0 for node in view.nodes)

# Check layer ordering (vertical)
business_y = [n.y for n in view.nodes if n.layer == "Business"]
app_y      = [n.y for n in view.nodes if n.layer == "Application"]
assert max(business_y) < min(app_y)
```
