# Quick Start: Feature 006 Testing Guide

**Date**: 2026-05-02  
**Target**: Developers implementing and testing the label visibility and view documentation fixes

## Overview

Feature 006 fixes two bugs:
1. **Label Visibility**: `bool("false")` → `True` (should be `False`)
2. **View Documentation**: `e.text` → should be `doc.text`

This guide shows how to test both fixes end-to-end.

## Prerequisites

```bash
cd /Users/xavier/PycharmProjects/pyArchimate
poetry install
poetry run pytest --version  # Verify pytest is available
poetry run behave --version  # Verify behave is available
```

## Test Command Reference

### Run All Tests

```bash
# Unit tests only
poetry run pytest tests/unit/ -v

# Integration tests only
poetry run pytest tests/integration/ -v

# BDD acceptance tests
poetry run behave tests/features/ --format progress

# All tests
poetry run pytest tests/ && poetry run behave tests/features/
```

### Run Feature 006 Tests Specifically

```bash
# Test boolean parsing helper
poetry run pytest tests/unit/test_helpers.py::test_parse_bool -v

# Test label visibility round-trip
poetry run pytest tests/integration/test_archimate_roundtrip.py::test_label_visibility_round_trip -v

# Test view documentation round-trip
poetry run pytest tests/integration/test_archimate_roundtrip.py::test_view_documentation_round_trip -v

# BDD scenarios for Feature 006
poetry run behave tests/features/archi_label_visibility.feature --format progress
poetry run behave tests/features/archi_view_documentation.feature --format progress
```

## Manual Testing Workflow

### 1. Test Label Visibility Fix

**Scenario**: Import an Archi file with hidden labels, verify they stay hidden.

**Setup**:
1. Create test Archi file `test_hidden_labels.archimate` with connections that have `nameVisible="false"`
2. Import into pyArchimate model
3. Verify `connection.show_label == False`
4. Export to new Archi file
5. Verify exported XML contains `value="false"` (not "true")

**Commands**:
```python
from src.pyArchimate.readers.archimateReader import read_archimate
from src.pyArchimate.writers.archimateWriter import write_archimate

# Import
model = read_archimate('test_hidden_labels.archimate')

# Check imported connection
for conn in model.conns:
    print(f"Connection {conn.uuid}: show_label={conn.show_label}")
    # Should show show_label=False for previously hidden connections

# Export and re-import
write_archimate('test_hidden_labels_export.archimate', model)
model_reimport = read_archimate('test_hidden_labels_export.archimate')

# Verify round-trip
for conn in model_reimport.conns:
    print(f"Connection {conn.uuid}: show_label={conn.show_label}")
    # Should show same values as original
```

**Expected Result**: Labels marked as hidden remain hidden after round-trip.

### 2. Test View Documentation Fix

**Scenario**: Import an Archi file with view documentation, verify it's preserved.

**Setup**:
1. Create test Archi file `test_view_docs.archimate` with views that have `<documentation>` elements
2. Import into pyArchimate model
3. Verify `view.desc` contains the documentation text
4. Export to new Archi file
5. Verify exported XML contains the documentation

**Commands**:
```python
from src.pyArchimate.readers.archimateReader import read_archimate
from src.pyArchimate.writers.archimateWriter import write_archimate

# Import
model = read_archimate('test_view_docs.archimate')

# Check imported views
for view in model.views:
    print(f"View {view.name}: desc='{view.desc}'")
    # Should show view.desc with documentation text (not None)

# Export and re-import
write_archimate('test_view_docs_export.archimate', model)
model_reimport = read_archimate('test_view_docs_export.archimate')

# Verify round-trip
for view in model_reimport.views:
    print(f"View {view.name}: desc='{view.desc}'")
    # Should show same documentation as original
```

**Expected Result**: View documentation text is preserved after round-trip.

## BDD Feature Files

Create BDD scenarios following existing patterns:

### `tests/features/archi_label_visibility.feature`

```gherkin
Feature: Archi label visibility round-trip fidelity
  
  Scenario: Hidden labels remain hidden after import
    Given an Archi file with connections marked nameVisible="false"
    When I import the file into pyArchimate
    Then each connection should have show_label=False
    
  Scenario: Hidden labels remain hidden after export
    Given a pyArchimate model with connections where show_label=False
    When I export to an Archi file
    Then each connection should have nameVisible="false" in the XML
    
  Scenario: Label visibility survives round-trip
    Given an Archi file with mixed label visibility (some true, some false)
    When I import and export back to Archi
    Then label visibility is preserved exactly
```

### `tests/features/archi_view_documentation.feature`

```gherkin
Feature: Archi view documentation round-trip fidelity
  
  Scenario: View documentation is imported correctly
    Given an Archi file with views that have <documentation> elements
    When I import the file into pyArchimate
    Then each view's desc property contains the documentation text
    
  Scenario: View documentation is exported correctly
    Given a pyArchimate model with views that have documentation
    When I export to an Archi file
    Then each view has a <documentation> element with the correct text
    
  Scenario: View documentation survives round-trip
    Given an Archi file with various view documentation
    When I import and export back to Archi
    Then all documentation text is preserved exactly
```

## Success Checklist

- [ ] **Unit Tests Pass**: `pytest tests/unit/ -v` — all boolean parsing tests pass
- [ ] **Integration Tests Pass**: `pytest tests/integration/ -v` — label & documentation round-trip tests pass
- [ ] **BDD Scenarios Pass**: `behave tests/features/archi_*.feature` — end-to-end acceptance tests pass
- [ ] **No Regression**: All existing Feature 004 tests still pass
- [ ] **Code Coverage**: ≥ 90% on modified files (`_archireader_helpers.py`, `helpers.py`)
- [ ] **Manual Testing**: Round-trip workflow confirms fixes work with real Archi files

## Troubleshooting

### Test: `bool("false")` returns True

**Issue**: `parse_bool()` function not yet implemented  
**Fix**: Create `src/pyArchimate/helpers.py` with the function (or add to existing helpers module)

### Test: View documentation still None after import

**Issue**: Line 237 still uses `e.text` instead of `doc.text`  
**Fix**: Update `src/pyArchimate/readers/_archireader_helpers.py:237`

### Test: Exported label visibility is "True" not "true"

**Issue**: Writer uses `str(bool_value)` which produces capitalized "True"/"False"  
**Fix**: Normalize output in `src/pyArchimate/writers/archiWriter.py:149-151`

## Integration with CI/CD

Once fixes are implemented, add to CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Feature 006 tests
  run: |
    poetry run pytest tests/unit/test_helpers.py::test_parse_bool -v
    poetry run pytest tests/integration/test_archimate_roundtrip.py -k "label_visibility or view_documentation" -v
    poetry run behave tests/features/archi_*.feature
```

## Related Documentation

- Feature 004 (ArchiMate v3.x compliance): `specs/004-archimate-spec-compliance/plan.md`
- ArchiToolGap.md: Gap analysis of Archi adapter fidelity
- CLAUDE.md: Project guidelines and active technologies
