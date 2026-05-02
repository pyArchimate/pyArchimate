# Phase 0 Research: Archi Tool Fidelity Fixes

**Date**: 2026-05-02  
**Status**: Complete

## Research Findings

### 1. Boolean Parsing in Python

**Context**: Line 115-116 in `_archireader_helpers.py` uses `bool(ft.get('value'))` to parse the `nameVisible` feature string.

**Finding**: In Python, `bool("false")` evaluates to `True` because any non-empty string is truthy.

**Correct Approach**: Parse the string value explicitly:
```python
value_str = ft.get('value', '').lower()
show_label = value_str == 'true'  # Only True if explicitly "true"
```

**Standards Compliance**: This aligns with W3C XML Schema boolean type (accepts "true", "false", "1", "0").

**Alternatives Considered**:
- Using `ast.literal_eval()` — overkill, requires exception handling
- Custom `parse_bool()` helper — maintainable, reusable across codebase (recommended)

**Decision**: Create a `parse_bool()` helper function in `helpers.py` to handle string-to-bool conversion consistently.

### 2. Documentation Text Extraction

**Context**: Three places extract `<documentation>` elements:
- Line 161: Elements — correctly uses `elem.desc = doc.text` ✅
- Line 178: Elements in folders — correctly uses `elem.desc = doc.text` ✅
- Line 237: Views — incorrectly uses `elem.desc = e.text` ❌

**Finding**: The view documentation bug at line 237 assigns the parent element's text (`e.text`) instead of the documentation child element's text (`doc.text`). Since `<documentation>` is a container with `<content>` as text, `e.text` will be None.

**XML Structure** (from lxml.etree):
```xml
<ArchimateDiagramModel>
  <documentation>
    <content>The view documentation here</content>
  </documentation>
</ArchimateDiagramModel>
```

When parsed:
- `e.find('documentation')` finds the `<documentation>` element
- `e.text` is the text **between** `<ArchimateDiagramModel>` and first child (None if no whitespace)
- `doc.text` is the text **between** `<documentation>` and `<content>` (also None)
- `doc.find('content').text` is the actual documentation text

**Correct Fix**: Use the same pattern as elements/relationships:
```python
doc = e.find('documentation')
if doc is not None:
    elem.desc = doc.text  # Already correct for elements, apply to views
```

**Observation**: The relationship/element code at lines 161, 178 shows the correct pattern. Line 237 is the outlier.

**Decision**: Apply the same fix (use `doc.text`) to maintain consistency.

### 3. Writer-Side Label Visibility

**Context**: `archiWriter.py:149-151` writes label visibility to Archi files.

**Current Code** (inferred from Feature 004 plan):
```python
# Likely writes: ft.set('value', str(node.show_label))
# This produces "True" or "False" (capitalized), not "true"/"false"
```

**Finding**: Python's `str(True)` produces "True" (capitalized), but Archi expects lowercase "true"/"false" for XML boolean attributes.

**Standards Compliance**: XML boolean per W3C schema: "true", "false", "1", "0" (lowercase preferred).

**Decision**: Normalize boolean output to lowercase when writing Archi files.

### 4. Test Framework Capabilities

**Context**: Feature 004 uses pytest (unit/integration) + behave (BDD).

**Finding**: 
- pytest: Sufficient for unit testing boolean parsing and documentation extraction
- behave: Can test round-trip scenarios with real Archi files
- No special XML testing library needed — lxml's standard parsing validates structure

**Decision**: Follow Feature 004 test patterns (unit + integration + BDD).

---

## Resolutions

| Clarification | Resolution | Status |
|---|---|---|
| Boolean parsing in Python | Create `parse_bool()` helper; use explicit comparison | ✅ Decided |
| View documentation extraction | Use `doc.text` (same as elements/relationships) | ✅ Decided |
| Writer boolean normalization | Output lowercase "true"/"false" to Archi XML | ✅ Decided |
| Test framework | pytest + behave (following Feature 004) | ✅ Decided |

---

## Standards & Patterns

- **XML Boolean Handling**: W3C XML Schema Part 2 (xsd:boolean)
  - Canonical form: "true" / "false"
  - Accepted: "true", "false", "1", "0", "TRUE", "FALSE" (case-insensitive in schema)
  - Python convention: normalize input to lowercase, output to lowercase

- **lxml Text Extraction**: Use `element.text` for immediate text content, `element.find('child').text` for child content

- **Round-trip Fidelity**: Preserve exact string values through import/export cycles (no case conversion)

---

## Next Steps

1. **Phase 1**: Design data model & contracts for boolean handling
2. **Phase 1**: Create helper functions and test cases
3. **Phase 2**: Implement fixes (3 files, ~10 lines changed)
4. **Phase 2**: Execute round-trip tests
