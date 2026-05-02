# Feature 007: Fix Writer Bugs - OpenGroup Exchange Format Compliance

## Overview
Fix critical bugs in `archimateWriter.py` that prevent generated OpenGroup Exchange format files from parsing correctly in standard ArchiMate tools (specifically archi.app and XML validators).

## Problem Statement
The default writer (OpenGroup Exchange format) was generating invalid XML that failed schema validation with error:
```
org.xml.sax.SAXParseException: cvc-elt.1.a - Declaration of element 'model' not found
```

Root causes identified:
1. **Wrong root element**: Using `<model>` instead of `<archimate:ArchimateModel>`
2. **Wrong namespace prefix**: Missing `archimate:` namespace prefix
3. **Wrong attribute names**: Using `identifier` instead of `id` on root element
4. **Wrong attribute placement**: Model name as child element `<name>` instead of attribute
5. **Wrong schema location**: Referencing non-existent/incorrect schema file

## P1 Gaps Addressed
- **Gap 1**: Enable BusinessInteraction element creation (feature 004 - shared concern)
- **Gap 2**: Fix influence strength round-trip metadata preservation (feature 004 - shared concern)
- **Gap 3**: Preserve relationship documentation during import/export (feature 004 - shared concern)
- **Gap 4 (NEW)**: Fix OpenGroup Exchange format XML structure compliance

## Technical Details

### archimateWriter.py Changes

#### Issue 1: Root Element Structure
**Before:**
```xml
<model xmlns="http://www.opengroup.org/xsd/archimate/3.1/" 
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.opengroup.org/xsd/archimate/3.1/ http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd"
       identifier="id-...">
    <name>Model Name</name>
    ...
</model>
```

**After:**
```xml
<archimate:ArchimateModel xmlns:archimate="http://www.opengroup.org/xsd/archimate/3.1/" 
                          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                          id="id-..."
                          name="Model Name">
    ...
</archimate:ArchimateModel>
```

#### Issue 2: Schema Location
- **Removed**: `xsi:schemaLocation` attribute (schema files not reliably accessible/correct)
- **Rationale**: Namespace alone sufficient for identification; tools don't strictly validate against schema on open

#### Issue 3: Model Name Handling
- **Changed**: From child element `<name>text</name>` to root attribute `name="text"`
- **Location**: Line 392-393 in archimateWriter.py

### Compliance Matrix
| Aspect | Status | Details |
|--------|--------|---------|
| Root element name | ✅ Fixed | Changed to `archimate:ArchimateModel` |
| Root element namespace | ✅ Fixed | Using `xmlns:archimate=` with correct URI |
| Root element prefix | ✅ Fixed | Added `archimate:` prefix |
| Root attributes | ✅ Fixed | `id` and `name` attributes now on root |
| Schema location | ✅ Fixed | Removed problematic schemaLocation attribute |
| Child element structure | ✅ Compatible | `<elements>`, `<relationships>`, `<organizations>`, `<views>` intact |

## Test Plan

### Unit Tests
- [ ] Test OpenGroup Exchange format XML structure validation
- [ ] Test round-trip: write → read → compare (fixture: test.archimate)
- [ ] Test model name attribute handling
- [ ] Test namespace declaration in generated files

### Integration Tests
- [ ] Validate generated XML parses without schema errors
- [ ] Test archi.app can open generated files without errors
- [ ] Test model data preserved during round-trip
- [ ] Verify views, nodes, connections preserved with correct positioning

### BDD Scenarios
- [ ] Scenario: Generate OpenGroup Exchange file with elements and relationships
- [ ] Scenario: Round-trip file through read/write cycle preserves all data
- [ ] Scenario: Generated files validate against OpenGroup XSD schema

## Files Modified
- `src/pyArchimate/writers/archimateWriter.py` (lines 380-393)

## Files Testing Impact
- `tests/unit/test_writers.py` (new or updated)
- `tests/integration/test_roundtrip.py` 
- `tests/fixtures/` (may need new fixtures)
- `tests/features/` (BDD scenarios)

## Validation Commands
```bash
# Validate XML structure
python3 -m xml.dom.minidom temp/demo.xml

# Test round-trip
python3 << 'EOF'
from src.pyArchimate import Model, ArchiType
m = Model("test")
m.add(ArchiType.BusinessActor, "Test")
m.write("test_out.xml")
m2 = Model()
m2.read("test_out.xml")
assert m2.name == "test"
print("✅ Round-trip test passed")
EOF

# Visual inspection
open -a "archi.app" temp/demo.xml
```

## Rollout Strategy
1. **Merge**: After unit + integration tests pass
2. **Soak**: Run against all existing test fixtures (ensure no regressions)
3. **Validate**: Spot-check with archi.app on key scenarios
4. **Monitor**: Check for any open issues from users of previous version

## Links
- Feature 004: ArchiMate v3.x Specification Compliance
- Issue: OpenGroup Exchange format files fail XML validation
- Fixture reference: `tests/fixtures/test_single_image.archimate`

## Status
- **Phase**: Implementation
- **Owner**: Claude
- **Target**: Completion before feature 004 merge
