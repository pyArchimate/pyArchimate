# P3 Task List: Complete ArchiMate Notation Support

**Version**: 1.0 (Planning Phase)  
**Date**: 2026-05-01  
**Feature**: ArchiMate v3.x Complete Notation Support (P3)  
**Branch**: `005-archimate-notation-support` (to be created)  
**Total Tasks**: 68 (T121–T188)  
**Status**: Planning Phase (No Implementation Yet)

---

## Overview

This task list covers the implementation of three complete ArchiMate notation features:

1. **P3.1: Element Grouping** (Semantic parent-child containment)
2. **P3.2: Junction Semantics** (Type validation for AND/OR/XOR)
3. **P3.3: Visual Properties** (Fill color, line color, line width, transparency)

**Scope**: 
- 68 tasks across 8 implementation phases
- 22–30 dev days estimated effort
- 90%+ test coverage maintained
- 100% round-trip fidelity
- 0 breaking changes to public API

---

## Phase 1: Foundation & Design (7 Tasks)

### Research & Specification

- [ ] **T121** [P] Audit Element class: Document all existing attributes, validation rules, and public API
- [ ] **T122** [P] Audit Model class: Understand element storage (elems_dict), current querying, relationships to views
- [ ] **T123** [P] Design containment tracking: Create design document for _element_hierarchy dict and parent UUID tracking
- [ ] **T124** [P] Design visual style storage: Compare property dict vs. VisualStyle dataclass; recommend approach
- [ ] **T125** [P] Verify folder concept: Confirm folders are metadata (not Element instances) and won't conflict with grouping
- [ ] **T126** Create P3 design document: Finalize data model, serialization rules, validation constraints, error handling
- [ ] **T127** [P] Create test fixtures: Build .archimate sample files with grouped elements, junctions, custom colors

---

## Phase 2: Element Grouping Implementation (10 Tasks)

### Core Classes

- [ ] **T128** [P] Add Element parent/children attributes: _parent_uuid and _children_uuids in Element.__init__
- [ ] **T129** [P] Implement add_child(child): Add child to _children_uuids; establish parent reference; cycle detection
- [ ] **T130** [P] Implement remove_child(child): Remove from _children_uuids; clear parent reference
- [ ] **T131** [P] Implement properties: get_children(), get_parent() with proper return types
- [ ] **T132** [P] Implement traversal: get_ancestors(), get_descendants() for tree navigation
- [ ] **T133** [P] Add depth validation: Enforce max 5-level containment depth
- [ ] **T134** [P] Implement cascade delete: Deleting parent element removes/clears children references
- [ ] **T135** Update Model: Add _element_hierarchy dict; maintain on add/delete operations

### Unit Tests (Grouping)

- [ ] **T136** [P] Test suite grouping logic: create, add_child, remove_child, parent consistency (8 unit tests)
- [ ] **T137** [P] Test cycle detection: Verify A→B→A raises ValueError; A→B→C→A also fails (2 edge case tests)

---

## Phase 3: Readers & Writers for Grouping (7 Tasks)

### XML Serialization

- [ ] **T138** Update archimateReader: Extend _archireader_helpers.py to parse nested <element> structures
- [ ] **T139** Update archimateReader: Establish parent-child references during import (Element.add_child calls)
- [ ] **T140** Update archiWriter: Emit nested <element> XML reflecting parent-child hierarchy
- [ ] **T141** Update archimateWriter: OpenGroup format support for element nesting (property-based or nested structure)
- [ ] **T142** [P] Manual testing: Import/export real Archi models with grouped elements; verify fidelity

### Integration Tests (Grouping)

- [ ] **T143** [P] Test roundtrip .archimate: grouped elements preserve nesting through export/import (5 integration tests)
- [ ] **T144** [P] Test roundtrip OpenGroup: grouped elements preserve nesting in OpenGroup format (5 integration tests)

---

## Phase 4: Junction Semantics (10 Tasks)

### Junction Implementation

- [ ] **T145** [P] Verify junction_type: Confirm Element.junction_type already exists (line 112 of element.py)
- [ ] **T146** [P] Add junction_type validation: Raise ValueError if not 'and' | 'or' | 'xor'; default to 'and'
- [ ] **T147** [P] Implement junction helpers: is_junction(), get_junction_type() convenience methods
- [ ] **T148** Implement Model.get_junctions(): Return all elements with elem_type == Junction

### Reader & Writer Updates

- [ ] **T149** [P] Design junction constraints: Document which relationships allowed per junction type (reference ArchiMate spec)
- [ ] **T150** Update archimateReader: Extract junctionType XML attribute; set Element.junction_type
- [ ] **T151** Update archiWriter: Emit junctionType as XML attribute on <element>
- [ ] **T152** Backward compatibility: Default to 'and' if junctionType missing (legacy file support)

### Unit Tests (Junctions)

- [ ] **T153** [P] Test junction creation/type: create Junction with and/or/xor type; verify storage (4 unit tests)
- [ ] **T154** [P] Test roundtrip junctions: .archimate and OpenGroup formats preserve type (4 integration tests)

---

## Phase 5: Visual Properties (10 Tasks)

### Visual Style Implementation

- [ ] **T155** [P] Design visual style storage: Finalize property dict structure {fill_color, line_color, line_width, transparency}
- [ ] **T156** [P] Add Element visual properties: Accessors fill_color, line_color, line_width, transparency (lazy-initialize)
- [ ] **T157** [P] Implement set_visual_style(): Fill color, line color, line width, transparency parameters
- [ ] **T158** [P] Implement get_visual_style(): Return dict with current style (includes defaults)
- [ ] **T159** [P] Color validation: Hex (#RRGGBB), named colors (red, blue, etc.), None; normalize to lowercase hex

### Reader & Writer Updates

- [ ] **T160** Update archimateReader: Extract visual properties from <property> elements; set Element visual style
- [ ] **T161** Update archiWriter: Emit visual properties as <property> elements (fillColor, lineColor, lineWidth, transparency)
- [ ] **T162** Implement color defaults: Standard ArchiMate palette (business=#FFFFB5, technology=#C9E7B7, etc.)

### Unit Tests (Visual Properties)

- [ ] **T163** [P] Test color validation: hex, named colors, None; invalid values rejected (6 unit tests)
- [ ] **T164** [P] Test roundtrip visual properties: .archimate and OpenGroup formats preserve colors (4 integration tests)

---

## Phase 6: Comprehensive Testing (7 Tasks)

### BDD & Full Suite

- [ ] **T165** [P] Create BDD feature files: grouping.feature, junctions.feature, visual_properties.feature (3 files)
- [ ] **T166** [P] Implement BDD steps: Step definitions for all three feature files in tests/features/steps/
- [ ] **T167** Run full test suite: `pytest tests/ --cov=src --cov-fail-under=90` (verify 90%+ coverage)
- [ ] **T168** Run BDD: `behave tests/features/` (verify all scenarios pass)
- [ ] **T169** Regression check: All P1+P2 tests still passing (453 tests baseline)

### Cross-Platform & Manual Testing

- [ ] **T170** [P] Manual testing: Import/export complex Archi models (grouping + junctions + styled elements)
- [ ] **T171** [P] Cross-platform: Test on macOS, Linux (Windows if available)

---

## Phase 7: Documentation (8 Tasks)

### Contract Documents

- [ ] **T172** Create contracts/grouped-elements.md: XML mappings, lifecycle, parent-child semantics, queries, edge cases
- [ ] **T173** Create contracts/junctions.md: Junction types (and/or/xor), constraints, relationship semantics, serialization
- [ ] **T174** Create contracts/visual-properties.md: Color palette, validation rules, inheritance, defaults, serialization

### Project Documentation

- [ ] **T175** Update specs/TECHNICAL.md: Add P3 implementation patterns (containment, visual styles, serialization)
- [ ] **T176** Update quickstart.md: Add examples for grouping (create, traverse, export), junctions (create, type set), visual properties
- [ ] **T177** Update CHANGELOG.md: Add v1.3.0 section with features, breaking changes (if any), migration guide
- [ ] **T178** [P] Add inline code comments: Mark complex logic in element.py, model.py, readers, writers (max 1-line per location)

### Final Review

- [ ] **T179** Final documentation review: Links, examples accuracy, completeness, consistency

---

## Phase 8: Review & Release (9 Tasks)

### Quality Gates

- [ ] **T180** Run pre-push checks: `bash scripts/pre_push_checks.sh` (full test suite, layer boundary, linting)
- [ ] **T181** Code review: SOLID principles (SRP, OCP, LSP, ISP, DIP), architecture, test coverage
- [ ] **T182** Linting: `ruff check src/pyArchimate/` (0 errors)
- [ ] **T183** Type checking: `mypy src/pyArchimate/` (0 errors)
- [ ] **T184** Formatting: `ruff format src/pyArchimate/` (all files properly formatted)

### Git & Release

- [ ] **T185** Create summary commit: Capture all P3 work (grouping, junctions, visual properties, docs)
- [ ] **T186** Open PR to develop: Request code review from team lead
- [ ] **T187** Address feedback: Iterate on review comments; push updates
- [ ] **T188** Merge & tag: Merge to develop; create v1.3.0 git tag

---

## Parallel Execution Opportunities

**Phase 1** (T121–T127): Can run in parallel
- T121, T122: Audits can run independently
- T123, T124, T125: Design tasks independent

**Phase 2** (T128–T137): Coding tasks can start once design done
- T128–T135 can run in parallel (different parts of Element/Model)
- T136–T137 can start once core implementation mostly complete

**Phases 3, 4, 5**: Reader/writer updates can overlap
- Reader and writer updates for different features (grouping vs. junctions vs. visual) can run in parallel

**Phase 6**: Testing can begin once Phase 5 mostly complete
- BDD steps can be written while code is being tested

---

## Task Dependencies

```
Phase 1: Foundation (T121-T127)
    ↓
Phase 2: Grouping Core (T128-T137)
    ↓ 
Phase 3: Serialization (T138-T144) ← → Phase 4: Junctions (T145-T154) ← → Phase 5: Visual (T155-T164) [Parallel]
    ↓
Phase 6: Testing (T165-T171)
    ↓
Phase 7: Documentation (T172-T179)
    ↓
Phase 8: Review & Release (T180-T188)
```

---

## Risk Areas & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Cycle detection performance | Slow on large models | Implement O(1) visited set tracking; test with 1000+ elements |
| Backward compatibility | Break legacy file imports | Property-based storage for visual styles; defaults for missing junction_type |
| Nesting depth limits | Confusing error messages | Clear ValueError with max depth; offer truncation option |
| Concurrent modifications | State corruption | Document that model operations must be serialized (GIL in CPython helps) |
| Cross-platform rendering | Visual inconsistency | Test color names on all platforms; use hex for consistency |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | 90%+ | `pytest --cov-fail-under=90` |
| Regressions | 0 | All P1+P2 tests (453) still passing |
| Round-Trip Fidelity | 100% | Integration tests: grouped/junction/visual preserved exactly |
| Code Quality | 0 errors | ruff lint, mypy, pyright checks |
| BDD Scenarios | All passing | `behave tests/features/` full success |
| Documentation | Complete | All 3 contracts + quickstart + CHANGELOG |
| Performance | No degradation | Model add/delete operations remain O(1) for most cases |

---

## Reference Documents

- **P3 Specification**: `/specs/004-archimate-spec-compliance/P3_NOTATION_SPEC.md`
- **P1+P2 Contracts**: `/specs/004-archimate-spec-compliance/contracts/`
- **Main Specification**: `/specs/004-archimate-spec-compliance/spec.md`
- **Constitution**: `/specs/.specify/memory/constitution.md`
- **Sample Files**: `/tests/fixtures/myModel.archimate` (contains junctions + grouping)

---

## Status Tracking

| Phase | Status | Owner | Notes |
|-------|--------|-------|-------|
| 1: Foundation | 📋 Planned | — | Design documents needed before implementation |
| 2: Grouping | 📋 Planned | — | Core feature; highest priority |
| 3: Serialization | 📋 Planned | — | Depends on Phase 2 |
| 4: Junctions | 📋 Planned | — | Simpler than grouping; can overlap |
| 5: Visual | 📋 Planned | — | Can overlap with phases 3–4 |
| 6: Testing | 📋 Planned | — | Depends on all implementation phases |
| 7: Documentation | 📋 Planned | — | Can start during Phase 6 |
| 8: Review & Release | 📋 Planned | — | Final gate before v1.3.0 release |

---

## How to Start Implementation

1. **Read** `/specs/004-archimate-spec-compliance/P3_NOTATION_SPEC.md` for refined design
2. **Execute** Phase 1 tasks (T121–T127) to finalize design and test fixtures
3. **Create** feature branch: `git checkout -b 005-archimate-notation-support`
4. **Begin** Phase 2: Start with T128 (Element attributes)
5. **Track** progress: Mark tasks as in_progress, completed in this document
6. **Iterate**: Use TDD cycle (Red → Green → Refactor) for each task

---

## Estimated Timeline

**Starting Point**: 2026-05-01 (after P2 completion)

- **Weeks 1–2**: Phases 1–2 (Foundation + Grouping)
- **Weeks 2–3**: Phase 3 (Serialization) + Phase 4 (Junctions) in parallel
- **Weeks 3–4**: Phase 5 (Visual Properties)
- **Weeks 4–5**: Phase 6 (Testing)
- **Weeks 5–6**: Phase 7 (Documentation)
- **Weeks 6–7**: Phase 8 (Review & Release)

**Total**: 6–7 weeks for full implementation + release
