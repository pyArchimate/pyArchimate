# Phase 1 Data Model: Derived Relationships

All entities below are transient (never written to `rels_dict`, `elems_dict`, a model file, or a view file), per FR-004/FR-006.

## RelationshipChain

Represents two existing, explicit relationships sharing a common intermediate element, used as derivation input.

| Field | Type | Notes |
|---|---|---|
| `leg1` | `Relationship` | The A→B relationship (existing, registered in the model) |
| `leg2` | `Relationship` | The B→C relationship (existing, registered in the model) |
| `intermediate` | `Element` | The shared element B; `leg1.target is leg2.source` |

**Validation rules**:
- `leg1.type` and `leg2.type` must each be one of the seven supported types (FR-008), else the chain is discarded before reaching derivation.
- `leg1.source is not leg2.target` (FR-009 — no self-referencing A→B→A cycles produce a derivation).
- Both `leg1` and `leg2` must resolve to elements present in the model (FR-011 — dangling references excluded).

## DerivedRelationship

The transient result of successfully deriving a relationship from a `RelationshipChain`.

| Field | Type | Notes |
|---|---|---|
| `source` | `Element` | Same as `chain.leg1.source` |
| `target` | `Element` | Same as `chain.leg2.target` |
| `type` | `str` | One of the seven supported ArchiMate relationship type names |
| `chain` | `RelationshipChain` | The chain that produced this result, for traceability (FR-003) |
| `is_derived` | `bool` | Always `True`; present so callers can discriminate without `isinstance` checks against `Relationship` |

**Behavior**:
- `__str__`/`__repr__` includes the `«derived»` marker (FR-007).
- Not equal to, and not an instance of, `Relationship` — deliberately a distinct type so it can never be mistaken for, or accidentally treated as, a modeled relationship (see research.md Decision 3).
- Multiple `DerivedRelationship` results MAY exist for the same `(source, target)` pair when more than one qualifying chain connects them (spec Edge Case); they are returned as a list, never merged.

## DuplicateFinding

The result of the scan capability: pairs an existing explicit relationship with the chain(s) that independently imply it.

| Field | Type | Notes |
|---|---|---|
| `relationship` | `Relationship` | The existing, explicit, modeled relationship being flagged |
| `implying_chains` | `list[RelationshipChain]` | One or more chains whose derived result matches `relationship`'s source/target/type exactly |

**Validation rules**:
- `relationship.type == derived.type and relationship.source is derived.source and relationship.target is derived.target` for every chain in `implying_chains` (FR-002).
- A given `relationship` appears in at most one `DuplicateFinding` (grouped, not duplicated one-per-chain — spec Edge Case: "the same duplicate is reachable via more than one qualifying chain").

## Derivation Rule Table (module-level constant, not a runtime entity)

Two lookup structures in `derivation.py`:

- `_STRUCTURAL_STRENGTH_ORDER: tuple[str, ...]` — `("Composition", "Aggregation", "Assignment", "Realization", "Serving")`, strongest to weakest.
- `_STRUCTURAL_UNDEFINED_PAIRS: frozenset[tuple[str, str]]` — the specific ordered `(leg1_type, leg2_type)` pairs the ArchiMate 3.2 spec marks as producing no derived relationship, transcribed during implementation directly from the spec's derivation table (Decision 1 in research.md) and covered one-for-one by unit tests.
- `_DYNAMIC_TYPES: frozenset[str]` — `{"Triggering", "Flow"}`.

No new fields are added to the existing `Relationship`, `Element`, or `Model` classes — this feature reads existing state only.
