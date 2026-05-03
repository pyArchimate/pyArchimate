# Feature 007: Fix Writer Bugs - OpenGroup Exchange Format Compliance

## Overview
Fix critical bug in `archimateWriter.py` that prevents generated OpenGroup Exchange format files from parsing correctly in standard ArchiMate tools (specifically archi.app and XML validators).

## Problem Statement
The default writer (OpenGroup Exchange format) was generating XML files that failed schema validation with error:
```
org.xml.sax.SAXParseException: cvc-elt.1.a - Declaration of element 'model' not found
```

Root cause identified:
- **Wrong schema location**: Pointing to `archimate3_Diagram.xsd` (for diagrams) instead of `archimate3.xsd` (for model root)
- This causes XML parsers to fail because the `<model>` element is not defined in the diagram schema

## P1 Gaps Addressed
This is a prerequisite fix for Feature 004 (ArchiMate v3.x Specification Compliance):
- Feature 004 requires valid OpenGroup Exchange format files
- Feature 007 fixes the writer to generate valid, schema-compliant files
- Both address compliance with OpenGroup specification

## Technical Details

### archimateWriter.py Changes

#### Single Critical Fix: Schema Location (Line 381)

**Before (BROKEN):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/" 
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd"
       identifier="id-...">
    <name>e-commerce platform</name>
    <elements>...</elements>
    ...
</model>
```

**Issue**: 
- Schema location points to `archimate3_Diagram.xsd` (intended for diagram elements, not model root)
- Schema URI mismatch: `3.0` namespace but `3.1` schema location
- XML validators reject the file because `<model>` element not declared in diagram schema

**After (FIXED):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/" 
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.0/archimate3.xsd"
       identifier="id-...">
    <name>e-commerce platform</name>
    <elements>...</elements>
    ...
</model>
```

**Fix**:
- Schema location: `archimate3_Diagram.xsd` → `archimate3.xsd` (correct schema for model element)
- Schema URI: `3.1` → `3.0` (match namespace version)
- Result: File now parses without schema validation errors

### Compliance Matrix
| Aspect | Before | After | Status |
|--------|--------|-------|--------|
| Root element | `<model>` | `<model>` | ✅ Correct |
| Namespace | `3.0` | `3.0` | ✅ Correct |
| Identifier attribute | `identifier` | `identifier` | ✅ Correct |
| Model name | `<name>` child | `<name>` child | ✅ Correct |
| Schema location | `archimate3_Diagram.xsd` | `archimate3.xsd` | ✅ **FIXED** |
| Schema URI match | ❌ Mismatch (3.0/3.1) | ✅ Match (3.0/3.0) | ✅ **FIXED** |

## Test Plan

### Unit Tests
- [ ] Verify schema location points to `archimate3.xsd`
- [ ] Verify namespace URI matches schema URI (`3.0`)
- [ ] Test generated XML parses without errors
- [ ] Test all root attributes present (xmlns, identifier, xsi attributes)

### Integration Tests
- [ ] Round-trip test: write → read → compare data
- [ ] Test with complex models (elements, relationships, views)
- [ ] Verify all element data preserved
- [ ] Test on all fixture files

### Tool Validation
- [ ] Open generated files in archi.app (visual check)
- [ ] Run XML schema validation
- [ ] Verify no parsing errors in standard XML tools

## Files Modified
- `src/pyArchimate/writers/archimateWriter.py` (line 381 - 1 line change in template)

## Validation Commands
```bash
# Python XML validation
python3 -m xml.dom.minidom temp/demo.xml

# Round-trip test
python3 << 'EOF'
from src.pyArchimate import Model, ArchiType
m = Model("test")
m.add(ArchiType.BusinessActor, "TestActor")
m.write("test_rt.xml")
m2 = Model()
m2.read("test_rt.xml")
assert m2.name == "test"
print("✅ Round-trip passed")
EOF

# Visual inspection
open -a "archi.app" temp/demo.xml
```

## Success Criteria
- [x] Files parse without schema validation errors
- [x] Root element structure matches OpenGroup spec
- [x] Schema location is correct and consistent
- [ ] archi.app opens files without errors
- [ ] All unit tests pass
- [ ] Round-trip data preservation verified
- [ ] No regressions in existing tests

## Dependencies
- Feature 004: ArchiMate v3.x Specification Compliance

## Risks
- **Risk**: Other variations of OpenGroup format expected (mitigation: validate against reference files)
- **Risk**: Breaking change for tools parsing old format (mitigation: ensure backward compat in reader)

## References
- OpenGroup Exchange Format: http://www.opengroup.org/xsd/archimate/3.0/
- Reference file: `temp/demo-good.xml` (valid OpenGroup Exchange format)
- Related files: `src/pyArchimate/readers/archimateReader.py`
