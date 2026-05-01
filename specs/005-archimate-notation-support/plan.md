# Implementation Plan: P3 Complete ArchiMate Notation Support

**Timeline**: 22-30 dev days across 8 phases  
**Start**: 2026-05-04 (Phase 2)  
**Target**: 2026-05-28 (v1.3.0 release)

---

## Architecture Overview

### Core Principle: Hybrid Storage (mirrors P2 viewpoint pattern)

```
Element (stores parent reference):
  ._parent_uuid: Optional[str] = None

Model (stores bidirectional maps):
  ._element_hierarchy: dict[child_uuid → parent_uuid]
  ._element_children: dict[parent_uuid → set(child_uuids)]
```

**Why Hybrid?**
- O(1) parent lookup (Element._parent_uuid)
- O(1) child enumeration (Model._element_children)
- Efficient cycle detection (O(depth), max 5)
- Avoids storing object references (cleaner XML serialization)
- Mirrors P2 viewpoint pattern for consistency

### Technology Stack

**Language**: Python 3.10+ (existing)  
**XML Processing**: lxml (existing)  
**Testing**: pytest + behave (existing)  
**Type Checking**: mypy/pyright (existing)  
**Code Quality**: ruff + pysonar (existing)

### File Structure & Responsibilities

```
src/pyArchimate/
├── element.py
│   ├── NEW: Element._parent_uuid attribute
│   ├── NEW: Element._visual_style dict
│   ├── NEW: set_fill_color(), get_fill_color()
│   ├── NEW: set_line_color(), get_line_color()
│   ├── NEW: set_line_width(), get_line_width()
│   ├── NEW: set_transparency(), get_transparency()
│   ├── NEW: set_visual_style(), get_visual_style()
│   ├── MODIFY: Element.delete() - add orphaning logic
│   └── NEW: Color normalization helpers
│
├── model.py
│   ├── NEW: Model._element_hierarchy dict
│   ├── NEW: Model._element_children dict
│   ├── NEW: add_child(parent_uuid, child_uuid)
│   ├── NEW: remove_child(parent_uuid, child_uuid)
│   ├── NEW: get_parent(elem_uuid) → Element
│   ├── NEW: get_children(elem_uuid) → list[Element]
│   ├── NEW: get_ancestors(elem_uuid) → list[Element]
│   ├── NEW: get_descendants(elem_uuid) → list[Element]
│   ├── NEW: get_depth(elem_uuid) → int
│   ├── NEW: get_root_elements() → list[Element]
│   ├── NEW: get_leaf_elements() → list[Element]
│   ├── NEW: _would_create_cycle(parent, child) → bool (private)
│   └── NEW: _get_depth(elem_uuid) → int (private)
│
├── readers/archimateReader.py
│   ├── MODIFY: Extract parentId attribute on import
│   ├── NEW: Extract visual style properties (fillColor, lineColor, etc.)
│   ├── NEW: Build Model._element_hierarchy during read
│   └── NEW: Validate hierarchies on import (warn on errors)
│
└── writers/archiWriter.py
    ├── MODIFY: Emit parentId attribute on export
    ├── NEW: Emit visual style properties as <property> elements
    └── NEW: Verify round-trip fidelity

tests/
├── unit/
│   ├── NEW: test_element_grouping.py (30+ tests)
│   │   ├── test_add_child (valid, already-has-parent, self-ref, cycle, depth, missing)
│   │   ├── test_remove_child (valid, not-parent, missing)
│   │   ├── test_get_parent, test_get_children, test_get_ancestors, test_get_descendants
│   │   ├── test_cycle_detection (algorithm correctness)
│   │   ├── test_depth_calculation (1-5 levels)
│   │   └── test_delete_with_grouping (orphaning)
│   │
│   ├── NEW: test_visual_style.py (25+ tests)
│   │   ├── test_color_validation (hex valid/invalid, named colors)
│   │   ├── test_color_normalization (case, hex conversion)
│   │   ├── test_line_width (valid, negative, type errors)
│   │   ├── test_transparency (valid, out-of-range, type errors)
│   │   ├── test_getters_setters (individual and bulk)
│   │   └── test_reset_style
│   │
│   └── NEW: test_constants.py
│       └── NAMED_COLORS dict with 140+ CSS/X11 colors
│
├── integration/
│   ├── NEW: test_round_trip_grouping.py (15+ tests)
│   │   ├── Test export/import with 1-5 level hierarchies
│   │   ├── Test mixed grouping + visual styles
│   │   ├── Test mixed with P2 viewpoints
│   │   └── Test invalid hierarchy handling on import
│   │
│   ├── NEW: test_round_trip_visual_style.py (10+ tests)
│   │   ├── Test color preservation
│   │   ├── Test line width/transparency preservation
│   │   └── Test property-dict serialization
│   │
│   └── NEW: test_grouping_queries.py (5+ tests)
│       ├── Query performance on large models
│       └── Cycle detection performance
│
└── features/ (BDD acceptance tests)
    ├── NEW: grouping.feature (7 scenarios)
    │   ├── Add element as child
    │   ├── Remove parent-child relationship
    │   ├── Prevent cycles
    │   ├── Enforce depth limit
    │   └── Orphan children on delete
    │
    ├── NEW: visual_style.feature (5 scenarios)
    │   ├── Set fill color
    │   ├── Validate line width
    │   ├── Preserve on round-trip
    │   └── Named color conversion
    │
    └── NEW: integration.feature (3 scenarios)
        ├── Combined grouping + visual styles
        └── Complex hierarchy with multiple property types
```

---

## Data Model Design

### Element Class Additions

```python
class Element:
    # NEW: Parent-child grouping (P3)
    _parent_uuid: Optional[str] = None
    
    # NEW: Visual style properties (P3)
    _visual_style: dict[str, Any] = {}
    
    # Properties
    @property
    def parent_uuid(self) -> Optional[str]:
        """UUID of parent element, or None if root."""
    
    # Visual style setters (validate on set)
    def set_fill_color(self, color: Optional[str]) -> None: ...
    def set_line_color(self, color: Optional[str]) -> None: ...
    def set_line_width(self, width: Optional[float]) -> None: ...
    def set_transparency(self, alpha: Optional[float]) -> None: ...
    
    # Visual style getters
    def get_fill_color(self) -> Optional[str]: ...
    def get_line_color(self) -> Optional[str]: ...
    def get_line_width(self) -> Optional[float]: ...
    def get_transparency(self) -> Optional[float]: ...
    
    # Bulk operations
    def set_visual_style(self, fill_color=..., line_color=..., ...) -> None: ...
    def get_visual_style(self) -> dict[str, Any]: ...
    def reset_visual_style(self) -> None: ...
    
    # MODIFY: Element.delete() - add orphaning
    def delete(self) -> None:
        """Delete element; orphan children (parent_uuid = None)."""
```

### Model Class Additions

```python
class Model:
    # NEW: Bidirectional hierarchy tracking
    _element_hierarchy: dict[str, Optional[str]] = {}     # child → parent
    _element_children: dict[str, set[str]] = {}           # parent → children
    
    # Mutation API
    def add_child(self, parent_uuid: str, child_uuid: str) -> None:
        """Assign parent to child. Raises on cycle, depth exceeded, not found."""
    
    def remove_child(self, parent_uuid: str, child_uuid: str) -> None:
        """Remove parent-child relationship. Child becomes root."""
    
    # Query API
    def get_parent(self, elem_uuid: str) -> Optional[Element]: ...
    def get_children(self, elem_uuid: str) -> list[Element]: ...
    def get_ancestors(self, elem_uuid: str) -> list[Element]: ...
    def get_descendants(self, elem_uuid: str) -> list[Element]: ...
    def get_depth(self, elem_uuid: str) -> int: ...
    def get_root_elements(self) -> list[Element]: ...
    def get_leaf_elements(self) -> list[Element]: ...
    
    # Private helpers
    def _would_create_cycle(self, parent: str, child: str) -> bool: ...
    def _get_depth(self, elem: str) -> int: ...
```

### Constants & Validation

```python
# New in constants.py or element.py

MAX_DEPTH = 5  # Maximum nesting level

NAMED_COLORS = {
    'red': '#ff0000',
    'blue': '#0000ff',
    'green': '#008000',
    'yellow': '#ffff00',
    'black': '#000000',
    'white': '#ffffff',
    # ... 134+ more CSS/X11 colors
}

STANDARD_PALETTE = {
    'strategy': '#F5DEAA',
    'business': '#FFFFB5',
    'application': '#B5FFFF',
    'technology': '#C9E7B7',
    'physical': '#C9E7B7',
    'migration': '#FFE0E0',
    'motivation': '#CCCCFF',
    'implementation': '#FFE0E0',
    'relationship': '#DDDDDD',
    'junction': '#000000',
    'other': '#FFFFFF'
}
```

---

## Phase Breakdown

### Phase 2 (T128-T137): Core Implementation (3-4 days)
**Focus**: Element grouping + visual style storage

Tasks:
- T128: Add Element._parent_uuid attribute
- T129: Add Element visual style dict and properties
- T130: Implement visual style setters with validation
- T131: Implement visual style getters
- T132: Add Model hierarchy dicts
- T133: Implement add_child() with validation
- T134: Implement remove_child()
- T135: Implement query methods (get_parent, get_children, etc.)
- T136: Update Element.delete() for orphaning
- T137: Add unit tests (grouping + visual styles)

**Deliverables**: Core classes, 50+ unit tests, code review ready

### Phase 3 (T138-T142): Reader Integration (2-3 days)
**Focus**: Import with hierarchy validation

### Phase 4 (T143-T147): Writer Integration (2-3 days)
**Focus**: Export with fidelity validation

### Phases 5-8: Polish, documentation, release (2 weeks)

---

## Testing Strategy

### Unit Tests (50+)
- Grouping: add_child, remove_child, cycle detection, depth, queries
- Visual styles: color validation, normalization, getters/setters
- Constants: NAMED_COLORS, STANDARD_PALETTE

### Integration Tests (30+)
- Round-trip: export/import with hierarchies
- Fidelity: colors preserved, properties intact
- Queries: performance on 1000+ element models
- Error handling: malformed imports

### BDD Tests (15+)
- User stories: grouping, visual styles, round-trip
- Edge cases: max depth, cycle prevention, orphaning
- Complex scenarios: multiple hierarchies, mixed properties

### Performance Benchmarks
- Cycle detection: <1ms on 1000 element models
- Query performance: <10ms for descendant traversal
- Memory: <100KB overhead for hierarchy maps (1000 elements)

---

## Dependencies & Constraints

### Requirements Met
- ✅ Python 3.10+ (existing)
- ✅ lxml for XML (existing)
- ✅ pytest for unit tests (existing)
- ✅ behave for BDD (existing)

### No New Dependencies Added
- All requirements already available
- Only using existing test frameworks

### Backward Compatibility Constraints
- ✅ No Element.__init__() signature change (new attributes have defaults)
- ✅ No Model API breaking changes (only additive methods)
- ✅ Existing tests must pass unchanged (validate with `pytest tests/`)
- ✅ Element.delete() behavior expanded (no breaking change)

---

## Quality Gates

### Before Phase 2 Starts
- [X] Phase 1 design complete and reviewed
- [X] Architecture approved
- [X] Test fixtures created and validated

### Before Phase 3
- [ ] Phase 2 code complete
- [ ] 50+ unit tests passing
- [ ] Code review approved
- [ ] All pre-commit checks pass

### Before Phase 4
- [ ] Phase 3 reader integration complete
- [ ] 30+ integration tests passing
- [ ] Round-trip validation passed

### Before Release
- [ ] All 8 phases complete
- [ ] 100+ total tests passing
- [ ] 100% round-trip fidelity
- [ ] Zero breaking changes
- [ ] Documentation complete

---

## Success Criteria

1. **Functional**: All 3 features implemented and tested
2. **Fidelity**: 100% round-trip preservation of grouping and styles
3. **Compatibility**: 100% backward compatible, all existing tests pass
4. **Quality**: 95%+ code coverage, all pre-commit checks pass
5. **Performance**: Cycle detection <1ms on large models
6. **Documentation**: Comprehensive docs, examples, BDD tests

---

## References

- **Phase 1 Design**: `/docs/P3_DESIGN_MASTER.md`
- **Containment Design**: `/docs/P3_DESIGN_CONTAINMENT.md`
- **Visual Style Design**: `/docs/P3_DESIGN_VISUAL_STYLE.md`
- **Test Fixtures**: `/tests/fixtures/p3_notation/` (4 files, 26 elements)

---

**Status**: Ready for Phase 2 Implementation  
**Next Step**: Run `/speckit-plan` to refine and `/speckit-tasks` to generate task breakdown

