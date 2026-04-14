# Data Model: Modular Model Modules

## Entities

### Model
- Orchestrates collections of `Element`, `Relationship`, `View`, `Node`, and `Connection` instances.  
- Responsibilities: property embedding/expansion, reader/writer registration, logging configuration, validation helpers.  
- Key fields: `elements: dict[str, Element]`, `relationships: dict[str, Relationship]`, `views: list[View]`, `props: dict[str, Any]` (used for persistence helpers).  
- State transitions: model creation → element/relationship registration → view serialization.  

### Element
- Represents ArchiMate elements with `id`, `name`, `type`, `properties`, `documentation`, `parent`.  
- Validation rules: rejects duplicate IDs, enforces required relationships (via helper `check_invalid_nodes`).  
- Serialization helpers live in `pyArchimate.element` and rely on property helpers for embedding/expansion.

### Relationship
- Captures links between `Element` instances with `source_id`, `target_id`, `type`, `metadata`.  
- Validation: uses helpers such as `check_invalid_conn` to ensure source/target exist within the model.  
- Relationships participate in import/export, which is why they remain accessible through package exports.

## Helper Modules

### Diagram helpers (`pyArchimate.helpers.diagram`)
- Provide utilities such as `get_or_create_node`, `get_or_create_connection`, node positioning, view creation, and label formatting.  
- Interact with `Model`/`Element` through imports from the new modules to avoid circular references.

### Property helpers (`pyArchimate.helpers.properties`)
- Manage property embedding/expansion for writers that cannot natively serialize metadata.  
- Centralize validation around `Model.embed_props`/`expand_props` to keep property semantics consistent across readers/writers.

### Logging helpers (`pyArchimate.helpers.logging`)
- Configure `pyArchimate.logger`, manage log levels, and expose helper functions used across modules for consistent messaging.

## Relationships
- Elements ↔ Model: each `Element` belongs to a `Model` and is registered/managed by it.  
- Relationships ↔ Elements: each `Relationship` references two `Element` IDs; helpers ensure references remain valid.  
- Helpers ↔ Domain entities: helper modules import the new `Model`, `Element`, and `Relationship` modules while remaining re-exported through `__init__.py` so callers can rely on a single namespace.
