# Implementation Plan: ArchiMate v3.x Specification Compliance

**Branch**: `develop` (to be created via git hook) | **Date**: 2026-04-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-archimate-spec-compliance/spec.md`

## Summary

Close three critical ArchiMate 3.x specification gaps in pyArchimate: enable `BusinessInteraction` element creation, resolve influence strength round-trip metadata mismatch, and preserve relationship documentation during Archi import/export. The approach is surgical: uncomment category mapping, align field names across readers/writers, and fix the documentation assignment bug. All changes are backward-compatible; existing tests continue to pass.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: lxml (XML parsing), oyaml (YAML), pillow (image handling)  
**Storage**: File I/O only (.archimate and OpenGroup exchange formats)  
**Testing**: pytest, behave (BDD), pytest-cov (coverage 90%+ target)  
**Target Platform**: Cross-platform (Linux, macOS, Windows)  
**Project Type**: Library (Python package for ArchiMate model creation and exchange)  
**Performance Goals**: No new performance targets (library, not runtime-sensitive)  
**Constraints**: Backward compatible; no breaking changes to public API  
**Scale/Scope**: Lightweight fixes affecting 6 primary files; 11 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Code Quality (I)**: Changes are surgical and localized; no magic numbers or unclear logic. All changes preserve modularity and readability.

✅ **Testing Standards (II)**: Feature requires unit and integration tests for each gap. BDD scenarios from spec will be converted to Gherkin steps.

✅ **User Experience Consistency (III)**: Library API remains unchanged; behavior becomes more predictable (fixes loss of metadata).

✅ **Performance Requirements (IV)**: No new performance-critical code; changes are O(1) configuration and field name alignment.

✅ **Security Practices (V)**: XML parsing and field mapping are existing mechanisms; no new input validation required beyond current XML schema validation.

✅ **State Management (VI)**: Metadata preservation is core to this feature; no new state transitions introduced (relationships remain in same lifecycle).

✅ **System Integrity & Accuracy (VII)**: This feature directly improves accuracy by preserving metadata losslessly and enabling conformant element creation.

✅ **Durability & Interoperability (VIII)**: Feature ensures round-trip fidelity with external tools (Archi, OpenGroup exchange). Field name alignment improves durability.

✅ **Cross-Platform Consistency (IX)**: File format handling is platform-agnostic (lxml is cross-platform); fixes apply equally across all supported platforms.

**Gate Status**: ✅ PASS - Feature aligns with all constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/003-archimate-spec-compliance/
├── plan.md                     # This file
├── spec.md                     # Feature specification (completed)
├── research.md                 # Phase 0: Dependency and field name research
├── data-model.md               # Phase 1: Data model and entity contracts
├── quickstart.md               # Phase 1: Quick reference for testing the fixes
├── contracts/                  # Phase 1: Format contracts (XML schema mappings)
└── checklists/requirements.md  # Quality checklist
```

### Source Code (affected modules)

```text
src/pyArchimate/
├── enums.py                              # Update: uncomment BusinessInteraction in ArchiType
├── checker_rules.yml                     # Update: uncomment BusinessInteraction category mapping
├── element.py                            # No changes (validation will pass once checker_rules.yml is updated)
├── relationship.py                       # Update: document influence strength field name
├── readers/
│   ├── archimateReader.py                # Update: read influenceStrength consistently
│   └── _archireader_helpers.py           # Fix: correct documentation text extraction
└── writers/
    ├── archimateWriter.py                # Update: write influenceStrength field
    └── archiWriter.py                    # Update: write influenceStrength field

tests/
├── unit/
│   ├── test_element.py                   # Add: BusinessInteraction creation tests
│   ├── test_relationship.py              # Add/update: influence strength round-trip tests
│   ├── test_readers/                     # Add: documentation preservation tests
│   └── test_writers/                     # Add: influence strength export tests
└── integration/
    └── test_archimate_roundtrip.py       # Add: end-to-end round-trip fidelity tests
```

**Structure Decision**: Single-project library structure. Fixes are surgical and focused on specific reader/writer/enum modules. Test additions follow existing test organization (unit + integration).

## Research Artifacts (Phase 0)

To be generated in `research.md`:

1. **ArchiMate 3.x specification reference**: Field names for influence strength in both .archimate and OpenGroup exchange formats
2. **Existing code patterns**: How other elements are validated and registered (reference for BusinessInteraction)
3. **Reader/writer inconsistencies**: Document current field name usage across all readers and writers
4. **Test frameworks**: Confirm BDD (behave) setup and GWT (Given-When-Then) syntax for acceptance tests

## Data Model & Entities (Phase 1)

To be generated in `data-model.md`:

**BusinessInteraction** (Element subtype)
- Field: `elem_type` = `ArchiType.BusinessInteraction`
- Inheritance: Inherits from Element (no new fields)
- Validation: Must pass `ARCHI_CATEGORY` check (once enabled in checker_rules.yml)
- Lifecycle: Same as other elements (create → relate → export)

**InfluenceRelationship** (Relationship metadata)
- Field: `influenceStrength` (canonical field name)
- Storage: Existing Relationship.properties dict
- Serialization: `.archimate` and OpenGroup formats
- Validation: Valid values per ArchiMate spec (e.g., "high", "medium", "low" or numeric scale—research to confirm)

**DocumentedRelationship** (Relationship metadata)
- Field: `description` (or `doc` - research current usage)
- Source: Archi `.archimate` files contain `<documentation>` XML element
- Round-trip: Must preserve exactly; no truncation or loss
- Edge case: Empty, long, or special-character documentation

## Contracts (Phase 1)

To be generated in `contracts/`:

**contract-influence-strength.md**: Field name mapping for influence strength across formats
- OpenGroup exchange: `influenceStrength` element or attribute
- Archi .archimate: `modifier` or other field (to be researched)
- Mapping logic: Define transparent conversion during import

**contract-business-interaction.md**: Element type registration
- ArchiType enum: `BusinessInteraction` (already present)
- ARCHI_CATEGORY mapping: Category and constraints (to be uncommented)
- XML schema: How BusinessInteraction appears in exported files

**contract-relationship-documentation.md**: Documentation field mapping
- Archi .archimate XML: `<documentation>` element text content
- Python object: Relationship.description or similar field
- Round-trip: Preservation without modification

## Quickstart (Phase 1)

To be generated in `quickstart.md`:

- How to create a BusinessInteraction element
- How to verify influence strength survives export/import cycle
- How to test relationship documentation preservation
- Test command examples for developers

## Next Steps

1. **Phase 0**: Run research agents to confirm ArchiMate 3.x field names and current code patterns
2. **Phase 1**: Generate data-model.md, contracts/, quickstart.md, and update agent context
3. **Phase 2** (via `/speckit.tasks`): Generate detailed task list with acceptance criteria

---

## Artifacts Generated

✅ **plan.md** - Implementation plan (this file)  
⏳ **research.md** - To be generated (Phase 0)  
⏳ **data-model.md** - To be generated (Phase 1)  
⏳ **quickstart.md** - To be generated (Phase 1)  
⏳ **contracts/** - To be generated (Phase 1)  
⏳ **tasks.md** - To be generated (Phase 2 via `/speckit.tasks`)
