# P3: Complete ArchiMate Notation Support - Task Breakdown

**Feature**: 005-archimate-notation-support  
**Status**: Phase 1 Design Complete → Phase 2 COMPLETE ✅  
**Total Tasks**: 68 (T001-T068)  
**Completed**: Phase 2 Core Implementation (T001-T024) + 113 unit tests  
**Timeline**: 22-30 dev days (8 phases) | Phase 2: ~1 day (ahead of schedule)  
**Generated**: 2026-05-01

---

## Overview

Tasks organized by phase and user story. Each task is independently specific and executable.

**Phase Structure**:
- Phase 2: Core Implementation (Element grouping + visual styles)
- Phase 3: Reader Integration (XML import with hierarchy)
- Phase 4: Writer Integration (XML export with fidelity)
- Phase 5: Junction Semantics (AND/OR/XOR validation)
- Phase 6: Advanced Features (Query optimization, performance)
- Phase 7: Testing & Documentation
- Phase 8: Release & Polish

---

## Phase 2: Core Implementation (T001-T010)

**Goal**: Implement element grouping and visual style storage with unit tests  
**Duration**: 3-4 days  
**Deliverable**: Core classes with 50+ unit tests

### Grouping Core (US1, US2)

- [x] T001 Add Element._parent_uuid attribute with default None in `src/pyArchimate/element.py` line 114
- [x] T002 Add Element._visual_style dict with default {} in `src/pyArchimate/element.py` line 115
- [x] T003 [P] Add Model._element_hierarchy dict with default {} in `src/pyArchimate/model.py` line 207
- [x] T004 [P] Add Model._element_children dict with default {} in `src/pyArchimate/model.py` line 208
- [x] T005 [US1] Implement Model.add_child(parent_uuid, child_uuid) with cycle detection in `src/pyArchimate/model.py`
- [x] T006 [US1] Implement Model.remove_child(parent_uuid, child_uuid) with bidirectional map cleanup in `src/pyArchimate/model.py`
- [x] T007 [P] [US2] Implement Model.get_parent(elem_uuid) in `src/pyArchimate/model.py`
- [x] T008 [P] [US2] Implement Model.get_children(elem_uuid) in `src/pyArchimate/model.py`
- [x] T009 [P] [US2] Implement Model.get_ancestors(elem_uuid) and Model.get_descendants(elem_uuid) in `src/pyArchimate/model.py`
- [x] T010 [P] [US2] Implement Model.get_depth(elem_uuid), Model.get_root_elements(), Model.get_leaf_elements() in `src/pyArchimate/model.py`

### Visual Style Core (US6)

- [x] T011 [P] Create NAMED_COLORS and STANDARD_PALETTE constants in `src/pyArchimate/constants.py`
- [x] T012 [P] Implement _normalize_color() helper function in `src/pyArchimate/element.py`
- [x] T013 [US6] Implement Element.set_fill_color(color) with validation in `src/pyArchimate/element.py`
- [x] T014 [P] [US6] Implement Element.set_line_color(color) in `src/pyArchimate/element.py`
- [x] T015 [P] [US6] Implement Element.set_line_width(width) with range validation in `src/pyArchimate/element.py`
- [x] T016 [P] [US6] Implement Element.set_transparency(alpha) with range validation in `src/pyArchimate/element.py`
- [x] T017 [US6] Implement Element.set_visual_style() bulk setter in `src/pyArchimate/element.py`
- [x] T018 [P] [US6] Implement Element.get_fill_color(), get_line_color(), get_line_width(), get_transparency() in `src/pyArchimate/element.py`
- [x] T019 [P] [US6] Implement Element.get_visual_style() and reset_visual_style() in `src/pyArchimate/element.py`

### Element Deletion Integration

- [x] T020 Modify Element.delete() to orphan children instead of cascading in `src/pyArchimate/element.py` lines 115-140

### Unit Tests Phase 2

- [x] T021 [US1] Create test_element_grouping.py with 50+ tests (add_child, remove_child, cycle detection, depth) in `tests/unit/`
- [x] T022 [P] [US2] Create test_model_queries.py with 30+ tests (get_parent, get_children, get_ancestors, get_descendants) in `tests/unit/`
- [x] T023 [P] [US6] Create test_visual_style.py with 35+ tests (color validation, normalization, ranges) in `tests/unit/`
- [x] T024 Verify all Phase 2 unit tests pass and coverage ≥95%

---

## Phase 3: Reader Integration (T025-T035)

**Goal**: Extract hierarchy and visual properties on XML import  
**Duration**: 2-3 days  
**Deliverable**: Full import support with validation

### Reader Implementation

- [ ] T025 Modify archimateReader.py to extract parentId attribute during element parsing in `src/pyArchimate/readers/archimateReader.py`
- [ ] T026 [P] Modify archimateReader.py to extract visual style properties (fillColor, lineColor, lineWidth, transparency) in `src/pyArchimate/readers/archimateReader.py`
- [ ] T027 Create _build_hierarchy_from_parents() helper to reconstruct Model maps after all elements loaded in `src/pyArchimate/readers/archimateReader.py`
- [ ] T028 [US3] Implement hierarchy validation on import with cycle detection in `src/pyArchimate/readers/archimateReader.py`
- [ ] T029 Implement lenient import error handling (warn on invalid, skip relationship) in `src/pyArchimate/readers/archimateReader.py`
- [ ] T030 [P] Implement color validation/normalization on import in `src/pyArchimate/readers/archimateReader.py`

### Integration Tests Phase 3

- [ ] T031 [US3] Create test_round_trip_grouping.py with 15+ import/export tests in `tests/integration/`
- [ ] T032 [P] Create test_import_hierarchies.py with edge cases (cycles, depth > 5, missing parents) in `tests/integration/`
- [ ] T033 Verify round-trip fidelity: export grouped model → import → verify hierarchy preserved

---

## Phase 4: Writer Integration (T036-T046)

**Goal**: Emit hierarchy and visual properties on XML export  
**Duration**: 2-3 days  
**Deliverable**: Full export support with 100% fidelity

### Writer Implementation

- [ ] T034 Modify archiWriter.py to emit parentId attribute for each element in `src/pyArchimate/writers/archiWriter.py`
- [ ] T035 [P] Modify archiWriter.py to emit visual style properties as <property> elements in `src/pyArchimate/writers/archiWriter.py`
- [ ] T036 [US7] Verify parent-child relationships preserved on round-trip in `tests/integration/test_round_trip_visual_style.py`

### Round-Trip Validation

- [ ] T037 Create test_round_trip_visual_style.py with 10+ tests (colors, widths, transparency) in `tests/integration/`
- [ ] T038 [P] Create test_fidelity_validation.py with 5+ comprehensive round-trip scenarios in `tests/integration/`
- [ ] T039 Verify 100% fidelity: model → write → read → verify identical state

---

## Phase 5: Junction Semantics (T047-T055)

**Goal**: Validate and preserve junction types (AND/OR/XOR)  
**Duration**: 2 days  
**Deliverable**: Junction type system with validation

### Junction Implementation

- [ ] T040 [US4] Implement junction_type validation in Element (restrict to 'and', 'or', 'xor') in `src/pyArchimate/element.py`
- [ ] T041 [P] Create JunctionType enum or validation constant in `src/pyArchimate/constants.py`
- [ ] T042 [US4] Implement set_junction_type(type_str) with validation in `src/pyArchimate/element.py`
- [ ] T043 [P] Implement get_junction_type() getter in `src/pyArchimate/element.py`

### Reader/Writer Integration

- [ ] T044 Modify archimateReader.py to extract and validate junctionType properties in `src/pyArchimate/readers/archimateReader.py`
- [ ] T045 [P] Modify archiWriter.py to emit junctionType properties in `src/pyArchimate/writers/archiWriter.py`

### Junction Tests

- [ ] T046 [US4] Create test_junction_semantics.py with 10+ tests (types, validation, round-trip) in `tests/unit/`
- [ ] T047 [US5] Create test_round_trip_junctions.py with 8+ export/import scenarios in `tests/integration/`

---

## Phase 6: Advanced Features (T056-T062)

**Goal**: Query optimization, performance, advanced traversal  
**Duration**: 2 days  
**Deliverable**: Efficient queries and utilities

### Performance & Optimization

- [ ] T048 [P] Implement _would_create_cycle() private helper for O(depth) cycle detection in `src/pyArchimate/model.py`
- [ ] T049 [P] Implement _get_depth() private helper in `src/pyArchimate/model.py`
- [ ] T050 Create performance benchmark tests (1000+ element models) in `tests/performance/`
- [ ] T051 Verify cycle detection <1ms and queries <10ms on large models

### Advanced Queries

- [ ] T052 [P] Implement get_siblings(elem_uuid) helper in `src/pyArchimate/model.py`
- [ ] T053 [P] Implement find_by_hierarchy_path(path) helper in `src/pyArchimate/model.py`
- [ ] T054 Create test_advanced_queries.py in `tests/unit/`

---

## Phase 7: BDD & Documentation (T063-T068)

**Goal**: Acceptance tests and comprehensive documentation  
**Duration**: 3 days  
**Deliverable**: 15+ BDD scenarios, full documentation

### BDD Acceptance Tests

- [ ] T055 [US1] Create grouping.feature with 7 BDD scenarios in `tests/features/`
- [ ] T056 [P] [US6] Create visual_style.feature with 5 BDD scenarios in `tests/features/`
- [ ] T057 [P] [US3] [US4] [US7] Create integration.feature with 3 complex scenarios in `tests/features/`
- [ ] T058 Implement step definitions for all feature scenarios in `tests/features/steps/`

### Documentation

- [ ] T059 Update Element class docstrings with new methods in `src/pyArchimate/element.py`
- [ ] T060 Update Model class docstrings with new methods in `src/pyArchimate/model.py`
- [ ] T061 Create CHANGELOG.md entry for v1.3.0 with all P3 features
- [ ] T062 Create P3_IMPLEMENTATION_NOTES.md with design decisions and patterns in `docs/`

### Final Validation

- [ ] T063 Run full test suite: `pytest tests/ --cov --cov-report=html`
- [ ] T064 Run code quality: `ruff check src/ && mypy src/ && pyright src/`
- [ ] T065 Verify no breaking changes: all existing tests pass unchanged
- [ ] T066 Verify round-trip fidelity: export/import complex models with all features

---

## Phase 8: Release (T067-T068)

**Goal**: Tag release and prepare v1.3.0  
**Duration**: 1 day  
**Deliverable**: v1.3.0 tag and release notes

### Release Tasks

- [ ] T067 Create git tag v1.3.0 with comprehensive release notes
- [ ] T068 Update version in pyproject.toml and __init__.py to 1.3.0

---

## Dependencies & Execution Order

### Critical Path (must complete in order)
1. Phase 2 (T001-T024): Core classes
2. Phase 3 (T025-T033): Reader integration
3. Phase 4 (T034-T039): Writer integration

### Can be Parallelized
- Within Phase 2: Model dicts (T003-T004) parallel with Element attributes (T001-T002)
- Within Phase 2: Grouping methods (T005-T010) parallel with visual style methods (T011-T019)
- Within Phase 3: Reader modifications (T025-T030) parallel with tests (T031-T033)
- Within Phase 4: Writer modifications (T034-T036) parallel with tests (T037-T039)
- Phase 5-8: Can overlap with Phase 3-4 (independent features)

### Story-Level Dependencies

**US1 (Grouping creation)** → Blocks US2, US3  
**US2 (Hierarchy queries)** → Blocks US1  
**US3 (Import hierarchies)** → Requires US1+US2  
**US4 (Junction types)** → Independent of US1-3  
**US5 (Junction round-trip)** → Requires US4  
**US6 (Visual styles)** → Independent of US1-5  
**US7 (Style round-trip)** → Requires US6  
**US8 (Transparency visual)** → Requires US6  

---

## User Story Coverage

| Story | Description | Phase | Tasks |
|-------|-------------|-------|-------|
| US1 | Organize business processes into sub-processes | P2 | T001-T010, T021 |
| US2 | View element hierarchy | P2 | T007-T010, T022 |
| US3 | Load Archi-exported models with grouping | P3 | T025-T033 |
| US4 | Specify AND/OR/XOR junctions | P5 | T040-T047 |
| US5 | Round-trip junction types | P5 | T044-T047 |
| US6 | Customize element colors | P2 | T011-T019, T023 |
| US7 | Preserve custom colors in exports | P4 | T034-T039 |
| US8 | Use transparency visually | P2,P4 | T016, T039 |

---

## Parallel Execution Opportunities

### Phase 2 Parallel Teams
```
Team A (Grouping):     T001-T010, T021, T025-T033
Team B (Visual):       T011-T019, T023, T034-T036
Team C (Tests):        T024, T037-T039, T046-T047
  → All can start simultaneously, integrate at Phase 3
```

### Phase 3-4 Parallel Strategy
```
Reader Team:           T025-T033 (extract + validate)
Writer Team:           T034-T039 (emit + verify)
Test Team:             T031-T032, T037-T038 (round-trip tests)
  → All run in parallel, merge before Phase 5
```

---

## Estimated Task Duration

| Phase | Tasks | Duration | Dev Days |
|-------|-------|----------|----------|
| Setup | - | - | 0 (done) |
| Phase 2 | T001-T024 | Core impl + unit tests | 3-4 |
| Phase 3 | T025-T033 | Reader integration | 2-3 |
| Phase 4 | T034-T039 | Writer integration | 2-3 |
| Phase 5 | T040-T047 | Junction semantics | 2 |
| Phase 6 | T048-T054 | Advanced features | 2 |
| Phase 7 | T055-T066 | BDD + docs | 3 |
| Phase 8 | T067-T068 | Release | 1 |
| **TOTAL** | **68** | | **22-30 days** |

---

## Success Metrics

✅ **All 68 tasks completed**  
✅ **100+ unit tests passing (50+ Phase 2, 30+ Phase 3, 25+ Phase 4)**  
✅ **15+ BDD acceptance tests passing**  
✅ **100% round-trip fidelity (grouping, junctions, styles)**  
✅ **Zero breaking changes (all existing tests pass)**  
✅ **95%+ code coverage**  
✅ **All pre-commit checks passing**  
✅ **v1.3.0 tag created and documented**  

---

## References

- **Phase 1 Design**: `/docs/P3_DESIGN_MASTER.md`
- **Specification**: `spec.md`
- **Technical Plan**: `plan.md`
- **Data Model**: `data-model.md`
- **API Contracts**: `contracts/`
- **Test Fixtures**: `/tests/fixtures/p3_notation/` (4 files, 26 elements)

---

**Status**: ✅ Ready for Phase 2 Implementation  
**Next**: Run `/speckit-implement phase 2` to begin implementation

