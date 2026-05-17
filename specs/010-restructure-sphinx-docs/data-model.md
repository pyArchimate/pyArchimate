# Data Model: Restructure Sphinx Documentation

**Feature**: 010-restructure-sphinx-docs  
**Date**: 2026-05-03

## Documentation Page Entities

Each documentation page is modelled as an entity with: tier, status, primary FR, and dependencies.

| Page | Tier | Status | Primary FR | Depends On |
|------|------|--------|-----------|------------|
| `index.rst` | All | Rewrite | FR-001, FR-007, FR-008 | All pages below |
| `getting-started.rst` | Basic | Create | FR-002 | tutorial/tutorial.md |
| `tutorial/tutorial.md` | Basic | Wire up (myst-parser) | FR-002, FR-006 | conf.py myst-parser |
| `concepts.rst` | Intermediate | Create | FR-006 | api/viewpoints.rst |
| `architecture.rst` | Intermediate | Create | FR-003 | diagrams.rst (include) |
| `guides/element-hierarchy.rst` | Intermediate | Recreate | FR-001, FR-005 | api/model.rst |
| `guides/visual-styling.rst` | Intermediate | Recreate | FR-001, FR-005 | api/element.rst |
| `guides/junction-types.rst` | Intermediate | Recreate | FR-001, FR-005 | api/element.rst |
| `guides/extending.rst` | Intermediate | Create | FR-004 | — |
| `examples/hierarchy_examples.rst` | Intermediate | Recreate | FR-009 | guides/element-hierarchy.rst |
| `examples/styling_examples.rst` | Intermediate | Recreate | FR-009 | guides/visual-styling.rst |
| `api/element.rst` | Advanced | Existing | FR-005 | guides/*, examples/* |
| `api/model.rst` | Advanced | Existing | FR-005 | guides/*, examples/* |
| `api/viewpoints.rst` | Advanced | Create | FR-005 | — |
| `modules.rst` | Advanced | Existing | FR-005 | — |
| `p3-quick-reference.rst` | Hidden | Create | FR-007 (compat) | — |

## Tier Definitions

| Tier | Audience | Entry Point | Navigation Label |
|------|----------|-------------|-----------------|
| Basic | New Python developers unfamiliar with ArchiMate | `getting-started.rst` | "Basic Usage" |
| Intermediate | Developers wanting to extend or integrate pyArchimate | `concepts.rst` | "Intermediate / Architecture" |
| Advanced | Contributors, maintainers, power users | `api/element.rst` | "Advanced / API Reference" |

## Validation Rules

- Every page listed in a `toctree` MUST exist as a file
- No `document isn't included in any toctree` warnings allowed
- All `:doc:` cross-references MUST resolve
- All code examples MUST use the current public API (no deprecated methods)
- `myst-parser` MUST be declared in both `docs/requirements.txt` and `pyproject.toml` docs group

## State Transitions

Pages follow a simple lifecycle:

```
MISSING → CREATED → IN_TOCTREE → BUILD_PASSES
```

All pages must reach `BUILD_PASSES` before the feature is complete.
