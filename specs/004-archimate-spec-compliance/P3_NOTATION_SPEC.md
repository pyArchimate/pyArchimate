# P3 Feature Specification: Complete ArchiMate Notation Support

**Version**: 0.1 (Draft)  
**Date**: 2026-05-01  
**Priority**: P3 (Post-P2 work)  
**Status**: Planning Phase  
**Scope**: Complete ArchiMate visual notation and semantic modeling

---

## Executive Summary

**Goal**: Enable pyArchimate to preserve and manipulate all ArchiMate 3.x visual and structural notation elements, closing the final gap for full specification compliance.

**Current Gap**: While basic element and relationship notation is preserved, advanced notation features are either unsupported or lossy during round-trip:
- Grouped elements (visual containers with N child elements)
- Junctions (logical AND/OR/XOR nodes for relationship routing)
- Nesting hierarchies and containment semantics
- Custom visual properties (colors, fill patterns, borders)
- Diagram-level notation constraints (allowed elements per viewpoint)

**Impact**: Limiting use cases for:
- Large-scale enterprise models (grouped elements are essential for abstraction)
- Complex logic flows (junctions required for decision logic)
- Custom styling and branding
- Full Archi/Sparx file interoperability

---

## Requirements & User Scenarios (To Be Refined)

### User Story 1: Grouped Elements (Tentative P3.1)

A developer creates a BusinessProcess element, then nests 2–3 sub-processes inside it to represent decomposition. The model is exported to .archimate and re-imported; the grouping and nesting structure are preserved.

**Acceptance Criteria** (draft):
1. Developer can create a GroupableElement and assign child elements
2. Child elements maintain parent reference and ordering
3. Visual representation (diagram nodes) reflects nesting
4. Export/import round-trip preserves hierarchy
5. Queries can traverse containment tree (e.g., `element.children`, `element.parent`)

---

### User Story 2: Junctions (Tentative P3.2)

A developer creates an influence relationship from Actor A to Decision Point (Junction), then Junction to Actor B. The junction type (AND/OR/XOR) affects semantic interpretation. The model is exported and re-imported; junction type is preserved.

**Acceptance Criteria** (draft):
1. Developer can create Junction elements with type (AND/OR/XOR)
2. Relationships can target junctions without validation errors
3. Junction type affects allowed child relationships (AND allows >1 input)
4. Export/import preserves junction type and semantic constraints
5. Visualization reflects junction visual style per ArchiMate spec

---

### User Story 3: Custom Visual Properties (Tentative P3.3)

A developer colors BusinessActor elements blue (custom color), sets fill pattern to "hatch", and adds a 2pt border. When exported to .archimate and re-imported, the visual styling is preserved.

**Acceptance Criteria** (draft):
1. Elements support custom color, fill, border properties
2. Styling is stored in element metadata (properties dict)
3. Export formats preserve styling in XML attributes or property elements
4. Import restores styling without loss
5. Default (ArchiMate standard) colors apply if custom styling not specified

---

## Architecture & Data Model (Draft)

### Core Classes (To Be Designed)

```
GroupableElement(Element)
  - parent: Optional[str]  # UUID of parent GroupableElement
  - children: list[str]    # UUIDs of child elements
  - ordering: int          # Visual Z-order in parent

Junction(Element)
  - junction_type: str     # 'and' | 'or' | 'xor'
  - allowed_relationships: set[str]  # constraint list per type

VisualStyle(DataClass)
  - fill_color: str        # Hex RGB or standard color name
  - border_color: str      # Hex RGB
  - border_width: float    # Points
  - fill_pattern: str      # 'solid' | 'hatch' | 'gradient' | ...
  - transparency: float    # 0.0-1.0

# Extended on Element:
Element._visual_style: Optional[VisualStyle]
Element._notation_type: str  # 'standard' | 'junction' | 'group' | ...
```

### XML Schema Mapping (ArchiMate 3.x Notation)

**Grouped Element**:
```xml
<element id="id-group1" name="Process Group" xsi:type="BusinessProcess">
  <element id="id-child1" name="Sub-Process 1" xsi:type="BusinessFunction"/>
  <element id="id-child2" name="Sub-Process 2" xsi:type="BusinessFunction"/>
</element>
```

**Junction**:
```xml
<element id="id-junction1" name="Decision" xsi:type="Junction" junctionType="xor">
  <!-- Junction has no direct children; relationships define flow -->
</element>
```

**Visual Styling**:
```xml
<element id="id-actor1" name="Actor" xsi:type="BusinessActor" 
         fillColor="#0066FF" borderColor="#000000" borderWidth="2.0" fillPattern="solid">
</element>
```

---

## Tentative Phases (Detailed Planning TBD)

### Phase 1: Research & Design (Week 1)
- [ ] Audit existing Archi tool samples (grouped/nested elements, junctions)
- [ ] Document ArchiMate notation spec constraints and allowed patterns
- [ ] Design GroupableElement and Junction class hierarchies
- [ ] Finalize data model and XML schema mappings
- [ ] Write design specification for validation rules

### Phase 2: Grouped Elements Implementation (Week 2–3)
- [ ] Implement GroupableElement class
- [ ] Add parent-child relationship tracking in Model
- [ ] Update readers (_archireader_helpers) to parse nested elements
- [ ] Update writers (archiWriter) to emit nested structure
- [ ] Add containment validation and cycle detection
- [ ] Unit tests for creation, nesting, querying
- [ ] Integration tests for round-trip fidelity

### Phase 3: Junctions Implementation (Week 3–4)
- [ ] Implement Junction element type and junction_type attribute
- [ ] Add relationship constraint validation
- [ ] Update readers to parse junctions and link relationships
- [ ] Update writers to emit junction elements
- [ ] Unit tests for junction creation and type validation
- [ ] Integration tests for relationship flow semantics

### Phase 4: Visual Styling (Week 4–5)
- [ ] Design VisualStyle dataclass with color/pattern fields
- [ ] Add styling storage to Element metadata
- [ ] Update readers to extract color/border properties
- [ ] Update writers to emit styling attributes
- [ ] Implement color validation and standard palette
- [ ] Unit tests for style preservation
- [ ] Integration tests for round-trip color fidelity

### Phase 5: Testing & Documentation (Week 5–6)
- [ ] Comprehensive unit test suite (70+ tests)
- [ ] Integration round-trip tests (grouped + junctions + styling)
- [ ] BDD acceptance scenarios (10+ features)
- [ ] Contract documentation (grouped-elements.md, junctions.md, visual-styling.md)
- [ ] CHANGELOG entry for v1.3.0
- [ ] Quickstart examples for all three features

### Phase 6: Review & Merge (Week 6–7)
- [ ] Code review (SOLID principles, test coverage 90%+)
- [ ] Linting & type checking (ruff, mypy)
- [ ] Final documentation review
- [ ] PR to develop/master

---

## Estimated Effort

- **Research & Analysis**: 2–3 days
- **Implementation**: 10–15 days
- **Testing**: 5–8 days
- **Documentation**: 3–5 days
- **Review & Merge**: 2–3 days

**Total**: ~20–30 dev days (4–6 weeks at full-time pace)

---

## Dependencies & Constraints

### Hard Dependencies
- P1 & P2 must be complete and merged before starting P3
- Existing test suite must remain at 90%+ coverage
- No breaking changes to public API

### Constraints
- No new runtime performance targets (library-based, not latency-sensitive)
- Must maintain backward compatibility with P1/P2 files
- JSON, YAML, and other exchange formats out of scope (ArchiMate only)

---

## Success Criteria (Tentative)

- [ ] All 13 ArchiMate standard element types supported (including Junction)
- [ ] Grouped elements (nesting up to 5 levels) create/import/export without loss
- [ ] Junction types (AND/OR/XOR) preserved in round-trip
- [ ] Visual styling (color, border, pattern) preserved in round-trip
- [ ] 90%+ test coverage maintained
- [ ] 0 regressions in P1/P2 test suite
- [ ] 100% round-trip fidelity for notation features
- [ ] BDD acceptance scenarios all passing

---

## Open Questions (To Be Addressed in Detailed Planning)

1. **Nesting Depth**: Does ArchiMate spec limit nesting depth? What's practical max?
2. **Visual Styling Scope**: Should we support all Archi properties or subset?
3. **Junction Semantics**: Are constraint rules applied at export time or runtime?
4. **Backward Compat**: How do legacy elements (pre-P3) render when grouped?
5. **Validation Rules**: Which notation combinations are invalid per spec?

---

## Next Steps

1. Schedule P3 specification refinement session (with user/domain expert)
2. Research ArchiMate spec documents for notation constraints
3. Audit existing Archi samples for real-world notation patterns
4. Finalize data model and design document
5. Generate detailed task list (T121–T200+)

---

## Cross-Reference

- **P1 Spec**: User Stories 1–3 (BusinessInteraction, influence strength, relationship docs)
- **P2 Spec**: User Story 4 (Viewpoints and perspectives)
- **Main Spec**: `/specs/004-archimate-spec-compliance/spec.md`
- **Main Plan**: `/specs/004-archimate-spec-compliance/plan.md`
- **Constitution**: `/specs/.specify/memory/constitution.md`
