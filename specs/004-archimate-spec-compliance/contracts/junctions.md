# Contract: Junction Semantics

**Version**: 1.0  
**Date**: 2026-05-30  
**Type**: Element Type Contract  
**Status**: Complete (P3 Implementation)

## Overview

Defines how ArchiMate junction elements (AND, OR, XOR) encode their type semantics, including storage, validation, serialization, and backward compatibility with legacy files.

---

## Junction Types in ArchiMate

ArchiMate 3.x defines three junction semantics for branching/merging relationship flows:

| Type | Slug | ArchiType enum | Description |
|------|------|----------------|-------------|
| AND junction | `'and'` | `ArchiType.Junction` or `ArchiType.AndJunction` | All paths must be satisfied |
| OR junction | `'or'` | `ArchiType.OrJunction` | At least one path must be satisfied |
| XOR junction | `'xor'` | `ArchiType.Junction` (extension, not in ArchiMate standard) | Exactly one path must be satisfied |

**Note**: In the OpenGroup Exchange format, `junction_type='and'` and `junction_type='xor'` both serialize to `xsi:type="AndJunction"` (see `archimateWriter.py:_get_elem_xsi_type`). Only `junction_type='or'` produces `xsi:type="OrJunction"`. Use `ArchiType.OrJunction` for OR junctions and `ArchiType.Junction`/`ArchiType.AndJunction` for AND junctions.

**Enum location**: `src/pyArchimate/enums.py` lines 164-166  
**Valid values constant**: `JUNCTION_TYPES = {"and", "or", "xor"}` in `src/pyArchimate/constants.py:64`

---

## Canonical Representation

**Storage** (`Element`):
- `junction_type: str | None` — set to `'and'`, `'or'`, `'xor'`, or `None` if not a junction
- Stored in lowercase (normalized on write)

**API**:

| Method | Location | Description |
|--------|----------|-------------|
| `element.set_junction_type(type_str)` | `element.py:631` | Validate and set junction type; `None` clears it |
| `element.get_junction_type()` | `element.py:647` | Return current junction type or `None` |

**Validation**: Raises `ValueError` for any value not in `{"and", "or", "xor", None}`. Input is case-insensitive (`"AND"` → `"and"`).

---

## XML Serialization

### `.archimate` format (Archi)

Junction type is written as both an `xsi:type` attribute and a `<property>` element:

```xml
<!-- AND junction -->
<element id="j1" xsi:type="Junction" type="and">
  <property key="junctionType" value="and"/>
</element>

<!-- OR junction -->
<element id="j2" xsi:type="OrJunction" type="or">
  <property key="junctionType" value="or"/>
</element>

<!-- XOR junction -->
<element id="j3" xsi:type="AndJunction" type="xor">
  <property key="junctionType" value="xor"/>
</element>
```

**Writer**: `archiWriter.py:111-114`

### OpenGroup exchange format

Junction type is written as an element attribute:

```xml
<element identifier="j1" xsi:type="Junction" junctionType="and"/>
<element identifier="j2" xsi:type="OrJunction" junctionType="or"/>
```

**Writer**: `archimateWriter.py:106-154`

---

## Import Logic and Backward Compatibility

### Primary path (new format)

`_archireader_helpers.py:241-245` reads `junctionType` property and calls `set_junction_type()`.

### Legacy path (old `.archimate` files)

`_archireader_helpers.py:272-301` reads `xsi:type` attribute (`AndJunction`, `OrJunction`) and maps to the canonical type string. If neither `junctionType` property nor a recognized `xsi:type` is present, `junction_type` remains `None`.

**Priority**: `junctionType` property overrides `xsi:type` inference (the property is processed last in the import loop and directly sets `elem.junction_type`).

---

## Round-Trip Fidelity

✅ Junction type survives `.archimate` export/import  
✅ Junction type survives OpenGroup export/import  
✅ Legacy files with `xsi:type` attribute only import correctly  
✅ `junction_type` is `None` when no type attribute or property is present (no forced default)

**Test coverage**:
- `tests/unit/test_junction_semantics.py` — validation, creation, type round-trip
- `tests/integration/test_round_trip_junctions.py` — full `.archimate` and OpenGroup cycles
- `tests/features/integration.feature` — BDD scenarios for junctions with flow

---

## Implementation Files

- `src/pyArchimate/enums.py` — `Junction`, `OrJunction`, `AndJunction` (lines 164-166)
- `src/pyArchimate/constants.py` — `JUNCTION_TYPES` constant (line 64)
- `src/pyArchimate/element.py` — `junction_type` attribute + methods (lines 165, 631-654)
- `src/pyArchimate/readers/_archireader_helpers.py` — import logic (lines 241-301)
- `src/pyArchimate/writers/archiWriter.py` — `.archimate` export (lines 111-114)
- `src/pyArchimate/writers/archimateWriter.py` — OpenGroup export (lines 106-154)

---

## Error Handling

**Invalid junction type**:
```
ValueError: Invalid junction type: foo. Must be one of {'and', 'or', 'xor'}
```

**Setting type on non-junction element**: Allowed at the API level (no elem_type restriction). Semantic validation is the caller's responsibility.
