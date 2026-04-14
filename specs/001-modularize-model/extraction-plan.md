# Modularization Extraction Plan

**Created**: 2024-04-10  
**Feature**: 001-modularize-model  
**Source**: `src/pyArchimate/_legacy.py` (3,745 lines)

## Overview

This document details the complete extraction plan for modularizing the monolithic `_legacy.py` file into focused, layered modules.

## Phase 1: Analysis Results

### Classes Found (20 total)

**Tier 1 - Core Domain (High Priority Extraction):**
- **Model** (line 3007, 37 methods): Core orchestrator for Archimate models
- **Element** (line 645, 17 methods): Base element class with subtypes
- **Relationship** (line 960, 23 methods): Relationship class with constraints

**Tier 2 - Views/Visualization:**
- **View** (line 2704, 14 methods): View/diagram representation
- **Node** (line 1373, 42 methods): Visual node representation  
- **Connection** (line 2352, 23 methods): Visual connection representation

**Tier 3 - Value Objects/Support:**
- **Point** (line 467, 5 methods): Coordinate point
- **Position** (line 530, 2 methods): Position representation
- **Font** (line 606, 3 methods): Font specification
- **RGBA** (line 566, 3 methods): Color representation
- **Profile** (line 1327, 3 methods): User profile

**Tier 4 - Enums:**
- **AccessType** (line 150): Access level enumeration
- **ArchiType** (line 185): Archimate type enumeration
- **Writers** (line 80): Writer drivers enumeration
- **Readers** (line 140): Reader types enumeration
- **TextPosition** (line 161): Text position enumeration
- **TextAlignment** (line 171): Text alignment enumeration

**Tier 5 - Exceptions:**
- **ArchimateRelationshipError** (line 297): Relationship validation error
- **ArchimateConceptTypeError** (line 301): Concept type error

**Tier 6 - Infrastructure:**
- **ReaderEntry** (line 39, dataclass): Reader registry entry

### Top-Level Functions: 11 found

Functions to be categorized into helpers:
- Diagram helpers (5-7 functions)
- Serialization helpers (2-3 functions)
- Logging helpers (1-2 functions)

### Dependencies Matrix

```
Model (Tier 1)
  ├─ imports Element, Relationship, View, Node
  ├─ uses constants (magic numbers)
  └─ uses enums (Writers, Readers, AccessType)

Element (Tier 1)
  ├─ uses enums (ArchiType, AccessType)
  ├─ uses exceptions
  └─ simple structure, minimal dependencies

Relationship (Tier 1)
  ├─ uses enums (ArchiType, AccessType)
  ├─ uses exceptions
  └─ simple structure, minimal dependencies

View (Tier 2) → depends on Element, Node, Connection, Point, Position, Font, RGBA
Node (Tier 2) → depends on Element, Point, Position, Font, RGBA
Connection (Tier 2) → depends on Relationship, Node, Point, Font, RGBA
```

## Extraction Plan

### Layer 1 (Base) - No pyArchimate Imports

**constants.py**
- Extract all module-level constants
- Magic numbers for defaults
- Configuration values
- Registry structures
- Dependency: stdlib only

**enums.py**
- AccessType
- ArchiType
- Writers
- Readers
- TextPosition
- TextAlignment
- Dependency: stdlib only

**exceptions.py**
- ArchimateRelationshipError
- ArchimateConceptTypeError
- Dependency: stdlib only

### Layer 2 (Core Domain) - Imports from Layer 1 only

**model.py**
- Model class (37 methods)
- Imports: Element, Relationship, View
- Imports: Layer 1 (constants, enums, exceptions)

**element.py**
- Element class (17 methods)
- Imports: Layer 1 (enums, exceptions)

**relationship.py**
- Relationship class (23 methods)
- Imports: Layer 1 (enums, exceptions)

### Layer 3 (Visualization) - Imports from Layers 1, 2, 3

**view.py**
- View class (14 methods)
- Imports: Element, Node, Connection

**node.py**
- Node class (42 methods)
- Imports: Element, value objects (Point, Position, Font, RGBA)

**connection.py**
- Connection class (23 methods)
- Imports: Relationship, Node, value objects

**value_objects.py** (optional grouping)
- Point, Position, Font, RGBA classes
- Imports: Layer 1 only

### Layer 4 (Helpers)

**helpers/diagram.py**
- Diagram visualization helpers
- Imports: Layers 1, 2, 3

**helpers/serialization.py**
- Property serialization helpers
- Imports: Layers 1, 2

**helpers/logging.py**
- Logging and configuration helpers
- Imports: Layer 1

### Entry Points

**__init__.py** (main)
- Re-exports Model, Element, Relationship
- Re-exports helpers
- Imports: All layers

**_legacy.py** (permanent compatibility)
- Re-exports all extracted classes
- Supports: `from src.pyArchimate.pyArchimate import Model`

**pyArchimate.py** (temporary shim)
- Re-exports from extracted modules
- Will be retired once readers/writers updated

## Import Dependencies by Class

### Model
```python
from . import Element, Relationship, View
from .constants import *
from .enums import Writers, Readers, AccessType
from .exceptions import ArchimateRelationshipError, ArchimateConceptTypeError
from typing import Callable
from uuid import UUID
```

### Element
```python
from .constants import *
from .enums import ArchiType, AccessType
from .exceptions import ArchimateConceptTypeError
from dataclasses import dataclass
```

### Relationship
```python
from .constants import *
from .enums import ArchiType, AccessType
from .exceptions import ArchimateRelationshipError
```

### View
```python
from . import Node, Connection, Element
from .enums import TextPosition
from typing import Optional, List
```

### Node
```python
from . import Element
from .value_objects import Point, Position, Font, RGBA
from typing import Optional
```

### Connection
```python
from . import Relationship, Node
from .value_objects import Point, Font
from typing import Optional, List
```

## Module Dependencies (Extraction Order)

1. **Layer 1** (no dependencies):
   - constants.py
   - enums.py
   - exceptions.py

2. **Layer 2** (depends on Layer 1):
   - element.py
   - relationship.py
   - value_objects.py (if created)
   - model.py (depends on element.py, relationship.py)

3. **Layer 3** (depends on Layers 1, 2):
   - view.py
   - node.py
   - connection.py

4. **Layer 4** (helpers):
   - helpers/diagram.py
   - helpers/serialization.py
   - helpers/logging.py

5. **Entry Points**:
   - __init__.py
   - _legacy.py
   - pyArchimate.py

## Testing Strategy

### Phase 1 (Layer 1):
- Each module imports independently
- No circular dependencies
- Unit tests for each enum/constant/exception

### Phase 2 (Layer 2):
- Model, Element, Relationship importable
- Behavioral parity with original
- Class instantiation tests
- Method behavior tests

### Phase 3 (Layer 3):
- View, Node, Connection importable
- Integration tests with Layer 2
- Diagram operations tests

### Phase 4 (Helpers & Entry Points):
- Helpers importable independently
- Entry point re-exports complete
- Backward compatibility tests
- Reader/Writer import verification

### Phase 5 (Integration & Validation):
- Full test suite runs
- All 230+ existing tests pass
- No broken readers/writers
- All acceptance criteria pass

## Current State

- Branch: `001-modularize-model`
- Status: Analysis complete
- Next: Begin Layer 1 extraction (constants.py, enums.py, exceptions.py)

## Acceptance Criteria

- [ ] AC-001: _legacy.py contains only re-export wrappers by end
- [ ] AC-002: Model, Element, Relationship have zero _legacy.py imports
- [ ] AC-003: All helpers extracted to helpers/ directory
- [ ] AC-004: __init__.py re-exports all public symbols
- [ ] AC-005: 100+ unit tests cover new modules
- [ ] AC-006: No circular imports between layers
- [ ] AC-007: All 230 existing tests pass unchanged
- [ ] AC-008: Documentation matches extracted structure
- [ ] AC-009: 95%+ backward compatibility maintained
- [ ] AC-010: Code review complete, all issues resolved
