# Feature Specification: Modular Model Modules

**Feature Branch**: `001-modularize-model`  
**Created**: 2026-04-07  
**Status**: Draft (pending remaining implementation)  
**Input**: User description: "Split the gigantic `Model`, `Element`, `Relationship`, and related helpers in `src/pyArchimate/pyArchimate.py` into focused modules (e.g., `model.py`, `element.py`, `relationship.py`). The current single-file implementation mixes domain models, validation rules, reader/writer plumbing, and diagram helpers, which makes the code hard to reason about and test."

## Clarifications

### Outstanding Work (as of 2026-04-11)
- Core modules still import `View`, `Profile`, `Node`, `Connection`, and `_resolve_writer` from `_legacy.py`; these need to be extracted into modern modules so the core is legacy-free.
- Compatibility registration currently calls back into `_legacy` from `element.py` and `relationship.py`; this should be flipped so legacy consumes the new modules without the new modules depending on `_legacy`.
- Once the extractions are complete, update `pyArchimate.py` and exception aliasing to rely on the new modules first, keeping `_legacy` strictly as a fallback layer.

### Session 2026-04-07
- Q: Should helper logic (diagram, property, logging, etc.) live in dedicated helper modules that are re-exported via `pyArchimate/__init__.py`? → A: Yes, to keep helpers testable but still available from the public package surface.
- Q: Should the extraction approach extract classes fully standalone from day 1, or incrementally migrate while tolerating temporary dependencies on legacy code? → A: Standalone from day 1 (full extraction). Model, Element, Relationship will have complete class definitions extracted into their own modules with zero dependencies on _legacy.py.
- Q: Should `pyArchimate.py` remain in the codebase after extraction? → A: Keep pyArchimate.py as compatibility shim. After extraction, pyArchimate.py will be stripped to only re-export the extracted classes (Model, Element, Relationship) and core helpers. Readers/writers can still import from it for backward compatibility.
- Q: What is the preferred structure for helpers—flat directory with focused submodules or nested subdirectories? → A: Flat helpers directory. Create `pyArchimate/helpers/` with focused submodules (`diagram.py`, `serialization.py`, `logging.py`) re-exported via `helpers/__init__.py` and main `__init__.py`.
- Q: What architectural layering should enforce dependency acyclicity and module coherence? → A: Core-first layering (strict acyclicity). Establishes 4 dependency layers: Layer 1 (Base): Constants, enums, exceptions—no pyArchimate imports. Layer 2 (Core Domain): model.py, element.py, relationship.py—import only from Layer 1. Layer 3 (Helpers): helpers/*—import from Layers 1 & 2. Layer 4 (Readers/Writers): Can import from Layers 1, 2, 3.
- Q: How long should backward compatibility with direct imports from `src.pyArchimate.pyArchimate` be maintained? → A: B - Permanent compatibility layer. _legacy.py will be maintained indefinitely and direct imports from src.pyArchimate.pyArchimate will continue to be supported through re-exports.

## Implementation Architecture

### Overview

Based on the six architectural clarifications above, the refactoring follows a **Core-first layering model** with **permanent backward compatibility**. This section synthesizes those decisions into a cohesive implementation strategy, visual dependencies, import patterns, and acceptance criteria.

### Architectural Decision Summary

| Decision | Answer | Rationale |
|----------|--------|-----------|
| **Module Extraction Depth** | Standalone from day 1 (full extraction) | Zero dependencies on legacy code ensures clean module boundaries and testability; eliminates intermediate bridging costs |
| **Entry Point Structure** | pyArchimate.py remains as compatibility shim | Readers, writers, and existing consumers continue to import from the public package without modification |
| **Helper Organization** | Flat `helpers/` directory with focused submodules | Keeps helpers testable, avoids nesting complexity, and simplifies re-export from main `__init__.py` |
| **Dependency Layers** | 4-layer core-first acyclic model | Strict layering prevents circular imports and enforces clear upstream/downstream relationships |
| **Backward Compatibility** | Permanent compatibility layer via `_legacy.py` | Long-term stability for downstream automation pipelines; existing direct imports from `src.pyArchimate.pyArchimate` remain valid indefinitely |

### 4-Layer Dependency Model

```
┌──────────────────────────────────────────────────────────────────┐
│ Layer 4: Readers / Writers / Adapters / CLI                      │
│ (Can import from Layers 1, 2, 3)                                 │
│  └─ readers/, writers/, adapters, cli modules                    │
└──────────────────────────────────────────────────────────────────┘
                                ↑
┌──────────────────────────────────────────────────────────────────┐
│ Layer 3: Helpers                                                  │
│ (Can import from Layers 1, 2)                                    │
│  ├─ helpers/diagram.py (view helpers, visualization)             │
│  ├─ helpers/serialization.py (property serialization)            │
│  └─ helpers/logging.py (logging & configuration)                 │
└──────────────────────────────────────────────────────────────────┘
                                ↑
┌──────────────────────────────────────────────────────────────────┐
│ Layer 2: Core Domain                                              │
│ (Can import from Layer 1 only)                                   │
│  ├─ model.py (Model class orchestrating domain logic)            │
│  ├─ element.py (Element class & lifecycle)                       │
│  └─ relationship.py (Relationship class & constraints)           │
└──────────────────────────────────────────────────────────────────┘
                                ↑
┌──────────────────────────────────────────────────────────────────┐
│ Layer 1: Base                                                     │
│ (No pyArchimate imports; stdlib/external only)                   │
│  ├─ constants.py (global constants, magic numbers)               │
│  ├─ enums.py (enumerations, static types)                        │
│  └─ exceptions.py (exception hierarchy)                          │
└──────────────────────────────────────────────────────────────────┘
```

### File Structure

```
src/pyArchimate/
├── pyArchimate/
│   ├── __init__.py              # Main entry point; re-exports Model, Element, Relationship, helpers
│   ├── _legacy.py               # Permanent compatibility layer; re-exports all extracted classes
│   │                            # Supports legacy direct imports: from src.pyArchimate.pyArchimate import Model
│   │
│   ├── constants.py             # (Layer 1) Global constants, enums, exceptions
│   ├── enums.py
│   ├── exceptions.py
│   │
│   ├── model.py                 # (Layer 2) Model class orchestrating core domain
│   ├── element.py               # (Layer 2) Element class definition & lifecycle
│   ├── relationship.py          # (Layer 2) Relationship class & constraint logic
│   │
│   ├── helpers/                 # (Layer 3) Focused helper submodules
│   │   ├── __init__.py          # Re-exports diagram, serialization, logging helpers
│   │   ├── diagram.py           # View/visualization helpers
│   │   ├── serialization.py     # Property serialization utilities
│   │   └── logging.py           # Logging & configuration setup
│   │
│   ├── readers/                 # (Layer 4) Import adapters for ArchiMate, XML, etc.
│   │   ├── __init__.py
│   │   ├── archimate_reader.py
│   │   └── ...
│   │
│   └── writers/                 # (Layer 4) Export adapters
│       ├── __init__.py
│       ├── archimate_writer.py
│       └── ...
```

### Import Patterns & Public API

#### Current Consumers (e.g., readers, writers, CLI)

**Recommended pattern (new modules)**:
```python
# Import core domain classes directly from main package (preferred for new code)
from pyArchimate import Model, Element, Relationship
from pyArchimate.helpers import diagram, serialization, logging

# Or explicitly from modules (acceptable for clarity in large files)
from pyArchimate.model import Model
from pyArchimate.element import Element
from pyArchimate.helpers.diagram import visualize_view
```

#### Legacy Consumers (backward compatibility)

**Direct module import (still supported indefinitely)**:
```python
# Old pattern: direct import from legacy module (via _legacy.py re-export)
from src.pyArchimate.pyArchimate import Model, Element, Relationship

# This continues to work because pyArchimate.py acts as a compat shim
# and _legacy.py re-exports all extracted names.
```

#### Package Entry Point (`pyArchimate/__init__.py`)

The main `__init__.py` consolidates all public exports:
```python
# Core domain
from pyArchimate.model import Model
from pyArchimate.element import Element
from pyArchimate.relationship import Relationship

# Helpers (make testable submodules available under pyArchimate.helpers)
from pyArchimate import helpers
from pyArchimate.helpers import diagram, serialization, logging

# Constants, enums, exceptions
from pyArchimate.constants import *
from pyArchimate.enums import *
from pyArchimate.exceptions import *

__all__ = [
    'Model', 'Element', 'Relationship',
    'helpers', 'diagram', 'serialization', 'logging',
    # Constants, enums, exceptions as needed
]
```

#### Compatibility Shim (`pyArchimate.py`)

After extraction, `pyArchimate.py` becomes a re-export module:
```python
# Stripped version: re-exports only extracted classes
from pyArchimate.model import Model
from pyArchimate.element import Element
from pyArchimate.relationship import Relationship
from pyArchimate.helpers import diagram, serialization, logging

__all__ = ['Model', 'Element', 'Relationship', 'diagram', 'serialization', 'logging']
```

#### Legacy Compatibility Layer (`_legacy.py`)

A permanent re-export layer for old direct imports:
```python
# Supports: from src.pyArchimate.pyArchimate import Model, Element, Relationship
# This file is maintained indefinitely for downstream automation pipelines.
from pyArchimate.model import Model
from pyArchimate.element import Element
from pyArchimate.relationship import Relationship
from pyArchimate.helpers import diagram, serialization, logging

__all__ = ['Model', 'Element', 'Relationship', 'diagram', 'serialization', 'logging']
```

### Dependency Rules & Validation

Each layer has strict import constraints:

| Layer | Can Import From | Examples |
|-------|-----------------|----------|
| **Layer 1: Base** | Only stdlib/external deps | `import enum`, `from typing import ...` |
| **Layer 2: Core Domain** | Layer 1 + own module | `from pyArchimate.enums import ElementType` |
| **Layer 3: Helpers** | Layers 1, 2 + own module | `from pyArchimate.model import Model` + own submodule |
| **Layer 4: Readers/Writers** | Any layer (1, 2, 3) | `from pyArchimate import Model`, `from pyArchimate.helpers.diagram import ...` |

**Validation methods**:
- **Static analysis**: Use `grep` / `ast` to scan each module for disallowed imports (e.g., Layer 2 importing Layer 3).
- **Import tracking**: Maintain or auto-generate a dependency matrix showing which modules import which.
- **CI checks**: Fail the build if a module imports from a prohibited layer.

### No Circular Imports Guarantee

By construction:
- Layer 1 has no pyArchimate imports → cannot circularly depend on anything.
- Layer 2 imports only Layer 1 → cannot circularly depend on Layers 3–4.
- Layer 3 imports only Layers 1–2 → cannot circularly depend on Layer 4.
- Layer 4 imports Layers 1–3 → may have internal cycles, but those are isolated to adapters.

Validation: A static analysis check (e.g., `python -c "import pyArchimate"`) confirms successful import without import errors.

### Acceptance Criteria for Architectural Validation

The refactoring is **complete and correct** when:

| Criterion | Validation Method | Pass Condition |
|-----------|-------------------|----------------|
| **AC-001: Module Extraction** | `python -c "from pyArchimate import Model, Element, Relationship"` succeeds | All three classes import and instantiate without errors |
| **AC-002: No Legacy Dependencies** | Scan `model.py`, `element.py`, `relationship.py` for imports of `_legacy` | Zero matches; no class imports legacy code |
| **AC-003: Helpers Isolation** | `python -c "from pyArchimate.helpers import diagram, serialization, logging"` succeeds; all are testable standalone | Each helper module is importable independently and runs its own tests |
| **AC-004: Layer Acyclicity** | Static analysis tool (e.g., custom script or `graphviz` dependency check) verifies no cycles | Dependency graph is a DAG (directed acyclic graph); report confirms 0 cycles |
| **AC-005: Entry Point Exports** | `python -c "from pyArchimate import Model; from pyArchimate.helpers import diagram"` both succeed | Public API re-exports match original interface; no import errors |
| **AC-006: Backward Compatibility** | Old imports still work: `from src.pyArchimate.pyArchimate import Model` | Legacy path resolves successfully; _legacy.py and pyArchimate.py re-exports are intact |
| **AC-007: Test Parity** | Full test suite passes (unit, integration, docs) without modifying test imports | All tests pass; behavioral output matches pre-refactor baseline |
| **AC-008: No Broken Readers/Writers** | Run integration tests for all readers (ArchiMate, XML, etc.) and writers | Read/save cycles work end-to-end; models load and serialize identically |
| **AC-009: Documentation Sync** | Diagrams in `docs/diagrams.rst` and `scripts/render_diagrams.sh` outputs match code layout | Published diagrams list the new modules (model, element, relationship, helpers) |
| **AC-010: Linting & Type Checks** | Run `mypy`, `pylint`, `black` on refactored code | All checks pass; no type errors, formatting issues, or style violations |

### Implementation Phases (Recommended)

1. **Phase 1: Extract Base Layer (constants.py, enums.py, exceptions.py)**
   - Move all enum, constant, and exception definitions into Layer 1.
   - Acceptance: Layer 1 modules import successfully with zero circular dependencies.

2. **Phase 2: Extract Core Domain (model.py, element.py, relationship.py)**
   - Extract each class with complete definition; no legacy dependencies.
   - Acceptance: Layer 2 modules import Layer 1 cleanly; AC-002 passes.

3. **Phase 3: Refactor Helpers (diagram.py, serialization.py, logging.py)**
   - Move helper logic into focused submodules under `helpers/`.
   - Acceptance: AC-003 passes; helpers are independently testable.

4. **Phase 4: Build Entry Points & Compatibility Layer**
   - Create/update `__init__.py`, `pyArchimate.py`, and `_legacy.py` for re-exports.
   - Acceptance: AC-005 and AC-006 pass; both modern and legacy imports work.

5. **Phase 5: Validation & Testing**
   - Validate acyclicity (AC-004), test parity (AC-007), and readers/writers (AC-008).
   - Update documentation to match new layout (AC-009).
   - Acceptance: AC-001 through AC-010 all pass.

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

- **Downstream legacy imports**: What happens when a downstream script imports from `src.pyArchimate.pyArchimate` directly instead of the package entry point? **Answer**: The permanent compatibility layer (`_legacy.py` and `pyArchimate.py` shim) ensures all names are re-exported and resolves successfully. **Validation**: AC-006 confirms legacy import paths still work.
- **State persistence across modularization**: How do we validate that splitting modules does not alter default logging or reader registration state that was embedded in the original monolithic file? **Answer**: Test fixtures must verify that logging levels, reader registry, and writer registry have identical state before/after refactoring. **Validation**: Add test to `tests/integration/test_state_preservation.py` that imports both old and new code paths and compares logging/registry state.

## Requirements *(mandatory)*

### Architectural Layering (Dependency & Acyclicity)

The refactored `pyArchimate` package enforces **Core-first layering** with strict acyclicity to prevent circular dependencies and maintain clear separation of concerns:

| Layer | Modules | Permitted Imports From |
|-------|---------|------------------------|
| **Layer 1: Base** | `constants.py`, `enums.py`, `exceptions.py` | No pyArchimate imports (only stdlib/external) |
| **Layer 2: Core Domain** | `model.py`, `element.py`, `relationship.py` | Layer 1 only |
| **Layer 3: Helpers** | `helpers/diagram.py`, `helpers/serialization.py`, `helpers/logging.py` | Layers 1 & 2 |
| **Layer 4: Readers/Writers** | `readers/`, `writers/`, adapters, CLI | Layers 1, 2, 3 (may import from any layer) |

This structure ensures:
- **No circular imports**: A module in Layer N never imports from Layer N+1.
- **Clear dependency flow**: Lower layers are always upstream; higher layers consume downstreams.
- **Testability**: Layer 2 can be unit-tested in isolation; Layers 3–4 test against concrete Layer 1/2 implementations.
- **Maintainability**: Adding new helpers or readers does not require modifying core domain modules.

### Functional Requirements

- **FR-001**: System MUST extract `Model`, `Element`, and `Relationship` as standalone modules with zero dependencies on legacy code (no _legacy.py imports). Each class must have its complete definition in its own module.
- **FR-002**: System MUST expose the same public API via `pyArchimate/__init__.py` so `from pyArchimate import Model` continues to work without changes for existing consumers.
- **FR-003**: System MUST ensure readers, writers, and CLI helpers continue to import their dependencies without modification by maintaining single-source references in the shared package namespace.
- **FR-004**: System MUST include module-level unit tests for each new file and update existing tests (unit, integration, examples) to point to the new modules where needed.
- **FR-005**: System MUST document the new module boundaries in the architecture docs (e.g., `docs/diagrams.rst`, README, or inline comments) and regenerate diagrams so documentation matches implementation.
- **FR-006**: System MUST move helper utilities (diagram helpers, property serialization, logging/configuration helpers) into a flat `pyArchimate/helpers/` directory with focused submodules (`diagram.py`, `serialization.py`, `logging.py`) re-exported through `helpers/__init__.py` and the main package entry point so they remain accessible while staying focused and testable.

### Key Entities *(include if feature involves data)*

- **Model**: Represents an ArchiMate model and coordinates elements, relationships, views, and properties. In the new layout, its orchestration logic lives in `pyArchimate.model` while helpers stay adjacent.
- **Element** / **Relationship**: Domain entities whose constructors, property helpers, and serialization helpers move into their own modules but remain exposed via the package boundary.
- **Diagram helpers**: View helpers, readers, and writers must reference the core entities through clear imports so their dependencies stay satisfied without causing circular imports.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can locate the `Model`, `Element`, and `Relationship` definitions within 3 seconds (per internal documentation) because each class lives in a dedicated file.
- **SC-002**: The full test suite passes (unit, integration, docs) after the refactor without modifying external imports, demonstrating behavioral parity.
- **SC-003**: Architecture diagrams in `docs/diagrams/` (e.g., `package.puml`, `class.puml`) explicitly show the new modules and their structure, making the modular architecture immediately obvious to new developers.
- **SC-004**: CI or local packaging still succeeds (e.g., `poetry check`) meaning the `src` layout and package exports remain valid with the split modules.
- **SC-005**: Documentation (docs/diagrams.rst, rendered diagrams, README) lists the new module names and shows the simplified modular structure compared to the monolithic original.

## Assumptions

- Consumers rely on the `pyArchimate` package exports (not the legacy `src.pyArchimate.pyArchimate` path) but we will keep compatibility wrappers for the short term.
- Existing fixtures and integration tests can be updated to import from the new modules without altering their expectations.
- The project continues to use the `src` layout defined in `pyproject.toml`, so new modules must be referenced from there.
- **Readers and writers do NOT require import modifications**. Per FR-003, they continue to import from the public package entry point (`pyArchimate/__init__.py`) without any code changes needed. The compatibility layers (`__init__.py` and `pyArchimate.py` shim) ensure that `from pyArchimate import Model` continues to work.
