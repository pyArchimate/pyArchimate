# Tasks: View Auto-Layout and Auto-Format

**Phase 2 Output** | **Date**: 2026-05-03 | **Feature Branch**: `011-view-auto-layout`

## Overview

This document contains the detailed task breakdown for implementing the View Auto-Layout and Auto-Format feature. Tasks are organized by phase and user story, with clear dependencies and parallel execution opportunities.

**Total Tasks**: 98 tasks across 7 phases  
**Estimated Duration**: MVP (US1+US2+foundational) ~3-4 weeks; Full feature ~6-7 weeks  
**Suggested MVP Scope**: Complete Phases 1-4 (Setup + Foundational + US1 + US2) + essential Phase 7 tasks

---

## Implementation Strategy

### Phase Structure

- **Phase 1**: Project Setup (shared infrastructure)
- **Phase 2**: Foundational (layout core, shared by all user stories)
- **Phase 3**: User Story 1 - Auto-Layout (force-directed algorithm, MVP critical)
- **Phase 4**: User Story 2 - Auto-Format (element standardization, MVP critical)
- **Phase 5**: User Story 3 - Hierarchical Layout (P2, specialized algorithm)
- **Phase 6**: User Story 4 - Customization (P2, advanced options)
- **Phase 7**: Polish & Documentation (cross-cutting, final refinement)

### MVP Scope

**Minimum Viable Product** includes:
- Force-directed layout algorithm (US1)
- Auto-format capability (US2)
- Basic orthogonal routing with label placement
- ArchiMate layer constraints enforced
- <2s performance for 300 elements
- Undo/rollback support

**Defer to Post-MVP**:
- Hierarchical layout algorithm (US3)
- Advanced configuration options (US4)
- Performance optimization beyond target
- Additional layout algorithms (grid, spline, etc.)

### Parallel Execution

Within each phase, independent tasks marked with `[P]` can be executed in parallel:
- **Phase 2**: Testing infrastructure can be set up in parallel with core module structure
- **Phase 3**: Algorithm implementation and integration tests can start simultaneously
- **Phase 4**: Element formatting and connection routing can be developed in parallel
- **Phase 5**: Hierarchical algorithm can be developed independently once Phase 2 is complete

---

## PHASE 1: Project Setup

### Goal
Establish project structure, create placeholder modules, and initialize testing infrastructure.

### Independent Test Criteria
- All module files exist with correct package structure
- PyCharm/IDE imports work without errors
- pytest discovers test files successfully

---

- [x] T001 Create layout module directory structure per plan in `src/pyArchimate/view/layout/`
- [x] T002 [P] Create `src/pyArchimate/view/layout/__init__.py` with public API exports
- [x] T003 [P] Create `src/pyArchimate/view/layout/core.py` with LayoutConfig and LayoutResult classes
- [x] T004 [P] Create `src/pyArchimate/view/layout/algorithms/` subdirectory
- [x] T005 [P] Create `src/pyArchimate/view/layout/algorithms/__init__.py` with algorithm registry
- [x] T006 [P] Create `src/pyArchimate/view/layout/routing/` subdirectory
- [x] T007 [P] Create `src/pyArchimate/view/layout/format/` subdirectory
- [x] T008 [P] Create `src/pyArchimate/view/layout/utils/` subdirectory
- [x] T009 [P] Create `tests/unit/layout/` directory
- [x] T010 [P] Create `tests/integration/` directory for round-trip tests
- [x] T011 [P] Create `tests/features/layout/` directory for BDD scenarios
- [x] T012 Update `pyproject.toml` to add layout module dependencies and test configuration
- [x] T013 Verify pytest configuration discovers all layout test files correctly
- [x] T014 [P] Create initial GitHub Actions CI/CD workflow for layout tests (if using CI)

---

## PHASE 2: Foundational Infrastructure

### Goal
Build shared layout core, geometry utilities, and foundational components required by all user stories.

### Blocking Tasks
- ALL user story tasks depend on completing Phase 2
- Layout algorithms (Phase 3+) require core classes and utilities
- Connection routing (all stories) requires utilities

### Independent Test Criteria
- Core classes (LayoutConfig, LayoutResult) instantiate correctly with valid parameters
- Utility functions (distance, intersection, grid) return correct values for test cases
- Layer constraint system validates and enforces layer ordering
- Geometry operations (point, rectangle, polyline) work correctly

---

- [x] T015 Implement LayoutConfig data class in `src/pyArchimate/view/layout/core.py` with validation
- [x] T016 Implement LayoutResult data class in `src/pyArchimate/view/layout/core.py` with quality metrics
- [x] T017 Implement base LayoutAlgorithm abstract class in `src/pyArchimate/view/layout/core.py`
- [x] T018 [P] Implement geometry utilities in `src/pyArchimate/view/layout/utils/geometry.py` (Point, Rectangle, distance, intersection, etc.)
- [x] T019 [P] Implement graph utilities in `src/pyArchimate/view/layout/utils/graph.py` (connectivity analysis, crossing detection)
- [x] T020 [P] Implement ArchiMate layer constraints in `src/pyArchimate/view/layout/routing/layer_constraints.py` (Layer enum, LayerConstraint class, validation)
- [x] T021 Implement apply_layout() public function in `src/pyArchimate/view/layout/__init__.py` with proper error handling
- [x] T022 [P] Implement apply_format() public function in `src/pyArchimate/view/layout/__init__.py` (delegates to FormatService)
- [x] T023 [P] Implement undo_layout() public function in `src/pyArchimate/view/layout/__init__.py` (uses pyArchimate transaction system)
- [x] T024 Create comprehensive unit tests in `tests/unit/layout/test_core.py` for LayoutConfig, LayoutResult validation
- [x] T025 [P] Create unit tests in `tests/unit/layout/test_geometry.py` for geometry utilities (distance, intersection, containment, etc.)
- [x] T026 [P] Create unit tests in `tests/unit/layout/test_layer_constraints.py` for layer constraint validation and enforcement
- [x] T027 Create integration test in `tests/integration/test_layout_api.py` for apply_layout(), apply_format(), undo_layout() with mock views

---

## PHASE 3: User Story 1 - Auto-Layout (Force-Directed)

### User Story Goal
Developers can invoke auto-layout on a view with overlapping/scattered elements and get a clean, non-overlapping layout with elements logically organized by relationships.

### Independent Test Criteria
- Force-directed layout completes in <2s for 300-element views
- 100% of elements are non-overlapping after layout
- Connections remain valid and linked to correct endpoints
- Layer boundaries are respected (if applicable)
- Element properties (name, type, docs) are preserved

### User Story Priority
**P1** - Core functionality, addresses most common pain point

---

- [x] T028 [US1] Implement ForceDirectedLayout class skeleton in `src/pyArchimate/view/layout/algorithms/force_directed.py`
- [x] T029 [US1] [P] Implement Spring-Embedder physics simulation core in `src/pyArchimate/view/layout/algorithms/force_directed.py` (repulsion, attraction forces)
- [x] T030 [US1] [P] Implement node position update loop with convergence detection in `src/pyArchimate/view/layout/algorithms/force_directed.py`
- [x] T031 [US1] [P] Implement adaptive iteration limits based on element count in `src/pyArchimate/view/layout/algorithms/force_directed.py`
- [x] T032 [US1] Implement layer constraint enforcement in force-directed layout in `src/pyArchimate/view/layout/algorithms/force_directed.py` (vertical/horizontal forces per layer)
- [x] T033 [US1] Register force-directed algorithm in layout registry (`src/pyArchimate/view/layout/algorithms/__init__.py`)
- [x] T034 [US1] [P] Implement connection routing: orthogonal polyline generation in `src/pyArchimate/view/layout/routing/orthogonal.py`
- [x] T035 [US1] [P] Implement connection routing: crossing detection and counting in `src/pyArchimate/view/layout/routing/orthogonal.py`
- [x] T036 [US1] [P] Implement barycentric crossing reduction in `src/pyArchimate/view/layout/routing/orthogonal.py`
- [x] T037 [US1] Implement connection endpoint spreading in `src/pyArchimate/view/layout/routing/orthogonal.py` (equal distribution on node edges)
- [x] T038 [US1] [P] Implement basic label positioning in `src/pyArchimate/view/layout/routing/label_placement.py` (offset perpendicular to connection)
- [x] T039 [US1] [P] Implement label overlap detection in `src/pyArchimate/view/layout/routing/label_placement.py`
- [x] T040 [US1] [P] Implement collision avoidance for labels in `src/pyArchimate/view/layout/routing/label_placement.py` (repositioning/truncation)
- [x] T041 [US1] [P] Create unit tests in `tests/unit/layout/test_force_directed.py` (convergence, force calculations, iteration limits)
- [x] T042 [US1] [P] Create unit tests in `tests/unit/layout/test_orthogonal_routing.py` (polyline generation, crossing minimization, endpoint spreading)
- [x] T043 [US1] [P] Create unit tests in `tests/unit/layout/test_label_placement.py` (collision detection, repositioning, truncation)
- [x] T044 [US1] Create integration test in `tests/integration/test_layout_round_trip.py` for force-directed layout (load → layout → save → verify XML integrity)
- [x] T045 [US1] Create BDD scenario in `tests/features/layout/auto_layout.feature` for "Auto-Layout Messy Diagram" with Given/When/Then steps
- [x] T046 [US1] Implement BDD step definitions in `tests/features/layout/auto_layout_steps.py` to support BDD scenarios

---

## PHASE 4: User Story 2 - Auto-Format

### User Story Goal
Developers can invoke auto-format on a view and get standardized element sizes, fonts, and alignment based on ArchiMate conventions, plus clean connection routing.

### Independent Test Criteria
- Element size variance reduced by 80% (measured by std dev)
- All elements aligned to grid (if alignment="grid")
- Fonts standardized per ArchiMate type
- Connections have orthogonal routing without overlaps
- Element properties (name, type, docs) preserved

### User Story Priority
**P1** - Improves diagram professionalism, works alongside US1

---

- [x] T047 [US2] Implement FormatService class in `src/pyArchimate/view/layout/format/element_format.py`
- [x] T048 [US2] [P] Implement ArchiMate element type → standard size mapping in `src/pyArchimate/view/layout/format/element_format.py`
- [x] T049 [US2] [P] Implement element resizing logic in `src/pyArchimate/view/layout/format/element_format.py` (respect user overrides)
- [x] T050 [US2] [P] Implement font standardization per ArchiMate type in `src/pyArchimate/view/layout/format/element_format.py`
- [x] T051 [US2] [P] Implement grid-based alignment in `src/pyArchimate/view/layout/format/element_format.py` (snap to grid or free positioning)
- [x] T052 [US2] Create unit tests in `tests/unit/layout/test_format.py` (size calculation, font mapping, alignment logic)
- [x] T053 [US2] Create integration test in `tests/integration/test_layout_round_trip.py` for auto-format (verify size/font standardization persists after save/load)
- [x] T054 [US2] Create BDD scenario in `tests/features/layout/auto_format.feature` for "Format Elements and Connections"
- [x] T055 [US2] Implement BDD step definitions in `tests/features/layout/auto_format_steps.py`

---

## PHASE 5: User Story 3 - Hierarchical Layout

### User Story Goal
Developers can apply hierarchical layout to views with parent-child relationships and get a layered, top-down visual structure respecting ArchiMate layer boundaries.

### Independent Test Criteria
- Elements organized in layers reflecting hierarchy
- Parent elements positioned above children (or left of children)
- Cross-layer connections visible and not obscured
- Business layer > Application layer > Technology layer enforced
- Layout completes in reasonable time for hierarchical views

### User Story Priority
**P2** - Valuable for organizational/hierarchical models, can be done after MVP

---

- [x] T056 [US3] Implement HierarchicalLayout class skeleton in `src/pyArchimate/view/layout/algorithms/hierarchical.py`
- [x] T057 [US3] [P] Implement Sugiyama layer assignment step respecting ArchiMate layers in `src/pyArchimate/view/layout/algorithms/hierarchical.py`
- [x] T058 [US3] [P] Implement Sugiyama crossing minimization step in `src/pyArchimate/view/layout/algorithms/hierarchical.py` (barycentric ordering)
- [x] T059 [US3] [P] Implement Sugiyama position assignment step in `src/pyArchimate/view/layout/algorithms/hierarchical.py` (node positioning in layers)
- [x] T060 [US3] Implement edge routing for hierarchical layout in `src/pyArchimate/view/layout/algorithms/hierarchical.py` (orthogonal routing respecting layers)
- [x] T061 [US3] Register hierarchical algorithm in layout registry
- [x] T062 [US3] [P] Create unit tests in `tests/unit/layout/test_hierarchical.py` (layer assignment, crossing minimization, position calculation)
- [x] T063 [US3] Create integration test for hierarchical layout in `tests/integration/test_layout_round_trip.py`
- [x] T064 [US3] Create BDD scenario in `tests/features/layout/auto_layout.feature` for "Hierarchical Layout"
- [x] T065 [US3] Implement BDD step definitions for hierarchical scenario

---

## PHASE 6: User Story 4 - Customization

### User Story Goal
Developers can customize layout behavior via LayoutConfig (algorithm selection, spacing, element exclusion, etc.) to meet domain-specific preferences.

### Independent Test Criteria
- All LayoutConfig options are respected (spacing, margin, alignment, etc.)
- Excluded elements retain their original positions
- Algorithm selection works correctly
- Custom configuration doesn't break layer constraints

### User Story Priority
**P2** - Enables real-world customization, can follow MVP

---

- [ ] T066 [US4] Implement advanced LayoutConfig options validation in `src/pyArchimate/view/layout/core.py` (all options from research.md)
- [ ] T067 [US4] [P] Implement excluded_element_ids handling in apply_layout() logic
- [ ] T068 [US4] [P] Implement spacing/margin parameter application in layout algorithms
- [ ] T069 [US4] [P] Implement alignment (grid vs. free) parameter handling in format module
- [ ] T070 [US4] [P] Implement routing_style parameter (orthogonal vs. mixed 45°) in routing module
- [ ] T071 [US4] [P] Implement layer_priority parameter (layer constraints vs. crossing reduction tradeoff)
- [ ] T072 [US4] Create unit tests in `tests/unit/layout/test_config.py` for all LayoutConfig combinations
- [ ] T073 [US4] Create integration test for config parameters in `tests/integration/test_layout_round_trip.py`
- [ ] T074 [US4] Create BDD scenario in `tests/features/layout/auto_layout.feature` for "Customize Layout Behavior"
- [ ] T075 [US4] Implement BDD step definitions for customization scenario

---

## PHASE 7: Polish & Documentation

### Goal
Final testing, documentation, API hardening, performance optimization, and cross-cutting concerns.

### Independent Test Criteria
- All edge cases handled (single element, no connections, circular deps, etc.)
- Performance targets met (<2s for 300 elements)
- Undo/rollback works reliably in all scenarios
- Documentation complete and accurate

---

- [ ] T076 Implement edge case handling for single-element views in all layout algorithms
- [ ] T077 [P] Implement edge case handling for views with no connections
- [ ] T078 [P] Implement edge case handling for views with circular dependencies
- [ ] T079 [P] Implement edge case handling for very large elements vs. small spacing
- [ ] T080 [P] Implement edge case handling for locked/fixed elements (deferred scope per Phase 5+)
- [ ] T081 Create comprehensive edge case tests in `tests/unit/layout/test_edge_cases.py`
- [ ] T082 Create performance tests in `tests/integration/test_layout_performance.py` (verify <2s for 300 elements, <5s for 500 elements)
- [ ] T083 [P] Performance profiling and optimization if necessary to meet targets
- [ ] T084 Create final round-trip integration test covering all scenarios in `tests/integration/test_layout_round_trip.py`
- [ ] T085 Run full test suite and ensure 100% pass rate (unit + integration + BDD)
- [ ] T086 [P] Create auto-layout-specifications.md technical document per spec deliverable (`specs/011-view-auto-layout/auto-layout-specifications.md`)
- [ ] T087 [P] Create user-facing documentation in project README (usage examples, algorithms overview)
- [ ] T088 [P] Update API documentation (docstrings, type hints for all public functions)
- [ ] T089 [P] Create architecture documentation explaining module structure and design decisions
- [ ] T090 [P] Create Sphinx RST documentation for layout feature in `docs/source/features/layout.rst`
- [ ] T091 [P] Update Sphinx index in `docs/source/index.rst` to include layout feature documentation
- [ ] T092 [P] Update Sphinx API documentation in `docs/source/api/view.rst` with layout module reference
- [ ] T093 [P] Build Sphinx documentation: `make clean && make html` in docs/ directory
- [ ] T094 Verify Sphinx build succeeds without warnings/errors and HTML output is correct
- [ ] T095 Verify code quality (ruff linting, mypy/pyright type checking, test coverage)
- [ ] T096 [P] Ensure undo/rollback integration with existing pyArchimate transaction system works correctly
- [ ] T097 [P] Final validation against constitution principles (code quality, testing, performance, etc.)
- [ ] T098 Create quick reference guide (`LAYOUT_QUICKSTART.md` in root or docs/)

---

## Task Summary by Phase

| Phase | Tasks | Focus |
|-------|-------|-------|
| Phase 1: Setup | T001-T014 (14 tasks) | Project structure, module initialization |
| Phase 2: Foundational | T015-T027 (13 tasks) | Core classes, utilities, shared infrastructure |
| Phase 3: US1 (Force-Directed) | T028-T046 (19 tasks) | Force-directed algorithm, routing, label placement |
| Phase 4: US2 (Auto-Format) | T047-T055 (9 tasks) | Element standardization, formatting |
| Phase 5: US3 (Hierarchical) | T056-T065 (10 tasks) | Hierarchical layout algorithm |
| Phase 6: US4 (Customization) | T066-T075 (10 tasks) | Configuration options, advanced features |
| Phase 7: Polish | T076-T098 (23 tasks) | Edge cases, performance, documentation, Sphinx build |
| **TOTAL** | **98 tasks** | **Full feature implementation** |

---

## MVP Task List (Phases 1-4 + Phase 7 Sphinx)

**MVP Scope**: Complete these phases for a functional, production-ready auto-layout feature:

- Phase 1: T001-T014 (14 tasks) — ~2 days
- Phase 2: T015-T027 (13 tasks) — ~3-4 days (critical path)
- Phase 3: T028-T046 (19 tasks) — ~5-6 days (longest phase)
- Phase 4: T047-T055 (9 tasks) — ~2-3 days
- Phase 7 (Sphinx + Core Docs): T086-T098 (subset) — ~2 days
- **Estimated MVP Duration**: 14-19 days (~3 weeks for experienced developer)

---

## Dependencies & Blocking Relationships

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKING GATE
    ↓
Phase 3 (US1) ─────┐
                   ├→ Phase 7 (Polish)
Phase 4 (US2) ─────┤
                   ├→ (Optional: Phase 5 & 6 for full feature)
Phase 5 (US3) ─────┤
                   │
Phase 6 (US4) ─────┘
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 7  
**Longest Phase**: Phase 3 (US1 Force-Directed, 19 tasks, 5-6 days)  
**Parallelizable Tasks**: Within each phase, many tasks marked [P] can run in parallel

---

## Execution Recommendations

### Week 1: Foundation & Core Algorithm
1. Complete Phase 1 (Setup) - Day 1
2. Complete Phase 2 (Foundational) - Days 2-4
3. Begin Phase 3 (US1) - Days 4-5

### Week 2: Force-Directed Layout & Testing
1. Complete Phase 3 (US1) - Days 1-3
2. Begin Phase 4 (US2) - Days 3-5

### Week 3: Auto-Format & MVP Release
1. Complete Phase 4 (US2) - Days 1-2
2. Complete Phase 7 Polish (MVP subset) - Days 2-5
3. **MVP Release Candidate Ready**

### Week 4+: Full Feature (Optional)
1. Phase 5 (US3 Hierarchical) - Days 1-3
2. Phase 6 (US4 Customization) - Days 3-5
3. Complete Phase 7 (Full Polish) - Days 5-10

---

## Success Metrics

- [ ] All 92 tasks (or MVP subset) completed and marked done
- [ ] 100% of unit tests passing
- [ ] 100% of integration tests passing
- [ ] 100% of BDD scenarios passing
- [ ] Performance targets met (<2s for 300 elements)
- [ ] Code review approved
- [ ] Documentation complete
- [ ] Feature merged to develop branch
- [ ] Release notes prepared
