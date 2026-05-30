# Contract: Visual Properties

**Version**: 1.0  
**Date**: 2026-05-30  
**Type**: Styling Metadata Contract  
**Status**: Complete (P3 Implementation)

## Overview

Defines how element-level visual styling (fill color, line color, line width, transparency) is stored, validated, serialized, and preserved through round-trips. Visual properties are optional on all elements; absent properties fall back to the default ArchiMate palette at render time.

---

## Canonical Representation

**Storage** (`Element._visual_style: dict[str, Any]`):

| Key | Type | Valid values |
|-----|------|-------------|
| `fillColor` | `str` | Normalized lowercase hex, e.g. `'#ffeb3b'` |
| `lineColor` | `str` | Normalized lowercase hex, e.g. `'#000000'` |
| `lineWidth` | `float` | ≥ 0.0 (pixels) |
| `transparency` | `float` | 0.0–1.0 (0 = fully transparent, 1 = fully opaque) |

Keys are absent from the dict when not set (not `None`). Setting a property to `None` removes it from the dict.

---

## API

| Method | Location | Description |
|--------|----------|-------------|
| `element.set_fill_color(color)` | `element.py:502` | Set or clear fill color |
| `element.set_line_color(color)` | `element.py:514` | Set or clear line color |
| `element.set_line_width(width)` | `element.py:526` | Set or clear line width |
| `element.set_transparency(alpha)` | `element.py:543` | Set or clear transparency |
| `element.set_visual_style(fill_color, line_color, line_width, transparency)` | `element.py:560` | Bulk setter; `None` parameters are ignored |
| `element.get_visual_style()` | `element.py` | Return copy of `_visual_style` dict |
| `element.reset_visual_style()` | `element.py` | Clear all visual properties |

---

## Color Validation and Normalization

Colors are accepted in the following formats, normalized to lowercase hex on storage:

| Input | Stored as | Notes |
|-------|-----------|-------|
| `'#FFEB3B'` | `'#ffeb3b'` | 6-digit hex only, case-insensitive |
| `'red'` | `'#ff0000'` | CSS named colors resolved via `NAMED_COLORS` |
| `None` | *(removed)* | Clears the property |

**Invalid inputs** raise `ValueError`: 3-digit hex (e.g. `'#fff'`), unknown names (e.g. `'banana'`), malformed hex (e.g. `'#gg0000'`). Only 6-digit hex (`#RRGGBB`) and names in `NAMED_COLORS` are accepted.

Color normalization is handled by `_normalize_color()` in `element.py`.

---

## XML Serialization

### `.archimate` format (Archi)

Visual properties are written as `<property>` child elements on the element:

```xml
<element id="e1" name="Customer Portal" xsi:type="ApplicationComponent">
  <property key="fillColor" value="#dce8f5"/>
  <property key="lineColor" value="#2b6cb0"/>
  <property key="lineWidth" value="2.0"/>
  <property key="transparency" value="0.85"/>
</element>
```

**Writer**: `archiWriter.py:116-122`  
**Reader**: `_archireader_helpers.py:246-252` — reads `fillColor`, `lineColor`, `lineWidth`, `transparency` properties; casts `lineWidth` and `transparency` to float.

### OpenGroup exchange format

Uses property definitions with `<value>` child elements (OpenGroup exchange schema):

```xml
<property propertyDefinitionRef="fillColor-prop-id">
  <value>#dce8f5</value>
</property>
<property propertyDefinitionRef="lineColor-prop-id">
  <value>#2b6cb0</value>
</property>
```

Property definition IDs are auto-registered in the `<propertyDefinitions>` section by `archimateWriter.py:_get_prop_def_id()`.

---

## Node-Level vs Element-Level Visual Properties

There are two separate style layers:

| Layer | Class | Purpose |
|-------|-------|---------|
| **Element** | `Element._visual_style` | Semantic/exported model styling |
| **Node** | `Node.fill_color`, `Node.line_color` | Diagram-level rendering in views |

Element-level properties are serialized in the element's `<property>` list and survive round-trips. Node-level properties apply per view and are stored as XML attributes on `<node>` tags. This contract covers the element-level layer only.

---

## Round-Trip Fidelity

✅ All four properties survive `.archimate` export/import  
✅ Absent properties remain absent after round-trip (no default injection)  
✅ Color normalization is idempotent (stored in canonical form)  
✅ `None` assignment correctly clears a previously-set property

**Test coverage**:
- `tests/unit/test_visual_style.py` — color validation, property set/get/clear, bulk setter
- `tests/integration/` — visual properties included in combined round-trip fixtures
- `tests/features/visual_style.feature` — BDD acceptance scenarios

---

## Default ArchiMate Palette (Reference)

When no visual property is set, renderers should apply the standard ArchiMate layer defaults:

| Layer | Fill color | Line color |
|-------|-----------|------------|
| Business | `#ffffb5` | `#000000` |
| Application | `#80ffff` | `#000000` |
| Technology | `#c9e7b7` | `#000000` |
| Motivation | `#ccccff` | `#000000` |
| Strategy | `#f5deaa` | `#000000` |
| Physical | `#c9e7b7` | `#000000` |

Defaults are not stored on the element; they are applied at render time via `default_color()` (`model.py:137`), which the OpenGroup writer (`archimateWriter.py`) calls when writing node styles in views.

---

## Implementation Files

- `src/pyArchimate/element.py` — `_visual_style` dict, accessors, normalization (lines 168, 502-590)
- `src/pyArchimate/readers/_archireader_helpers.py` — property extraction (lines 246-252)
- `src/pyArchimate/writers/archiWriter.py` — property emission (lines 116-122)
- `src/pyArchimate/writers/archimateWriter.py` — OpenGroup emission + default palette (lines 98-104, 162)
