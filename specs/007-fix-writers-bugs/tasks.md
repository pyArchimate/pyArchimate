# Feature 007 Tasks: Fix Writer Bugs - OpenGroup Exchange Format Compliance

## Overview
- **Feature**: Fix Writer Bugs - OpenGroup Exchange Format
- **Total Tasks**: 14
- **Phases**: 5 (Setup, Foundational, US1, US2, US3)
- **MVP Scope**: US1 (already complete) ✅

---

## Phase 1: Setup & Project Structure

- [ ] T001 Verify Feature 007 directory structure with plan.md, spec.md, and implementation docs
- [ ] T002 Create .specify/feature.json context for Feature 007
- [ ] T003 Configure git tracking for feature branch 007-fix-ouput-file-format-issues

---

## Phase 2: Foundational Prerequisites

- [ ] T004 Review archimateWriter.py and archimateReader.py architecture
- [ ] T005 Identify all reader/writer implementations in src/pyArchimate/writers/ and src/pyArchimate/readers/
- [ ] T006 [P] Document current file format detection logic (if any) in Model.read() and Model.write()
- [ ] T007 [P] Extract file extension handling requirements from spec.md US2

---

## Phase 3: User Story 1 - Fix OpenGroup Exchange Writer Schema Validation [P1]

**Story Goal**: Generate valid OpenGroup Exchange format files that parse without schema errors  
**Status**: ✅ COMPLETE

- [ ] T008 [US1] [P] Verify schema location fix in archimateWriter.py line 381 (archimate3.xsd)
- [ ] T009 [US1] [P] Confirm namespace URI matches schema version (3.0/3.0)
- [ ] T010 [US1] Validate generated temp/demo.xml parses without cvc-elt.1.a errors
- [ ] T011 [US1] Compare temp/demo.xml structure against specs/007-fix-writers-bugs/demo-good.xml reference
- [ ] T012 [US1] Run pytest unit tests to ensure no regressions (696 tests pass)
- [ ] T013 [US1] Verify ruff linting passes (11 linting fixes applied)

---

## Phase 4: User Story 2 - Implement Smart File Format Selection [P2]

**Story Goal**: Auto-select appropriate reader/writer based on file extension

**Independent Test Criteria**:
- Write model with `.archimate` → uses Archi native format
- Write model with `.xml` → uses OpenGroup Exchange format
- Read `.archimate` file → parses correctly
- Read `.xml` file → parses correctly
- Round-trip with both formats preserves data

### Implementation Tasks

- [ ] T014 [US2] [P] Create file extension detection utility in src/pyArchimate/writers/__init__.py
- [ ] T015 [US2] [P] Create file extension detection utility in src/pyArchimate/readers/__init__.py
- [ ] T016 [US2] Refactor Model.write() method to select writer based on extension (src/pyArchimate/model.py)
- [ ] T017 [US2] Refactor Model.read() method to select reader based on extension (src/pyArchimate/model.py)
- [ ] T018 [US2] Update Writers enum to include both archi and archimate formats (src/pyArchimate/enums.py)
- [ ] T019 [US2] Add integration tests for `.archimate` write/read cycle (tests/integration/test_format_selection.py)
- [ ] T020 [US2] Add integration tests for `.xml` write/read cycle (tests/integration/test_format_selection.py)
- [ ] T021 [US2] Update documentation in Model class docstring with format selection examples (src/pyArchimate/model.py)

---

## Phase 5: User Story 3 - Remove ARIS Format Support [P3]

**Story Goal**: Clean up deprecated ARIS format code

**Independent Test Criteria**:
- No ARIS imports in main API
- All tests pass without ARIS dependencies
- Code compiles and runs without ARIS references

### Implementation Tasks

- [ ] T022 [US3] [P] Identify all ARIS format references in codebase (grep -r "aris" src/)
- [ ] T023 [US3] [P] Mark arisAMLreader.py as deprecated with migration notice (src/pyArchimate/readers/arisAMLreader.py)
- [ ] T024 [US3] Remove ARIS format from Writers enum or mark as deprecated (src/pyArchimate/enums.py)
- [ ] T025 [US3] Remove ARIS format imports from main package __init__.py (src/pyArchimate/__init__.py)
- [ ] T026 [US3] Remove ARIS-related test files or mark as legacy (tests/unit/readers/test_arisAMLreader.py)
- [ ] T027 [US3] Update API documentation to remove ARIS format mentions (docs/api.md or equivalent)
- [ ] T028 [US3] Add deprecation notice to changelog for ARIS format removal (CHANGELOG.md)

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T029 [P] Run full pre-commit checks (ruff, pyright, mypy, pytest)
- [ ] T030 [P] Update specs/007-fix-writers-bugs/ documentation with final status
- [ ] T031 Ensure Feature 004 integration compatibility (schema-compliant files)
- [ ] T032 Document new file format selection behavior in README.md

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
✅ **US1**: Fix OpenGroup Exchange Writer Schema Validation
- One-line schema location fix
- All validation complete
- Ready for Feature 004

### Phase 2 (Ready After US1)
🔄 **US2**: Implement Smart File Format Selection
- Refactor Model read/write methods
- Adds `.archimate` / `.xml` auto-selection
- Enables parallel work on US3

### Phase 3 (Polish)
⏳ **US3**: Remove ARIS Format Support
- Code cleanup only
- No impact on core functionality
- Can run in parallel with US2

---

## Task Dependencies

```
T001-T003 (Setup)
    ↓
T004-T007 (Foundational)
    ├── T008-T013 (US1) ✅ COMPLETE
    ├── T014-T021 (US2) 🔄 Ready to start
    └── T022-T028 (US3) ⏳ Ready to start (parallel with US2)
        ↓
T029-T032 (Polish)
```

---

## Parallel Execution Examples

### Scenario 1: Sequential (Recommended for this feature)
1. Complete US1 ✅ (already done)
2. Complete US2 (blocks US3 refactoring)
3. Complete US3 while waiting for integration tests

### Scenario 2: Parallel (After US1)
- **Thread 1**: T014-T021 (US2 implementation)
- **Thread 2**: T022-T028 (US3 cleanup) - can start after T005
- Both threads converge at T029 (final checks)

### Scenario 3: MVP Only (Current)
- Deploy US1 ✅ with Feature 004
- Schedule US2 and US3 for next sprint

---

## Testing Strategy

### Unit Tests (Per US)
- **US1**: Schema validation, file parsing (T012)
- **US2**: Extension detection, format selection
- **US3**: Import cleanup, no ARIS references

### Integration Tests (Per US)
- **US1**: Round-trip with OpenGroup format
- **US2**: Round-trip with `.archimate` and `.xml` extensions
- **US3**: Full test suite passes without ARIS

### Pre-Commit Checks (All Phases)
- ✅ ruff linting
- ✅ pyright type checking
- ✅ mypy type checking
- ✅ pytest (696+ tests)

---

## Success Criteria

### Phase 1 & 2: Setup & Foundation
- [ ] Feature 007 structure established
- [ ] Readers/writers inventory complete
- [ ] Git workflow configured

### US1: Schema Fix [P1]
- [x] Schema location corrected (archimate3.xsd)
- [x] Namespace/schema version consistent (3.0/3.0)
- [x] Generated files parse without errors
- [x] All tests pass (696 tests)
- [x] Pre-commit checks pass

### US2: Format Selection [P2]
- [ ] File extension detection works
- [ ] Model.read() auto-selects reader
- [ ] Model.write() auto-selects writer
- [ ] Round-trip tests pass for both formats
- [ ] Backward compatibility maintained

### US3: ARIS Removal [P3]
- [ ] No ARIS imports in main API
- [ ] All ARIS tests removed or marked legacy
- [ ] Tests pass without ARIS dependencies
- [ ] Documentation updated

### Polish & Integration
- [ ] All pre-commit checks pass
- [ ] Feature 004 compatibility verified
- [ ] Documentation complete

---

## Status Tracking

| Story | Status | Start | Target | Owner |
|-------|--------|-------|--------|-------|
| US1 | ✅ Complete | 2026-05-02 | 2026-05-02 | Claude |
| US2 | ⏳ Ready | - | 2026-05-03 | - |
| US3 | ⏳ Ready | - | 2026-05-03 | - |
| Polish | ⏳ Pending | - | 2026-05-04 | - |

---

## Notes

- **US1 is production-ready**: Can merge to develop branch now
- **US2 impacts API**: Requires code review for backward compatibility
- **US3 is cleanup**: Low risk, can be done iteratively
- **Feature 004 depends on US1**: Can proceed with this fix in place
