# pyArchimate Architecture Diagrams

This directory contains UML diagrams documenting the modularized architecture of pyArchimate following the **001-modularize-model** feature specification.

## Diagrams

### package.puml
**Module Structure** - Shows how pyArchimate is organized:
- `model.py`, `view.py`, `element.py`, `relationship.py` - Core domain modules
- `helpers/` - Focused utility modules (diagram, properties, logging)
- `readers/`, `writers/` - External format adapters
- `pyArchimate.py` - Package entry point and public API shim

This diagram answers: "What modules exist and how do they connect?"

### class.puml
**Domain Model** - Shows the core data structures:
- `Model` - Root container for elements, relationships, views, and profiles.
- `Element` - Represents an ArchiMate element concept.
- `Relationship` - Represents a connection between concepts (Elements or other Relationships).
- `View`, `Node`, `Connection` - Diagram visualization structures in `view.py`.
- `Profile` - Tagging/specialization metadata for elements and relationships.

This diagram answers: "What classes and data structures does the domain use?"

## Why Modularized?

After modularization, the codebase is better organized:
- **Clean module separation** - Domain logic is decoupled from visualization and IO.
- **Explicit dependencies** - Layers are enforced (e.g., core domain cannot import from readers/writers).
- **Facade pattern** - `pyArchimate.py` provides a stable interface for library consumers.
- **Improved Maintainability** - Clearer boundaries make the system easier to test and extend.

## Rendering

To render diagrams to PNG/SVG, install PlantUML and run:

```bash
plantuml docs/diagrams/package.puml
plantuml docs/diagrams/class.puml
```

Or use the online editor: https://www.plantuml.com/plantuml/uml/

## Key Architectural Properties

✅ **Clean module separation** - Each module has a single responsibility  
✅ **No circular imports** - By design (module dependencies flow one direction)  
✅ **Testable in isolation** - Helpers and readers/writers can be tested independently  
✅ **Backward compatible** - Old import paths continue to work (via `pyArchimate.py`)  

---

**Last Updated**: 2026-04-16  
**Status**: Modularized Production Architecture
