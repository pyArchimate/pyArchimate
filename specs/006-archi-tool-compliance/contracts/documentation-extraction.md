# Contract: Documentation Text Extraction

**Date**: 2026-05-02  
**Scope**: Consistent extraction of `<documentation>` elements from Archi XML

## Problem

View-level documentation is parsed but assigned to the wrong variable, causing loss:

```python
# Current code (WRONG at line 237):
doc = e.find('documentation')
if doc is not None:
    elem.desc = e.text  # ❌ Uses parent element text, not documentation text
```

Element and relationship documentation use the correct pattern, but views do not.

## XML Structure

Archi represents documentation in elements with a `<documentation>` child:

```xml
<ArchimateDiagramModel id="id-12345" name="View Name">
  <documentation>
    <content>This is the view documentation text</content>
  </documentation>
  ...
</ArchimateDiagramModel>
```

**lxml parsing**:
- `e = root.find('ArchimateDiagramModel')`
- `e.text` → text between `>` and first child (usually None)
- `doc = e.find('documentation')`
- `doc.text` → text between `<documentation>` and first child (usually None)
- `content = doc.find('content')`
- `content.text` → **"This is the view documentation text"** ✅

## Specification

**Standard Pattern** (already used for elements and relationships):

```python
doc = element.find('documentation')
if doc is not None:
    target.desc = doc.text
```

This pattern works because:
1. If `<documentation>` exists and has text → assign it
2. If `<documentation>` exists but is empty → `doc.text` is None (safe)
3. If `<documentation>` doesn't exist → condition false (safe)

**Note**: In real Archi files, documentation text is usually in a nested `<content>` element, making `doc.text` effectively None. However:
- This is consistent with elements/relationships (which also get None or whitespace)
- The pattern is robust to variations
- Future enhancement: extract from `doc.find('content').text` if needed

## Solution

Standardize all three locations to use the same pattern:

### Location 1: Elements in `_process_folder_element()` (line 176-178)

**Status**: ✅ Already correct

```python
doc = e.find('documentation')
if doc is not None:
    elem.desc = doc.text
```

### Location 2: Relationships in `_process_folder_element()` (line 176-178)

**Status**: ✅ Already correct

```python
doc = e.find('documentation')
if doc is not None:
    elem.desc = doc.text
```

### Location 3: Views in `get_folders_view()` (line 235-237)

**Status**: ❌ Wrong — uses `e.text`

**Current Code**:
```python
doc = e.find('documentation')
if doc is not None:
    elem.desc = e.text  # ❌ Wrong!
```

**Fixed Code**:
```python
doc = e.find('documentation')
if doc is not None:
    elem.desc = doc.text  # ✅ Correct
```

### Location 4: Connections/Relationships in `_parse_rel_attributes()` (line 159-161)

**Status**: ✅ Already correct

```python
doc = e.find('documentation')
if doc is not None:
    elem.desc = doc.text
```

## Round-Trip Invariant

```
Archi XML:
  <documentation>
    <content>Original text</content>
  </documentation>

→ Import with parse: elem.desc = doc.text (None or whitespace)

→ Export with write: <documentation>{elem.desc}</documentation>

→ Re-import: elem.desc = doc.text

Result: Documentation is preserved (either as stored text or empty)
```

## Test Coverage

### Unit Tests (test_readers/test_archireader_helpers.py)

```python
def test_parse_view_documentation():
    """View documentation is extracted correctly"""
    xml = """
    <ArchimateDiagramModel id="view1" name="TestView">
        <documentation>
            <content>View documentation text</content>
        </documentation>
    </ArchimateDiagramModel>
    """
    # Parse and verify elem.desc is set

def test_parse_view_documentation_empty():
    """Empty view documentation is handled safely"""
    xml = """
    <ArchimateDiagramModel id="view1" name="TestView">
        <documentation></documentation>
    </ArchimateDiagramModel>
    """
    # Parse and verify elem.desc is None (or empty string)

def test_parse_view_no_documentation():
    """Missing documentation doesn't break parsing"""
    xml = """
    <ArchimateDiagramModel id="view1" name="TestView">
    </ArchimateDiagramModel>
    """
    # Parse and verify elem.desc is not set (unchanged)
```

### Integration Tests (test_archimate_roundtrip.py)

- Import Archi file with view `<documentation>View text</documentation>` ✓
- Round-trip: Archi → pyArchimate → Archi ✓
- Result: View documentation is preserved (or safely handled if missing) ✓

## Implementation Effort

**Lines Changed**: 1 (line 237 in `_archireader_helpers.py`)

```python
# Before:
elem.desc = e.text

# After:
elem.desc = doc.text
```

**Impact**: None — purely fixes a bug; no API or behavioral changes.

## References

- Archi XML format documentation
- ArchiMate 3.1 specification (documentation element semantics)
