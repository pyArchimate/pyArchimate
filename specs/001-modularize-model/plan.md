# Implementation Plan: Modular Model Modules

**Branch**: `001-modularize-model` | **Date**: 2026-04-07 | **Spec**: `specs/001-modularize-model/spec.md`
**Input**: Feature specification from `/specs/001-modularize-model/spec.md`

## Summary
Split `src/pyArchimate/pyArchimate.py` into purpose-built modules for `Model`, `Element`, `Relationship`, and helper utilities (diagram, property, logging) so each domain concept can be tested and reasoned about independently while keeping the public API (`pyArchimate.Model`, etc.) intact through `pyArchimate/__init__.py` and compatibility wrappers.

## Technical Context
**Language/Version**: Python 3.11 (project targets `>=3.10,<4.0` with tooling tuned to 3.12/3.13).  
**Primary Dependencies**: `lxml`, `oyaml`, `pillow`, `requests`, plus standard pytest/behave/httpx tooling for tests, and Sphinx for docs.  
**Storage**: N/A (in-memory model objects, no persisted database).  
**Testing**: `pytest` (unit/integration/examples), `behave` for BDD scenarios, `ruff`, `pyright`, `mypy` for static checks.  
**Target Platform**: Cross-platform Python library/CLI (Linux / macOS / Windows automation scripts).  
**Project Type**: Library + CLI helpers (pyArchimate exports plus example scripts/CLI entry points).  
**Performance Goals**: Keep core model/read/write helpers below 200 ms where practical; splitting modules must not introduce measurable startup latency or I/O regressions.  
**Constraints**: Must preserve the current `pyArchimate` package exports, avoid circular imports when splitting modules, and keep `src` layout compatible with existing packaging/test tooling.  
**Scale/Scope**: Supports existing Archi, OEF, and ARIS integration pipelines with hundreds of elements per model; change should be contained within the `src/pyArchimate` package and associated tests/docs.

## Constitution Check
I. Code Quality: Breaking `pyArchimate.py` into focused modules aligns with the constitution’s clarity goal and keeps logic self-documenting.  
II. Testing Standards: Each new module will ship dedicated unit tests and the existing integration/examples will verify public APIs.  
VII. System Integrity & Accuracy: Compatibility wrappers and regression smoke tests ensure outputs stay faithful.  
VIII. Durability & Interoperability: Documenting exports and re-exporting helpers protects downstream readers/writers.  
IX. Cross-Platform Consistency: No platform-specific assumptions; docs/scripts are regenerated per project conventions.  
All other principles remain satisfied by adhering to project testing, security, and observability requirements.

## Project Structure
### Documentation (this feature)
```text
specs/001-modularize-model/
├── plan.md              # this file (output of /speckit.plan)
├── research.md          # Phase 0 deliverable (module boundary decisions)
├── data-model.md        # Phase 1 deliverable (entities + helpers)
├── quickstart.md        # Phase 1 deliverable (how to build/test/regenerate docs)
├── contracts/
│   └── pyarchimate-api.md  # Phase 1 deliverable (package export contract)
└── tasks.md             # Phase 2 output (not yet generated)
```

### Source Code (repository root)
```text
src/
└── pyArchimate/
    ├── __init__.py       # re-export module APIs and compatibility helpers
    ├── model.py          # Model orchestration logic
    ├── element.py        # Element constructors, validation, serialization helpers
    ├── relationship.py   # Relationship constructors and helpers
    ├── helpers/
    │   ├── diagram.py    # View/diagram helper utilities
    │   ├── properties.py # Property embedding/expansion, validation helpers
    │   └── logging.py    # Shared logger/configuration helpers
    ├── readers/          # Existing reader adapters (referencing new modules)
    ├── writers/          # Existing writer adapters
    └── cli/              # Example CLI scripts (importing re-exports)
tests/
├── unit/
├── integration/
└── examples/
```
**Structure Decision**: Use the existing `src/pyArchimate` layout, carve `pyArchimate.py` into module files and helper submodules, update `pyArchimate/__init__.py` to expose the same API surface, and leave reader/writer/CLI directories untouched except for import paths.

## Phase 0 Research Deliverables
- `research.md`: Captures module boundary decision (helpers follow dedicated modules re-exported via package entry point) and compatibility requirement.  
- No additional unknowns were flagged; research doc focuses on rationales and alternatives for the helper split.

## Phase 1 Design Deliverables
- `data-model.md`: Documents Model/Element/Relationship entities, helper modules, and their expected relationships/validation rules.  
- `contracts/pyarchimate-api.md`: Declares the package export contract so readers, writers, CLI helpers continue importing `pyArchimate.Model`, `.Element`, `.Relationship`, and helper modules.  
- `quickstart.md`: Lists commands to verify builds/tests/docs after refactor and how to regenerate diagrams via `scripts/render_diagrams.sh`.  
- Agent context update: run `./.specify/scripts/bash/update-agent-context.sh codex` after populating plan fields to keep Codex-specific guidance aligned with this plan.

## Phase 2 Planning
- `tasks.md` will enumerate task breakdown, mapping requirements to steps (split modules, update __init__, rewire tests/docs, update CLI/examples, regenerate docs, verify compatibility).

## Complexity Tracking
No constitution violations anticipated; module split keeps responsibilities aligned with existing principles.
