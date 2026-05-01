# Visual Style Storage Design (T124)

**Date**: 2026-05-01  
**Status**: Complete  
**Based On**: P2 property-based storage pattern  
**Recommendation**: **Option A (Property Dict)** ✅

---

## Executive Summary

Element visual properties (colors, line width, transparency) should be stored in a property dict (`_visual_style`) that mirrors the P2 viewpoint storage pattern. This approach:
- ✅ Matches existing Element._properties pattern
- ✅ Enables easy serialization to XML `<property>` elements
- ✅ Allows future additions without code changes
- ✅ Provides flexible color validation

---

## Approach Comparison

### Option A: Property Dict ✅ RECOMMENDED

**Storage**:
```python
self._visual_style: dict[str, Any] = {
    'fillColor': '#0066FF',
    'lineColor': '#000000',
    'lineWidth': 2.0,
    'transparency': 0.8
}
```

**Pros**:
- Mirrors P2 viewpoint pattern (uses dicts)
- Flexible: add new properties without code changes
- Serializes directly to XML `<property>` elements
- Property keys match XML attribute names exactly
- Handles None values gracefully
- Easy to iterate/export

**Cons**:
- No type hints for dict values
- Must validate keys at runtime (no static guarantee)

**Best For**: Our codebase (consistent with existing patterns)

---

### Option B: Dataclass

**Storage**:
```python
@dataclass
class VisualStyle:
    fill_color: Optional[str] = None
    line_color: Optional[str] = None
    line_width: Optional[float] = None
    transparency: Optional[float] = None

self._visual_style: VisualStyle = VisualStyle()
```

**Pros**:
- Type-safe (type hints)
- Clear attribute names
- IDE autocomplete support

**Cons**:
- Requires new class definition
- Harder to serialize (must convert to dict)
- Future additions require code changes
- Breaks consistency with P2 pattern

---

### Option C: Individual Attributes

**Storage**:
```python
self.fill_color: Optional[str] = None
self.line_color: Optional[str] = None
self.line_width: Optional[float] = None
self.transparency: Optional[float] = None
```

**Pros**:
- Simple (no nested dict)
- Clear attribute names

**Cons**:
- Pollutes Element namespace
- Harder to iterate/export
- Inconsistent with existing Element._properties pattern
- Not extensible (adding new property = new attribute)

---

## Chosen Design: Property Dict (Option A)

### Storage Structure

**New Attribute in Element** (add to `__init__()` after line 113):

```python
self._visual_style: dict[str, Any] = {}  # Empty on init; values set via setters
```

**Key Names** (match Archi tool and ArchiMate spec):
- `'fillColor'` → Element fill color (hex or named color)
- `'lineColor'` → Element border color
- `'lineWidth'` → Element border width (float, pixels)
- `'transparency'` → Element transparency (float, 0.0-1.0)

**Format Examples**:
```python
elem._visual_style = {
    'fillColor': '#0066FF',      # Hex color
    'lineColor': '#000000',       # Black border
    'lineWidth': 2.0,             # 2 pixels
    'transparency': 0.8           # 80% opaque
}

# Or with named colors (normalized to lowercase hex):
elem._visual_style = {
    'fillColor': '#ff0000',       # Normalized red
    'lineColor': '#000000',       # Black
    'lineWidth': 1.5,
    'transparency': 1.0           # Fully opaque
}

# Or mixed (None means use default):
elem._visual_style = {
    'fillColor': '#0066FF',
    'lineColor': None,            # Use default line color
    'lineWidth': None,            # Use default width
    'transparency': 1.0           # Fully opaque
}
```

---

## Color Validation Rules

### Color Value Types

**Accepted Formats**:

1. **Hex Colors** (Preferred)
   - Format: `#RRGGBB` or `#rrggbb` (case-insensitive)
   - Examples: `#FF0000`, `#ff0000`, `#0066FF`
   - Normalized: Converted to lowercase `#rrggbb`
   - Validation: Regex `^#[0-9a-fA-F]{6}$`

2. **Named Colors** (Convenience)
   - Examples: `'red'`, `'blue'`, `'white'`, `'black'`
   - Case-insensitive; normalized to lowercase
   - Maps to hex via standard color palette
   - Supported: CSS/X11 standard colors (140+ colors)

3. **None** (Default)
   - Means use standard ArchiMate palette default for element type
   - Serialized: Omitted from XML (will default on read)

### Color Normalization

```python
def _normalize_color(color: Optional[str]) -> Optional[str]:
    """
    Normalize color to lowercase hex format.
    
    Args:
        color: Hex (#RRGGBB), named color, or None
        
    Returns:
        Normalized lowercase hex, or None
        
    Raises:
        ValueError: if color format invalid
    """
    if color is None:
        return None
    
    color = str(color).strip()
    
    # If hex format: validate and normalize
    if color.startswith('#'):
        if not re.match(r'^#[0-9a-fA-F]{6}$', color):
            raise ValueError(f"Invalid hex color: {color} (expected #RRGGBB)")
        return color.lower()
    
    # If named color: convert to hex
    named_color_hex = NAMED_COLORS.get(color.lower())
    if named_color_hex:
        return named_color_hex.lower()
    
    # Invalid format
    raise ValueError(f"Unknown color: {color} (hex or named color expected)")
```

### Standard ArchiMate Palette

Default fill colors by element category (Archi theme):

```python
STANDARD_PALETTE = {
    'strategy': '#F5DEAA',
    'business': '#FFFFB5',        # Business elements
    'application': '#B5FFFF',     # Application elements
    'technology': '#C9E7B7',      # Technology elements
    'physical': '#C9E7B7',        # Physical elements
    'migration': '#FFE0E0',       # Migration elements
    'motivation': '#CCCCFF',      # Motivation elements
    'implementation': '#FFE0E0',  # Implementation elements
    'relationship': '#DDDDDD',    # Relationships
    'junction': '#000000',        # Junctions
    'other': '#FFFFFF'            # Default
}
```

**Fallback Colors**:
- Line color: `#000000` (black)
- Line width: `1.0` (pixels)
- Transparency: `1.0` (fully opaque)

---

## Public API: Getter & Setter Methods

### Style Getters

**`get_visual_style() → dict[str, Any]`** (Read all properties)

```python
def get_visual_style(self) -> dict[str, Any]:
    """
    Return a copy of the visual style dict.
    
    Returns:
        dict with keys: 'fillColor', 'lineColor', 'lineWidth', 'transparency'
        Values may be None (use defaults)
    """
    return dict(self._visual_style)  # Return copy, not reference
```

**`get_fill_color() → Optional[str]`**

```python
def get_fill_color(self) -> Optional[str]:
    """Return fill color (hex) or None (use default)."""
    return self._visual_style.get('fillColor')
```

**`get_line_color() → Optional[str]`**

```python
def get_line_color(self) -> Optional[str]:
    """Return line color (hex) or None (use default)."""
    return self._visual_style.get('lineColor')
```

**`get_line_width() → Optional[float]`**

```python
def get_line_width(self) -> Optional[float]:
    """Return line width (pixels) or None (use default)."""
    return self._visual_style.get('lineWidth')
```

**`get_transparency() → Optional[float]`**

```python
def get_transparency() -> Optional[float]:
    """Return transparency (0.0-1.0) or None (use default)."""
    return self._visual_style.get('transparency')
```

### Style Setters

**`set_visual_style(fill_color=None, line_color=None, line_width=None, transparency=None) → None`** (Set multiple properties)

```python
def set_visual_style(self, 
                     fill_color: Optional[str] = None,
                     line_color: Optional[str] = None,
                     line_width: Optional[float] = None,
                     transparency: Optional[float] = None) -> None:
    """
    Set visual style properties (only set provided arguments).
    
    Args:
        fill_color: Hex (#RRGGBB), named color, or None
        line_color: Hex (#RRGGBB), named color, or None
        line_width: Float (pixels) or None
        transparency: Float (0.0-1.0) or None
        
    Raises:
        ValueError: if color format invalid or value out of range
    """
    if fill_color is not None:
        self._visual_style['fillColor'] = _normalize_color(fill_color)
    if line_color is not None:
        self._visual_style['lineColor'] = _normalize_color(line_color)
    if line_width is not None:
        if not isinstance(line_width, (int, float)) or line_width < 0:
            raise ValueError(f"Line width must be non-negative number, got {line_width}")
        self._visual_style['lineWidth'] = float(line_width)
    if transparency is not None:
        if not isinstance(transparency, (int, float)) or not (0.0 <= transparency <= 1.0):
            raise ValueError(f"Transparency must be 0.0-1.0, got {transparency}")
        self._visual_style['transparency'] = float(transparency)
```

**`set_fill_color(color: Optional[str]) → None`**

```python
def set_fill_color(self, color: Optional[str]) -> None:
    """Set fill color; raises ValueError if invalid."""
    if color is not None:
        self._visual_style['fillColor'] = _normalize_color(color)
    else:
        self._visual_style.pop('fillColor', None)
```

**`set_line_color(color: Optional[str]) → None`**

```python
def set_line_color(self, color: Optional[str]) -> None:
    """Set line color; raises ValueError if invalid."""
    if color is not None:
        self._visual_style['lineColor'] = _normalize_color(color)
    else:
        self._visual_style.pop('lineColor', None)
```

**`set_line_width(width: Optional[float]) → None`**

```python
def set_line_width(self, width: Optional[float]) -> None:
    """Set line width (pixels); raises ValueError if invalid."""
    if width is not None:
        if not isinstance(width, (int, float)) or width < 0:
            raise ValueError(f"Line width must be non-negative, got {width}")
        self._visual_style['lineWidth'] = float(width)
    else:
        self._visual_style.pop('lineWidth', None)
```

**`set_transparency(alpha: Optional[float]) → None`**

```python
def set_transparency(self, alpha: Optional[float]) -> None:
    """Set transparency (0.0-1.0); raises ValueError if invalid."""
    if alpha is not None:
        if not isinstance(alpha, (int, float)) or not (0.0 <= alpha <= 1.0):
            raise ValueError(f"Transparency must be 0.0-1.0, got {alpha}")
        self._visual_style['transparency'] = float(alpha)
    else:
        self._visual_style.pop('transparency', None)
```

### Reset

**`reset_visual_style() → None`** (Clear all custom styles)

```python
def reset_visual_style(self) -> None:
    """Clear all visual styles; elements will use defaults."""
    self._visual_style.clear()
```

---

## Serialization: XML Mapping

### Write (Export)

**Format**: Store each property as `<property>` XML element

```xml
<element id="id-abc123" name="Business Process">
  <property key="fillColor" value="#FFFFB5"/>
  <property key="lineColor" value="#000000"/>
  <property key="lineWidth" value="1.5"/>
  <property key="transparency" value="0.8"/>
</element>
```

**Implementation** (archiWriter):

```python
# In element serialization loop:
for key, val in element._visual_style.items():
    et.SubElement(element_elem, 'property', key=key, value=str(val))
```

### Read (Import)

**Format**: Extract from `<property>` elements with keys: `fillColor`, `lineColor`, etc.

```python
# In element deserialization:
for prop_elem in element_elem.findall('property'):
    key = prop_elem.get('key')
    value = prop_elem.get('value')
    if key in ('fillColor', 'lineColor', 'lineWidth', 'transparency'):
        element._visual_style[key] = value  # Store as string; validate on access
```

**Validation on Import**:
- Normalize colors via `_normalize_color()`
- Parse lineWidth/transparency as float
- Log warning if invalid; skip property
- Model remains valid even if properties skipped

---

## Integration with Existing Code

### Element._properties vs Element._visual_style

**Separation**:
- `_properties`: Generic key-value store (user-defined, free-form)
- `_visual_style`: Structured visual attributes (managed, validated)

**Rationale**: Keep visual style separate from generic properties for clarity and validation

**Serialization**: Both stored as `<property>` elements in XML (keys distinguish them)

---

## Usage Examples

### Setting Colors by Name

```python
from pyArchimate import ArchiType
from pyArchimate.model import Model

m = Model('example')
proc = m.add(ArchiType.BusinessProcess, 'My Process')

# Set fill color by name
proc.set_fill_color('red')  # Normalized to #ff0000
print(proc.get_fill_color())  # Output: #ff0000

# Set multiple properties
proc.set_visual_style(
    fill_color='blue',      # Named color
    line_color='#000000',   # Hex color
    line_width=2.0,
    transparency=0.9
)
```

### Reading Properties

```python
style = proc.get_visual_style()
print(style)
# Output: {'fillColor': '#0000ff', 'lineColor': '#000000', 'lineWidth': 2.0, 'transparency': 0.9}

# Check individual properties
if proc.get_transparency() < 1.0:
    print("Element is semi-transparent")
```

### Round-Trip Fidelity

```python
# Write to file
m.write('example.archimate')

# Read back
m2 = Model()
m2.read('example.archimate')

# Visual styles preserved
proc2 = m2.find_elements('My Process')[0]
print(proc.get_visual_style() == proc2.get_visual_style())
# Output: True (100% fidelity)
```

---

## Error Handling

### Invalid Colors

```python
proc.set_fill_color('#GGGGGG')  # Invalid hex
# Raises: ValueError("Invalid hex color: #GGGGGG (expected #RRGGBB)")

proc.set_fill_color('rainbow')  # Unknown named color
# Raises: ValueError("Unknown color: rainbow (hex or named color expected)")
```

### Invalid Line Width

```python
proc.set_line_width(-1)  # Negative width
# Raises: ValueError("Line width must be non-negative number, got -1")

proc.set_line_width('thick')  # String instead of float
# Raises: ValueError("...")  # Type error or explicit message
```

### Invalid Transparency

```python
proc.set_transparency(1.5)  # Out of range
# Raises: ValueError("Transparency must be 0.0-1.0, got 1.5")
```

---

## Summary

| Aspect | Design Decision |
|--------|-----------------|
| **Storage** | Dict with keys: fillColor, lineColor, lineWidth, transparency |
| **Colors** | Hex (#RRGGBB) or named colors, normalized to lowercase hex |
| **Validation** | Strict on set; lenient on import (warn, skip invalid) |
| **Defaults** | Standard ArchiMate palette per element type |
| **Serialization** | `<property>` XML elements (matches P2 pattern) |
| **Transparency** | Float 0.0-1.0 (0 = invisible, 1 = opaque) |
| **Line Width** | Float ≥ 0 (pixels) |
| **API** | Getter/setter methods + bulk set_visual_style() |

**Benefits**:
- ✅ Consistent with P2 viewpoint pattern
- ✅ Flexible (add properties without code changes)
- ✅ Validates input but lenient on import
- ✅ Clear, type-safe public API
- ✅ Easy to serialize/export
- ✅ Supports color convenience (named colors)

**Implementation Effort**: ~150 lines of code (Element class additions)

