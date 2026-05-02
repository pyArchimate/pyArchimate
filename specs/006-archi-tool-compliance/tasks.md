# Feature 006: Archi Tool Fidelity & Bug Fixes — Implementation Tasks

**Feature Branch**: `006-archi-tool-compliance`  
**Total Tasks**: 15 (13 implementation + 2 polish/refactoring)  
**Estimated Effort**: ~170 minutes (~2.8 hours) + ~30 minutes refactoring  
**Target Completion**: 2026-05-02 ✅ COMPLETED  
**Scope Expansion**: Added image preservation validation (US-003)
**Additional Work**: Cognitive complexity refactoring + comprehensive docstrings

**Status**: ✅ ALL TASKS COMPLETED — Ready for pull request to develop branch

---

## Task Dependency Graph

```
Phase 1: Setup (0 tasks - no infrastructure needed)
         ↓
Phase 2: Foundational (1 task - helper functions)
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
Phase 5: User Story 3 - Image Preservation (4 tasks - can execute in parallel after T001)
    ├─ T009 [P] [US3]: Create test Archi files with embedded images
    ├─ T010 [P] [US3]: Implement image extraction/comparison helper
    ├─ T011 [P] [US3]: Integration test for single image round-trip
    └─ T012 [P] [US3]: Integration test for multiple images round-trip
         ↓
Phase 6: Polish (1 task)
    └─ T013: Regression tests + Feature 004 compatibility check
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

- [x] T001 Create `parse_bool()` helper function in `src/pyArchimate/helpers/parsing.py` ✅
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

- [x] T002 [P] [US1] Fix label visibility parsing in `src/pyArchimate/readers/_archireader_helpers.py:125` ✅
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

- [x] T003 [P] [US1] Verify/fix boolean output in `src/pyArchimate/writers/archiWriter.py:160-162` ✅
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

- [x] T005 [P] [US1] Create unit tests for `parse_bool()` in `tests/unit/test_parsing_helpers.py` ✅
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

- [x] T006 [P] [US1] Create integration test for label visibility round-trip in `tests/integration/test_label_visibility_roundtrip.py` ✅
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

- [x] T004 [P] [US2] Fix view documentation text extraction in `src/pyArchimate/readers/_archireader_helpers.py:238` ✅
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

- [x] T007 [P] [US2] Create integration test for view documentation round-trip in `tests/integration/test_view_documentation_roundtrip.py` ✅
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

## Phase 5: User Story 3 - Image Preservation in Round-Trip

**Goal**: Embedded images in Archi files survive import/export cycles with exact fidelity  
**Story Priority**: P1 (Critical)  
**MVP Scope**: ✅ Fully included

### T009: Create Test Archi Files with Embedded Images

**Story**: [US3]  
**Effort**: ~15 minutes  
**Parallelizable**: [P]  
**Depends on**: None (independent test fixture creation)

- [x] T009 [P] [US3] Create minimal Archi files with embedded test images in `tests/fixtures/` ✅
  - Create 1x1 PNG image (smallest valid PNG, ~70 bytes)
  - Create simple SVG image (plain text, ~200 bytes)
  - Embed both as base64 in Archi XML structure
  - Create two test files:
    - `test_single_image.archimate` — one PNG image embedded
    - `test_multiple_images.archimate` — both PNG and SVG images embedded
  - Store base64 hashes for comparison (see T010)
  - Commit test files to repo

**Test Command**: ls -la tests/fixtures/test_*_image.archimate

**Acceptance**:
- Test files exist and are valid XML
- Base64 data is embedded correctly in archimate elements
- Files are small enough for version control (<1 MB total)
- Each test file can be imported without errors

---

### T010: Implement Image Data Extraction & Comparison Helper

**Story**: [US3]  
**Effort**: ~15 minutes  
**Parallelizable**: [P]  
**Depends on**: None (independent utility)

- [x] T010 [P] [US3] Create image comparison utility in `src/pyArchimate/helpers/parsing.py` ✅
  - Function: `extract_images(archimate_xml_element)` → list of base64 strings
  - Function: `compare_image_data(data1, data2)` → bool (byte-for-byte match)
  - Handle multiple image elements in a single file
  - Return list of image base64 strings in consistent order
  - No image decoding or re-encoding (strings only)

**Test Command**: pytest tests/unit/test_helpers.py::test_image_extraction -v

**Acceptance**:
- Functions exist and are importable
- `extract_images()` returns list of base64 strings
- `compare_image_data()` returns True for identical data, False otherwise
- Handles edge cases: missing images, empty lists, None values

---

### T011: Integration Test - Single Image Round-Trip

**Story**: [US3]  
**Effort**: ~20 minutes  
**Parallelizable**: [P]  
**Depends on**: T009, T010

- [x] T011 [P] [US3] Create integration test for single image preservation in `tests/integration/test_image_preservation_roundtrip.py` ✅
  - Load `test_single_image.archimate` file
  - Extract image base64 data
  - Import into pyArchimate model
  - Export to new Archi file
  - Re-import and extract image data again
  - Compare: original base64 == re-imported base64 (byte-for-byte)
  - Verify: no errors during any step

**Test Command**: pytest tests/integration/test_archimate_roundtrip.py::test_single_image_round_trip -v

**Acceptance**:
- Image data preserved exactly (base64 strings match byte-for-byte)
- Round-trip completes without errors
- Test covers both import and export paths

---

### T012: Integration Test - Multiple Images Round-Trip

**Story**: [US3]  
**Effort**: ~20 minutes  
**Parallelizable**: [P]  
**Depends on**: T009, T010

- [x] T012 [P] [US3] Create integration test for multiple images preservation in `tests/integration/test_image_preservation_roundtrip.py` ✅
  - Load `test_multiple_images.archimate` file (PNG + SVG)
  - Extract all image base64 data (should be 2 images)
  - Import into pyArchimate model
  - Export to new Archi file
  - Re-import and extract all images again
  - Compare: each image base64 == re-imported base64 (byte-for-byte)
  - Verify: no data loss or reordering

**Test Command**: pytest tests/integration/test_archimate_roundtrip.py::test_multiple_images_round_trip -v

**Acceptance**:
- All image data preserved exactly (both PNG and SVG)
- Image order preserved (if applicable)
- No data loss or corruption
- Test covers diverse image formats (PNG, SVG)

---

## Phase 6: Polish & Regression

### T013: Regression Tests & Feature 004 Compatibility Check

**Story**: Polish  
**Effort**: ~10 minutes  
**Blocking**: None (final validation)

- [x] T013 Verify no regressions and Feature 004 compatibility ✅
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

## Phase 7: Code Quality & Documentation Polish

### T014: Refactor _process_folder_element() to Reduce Cognitive Complexity

**Story**: Polish  
**Effort**: ~25 minutes  
**Parallelizable**: [P]  
**Depends on**: None (independent refactoring)

- [x] T014 Refactor `_process_folder_element()` in `src/pyArchimate/readers/_archireader_helpers.py` to reduce cognitive complexity below 15 ✅
  - Extract 5 helper functions to reduce main function complexity
  - Helper: `_process_viewpoint_property()` - viewpoint assignment with validation
  - Helper: `_process_property()` - property dispatch (viewpoint vs generic)
  - Helper: `_get_or_create_element()` - element retrieval with merge logic
  - Helper: `_set_documentation()` - documentation extraction
  - Helper: `_set_junction_type()` - junction type with 'and' default
  - Main function complexity reduced from ~15+ to ~5
  - All 684 tests pass
  - Code coverage maintained at 93%

**Test Command**: pytest tests/ -q

**Acceptance**:
- Main function has simple linear flow
- Helper functions are well-structured with single responsibility
- All tests passing (684/684)
- No regressions in Feature 004 or earlier features

---

### T015: Add Docstrings to Helper Functions

**Story**: Polish  
**Effort**: ~5 minutes  
**Parallelizable**: [P]  
**Depends on**: T014

- [x] T015 Add docstrings to all extracted helper functions in `src/pyArchimate/readers/_archireader_helpers.py` ✅
  - Add concise one-line docstrings to:
    - `_process_viewpoint_property()`: Viewpoint assignment with validation
    - `_process_property()`: Property dispatch (viewpoint vs generic)
    - `_get_or_create_element()`: Element retrieval with merge logic
    - `_set_documentation()`: Documentation extraction
    - `_set_junction_type()`: Junction type assignment with default
  - Follow project docstring conventions
  - Maintain code readability and maintainability

**Test Command**: python -m pyright src/pyArchimate/readers/_archireader_helpers.py

**Acceptance**:
- All functions have clear docstrings
- pyright: 0 errors, 0 warnings
- mypy: No issues found
- ruff: All checks passed
- All tests passing (684/684)

---

## Task Execution Strategy

### MVP Scope

**Recommended MVP**: All user stories (T001-T013)

Rationale: All three bugs/gaps are P1 critical. Label visibility and documentation are straightforward (5 lines of code), and image validation is essential for faithful round-trip support. No partial scope makes sense.

### Parallel Execution Plan

**After T001** (parse_bool helper created), you can execute **in 3 independent parallel streams**:
- **Stream 1**: T002, T003, T005, T006 (Label visibility)
- **Stream 2**: T004, T007 (View documentation)
- **Stream 3**: T009, T010, T011, T012 (Image preservation)

Example execution schedule with maximum parallelization:
```
Time 0:00-0:05   → T001 (create helper)
Time 0:05-0:35   → T002, T004, T009 (parallel: readers + test files)
Time 0:35-0:40   → T003, T010 (parallel: writer + image helper)
Time 0:40-1:00   → T005, T011 (parallel: boolean unit tests + single image test)
Time 1:00-1:20   → T006, T007, T012 (parallel: label test + doc test + multi-image test)
Time 1:20-1:30   → T013 (regression tests)
Total: ~90 minutes (with maximum parallelization)
Overall: ~170 minutes serial → ~90 minutes parallel (47% efficiency)
```

### Independent Test Criteria

**Per User Story**:

| US | Min. Tests to Validate | Pass/Fail Criteria |
|----|------------------------|--------------------|
| [US1] Label Visibility | T005 + T006 | All assertions pass; round-trip fidelity confirmed (true/false, hidden/shown) |
| [US2] View Documentation | T004 + T007 | All assertions pass; round-trip fidelity confirmed (text preserved exactly) |
| [US3] Image Preservation | T009 + T010 + T011 + T012 | All assertions pass; byte-for-byte base64 comparison matches; no data loss |
| Polish | T013 | Full suite passes; no regressions in Feature 004 or earlier features |

---

## Files to Modify

| File | Lines | Task(s) | Change Type |
|------|-------|---------|-------------|
| `src/pyArchimate/helpers.py` | New | T001, T010 | New functions (parse_bool, image helpers) |
| `src/pyArchimate/readers/_archireader_helpers.py` | 115-116 | T002 | Replace bool() with parse_bool() |
| `src/pyArchimate/readers/_archireader_helpers.py` | 237 | T004 | Replace e.text with doc.text |
| `src/pyArchimate/writers/archiWriter.py` | 149-151 | T003 | Normalize boolean output |
| `tests/unit/test_helpers.py` | New | T005, T010 | New test functions (parse_bool, image extraction) |
| `tests/integration/test_archimate_roundtrip.py` | New | T006, T007, T011, T012 | New test functions (round-trip tests) |
| `tests/fixtures/test_single_image.archimate` | New | T009 | Test data (Archi file with 1 image) |
| `tests/fixtures/test_multiple_images.archimate` | New | T009 | Test data (Archi file with 2 images) |
| `tests/features/*.feature` | New | T013 (optional) | BDD scenarios |

---

## Success Checklist

- [x] All 15 tasks completed ✅
- [x] All unit tests pass (T005, T010) - 15 unit tests ✅
- [x] All integration tests pass (T006, T007, T011, T012) - 22 integration tests ✅
- [x] Test fixtures created (T009) ✅
- [x] Full regression test suite passes (T013) - 684/684 tests ✅
- [x] Code coverage ≥ 90% on modified files - 93% overall ✅
- [x] Image data preserved byte-for-byte (T011, T012) ✅
- [x] No breaking API changes ✅
- [x] Backward compatible ✅
- [x] Commits follow project conventions - 13 commits ✅
- [x] Branch ready for PR to develop ✅
- [x] Cognitive complexity refactored below 15 (T014) ✅
- [x] All functions documented with docstrings (T015) ✅
- [x] Code quality checks pass (pyright, mypy, ruff) ✅

---

## Implementation Summary

### Completed Work

**Total Commits**: 15  
**Branch**: `006-archi-tool-compliance`

#### Core Implementation (T001-T013)
- ✅ Parsing helper (`parse_bool`) with W3C xsd:boolean compliance
- ✅ Label visibility round-trip fidelity (nameVisible preservation)
- ✅ View documentation extraction and round-trip preservation
- ✅ Image preservation validation with byte-for-byte comparison
- ✅ Image property key handling ('image', 'image-data', 'image_data')
- ✅ 37 tests created (15 unit + 22 integration)
- ✅ 100% coverage on new parsing module
- ✅ Zero regressions in existing code (684/684 tests passing)

#### Code Quality (T014-T015)
- ✅ Cognitive complexity refactored below 15 in `_process_folder_element()`
- ✅ 5 helper functions extracted with single responsibility
- ✅ Comprehensive docstrings on all helper functions
- ✅ Type checking: pyright 0 errors, mypy 0 issues
- ✅ Linting: ruff all checks passed

### Commit History

```
bc81bfb docs: Add docstrings to helper functions in _archireader_helpers.py
9ed64bc refactor: Extract helper functions in _process_folder_element
873d699 fix(typing): Add type annotation for element parameter
05ecc3c fix(exports): Export parse_bool from helpers.parsing in __init__.py
fd880e3 test(T013): Verify regression tests and Feature 004 compatibility
d92d240 feat,test(T009-T012): Add image preservation validation with test fixtures
d8e5c81 test(T007): Add integration tests for view documentation round-trip
cd9be45 test(T006): Add integration tests for label visibility round-trip
a48df2a fix,test(T004,T005): Fix view docs extraction and add comprehensive unit tests
00b40fe fix(T002,T003): Fix label visibility boolean parsing in reader and writer
6ca1e50 feat(T001): Create parse_bool() and image helpers in parsing module
58f30ed docs: Expand Feature 006 scope to include image preservation validation
f766257 docs: Generate Feature 006 implementation tasks
468e611 docs: Add clarifications section to Feature 006 spec
3e083fc docs: Create Feature 006 specification for Archi tool fidelity fixes
```

### Test Results

- **Unit Tests**: 15 passing (100%)
- **Integration Tests**: 22 passing (100%)
- **Total Tests**: 684 passing (Feature 006 + all existing tests)
- **Code Coverage**: 93% overall, 100% on new parsing module
- **Type Checking**: 0 errors (pyright + mypy)
- **Linting**: All checks passed (ruff)

---

## References

- **Specification**: `specs/006-archi-tool-compliance/spec.md`
- **Plan**: `specs/006-archi-tool-compliance/plan.md`
- **Research**: `specs/006-archi-tool-compliance/research.md`
- **Contracts**: `specs/006-archi-tool-compliance/contracts/`
- **Testing Guide**: `specs/006-archi-tool-compliance/quickstart.md`
- **Related**: Feature 004 (`specs/004-archimate-spec-compliance/`)

---

**Next Step**: Create pull request to `develop` branch for code review and integration
