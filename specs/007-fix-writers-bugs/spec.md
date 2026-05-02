# Feature 007: Fix Writer Bugs - OpenGroup Exchange Format Compliance

## Feature Overview
Fix critical bugs in the archimateWriter preventing valid OpenGroup Exchange format file generation. Ensure all export formats work correctly with standard ArchiMate tools and XML validators.

## User Stories

### US1: Fix OpenGroup Exchange Writer Schema Validation [P1]
**Goal**: Generate valid OpenGroup Exchange format files that parse without schema errors

**Acceptance Criteria**:
- Generated files point to correct schema (archimate3.xsd, not archimate3_Diagram.xsd)
- Schema namespace URI matches schema location version
- Files parse without cvc-elt.1.a validation errors
- Generated structure matches OpenGroup Exchange reference format
- Root element is `<model>` with `identifier` attribute
- Model name stored as `<name>` child element

**Test Scenarios**:
- Generate simple model with elements, relationships
- Parse generated XML with standard parser (no exceptions)
- Validate schema location points to model schema file
- Compare structure against demo-good.xml reference

---

### US2: Implement Smart File Format Selection [P2]
**Goal**: Auto-select appropriate reader/writer based on file extension

**Acceptance Criteria**:
- `.archimate` files use archiReader/archiWriter (Archi native format)
- `.xml` files use archimateReader/archimateWriter (OpenGroup Exchange format)
- Default to OpenGroup Exchange if extension not recognized
- Selection works for both read() and write() operations
- Maintain backward compatibility with existing code

**Test Scenarios**:
- Write model with `.archimate` extension → uses Archi writer
- Write model with `.xml` extension → uses OpenGroup writer
- Write model with no extension → defaults to OpenGroup
- Read `.archimate` file → uses Archi reader
- Read `.xml` file → uses OpenGroup reader
- Round-trip: write as .xml, read as .xml → data preserved

---

### US3: Remove ARIS Format Support [P3]
**Goal**: Clean up deprecated ARIS format code and references

**Acceptance Criteria**:
- ARIS-specific readers removed or deprecated
- ARIS-specific writers removed or deprecated
- ARIS format tests removed (or marked as legacy)
- Documentation updated to remove ARIS references
- No ARIS imports in main API
- Codebase focuses on Archi and OpenGroup formats only

**Test Scenarios**:
- Verify no arisAMLreader imports in main code
- Confirm ARIS format not available in Writers enum
- Check all integration tests pass (no ARIS dependencies)
- Validate documentation removes ARIS format mentions

---

## Dependencies & Priorities

**MVP Scope** (Minimum Viable Product):
- US1: Fix OpenGroup Exchange Writer Schema Validation (P1) ✅ **COMPLETE**

**Phase 2** (Ready for Feature 004):
- US2: Implement Smart File Format Selection (P2)

**Phase 3** (Polish):
- US3: Remove ARIS Format Support (P3)

## Notes

- US1 is already implemented and tested
- US2 requires refactoring Model.read() and Model.write() methods
- US3 is code cleanup, can run in parallel with US2
