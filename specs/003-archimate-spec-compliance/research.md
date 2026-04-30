# Research Findings: ArchiMate v3.x Compliance

**Phase**: 0 - Research & Investigation  
**Date**: 2026-04-30  
**Status**: Complete

---

## 1. BusinessInteraction Category Mapping

**Decision**: Uncomment `BusinessInteraction: Business` in `checker_rules.yml` under `archi_category` section.

**Rationale**: 
- BusinessInteraction is already defined in `ArchiType` enum (line 76 of `enums.py`)
- BusinessInteraction is already referenced in relationship rules (9 rule entries in checker_rules.yml)
- It is only commented out in the `archi_category` section (line 99)
- Once uncommented, `Element.__init__` validation will pass for BusinessInteraction elements

**Alternatives considered**: 
- Creating a new category for BusinessInteraction (rejected - it already maps to Business layer per ArchiMate spec)
- Conditional validation (rejected - simpler to enable outright as it's part of spec)

**Implementation note**: Single line uncomment in checker_rules.yml; no enum or code changes needed.

---

## 2. Influence Strength Field Naming & Round-Trip

**Current State** (inconsistency found):
| Component | Field Name | Format |
|-----------|-----------|--------|
| archimateReader.py | `modifier` | Read from OpenGroup exchange |
| archiWriter.py | `strength` | Write to Archi .archimate |
| archimateWriter.py | `influenceStrength` | Write to OpenGroup exchange |
| Relationship object | `influence_strength` | Python property |

**Decision**: Standardize on `influenceStrength` for both .archimate and OpenGroup export; transparently map legacy `modifier` on import.

**Rationale**:
- `influenceStrength` is already used by archimateWriter.py (the OpenGroup writer)
- ArchiMate 3.x spec uses `influenceStrength` terminology
- Transparent mapping of legacy `modifier` during import ensures backward compatibility
- Eliminates round-trip data loss by using consistent field names

**Mapping Logic**:
```
On import:
  - Read `influenceStrength` if present
  - Fallback to read `modifier` if `influenceStrength` not found
  - Store as Relationship.influence_strength property

On export (.archimate):
  - Write Relationship.influence_strength to `influenceStrength` element/attribute

On export (OpenGroup):
  - Write Relationship.influence_strength to `influenceStrength` element/attribute
```

**Alternatives considered**:
- Keep separate field names per format (rejected - violates DRY principle and causes round-trip loss)
- Always require influenceStrength in input (rejected - breaks backward compatibility with legacy files)

**Files affected**:
- `src/pyArchimate/readers/archimateReader.py` - Change `'modifier'` to `'influenceStrength'` with fallback
- `src/pyArchimate/writers/archiWriter.py` - Change `'strength'` to `'influenceStrength'`
- `src/pyArchimate/writers/archimateWriter.py` - Already correct
- `src/pyArchimate/relationship.py` - Document property mapping

---

## 3. Relationship Documentation Preservation

**Current Issue** (from gap analysis):
In `_archireader_helpers.py`, the relationship parser finds the `<documentation>` XML element but assigns the wrong text content.

**Pattern found in codebase**:
- Other elements store documentation in `.description` or `.doc` property
- Relationship class likely has similar property

**Decision**: Correct the assignment to read from the proper `<documentation>` XML element and store in the relationship's description/doc field.

**Implementation note**: Single-line fix in `_archireader_helpers.py` (change `elem.desc = e.text` to `elem.desc = doc.text` where doc is the documentation element).

**Validation**:
- Test round-trip: create relationship with documentation → export to .archimate → import → verify documentation preserved
- Test edge cases: empty, Unicode, special XML characters, very long text

---

## 4. Test Framework & BDD Setup

**Current state**:
- Test framework: pytest
- BDD framework: behave
- Coverage tool: pytest-cov (target: >90%)

**Test structure in use**:
- `tests/unit/` - Unit tests (isolated function tests)
- `tests/integration/` - Integration tests (multi-component interaction)
- BDD scenarios in `.feature` files (Gherkin syntax)

**Approach for this feature**:
- Unit tests for each gap fix (element creation, field mapping, documentation extraction)
- Integration tests for round-trip scenarios (create → export → import → verify)
- BDD acceptance tests from spec user stories

---

## 5. Code Patterns & Validation

**Element validation pattern**:
```python
# Location: src/pyArchimate/element.py Element.__init__
ARCHI_CATEGORY[elem_type]  # Validates elem_type is in allowed categories
```

**Reader pattern**:
```python
# Location: src/pyArchimate/readers/*.py
r.get('field_name')  # Safe dictionary access for optional fields
```

**Writer pattern**:
```python
# Location: src/pyArchimate/writers/*.py
elem.set('field_name', value)  # XML attribute setting
e.property_name  # Relationship property access
```

**Relationship property pattern**:
```python
# Location: src/pyArchimate/relationship.py
relationship.influence_strength  # Snake case property matching ArchiMate camelCase field
relationship.description         # Documentation storage
```

---

## 6. ArchiMate 3.x Specification Field Names

**Influence Strength** (from gap analysis confirmation + OpenGroup writer):
- Field name: `influenceStrength` (camelCase)
- Format: OpenGroup exchange uses `influenceStrength` element
- Archi .archimate legacy: uses `modifier` (must support for backward compatibility)

**BusinessInteraction** (from ArchiType enum):
- Element type: `BusinessInteraction`
- Category: Business Layer
- Relationships: All standard ArchiMate relationships apply

**Relationship Documentation**:
- XML element: `<documentation>` (in Archi format)
- Python storage: `description` or `doc` property on Relationship
- Must preserve text content exactly (no truncation, encoding handling required)

---

## Summary of Changes

| Gap | Fix | Files | Complexity |
|-----|-----|-------|------------|
| BusinessInteraction | Uncomment category mapping | checker_rules.yml | Trivial |
| Influence strength round-trip | Align field names, add fallback | archimateReader.py, archiWriter.py, relationship.py | Low |
| Documentation preservation | Fix assignment in parser | _archireader_helpers.py | Low |
| Testing | Add unit & integration tests | tests/unit/*, tests/integration/* | Medium |

**Total effort estimate**: 3-5 work units (well-scoped, surgical fixes)

---

## Next Steps (Phase 1)

1. Generate `data-model.md` with entity definitions
2. Generate `contracts/` directory with format mappings
3. Generate `quickstart.md` with testing instructions
4. Update agent context via `.specify/scripts/bash/update-agent-context.sh`
5. Proceed to Phase 2 task generation with `/speckit.tasks`
