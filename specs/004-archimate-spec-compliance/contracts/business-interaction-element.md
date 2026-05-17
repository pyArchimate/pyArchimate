# Contract: BusinessInteraction Element Registration

**Version**: 1.0  
**Date**: 2026-04-30  
**Type**: Element Type Contract

## Overview

Defines how the `BusinessInteraction` ArchiMate element type is registered, validated, and serialized across the pyArchimate library.

## Registration

### ArchiType Enum

```python
# File: src/pyArchimate/enums.py
class ArchiType(str, Enum):
    BusinessInteraction = "BusinessInteraction"  # Already present (line 76)
```

**Status**: ✅ Already defined; no change needed.

### ARCHI_CATEGORY Mapping

```yaml
# File: src/pyArchimate/checker_rules.yml (line 99)
archi_category:
  BusinessInteraction: Business  # CURRENTLY COMMENTED OUT
  # Change to:
  BusinessInteraction: Business  # UNCOMMENT THIS LINE
```

**Status**: ⚠️ Requires uncomment; this is the single required change for this contract.

## Validation

### Element.__init__ Validation

```python
# File: src/pyArchimate/element.py
def __init__(self, name, elem_type, ...):
    if elem_type not in ARCHI_CATEGORY:
        raise ValueError(f"Unknown element type: {elem_type}")
    # After fix: BusinessInteraction will be in ARCHI_CATEGORY
```

**Behavior after fix**:
- `Element(name='X', elem_type=ArchiType.BusinessInteraction)` → ✅ Success
- No additional code changes needed

### Relationship Rules

```yaml
# File: src/pyArchimate/checker_rules.yml (lines 30, 99, 171, 234, 297, 360, 423, 486, 549, 612)
# BusinessInteraction already referenced in 9 relationship rule entries
# Once category is enabled, all rules become active
```

**Status**: ✅ Already defined; will activate once category is uncommented.

## Serialization

### Export to .archimate format

```xml
<!-- Expected output -->
<BusinessInteraction name="Customer Service Interaction">
  <documentation>...</documentation>
</BusinessInteraction>
```

**Writer**: `src/pyArchimate/writers/archiWriter.py`
- Existing element serialization mechanism will handle BusinessInteraction
- No format changes needed

### Export to OpenGroup exchange format

```xml
<!-- Expected output -->
<element xsi:type="BusinessInteraction" name="..." id="...">
  ...
</element>
```

**Writer**: `src/pyArchimate/writers/archimateWriter.py`
- Existing element serialization mechanism will handle BusinessInteraction
- No format changes needed

### Import from .archimate format

```python
# Existing reader logic will parse BusinessInteraction elements
# Once ARCHI_CATEGORY is enabled, Element.__init__ validation passes
```

**Reader**: `src/pyArchimate/readers/archiReader.py`
- Existing element parsing mechanism handles BusinessInteraction
- No parser changes needed

## Testing Criteria

**Creation Test**:

```python
elem = Element(name='Test', elem_type=ArchiType.BusinessInteraction)
assert elem.elem_type == ArchiType.BusinessInteraction
assert elem.name == 'Test'
```

**Export Test**:

```python
model.add_element(elem)
model.export_to_file('test.archimate', Writers.archi)
# Verify test.archimate contains <BusinessInteraction ... />
```

**Import Test**:

```python
imported_model = read_archimate_file('test.archimate')
imported_elem = imported_model.get_element_by_type(ArchiType.BusinessInteraction)[0]
assert imported_elem.name == 'Test'
```

**Relationship Test**:

```python
# All existing relationship rule tests should pass once category is enabled
# Example: Can relate BusinessInteraction to BusinessActor via Realization
```

## Edge Cases

- **Mixed version models**: Models with BusinessInteraction alongside legacy elements → ✅ Supported
- **Relationship constraints**: BusinessInteraction respects existing relationship rules → ✅ Enforced
- **Category inheritance**: BusinessInteraction is Business category (not custom) → ✅ Inherits Business rules
- **Backward compatibility**: Files created without BusinessInteraction still import/export correctly → ✅ Preserved

## Activation Steps

1. Locate `src/pyArchimate/checker_rules.yml` line 99
2. Uncomment: `BusinessInteraction: Business`
3. No other code changes required
4. Run test suite to verify no regressions

## Files Modified

- `src/pyArchimate/checker_rules.yml` (1 line change: uncomment)
- No other files require changes for this contract

## Compliance

✅ Aligns with ArchiMate 3.x specification  
✅ Uses existing validation and serialization mechanisms  
✅ No breaking changes to public API  
✅ Backward compatible with existing models  
