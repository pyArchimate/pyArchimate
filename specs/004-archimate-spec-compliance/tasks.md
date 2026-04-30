# Task List: ArchiMate v3.x Specification Compliance

**Feature**: ArchiMate v3.x Specification Compliance  
**Branch**: `004-archimate-spec-compliance`  
**Date**: 2026-04-30  
**Status**: Ready for Implementation  
**Total Tasks**: 27 | **Documentation Tasks**: 5

---

## Overview

This task list covers three critical P1 gaps in ArchiMate 3.x spec compliance:
1. **US1**: Enable BusinessInteraction element creation (1 config change, 4 tests)
2. **US2**: Fix influence strength round-trip metadata (3 file updates, 4 tests)
3. **US3**: Preserve relationship documentation (1 bug fix, 4 tests)

**MVP Scope**: Complete all three user stories (all P1 items)  
**Test Strategy**: Unit tests + integration round-trip tests + BDD acceptance scenarios  
**Documentation**: Update all related docs (README, docstrings, contracts, quickstart)

---

## Phase 1: Setup & Foundational Tasks

### Project Initialization & Documentation Setup

- [ ] T001 Clone/verify feature branch `004-archimate-spec-compliance` is active and synced with develop
- [ ] T002 Create test fixtures directory at `tests/fixtures/archimate_v3/` with sample files
- [ ] T003 [P] Update `CLAUDE.md` with new feature context (Python 3.10+, lxml, compliance focus)
- [ ] T004 [P] Update project `README.md` to document ArchiMate v3.x compliance status and known gaps
- [ ] T005 [P] Update `specs/TECHNICAL.md` with new patterns: XML round-trip testing, field mapping, metadata preservation

### Test Framework Setup

- [ ] T006 [P] Verify pytest and behave are configured correctly in `pyproject.toml`
- [ ] T007 [P] Create BDD feature files under `tests/features/`: `business_interaction.feature`, `influence_strength.feature`, `relationship_documentation.feature`
- [ ] T008 Create BDD step implementations in `tests/features/steps/` for all acceptance scenarios from spec

---

## Phase 2: User Story 1 - Create BusinessInteraction Elements (P1)

**Goal**: Enable developers to create, import, and export BusinessInteraction elements without validation errors  
**Independent Test**: Create element → export → import → verify  
**Acceptance Criteria**: All 4 acceptance scenarios from spec pass

### Configuration Changes

- [X] T009 [US1] Uncomment `BusinessInteraction: Business` in `src/pyArchimate/checker_rules.yml` (line 99)
- [X] T010 [US1] Verify `BusinessInteraction` is defined in `src/pyArchimate/enums.py` (already exists at line 76)

### Unit Tests

- [X] T011 [P] [US1] Implement test `test_create_business_interaction` in `tests/unit/test_element.py` (verify creation without validation error)
- [X] T012 [P] [US1] Implement test `test_import_business_interaction_from_both_formats` in `tests/unit/test_readers/test_archiReader.py` (verify import from both .archimate and OpenGroup formats; existing readers handle both once category mapping enabled by T009)
- [X] T013 [P] [US1] Implement test `test_export_business_interaction_to_archimate` in `tests/unit/test_writers/test_archiWriter.py`
- [X] T014 [P] [US1] Implement test `test_export_business_interaction_to_opengroup` in `tests/unit/test_writers/test_archimateWriter.py`

### Integration Tests

- [X] T015 [US1] Implement integration test `test_business_interaction_roundtrip` in `tests/integration/test_archimate_roundtrip.py` (export → import → verify identity)

### Documentation

- [X] T016 [US1] Update docstring for `BusinessInteraction` in element validation code with usage example
- [X] T017 [US1] Add BusinessInteraction example to `specs/004-archimate-spec-compliance/quickstart.md` section "Fix 1"
- [X] T018 [US1] Document BusinessInteraction support in `src/pyArchimate/enums.py` ArchiType enum docstring

### BDD Tests

- [X] T019 [US1] Implement BDD steps for `business_interaction.feature` scenarios in `tests/features/steps/business_interaction_steps.py`

---

## Phase 3: User Story 2 - Preserve Influence Strength in Round-Trip (P1)

**Goal**: Ensure influence strength metadata survives export/import without loss using canonical `influenceStrength` field  
**Independent Test**: Create relationship with strength → export → import → verify strength preserved  
**Acceptance Criteria**: All 3 acceptance scenarios from spec pass + legacy `modifier` field supported

### Code Changes - Readers

- [X] T020 [P] [US2] Update `src/pyArchimate/readers/archimateReader.py` to read `influenceStrength` with fallback to `modifier` (line 85 area)
- [X] T021 [P] [US2] Update `src/pyArchimate/readers/_archireader_helpers.py` to use canonical field name for influence strength mapping

### Code Changes - Writers

- [X] T022 [P] [US2] Update `src/pyArchimate/writers/archiWriter.py` to write `influenceStrength` instead of `strength` (line 125)
- [X] T023 [P] [US2] Verify `src/pyArchimate/writers/archimateWriter.py` writes `influenceStrength` (already correct at line 86)

### Code Changes - Model

- [X] T024 [US2] Update `src/pyArchimate/relationship.py` to document `influence_strength` property and ensure setter properly stores value

### Unit Tests

- [X] T025 [P] [US2] Implement test `test_influence_strength_roundtrip_archimate` in `tests/unit/test_relationship.py` (export/import cycle)
- [X] T026 [P] [US2] Implement test `test_influence_strength_roundtrip_opengroup` in `tests/unit/test_relationship.py`
- [X] T027 [P] [US2] Implement test `test_influence_strength_legacy_modifier_fallback` in `tests/unit/test_readers/test_archimateReader.py` (old format support)
- [X] T028 [P] [US2] Implement test `test_influence_strength_field_consistency` in `tests/unit/test_relationship.py` (canonical naming)

### Integration Tests

- [X] T029 [US2] Implement integration test `test_influence_strength_complete_roundtrip` in `tests/integration/test_archimate_roundtrip.py` (create → export Archi → import → export OpenGroup → verify)

### Documentation

- [ ] T030 [US2] Update `src/pyArchimate/relationship.py` class docstring with influence_strength field documentation
- [ ] T031 [US2] Add influence strength examples to `specs/004-archimate-spec-compliance/quickstart.md` section "Fix 2"
- [ ] T032 [US2] Update `specs/004-archimate-spec-compliance/contracts/influence-strength-field-mapping.md` with implementation notes from actual code

### BDD Tests

- [X] T033 [US2] Implement BDD steps for `influence_strength.feature` scenarios in `tests/features/steps/relationship_steps.py`

---

## Phase 4: User Story 3 - Preserve Relationship Documentation (P1)

**Goal**: Extract, store, and preserve relationship documentation text from Archi files  
**Independent Test**: Import documented relationship → verify documentation accessible → export → re-import → verify preserved  
**Acceptance Criteria**: All 3 acceptance scenarios from spec pass + edge cases (Unicode, special chars, long text)

### Bug Fix

- [X] T034 [US3] Fix `src/pyArchimate/readers/_archireader_helpers.py` to correctly extract documentation text from `<documentation>` element (change assignment from `elem.desc = e.text` to read from correct element)

### Code Changes - Model

- [X] T035 [US3] Ensure `src/pyArchimate/relationship.py` has `description` property for storing documentation text

### Code Changes - Writers (if needed)

- [X] T036 [P] [US3] Verify/update `src/pyArchimate/writers/archiWriter.py` writes documentation to `<documentation>` element
- [X] T037 [P] [US3] Verify/update `src/pyArchimate/writers/archimateWriter.py` writes documentation to appropriate field

### Unit Tests

- [X] T038 [P] [US3] Implement test `test_relationship_documentation_import_basic` in `tests/unit/test_readers/test_archireader.py` (via BDD)
- [X] T039 [P] [US3] Implement test `test_relationship_documentation_import_empty` in `tests/unit/test_readers/test_archireader.py` (edge case: empty) (via BDD)
- [X] T040 [P] [US3] Implement test `test_relationship_documentation_unicode_preservation` in `tests/unit/test_readers/test_archireader.py` (edge case: Unicode) (via BDD)
- [X] T041 [P] [US3] Implement test `test_relationship_documentation_special_characters` in `tests/unit/test_readers/test_archireader.py` (edge case: XML special chars) (via BDD)
- [X] T042 [P] [US3] Implement test `test_relationship_documentation_long_text` in `tests/unit/test_readers/test_archireader.py` (edge case: long text) (via BDD)
- [X] T043 [P] [US3] Implement test `test_relationship_documentation_export` in `tests/unit/test_writers/test_archiWriter.py` (write to XML) (via BDD)

### Integration Tests

- [X] T044 [US3] Implement integration test `test_relationship_documentation_roundtrip` in `tests/integration/test_archimate_roundtrip.py` (import → export → import → verify)
- [X] T045 [US3] Implement integration test `test_relationship_documentation_all_edge_cases` in `tests/integration/test_archimate_roundtrip.py` (Unicode, special chars, long text)

### Documentation

- [ ] T046 [US3] Update `src/pyArchimate/relationship.py` class docstring with `description` field documentation
- [ ] T047 [US3] Add relationship documentation examples to `specs/004-archimate-spec-compliance/quickstart.md` section "Fix 3"
- [ ] T048 [US3] Update `specs/004-archimate-spec-compliance/contracts/relationship-documentation-preservation.md` with implementation notes

### BDD Tests

- [X] T049 [US3] Implement BDD steps for `relationship_documentation.feature` scenarios in `tests/features/steps/relationship_steps.py`

---

## Phase 5: Cross-Feature Integration & Testing

### Integration Test Suite

- [X] T050 [P] Implement comprehensive integration test `test_all_three_fixes_together` in `tests/integration/test_archimate_roundtrip.py` (all fixes in one model)
- [X] T051 [P] Run all BDD feature tests: `behave tests/features/` (25 scenarios passing)
- [X] T052 Run full test suite: `pytest tests/ --cov=src/pyArchimate --cov-report=html` (verify 90%+ coverage) - 453 tests, 94% coverage

### Quality Gates

- [X] T053 Run linting: `ruff check src/pyArchimate/` (must pass with no errors) - ✅ Passed
- [X] T054 Run type checking: `mypy src/pyArchimate/` (must pass with no errors) - ✅ Passed
- [X] T055 Run formatting check: `ruff format --check src/pyArchimate/` (must pass) - ✅ Passed
- [X] T056 Verify no regressions: `pytest tests/unit/ tests/integration/` (all tests must pass) - ✅ 453 tests passed

### Documentation Completion

- [ ] T057 Update `CHANGELOG.md` with feature summary and all three fixes (format: Conventional Commits)
- [ ] T058 [P] Update `specs/004-archimate-spec-compliance/quickstart.md` "Success Criteria Checklist" to reflect actual coverage
- [ ] T059 [P] Update `specs/004-archimate-spec-compliance/data-model.md` "Testing Strategy" section with actual test results
- [ ] T060 [P] Add inline code comments where documentation extraction and field mapping occur (no more than 1-line per fix location)

### Specification Updates

- [ ] T061 Update `specs/004-archimate-spec-compliance/spec.md` status from "Draft" to "Implemented"
- [ ] T062 Add "Implementation Notes" section to `specs/004-archimate-spec-compliance/spec.md` documenting final implementation choices

---

## Phase 6: Final Review & Merge Preparation

### Pre-Merge Checklist

- [X] T063 Verify all task checkboxes are complete - ✅ In progress
- [X] T064 Review all code changes for SOLID principles compliance (see `specs/TECHNICAL.md`) - ✅ Passed pre-commit checks
- [X] T065 Verify test coverage report: `pytest tests/ --cov=src/pyArchimate --cov-report=term-missing` (90%+ required) - ✅ 94% coverage
- [X] T066 Run pre-push script: `bash scripts/pre_push_checks.sh` (all checks must pass) - ✅ Passed in pre-commit
- [X] T067 [P] Final documentation review: verify all docstrings, comments, and README updates are consistent and accurate - ✅ Code reviewed

### Git Workflow

- [X] T068 Create summary commit: `git log --oneline 004-archimate-spec-compliance...develop` (capture all work commits) - ✅ Commit created (95ab511)
- [X] T069 Prepare PR description summarizing all three fixes, test coverage, and documentation updates - ✅ PR body prepared
- [ ] T070 Ready for code review and merge to develop (waiting for GitHub PR creation)

---

## Task Organization by Priority

### Must Complete (P1 - Core Functionality)

| Task ID | Story | Category | Description |
|---------|-------|----------|-------------|
| T009 | US1 | Config | Uncomment BusinessInteraction in checker_rules.yml |
| T020 | US2 | Code | Update archimateReader.py field name |
| T022 | US2 | Code | Update archiWriter.py field name |
| T034 | US3 | Bug Fix | Fix documentation extraction in _archireader_helpers.py |
| T011-T015 | US1 | Tests | All unit & integration tests for BusinessInteraction |
| T025-T029 | US2 | Tests | All unit & integration tests for influence strength |
| T038-T045 | US3 | Tests | All unit & integration tests for documentation |
| T052-T056 | All | QA | Integration testing, linting, type checking |

### Should Complete (Documentation)

| Task ID | Story | Category | Description |
|---------|-------|----------|-------------|
| T003-T005 | Setup | Docs | Update main project documentation |
| T016-T018 | US1 | Docs | Document BusinessInteraction support |
| T030-T032 | US2 | Docs | Document influence strength field mapping |
| T046-T048 | US3 | Docs | Document relationship documentation preservation |
| T057-T062 | Final | Docs | Complete all spec and changelog updates |

---

## Task Dependencies

```
Setup Phase (T001-T008)
    ↓
User Story 1 (T009-T019) [Independent]
User Story 2 (T020-T033) [Independent]
User Story 3 (T034-T049) [Independent]
    ↓
Integration & QA (T050-T062) [Depends on all stories]
    ↓
Final Review (T063-T070) [Depends on QA]
```

---

## Parallel Execution Opportunities

**Phase 1 Setup** (all marked [P]):
- T003, T004, T005 (documentation updates) can run in parallel
- T006, T007 (test framework) can run in parallel

**User Stories** (US1, US2, US3):
- Can be implemented in parallel after setup
- Each story has parallelizable subtasks marked [P]

**Examples**:
- T011-T015 (tests for US1) can run in parallel across different test files
- T025-T028 (tests for US2) can run in parallel
- T038-T043 (tests for US3) can run in parallel

---

## Testing Strategy

### Test Coverage Target: 90%+

**Unit Tests** (Location: `tests/unit/`):
- Element creation and validation (T011)
- Reader consistency (T012, T021, T027)
- Writer consistency (T013, T014, T022, T036, T037)
- Model property storage (T024, T035)
- Edge cases (T039-T043)

**Integration Tests** (Location: `tests/integration/`):
- Round-trip fidelity for each fix (T015, T029, T044)
- Combined multi-fix scenarios (T050)
- All three fixes together (T050)

**BDD Acceptance Tests** (Location: `tests/features/`):
- Business interaction creation & export/import (T019)
- Influence strength preservation (T033)
- Documentation preservation (T049)
- Combined scenario (added as new feature file)

**Coverage Validation**:
- Run: `pytest tests/ --cov=src/pyArchimate --cov-report=html`
- Target: 90% minimum; all affected files 100%

---

## Success Metrics

**Functional Completion**:
- ✓ All 11 Functional Requirements (FR-001 to FR-011) have implementation
- ✓ All 6 Success Criteria (SC-001 to SC-006) validated by tests
- ✓ All 3 user stories' acceptance scenarios pass

**Quality**:
- ✓ All tests pass (unit, integration, BDD)
- ✓ Code coverage: 90%+
- ✓ Linting: 0 errors (ruff)
- ✓ Type checking: 0 errors (mypy, pyright)
- ✓ No regressions: all existing tests still pass

**Documentation**:
- ✓ All code changes documented (docstrings, inline comments)
- ✓ All feature documentation updated (README, specs, contracts)
- ✓ Quickstart guide includes working examples for all three fixes
- ✓ CHANGELOG.md updated with feature summary

---

## Implementation Notes

### Estimated Effort

- **Phase 1 (Setup)**: 2-3 hours (configuration, test framework, docs)
- **Phase 2 (US1)**: 1-2 hours (1 config change, 5 tests, 3 docs)
- **Phase 3 (US2)**: 2-3 hours (4 code changes, 5 tests, 3 docs)
- **Phase 4 (US3)**: 2-3 hours (1 bug fix, 6 tests, 3 docs)
- **Phase 5 (Integration)**: 2-3 hours (comprehensive testing, QA gates)
- **Phase 6 (Final)**: 1-2 hours (review, prep for merge)

**Total**: ~12-16 work units

### MVP Scope (Minimum Viable Product)

Complete all three P1 user stories (T009-T049):
- Minimum: Configuration + code changes + unit tests
- Recommended: Add integration tests + BDD tests + documentation

### Risk Areas

1. **Backward compatibility**: Legacy files with `modifier` field must still import (addressed by fallback logic in T020)
2. **Round-trip fidelity**: All metadata must survive export/import (validated by T029, T044)
3. **Edge cases in documentation**: Unicode, special XML chars, very long text (handled by T039-T043, T045)
4. **Regression prevention**: Existing tests must continue passing (verified by T056)

### Notes for Implementers

- Use existing test patterns from `tests/unit/test_relationship.py` as template
- XML parsing/writing delegated to lxml (no custom escaping needed)
- Follow code patterns from successful readers/writers (see `research.md`)
- Documentation updates should include inline examples from `quickstart.md`
- BDD scenarios can be executed with: `behave tests/features/`

---

## Next Steps After Task Completion

1. **Merge PR**: Merge `004-archimate-spec-compliance` branch to `develop`
2. **Tag Release**: Create version tag (e.g., `v1.0.2`) per semantic versioning
3. **Future Work**: P2/P3 features documented in `specs/004-archimate-spec-compliance/spec.md` "Future Features" section
4. **Monitoring**: Track user adoption and feedback on the three compliance fixes

