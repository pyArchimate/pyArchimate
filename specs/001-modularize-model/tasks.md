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
- [X] T004 [P] Add `src/pyArchimate/element.py` that will host the `Element` class plus serialization helpers extracted from `pyArchimate.py`
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
