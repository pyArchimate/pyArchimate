# pyArchimate package

[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/pyArchimate.svg)](https://pypi.org/project/pyArchimate/)
[![codecov](https://codecov.io/gh/pyArchimate/pyArchimate/graph/badge.svg?token=H7728VH5TG)](https://codecov.io/gh/pyArchimate/pyArchimate)
[![test](https://github.com/pyArchimate/pyArchimate/actions/workflows/ci.yml/badge.svg)](https://github.com/pyArchimate/pyArchimate/actions/workflows/ci.yml)
[![Release](https://github.com/pyArchimate/pyArchimate/actions/workflows/release.yml/badge.svg)](https://github.com/pyArchimate/pyArchimate/actions/workflows/release.yml)

[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=pyArchimate_pyArchimate&metric=alert_status)](https://sonarcloud.io/project/overview?id=pyArchimate_pyArchimate)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=pyArchimate_pyArchimate&metric=bugs)](https://sonarcloud.io/project/overview?id=pyArchimate_pyArchimate)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=pyArchimate_pyArchimate&metric=security_rating)](https://sonarcloud.io/project/overview?id=pyArchimate_pyArchimate)
[![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=pyArchimate_pyArchimate&metric=sqale_rating)](https://sonarcloud.io/project/overview?id=pyArchimate_pyArchimate)
[![Docs](https://readthedocs.org/projects/pyarchimate/badge/?version=latest)](https://pyarchimate.readthedocs.io)

Documentation: [readthedocs.org](https://pyarchimate.readthedocs.io)

pyArchimate is a Python library for programmatically reading, writing, and manipulating [Open Group ArchiMate](https://www.opengroup.org/xsd/archimate/) enterprise architecture models. It has no GUI — it is purely a file I/O and object model library designed for batch and scripting use.

## Core concepts

| Object | What it represents |
|---|---|
| `Model` | Top-level container for everything |
| `Element` | An architectural concept (business process, application, server, capability…) |
| `Relationship` | A typed link between two elements (Association, Realization, Composition, Flow…) |
| `View` | A diagram — a named subset of elements/relationships laid out visually |
| `Node` | The visual box representing an element inside a view |
| `Connection` | The visual arrow representing a relationship inside a view |

Elements span the full ArchiMate 3 layer stack: **Strategy, Motivation, Business, Application, Technology, Physical, and Implementation**.

## Supported formats

| Format | Read | Write |
|---|---|---|
| ArchiMate Open Exchange XML | yes | yes |
| Archi tool format (.archimate) | yes | yes |
| CSV | — | yes |

## Key operations

- **Read / Write / Merge** — load one or more files and save to any supported format
- **Create & modify** — add elements, relationships, and views via the API without touching a file
- **Filter** — extract subsets of elements, relationships, or views by custom predicates
- **Style** — set colours, coordinates, dimensions, and text layout on nodes
- **Validate** — check for broken references and invalid connections
- **Auto-Layout** — automatically arrange view elements using force-directed or hierarchical algorithms
- **Auto-Format** — standardize element sizes, fonts, and alignment per ArchiMate conventions
- **SVG Export** — render views as self-contained SVG with ArchiMate symbols and standard colors

## Auto-Layout and Auto-Format (BETA)

⚠️ **Status**: BETA — Core functionality is stable and production-ready for typical use cases. API may evolve based on user feedback.

### Quick Start

```python
from pyArchimate.view import load_view, save_view
from pyArchimate.view.layout import apply_layout, apply_format, LayoutConfig

# Load a view
view = load_view("architecture.archimate")

# Apply automatic layout
result = apply_layout(view)

# Or apply formatting only (without repositioning)
result = apply_format(view)

# Export as SVG
svg = view.to_svg(filepath="diagram.svg")

# Save the laid-out view
save_view(view, "laid_out.archimate")
```

### Features

- **Two layout algorithms**: Force-directed (general-purpose) and hierarchical (organizational structures)
- **Respect ArchiMate layers**: Business → Application → Technology ordering enforced
- **Connection routing**: Orthogonal polylines with intelligent label placement
- **SVG export**: Self-contained SVG with all 30+ ArchiMate element types and standard colors
- **Undo/rollback**: Revert layout changes with `undo_layout(view)`
- **Configuration**: Customize spacing, margins, alignment, element exclusion, and routing style

### Performance

| View Size | Force-Directed | Hierarchical |
|-----------|----------------|--------------|
| 100 elements | <200ms | <50ms |
| 300 elements | <2s | <500ms |
| 500 elements | <5s | <1s |

### Learn More

- [Auto-Layout Quickstart Guide](specs/011-view-auto-layout/quickstart.md)
- [Technical Specifications](specs/011-view-auto-layout/auto-layout-specifications.md)
- [API Reference](specs/011-view-auto-layout/contracts/layout-api.md)

## Limitations

- No GUI, no diagram renderer
- Not designed for interactive or real-time use — batch/scripting oriented

## Documentation

- [AI.md](AI.md) — machine-readable reference for AI-assisted tooling and developer onboarding
- [Tutorial](docs/tutorial/tutorial.md) — step-by-step guide for new users with runnable code examples

## ArchiMate v3.x Compliance

pyArchimate now supports ArchiMate 3.x specification compliance with the following features:

### Supported Features

- ✅ **BusinessInteraction elements**: Full support for creating, importing, and exporting BusinessInteraction elements
- ✅ **Influence strength metadata**: Complete round-trip preservation of influence relationship strength (both `.archimate` and OpenGroup formats)
- ✅ **Relationship documentation**: Full preservation of relationship documentation/description text during import and export

### Known Gaps

See [Gap Analysis Documentation](docs/archimate-gaps.md) for detailed analysis of specification alignment and areas for future enhancement (P2/P3).

## Metamodel

![](docs/metaModel.png)
