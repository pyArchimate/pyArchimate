# Phase 0 Research: Derived Relationships

## Decision 1 — Derivation-rule table scope and structure

**Decision**: Split the seven supported relationship types into two subgroups and define derivation only within each subgroup, never across them:

- **Structural subgroup**: `Composition`, `Aggregation`, `Assignment`, `Realization`, `Serving`. Combine two structural relationships in sequence (A→B, B→C) via the ArchiMate 3.2 §3.5 "weakest link" total order — `Composition` (strongest) > `Aggregation` > `Assignment` > `Realization` > `Serving` (weakest) — the derived type between A and C is the weaker of the two legs, except for the specific cell combinations the spec itself marks as undefined (no derived relationship), which are transcribed verbatim from the spec's derivation table during implementation and locked in as unit-test fixtures (one test per cell, 25 combinations).
- **Dynamic subgroup**: `Triggering`, `Flow`. Two legs both `Triggering` derive `Triggering`; any other combination (`Triggering`+`Flow`, `Flow`+`Triggering`, `Flow`+`Flow`) derives `Flow`.
- **Cross-subgroup chains** (one leg structural, one leg dynamic, e.g. `Assignment` then `Triggering`): the ArchiMate 3.2 specification does not define a total-order combination across these categories. Rather than guess, such chains are treated as **not qualifying** for derivation (FR-001's "yields a defined implied relationship type" is false for these), consistent with the spec's own conservative stance on Access/Influence/Specialization/Association.

**Rationale**: The issue explicitly asked for only "the unambiguous subset" and to leave ambiguous cases "to a human." Guessing a cross-subgroup result risks presenting a misleading derived relationship as authoritative, which directly conflicts with Principle VII (System Integrity & Accuracy). A precisely transcribed, cell-tested table is auditable and keeps the feature's claims traceable to the spec section that licenses them.

**Alternatives considered**:
- *Full cross-category total order* (as some ArchiMate tutorials informally present): rejected — no single authoritative total order across all relationship categories exists in the spec; inventing one would produce results the spec doesn't actually support.
- *Configurable/pluggable rule table*: rejected as over-engineering for this feature's scope (YAGNI) — nothing in the issue or spec asks for user-customizable derivation rules, and the existing `checker_rules.yml` pattern is for element/relationship legality, not derivation semantics; introducing a second rules-config surface would add complexity without a requirement driving it.

## Decision 2 — Where the derivation table and logic live

**Decision**: New module `src/pyArchimate/derivation.py`, following the existing convention of one focused module per concern (`relationship.py`, `element.py`, `viewpoint.py`), rather than growing `model.py` or `relationship.py` further.

**Rationale**: `model.py` already delegates specialized validation logic to `relationship.py` (`check_valid_relationship`) via a local import to avoid a circular import at module-load time (see `model.py`'s `check_invalid_relationships`, which imports from `.relationship` inside the method body). The same pattern is reused: `model.py` gets two thin wrapper methods that import from `.derivation` locally and delegate.

**Alternatives considered**:
- *Add functions directly to `relationship.py`*: rejected — `relationship.py` is about a single relationship's validity, not multi-relationship chain analysis; mixing concerns would violate Principle I (Code Quality / SOLID).
- *Add functions directly to `model.py`*: rejected — `model.py` is already large; a dedicated module keeps the new ~7-type rule table and chain-walking logic independently unit-testable without needing a full `Model` fixture for every table-cell test.

## Decision 3 — Public API shape

**Decision**: Expose two library-level entry points, both delegating to `derivation.py`:

- `Model.check_derivable_duplicates() -> list[DuplicateFinding]` — mirrors `Model.check_invalid_relationships()`'s existing signature convention (a bound method returning a list of findings, no mutation).
- `Model.derive_relationship(element_a, element_b) -> list[DerivedRelationship]` — takes two `Element` (or UUID) references already resolvable against the model, returns zero or more `DerivedRelationship` results (plural, per spec Edge Case: multiple qualifying chains are reported independently, never merged).

Both `DuplicateFinding` and `DerivedRelationship` are plain, immutable `dataclasses` (not `Relationship` subclasses) — deliberately **not** ORM-style objects registered anywhere in the model's dictionaries, so there is no risk of them being accidentally serialized by a writer. Their string representation includes the `«derived»` marker (FR-007) so any caller that does naive `str()`-based logging or display gets the distinguishing label without extra effort; callers doing structured rendering (e.g., an SVG generator) read `.is_derived` / `.type` explicitly instead.

**Rationale**: Reusing the `check_invalid_*` naming and return-shape convention satisfies Principle III (UX Consistency) — existing users of the checker methods immediately recognize the pattern. Keeping results as plain dataclasses outside `rels_dict`/`elems_dict` guarantees FR-004/FR-006 (no persistence) structurally, not just by convention.

**Alternatives considered**:
- *Return actual (unregistered) `Relationship` instances*: rejected — `Relationship.__init__` registers itself into `parent.rels_dict` as a side effect (see `relationship.py`), so producing one without registering it would require bypassing the class's own invariants, which is fragile and could break if `Relationship.__init__` changes. A dedicated dataclass is simpler and safer.
- *A free function instead of a `Model` method*: rejected — every other whole-model check (`check_invalid_relationships`, `check_invalid_conn`, `check_invalid_nodes`) is a `Model` method; matching that convention was rated more valuable than a marginally more "functional" API.

## Decision 4 — Test strategy

**Decision**:
- `tests/unit/test_derivation.py`: parametrized tests over every structural-pair combination (25 cells) and every dynamic-pair combination (4 cells), each asserting the exact derived type or "no derivation"; plus targeted tests for the edge cases called out in spec.md (self-referencing A→B→A cycles, chains with an out-of-scope leg type, dangling-reference exclusion).
- `tests/integration/test_derivation_roundtrip.py`: builds a small model with a known duplicate and a known derivable-but-unmodeled pair, asserts `check_derivable_duplicates()` and `derive_relationship()` results, then re-reads the model/view files' bytes before and after each call to prove immutability (SC-002).

**Rationale**: Matches Principle II (100% coverage on core business logic; TDD Red-Green-Refactor) and gives SC-001/SC-002/SC-004 direct, automatable verification rather than relying on manual review.
