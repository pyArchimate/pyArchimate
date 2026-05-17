# Phase 1 Data Model & Contracts

**Date**: 2026-05-02  
**Status**: Complete

## Data Model

### 1. BooleanField Parsing Contract

**Purpose**: Standardize string-to-boolean conversion across Archi reader to match W3C XML Schema boolean semantics.

**Entity**: `parse_bool(value: str | None) -> bool`

**Fields**:
- `value` (str | None): The string value from Archi XML
  - `"true"`, `"1"` → `True`
  - `"false"`, `"0"` → `False`
  - `None`, `""`, other values → `False` (safe default)
  - Case-insensitive (handles "TRUE", "False", etc.)

**Implementation Location**: `src/pyArchimate/helpers.py` (new helper module or existing)

**Usage**:

```python
conn.show_label = parse_bool(ft.get('value'))
```

**Test Cases**:
- `parse_bool(None)` → `False`
- `parse_bool("true")` → `True`
- `parse_bool("false")` → `False`
- `parse_bool("True")` → `True` (case-insensitive)
- `parse_bool("1")` → `True`
- `parse_bool("0")` → `False`
- `parse_bool("")` → `False`
- `parse_bool("random")` → `False`

### 2. DocumentationExtraction Contract

**Purpose**: Consistently extract `<documentation>` text from XML elements.

**Pattern**: All three contexts (elements, relationships, views) should use identical logic:

```python
doc = element.find('documentation')
if doc is not None:
    target.desc = doc.text
```

**Affected Locations**:
- ✅ Line 161: Elements in `_process_folder_element()` — correct pattern
- ✅ Line 178: Elements in `_process_folder_element()` — correct pattern
- ❌ Line 237: Views in `get_folders_view()` — uses `e.text` (wrong)

**Fix**: Replace line 237:

```python
# Current (WRONG):
elem.desc = e.text

# Fixed:
doc = e.find('documentation')
if doc is not None:
    elem.desc = doc.text
```

**Edge Cases Handled**:
- Missing `<documentation>` element → `elem.desc` not set (unchanged)
- Empty `<documentation>` → `elem.desc = None` (safe, matches existing behavior)
- Multiple `<documentation>` elements → `find()` returns first (safe, matches Archi spec)

### 3. LabelVisibility Contract

**Purpose**: Correctly parse and serialize diagram connection label visibility.

**Current Bug**: `bool("false")` → `True` (non-empty string is truthy)

**Reader Side** (Input - Archi XML → Python):
- XML: `<feature name="nameVisible" value="false" />`
- Parsed: `ft.get('value')` → `"false"` (string)
- Current: `conn.show_label = bool("false")` → `True` ❌
- Fixed: `conn.show_label = parse_bool("false")` → `False` ✅

**Writer Side** (Output - Python → Archi XML):
- Python: `conn.show_label = True`
- Current output: `str(True)` → `"True"` (capitalized)
- Fixed output: `"true"` (lowercase)

**Locations**:
- Reader: `src/pyArchimate/readers/_archireader_helpers.py:115-116`
- Writer: `src/pyArchimate/writers/archiWriter.py:149-151` (verify capitalization)

**Test Cases**:
- Import: `nameVisible="false"` → `show_label=False` ✓
- Import: `nameVisible="true"` → `show_label=True` ✓
- Import: missing attribute → `show_label=True` (default visible) ✓
- Export: `show_label=True` → `value="true"` ✓
- Export: `show_label=False` → `value="false"` ✓

---

## Contracts Directory

### `/contracts/boolean-handling.md`

Documents the boolean parsing strategy across the Archi adapter.

**File Location**: `specs/006-archi-tool-compliance/contracts/boolean-handling.md`

**Content**:
- W3C XML Schema boolean spec reference
- Python implementation (`parse_bool()` function)
- Reader expectations (string input formats)
- Writer output format (lowercase "true"/"false")
- Round-trip invariant: `value == parse_bool(write_bool(value))`

### `/contracts/documentation-extraction.md`

Documents the consistent documentation text extraction pattern.

**File Location**: `specs/006-archi-tool-compliance/contracts/documentation-extraction.md`

**Content**:
- XML structure of `<documentation>` elements in Archi files
- Extraction pattern: `element.find('documentation')` then `doc.text`
- Consistent application across elements, relationships, views
- Edge cases and safe defaults

---

## State & Lifecycle

No new state transitions. Existing state:
- `Node.show_label` → boolean flag, already persisted
- `Element.desc` / `Relationship.desc` → documentation string, already persisted
- `View.desc` → documentation string, already persisted

Changes are purely in reader/writer fidelity, not in model semantics.

---

## Backward Compatibility

✅ **Fully backward compatible**:
- No API changes to public classes
- No changes to storage format (XML structure unchanged)
- Fixes align with Archi's canonical boolean format
- Existing code that correctly writes booleans unaffected
- Only fixes bugs in incorrect parsing

---

## Open Questions

None — all clarifications resolved in Phase 0 research.
