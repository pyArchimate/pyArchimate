# Phase 0 Research: Derived Relationships

## Decision 1 — Derivation-rule table scope and structure

**Status**: Verified against a primary copy of the ArchiMate 3.2 Specification (The Open Group, 2012-2022) on 2026-09-13, superseding the secondary-source-only version of this decision recorded during initial planning. The open item this section previously flagged (see `plan.md`'s Constitution Check for Principle VII and `tasks.md`'s "Known Deviations") is now **closed**. Two real errors in the original secondary-source-derived table were found and corrected as part of this verification (see "What changed" below) — this was not merely a matter of confirming an already-correct guess.

**Decision**: The relevant ArchiMate 3.2 relationship categories (Specification §5.1-§5.4) are:

- **Structural** (§5.1): `Composition`, `Aggregation`, `Assignment`, `Realization` — exactly four types. **`Serving` is not a structural relationship.**
- **Dependency** (§5.2): `Serving`, `Access`, `Influence`, `Association`. Of these, only `Serving` is in this feature's scope (the other three are excluded per the issue).
- **Dynamic** (§5.3): `Triggering`, `Flow`.
- **Other** (§5.4): `Specialization` (excluded per the issue).

Appendix B ("Relationships (Normative)"), Section B.2 ("Derivation Rules for Valid Relationships") defines the "certain" (as opposed to merely "potential", see B.3) derivation rules as DR1 through DR8. This feature implements the rules that apply to a simple two-step "in-line" forward chain (leg1: a→b, leg2: b→c, same direction) among the seven in-scope types:

- **DR2** (p.128): both legs structural → derive the weaker of the two, using the strength order `Composition` (strongest) > `Aggregation` > `Assignment` > `Realization` (weakest).
- **DR3** (p.129): structural then `Serving` → derive `Serving`.
- **DR5** (p.130): structural then a dynamic relationship (`Triggering` or `Flow`) → derive that same dynamic type.
- **DR7** (p.130): `Triggering` then structural → derive `Triggering`.
- **DR8** (p.131): `Triggering` then `Triggering` → derive `Triggering` (transitivity).

Every other combination of the seven in-scope types (e.g. `Serving` as the first leg, `Flow`-then-structural, `Flow`+`Flow`, `Triggering`+`Flow`, `Serving`+`Serving`, `Serving` combined with a dynamic relationship in either order) has **no** "certain" derivation rule in Appendix B.2 and correctly yields no result. The specification's "opposing" rules (DR4, DR6 — where the second leg points *into* the intermediate element rather than out of it) do not apply, since this feature's chain discovery (`find_chains`) only produces the "in-line" forward shape.

**What changed from the pre-verification (secondary-source) version of this decision**:
1. `Serving` was incorrectly modeled as "the weakest structural relationship" (a fifth entry in the structural strength order). It is a *dependency* relationship with entirely different combination rules (DR3), not part of the structural total order at all.
2. Dynamic-dynamic combination was incorrectly generalized as "`Triggering`+`Triggering` → `Triggering`, else → `Flow`" for any pairing of `Triggering`/`Flow`. Only `Triggering`+`Triggering` (DR8) is a defined "certain" rule; `Flow`+`Flow`, `Flow`+`Triggering`, and `Triggering`+`Flow` have none.
3. Previously-unmodeled cross-category rules were discovered and added: structural-then-`Serving` (DR3), structural-then-dynamic (DR5), and `Triggering`-then-structural (DR7). The pre-verification version treated *all* cross-subgroup chains as non-qualifying, which was too conservative in exactly these three cases.

**Rationale**: The issue explicitly asked for only "the unambiguous subset" and to leave ambiguous cases "to a human." Implementing precisely DR2/DR3/DR5/DR7/DR8 — no more, no less — keeps every claim this feature makes traceable to a specific, cited rule in the normative appendix, satisfying Principle VII (System Integrity & Accuracy) without either guessing at undefined combinations or being needlessly more conservative than the specification itself.

**Source**: ArchiMate® 3.2 Specification, The Open Group, © 2012-2022, Appendix B ("Relationships (Normative)"), Sections B.1-B.2 (pp.127-131), and Section 5 ("Relationships and Relationship Connectors"), Sections 5.1-5.4 (pp.23-35) for the category definitions.

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
