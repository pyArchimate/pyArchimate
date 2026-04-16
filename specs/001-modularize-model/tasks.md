---

description: "Tasks for Modular Model Modules"
---

# Tasks: Modular Model Modules

**Input**: Design documents from `/specs/001-modularize-model/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (arising from /speckit.plan)

**Tests**: The feature spec requests regression coverage via the existing unit/integration/examples suites. New tests should keep failing until the implementation is ready.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently.

## Format: `[ID] [P?] [Story] Description`
- [P] = Parallelizable (no dependency on incomplete work)
- [Story] = `US1`/`US2`/`US3` according to spec priorities
- Include exact file paths for every task

---

## Phase 1: Setup (Shared infrastructure)

**Purpose**: Prepare the module/package structure before moving logic.

- [X] T001 [P] Create `src/pyArchimate/helpers/__init__.py` so the helper subpackage can be imported from the main package
- [X] T002 [P] Add placeholder helper modules `src/pyArchimate/helpers/diagram.py`, `src/pyArchimate/helpers/properties.py`, and `src/pyArchimate/helpers/logging.py` to receive the extracted utilities

---

## Phase 2: Foundational (Blocking prerequisites)

**Purpose**: Carve out the core module files and wiring that every story depends on.

- [X] T003 [P] Add `src/pyArchimate/model.py` that will host the `Model` class formerly living in `pyArchimate.py` and wire necessary imports
- [X] T004 [P] Add `src/pyArchimate/element.py` that will host the `Element` class plus property helpers extracted from `pyArchimate.py`
- [X] T005 [P] Add `src/pyArchimate/relationship.py` that will host the `Relationship` class and related connection helpers
- [X] T006 [P] Move the diagram/property/logging helpers (`get_or_create_node`, `embed_props`/`expand_props`, `pyArchimate.logger` setup, etc.) from `src/pyArchimate/pyArchimate.py` into the new helper modules under `src/pyArchimate/helpers`
- [X] T007 [P] Update `src/pyArchimate/__init__.py` to import/export `Model`, `Element`, `Relationship`, and the helper utilities from the new modules instead of `pyArchimate.py`
- [X] T008 [P] Keep `src/pyArchimate/pyArchimate.py` as a compatibility shim by re-exporting the public symbols from `pyArchimate.model`, `pyArchimate.element`, `pyArchimate.relationship`, and `pyArchimate.helpers`

---

## Phase 3: User Story 1 - Maintain architecture clarity (Priority: P1) 🎯 MVP

**Goal**: Ensure each core class lives in its own module and is reachable through the package surface.

**Independent Test**: Import `Model`, `Element`, and `Relationship` directly from `src.pyArchimate.model`, `element`, and `relationship` (via `src/pyArchimate/__init__.py`) and run existing unit assertions from `tests/unit/test_pyArchimate_pyArchimate.py`.

- [X] T009 [US1] Update `tests/unit/_helpers.py` and `tests/unit/test_pyArchimate_pyArchimate.py` so they import `Model` (and supporting primitives) from the new modules and the package entry point, keeping the tests otherwise unchanged
- [X] T010 [US1] Add `tests/unit/test_module_imports.py` that explicitly asserts `from src.pyArchimate.model import Model`, `from src.pyArchimate.element import Element`, and `from src.pyArchimate.relationship import Relationship` all succeed and expose the same API surface as before

---

## Phase 4: User Story 2 - Reader/writer stability (Priority: P2)

**Goal**: Keep reader, writer, and example adapters working without changing their public imports.

**Independent Test**: Run the reader/writer-specific unit tests (`tests/unit/test_pyArchimate_readers_*` and `tests/unit/test_pyArchimate_writers_*`) to confirm they still resolve `pyArchimate.Model`/`Element`/`Relationship` while internally importing via the package entry point.

- [X] T011 [US2] Update `src/pyArchimate/readers/archiReader.py`, `src/pyArchimate/readers/archimateReader.py`, and `src/pyArchimate/readers/arisAMLreader.py` to import the domain classes and helpers through the package entry points that now wrap `pyArchimate.model`, `element`, `relationship`, and `helpers`
- [X] T012 [US2] Update `src/pyArchimate/writers/archiWriter.py`, `src/pyArchimate/writers/archimateWriter.py`, and `src/pyArchimate/writers/csvWriter.py` to align with the new imports and confirm they still expose the same functions (e.g., `archi_writer`)
- [X] T013 [US2] Update `tests/examples/Archi2Aris.py` and any CLI helpers (`tests/examples/*.py`) to import through `src.pyArchimate` so they remain compatible with the re-exported symbols
- [X] T014 [US2] Run `poetry run pytest tests/unit/test_pyArchimate_readers_archiReader.py tests/unit/test_pyArchimate_readers_archimateReader.py tests/unit/test_pyArchimate_readers_arisAMLreader.py tests/unit/test_pyArchimate_writers_archiWriter.py tests/unit/test_pyArchimate_writers_archimateWriter.py tests/unit/test_pyArchimate_writers_csvWriter.py` to verify reader/writer stability (command recorded for verification)

---

## Phase 5: User Story 3 - Documentation and diagrams (Priority: P3)

**Goal**: Document the modular layout in PlantUML and regenerated docs so users know where to look for each class.

**Independent Test**: Inspect `docs/diagrams/package.puml` and `docs/diagrams/class.puml` renders (PNG) to confirm the new modules/helpers appear where the spec expects them.

- [X] T015 [US3] Update `docs/diagrams/package.puml` so the `pyArchimate` package shows `model.py`, `element.py`, `relationship.py`, and `helpers` as separate components while preserving reader/writer packages
- [X] T016 [US3] Update `docs/diagrams/class.puml` (and any closely related UML file that references `pyArchimate.py`) to reflect the new class/module locations and helper responsibilities
- [X] T017 [US3] Run `scripts/render_diagrams.sh` so all PNG outputs (`package.png`, `class.png`, etc.) are regenerated from the updated `.puml` sources
- [X] T018 [US3] Run `scripts/create_documentation.sh` to rebuild `docs/diagrams.rst` and other Sphinx outputs that reference the refreshed diagrams

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and hygiene across the feature.

- [X] T019 Run `poetry run pytest` to verify the full test suite passes after the refactor
- [X] T020 Run `poetry check` to ensure packaging metadata and imports remain valid with the split modules
- [X] T026 Add a layer-boundary enforcement check (e.g., via `importlinter` or a custom `ast` script) to CI that fails if any Layer 2 module (`model.py`, `element.py`, `relationship.py`) imports from Layer 3 or Layer 4 — satisfies AC-004
- [X] T027 Create `tests/integration/test_state_preservation.py` that imports both the old and new code paths and asserts logging level, reader registry, and writer registry state are identical before and after modularization — covers the state-persistence edge case in spec.md
- [X] T028 Run `poetry run ruff check src/pyArchimate && poetry run pyright src/pyArchimate && poetry run mypy src/pyArchimate` and confirm zero errors — satisfies AC-010

---

## Phase 6: Legacy-Independent Views & Writers (New)

**Purpose**: Remove core runtime dependencies on `_legacy.py` while preserving legacy import compatibility.

**TDD order**: Write failing tests first (T021a–T021c), then implement (T021–T025).

- [X] T021a [P] Write failing tests in `tests/unit/test_view.py` asserting `from pyArchimate.view import View, Node, Connection, Profile` succeeds and that each class exposes the same interface as the current `_legacy.py` equivalents — tests must fail before T021 runs
- [X] T021b [P] Write failing tests in `tests/unit/test_legacy_independence.py` asserting that `model.py`, `element.py`, and `relationship.py` import cleanly with `_legacy.py` absent from `sys.modules` — tests must fail before T022 runs
- [X] T021c [P] Write failing tests in `tests/unit/test_writer_registry.py` asserting `register_writer` and `_resolve_writer` are importable from a modern module (not `_legacy`) — tests must fail before T023 runs
- [X] T021 Replace the legacy-facade shim in `src/pyArchimate/view.py` with full modern implementations of `View`, `Node`, `Connection`, and `Profile` that have zero `_legacy` imports, maintaining full behavioral parity (validation, styling, bendpoints, properties, profiles).
- [X] T022 Update `model.py`, readers, and writers to import the new view stack; keep `_legacy` consuming the new classes as a fallback, not vice versa.
- [X] T023 Move writer registry/resolution (`register_writer`, `_resolve_writer`, defaults) into modern code and point `_legacy` at it; ensure legacy custom writer registration still works.
- [X] T024 Add/adjust tests to assert legacy import shims still expose `Element`, `Relationship`, `View`, and writer registration while core modules import only modern code.
- [X] T025 Run full test suite with `_legacy` present but unused by core modules; document the outcome in `specs/001-modularize-model/spec.md`.

**Acceptance Test**: With `_legacy.py` left untouched on disk, core modules (`model.py`, `element.py`, `relationship.py`, new view/writer modules) must import only modern code paths; `PYTHONPATH=. poetry run pytest` passes, and legacy import tests continue to succeed.

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** must complete before foundational files exist
- **Phase 2 (Foundational)** blocks all user stories because they depend on the new module files and exports
- **User Story phases (Phase 3+)** depend on the foundational split but can proceed in parallel once it completes
- **Polish** depends on all user stories being in place

## Parallel Opportunities

- Tasks marked `[P]` (T001–T008) can run in parallel because they touch different files/directories
- User stories can be worked on concurrently once foundational work is complete, while US2 and US3 also expose parallelism inside their phases

## Implementation Strategy

1. Finish Setup + Foundational phases to add new module files and re-export the API
2. Add tests and reader/writer adjustments (US1/US2) to confirm the new structure behaves identically
3. Document the new architecture and rebuild the diagrams/docs (US3)
4. Run the full regression suite (`poetry run pytest`) and `poetry check` before final review
