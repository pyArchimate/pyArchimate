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

## Current State Assessment

### What Already Exists
- ✅ `Junction`, `OrJunction`, `AndJunction` enums defined in ArchiType
- ✅ Junction elements can be created and stored in elements_dict
- ✅ Visual properties (fillColor, lineColor) read/written to diagram XML
- ✅ Node class has fill_color, line_color properties
- ✅ Group visual containers exist at diagram level (archimate:Group)
- ⚠️ **Gap**: No semantic modeling of junctions (junctionType attribute not accessed)
- ⚠️ **Gap**: No element-level grouping (only visual grouping in diagrams)
- ⚠️ **Gap**: Visual properties not accessible from Element class

---

## Requirements & User Scenarios (Refined)

### User Story 1: Semantic Element Grouping (P3.1)

A developer creates a BusinessProcess element representing a "main process", then programmatically nests 2–3 BusinessFunction child elements inside it to represent sub-processes. The parent maintains a list of children; each child maintains a reference to parent. The containment hierarchy is preserved when exported to .archimate and re-imported.

**Acceptance Criteria**:
1. Element class supports optional parent reference (`element.parent`)
2. Element class supports children list (`element.children`)
3. Parent-child relationships are bidirectional and consistent
4. Cannot create cycles (validation prevents A→B→A)
5. Containment depth limited to 5 levels (per ArchiMate practical limit)
6. Export to .archimate preserves nested <element> structure
7. Import from .archimate correctly establishes parent-child relationships
8. Queries can traverse tree: `element.get_ancestors()`, `element.get_descendants()`
9. Deleting parent cascades to children (or raises error if non-empty)
10. Child element ordering preserved in round-trip

---

### User Story 2: Junction Semantics & Type Validation (P3.2)

A developer creates a Junction element (decision point), assigns it type "xor", then connects multiple incoming relationships. The junction enforces XOR semantics (only one input should be true at a time). The junction type is serialized to .archimate files and preserved on re-import.

**Acceptance Criteria**:
1. Junction element creation via `Element(ArchiType.Junction, ...)` succeeds
2. Junction.junction_type attribute supports: 'and' (default), 'or', 'xor'
3. Incoming and outgoing relationships are allowed on junctions (no validation error)
4. Junction type is serialized to .archimate as `<element...junctionType="and">` 
5. Import from .archimate correctly reads and sets junction_type
6. Validation can enforce allowed relationship types per junction type (AND/OR/XOR)
7. Visual representation reflects junction type (different symbols per ArchiMate spec)
8. Round-trip fidelity: junction type preserved through export/import cycle
9. Query methods: `model.get_junctions()`, `element.get_junction_type()`
10. Backward compatibility: legacy files without junctionType default to 'and'

---

### User Story 3: Element-Level Visual Properties (P3.3)

A developer creates a BusinessActor element, then sets custom visual properties: fillColor="#0066FF", lineColor="#000000", lineWidth=2.0. These properties are accessible from the Element class (not just Node). When exported to .archimate and re-imported, the visual styling is preserved.

**Acceptance Criteria**:
1. Element class exposes visual properties: fill_color, line_color, line_width, transparency
2. Visual properties are stored in Element._visual_style dataclass (or properties dict)
3. Element.set_visual_style(fill_color, line_color, line_width, transparency) method
4. Element.get_visual_style() returns dict with current style
5. Export to .archimate writes style as XML attributes on <element> or as <property> elements
6. Import from .archimate reads style properties and restores to Element
7. Default colors apply if not explicitly set (per ArchiMate standard palette)
8. Style inheritance: Child elements can inherit parent style (unless overridden)
9. Color validation: Accepts #RRGGBB hex, named colors ('red', 'blue'), or None
10. Round-trip fidelity: 100% preservation of custom styles through export/import cycle

---

## Architecture & Data Model (Refined)

### Core Class Changes

**Element (src/pyArchimate/element.py)**:
```python
class Element:
    # Existing (already present):
    junction_type: Optional[str] = None  # 'and' | 'or' | 'xor'
    
    # NEW for P3:
    _parent_uuid: Optional[str] = None    # UUID of parent element
    _children_uuids: list[str] = []       # UUIDs of child elements
    _visual_style: dict = {}              # {fill_color, line_color, line_width, transparency}
    
    # Methods:
    def add_child(self, child_elem: Element) -> None
    def remove_child(self, child_elem: Element) -> None
    def get_children(self) -> list[Element]
    def set_parent(self, parent_elem: Optional[Element]) -> None
    def get_parent(self) -> Optional[Element]
    def get_ancestors() -> list[Element]
    def get_descendants() -> list[Element]
    def set_visual_style(self, fill_color=None, line_color=None, line_width=None, transparency=None)
    def get_visual_style() -> dict
```

**Model (src/pyArchimate/model.py)**:
```python
class Model:
    # NEW for tracking containment hierarchy:
    _element_hierarchy: dict[str, Optional[str]] = {}  # child_uuid → parent_uuid
    
    # Methods:
    def get_grouped_elements(self) -> list[Element]  # elements with children
    def get_junctions(self) -> list[Element]
    def get_elements_by_visual_style(self, fill_color=None) -> list[Element]
```

### XML Schema Mapping (ArchiMate 3.x)

**Grouped Element (Nested Children)**:
```xml
<element id="id-proc1" name="Main Process" xsi:type="BusinessProcess">
  <element id="id-func1" name="Sub-Process 1" xsi:type="BusinessFunction"/>
  <element id="id-func2" name="Sub-Process 2" xsi:type="BusinessFunction">
    <property key="fillColor" value="#0066FF"/>
  </element>
</element>
```

**Junction with Type**:
```xml
<element id="id-junc1" name="Decision" xsi:type="Junction" junctionType="xor">
  <!-- Relationships link to this junction; no child elements -->
</element>
```

**Visual Properties (Element-Level)**:
```xml
<element id="id-actor1" name="Customer" xsi:type="BusinessActor">
  <property key="fillColor" value="#0066FF"/>
  <property key="lineColor" value="#000000"/>
  <property key="lineWidth" value="2.0"/>
  <property key="transparency" value="0.8"/>
</element>
```

### Serialization Strategy

**Approach**: Use `<property key="...">` elements for visual properties (consistency with viewpoints)
- **Advantage**: Compatible with existing property parsing
- **Advantage**: Backward compatible (unknown properties ignored on import)
- **Advantage**: Works with both .archimate and OpenGroup formats

**Containment**: Use nested `<element>` structure (already supported by XML)
- **Advantage**: Preserves folder-like hierarchy in Archi
- **Advantage**: Natural nesting matches ArchiMate decomposition semantics
- **Limitation**: Depth-first; requires care when traversing

---

## Implementation Phases (Detailed Planning)

### Phase 1: Foundation & Refactoring (Week 1–2)
**Goal**: Establish base classes and storage; verify existing code doesn't conflict

- [ ] T121: Audit Element class; document all existing attributes and validation rules
- [ ] T122: Audit Model class; understand current element storage and querying
- [ ] T123: Design containment tracking mechanism (hierarchy dict in Model)
- [ ] T124: Design visual style storage (property dict vs. VisualStyle dataclass)
- [ ] T125: Verify no conflicts with existing folder concept (folders are metadata, not elements)
- [ ] T126: Create P3 design document (data model, serialization rules, validation rules)
- [ ] T127: Design test fixtures (sample .archimate files with grouped/junction/styled elements)

### Phase 2: Element Grouping (Week 2–3)
**Goal**: Implement semantic parent-child relationships for elements

- [ ] T128: Add _parent_uuid and _children_uuids to Element.__init__
- [ ] T129: Implement Element.add_child(child) with cycle detection
- [ ] T130: Implement Element.remove_child(child)
- [ ] T131: Implement Element.get_children(), get_parent() properties
- [ ] T132: Implement Element.get_ancestors(), get_descendants() traversal
- [ ] T133: Add containment validation: max depth 5 levels
- [ ] T134: Add cascade delete: deleting parent cleans up children references
- [ ] T135: Update Model._element_hierarchy to track parent relationships on add/delete
- [ ] T136: Unit tests: creation, parent-child consistency, cycle detection (10 tests)
- [ ] T137: Integration tests: grouping with multiple depths (5 tests)

### Phase 3: Reader & Writer Updates for Grouping (Week 3–4)
**Goal**: Preserve nested element structure in import/export

- [ ] T138: Update _archireader_helpers.py to parse nested <element> structures
- [ ] T139: Update archimateReader.py to establish parent-child references during import
- [ ] T140: Update archiWriter.py to emit nested element XML
- [ ] T141: Update archimateWriter.py (OpenGroup) to serialize nesting
- [ ] T142: Test with real Archi samples (grouping round-trip)
- [ ] T143: Integration tests: grouped elements round-trip .archimate (5 tests)
- [ ] T144: Integration tests: grouped elements round-trip OpenGroup (5 tests)

### Phase 4: Junction Semantics (Week 4–5)
**Goal**: Fully model junction types and enforce semantic constraints

- [ ] T145: Verify junction_type already exists in Element (confirm line 112)
- [ ] T146: Implement junction_type validation (only 'and'|'or'|'xor')
- [ ] T147: Add Junction helper methods (get_junction_type, is_junction)
- [ ] T148: Implement Model.get_junctions() query
- [ ] T149: Design junction constraint rules (AND/OR/XOR relationship semantics)
- [ ] T150: Update readers to extract junctionType from XML attribute
- [ ] T151: Update writers to emit junctionType as XML attribute
- [ ] T152: Implement backward compatibility (default to 'and' if not specified)
- [ ] T153: Unit tests: junction creation, type validation (8 tests)
- [ ] T154: Integration tests: junction type round-trip (4 tests)

### Phase 5: Visual Properties (Week 5–6)
**Goal**: Expose Node visual properties at Element level

- [ ] T155: Design VisualStyle approach (property dict vs. dataclass)
- [ ] T156: Add visual property accessors to Element (fill_color, line_color, line_width, transparency)
- [ ] T157: Implement Element.set_visual_style() method
- [ ] T158: Implement Element.get_visual_style() method
- [ ] T159: Design color validation and normalization (hex, named colors, None)
- [ ] T160: Update readers to extract visual properties from <property> elements
- [ ] T161: Update writers to emit visual properties
- [ ] T162: Implement color palette defaults (standard ArchiMate colors)
- [ ] T163: Unit tests: color validation, style storage (10 tests)
- [ ] T164: Integration tests: visual properties round-trip (5 tests)

### Phase 6: Testing & Validation (Week 6–7)
**Goal**: Comprehensive testing; ensure no regressions

- [ ] T165: BDD feature files: grouping.feature, junctions.feature, visual_properties.feature
- [ ] T166: BDD step implementations for all three features
- [ ] T167: Run full test suite: `pytest tests/ --cov=src --cov-fail-under=90`
- [ ] T168: Run BDD: `behave tests/features/`
- [ ] T169: Verify 0 regressions: all P1+P2 tests still passing
- [ ] T170: Manual testing with real Archi files (complex models)
- [ ] T171: Cross-platform testing (macOS, Linux, Windows if available)

### Phase 7: Documentation (Week 7–8)
**Goal**: Complete documentation and prepare for release

- [ ] T172: Create contracts/grouped-elements.md (XML mapping, lifecycle, queries)
- [ ] T173: Create contracts/junctions.md (junction types, constraints, relationships)
- [ ] T174: Create contracts/visual-properties.md (color palette, validation, inheritance)
- [ ] T175: Update specs/TECHNICAL.md with P3 implementation patterns
- [ ] T176: Update quickstart.md with examples for grouping, junctions, styling
- [ ] T177: Update CHANGELOG.md with v1.3.0 features and breaking changes (if any)
- [ ] T178: Add inline code comments where nesting, junction type, visual props are handled
- [ ] T179: Final documentation review and link updates

### Phase 8: Review & Merge (Week 8–9)
**Goal**: Code review and release

- [ ] T180: Run pre-push checks: `bash scripts/pre_push_checks.sh`
- [ ] T181: Code review: SOLID principles, architecture, test coverage
- [ ] T182: Linting: `ruff check src/pyArchimate/`
- [ ] T183: Type checking: `mypy src/pyArchimate/`
- [ ] T184: Formatting: `ruff format src/pyArchimate/`
- [ ] T185: Create summary commit with all P3 work
- [ ] T186: Open PR to develop; request code review
- [ ] T187: Address review feedback; iterate
- [ ] T188: Merge to develop and tag v1.3.0

---

## Estimated Effort (Refined)

| Phase | Task Count | Effort | Notes |
|-------|-----------|--------|-------|
| 1: Foundation | T121–T127 (7) | 2–3 days | Design + audit |
| 2: Grouping | T128–T137 (10) | 3–4 days | Core implementation |
| 3: Readers/Writers | T138–T144 (7) | 3–4 days | Serialization |
| 4: Junctions | T145–T154 (10) | 2–3 days | Simpler (type attribute only) |
| 5: Visual Props | T155–T164 (10) | 3–4 days | Color/style management |
| 6: Testing | T165–T171 (7) | 4–5 days | BDD + full suite + cross-platform |
| 7: Documentation | T172–T179 (8) | 3–4 days | Contracts + guides |
| 8: Review & Release | T180–T188 (9) | 2–3 days | CI/CD + PR |
| **TOTAL** | **T121–T188 (68 tasks)** | **22–30 days** | ~4–6 weeks full-time |

**Velocity assumptions**: 10–12 tasks/day (mix of coding, testing, documentation)

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

## Success Criteria (Refined)

### Functional
- ✅ All 13 ArchiMate standard element types supported (including Junction)
- ✅ Element containment: parent-child relationships with max 5-level depth
- ✅ Grouped elements create/import/export without loss
- ✅ Junction types (AND/OR/XOR) preserved in round-trip
- ✅ Visual styling (fill_color, line_color, line_width, transparency) preserved
- ✅ Backward compatibility: legacy files (without P3 features) import unchanged
- ✅ Query API: get_grouped_elements(), get_junctions(), get_elements_by_visual_style()

### Quality
- ✅ 90%+ test coverage maintained (no regression below 90%)
- ✅ 0 regressions in P1/P2 test suite (all 453 tests still passing)
- ✅ 100% round-trip fidelity for all three notation features
- ✅ 68+ new unit tests covering grouping, junctions, visual properties
- ✅ 10+ BDD acceptance scenarios (features) all passing
- ✅ Linting: 0 errors (ruff), type checking: 0 errors (mypy/pyright)

### Documentation
- ✅ 3 new contracts (grouped-elements.md, junctions.md, visual-properties.md)
- ✅ CHANGELOG.md entry for v1.3.0
- ✅ Quickstart.md examples for all three features
- ✅ Inline code comments for complex logic
- ✅ specs/TECHNICAL.md updated with P3 patterns

---

## Open Questions (Addressed in Refined Plan)

### ✅ Resolved
1. **Nesting Depth**: Practical limit set to 5 levels (per ArchiMate guidelines)
2. **Junction Types**: Already exist as junction_type attribute (and/or/xor)
3. **Visual Properties**: Already partially supported; extend from Node to Element
4. **Serialization**: Use nested <element> for grouping, <property> for visual styles
5. **Backward Compat**: Property-based approach is backward compatible

### ⚠️ For User Clarification
1. **Containment Semantics**: Should element containment affect relationship validity? 
   - E.g., can child-of-A relate to sibling-of-A?
   - *Recommendation*: No restrictions; containment is structural, not semantic

2. **Visual Style Inheritance**: Should child elements inherit parent colors?
   - *Recommendation*: No inheritance; each element has explicit style

3. **Junction Diagram Representation**: Visual symbol for AND/OR/XOR junctions?
   - *Recommendation*: Use Node rendering with type-specific icons (researched from Archi)

4. **Grouping vs. Folder**: Difference between element grouping and folder structure?
   - *Note*: Folders are model organization (metadata); grouping is semantic decomposition

5. **Performance**: Should model maintain cache of grouped elements?
   - *Recommendation*: Yes; lazy-load cache on first query (get_grouped_elements)

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
