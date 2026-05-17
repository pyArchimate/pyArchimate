# Contract: Element Visual Style API

**Version**: 1.0  
**Status**: Design Complete (Phase 1)  
**Target**: Phase 2 Implementation

---

## Overview

The Element Visual Style API enables per-element customization of colors, line width, and transparency.

---

## Color Constants

### Named Colors (140+)

Standard CSS/X11 named colors:

```python
NAMED_COLORS = {
    'red': '#ff0000',
    'blue': '#0000ff',
    'green': '#008000',
    # ... 137 more colors
}
```

All converted to lowercase hex on storage.

### Standard Palette (Defaults)

By ArchiMate category:

```python
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
```

---

## Setters (Validate on Set)

### Set Fill Color

**Method**: `Element.set_fill_color(color: Optional[str]) -> None`

**Purpose**: Set element fill color

**Input**:
| Parameter | Type | Format | Example |
|-----------|------|--------|---------|
| color | Optional[str] | Hex or named | '#ff0000' or 'red' or None |

**Validation**:
- Hex: Must match `^#[0-9a-fA-F]{6}$` (case-insensitive)
- Named: Must exist in NAMED_COLORS (case-insensitive)
- None: Valid (clears custom color, use defaults)

**Normalization**:
- Hex: Converted to lowercase (#RRGGBB → #rrggbb)
- Named: Converted to hex via NAMED_COLORS

**Postcondition**:
- `Element._visual_style['fillColor'] = '#rrggbb'` (normalized hex)
- Or removed if color=None

**Errors**:
- `ValueError`: Invalid hex format
  - Message: `"Invalid hex color: {color} (expected #RRGGBB)"`
- `ValueError`: Unknown named color
  - Message: `"Unknown color: {color} (hex or named color expected)"`

**Examples**:

```python
elem.set_fill_color('#FF0000')         # Hex (case-insensitive)
elem.set_fill_color('red')             # Named color
elem.set_fill_color(None)              # Clear custom color

# Stored as:
elem._visual_style['fillColor'] = '#ff0000'  # Always lowercase hex
```

**Test Cases**:
- ✅ Valid hex (#FF0000, #ff0000)
- ✅ Valid named ('red', 'RED')
- ✅ Valid None
- ✅ Error: Invalid hex
- ✅ Error: Unknown named color
- ✅ Normalization to lowercase

---

### Set Line Color

**Method**: `Element.set_line_color(color: Optional[str]) -> None`

**Purpose**: Set element border/line color

**Input**: Same as set_fill_color

**Validation**: Same as set_fill_color

**Postcondition**: `Element._visual_style['lineColor'] = '#rrggbb'`

**Errors**: Same as set_fill_color

---

### Set Line Width

**Method**: `Element.set_line_width(width: Optional[float]) -> None`

**Purpose**: Set element border width (in pixels)

**Input**:
| Parameter | Type | Constraint | Example |
|-----------|------|-----------|---------|
| width | Optional[float] | ≥ 0 | 1.0, 2.5, None |

**Validation**:
- Must be float or int
- Must be ≥ 0 (non-negative)
- None: Valid (clears custom width)

**Postcondition**:
- `Element._visual_style['lineWidth'] = float(width)` (converted to float)
- Or removed if width=None

**Errors**:
- `ValueError`: Negative width
  - Message: `"Line width must be non-negative number, got {width}"`
- `TypeError`: Not numeric
  - Message: `"Line width must be number, got {type}"`

**Examples**:

```python
elem.set_line_width(1.0)           # 1 pixel
elem.set_line_width(2)             # 2 pixels (converted to float)
elem.set_line_width(None)          # Clear custom width
elem.set_line_width(-1)            # Error: ValueError
```

**Test Cases**:
- ✅ Valid float (1.0, 2.5, 0.5)
- ✅ Valid int (1, 2)
- ✅ Valid zero (0.0)
- ✅ Valid None
- ✅ Error: Negative
- ✅ Error: String "1.0"
- ✅ Conversion to float

---

### Set Transparency

**Method**: `Element.set_transparency(alpha: Optional[float]) -> None`

**Purpose**: Set element opacity (0.0 = invisible, 1.0 = opaque)

**Input**:
| Parameter | Type | Range | Example |
|-----------|------|-------|---------|
| alpha | Optional[float] | [0.0, 1.0] | 0.8, 0.5, None |

**Validation**:
- Must be float or int
- Must be in range [0.0, 1.0] (inclusive)
- None: Valid (clears custom transparency)

**Postcondition**:
- `Element._visual_style['transparency'] = float(alpha)`
- Or removed if alpha=None

**Errors**:
- `ValueError`: Out of range
  - Message: `"Transparency must be 0.0-1.0, got {alpha}"`
- `TypeError`: Not numeric
  - Message: `"Transparency must be number, got {type}"`

**Examples**:

```python
elem.set_transparency(0.8)         # 80% opaque
elem.set_transparency(0.5)         # 50% opaque
elem.set_transparency(1.0)         # Fully opaque
elem.set_transparency(0.0)         # Invisible
elem.set_transparency(None)        # Clear custom transparency
elem.set_transparency(1.5)         # Error: ValueError
```

**Test Cases**:
- ✅ Valid range (0.0, 0.5, 1.0)
- ✅ Valid int (0, 1)
- ✅ Valid None
- ✅ Error: Out of range (1.5, -0.1)
- ✅ Error: String "0.8"

---

### Set Visual Style (Bulk)

**Method**: `Element.set_visual_style(fill_color=None, line_color=None, line_width=None, transparency=None) -> None`

**Purpose**: Set multiple style properties at once

**Input**:
| Parameter | Type | Optional | Validation |
|-----------|------|----------|-----------|
| fill_color | Optional[str] | Yes | Hex or named |
| line_color | Optional[str] | Yes | Hex or named |
| line_width | Optional[float] | Yes | ≥ 0 |
| transparency | Optional[float] | Yes | [0.0, 1.0] |

**Behavior**:
- Only provided arguments are updated
- Missing/None arguments not updated
- Validation applied per-argument
- Atomic: All succeed or all fail

**Postcondition**:
- `Element._visual_style` updated with valid values

**Errors**:
- Same as individual setters
- Failure: No updates applied (atomic)

**Examples**:

```python
# Set fill and transparency
elem.set_visual_style(fill_color='red', transparency=0.8)

# Set only line properties
elem.set_visual_style(line_color='#000000', line_width=2.0)

# Set all
elem.set_visual_style(
    fill_color='blue',
    line_color='black',
    line_width=1.5,
    transparency=0.9
)
```

---

## Getters (Read-Only)

### Get Fill Color

**Method**: `Element.get_fill_color() -> Optional[str]`

**Returns**:
- Normalized hex color (#rrggbb), or
- None if not set (use default)

**Example**:

```python
color = elem.get_fill_color()
# Returns: '#ff0000' or None
```

---

### Get Line Color

**Method**: `Element.get_line_color() -> Optional[str]`

**Returns**: Hex color or None

---

### Get Line Width

**Method**: `Element.get_line_width() -> Optional[float]`

**Returns**: Width in pixels (float) or None

---

### Get Transparency

**Method**: `Element.get_transparency() -> Optional[float]`

**Returns**: Opacity [0.0, 1.0] or None

---

### Get All Style Properties

**Method**: `Element.get_visual_style() -> dict[str, Any]`

**Returns**: Dictionary with keys:
- `'fillColor'`: hex or absent
- `'lineColor'`: hex or absent
- `'lineWidth'`: float or absent
- `'transparency'`: float or absent

**Example**:

```python
style = elem.get_visual_style()
# Returns: {
#   'fillColor': '#ff0000',
#   'lineColor': '#000000',
#   'lineWidth': 2.0,
#   'transparency': 0.8
# }
# Or partial if some properties not set
```

---

### Reset to Defaults

**Method**: `Element.reset_visual_style() -> None`

**Purpose**: Clear all custom styles; use defaults

**Postcondition**:
- `Element._visual_style = {}` (empty dict)
- Getters return None
- Uses standard palette defaults

**Example**:

```python
elem.reset_visual_style()
# Now get_fill_color() returns None (use default)
```

---

## State Invariants

**Invariant 1: Normalized Storage**
- All colors in `_visual_style` are lowercase hex (#rrggbb)
- Named colors never stored (converted to hex)

**Invariant 2: Valid Ranges**
- lineWidth ≥ 0
- transparency ∈ [0.0, 1.0]

**Invariant 3: Absence Means Default**
- If key absent from `_visual_style`, getter returns None
- Absence is same as None

---

## XML Serialization Contract

### Write (Export)

```xml
<element id="id-123" ...>
  <property key="fillColor" value="#ff0000"/>
  <property key="lineColor" value="#000000"/>
  <property key="lineWidth" value="2.0"/>
  <property key="transparency" value="0.8"/>
</element>
```

- Only emit properties that are set (not None)
- Value is string representation of Python object

### Read (Import)
- Extract properties with keys: fillColor, lineColor, lineWidth, transparency
- Validate and normalize on import
- On error: Log warning, skip property, continue (model remains valid)
- Lenient on import (strict on set)

---

## Performance Targets

| Operation | Target | Method |
|-----------|--------|--------|
| set_fill_color() | <1ms | Color validation + dict store |
| get_fill_color() | <1ms | Dict lookup |
| set_visual_style() | <5ms | 4 validations + dict updates |
| get_visual_style() | <1ms | Dict copy |
| Color normalization | <1ms | Regex or dict lookup |

---

## Backward Compatibility

- ✅ No Element.__init__() signature change
- ✅ No existing method modifications
- ✅ _visual_style is internal (not part of public API originally)

---

## Default Behavior

If element has no custom visual style:
- Fill color: Standard palette color for element's category
- Line color: Black (#000000)
- Line width: 1.0 pixels
- Transparency: 1.0 (fully opaque)

---

**Contract Status**: Ready for Phase 2 Implementation
