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
