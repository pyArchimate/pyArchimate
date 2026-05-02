# Feature 006: Archi Tool Fidelity & Bug Fixes — Implementation Tasks

**Feature Branch**: `006-archi-tool-compliance`  
**Total Tasks**: 8  
**Estimated Effort**: ~90 minutes  
**Target Completion**: 2026-05-02

---

## Task Dependency Graph

```
Phase 1: Setup (0 tasks - no infrastructure needed)
         ↓
Phase 2: Foundational (1 task - helper function)
         T001: Create parse_bool() helper
         ↓
Phase 3: User Story 1 - Label Visibility (4 tasks - can execute in parallel after T001)
    ├─ T002 [P] [US1]: Fix boolean reader (line 115-116)
    ├─ T003 [P] [US1]: Fix boolean writer (line 149-151)
    ├─ T005 [P] [US1]: Unit tests for parse_bool()
    └─ T006 [P] [US1]: Integration test for label round-trip
         ↓
Phase 4: User Story 2 - View Documentation (2 tasks - can execute in parallel after T001)
    ├─ T004 [P] [US2]: Fix view documentation extraction (line 237)
    └─ T007 [P] [US2]: Integration test for view documentation round-trip
         ↓
Phase 5: Polish (1 task)
    └─ T008: Regression tests + Feature 004 compatibility check
```

---

## Phase 1: Setup

No setup tasks required. All dependencies (pytest, behave, lxml) are existing.

---

## Phase 2: Foundational

### T001: Create parse_bool() Helper Function

**Story**: Foundational  
**Effort**: ~5 minutes  
**Blocking**: T002, T003, T005, T006, T007

- [ ] T001 Create `parse_bool()` helper function in `src/pyArchimate/helpers.py`
  - Implement per W3C xsd:boolean spec
  - Handle inputs: "true", "false", "1", "0", case-insensitive
  - Handle edge cases: None, empty string, whitespace
  - Return boolean value (True/False)
  - See `specs/006-archi-tool-compliance/contracts/boolean-handling.md` for specification

**Test Command**: None (function tested in T005)

**Acceptance**:
- Function exists and is importable
- Returns True for "true", "TRUE", "1", " true "
- Returns False for "false", "FALSE", "0", None, ""
- No exceptions on edge cases

---

## Phase 3: User Story 1 - Fix Label Visibility Parsing

**Goal**: Diagram element labels preserve their visibility state (hidden/shown) through export/import cycles  
**Story Priority**: P1 (Critical)  
**MVP Scope**: ✅ Fully included

### T002: Fix Boolean Parsing in Reader (Line 115-116)

**Story**: [US1]  
**Effort**: ~2 minutes  
**Parallelizable**: [P]  
**Depends on**: T001

- [ ] T002 [P] [US1] Fix label visibility parsing in `src/pyArchimate/readers/_archireader_helpers.py:115-116`
  - Current: `conn.show_label = bool(ft.get('value'))`
  - Fixed: `conn.show_label = parse_bool(ft.get('value'))`
  - Import `parse_bool` from helpers module
  - Verify: Test against nameVisible="false" inputs

**Test Command**: pytest tests/unit/test_archireader_helpers.py::test_parse_bool_in_reader -v

**Acceptance**:
- Line 115-116 uses parse_bool() instead of bool()
- Import statement added at top of file
- Code diff shows exactly 1-2 lines changed

---

### T003: Fix Boolean Output in Writer (Line 149-151)

**Story**: [US1]  
**Effort**: ~5 minutes  
**Parallelizable**: [P]  
**Depends on**: T001

- [ ] T003 [P] [US1] Verify/fix boolean output in `src/pyArchimate/writers/archiWriter.py:149-151`
  - Current: May use `str(show_label)` → "True"/"False" (capitalized)
  - Fixed: Output lowercase "true"/"false" to match Archi spec
  - Change: `ft.set('value', 'true' if show_label else 'false')`
  - Verify: Exported XML contains nameVisible="false" (lowercase)

**Test Command**: pytest tests/unit/test_archiwriter.py::test_boolean_output -v

**Acceptance**:
- Writer produces lowercase "true" and "false"
- No capitalized "True"/"False" in output
- Existing tests still pass

---

### T005: Unit Tests for parse_bool() Function

**Story**: [US1]  
**Effort**: ~15 minutes  
**Parallelizable**: [P]  
**Depends on**: T001

- [ ] T005 [P] [US1] Create unit tests for `parse_bool()` in `tests/unit/test_helpers.py`
  - Test: `parse_bool(None)` → False
  - Test: `parse_bool("true")` → True
  - Test: `parse_bool("false")` → False
  - Test: `parse_bool("True")` → True (case-insensitive)
  - Test: `parse_bool("1")` → True
  - Test: `parse_bool("0")` → False
  - Test: `parse_bool("")` → False
  - Test: `parse_bool("  true  ")` → True (whitespace trimmed)
  - Test: `parse_bool("random")` → False (invalid input)
  - See `specs/006-archi-tool-compliance/contracts/boolean-handling.md` for complete spec

**Test Command**: pytest tests/unit/test_helpers.py::test_parse_bool -v

**Acceptance**:
- All 9+ test cases pass
- Code coverage for parse_bool() = 100%
- No uncaught exceptions

---

### T006: Integration Test - Label Visibility Round-Trip

**Story**: [US1]  
**Effort**: ~20 minutes  
**Parallelizable**: [P]  
**Depends on**: T002, T003

- [ ] T006 [P] [US1] Create integration test for label visibility round-trip in `tests/integration/test_archimate_roundtrip.py`
  - Test: Import Archi file with `nameVisible="false"` → verify `conn.show_label=False`
  - Test: Import Archi file with `nameVisible="true"` → verify `conn.show_label=True`
  - Test: Import, export, re-import → label visibility matches exactly
  - Verify: No regression in existing Feature 004 tests
  - See `specs/006-archi-tool-compliance/quickstart.md` for manual test workflow

**Test Command**: pytest tests/integration/test_archimate_roundtrip.py::test_label_visibility_round_trip -v

**Acceptance**:
- Round-trip test passes
- Label visibility preserved exactly: hidden → hidden, visible → visible
- No regression in existing tests
- Test covers both positive and negative cases (true/false, hidden/shown)

---

## Phase 4: User Story 2 - Fix View Documentation Extraction

**Goal**: View-level documentation text is preserved during import  
**Story Priority**: P1 (Critical)  
**MVP Scope**: ✅ Fully included

### T004: Fix View Documentation Text Extraction (Line 237)

**Story**: [US2]  
**Effort**: ~2 minutes  
**Parallelizable**: [P]  
**Depends on**: T001 (none, but grouped with Phase 2 for convenience)

- [ ] T004 [P] [US2] Fix view documentation text extraction in `src/pyArchimate/readers/_archireader_helpers.py:237`
  - Current: `elem.desc = e.text` (wrong - uses parent element text)
  - Fixed: `elem.desc = doc.text` (correct - uses documentation element text)
  - Verify: Line 237 now matches pattern used for elements/relationships (lines 161, 178)
  - Code change: Exactly 1 line

**Test Command**: pytest tests/unit/test_archireader_helpers.py::test_view_documentation_extraction -v

**Acceptance**:
- Line 237 changed from `e.text` to `doc.text`
- No other changes to the function
- Diff shows exactly 1 line change

---

### T007: Integration Test - View Documentation Round-Trip

**Story**: [US2]  
**Effort**: ~20 minutes  
**Parallelizable**: [P]  
**Depends on**: T004

- [ ] T007 [P] [US2] Create integration test for view documentation round-trip in `tests/integration/test_archimate_roundtrip.py`
  - Test: Import Archi file with view `<documentation>` elements → verify `view.desc` is set
  - Test: Import, export, re-import → view documentation text matches exactly
  - Test: Empty `<documentation>` → handled gracefully (view.desc = None or "")
  - Test: Documentation with special characters → preserved exactly
  - See `specs/006-archi-tool-compliance/quickstart.md` for manual test workflow

**Test Command**: pytest tests/integration/test_archimate_roundtrip.py::test_view_documentation_round_trip -v

**Acceptance**:
- Round-trip test passes
- Documentation text preserved exactly
- Empty documentation handled gracefully
- No regression in existing tests
- Test covers positive, negative, and edge cases

---

## Phase 5: Polish & Regression

### T008: Regression Tests & Feature 004 Compatibility Check

**Story**: Polish  
**Effort**: ~10 minutes  
**Blocking**: None (final validation)

- [ ] T008 Verify no regressions and Feature 004 compatibility
  - Run full test suite: `pytest tests/ -v`
  - Run BDD scenarios: `behave tests/features/ --format progress`
  - Verify code coverage: ≥ 90% on modified files
  - Verify Feature 004 tests still pass (relationship docs, influence strength, BusinessInteraction)
  - Create BDD scenarios for label visibility and view documentation (optional)
    - `tests/features/archi_label_visibility.feature`
    - `tests/features/archi_view_documentation.feature`

**Test Command**: pytest tests/ && behave tests/features/

**Acceptance**:
- All tests pass (pytest + behave)
- Code coverage ≥ 90% on:
  - `src/pyArchimate/helpers.py` (parse_bool)
  - `src/pyArchimate/readers/_archireader_helpers.py` (lines 115-116, 237)
  - `src/pyArchimate/writers/archiWriter.py` (lines 149-151)
- No regression in Feature 004 tests
- All acceptance criteria from spec.md are met

---

## Task Execution Strategy

### MVP Scope

**Recommended MVP**: All user stories (T001-T008)

Rationale: Both bugs are P1 critical and fix straightforward issues (5 lines of code changed). No partial scope makes sense; both fixes are needed for faithful round-trip support.

### Parallel Execution Plan

**After T001** (parse_bool helper created), you can execute **in parallel**:
- T002, T003, T005, T006 (Label visibility fixes)
- T004, T007 (View documentation fix)

Example execution schedule:
```
Time 0:00-0:05   → T001 (create helper)
Time 0:05-0:25   → T002, T004 (both readers, parallel)
Time 0:25-0:30   → T003 (writer fix, parallel)
Time 0:30-0:45   → T005 (unit tests, parallel)
Time 0:45-1:05   → T006, T007 (integration tests, parallel)
Time 1:05-1:15   → T008 (regression tests)
Total: ~75 minutes (with parallelization)
```

### Independent Test Criteria

**Per User Story**:

| US | Min. Tests to Validate | Pass/Fail Criteria |
|----|------------------------|--------------------|
| [US1] Label Visibility | T005 + T006 | All assertions pass; round-trip fidelity confirmed |
| [US2] View Documentation | T004 + T007 | All assertions pass; round-trip fidelity confirmed |
| Polish | T008 | Full suite passes; no regressions |

---

## Files to Modify

| File | Lines | Task(s) | Change Type |
|------|-------|---------|-------------|
| `src/pyArchimate/helpers.py` | New | T001 | New function (parse_bool) |
| `src/pyArchimate/readers/_archireader_helpers.py` | 115-116 | T002 | Replace bool() with parse_bool() |
| `src/pyArchimate/readers/_archireader_helpers.py` | 237 | T004 | Replace e.text with doc.text |
| `src/pyArchimate/writers/archiWriter.py` | 149-151 | T003 | Normalize boolean output |
| `tests/unit/test_helpers.py` | New | T005 | New test function (test_parse_bool) |
| `tests/integration/test_archimate_roundtrip.py` | New | T006, T007 | New test functions |
| `tests/features/*.feature` | New | T008 (optional) | BDD scenarios |

---

## Success Checklist

- [ ] All 8 tasks completed
- [ ] All unit tests pass (T005)
- [ ] All integration tests pass (T006, T007)
- [ ] Full regression test suite passes (T008)
- [ ] Code coverage ≥ 90%
- [ ] No breaking API changes
- [ ] Backward compatible
- [ ] Commits follow project conventions
- [ ] Branch ready for PR to develop

---

## References

- **Specification**: `specs/006-archi-tool-compliance/spec.md`
- **Plan**: `specs/006-archi-tool-compliance/plan.md`
- **Research**: `specs/006-archi-tool-compliance/research.md`
- **Contracts**: `specs/006-archi-tool-compliance/contracts/`
- **Testing Guide**: `specs/006-archi-tool-compliance/quickstart.md`
- **Related**: Feature 004 (`specs/004-archimate-spec-compliance/`)
