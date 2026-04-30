# pyArchimate AI Reference

Machine-readable reference for the `pyArchimate` Python library. Intended for AI-assisted tooling,
documentation generation, and developer onboarding. No conversational language.

---

## Summary

A **Python-based engine for creating and manipulating enterprise architecture models using ArchiMate**,
enabling automation, integration, and "architecture-as-code" workflows.

It bridges the gap between **enterprise architecture modeling** and **modern software engineering
practices**, making architecture **scriptable, testable, and version-controlled**.

---

## Overview

**pyArchimate** is a lightweight Python library for **programmatically creating, manipulating,
and persisting enterprise architecture models** using the **ArchiMate standard** (The Open Group).

It acts as an **"Architecture-as-Code" toolkit**, enabling developers and architects to build,
modify, and manage ArchiMate models using Python instead of GUI-based tools.

The library provides a **structured object model aligned with the ArchiMate metamodel**, allowing
users to represent architectural concepts (elements, relationships, views) and serialize them into
standard **ArchiMate XML files**.

---

## Core Purpose

pyArchimate is intended to:

- Automate creation and maintenance of enterprise architecture models
- Enable integration of architecture modelling into **CI/CD pipelines or scripts**
- Provide a programmable alternative to tools like Archi
- Support **model transformation, validation, and generation workflows**
- Facilitate **Architecture-as-Code practices**

---

## Conceptual Model (Metamodel Support)

Key ArchiMate concepts implemented as Python objects:

### Model

Root container for all architectural data. Holds elements, relationships, and views.
Represents the full enterprise architecture.

### View (Diagram)

Visual representation of part of the model. Contains nodes and connections.
Used to communicate architecture to stakeholders.

### Element

Core building blocks (e.g., Business Actor, Application Component).
Represent structural or behavioural concepts.

### Relationship

Defines how elements interact (e.g., association, flow, assignment).

### Node

Visual instance of an element within a view.

### Connection

Visual representation of a relationship between nodes.

---

## Key Features & Functionality

### File Handling & Persistence

- Read existing ArchiMate models from XML
- Write/export models to ArchiMate-compliant XML
- Round-trip editing (load → modify → save)

### Model Creation & Management

- Create models from scratch programmatically
- Define architecture layers and structures
- Maintain centralised architecture repositories in code

### CRUD Operations on Architecture Artefacts

- Create, update, and delete elements, relationships, and views/diagrams
- Enables full lifecycle management of architecture components

### Diagram (View) Management

- Create and manage diagrams programmatically
- Add/remove nodes and connections
- Control layout structure (logical positioning; limited styling)

### Metamodel Compliance

- Enforces ArchiMate structure and relationship rules
- Ensures models remain valid and interoperable

### Separation of Logical vs Visual Layers

- Logical layer: elements and relationships
- Visual layer: nodes and connections in views
- Allows reuse of elements across multiple diagrams

### Automation & Scripting

- Integrate with Python scripts for bulk model generation, migration, and refactoring
- Useful for DevOps pipelines and model synchronization with codebases

### Extensibility

- Python-native; easy to extend or wrap
- Composable with data pipelines, APIs, and other modelling or visualization tools

### Lightweight Design

- Minimal overhead; easy installation (`pip install pyArchimate`)
- Suitable for embedding in larger systems

### Cross-Tool Compatibility

- Outputs standard ArchiMate XML
- Compatible with Archi and other EA platforms supporting ArchiMate

---

## Typical Use Cases

### Architecture-as-Code

Define enterprise architecture in Python, version-control with Git, and automate updates.

### Model Generation

Generate diagrams from infrastructure definitions, cloud configurations,
or microservice architecture inventories.

### Model Transformation

Convert or refactor existing models; apply bulk updates across large architectures.

### DevOps Integration

Embed architecture validation in pipelines; ensure architecture consistency with deployments.

### Analysis & Reporting

Extract relationships and dependencies; build custom analytics or reports on architecture data.

---

## Strengths

- Programmatic control over architecture models
- Strong alignment with ArchiMate standard
- Lightweight and easy to integrate
- Enables automation — a major gap in traditional EA tools

---

## Limitations (Important Context)

- No built-in graphical editor (code-first only)
- Limited layout/styling capabilities compared to GUI tools
- Requires understanding of ArchiMate concepts
- Visualization typically handled by external tools (e.g., Archi)
- Not fully conformant to the complete ArchiMate 3.x specification (see Non-Conformances below)

---

## Non-Conformances

Known deviations from the ArchiMate 3.x standard and Archi tool compatibility gaps.
Sourced from `ArchiToolGap.md` and `Archimategap.md`. Flagged for resolution in future releases.

### ArchiMate 3.x Conformance Gaps

| Gap | Impact |
|-----|--------|
| `BusinessInteraction` not in `checker_rules.yml` | Creating/importing `BusinessInteraction` may fail |
| Viewpoints not first-class; stored as generic `View` | Viewpoint-aware models not fully supported |
| Reader reads `modifier`; writer emits `influenceStrength` | Strength lost on Open Group format round trips |

### Archi Import/Export Compatibility Gaps

| Gap | Impact |
|-----|--------|
| Docs parsed with `e.text` instead of `doc.text` | Relationship docs lost in Archi round trips |
| `bool("false")` always `True` for `nameVisible` | Hidden labels reappear after Archi import |
| Influence strength not symmetric in Archi adapter | Strength differs from expected behaviour |
| Model version hard-coded to `4.9.0` on export | Source document version not preserved |
| Folder taxonomy rebuilt on export | Exact folder structure not round-tripped |
| Only four node kinds recognised; unknown kinds dropped | Non-standard nodes silently lost on import |
