# Tasks: SVG Z-Order Fix for Contained Elements

**Bug Fix** | **Date**: 2026-05-06 | **Feature Branch**: `011-view-auto-layout`

## Overview

This document contains the task breakdown for fixing SVG rendering z-order to ensure contained elements appear behind their parent containers. This is a focused bug fix addressing a visual hierarchy issue in SVG exports.

**Total Tasks**: 17 tasks across 3 phases  
**Estimated Duration**: ~1-2 days  
**Scope**: Complete bug fix (all phases required)

---

## Implementation Strategy

### Phase Structure

- **Phase 1**: Analysis & Understanding (identify the problem and current behavior)
- **Phase 2**: Implementation (implement z-order fix)
- **Phase 3**: Testing & Validation (unit and integration tests)

### MVP Scope

This entire bug fix is the minimum viable product. All phases must complete:
- Node containment hierarchy analysis
- SVG rendering order fix implementation  
- Unit and integration tests validating z-order correctness
- Backward compatibility verification (flat views unchanged)

No features are deferred; this is a complete, self-contained bug fix.

### Parallel Execution

Within each phase, independent tasks marked with `[P]` can be executed in parallel:
- **Phase 1**: Tasks T002-T003 (review SVG export and identify rendering gaps)
- **Phase 2**: Tasks T007-T008 (edge case handling for both View-rooted and nested nodes)
- **Phase 3**: Tasks T011-T014 (all unit test implementations can run in parallel)

---

## PHASE 1: Analysis & Understanding

### Goal
Understand the Node containment hierarchy in the view model and identify how the current SVG rendering fails to respect z-order.

### Independent Test Criteria
- Documentation of Node parent-child relationships is clear
- Current SVG rendering flow is fully understood
- Test case with nested nodes demonstrates z-order bug
- Problem is localized to SVG export module, not model

### Blocking Tasks
- All Phase 2 implementation depends on understanding Node model and current rendering

---

- [x] T001 Analyze Node containment hierarchy in `src/pyArchimate/view/__init__.py` and document parent-child relationships
- [x] T002 [P] Review current SVG rendering flow in `src/pyArchimate/view/layout/export/svg_export.py` (lines 34-87, specifically the to_svg method)
- [x] T003 [P] Identify all node rendering calls and understand how nodes are currently ordered
- [x] T004 Create a test case with nested nodes (parent containing child) to verify current z-order bug

---

## PHASE 2: Implementation

### Goal
Implement node sorting by containment hierarchy and integrate into SVG export rendering pipeline.

### Independent Test Criteria
- Nodes with parent references are sorted before their children
- Nodes with View parent maintain compatibility (appear in original order)
- Deep nesting is handled without stack overflow or performance degradation
- SVG rendering remains under 2 seconds for 300-element views
- No breaking changes to public APIs (Node, View, SVGExportService)

### Blocking Tasks
- Phase 3 testing depends on Phase 2 implementation

---

- [x] T005 Implement `_sort_nodes_by_hierarchy()` method in SVGExportService class to sort nodes so parents precede children using depth-first traversal
- [x] T006 Modify `to_svg()` method to use sorted node order: replace `for node in view.nodes:` with `for node in self._sort_nodes_by_hierarchy(view):`
- [x] T007 [P] Handle edge case: nodes without parent references (direct View children) should maintain compatibility
- [x] T008 [P] Ensure sort handles deep nesting (arbitrary containment depth) without stack overflow
- [x] T009 Add inline documentation to rendering order change explaining the z-order requirement

---

## PHASE 3: Testing & Validation

### Goal
Validate z-order fix through unit and integration tests, ensuring correctness and backward compatibility.

### Independent Test Criteria (for entire bug fix)
- Z-order Correctness: SVG export of nested view renders parent nodes before child nodes in XML output
- Visual Hierarchy: Containers appear behind contained elements (verified in SVG element tree)
- Backward Compatibility: Flat views (all nodes with View parent) render identically to before fix
- Performance: SVG export remains under 2 seconds for 300-element views
- Edge Cases: Empty views, single-node views, deeply nested views all render correctly
- No regressions: All existing tests continue to pass

---

- [x] T010 Create unit test file `tests/unit/view/layout/export/test_svg_zorder.py` with tests for `_sort_nodes_by_hierarchy()` method
- [x] T011 [P] Write unit test: `test_sort_parents_before_children()` - verify parents in output list before their children
- [x] T012 [P] Write unit test: `test_sort_preserves_view_root_nodes()` - verify nodes with View parent maintain position
- [x] T013 [P] Write unit test: `test_sort_handles_deep_nesting()` - verify deeply nested nodes maintain hierarchy
- [x] T014 [P] Write unit test: `test_sort_empty_node_list()` - verify edge case with no nodes
- [x] T015 Add integration test to `tests/integration/test_svg_background.py`: `test_svg_zorder_parent_before_children()` verifying SVG element tree has parents before children
- [x] T016 [P] Add integration test: `test_nested_elements_render_hierarchy()` - export view with nested nodes and verify SVG structure
- [x] T017 Verify all existing tests pass (ruff, pyright, mypy, pytest) - no regressions introduced

---

## Files Affected

### Modified
- `src/pyArchimate/view/layout/export/svg_export.py` - Add sort method, modify to_svg()
- `tests/integration/test_svg_background.py` - Add z-order integration tests

### Created
- `tests/unit/view/layout/export/test_svg_zorder.py` - New unit test module

### Unchanged
- `src/pyArchimate/view/__init__.py` - Node and View classes (analysis only)
- All symbol definitions and other SVG utilities

---

## Success Criteria

✅ All unit tests pass (test_svg_zorder.py)  
✅ All integration tests pass (test_svg_background.py)  
✅ All existing tests continue to pass (no regressions)  
✅ Code quality checks pass: ruff, pyright, mypy  
✅ Z-order bug is fixed: nested views render with correct visual hierarchy  

---

## Risk Mitigation

**Low Risk** - Change is localized to SVG rendering order

- No changes to model persistence (views still save/load identically)
- No changes to View or Node class APIs
- Sorting is deterministic and testable
- Fallback: if sort encounters unforeseen issues, can revert single change in to_svg()

---

## Summary

This bug fix consists of 17 focused tasks across 3 phases:
- **Phase 1 (4 tasks)**: Understanding Node containment and current rendering
- **Phase 2 (5 tasks)**: Implementing sort algorithm and integrating into SVG export
- **Phase 3 (8 tasks)**: Unit and integration tests validating correctness

All phases are required for a complete fix. The entire scope should take 1-2 days of focused development.
