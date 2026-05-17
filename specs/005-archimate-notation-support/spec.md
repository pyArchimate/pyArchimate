# P3: Complete ArchiMate Notation Support

**Feature ID**: 005-archimate-notation-support  
**Phase**: 3 of 3 (P1+P2 in 004, P3 here)  
**Status**: Phase 1 Design Complete, Ready for Phase 2 Implementation  
**Timeline**: 22-30 dev days (8 phases)

---

## Overview

P3 adds three critical notation features to pyArchimate to achieve 100% ArchiMate v3.x specification compliance:

1. **Element Grouping**: Semantic parent-child containment relationships
2. **Junction Semantics**: AND/OR/XOR type validation and preservation
3. **Element Visual Properties**: Fill color, line color, line width, transparency

All features are designed for 100% round-trip XML fidelity and backward compatibility.

---

## Functional Requirements

### FR1: Element Grouping (Semantic Parent-Child Relationships)

**Requirement**: Enable elements to be organized into hierarchical groups with semantic containment relationships.

**Details**:
- Elements can have 0 or 1 parent element (unique parent constraint)
- Maximum nesting depth: 5 levels
- No circular relationships allowed (acyclic invariant)
- Parent-child relationships preserved on XML round-trip via `parentId` attribute
- Deletion of parent element orphans children (non-destructive)
- Folder metadata independent of grouping (can coexist)

**User Stories**:
- US1: "As an architect, I can organize business processes into sub-processes so that large models are easier to understand"
- US2: "As a modeler, I can view element hierarchy to understand composition relationships"
- US3: "As an importer, I can load Archi-exported models with grouped elements and have relationships preserved"

### FR2: Junction Semantics (AND/OR/XOR Types)

**Requirement**: Preserve and validate junction element types (AND, OR, XOR) with round-trip fidelity.

**Details**:
- Junction elements have optional `junctionType` property (already exists: line 112 of element.py)
- Supported types: 'and', 'or', 'xor' (case-insensitive on import, normalized on storage)
- Type stored as property in XML and Python
- Type validation on set (restrict to valid types)
- Validation on import (warn on invalid, skip relationship)

**User Stories**:
- US4: "As a process modeler, I can specify AND/OR/XOR junctions to model decision and merge points"
- US5: "As an exporter, I can round-trip junction types without loss"

### FR3: Element Visual Properties (Colors, Line Width, Transparency)

**Requirement**: Store and preserve element visual styling (colors, borders, opacity) with round-trip fidelity.

**Details**:
- Per-element fill color (hex #RRGGBB or named color)
- Per-element line color (border)
- Per-element line width (pixels, non-negative float)
- Per-element transparency (0.0-1.0, where 0=invisible, 1=opaque)
- Standard ArchiMate palette provides defaults
- Properties stored in XML as `<property>` elements
- Color validation strict on set, lenient on import
- Named colors converted to hex on normalization

**User Stories**:
- US6: "As a designer, I can customize element colors to match organizational standards"
- US7: "As an exporter, I can preserve custom colors in exported files for round-trip fidelity"
- US8: "As a modeler, I can use transparency to show element relationships or hierarchy visually"

---

## Success Criteria

### SC1: Grouping Round-Trip Fidelity
**Measurable**: Export model with grouped elements, import back, verify parent-child relationships preserved
- ✅ All 3+ level hierarchies preserved
- ✅ Cycle prevention active (no malformed trees imported)

### SC2: Junction Type Preservation
**Measurable**: Export junctions with types, import, verify types intact
- ✅ AND/OR/XOR types preserved on round-trip
- ✅ Invalid types logged as warnings during import

### SC3: Visual Properties Preservation
**Measurable**: Set element colors/widths, export, import, verify values unchanged
- ✅ All four properties (fill, line, width, transparency) preserved
- ✅ Color normalization correct (hex vs named)

### SC4: Backward Compatibility
**Measurable**: All existing P1+P2 features work unchanged
- ✅ No Element or Model API breaking changes
- ✅ Existing tests pass without modification
- ✅ Existing models load correctly

### SC5: Code Quality
**Measurable**:
- ✅ 100+ new unit tests for grouping and visual styles
- ✅ 30+ integration tests for round-trip fidelity
- ✅ 15+ BDD acceptance tests
- ✅ All pre-commit checks pass (linting, type checking)

---

## Architecture & Design

### Storage Design (Hybrid Approach)

**Element Additions**:

```python
Element._parent_uuid: Optional[str] = None        # Parent reference
Element._visual_style: dict[str, Any] = {}        # Visual properties
```

**Model Additions**:

```python
Model._element_hierarchy: dict[str, Optional[str]]  # child → parent mapping
Model._element_children: dict[str, set[str]]       # parent → children mapping
```

### Validation Rules

- **Cycle Detection**: O(depth) ancestor walk before mutation
- **Depth Limit**: Max 5 levels enforced
- **Color Validation**: Hex (#RRGGBB) or named colors, normalized to lowercase hex
- **Range Checks**: lineWidth ≥ 0; transparency ∈ [0.0, 1.0]

### XML Serialization

**Element Attributes**:
- `parentId`: UUID of parent element (optional)
- `folder`: Existing organizational path (independent of grouping)

**Properties**:
- `fillColor`: Element fill color (hex)
- `lineColor`: Element border color (hex)
- `lineWidth`: Element border width (pixels)
- `transparency`: Element opacity (0.0-1.0)
- `junctionType`: Junction type ('and', 'or', 'xor')

---

## Assumptions & Constraints

1. **Max Depth = 5**: Prevents pathological trees; sufficient for typical ArchiMate models
2. **Non-Destructive Delete**: Children orphaned on parent delete (preserves data)
3. **Unique Parent**: Each element has ≤1 parent (no multiple inheritance)
4. **Acyclic**: No circular relationships allowed (enforced on mutation)
5. **Folder Independence**: Folder and grouping completely separate (can coexist)
6. **P2 Pattern Reuse**: Grouping mirrors P2 viewpoint storage for consistency

---

## Integration Points

### With P1+P2 Features
- Element and Model APIs minimal changes (additive only)
- Existing viewpoint support unaffected
- Folder organization unaffected
- Relationship validation unaffected

### With XML Readers/Writers
- archimateReader: Extract parentId and visual properties on import
- archiWriter: Emit parentId and properties on export
- Validation on import: Non-strict (warn on errors, continue)

### With Test Suite
- Unit tests for grouping (30+ tests)
- Unit tests for visual styles (25+ tests)
- Integration tests for round-trip (30+ scenarios)
- BDD tests for user stories (15+ scenarios)

---

## Success Metrics

| Metric | Target | Method |
|--------|--------|--------|
| Code Coverage | ≥95% | pytest coverage report |
| Round-Trip Fidelity | 100% | Export/import test suite |
| Backward Compat | 100% | Existing test suite passes |
| Cycle Prevention | 100% | Unit tests for cycle detection |
| Color Validation | 100% | Unit tests for normalization |
| Performance | <100ms | Cycle detection on 1000+ element models |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Corrupted hierarchy on import | Data loss | Non-strict import, skip invalid, log warnings |
| Performance regression on large models | Usability | O(depth) cycle detection (max 5 = O(1) practical) |
| Color database out of sync | User confusion | Use standard CSS/X11 colors, clear error messages |
| Breaking changes to APIs | Incompatibility | Additive only, no signature changes |
| Orphaned children surprise | User confusion | Clear documentation and BDD tests |

---

## Phases (2-8)

**Phase 1**: ✅ Complete - Design & audit (see P3_DESIGN_MASTER.md)

**Phase 2** (3-4 days, 2026-05-04+): Core implementation
- Add Element attributes and Model storage
- Implement mutation & query APIs
- Add grouping unit tests
- Add visual style unit tests

**Phase 3** (2-3 days): Reader integration
- Extract parentId and properties on import
- Build hierarchy during read
- Validate on import

**Phase 4** (2-3 days): Writer integration
- Emit parentId and properties on export
- Verify round-trip fidelity
- Performance benchmarks

**Phases 5-8**: Advanced features, documentation, release
- Junction type validation
- Advanced queries
- Performance optimization
- Release documentation & v1.3.0

---

## Deliverables (Phase 2-8)

- ✅ Core grouping classes (Element._parent_uuid, Model hierarchy maps)
- ✅ Visual style setters/getters
- ✅ Unit tests (50+)
- ✅ Integration tests (30+)
- ✅ BDD acceptance tests (15+)
- ✅ Round-trip fidelity validation
- ✅ Updated Element.delete() with orphaning logic
- ✅ Code review ready
- ✅ Comprehensive documentation
- ✅ v1.3.0 release tag

---

## References

- **Phase 1 Design**: `/docs/P3_DESIGN_MASTER.md`
- **Element Audit**: `/docs/P3_AUDIT_ELEMENT_CLASS.md`
- **Model Audit**: `/docs/P3_AUDIT_MODEL_CLASS.md`
- **Containment Design**: `/docs/P3_DESIGN_CONTAINMENT.md`
- **Visual Style Design**: `/docs/P3_DESIGN_VISUAL_STYLE.md`
- **Folder/Grouping**: `/docs/P3_FOLDER_VS_GROUPING.md`
- **Test Fixtures**: `/tests/fixtures/p3_notation/`
- **Execution Guide**: `/P3_PHASE1_EXECUTION_GUIDE.md`

---

**Status**: Phase 1 Design Complete  
**Next**: Phase 2 Implementation (2026-05-04)
