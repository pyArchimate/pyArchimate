# Feature Specification: Modular Model Modules

**Feature Branch**: `001-modularize-model`  
**Created**: 2026-04-07  
**Status**: Draft  
**Input**: User description: "Split the gigantic `Model`, `Element`, `Relationship`, and related helpers in `src/pyArchimate/pyArchimate.py` into focused modules (e.g., `model.py`, `element.py`, `relationship.py`). The current single-file implementation mixes domain models, validation rules, reader/writer plumbing, and diagram helpers, which makes the code hard to reason about and test."

## Clarifications

### Session 2026-04-07
- Q: Should helper logic (diagram, property, logging, etc.) live in dedicated helper modules that are re-exported via `pyArchimate/__init__.py`? → A: Yes, to keep helpers testable but still available from the public package surface.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Maintain architecture clarity (Priority: P1)

As a core maintainer I need the Model, Element, Relationship, and view helpers to live in purpose-built files so I can reason about each domain concept independently, review changes faster, and add unit tests that target a single module.

**Why this priority**: Modular files are required before any major refactor or reader/writer change because the current monolithic `pyArchimate.py` creates cognitive overload and makes targeted testing almost impossible.

**Independent Test**: Execute unit tests that import each new module (e.g., `pyArchimate.model`, `pyArchimate.element`) and ensure the existing Model/Element APIs behave identically to the previous single-module implementation.

**Acceptance Scenarios**:

1. **Given** the new module file layout, **When** a reviewer inspects `pyArchimate.element`, **Then** they can find the Element class definition without scrolling through unrelated reader/writer logic.
2. **Given** the same core suite, **When** tests import `pyArchimate.model` and `pyArchimate.relationship`, **Then** they run in isolation with no additional reader/writer side effects.

---

### User Story 2 - Reader/writer stability (Priority: P2)

As a reader/writer owner I need to know that splitting modules does not change the public API so the adapters can still import `pyArchimate.Model`, `pyArchimate.Element`, and `pyArchimate.Relationship` without update.

**Why this priority**: Existing automation pipelines (Archi imports, CLI scripts) depend on `pyArchimate.py`; breaking that import path would cascade into downstream consumers.

**Independent Test**: Run the integration suite (or a targeted smoke test) that exercises the read/write adapters and confirm models load/save exactly as before.

**Acceptance Scenarios**:

1. **Given** the new modules, **When** a reader imports `pyArchimate.Model` from `pyArchimate/__init__.py`, **Then** it resolves to the split implementation and the read/save cycle works.

---

### User Story 3 - Documentation and diagrams (Priority: P3)

As a documentation author I need the architecture diagrams and Python docs to reference the same entities so I can point readers to the right module for each concept and keep the diagrams current.

**Why this priority**: Documentation must mirror the execution model; if modules move, the diagrams and doc references must be synchronized.

**Independent Test**: Update `docs/diagrams.rst` (or similar) to mention the new module names and rerun `scripts/render_diagrams.sh` so the published docs show the modular structure.

**Acceptance Scenarios**:

1. **Given** the relocated classes, **When** a reader browses the diagrams or README, **Then** they see `pyArchimate.model`, `pyArchimate.element`, and `pyArchimate.relationship` listed where previously only `pyArchimate.Model` appeared.

---

### Edge Cases

- What happens when a downstream script imports from `src.pyArchimate.pyArchimate` directly instead of the package entry point? Ensure the compatibility layer still exposes the same names.
- How do we validate that splitting modules does not alter default logging or reader registration state embedded in the current file?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST split the core domain classes (`Model`, `Element`, `Relationship`, connection helpers) into dedicated modules within `src/pyArchimate` while keeping behavior identical to the monolithic file.
- **FR-002**: System MUST expose the same public API via `pyArchimate/__init__.py` so `from pyArchimate import Model` continues to work without changes for existing consumers.
- **FR-003**: System MUST ensure readers, writers, and CLI helpers continue to import their dependencies without modification by maintaining single-source references in the shared package namespace.
- **FR-004**: System MUST include module-level unit tests for each new file and update existing tests (unit, integration, examples) to point to the new modules where needed.
- **FR-005**: System MUST document the new module boundaries in the architecture docs (e.g., `docs/diagrams.rst`, README, or inline comments) and regenerate diagrams so documentation matches implementation.
- **FR-006**: System MUST move helper utilities (diagram helpers, property serialization, logging/configuration helpers) into dedicated modules that are re-exported through the package entry point so they remain accessible while staying focused and testable.

### Key Entities *(include if feature involves data)*

- **Model**: Represents an ArchiMate model and coordinates elements, relationships, views, and properties. In the new layout, its orchestration logic lives in `pyArchimate.model` while helpers stay adjacent.
- **Element** / **Relationship**: Domain entities whose constructors, property helpers, and serialization helpers move into their own modules but remain exposed via the package boundary.
- **Diagram helpers**: View helpers, readers, and writers must reference the core entities through clear imports so their dependencies stay satisfied without causing circular imports.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can locate the `Model`, `Element`, and `Relationship` definitions within 3 seconds (per internal documentation) because each class lives in a dedicated file.
- **SC-002**: The full test suite passes (unit, integration, docs) after the refactor without modifying external imports, demonstrating behavioral parity.
- **SC-003**: Documentation (docs/diagrams) lists the new module names and renders updated PNGs from `scripts/render_diagrams.sh` showing the modular structure.
- **SC-004**: CI or local packaging still succeeds (e.g., `poetry check`) meaning the `src` layout and package exports remain valid with the split modules.
- **SC-005**: The package/class diagrams under `docs/diagrams` (e.g., `package.puml`, `class.puml`) explicitly show the new modules/helpers and are regenerated via `scripts/render_diagrams.sh`/`scripts/create_documentation.sh` so published docs match the code layout.

## Assumptions

- Consumers rely on the `pyArchimate` package exports (not the legacy `src.pyArchimate.pyArchimate` path) but we will keep compatibility wrappers for the short term.
- Existing fixtures and integration tests can be updated to import from the new modules without altering their expectations.
- The project continues to use the `src` layout defined in `pyproject.toml`, so new modules must be referenced from there.
- Readers and writers will continue to live in the same package but may adjust their imports to the split modules as needed during the refactor.
