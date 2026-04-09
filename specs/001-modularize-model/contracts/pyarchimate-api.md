# pyArchimate API Contract

## Public symbols
- `pyArchimate.Model`: entry point for Model creation; now implemented in `pyArchimate.model` but re-exported through `__init__.py`.  
- `pyArchimate.Element`: element constructors/validators from `pyArchimate.element`.  
- `pyArchimate.Relationship`: relationship constructors from `pyArchimate.relationship`.  
- Helpers originally in `pyArchimate.py` continue to be reachable via `pyArchimate.helpers.diagram`, `pyArchimate.helpers.properties`, and `pyArchimate.helpers.logging` when consumers opt in.

## Compatibility guarantees
- Consumers that imported `from pyArchimate import Model, Element, Relationship` do not need to change their imports; `__all__` and package exports maintain the same names.  
- Legacy `src.pyArchimate.pyArchimate` imports still resolve via compatibility shim to avoid breaking scripts that bypass the package entry point.  
- Helper utilities mirror their previous behavior but now live in dedicated modules; any refactor that moves helper functions must preserve their public functions/classes or document the change as a breaking change.

## Error handling contract
- Model, Element, and Relationship constructors still raise the same exceptions for invalid IDs/properties.  
- Helper modules provide validation helpers that log errors through the shared `pyArchimate.logger`; their contract now explicitly includes the logging helper to standardize output.

## Testing/Verification
- Import smoke tests should continue to import from `pyArchimate` without referencing `src/pyArchimate`.  
- Reader and writer adapters must verify they still resolve `pyArchimate.Model`/`Element`/`Relationship` before release.  
- Any new helper module should document its exposure in this contract before being used by downstream scripts.
