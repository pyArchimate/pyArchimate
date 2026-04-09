# Research Notes: Modular Model Modules

## Decision: Dedicated helper modules
**Decision:** Move diagram, property, and logging helpers into their own `pyArchimate.helpers` modules that stay re-exported via `pyArchimate/__init__.py`.  
**Rationale:** Dedicated helper modules keep logic focused, make unit tests more isolated, and reduce merge conflicts when refactoring helper behavior.  
**Alternatives considered:** Keeping helpers scattered near the closest domain class (rejected because the monolith already made individual helpers hard to find and test).  

## Decision: Compatibility layering through the package boundary
**Decision:** Maintain the existing names (`pyArchimate.Model`, etc.) in `__init__.py` so readers, writers, and CLI scripts can continue importing the public API without changes.  
**Rationale:** The spec explicitly mandates stability for downstream adapters; preserving the export ensures refactors do not cascade into deployment scripts.  
**Alternatives considered:** Letting consumers import from new modules directly (rejected due to the high churn for automation pipelines already dependent on the old entry point).  

## Decision: Validation and regression safety
**Decision:** Rely on the existing integration/examples tests plus targeted unit tests on each new module to prove behavioral parity.  
**Rationale:** The constitution emphasizes testing coverage and accuracy; reusing existing suites while adding module-specific tests balances effort with confidence.  
**Alternatives considered:** Creating new end-to-end fixtures (too heavy) or relying only on unit tests (insufficient for verifying reader/writer stability).
