# Implementation Plan: Archi Tool Fidelity & Bug Fixes

**Branch**: `006-archi-tool-compliance` | **Date**: 2026-05-02 | **Spec**: [spec.md](spec.md)

## Summary

Fix two critical bugs in the Archi reader that compromise round-trip fidelity: incorrect boolean parsing for label visibility and incorrect text extraction for view documentation. Surgical changes to 3 files; 15 lines of code modified/added. Fully backward compatible.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: lxml (XML parsing), oyaml (YAML configuration)  
**Storage**: File I/O only (.archimate XML format)  
**Testing**: pytest (unit/integration), behave (BDD acceptance tests)  
**Target Platform**: Cross-platform (Linux, macOS, Windows)  
**Project Type**: Library (Python package for ArchiMate model creation and exchange)  
**Constraints**: Backward compatible; no breaking changes to public API

## Constitution Check

*GATE: Must pass before Phase 0 research.*

✅ **Code Quality (I)**: Changes are surgical (3 files, <20 lines); no magic numbers or unclear logic.

✅ **Testing Standards (II)**: Feature requires unit tests for boolean parsing and integration tests for round-trip fidelity.

✅ **User Experience Consistency (III)**: Library API unchanged; behavior becomes more predictable (preserves metadata losslessly).

✅ **Performance Requirements (IV)**: No new performance-critical code; boolean parsing is O(1) string comparison.

✅ **Security Practices (V)**: No new input validation required; changes are in existing XML parsing mechanisms.

✅ **State Management (VI)**: No new state transitions; fixes apply to existing `show_label` and `desc` fields.

✅ **System Integrity & Accuracy (VII)**: This feature directly improves accuracy by fixing bugs that cause metadata loss.

✅ **Durability & Interoperability (VIII)**: Fixes align with W3C XML boolean standards and Archi's documented format.

✅ **Cross-Platform Consistency (IX)**: String parsing and XML handling are platform-agnostic; fixes apply equally across all supported platforms.

**Gate Status**: ✅ PASS — Feature aligns with all constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/006-archi-tool-compliance/
├── plan.md                       # This file (implementation plan)
├── spec.md                       # Feature specification
├── research.md                   # Phase 0: Research findings
├── data-model.md                 # Phase 1: Data model & entities
├── quickstart.md                 # Testing guide
└── contracts/                    # Phase 1: Interface contracts
    ├── boolean-handling.md       # Boolean parsing contract
    └── documentation-extraction.md  # Documentation extraction contract
```

### Source Code (affected modules)

```text
src/pyArchimate/
├── helpers.py                    # New: parse_bool() function
├── readers/
│   └── _archireader_helpers.py   # Fix: Lines 115-116 (boolean), 237 (documentation)
└── writers/
    └── archiWriter.py            # Verify: Lines 149-151 (boolean output)

tests/
├── unit/
│   └── test_helpers.py           # Add: test_parse_bool() cases
├── integration/
│   └── test_archimate_roundtrip.py  # Add: round-trip fidelity tests
└── features/
    ├── archi_label_visibility.feature    # BDD scenarios
    └── archi_view_documentation.feature  # BDD scenarios
```

**Structure Decision**: Surgical fixes to existing modules; no new files except `parse_bool()` helper (added to existing or new `helpers.py`).

## Phases

### Phase 0: Research ✅ COMPLETE

**Output**: `research.md` with all clarifications resolved

**Findings**:
1. Boolean parsing: Create `parse_bool()` helper per W3C xsd:boolean spec
2. View documentation: Use `doc.text` (same as elements/relationships)
3. Writer output: Normalize boolean strings to lowercase "true"/"false"
4. Test framework: pytest + behave (existing, matches Feature 004)

### Phase 1: Design & Contracts ✅ COMPLETE

**Prerequisites**: Research complete (✅)

**Deliverables**:
- ✅ `data-model.md` — Data model for boolean parsing and documentation extraction
- ✅ `contracts/boolean-handling.md` — W3C boolean spec compliance and implementation
- ✅ `contracts/documentation-extraction.md` — Consistent extraction pattern
- ✅ `quickstart.md` — Testing guide with manual and automated test workflows

**Implementation Tasks** (Phase 2):

| Task | File | Lines | Effort | Status |
|------|------|-------|--------|--------|
| T1 | Create `parse_bool()` helper | `helpers.py` | ~15 | 5 min | Pending |
| T2 | Fix label visibility reader | `_archireader_helpers.py:115-116` | 1 | 2 min | Pending |
| T3 | Fix view documentation reader | `_archireader_helpers.py:237` | 1 | 2 min | Pending |
| T4 | Verify/fix boolean writer output | `archiWriter.py:149-151` | 1-5 | 5 min | Pending |
| T5 | Unit tests: `parse_bool()` | `test_helpers.py` | ~30 | 15 min | Pending |
| T6 | Integration tests: round-trip | `test_archimate_roundtrip.py` | ~40 | 20 min | Pending |
| T7 | BDD scenarios | `archi_*.feature` | ~40 | 20 min | Pending |
| T8 | Regression: Feature 004 tests | All existing tests | 0 | 10 min | Pending |

**Total Effort**: ~90 minutes (including testing)

### Phase 2: Implementation & Testing (Next)

Will execute tasks T1-T8 in order, with test validation after each change.

## Implementation Checklist

### Pre-Implementation
- [ ] Branch created: `006-archi-tool-compliance` ✅
- [ ] Specs folder created: `specs/006-archi-tool-compliance/` ✅
- [ ] All design documents complete ✅
- [ ] Stakeholder review of plan (optional)

### Implementation
- [ ] T1: Create `parse_bool()` in `helpers.py`
- [ ] T2: Update line 115-116 in `_archireader_helpers.py`
- [ ] T3: Update line 237 in `_archireader_helpers.py`
- [ ] T4: Verify boolean output in `archiWriter.py`
- [ ] T5: Write unit tests for `parse_bool()`
- [ ] T6: Write integration tests for round-trip fidelity
- [ ] T7: Write BDD scenarios
- [ ] T8: Run all tests (including Feature 004 regression tests)

### Pre-Merge
- [ ] All tests pass (`pytest` + `behave`)
- [ ] Code coverage ≥ 90% on modified files
- [ ] No breaking changes to public API
- [ ] Manual round-trip testing with real Archi files (optional)
- [ ] Commit message follows project conventions
- [ ] Branch ready for PR to `develop`

### Post-Merge
- [ ] Update `ArchiToolGap.md` to reflect fixes
- [ ] Close/update any related issues (if applicable)
- [ ] Document in release notes (if applicable)

## Success Criteria

- [ ] Boolean parsing works for all edge cases ("true", "false", "1", "0", None, etc.)
- [ ] Label visibility round-trips correctly through import/export cycles
- [ ] View documentation round-trips correctly through import/export cycles
- [ ] All new tests pass
- [ ] All existing tests pass (no regression)
- [ ] Code coverage ≥ 90% on modified files
- [ ] Backward compatible; no API changes

## Dependencies

- **Feature 004**: Must be complete and merged (influences strength and relationship documentation fixes already in place)
- **No external dependencies**: Uses only lxml (already present)

## Constraints

- Backward compatible: No breaking changes
- No new public API: Fixes are internal to readers/writers
- No performance impact: O(1) string operations only

## Related Documentation

- **Feature 004** (ArchiMate v3.x Specification Compliance): `specs/004-archimate-spec-compliance/plan.md`
- **ArchiToolGap.md**: Gap analysis that identified these bugs
- **CLAUDE.md**: Project guidelines, technologies, and active features
- **W3C xsd:boolean**: <https://www.w3.org/TR/xmlschema-2/#boolean>

## Artifacts Generated

✅ **plan.md** — Implementation plan (this file)  
✅ **research.md** — Phase 0 research findings  
✅ **data-model.md** — Phase 1 data model  
✅ **contracts/** — Phase 1 interface contracts  
✅ **quickstart.md** — Phase 1 testing guide

---

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 0: Research | Complete | ✅ Done |
| Phase 1: Design | Complete | ✅ Done |
| Phase 2: Implementation | ~90 min | ⏳ Next |
| Merge to develop | 1 day | Pending |

**Estimated completion**: 2026-05-02 (same day if implementation starts immediately)
