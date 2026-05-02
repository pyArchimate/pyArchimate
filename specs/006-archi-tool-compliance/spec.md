# Feature 006: Archi Tool Fidelity & Bug Fixes

**Status**: Planning  
**Date**: 2026-05-02  
**Related**: Feature 004 (ArchiMate v3.x Specification Compliance), ArchiToolGap.md

## Feature Summary

Close two critical bugs in the Archi (.archimate) reader/writer that cause metadata loss during round-trip import/export: incorrect boolean parsing for label visibility and incorrect text extraction for view documentation. These bugs prevent faithful round-trip fidelity with Archi tool files.

## Problem Statement

The Archi adapter's round-trip fidelity is compromised by two P0 bugs discovered in Feature 004's gap analysis:

1. **Label Visibility Bug**: `bool("false")` evaluates to `True` in Python, causing diagram element labels marked as hidden in Archi to re-appear as visible after import. This breaks visual design intent from source models.

2. **View Documentation Bug**: View-level documentation is parsed but assigned to the wrong variable (`e.text` instead of `doc.text`), causing relationship and view documentation to be lost during import.

These bugs affect the integrity of round-trip workflows and prevent the adapter from being a faithful mirror of Archi's internal model.

## User Stories

### US-001: Fix Label Visibility Parsing
**As a** model architect  
**I want** diagram element labels to preserve their visibility state (hidden/shown) through export/import cycles  
**So that** my visual design intent is preserved when round-tripping models through Archi  

**Acceptance Criteria**:
- Elements marked with `nameVisible="false"` in Archi files import with `show_label=False`
- Elements marked with `nameVisible="true"` or absent (default) import with `show_label=True`
- Export produces correct boolean strings ("false", "true") in Archi XML
- Round-trip: Archi → pyArchimate → Archi preserves label visibility exactly

### US-002: Fix View Documentation Extraction
**As a** documentation maintainer  
**I want** view-level documentation text to be preserved during import  
**So that** I can maintain model documentation across tool boundaries  

**Acceptance Criteria**:
- View `<documentation>` elements are correctly parsed and assigned to `view.desc`
- Relationship `<documentation>` elements continue to work (already fixed in Feature 004)
- Element `<documentation>` elements continue to work (already fixed in Feature 004)
- Empty documentation is handled gracefully (no error, empty string)
- Round-trip: Archi → pyArchimate → Archi preserves documentation text exactly

## Technical Scope

### Files Affected
- **src/pyArchimate/readers/_archireader_helpers.py**
  - Line 115-116: Fix boolean parsing for `nameVisible` feature
  - Line 237: Fix documentation text extraction for views

- **src/pyArchimate/writers/archiWriter.py** (if applicable)
  - Verify label visibility export logic

### Test Coverage Required
- Unit tests: Boolean parsing edge cases (e.g., "false", "true", None, empty string)
- Unit tests: Documentation extraction for elements, relationships, views
- Integration tests: Round-trip fidelity for label visibility (Archi → import → export → Archi)
- Integration tests: Round-trip fidelity for view documentation
- BDD scenarios: End-to-end workflows with real Archi files

## Success Criteria

- [ ] All label visibility round-trip tests pass
- [ ] All view documentation round-trip tests pass
- [ ] No regression in existing Feature 004 tests
- [ ] Code coverage remains ≥ 90%
- [ ] Branch ready for merge to develop

## Dependencies

- Python 3.10+ (existing)
- lxml (existing)
- pytest, behave (existing)
- Feature 004 completion (influence strength and relationship documentation fixes already merged)

## Out of Scope

- Version preservation (Feature 004's "others")
- Folder taxonomy normalization (Feature 004's "others")
- Additional diagram node kinds (Feature 004's "others")
- View point support (Feature 004 Phase 2)

## Metrics

- Fidelity Score: All critical metadata (labels, documentation) preserved in round-trip
- Test Coverage: ≥ 90% of affected code paths
- Performance: No new O(n) operations introduced
