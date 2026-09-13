# Contract: Derivation API (library-level)

pyArchimate is a library with no CLI or network surface for checker-style capabilities (precedent: `check_invalid_relationships`, `check_invalid_conn`, `check_invalid_nodes` are plain `Model` methods, not commands or endpoints). This feature follows the same contract style: public Python method/function signatures, importable from `pyArchimate` per the existing facade convention in `pyArchimate.py`.

## `Model.check_derivable_duplicates`

```python
def check_derivable_duplicates(self) -> list["DuplicateFinding"]:
    """
    Scan this model for explicit relationships that duplicate what a
    two-step relationship chain already implies per the ArchiMate 3.2
    §3.5 derivation rule (restricted to Composition, Aggregation,
    Assignment, Realization, Serving, Triggering, Flow).

    Read-only: never modifies the model.

    :return: one DuplicateFinding per explicit relationship found to be
             a duplicate, each citing the chain(s) that imply it.
    :rtype: list(DuplicateFinding)
    """
```

**Preconditions**: `self` is a loaded `Model` (relationships and elements already populated).
**Postconditions**: `self.rels_dict`, `self.elems_dict`, `self.conns_dict`, and every `View` are unchanged (SC-002). Return value length is 0 for a model with no duplicates (Acceptance Scenario 2/4 in User Story 1).

## `Model.derive_relationship`

```python
def derive_relationship(
    self, source: "Element | str", target: "Element | str"
) -> list["DerivedRelationship"]:
    """
    Compute the relationship(s) implied between two elements by any
    qualifying two-step chain, without persisting the result.

    :param source: source Element or its uuid
    :param target: target Element or its uuid
    :return: zero or more DerivedRelationship results (independent
             results when multiple qualifying chains exist).
    :rtype: list(DerivedRelationship)
    """
```

**Preconditions**: `source` and `target` resolve to elements present in `self.elems_dict`.
**Postconditions**: `self` and any view are unchanged (SC-002). Returns `[]` when no qualifying chain connects the pair (Acceptance Scenario 2 in User Story 2), regardless of whether an explicit relationship already exists between them (Acceptance Scenario 3 — this method never inspects or excludes based on existing explicit relationships between the same pair).

## `derivation.DuplicateFinding` / `derivation.DerivedRelationship`

Public dataclasses, re-exported from `pyArchimate` (`from pyArchimate import DuplicateFinding, DerivedRelationship`). See `data-model.md` for field definitions. Both are read-only value objects: no methods mutate model state, and neither type is accepted as an argument anywhere a `Relationship` is expected (enforced by them not being `Relationship` subclasses).

## Error handling

- `derive_relationship` raises `ValueError` if `source` or `target` does not resolve to an element in the model (consistent with `_resolve_and_validate_ref`'s existing error style in `relationship.py`).
- `check_derivable_duplicates` never raises for a structurally valid model; a model whose relationships fail `check_invalid_relationships` is out of this feature's contract (callers are expected to run `check_invalid_relationships` first, matching existing practice).
