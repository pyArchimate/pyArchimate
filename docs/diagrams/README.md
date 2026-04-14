# pyArchimate Architecture Diagrams

This directory contains UML diagrams documenting the modularized architecture of pyArchimate following the **001-modularize-model** feature specification.

## Diagrams

### package.puml
**Module Structure** - Shows how pyArchimate is organized:
- `model.py`, `element.py`, `relationship.py` - Core domain classes
- `helpers/` - Focused utility modules (diagram, properties, logging)
- `readers/`, `writers/` - External format adapters
- `__init__.py` - Package entry point that re-exports public API

This diagram answers: "What modules exist and how do they connect?"

### class.puml
**Domain Model** - Shows the core data structures:
- `Model` - Container for elements, relationships, views, and profiles
- `Element` - Represents an ArchiMate element
- `Relationship` - Represents a connection between elements
- `View`, `Node`, `Connection` - Diagram visualization structure
- `Profile` - Tag/metadata for elements

This diagram answers: "What classes and data structures does the domain use?"

## Why Simplified?

After modularization, the codebase is simpler. The diagrams reflect that:
- **No complex dependency layers** - Just clean module boundaries
- **No backward compatibility plumbing** - That's hidden behind `__init__.py`
- **No legacy references** - The architecture focuses on the future state
- **Easy to understand** - Anyone can grasp the structure in 30 seconds

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
✅ **Backward compatible** - Old import paths continue to work (via `__init__.py`)  

---

**Last Updated**: 2026-04-10  
**Status**: Simplified Future-State Architecture

