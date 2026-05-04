# Implementation Plan: Restructure Sphinx Documentation

**Branch**: `010-restructure-sphinx-docs` | **Date**: 2026-05-03 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/010-restructure-sphinx-docs/spec.md`

## Summary

Restructure the pyArchimate Sphinx documentation from a flat module dump into a three-tier navigation site (Basic / Intermediate / Advanced) that lets new users start in under 2 minutes, intermediate users understand the architecture, and advanced users access the full API reference. The approach wires the existing `docs/tutorial/tutorial.md` into Sphinx via `myst-parser`, recreates deleted guide/example pages, fixes all broken cross-references, and rewrites `index.rst` with three clearly labelled `toctree` sections. Additionally, update all architecture PlantUML diagrams to reflect the current library state.

## Technical Context

**Language/Version**: Python 3.10+ (pyproject.toml `requires-python = ">=3.10,<4.0"`)  
**Primary Dependencies**: Sphinx ≥9.1, sphinx-rtd-theme ≥3.1 (declared in pyproject.toml extras); `myst-parser` to be added  
**Storage**: File I/O only — `.rst` / `.md` documentation sources, PNG diagrams already under version control  
**Testing**: Sphinx build (`make html`) — zero warnings/errors is the pass criterion  
**Target Platform**: Read the Docs (HTML build); locally runnable via `make html` in `docs/`  
**Project Type**: Documentation restructure for an existing Python library  
**Performance Goals**: `make html` completes without error; `make clean html` <60 s  
**Constraints**: Preserve existing Sphinx config, theme, and deployment pipeline; no changes to source Python code  
**Scale/Scope**: ~20 existing RST files; 15 files to create or modify; 1 new dependency (`myst-parser`); 15 PlantUML diagrams to audit/update

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|-----------|-------|
| I. Code Quality | ✅ PASS | Documentation-only change; no production Python modified |
| II. Testing Standards | ✅ PASS | Verification is Sphinx build + zero-warning gate |
| III. UX Consistency | ✅ PASS | Three-tier nav matches FR-001; consistent visual labels |
| IV. Performance | ✅ PASS | Build time not a concern; `make html` is build-time only |
| V. Security | ✅ PASS | No code or credentials involved |
| VI. State Management | N/A | No state machines involved |
| VII. System Integrity | ✅ PASS | All code examples drawn from current API; round-trip notes preserved |
| VIII. Durability | ✅ PASS | Existing rst shim pages and `pyArchimate.rst` kept unchanged |
| IX. Cross-Platform | ✅ PASS | RTD theme is fully cross-platform; WCAG 2.1 AA by theme + plan |
| Project: Docs as living code | ✅ PASS | diagrams.rst included verbatim in new architecture.rst; PlantUML diagrams updated |

**Decision**: No violations. Proceed.

## Project Structure

### Documentation (this feature)

```text
specs/010-restructure-sphinx-docs/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code Changes (docs/ only)

```text
docs/
├── conf.py                          # MODIFY: add myst_parser + source_suffix
├── requirements.txt                 # MODIFY: add myst-parser
├── index.rst                        # REWRITE: three-tier toctree structure
│
├── getting-started.rst              # CREATE: FR-002 — install + working example
├── concepts.rst                     # CREATE: FR-006 — domain concepts
├── architecture.rst                 # CREATE: FR-003 — package→responsibility table
│
├── guides/
│   ├── element-hierarchy.rst        # RECREATE: fix broken ref from api/model.rst
│   ├── visual-styling.rst           # RECREATE: fix broken ref from api/element.rst
│   ├── junction-types.rst           # RECREATE: fix broken ref from api/element.rst
│   └── extending.rst                # CREATE: FR-004 — custom readers/writers
│
├── examples/
│   ├── hierarchy_examples.rst       # RECREATE: fix broken ref from api/model.rst
│   └── styling_examples.rst         # RECREATE: fix broken ref from api/element.rst
│
├── api/
│   ├── element.rst                  # MODIFY: Add "New to this topic?" note (FR-005)
│   ├── model.rst                    # MODIFY: Add "New to this topic?" note (FR-005)
│   └── viewpoints.rst               # CREATE: FR-005 gap — viewpoint API
│
├── hierarchy-styling-overview.rst   # CREATE: compat stub
│
├── diagrams/                        # AUDIT & UPDATE (NEW PHASE)
│   ├── *.puml files                 # REVIEW: verify against current source
│   └── *.png files                  # REGENERATE: via scripts/render_diagrams.sh
│
└── tutorial/tutorial.md             # EXISTING — no change needed
```

**Structure Decision**: Documentation is restructured into three tiers (Basic/Intermediate/Advanced) per spec. PlantUML diagrams are audited and regenerated to reflect current library architecture.

---

## Phase 0: Research

*See [research.md](./research.md)*

Key decisions resolved:

1. **myst-parser vs RST conversion** → Use `myst-parser`
2. **tutorial inclusion method** → Add `myst_parser` to `conf.py` + `source_suffix` mapping
3. **pyproject.toml dependency** → `myst-parser` added to docs optional-dependency group
4. **p3-quick-reference** → Recreate as functional stub (`hierarchy-styling-overview.rst`)
5. **diagrams.rst fate** → Keep intact; include in `architecture.rst`
6. **api/element.rst and api/model.rst** → Modify to add "New to this topic?" notes (FR-005 enhancement)
7. **viewpoints documentation** → Create `api/viewpoints.rst`
8. **PlantUML diagram updates** → Audit current diagrams; regenerate to match library state

---

## Phase 1: Design

### Data Model

*See [data-model.md](./data-model.md)*

Documentation pages and diagrams are modeled as entities with tier, status, primary FR, and dependencies.

### PlantUML Diagrams Audit

**Current diagrams in `docs/diagrams/`**:
- `context.puml` / `c4_context.puml` — System context
- `package.puml` / `c4_container.puml` — Container/package structure
- `component.puml` / `c4_component.puml` — Component relationships
- `deployment.puml` / `c4_deployment.puml` — Deployment architecture
- `class.puml` — Class structure
- `object.puml` — Instance/object diagram
- `composite.puml` — Composite structure
- `state.puml` — State machine
- `sequence.puml` — Interaction sequence
- `activity.puml` — Activity flow
- `communication.puml` — Communication diagram

**Audit scope**: Verify each diagram accurately represents:
1. Current module boundaries (readers, writers, model, helpers, etc.)
2. Public API classes and relationships
3. Data flow and dependencies
4. Extension points (custom readers/writers)

**Regeneration**: Run `scripts/render_diagrams.sh` to produce updated PNGs.

---

## Phase 2: Implementation Sequence

Execute in this order:

**Documentation Restructuring (Phases 1–2 of tasks.md)**:
1. T001–T004: Setup dependencies (myst-parser)
2. T005–T007: Rewrite index.rst
3. T008–T040: Create/modify documentation pages (3 tiers)

**PlantUML Diagram Updates (New Phase — after doc structure is complete)**:
4. **Phase 7: Diagram Audit & Regeneration**
   - Audit each PlantUML source against current source code
   - Update `.puml` files to reflect current architecture
   - Run render script to regenerate `.png` files
   - Verify generated diagrams in `docs/_build/html/`

---

## Verification

```bash
# Install myst-parser (if not already)
pip install myst-parser

# Full clean build — target: zero warnings, zero errors
cd /Users/xavier/PycharmProjects/pyArchimate/docs
make clean html 2>&1 | grep -E "WARNING|ERROR|error" \
  | grep -v "duplicate.*pyarchimate"
# Expected output: (empty)

# Verify PlantUML diagrams rendered
ls -la docs/diagrams/*.png
# Should show all 15 PNG files with recent timestamps

# Quick rebuild during development
make html 2>&1 | grep -i "warning\|error" | grep -v "duplicate.*pyarchimate"
```

Success criteria:
- `make clean html` exits 0
- Zero `document isn't included in any toctree` warnings
- Zero broken `:doc:` or `:ref:` reference warnings
- All PlantUML `.png` files present and up-to-date
- `docs/_build/html/architecture.html` displays diagrams correctly
