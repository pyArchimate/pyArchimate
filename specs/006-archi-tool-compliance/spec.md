# Feature 006: Archi Tool Fidelity & Bug Fixes

**Status**: Planning  
**Date**: 2026-05-02  
**Related**: Feature 004 (ArchiMate v3.x Specification Compliance), ArchiToolGap.md

## Feature Summary

Close two critical bugs in the Archi (.archimate) reader/writer that cause metadata loss during round-trip import/export: incorrect boolean parsing for label visibility and incorrect text extraction for view documentation. Additionally, validate that embedded images survive round-trip import/export cycles with byte-for-byte fidelity. These bugs and gaps prevent faithful round-trip fidelity with Archi tool files.

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

### US-003: Validate Image Preservation in Round-Trip
**As a** model architect with visual diagrams  
**I want** embedded images in Archi files to survive import/export cycles with exact fidelity  
**So that** my visual assets and diagram graphics are not corrupted or lost  

**Acceptance Criteria**:
- Archi files with embedded images (base64-encoded in XML) can be imported without error
- All embedded images are preserved byte-for-byte through round-trip (Archi → import → export → Archi)
- Image base64 data is identical before and after round-trip
- Multiple images in a single file are all preserved
- Round-trip: Archi file with images → pyArchimate → Archi file produces identical image data

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
- Unit tests: Image data extraction and base64 comparison utilities
- Integration tests: Round-trip fidelity for label visibility (Archi → import → export → Archi)
- Integration tests: Round-trip fidelity for view documentation
- Integration tests: Round-trip fidelity for embedded images (byte-for-byte comparison)
- Test fixtures: Minimal Archi files with embedded images (1-2 small test images)
- BDD scenarios: End-to-end workflows with real Archi files (including images)

## Success Criteria

- [ ] All label visibility round-trip tests pass
- [ ] All view documentation round-trip tests pass
- [ ] All image preservation round-trip tests pass (byte-for-byte comparison)
- [ ] No regression in existing Feature 004 tests
- [ ] Code coverage remains ≥ 90%
- [ ] Test fixtures with embedded images created and committed
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
- Image format conversion or re-encoding (byte-for-byte comparison only, no transcoding)
- Image content validation beyond base64 data comparison
- Image extraction or separate image file export

## Metrics

- Fidelity Score: All critical metadata (labels, documentation, images) preserved in round-trip
- Image Preservation: 100% byte-for-byte match of base64-encoded image data after round-trip
- Test Coverage: ≥ 90% of affected code paths
- Performance: No new O(n) operations introduced

## Clarifications

### Session 2026-05-02 (Initial)

- Q: How should empty documentation (`<documentation></documentation>`) be handled? → A: `elem.desc = None` (safe default, matches Feature 004 pattern for elements/relationships)
- Q: What about whitespace-only documentation text? → A: Preserve as-is (lxml .text extracts literal content; strip only if explicitly needed in future)
- Q: Should `parse_bool()` handle whitespace in string values (e.g., " true ")? → A: Yes, normalize with `.lower().strip()` for robustness
- Q: Are there any other boolean fields besides `nameVisible` in diagram objects? → A: Deferred to implementation phase (scan during T2-T3); current focus on `nameVisible` only

### Session 2026-05-02 (Image Handling Scope)

- Q: Should Feature 006's round-trip tests include Archi files with embedded images? → A: **Yes, with full validation** (Option A) - Include embedded images in test files and validate byte-for-byte preservation
- Q: Should image validation be part of Feature 006 or a separate feature? → A: **Expand Feature 006** (Option A) - Add image validation tasks; increases effort from ~90 min to ~170 min
- Q: How should image preservation be validated? → A: **Byte-for-byte base64 comparison** (Option B) - Compare base64-encoded image data strings; simple, deterministic, catches any corruption
- Q: Should we use existing test files or create new ones? → A: **Create minimal test files** (Option A) - Generate small Archi files with embedded test images (e.g., 1x1 PNG) for reproducible testing
