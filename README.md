# pyArchimate package

[![test](https://github.com/pyArchimate/pyArchimate/actions/workflows/ci.yml/badge.svg)](https://github.com/pyArchimate/pyArchimate/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/pyArchimate/pyArchimate/graph/badge.svg?token=H7728VH5TG)](https://codecov.io/gh/pyArchimate/pyArchimate)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Release](https://github.com/pyArchimate/pyArchimate/actions/workflows/release.yml/badge.svg)](https://github.com/pyArchimate/pyArchimate/actions/workflows/release.yml) [PyPI release](https://pypi.org/project/pyArchimate/)

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
| ARIS AML | yes | — |
| CSV | — | yes |

## Key operations

- **Read / Write / Merge** — load one or more files and save to any supported format
- **Create & modify** — add elements, relationships, and views via the API without touching a file
- **Filter** — extract subsets of elements, relationships, or views by custom predicates
- **Style** — set colours, coordinates, dimensions, and text layout on nodes
- **Validate** — check for broken references and invalid connections

## Limitations

- No GUI, no diagram renderer
- No write support for ARIS AML
- Not designed for interactive or real-time use — batch/scripting oriented

## Metamodel

![](docs/metaModel.png)
