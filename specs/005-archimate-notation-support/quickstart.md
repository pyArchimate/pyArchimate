# Quick Start: P3 Notation Support

**Target Audience**: Developers integrating P3 features into pyArchimate  
**Level**: Intermediate  
**Time**: 15-30 minutes

---

## Scenario 1: Building Element Hierarchies

### Use Case
Organize a business process into sub-functions and sub-sub-processes.

### Code

```python
from pyArchimate import ArchiType
from pyArchimate.model import Model

# Create model
model = Model('E-Commerce')

# Create top-level process
order_proc = model.add(
    ArchiType.BusinessProcess,
    'Order Processing',
    desc='Main order workflow'
)

# Create level-1 functions
validate_func = model.add(
    ArchiType.BusinessFunction,
    'Validate Order',
    desc='Validates order details'
)
payment_func = model.add(
    ArchiType.BusinessFunction,
    'Process Payment',
    desc='Handles payment'
)
ship_func = model.add(
    ArchiType.BusinessFunction,
    'Ship Order',
    desc='Arranges shipment'
)

# Build hierarchy: Process → [3 Functions]
model.add_child(order_proc.uuid, validate_func.uuid)
model.add_child(order_proc.uuid, payment_func.uuid)
model.add_child(order_proc.uuid, ship_func.uuid)

# Get children
children = model.get_children(order_proc.uuid)
print(f"Order process has {len(children)} sub-functions")
# Output: Order process has 3 sub-functions

# Check depth
depth = model.get_depth(validate_func.uuid)
print(f"Validate function is at depth {depth}")
# Output: Validate function is at depth 1

# Get ancestors
ancestors = model.get_ancestors(validate_func.uuid)
print(f"Ancestors: {[e.name for e in ancestors]}")
# Output: Ancestors: ['Validate Order', 'Order Processing']
```

### Error Handling

```python
# Try to create cycle (error)
try:
    model.add_child(validate_func.uuid, order_proc.uuid)
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Cycle detected: adding ... would create cycle

# Try to re-parent (error)
try:
    model.add_child(payment_func.uuid, validate_func.uuid)
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Element ... already has parent ...
```

---

## Scenario 2: Styling Elements

### Use Case
Customize element colors to match organizational standards and highlight important elements.

### Code

```python
from pyArchimate import ArchiType
from pyArchimate.model import Model

# Create model
model = Model('Styled Architecture')

# Create elements
critical_proc = model.add(
    ArchiType.BusinessProcess,
    'Critical Process'
)
secondary_proc = model.add(
    ArchiType.BusinessProcess,
    'Secondary Process'
)
app = model.add(
    ArchiType.ApplicationComponent,
    'Legacy System'
)

# Style critical process (bright red)
critical_proc.set_fill_color('red')
critical_proc.set_line_color('darkred')
critical_proc.set_line_width(3.0)

# Style secondary process (light blue, semi-transparent)
secondary_proc.set_visual_style(
    fill_color='lightblue',
    line_color='blue',
    transparency=0.7
)

# Style legacy system (faded, narrow border)
app.set_fill_color('#FFD700')  # Gold (hex)
app.set_line_width(0.5)
app.set_transparency(0.6)

# Read styles back
print(f"Critical: {critical_proc.get_visual_style()}")
# Output: {'fillColor': '#ff0000', 'lineColor': '#8b008b', 'lineWidth': 3.0}

print(f"Secondary: {secondary_proc.get_fill_color()}")
# Output: #add8e6  (normalized from 'lightblue')
```

### Named Colors

```python
# Common colors available
colors = [
    'red', 'blue', 'green', 'yellow', 'black', 'white',
    'lightblue', 'darkred', 'orange', 'purple', 'cyan',
    # ... and 130+ more CSS/X11 colors
]

proc.set_fill_color('orange')  # Convenient naming
print(proc.get_fill_color())  # Returns: '#ffa500'
```

---

## Scenario 3: Round-Trip Fidelity

### Use Case
Export model with grouped elements and custom styles, then import and verify preservation.

### Code

```python
from pyArchimate import ArchiType
from pyArchimate.model import Model

# Create complex model
model = Model('Complex')

# Build hierarchy
parent = model.add(ArchiType.BusinessProcess, 'Parent')
child1 = model.add(ArchiType.BusinessFunction, 'Child 1')
child2 = model.add(ArchiType.BusinessFunction, 'Child 2')
grandchild = model.add(ArchiType.BusinessProcess, 'Grandchild')

model.add_child(parent.uuid, child1.uuid)
model.add_child(parent.uuid, child2.uuid)
model.add_child(child1.uuid, grandchild.uuid)

# Add visual styles
parent.set_visual_style(fill_color='#FFFFB5', transparency=1.0)
child1.set_fill_color('lightblue')
grandchild.set_visual_style(
    fill_color='#FFE0E0',
    line_color='#FF6F00',
    line_width=2.0,
    transparency=0.9
)

# Export
model.write('complex_model.archimate')
print("Model exported")

# Import back
model2 = Model()
model2.read('complex_model.archimate')

# Verify hierarchy preserved
parent2 = model2.find_elements(name='Parent')[0]
children2 = model2.get_children(parent2.uuid)
print(f"Preserved {len(children2)} children")
# Output: Preserved 2 children

# Verify styles preserved
grandchild2 = model2.find_elements(name='Grandchild')[0]
style = grandchild2.get_visual_style()
print(f"Grandchild style: {style}")
# Output: Grandchild style: {'fillColor': '#ffe0e0', 'lineColor': '#ff6f00', 'lineWidth': 2.0, 'transparency': 0.9}

# Verify hierarchy
assert grandchild2.parent_uuid == children2[0].uuid
print("✓ All hierarchy and styles preserved!")
```

---

## Scenario 4: Querying Hierarchies

### Use Case
Analyze model structure to find all processes, functions, and their relationships.

### Code

```python
from pyArchimate import ArchiType
from pyArchimate.model import Model

# Load existing model
model = Model()
model.read('large_model.archimate')

# Find all root elements
roots = model.get_root_elements()
print(f"Root elements: {len(roots)}")
for root in roots:
    print(f"  - {root.name} (type: {root.type})")

# Find all leaf elements (most detailed level)
leaves = model.get_leaf_elements()
print(f"Leaf elements: {len(leaves)}")

# Analyze hierarchy depths
depth_dist = {}
for elem in model.elements:
    depth = model.get_depth(elem.uuid)
    depth_dist[depth] = depth_dist.get(depth, 0) + 1

print("Depth distribution:")
for depth in sorted(depth_dist.keys()):
    print(f"  Level {depth}: {depth_dist[depth]} elements")

# Find all processes with children (composite processes)
for elem in model.elements:
    if elem.type == 'BusinessProcess':
        children = model.get_children(elem.uuid)
        if children:
            print(f"Composite: {elem.name} ({len(children)} children)")
```

---

## Scenario 5: Complex Mixed Features

### Use Case
Build a complete enterprise architecture with grouping, junction semantics, and visual styling.

### Code

```python
from pyArchimate import ArchiType
from pyArchimate.model import Model

model = Model('Enterprise EA')

# Business Layer: Order Processing
order_proc = model.add(ArchiType.BusinessProcess, 'Order Processing')
order_proc.set_fill_color('#FFFFB5')

# Sub-processes
validate = model.add(ArchiType.BusinessFunction, 'Validate')
validate.set_fill_color('#FFE0B2')

ship = model.add(ArchiType.BusinessFunction, 'Ship')
ship.set_fill_color('#FFE0B2')

model.add_child(order_proc.uuid, validate.uuid)
model.add_child(order_proc.uuid, ship.uuid)

# Junctions for routing
and_junc = model.add(ArchiType.Junction, 'AND Gate')
and_junc.prop('junctionType', 'and')

xor_junc = model.add(ArchiType.Junction, 'XOR Gate')
xor_junc.prop('junctionType', 'xor')

# Make junctions part of order process
model.add_child(order_proc.uuid, and_junc.uuid)
model.add_child(order_proc.uuid, xor_junc.uuid)

# Application Layer: IT Systems
erp = model.add(ArchiType.ApplicationComponent, 'ERP System')
erp.set_visual_style(fill_color='#B5FFFF', transparency=1.0)

warehouse = model.add(ArchiType.ApplicationComponent, 'Warehouse System')
warehouse.set_visual_style(fill_color='#B5FFFF', line_width=1.5)

model.add_child(erp.uuid, warehouse.uuid)

# Relationships
val_rel = model.add_relationship(
    rel_type=ArchiType.RealizationRelationship,
    source=erp,
    target=order_proc,
    name='Realizes'
)

ship_rel = model.add_relationship(
    rel_type=ArchiType.FlowRelationship,
    source=and_junc,
    target=warehouse,
    name='Flows to'
)

# Verify structure
print(f"Business hierarchy depth: {model.get_depth(and_junc.uuid)}")
print(f"App hierarchy depth: {model.get_depth(warehouse.uuid)}")
print(f"Root elements: {len(model.get_root_elements())}")
print(f"Descendants of ERP: {len(model.get_descendants(erp.uuid))}")

# Export
model.write('enterprise_ea.archimate')
print("✓ Enterprise model exported with all features!")
```

---

## Error Handling Patterns

### Cycle Prevention

```python
try:
    model.add_child(child.uuid, parent.uuid)
except ValueError as e:
    print(f"Cycle prevented: {e}")
```

### Depth Limits

```python
try:
    # Try to add 6th level
    model.add_child(level_4.uuid, level_5.uuid)
except ValueError as e:
    print(f"Depth limit: {e}")
    # Output: Error: Max nesting depth 5 exceeded
```

### Color Validation

```python
try:
    elem.set_fill_color('#GGGGGG')  # Invalid hex
except ValueError as e:
    print(f"Color error: {e}")
    # Output: Invalid hex color: #GGGGGG (expected #RRGGBB)

try:
    elem.set_fill_color('rainbow')  # Unknown color
except ValueError as e:
    print(f"Color error: {e}")
    # Output: Unknown color: rainbow (hex or named color expected)
```

### Range Validation

```python
try:
    elem.set_line_width(-1)  # Negative width
except ValueError as e:
    print(f"Width error: {e}")

try:
    elem.set_transparency(1.5)  # Out of range
except ValueError as e:
    print(f"Transparency error: {e}")
    # Output: Transparency must be 0.0-1.0, got 1.5
```

---

## API Quick Reference

### Hierarchy APIs

| Method | Purpose |
|--------|---------|
| `model.add_child(parent_uuid, child_uuid)` | Create parent-child relationship |
| `model.remove_child(parent_uuid, child_uuid)` | Remove relationship (orphan child) |
| `model.get_parent(elem_uuid)` | Get parent element |
| `model.get_children(elem_uuid)` | Get all direct children |
| `model.get_ancestors(elem_uuid)` | Get all ancestors up to root |
| `model.get_descendants(elem_uuid)` | Get all descendants (BFS) |
| `model.get_depth(elem_uuid)` | Get nesting depth |
| `model.get_root_elements()` | Get all roots (no parent) |
| `model.get_leaf_elements()` | Get all leaves (no children) |

### Visual Style APIs

| Method | Purpose |
|--------|---------|
| `elem.set_fill_color(color)` | Set fill color |
| `elem.set_line_color(color)` | Set line color |
| `elem.set_line_width(width)` | Set line width |
| `elem.set_transparency(alpha)` | Set transparency |
| `elem.set_visual_style(...)` | Set multiple properties |
| `elem.get_fill_color()` | Get fill color |
| `elem.get_line_color()` | Get line color |
| `elem.get_line_width()` | Get line width |
| `elem.get_transparency()` | Get transparency |
| `elem.get_visual_style()` | Get all properties |
| `elem.reset_visual_style()` | Clear all custom styles |

---

## Best Practices

1. **Always validate on read**: Check model structures after import
2. **Use named colors for clarity**: More readable than hex for common colors
3. **Consistent styling**: Use similar colors for similar element types
4. **Document hierarchies**: Use element names and descriptions to document structure
5. **Test round-trip**: Always export/import test to verify fidelity
6. **Respect depth limits**: Keep hierarchies to 3-4 levels for clarity
7. **Check for roots**: Use `get_root_elements()` to identify top-level processes

---

## Next Steps

- **For Unit Testing**: See `/tests/unit/test_element_grouping.py` and `/tests/unit/test_visual_style.py`
- **For Integration Testing**: See `/tests/integration/test_round_trip_*.py`
- **For BDD Scenarios**: See `/tests/features/grouping.feature` and `/tests/features/visual_style.feature`
- **For API Details**: See `/specs/005-archimate-notation-support/contracts/`

---

**Ready to build!** 🚀
