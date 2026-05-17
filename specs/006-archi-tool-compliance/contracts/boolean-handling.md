# Contract: Boolean Handling in Archi XML

**Date**: 2026-05-02  
**Scope**: Archi reader/writer boolean parsing and serialization

## Problem

Python's `bool(string)` returns `True` for any non-empty string, including `"false"`. This breaks parsing of Archi's `nameVisible` feature.

**Example**:

```python
bool("false")  # → True (BUG!)
bool("true")   # → True (correct)
bool("")       # → False (correct)
```

## Standard

**W3C XML Schema Part 2: Datatypes (xsd:boolean)**

Lexical space: `"true" | "false" | "1" | "0"`

- Canonical form: `"true"` or `"false"` (lowercase)
- Input parsing must accept case-insensitive variations
- Example: `xsi:type="xsd:boolean"` attribute with value `"FALSE"` is valid

## Solution

### Reader: String → Python bool

Create `parse_bool(value: str | None) -> bool` function in `src/pyArchimate/helpers.py`:

```python
def parse_bool(value: str | None) -> bool:
    """
    Parse string to boolean per W3C xsd:boolean semantics.
  
    Args:
        value: String from XML ("true", "false", "1", "0", None, etc.)
  
    Returns:
        True if value matches "true" or "1" (case-insensitive)
        False otherwise (including None, empty, invalid)
    """
    if value is None:
        return False
    normalized = str(value).lower().strip()
    return normalized in ("true", "1")
```

**Usage in _archireader_helpers.py:116**:

```python
# Before:
conn.show_label = bool(ft.get('value'))

# After:
from ..helpers import parse_bool
conn.show_label = parse_bool(ft.get('value'))
```

### Writer: Python bool → Archi XML string

Ensure output uses lowercase "true" / "false":

```python
# When writing to XML:
ft.set('value', 'true' if show_label else 'false')
```

**Verification in archiWriter.py:149-151**: Check current output format and normalize if needed.

## Round-Trip Invariant

```
original_value ∈ {"true", "false", "TRUE", "FALSE", "1", "0", None}
  → parse_bool(original_value)
  → write_bool(result)
  → canonical_value ∈ {"true", "false"}
  → parse_bool(canonical_value)
  → same boolean result ✓
```

## Test Coverage

### Unit Tests (test_helpers.py)

```python
def test_parse_bool_true_values():
    assert parse_bool("true") is True
    assert parse_bool("True") is True
    assert parse_bool("TRUE") is True
    assert parse_bool("1") is True

def test_parse_bool_false_values():
    assert parse_bool("false") is False
    assert parse_bool("False") is False
    assert parse_bool("FALSE") is False
    assert parse_bool("0") is False

def test_parse_bool_edge_cases():
    assert parse_bool(None) is False
    assert parse_bool("") is False
    assert parse_bool("random") is False
    assert parse_bool("yes") is False
    assert parse_bool("  true  ") is True  # whitespace trimmed
```

### Integration Tests (test_archimate_roundtrip.py)

- Import Archi file with `nameVisible="false"` → `show_label=False` ✓
- Export → Archi file with `value="false"` ✓
- Re-import → `show_label=False` ✓

## References

- W3C XML Schema Part 2: <https://www.w3.org/TR/xmlschema-2/#boolean>
- ArchiMate 3.1 XML Serialization (section on feature attributes)
