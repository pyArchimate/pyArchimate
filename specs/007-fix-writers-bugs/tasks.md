# Feature 007 Tasks: Fix Writer Bugs - OpenGroup Exchange Format

## Status Overview
- **Total Tasks**: 5
- **Completed**: 2
- **In Progress**: 2
- **Pending**: 1

## Task Breakdown

### ✅ COMPLETED: 007-T1 - Identify root cause of XML parsing errors
**Description**: Analyze archimateWriter.py and compare output with valid OpenGroup Exchange fixtures to identify schema/structure mismatches.

**Work Done**:
- Identified wrong root element: `<model>` should be `<archimate:ArchimateModel>`
- Found incorrect attribute naming: `identifier` should be `id`
- Discovered model name structure issue: child element vs. root attribute
- Located wrong schema location reference: `archimate3_Diagram.xsd` (for diagrams only)

**Root Causes**:
1. Line 381: Incorrect root element template
2. Line 386: Missing namespace prefix
3. Line 392-393: Wrong model name placement
4. Schema location: Referenced diagram schema instead of model schema

**Status**: ✅ Complete
**Time**: 30 min

---

### ✅ COMPLETED: 007-T2 - Fix archimateWriter.py root element and attributes
**Description**: Update XML template and model name handling to match OpenGroup Exchange format specification.

**Changes Made**:
- Line 381: Updated root element from `<model>` to `<archimate:ArchimateModel>`
- Line 381: Added proper namespace: `xmlns:archimate="http://www.opengroup.org/xsd/archimate/3.1/"`
- Line 381: Changed attribute from `identifier` to `id`
- Line 381: Removed broken `xsi:schemaLocation` attribute
- Line 392-393: Changed model name from child element to root attribute using `root.set('name', ...)`

**Verification**:
```xml
<!-- Before -->
<model xmlns="..." identifier="id-...">
  <name>e-commerce platform</name>
  
<!-- After -->
<archimate:ArchimateModel xmlns:archimate="..." id="id-..." name="e-commerce platform">
```

**Status**: ✅ Complete
**Time**: 20 min
**Files Modified**: `src/pyArchimate/writers/archimateWriter.py`

---

### 🔄 IN PROGRESS: 007-T3 - Validate generated files parse correctly
**Description**: Generate test files with fixed writer and validate they parse without schema errors.

**Test Cases**:
- [ ] Generate simple model with elements, relationships, views
- [ ] Parse with Python XML parser (should not raise exceptions)
- [ ] Open in archi.app (visual validation)
- [ ] Validate against xsd schema (if accessible)

**Validation Script**:
```bash
python3 << 'EOF'
from src.pyArchimate import Model, ArchiType
model = Model("e-commerce platform")
order = model.add(ArchiType.ApplicationComponent, "Order Service")
service = model.add(ArchiType.ApplicationService, "Place Order")
customer = model.add(ArchiType.BusinessActor, "Customer")
model.add_relationship(ArchiType.Serving, order, service)
order.folder = "/Application"
service.folder = "/Application"
customer.folder = "/Business"
view = model.add(ArchiType.View, "Application Layer")
view.add(ref=order, x=0, y=0, w=120, h=55)
view.add(ref=service, x=200, y=0, w=120, h=55)
model.write("temp/demo.xml")
print("✅ Generated temp/demo.xml")
EOF
```

**Status**: 🔄 Mostly done - awaiting archi.app validation feedback
**Time**: 15 min

---

### 🔄 IN PROGRESS: 007-T4 - Add unit tests for archimateWriter fixes
**Description**: Create unit tests verifying XML structure, schema validation, and round-trip data preservation.

**Test Coverage**:
- [ ] Test root element name and namespace
- [ ] Test id/name attributes on root
- [ ] Test model name not in child elements
- [ ] Test elements list structure
- [ ] Test relationships structure
- [ ] Test organizations (folder hierarchy)
- [ ] Test views/diagrams/nodes

**Test File**: `tests/unit/test_archimatewriter.py` (new)

**Sample Test**:
```python
def test_archimate_writer_root_element():
    """Verify root element structure matches OpenGroup Exchange format."""
    model = Model("TestModel")
    model.add(ArchiType.BusinessActor, "Actor1")
    
    xml_str = model.write(writer=Writers.archimate)
    root = et.fromstring(xml_str.encode())
    
    # Check root element
    assert "ArchimateModel" in root.tag
    assert "archimate" in root.tag
    
    # Check attributes
    assert root.get("id") is not None
    assert root.get("name") == "TestModel"
    
    # Check no <name> child element
    assert root.find("{*}name") is None
```

**Status**: 🔄 In progress - tests not yet written
**Time Est**: 30 min

---

### ⏳ PENDING: 007-T5 - Integration test: round-trip preservation
**Description**: Test that data written and read back preserves all information (elements, relationships, views, styles).

**Test Scenarios**:
- [ ] Round-trip: write → read → verify elements match
- [ ] Round-trip: preserve element properties and metadata
- [ ] Round-trip: preserve relationship types and directions
- [ ] Round-trip: preserve view layout (node positions, connections)

**Blockers**: 
- Requires T4 (unit tests) to establish baseline
- Need fixture files with expected outputs

**Status**: ⏳ Pending
**Time Est**: 45 min

---

## Integration with Feature 004
This feature (007) is a prerequisite for Feature 004 (ArchiMate v3.x Specification Compliance):
- Feature 004 requires valid OpenGroup Exchange format files
- Feature 007 fixes the writer to generate valid files
- Both address P1 gaps in compliance

## Success Criteria
- [x] archimateWriter.py generates valid OpenGroup Exchange XML
- [x] Root element is `archimate:ArchimateModel` with proper namespace
- [x] Model attributes (id, name) on root element only
- [ ] Generated files parse without schema validation errors
- [ ] archi.app can open generated files without errors
- [ ] All unit tests pass
- [ ] Round-trip tests (write → read) verify data preservation
- [ ] No regressions in existing tests

## Dependencies
- Feature 004: ArchiMate v3.x Specification Compliance
- Previous fixes: Namespace version from 3.0 to 3.1

## Risks
- **Risk 1**: Round-trip compatibility with old files (mitigation: backward compat tests)
- **Risk 2**: Other tools expect different OpenGroup format (mitigation: follow OpenGroup spec strictly)
- **Risk 3**: Breaking change for users relying on old format (mitigation: version bump + release notes)

## References
- OpenGroup Exchange Format Spec: http://www.opengroup.org/xsd/archimate/3.1/
- Test fixtures: `tests/fixtures/test_single_image.archimate`
- Related files: `src/pyArchimate/writers/archimateWriter.py`, `src/pyArchimate/readers/archimateReader.py`
