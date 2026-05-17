# Data Model: P3 Notation Support

**Status**: Design Complete (Phase 1)  
**Based On**: Phase 1 audit and design documents  
**Implementation**: Phase 2+

---

## Entity Overview

P3 adds hierarchy tracking and visual properties to existing Element and Model entities. No new entity classes are introduced; instead, existing classes are enhanced with new attributes and methods.

---

## Entity: Element

### Existing Attributes (from audit)

```python
_uuid: str                          # Immutable identifier (generated UUID)
parent: Model                       # Reference to parent model
model: Model                        # Alias for parent (backward compat)
name: Optional[str]                 # Element name
_type: Optional[str]                # ArchiMate type (e.g., BusinessProcess)
desc: Optional[str]                 # Documentation text
folder: Optional[str]               # Folder path (metadata, independent of grouping)
_properties: dict[str, object]      # Generic key-value properties
_profile: Optional[str]             # Profile UUID reference
junction_type: Optional[str]        # AND/OR/XOR (P2, line 112)
_viewpoints: list[str]              # Assigned viewpoint slugs (P2, line 113)
```

### NEW: P3 Attributes

| Attribute | Type | Default | Mutable | Purpose |
|-----------|------|---------|---------|---------|
| `_parent_uuid` | Optional[str] | None | No¹ | UUID of parent element (or None if root) |
| `_visual_style` | dict[str, Any] | {} | Yes | Visual properties (fillColor, lineColor, lineWidth, transparency) |

¹ Mutation only via Model.add_child() / Model.remove_child()

### NEW: P3 Properties

```python
@property
def parent_uuid(self) -> Optional[str]:
    """Return UUID of parent element, or None if root."""
    return self._parent_uuid
```

### NEW: P3 Visual Style API

#### Setters (validate on set; raise ValueError on invalid)

```python
def set_fill_color(self, color: Optional[str]) -> None:
    """Set fill color (hex #RRGGBB or named color). Normalizes to lowercase hex."""
    # Validates hex format or named color
    # Raises: ValueError if invalid

def set_line_color(self, color: Optional[str]) -> None:
    """Set line color. Normalizes to lowercase hex."""

def set_line_width(self, width: Optional[float]) -> None:
    """Set line width (pixels). Must be non-negative."""
    # Raises: ValueError if negative

def set_transparency(self, alpha: Optional[float]) -> None:
    """Set transparency (0.0-1.0). 0=invisible, 1=opaque."""
    # Raises: ValueError if out of range

def set_visual_style(self,
                     fill_color: Optional[str] = None,
                     line_color: Optional[str] = None,
                     line_width: Optional[float] = None,
                     transparency: Optional[float] = None) -> None:
    """Set multiple visual properties. Only provided args are updated."""
```

#### Getters (return stored value or None)

```python
def get_fill_color(self) -> Optional[str]:
    """Return fill color (hex) or None (use default)."""

def get_line_color(self) -> Optional[str]:
    """Return line color (hex) or None (use default)."""

def get_line_width(self) -> Optional[float]:
    """Return line width (pixels) or None (use default)."""

def get_transparency(self) -> Optional[float]:
    """Return transparency (0.0-1.0) or None (use default)."""

def get_visual_style(self) -> dict[str, Any]:
    """Return copy of visual style dict (keys: fillColor, lineColor, lineWidth, transparency)."""
```

#### Reset

```python
def reset_visual_style(self) -> None:
    """Clear all custom visual styles; use defaults."""
```

### MODIFY: Element.delete()

**Existing Behavior**: Delete from model, remove visual nodes, delete relationships

**New Behavior (P3)**: Also orphan children

```python
def delete(self) -> None:
    """
    Delete element from model.
    - Removes from elems_dict
    - Deletes all nodes referencing this element
    - Deletes all relationships (source or target)
    - NEW: Orphans children (sets parent_uuid = None)
    """
```

---

## Entity: Model

### Existing Attributes (from audit)

```python
_uuid: str                          # Model identifier
name: Optional[str]                 # Model name
desc: Optional[str]                 # Model documentation
_properties: dict[str, object]      # Model-level properties
pdefs: dict                         # Unknown (legacy)
_profiles_dict: dict[str, Profile]  # Profiles by UUID
elems_dict: dict[str, Element]      # Elements by UUID
rels_dict: dict[str, Relationship]  # Relationships by UUID
nodes_dict: dict[str, Node]         # Visual nodes by UUID
conns_dict: dict[str, Connection]   # Visual connections by UUID
views_dict: dict[str, View]         # Views/diagrams by UUID
labels_dict: dict[str, Any]         # Labels by UUID
orgs: defaultdict(list)             # Organization structure
theme: str                          # Color theme ('archi' or 'aris')
_viewpoint_elements: dict[str, set[str]]  # Viewpoint → element UUIDs (P2)
_viewpoint_views: dict[str, str]          # View UUID → viewpoint slug (P2)
```

### NEW: P3 Attributes

| Attribute | Type | Default | Purpose |
|-----------|------|---------|---------|
| `_element_hierarchy` | dict[str, Optional[str]] | {} | Child UUID → Parent UUID mapping |
| `_element_children` | dict[str, set[str]] | {} | Parent UUID → Set of Child UUIDs |

### Invariants (enforced in mutation methods)

1. **Acyclic**: If A is parent of B, B cannot be parent of A (no cycles)
2. **Unique Parent**: Each element has ≤1 parent
3. **Max Depth**: No element deeper than 5 levels
4. **Bidirectional Consistency**:
   - If `_element_hierarchy[child] = parent`, then `parent ∈ _element_children[parent]`
   - If `parent ∈ _element_children[parent]`, then `_element_hierarchy[child] = parent`
5. **Element Sync**: `Element._parent_uuid == _element_hierarchy.get(element.uuid)`

### NEW: P3 Mutation API

```python
def add_child(self, parent_uuid: str, child_uuid: str) -> None:
    """
    Assign parent_uuid as parent of child_uuid.
  
    Validations:
    - Parent and child UUIDs must exist in model
    - Child must not already have a parent
    - No cycles allowed (checked via _would_create_cycle)
    - Max depth not exceeded (checked via _get_depth)
  
    Raises:
    - KeyError: If UUID not in model
    - ValueError: If validation fails (parent exists, cycle, depth)
  
    Updates:
    - Element._parent_uuid = parent_uuid
    - Model._element_hierarchy[child_uuid] = parent_uuid
    - Model._element_children[parent_uuid].add(child_uuid)
    """

def remove_child(self, parent_uuid: str, child_uuid: str) -> None:
    """
    Remove parent-child relationship. Child becomes root.
  
    Validations:
    - Both UUIDs must exist in model
    - Relationship must exist (child is actually child of parent)
  
    Raises:
    - KeyError: If UUID not in model
    - ValueError: If relationship doesn't exist
  
    Updates:
    - Element._parent_uuid = None
    - Delete from _element_hierarchy[child_uuid]
    - Remove from _element_children[parent_uuid]
    """
```

### NEW: P3 Query API

```python
def get_parent(self, elem_uuid: str) -> Optional[Element]:
    """
    Return parent element of elem_uuid, or None if root.
  
    O(1) lookup via _element_hierarchy
    """

def get_children(self, elem_uuid: str) -> list[Element]:
    """
    Return all direct children of elem_uuid.
  
    O(n) where n = number of children
    """

def get_ancestors(self, elem_uuid: str) -> list[Element]:
    """
    Return all ancestors from elem_uuid up to root (inclusive).
  
    O(depth), max depth 5 → O(1) practical
    Returns: [elem_uuid, parent, grandparent, ..., root]
    """

def get_descendants(self, elem_uuid: str) -> list[Element]:
    """
    Return all descendants of elem_uuid (breadth-first).
  
    O(subtree_size) traversal
    Returns: [child1, child2, grandchild1, ...] (excludes elem_uuid)
    """

def get_depth(self, elem_uuid: str) -> int:
    """
    Get nesting depth of elem_uuid (0 = root, 1 = direct child, ...).
  
    O(depth), max depth 5 → O(1) practical
    """

def get_root_elements(self) -> list[Element]:
    """
    Return all elements with no parent (depth = 0).
  
    O(n) scan of _element_hierarchy
    """

def get_leaf_elements(self) -> list[Element]:
    """
    Return all elements with no children.
  
    O(n) scan of _element_children
    """
```

### NEW: P3 Private Helpers

```python
def _would_create_cycle(self, parent_uuid: str, child_uuid: str) -> bool:
    """
    Check if adding parent→child link would create cycle.
  
    Algorithm: Walk up from parent_uuid; if we reach child_uuid, cycle detected.
  
    O(depth), max depth 5 → O(1) practical
    Returns: True if cycle would occur, False if safe
    """

def _get_depth(self, elem_uuid: str) -> int:
    """
    Get nesting depth of elem_uuid.
  
    Used internally by add_child() to enforce max depth.
    O(depth), max depth 5 → O(1) practical
    """
```

---

## Constants

### Color Constants

```python
# Named color mapping (CSS/X11 standard)
NAMED_COLORS = {
    'aliceblue': '#f0f8ff',
    'antiquewhite': '#faebd7',
    'aqua': '#00ffff',
    'aquamarine': '#7fffd4',
    'azure': '#f0ffff',
    'beige': '#f5f5dc',
    'bisque': '#ffe4c4',
    'black': '#000000',
    'blanchedalmond': '#ffebcd',
    'blue': '#0000ff',
    'blueviolet': '#8a2be2',
    'brown': '#a52a2a',
    'burlywood': '#deb887',
    'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00',
    'chocolate': '#d2691e',
    'coral': '#ff7f50',
    'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc',
    'crimson': '#dc143c',
    'cyan': '#00ffff',
    'darkblue': '#00008b',
    'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9',
    'darkgrey': '#a9a9a9',
    'darkgreen': '#006400',
    'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00',
    'darkorchid': '#9932cc',
    'darkred': '#8b0000',
    'darksalmon': '#e9967a',
    'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f',
    'darkslategrey': '#2f4f4f',
    'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3',
    'deeppink': '#ff1493',
    'deepskyblue': '#00bfff',
    'dimgray': '#696969',
    'dimgrey': '#696969',
    'dodgerblue': '#1e90ff',
    'firebrick': '#b22222',
    'floralwhite': '#fffaf0',
    'forestgreen': '#228b22',
    'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc',
    'ghostwhite': '#f8f8ff',
    'gold': '#ffd700',
    'goldenrod': '#daa520',
    'gray': '#808080',
    'grey': '#808080',
    'green': '#008000',
    'greenyellow': '#adff2f',
    'honeydew': '#f0fff0',
    'hotpink': '#ff69b4',
    'indianred': '#cd5c5c',
    'indigo': '#4b0082',
    'ivory': '#fffff0',
    'khaki': '#f0e68c',
    'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5',
    'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6',
    'lightcoral': '#f08080',
    'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2',
    'lightgray': '#d3d3d3',
    'lightgrey': '#d3d3d3',
    'lightgreen': '#90ee90',
    'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa',
    'lightskyblue': '#87cefa',
    'lightslategray': '#778899',
    'lightslategrey': '#778899',
    'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0',
    'lime': '#00ff00',
    'limegreen': '#32cd32',
    'linen': '#faf0e6',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370db',
    'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a',
    'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585',
    'midnightblue': '#191970',
    'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5',
    'navajowhite': '#ffdead',
    'navy': '#000080',
    'oldlace': '#fdf5e6',
    'olive': '#808000',
    'olivedrab': '#6b8e23',
    'orange': '#ffa500',
    'orangered': '#ff4500',
    'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa',
    'palegreen': '#98fb98',
    'paleturquoise': '#afeeee',
    'palevioletred': '#db7093',
    'papayawhip': '#ffefd5',
    'peachpuff': '#ffdab9',
    'peru': '#cd853f',
    'pink': '#ffc0cb',
    'plum': '#dda0dd',
    'powderblue': '#b0e0e6',
    'purple': '#800080',
    'red': '#ff0000',
    'rosybrown': '#bc8f8f',
    'royalblue': '#4169e1',
    'saddlebrown': '#8b4513',
    'salmon': '#fa8072',
    'sandybrown': '#f4a460',
    'seagreen': '#2e8b57',
    'seashell': '#fff5ee',
    'sienna': '#a0522d',
    'silver': '#c0c0c0',
    'skyblue': '#87ceeb',
    'slateblue': '#6a5acd',
    'slategray': '#708090',
    'slategrey': '#708090',
    'snow': '#fffafa',
    'springgreen': '#00ff7f',
    'steelblue': '#4682b4',
    'tan': '#d2b48c',
    'teal': '#008080',
    'thistle': '#d8bfd8',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    'wheat': '#f5deb3',
    'white': '#ffffff',
    'whitesmoke': '#f5f5f5',
    'yellow': '#ffff00',
    'yellowgreen': '#9acd32'
}

# Standard ArchiMate palette (default fill colors by category)
STANDARD_PALETTE = {
    'strategy': '#F5DEAA',
    'business': '#FFFFB5',
    'application': '#B5FFFF',
    'technology': '#C9E7B7',
    'physical': '#C9E7B7',
    'migration': '#FFE0E0',
    'motivation': '#CCCCFF',
    'implementation': '#FFE0E0',
    'relationship': '#DDDDDD',
    'junction': '#000000',
    'other': '#FFFFFF'
}

# Maximum nesting depth
MAX_DEPTH = 5
```

---

## Validation Rules

### Color Validation

```python
def _normalize_color(color: Optional[str]) -> Optional[str]:
    """
    Normalize color to lowercase hex (#rrggbb).
  
    Accepts:
    - Hex: #RRGGBB (any case) → lowercase
    - Named: 'red', 'blue', etc. → hex conversion
    - None: → None (use defaults)
  
    Raises: ValueError if invalid format
    """
```

### Hierarchy Validation

```python
# Cycle detection (called before add_child)
_would_create_cycle(parent_uuid, child_uuid) -> bool

# Depth check (called before add_child)
_get_depth(elem_uuid) -> int  # Raises if >= MAX_DEPTH

# Unique parent (checked before add_child)
# Raises if child._parent_uuid is not None
```

### Numeric Validation

```python
# Line width: must be >= 0
# Transparency: must be in [0.0, 1.0]
```

---

## State Transitions

### Element State

```
Element created with _parent_uuid = None (root)
    ↓
add_child(parent, elem)
    ↓
Element has _parent_uuid = parent (child)
    ↓
remove_child(parent, elem)
    ↓
Element has _parent_uuid = None (orphaned)
```

### Visual Style State

```
Element created with _visual_style = {} (all defaults)
    ↓
set_fill_color('red')
    ↓
_visual_style['fillColor'] = '#ff0000'
    ↓
reset_visual_style()
    ↓
_visual_style = {} (back to defaults)
```

---

## Serialization

### XML Element Attributes (new)
- `parentId`: UUID of parent (optional, omitted if None)
- `folder`: Existing folder path (unchanged, independent)

### XML Properties (new)
- `fillColor`: Element fill color (hex)
- `lineColor`: Element border color (hex)
- `lineWidth`: Element border width (pixels)
- `transparency`: Element opacity (0.0-1.0)

---

**Status**: Complete and ready for Phase 2 implementation
