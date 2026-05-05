# Implementation Plan: View Auto-Layout and Auto-Format

**Branch**: `011-view-auto-layout` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/011-view-auto-layout/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the
execution workflow.

## Summary

Implement auto-layout and auto-format functionality for ArchiMate views with two layout algorithms (force-directed and
hierarchical), mandatory ArchiMate layer respecting, orthogonal connection routing with intelligent label placement, and
advanced configuration options. MVP targets force-directed algorithm with hierarchical support. All algorithms must
enforce Business→Application→Technology layer constraints and achieve <2s layout time for 300-element views.

## Technical Context

**Language/Version**: Python 3.10+ (per pyproject.toml `requires-python = ">=3.10,<4.0"`)  
**Primary Dependencies**: lxml (ArchiMate XML parsing), existing pyArchimate view model, poetry (package manager)  
**Storage**: File I/O only (views are persisted as XML files within .archimate archives)  
**Testing**: pytest (unit/integration), behave (BDD acceptance tests)  
**Target Platform**: Cross-platform Python library (file-based I/O, no external services)
**Project Type**: Library (pyArchimate library for ArchiMate model manipulation)  
**Performance Goals**: <2 seconds for views with 300 elements, <5 seconds for 500-element views (SC-001)  
**Constraints**: Layout operates on in-memory view representation; no external layout engines; must preserve all
element/connection properties during repositioning  
**Scale/Scope**: Support views with up to 500 elements; MVP implements 1 core algorithm (force-directed) + 1
specialized (hierarchical); custom configuration for spacing, margins, alignment, element exclusion

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle                 | Status | Notes                                                                                                                                     |
|---------------------------|--------|-------------------------------------------------------------------------------------------------------------------------------------------|
| **I. Code Quality**       | ✓ PASS | Layout algorithms will use clear, modular design with helper functions; orthogonal routing and force-directed physics as distinct modules |
| **II. Testing Standards** | ✓ PASS | TDD approach: unit tests for layout algorithms, integration tests for round-trip view fidelity, BDD scenarios for acceptance criteria     |
| **III. UX Consistency**   | ✓ PASS | Configuration via LayoutConfig object; API follows existing view manipulation patterns                                                    |
| **IV. Performance**       | ✓ PASS | <2s requirement for 300 elements aligns with Constitution constraint; profiling during implementation                                     |
| **V. Security Practices** | ✓ PASS | Layout operates on in-memory models; no external inputs; view integrity validated before/after layout                                     |
| **VI. State Management**  | ✓ PASS | Layout is a transformation: view state → repositioned view; undo/rollback via existing transaction system                                 |
| **VII. System Integrity** | ✓ PASS | Layout must preserve all properties (names, docs, types, relationships); validation ensures output correctness                            |
| **VIII. Durability**      | ✓ PASS | Layout output is serializable to XML; round-trip tests verify fidelity across import/export cycles                                        |
| **IX. Cross-Platform**    | ✓ PASS | Pure Python, file-based; no platform-specific graphical dependencies                                                                      |

## Project Structure

### Documentation (this feature)

```text
specs/011-view-auto-layout/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   └── layout-api.md    # Public API contract for layout functions
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/pyArchimate/
├── view/
│   ├── layout/                  # NEW: Layout module
│   │   ├── __init__.py
│   │   ├── core.py              # LayoutConfig, LayoutResult, base layout interface
│   │   ├── algorithms/
│   │   │   ├── __init__.py
│   │   │   ├── force_directed.py # Force-directed physics-based layout
│   │   │   └── hierarchical.py   # Hierarchical layered layout
│   │   ├── routing/             # NEW: Connection routing
│   │   │   ├── __init__.py
│   │   │   ├── orthogonal.py    # Orthogonal routing, crossing minimization
│   │   │   ├── label_placement.py # Label positioning without overlaps
│   │   │   └── layer_constraints.py # ArchiMate layer enforcement
│   │   ├── format/              # NEW: Element formatting
│   │   │   ├── __init__.py
│   │   │   └── element_format.py # Element sizing, alignment, standardization
│   │   └── utils/               # Helpers: geometry, graph analysis
│   │       ├── __init__.py
│   │       ├── geometry.py
│   │       └── graph.py
│   └── model.py                 # Existing: View, Element, Connection classes (unchanged)

tests/
├── unit/
│   ├── layout/
│   │   ├── test_force_directed.py
│   │   ├── test_hierarchical.py
│   │   ├── test_orthogonal_routing.py
│   │   ├── test_label_placement.py
│   │   ├── test_layer_constraints.py
│   │   └── test_format.py
│   └── ...existing tests...
├── integration/
│   ├── test_layout_round_trip.py # Verify layout preserves model integrity
│   ├── test_undo_rollback.py     # Test undo/rollback behavior
│   └── ...existing tests...
└── features/
    └── layout/
        ├── auto_layout.feature    # BDD: auto-layout user stories
        └── auto_format.feature    # BDD: auto-format user stories
```

**Structure Decision**: Single project (DEFAULT) — Layout functionality integrates into existing pyArchimate view
module. New `layout/` subpackage contains algorithms, routing, and formatting. Tests follow existing pytest/behave
patterns with new test files under `tests/unit/layout/` and `tests/integration/`. No external services or databases.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation                  | Why Needed         | Simpler Alternative Rejected Because |
|----------------------------|--------------------|--------------------------------------|
| [e.g., 4th project]        | [current need]     | [why 3 projects insufficient]        |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient]  |
