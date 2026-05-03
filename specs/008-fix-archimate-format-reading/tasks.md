# Feature 008 Tasks: Fix .archimate Format File Reading - ZIP Archive Support

## Overview
- **Feature**: Fix .archimate Format File Reading - ZIP Archive Support
- **Total Tasks**: 32
- **Phases**: 6 (Setup, Foundational, US1, US2, US3, Polish)
- **MVP Scope**: US1 (complete) ✅
- **Completion**: 100% ✅ (All tasks complete)

---

## Phase 1: Setup & Project Structure

- [x] T001 Verify Feature 008 directory structure with plan.md, spec.md, and implementation docs
- [x] T002 Create test fixture files (valid .archimate, corrupted, missing model.xml) in tests/fixtures/
- [x] T003 Configure git tracking for feature branch 008-fix-archimate-format-reading

---

## Phase 2: Foundational Prerequisites

- [x] T004 [P] Review Model._load_file_contents() implementation in src/pyArchimate/model.py
- [x] T005 [P] Review zipfile module documentation and usage patterns
- [x] T006 [P] Document ZIP format detection strategy (magic bytes, error handling)
- [x] T007 [P] Identify all file I/O entry points in Model class (read, merge, etc.)

---

## Phase 3: User Story 1 - Detect and Extract ZIP Archives [P1]

**Story Goal**: Handle `.archimate` ZIP format files correctly  
**Status**: ✅ Complete

**Independent Test Criteria**:
- ✅ Detect file is ZIP archive using magic bytes (PK signature)
- ✅ Extract XML content from archive root
- ✅ Handle corrupted ZIP files gracefully
- ✅ Handle ZIP files without model.xml with meaningful errors

### Implementation Tasks

- [x] T008 [P] [US1] Implement _detect_zip_file() method in src/pyArchimate/model.py (read 2 bytes, check for PK)
- [x] T009 [P] [US1] Implement _extract_xml_from_zip() method in src/pyArchimate/model.py (zipfile.ZipFile)
- [x] T010 [US1] Add error handling for corrupted ZIP archives (zipfile.BadZipFile)
- [x] T011 [US1] Add error handling for missing model.xml in archive (KeyError → informative message)
- [x] T012 [US1] Add type hints to new methods (file_path: str, return: bool/str)
- [x] T013 [US1] Add docstrings with examples for both methods

---

## Phase 4: User Story 2 - Unified File Loading [P2]

**Story Goal**: Refactor _load_file_contents to handle both plain XML and ZIP formats  
**Status**: ✅ Complete

**Independent Test Criteria**:
- ✅ _load_file_contents() detects format automatically
- ✅ Routes to ZIP extraction for .archimate files
- ✅ Routes to plain text reading for .xml files
- ✅ Backward compatible (no behavior change for .xml files)
- ✅ Clear separation of concerns (detection vs loading)

### Implementation Tasks

- [x] T014 [P] [US2] Refactor Model._load_file_contents() to use _detect_zip_file() (src/pyArchimate/model.py)
- [x] T015 [P] [US2] Add conditional logic: if ZIP then call _extract_xml_from_zip() else read plain text
- [x] T016 [US2] Verify backward compatibility: existing .xml reading unchanged (src/pyArchimate/model.py)
- [x] T017 [US2] Update docstring for _load_file_contents() with format detection behavior
- [x] T018 [US2] Test edge case: file without extension (should try plain text first)
- [x] T019 [US2] Improve error messages to distinguish ZIP vs plain text errors

---

## Phase 5: User Story 3 - Comprehensive Testing [P3]

**Story Goal**: Ensure round-trip fidelity with ZIP archive support  
**Status**: ✅ Complete

**Independent Test Criteria**:
- ✅ Unit tests for ZIP detection and extraction pass
- ✅ Integration tests verify round-trip (read .archimate → modify → write → read again)
- ✅ All existing tests still pass (no regressions)
- ✅ Error cases handled gracefully

### Unit Tests: ZIP Detection & Extraction

- [x] T020 [P] [US3] Add unit test: valid .archimate file detected as ZIP (tests/unit/test_file_loading.py)
- [x] T021 [P] [US3] Add unit test: plain XML file detected as non-ZIP (tests/unit/test_file_loading.py)
- [x] T022 [P] [US3] Add unit test: extract XML from valid archive (tests/unit/test_file_loading.py)
- [x] T023 [P] [US3] Add unit test: error on corrupted ZIP (tests/unit/test_file_loading.py)
- [x] T024 [P] [US3] Add unit test: error on missing model.xml (tests/unit/test_file_loading.py)
- [x] T025 [P] [US3] Add unit test: handle non-existent file gracefully (tests/unit/test_file_loading.py)

### Integration Tests: Round-trip & Format Selection

- [x] T026 [US3] Add integration test: read valid .archimate file (tests/integration/test_archimate_format_reading.py)
- [x] T027 [US3] Add integration test: round-trip (write + read) .archimate format (tests/integration/test_archimate_format_reading.py)
- [x] T028 [US3] Add integration test: .xml files still work (backward compatibility) (tests/integration/test_archimate_format_reading.py)

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T029 [P] Run full pre-commit checks (ruff, pyright, mypy, pytest) - all must pass
- [x] T030 [P] Verify all 737+ existing tests pass (no regressions)
- [x] T031 Update CHANGELOG.md with bug fix entry (Feature 008)
- [x] T032 Update Model.read() docstring to document ZIP support

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
✅ **US1**: Detect and Extract ZIP Archives (COMPLETE)
- ✅ Add _detect_zip_file() and _extract_xml_from_zip() methods
- ✅ Basic error handling for invalid files
- ✅ Ready for Feature 007 integration

### Phase 2 (Completed)
✅ **US2**: Unified File Loading (COMPLETE)
- ✅ Refactor _load_file_contents() to use new methods
- ✅ Ensure backward compatibility with .xml files

### Phase 3 (Testing & Polish - Completed)
✅ **US3**: Comprehensive Testing (COMPLETE)
- ✅ Unit tests for detection and extraction
- ✅ Integration tests for round-trip fidelity
- ✅ All existing tests pass

---

## Task Dependencies

```
T001-T003 (Setup)
    ↓
T004-T007 (Foundational)
    ├── T008-T013 (US1) → Can run parallel
    ├── T014-T019 (US2) → Depends on US1 complete
    └── T020-T028 (US3) → Depends on US1+US2 complete
        ↓
T029-T032 (Polish)
```

---

## Parallel Execution Examples

### Scenario 1: Sequential (Recommended - Low Risk)
1. Complete T008-T013 (US1 implementation)
2. Write T020-T025 tests while waiting for code review
3. Complete T014-T019 (US2 refactoring)
4. Run T026-T028 integration tests
5. Complete T029-T032 (Polish)

### Scenario 2: Parallel (After Foundational)
- **Thread 1**: T008-T013 (US1 implementation)
- **Thread 1.5**: T020-T025 (US1 unit tests - can write while implementing)
- **Thread 2**: Design T026-T028 integration tests while US1 is in progress
- Both threads converge at T014 (US2 refactoring - needs US1 complete)

### Scenario 3: MVP Only (Current)
- Deploy US1 with Feature 007 first
- Schedule US2 and US3 for next sprint

---

## Testing Strategy

### Unit Tests (Per US)
- **US1**: ZIP detection, extraction, error handling (T020-T025)
- **US2**: Format routing, backward compatibility (integrated into T016-T018)
- **US3**: Round-trip fidelity, integration (T026-T028)

### Integration Tests (Per US)
- **US1**: Extract valid archives, handle errors
- **US2**: Read .archimate and .xml files identically except for format
- **US3**: Full round-trip (read → modify → write → read)

### Pre-Commit Checks (All Phases)
- ✅ ruff linting
- ✅ pyright type checking
- ✅ mypy type checking
- ✅ pytest (737+ tests)

---

## Success Criteria

### Phase 1 & 2: Setup & Foundation
- [x] Feature 008 structure established
- [x] Test fixtures planned
- [x] Git workflow configured

### US1: ZIP Detection & Extraction [P1]
- [x] _detect_zip_file() method implemented and tested
- [x] _extract_xml_from_zip() method implemented and tested
- [x] Error handling for corrupted files
- [x] Error handling for missing model.xml
- [x] All 6 unit tests pass (T020-T025)

### US2: Unified File Loading [P2]
- [x] _load_file_contents() refactored to use detection
- [x] .xml files still work identically
- [x] Error messages distinguish between formats
- [x] Type hints and documentation complete
- [x] T014-T019 implementation tasks complete

### US3: Comprehensive Testing [P3]
- [x] 6 unit tests for ZIP handling pass
- [x] 3 integration tests for round-trip pass
- [x] All 733+ existing tests pass (no regressions)
- [x] T026-T028 integration tests pass

### Polish & Integration
- [x] All pre-commit checks pass
- [x] Feature 007 integration verified
- [x] CHANGELOG updated
- [x] Documentation complete

---

## Status Tracking

| Story | Status | Tasks | Owner |
|-------|--------|-------|-------|
| Setup | ✅ Complete | 3/3 | claude |
| Foundational | ✅ Complete | 4/4 | claude |
| US1 | ✅ Complete | 6/6 | claude |
| US2 | ✅ Complete | 6/6 | claude |
| US3 | ✅ Complete | 9/9 | claude |
| Polish | ✅ Complete | 4/4 | claude |

---

## Notes

- **Critical Bug Fix**: This feature unblocks Feature 007 (.archimate files are currently unreadable)
- **Zero Dependencies**: Uses only Python stdlib (zipfile)
- **Backward Compatible**: No changes to public API, existing .xml files work identically
- **Low Risk**: Localized changes to file I/O layer, extensive error handling
- **Test Coverage**: 18 test scenarios planned across unit and integration tests
- **MVP Scope**: US1 alone unblocks Feature 007; US2+US3 adds robustness and testing

---

## Parallel Opportunities

**High-Confidence Parallel Work**:
1. T008-T013 (US1 implementation) can run parallel with T020-T025 (US1 testing) - different files, tests written first or concurrently
2. T004-T007 (Foundational) can run in full parallel - independent research/review tasks
3. Design T026-T028 (US3 integration tests) while US1 implementation is in progress

**Blocked Work**:
- T014-T019 (US2) blocked until T008-T013 (US1) complete - depends on new methods
- T029-T032 (Polish) blocked until T026-T028 complete - needs all implementation done

---

## Format Validation

✅ **ALL tasks follow strict checklist format**:
- Checkbox: ✅ All start with `- [ ]`
- Task ID: ✅ Sequential T001-T032
- Priority/Story: ✅ [P] and [US1]/[US2]/[US3] correctly placed
- File Paths: ✅ All tasks include exact file paths
- Descriptions: ✅ Clear, actionable descriptions

Example tasks:
- `- [ ] T008 [P] [US1] Implement _detect_zip_file() method in src/pyArchimate/model.py` ✅
- `- [ ] T020 [P] [US3] Add unit test: valid .archimate file detected as ZIP (tests/unit/test_file_loading.py)` ✅
- `- [ ] T029 [P] Run full pre-commit checks (ruff, pyright, mypy, pytest)` ✅

---

## Phase 7: Bug Fix - Image Preservation in .archimate Round-Trip

**Bug**: Images are lost when reading .archimate ZIP files and writing them back

**Status**: ✅ Complete

**Root Cause**: archiWriter creates plain XML files instead of ZIP archives with images

### Implementation Tasks

- [x] T033 [P] Add _images_dict property to Model class in src/pyArchimate/model.py
- [x] T034 [P] Add _image_files list to track image filenames in src/pyArchimate/model.py
- [x] T035 [P] Enhance _extract_xml_from_zip() to capture image files in src/pyArchimate/model.py
- [x] T036 Add method _extract_images_from_zip() to extract images/{filename} entries in src/pyArchimate/model.py
- [x] T037 Store extracted images in Model._images_dict with {filename: bytes} format in src/pyArchimate/model.py
- [x] T038 [P] Modify archiWriter.write() to detect .archimate extension in src/pyArchimate/writers/archiWriter.py
- [x] T039 Create ZIP archive with model.xml at root and images/ folder structure in src/pyArchimate/writers/archiWriter.py

### Testing Tasks

- [x] T040 [P] Test: Read export_demo.archimate and verify images captured in Model._images_dict
- [x] T041 Test: Write temp file with images and verify ZIP structure contains images/ folder
- [x] T042 Integration test: Round-trip with images - read → write → read, verify all images preserved in tests/integration/test_archimate_format_reading.py
- [x] T043 Verify all 733+ existing unit tests still pass (no regressions)

---

## Bug Fix Implementation Strategy

### MVP Scope (Bug Fix)
1. Extract images during read (T035-T037)
2. Create ZIP archives during write (T038-T039)
3. Verify with round-trip test (T042)

### Success Criteria
✅ Images preserved when reading .archimate ZIP
✅ ZIP archives created on write with images included
✅ Round-trip preserves all images: read → write → read
✅ No regressions in existing 733+ tests
✅ Compatible with Archi tool format

### Files to Modify
1. **src/pyArchimate/model.py**
   - Add _images_dict and _image_files properties
   - Enhance _extract_xml_from_zip() to capture images
   - Add _extract_images_from_zip() helper method

2. **src/pyArchimate/writers/archiWriter.py**
   - Detect .archimate extension
   - Create ZIP archive instead of plain XML
   - Write model.xml at root + images/ folder

3. **tests/integration/test_archimate_format_reading.py** (enhance)
   - Add round-trip test with image preservation

### Risk Assessment
- **Low Risk**: Focused changes to file I/O
- **Impact**: Only .archimate format affected
- **Backward Compatible**: No public API changes
- **Dependencies**: zipfile (stdlib) - already imported

---

## Bug Fix Completion Status

| Component | Status | Tasks |
|-----------|--------|-------|
| Setup & Analysis | ✅ Complete | T033-T034 |
| Read Path Enhancement | ✅ Complete | T035-T037 |
| Write Path Enhancement | ✅ Complete | T038-T039 |
| Testing & Validation | ✅ Complete | T040-T043 |
