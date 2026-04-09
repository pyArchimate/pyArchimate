# Project Principles for pyArchimate

This document augments the Core Principles in `.specify/memory/constitution.md` with project‑specific expectations that keep development grounded in what matters for pyArchimate: a focused Archimate modelling library with stable output, precise documentation, and a predictable release workflow.

## Constitution Additions

### I. Modularize the Core Model

pyArchimate’s central value proposition is the `Model`, `Element`, `Relationship`, and view helpers. They must live in focused modules with no hidden global state so refactors and tests can reason about each concept in isolation.

- **Rules**: Split the current `pyArchimate.py` into targeted modules (`model.py`, `element.py`, `relationship.py`, etc.), encapsulate helper state/dictionaries, and re-export the API via `pyArchimate/__init__.py` so readers, writers, and scripts keep working. Every refactor should ship a focused test or well-documented example showing the new module boundaries.
- **Rationale**: Modular core logic is easier to reason about, improves testability, and limits the regression surface when reader/writer behaviors change, preserving trust for automations and CLI consumers.

### II. Treat documentation and diagrams as living code

The PlantUML assets under `docs/diagrams` mirror the architecture, so they must stay accurate as the code evolves.

- **Rules**: Regenerate diagrams with `scripts/render_diagrams.sh` whenever the architecture changes, keep the PNG outputs under version control, and describe new diagrams in `docs/diagrams.rst`. Always run `scripts/create_documentation.sh` before publishing so the generated site matches the code.
- **Rationale**: High‑quality visuals and docs lower onboarding friction, help reviewers understand refactors (especially around readers/writers), and keep the project trustworthy for integrators who depend on the ArchiMate model semantics.
