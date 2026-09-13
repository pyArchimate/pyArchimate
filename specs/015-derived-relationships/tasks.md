# Tasks: Derived Relationships (Scan & Render-Time Computation)

**Input**: Design documents from `/specs/015-derived-relationships/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/derivation-api.md, quickstart.md

**Tests**: Included and required — the project constitution (Principle II) mandates TDD (Red-Green-Refactor); tests are written first in every phase below.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- File paths are exact and relative to the repository root

---

## Phase 1: Setup

**Purpose**: Scaffold the new test files. No new dependencies or project initialization needed — this feature extends the existing `pyArchimate` library in place.

- [X] T001 [P] Create `tests/unit/test_derivation.py` with module docstring and imports (`pytest`, `from pyArchimate import Model`, `from pyArchimate.derivation import ...` — imports will fail until later tasks create the module; that's expected at this point)
- [X] T002 [P] Create `tests/integration/test_derivation_roundtrip.py` with module docstring, imports, and a small helper that builds an in-memory `Model` fixture with a known chain (reusable across integration tests)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The derivation-rule table and chain-discovery logic that both User Story 1 and User Story 2 depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Write failing unit tests in `tests/unit/test_derivation.py` for a `derive_pair_type(leg1_type, leg2_type)` function: parametrize over all 25 structural-type combinations (`Composition`, `Aggregation`, `Assignment`, `Realization`, `Serving`) and all 4 dynamic-type combinations (`Triggering`, `Flow`), asserting the expected derived type or `None`, per research.md Decision 1
- [X] T004 Implement `_STRUCTURAL_STRENGTH_ORDER`, `_DEPENDENCY_TYPES_IN_SCOPE`, and `_DYNAMIC_TYPES` constants and `derive_pair_type(leg1_type, leg2_type) -> str | None` in `src/pyArchimate/derivation.py` (new file) to make T003 pass, implementing DR2/DR3/DR5/DR7/DR8 from ArchiMate 3.2 Specification Appendix B.2. **Re-verified against a primary copy of the spec on 2026-09-13** (see research.md Decision 1) — this replaced an initial secondary-source-only version of the table that had two real errors (treating `Serving` as structural rather than a dependency relationship, and over-generalizing dynamic-dynamic combination beyond DR8), both corrected during verification.
- [X] T005 Write failing unit tests in `tests/unit/test_derivation.py` for a `RelationshipChain` dataclass and `find_chains(model)` function: cover a valid two-step chain, a self-referencing A→B→A cycle (must be excluded, FR-009), a chain with an out-of-scope leg type such as `Association` (must be excluded, FR-008), and a relationship referencing an element absent from the model (must be excluded, FR-011)
- [X] T006 Implement `RelationshipChain` dataclass and `find_chains(model) -> list[RelationshipChain]` in `src/pyArchimate/derivation.py` (depends on T004) to make T005 pass — group the model's relationships by intermediate element (`leg1.target is leg2.source`), applying all three exclusions

**Checkpoint**: Derivation rule table and chain discovery are fully unit-tested. Both user stories can now build on `derive_pair_type` and `find_chains`.

---

## Phase 3: User Story 1 - Find redundant explicit relationships (Priority: P1) 🎯 MVP

**Goal**: Given a model, report every explicit relationship that duplicates what an existing two-step chain already implies.

**Independent Test**: Run the scan against a model with a known duplicate and a control model with none; confirm the report lists exactly the duplicate with zero false positives (spec.md SC-001).

### Tests for User Story 1

- [X] T007 [P] [US1] Write failing unit tests in `tests/unit/test_derivation.py` for a `DuplicateFinding` dataclass and `find_duplicate_relationships(model) -> list[DuplicateFinding]`: cover User Story 1's four acceptance scenarios (duplicate flagged with its chain cited, no explicit relationship → no finding, mismatched type → no finding, no chains at all → empty report) plus the edge case of the same duplicate reachable via more than one qualifying chain (grouped into one finding, not two)

### Implementation for User Story 1

- [X] T008 [US1] Implement `DuplicateFinding` dataclass and `find_duplicate_relationships(model) -> list[DuplicateFinding]` in `src/pyArchimate/derivation.py` (depends on T006) to make T007 pass; group multiple implying chains under one finding per FR-002/FR-003
- [X] T009 [US1] Add `Model.check_derivable_duplicates(self) -> list[DuplicateFinding]` method in `src/pyArchimate/model.py`, delegating to `derivation.find_duplicate_relationships` via a local import inside the method body (mirrors the existing `check_invalid_relationships` circular-import pattern)
- [X] T010 [P] [US1] Write an integration test in `tests/integration/test_derivation_roundtrip.py` that builds a model with a known duplicate, calls `model.check_derivable_duplicates()`, and asserts `model.rels_dict`, `model.elems_dict`, `model.conns_dict`, and every `View` are byte-for-byte unchanged before/after (SC-002)
- [X] T011 [US1] Manually run quickstart.md Scenario 1 and confirm the documented output matches exactly

**Checkpoint**: User Story 1 is fully functional and independently testable — the scan capability can ship on its own.

---

## Phase 4: User Story 2 - Compute the implied relationship on demand (Priority: P1)

**Goal**: Given two elements with no explicit relationship, compute what the derivation rule implies between them, without persisting anything.

**Independent Test**: Query a pair of elements known to be connected by a qualifying chain and a pair known not to be; confirm results are correct and the model/view files are unchanged after (spec.md SC-002).

### Tests for User Story 2

- [X] T012 [P] [US2] Write failing unit tests in `tests/unit/test_derivation.py` for a `DerivedRelationship` dataclass and `derive_between(model, source, target) -> list[DerivedRelationship]`: cover User Story 2's four acceptance scenarios (qualifying chain found, no qualifying chain → empty list, existing explicit relationship doesn't suppress or alter the result, and model/view untouched) plus the multiple-independent-chains edge case (each chain's result returned separately, never merged)

### Implementation for User Story 2

- [X] T013 [US2] Implement `DerivedRelationship` dataclass (fields: `source`, `target`, `type`, `chain`, `is_derived=True`, with `__str__`/`__repr__` including the `«derived»` marker per FR-007) and `derive_between(model, source, target) -> list[DerivedRelationship]` in `src/pyArchimate/derivation.py` (depends on T006) to make T012 pass
- [X] T014 [US2] Add `Model.derive_relationship(self, source, target) -> list[DerivedRelationship]` method in `src/pyArchimate/model.py`, delegating to `derivation.derive_between` via a local import; raise `ValueError` when `source`/`target` don't resolve to elements in the model, matching `_resolve_and_validate_ref`'s error style in `relationship.py` (per contracts/derivation-api.md)
- [X] T015 [P] [US2] Write an integration test in `tests/integration/test_derivation_roundtrip.py` that reads a real `.archimate` fixture file with `Model.read()`, calls `check_derivable_duplicates()`/`derive_relationship(...)`, and asserts the fixture file's bytes on disk are unchanged (SHA-256 hash before/after) — implemented via a direct file-hash check rather than a write()-roundtrip comparison, since a roundtrip conflates writer determinism with this feature's own guarantee (SC-002, quickstart.md Scenario 3)
- [X] T016 [US2] Manually run quickstart.md Scenarios 2 and 4 and confirm the documented output matches exactly

**Checkpoint**: User Stories 1 and 2 both work independently — the core scan and query capabilities from the issue are complete.

---

## Phase 5: User Story 3 - Distinguish derived from modeled relationships (Priority: P2)

**Goal**: Ensure a derived relationship is never mistaken for an explicit one in any output.

**Independent Test**: Inspect any output containing both a `DerivedRelationship` and an ordinary `Relationship`; confirm only the former carries the "derived" marker (spec.md SC-003).

### Tests for User Story 3

- [X] T017 [P] [US3] Write a failing unit test in `tests/unit/test_derivation.py` asserting `str(DerivedRelationship(...))` always contains `"«derived»"`, and that `str()`/`repr()` of an ordinary `Relationship` object (as returned inside a `DuplicateFinding.relationship`) never contains that marker

### Implementation for User Story 3

- [X] T018 [US3] Close any gap found by T017 in `DerivedRelationship.__str__`/`__repr__` in `src/pyArchimate/derivation.py` (expected to already satisfy this from T013; this task exists to make the guarantee explicit and regression-tested rather than incidental)

**Checkpoint**: All three user stories are independently functional and tested.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Wire the new capability into the public API and confirm the whole feature meets its constitution and success-criteria gates.

- [X] T019 [P] Re-export `DuplicateFinding`, `DerivedRelationship`, `find_duplicate_relationships`, and `derive_between` from `src/pyArchimate/pyArchimate.py`, following the existing facade re-export convention (alongside `check_invalid_relationships`, etc.)
- [X] T020 [P] Add Sphinx-style docstrings to every public name in `src/pyArchimate/derivation.py` and to the two new `Model` methods in `src/pyArchimate/model.py`, matching the existing docstring style in that file — confirmed already complete by the docs-uplift pass; also added a `__repr__` override to `DerivedRelationship` (previously only `__str__` carried the `«derived»` marker, which understated the FR-007/SC-003 guarantee — fixed rather than weakening the docs)
- [X] T021 Run `poetry run pytest tests/unit/test_derivation.py tests/integration/test_derivation_roundtrip.py --cov=src/pyArchimate/derivation -v` and confirm 100% coverage on `src/pyArchimate/derivation.py` per constitution Principle II — 57 tests passed, 100% coverage (96/96 lines) confirmed
- [X] T022 Run `poetry run ruff check src/pyArchimate/derivation.py src/pyArchimate/model.py src/pyArchimate/pyArchimate.py` and `poetry run pyright src/pyArchimate/derivation.py` (or the project's configured type checker), fixing any findings — both clean; the quality-uplift pass found and fixed two real `Optional[Element]` narrowing gaps pyright caught (see commit 17f1040)
- [X] T023 Run the full existing test suite (`poetry run pytest`) to confirm no regressions in `check_invalid_relationships`, readers, writers, or view rendering — 1689 passed, 1 skipped, 4 xfailed (pre-existing), 95% overall coverage, no regressions
- [X] T024 Review `specs/015-derived-relationships/checklists/requirements.md` and note any deviations discovered during implementation, for traceability — see the Requirements Traceability Matrix and Known Deviations sections below

---

## Requirements Traceability Matrix

*Added post-implementation per `specs/TECHNICAL.md`'s mandatory traceability component; backfilled from a spec-alignment review rather than at task-generation time — see Known Deviations below.*

| Requirement | Type | Task IDs | User Story | Success Criteria |
|---|---|---|---|---|
| FR-001 (identify 2-step chains) | Functional | T005, T006 | Foundational | — |
| FR-002 (scan reports exact-match duplicates) | Functional | T007, T008 | US1 | SC-001 |
| FR-003 (cite the implying chain) | Functional | T007, T008 | US1 | SC-001 |
| FR-004 (scan is read-only) | Functional | T008, T009, T010 | US1 | SC-002 |
| FR-005 (query implied relationship on demand) | Functional | T012, T013 | US2 | — |
| FR-006 (query never persists) | Functional | T013, T014, T015 | US2 | SC-002 |
| FR-007 (derived results marked) | Functional | T013, T017, T018 | US3 | SC-003 |
| FR-008 (restrict to 7 supported types) | Functional | T003, T004, T005, T006 | Foundational | SC-004 |
| FR-009 (no A→B→A self-cycle) | Functional | T005, T006 | Foundational | — |
| FR-010 (multiple chains reported independently) | Functional | T012, T013 | US2 | — |
| FR-011 (exclude dangling refs) | Functional | T005, T006 | Foundational | — |
| SC-001 (100% duplicate detection, 0 false positives) | Success Criterion | T007, T010 | US1 | — |
| SC-002 (no persistence, verified) | Success Criterion | T010, T015 | US1, US2 | — |
| SC-003 (marking always distinguishes) | Success Criterion | T017, T018 | US3 | — |
| SC-004 (decline for out-of-scope types) | Success Criterion | T003, T007, T012 | Foundational, US1, US2 | — |

Coverage: 11/11 functional requirements traced to code and tests; 4/4 success criteria traced to automated tests (none verified by prose/manual claim alone). No orphaned tasks and no requirement without a task.

## Known Deviations (T024)

Recorded here per constitution Governance ("deviations must be justified in the plan.md complexity tracking section") and `specs/TECHNICAL.md`'s traceability requirement, discovered during a post-implementation spec-alignment review:

1. **Constitution Principle VII — open item, now CLOSED (resolved 2026-09-13).** The derivation-rule table was initially built from secondary web sources only (the Open Group's primary specification pages required authentication unavailable at planning time), and `plan.md`'s Constitution Check briefly and inaccurately claimed it was "transcribed directly from the spec." Once a primary copy of the ArchiMate 3.2 Specification was obtained, verification against Appendix B.2 found **two real errors**, not just an unverified-but-correct guess: (a) `Serving` was modeled as the weakest *structural* relationship, when it is actually a *dependency* relationship (§5.2) with different combination rules (DR3); (b) dynamic-relationship combination was generalized as "`Triggering`+`Triggering`→`Triggering`, else→`Flow`", when the specification only defines `Triggering`+`Triggering` (DR8) — `Flow`+`Flow`, `Flow`+`Triggering`, and `Triggering`+`Flow` have no defined derivation. Both were fixed in `src/pyArchimate/derivation.py`, with previously-missing cross-category rules (DR3, DR5, DR7) added at the same time. See `research.md` Decision 1 for full detail and page citations. `plan.md`'s Constitution Check for Principle VII now reads PASS (not conditional).
2. **`__repr__` gap, fixed rather than left as a doc mismatch.** `DerivedRelationship` originally only overrode `__str__` with the `«derived»` marker; `repr()` used the dataclass default and carried no marker, which understated the FR-007/SC-003 guarantee. Fixed by adding a `__repr__` override (see `src/pyArchimate/derivation.py`) rather than weakening the documented guarantee.
3. **Requirements Traceability Matrix was missing from initial `tasks.md`.** `specs/TECHNICAL.md` mandates this table; it was omitted during `/speckit-tasks` and backfilled above once the gap was found.
4. **quickstart.md Scenario 3 referenced a nonexistent fixture** (`tests/fixtures/sample.archimate` instead of the real `tests/fixtures/valid_model.archimate`, which the actual integration test correctly uses). Corrected in quickstart.md.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (T004/T006 are the shared rule table and chain-walker every story calls)
- **User Story 1 (Phase 3)**: Depends on Foundational (T006) — no dependency on US2/US3
- **User Story 2 (Phase 4)**: Depends on Foundational (T006) — no dependency on US1; may run in parallel with Phase 3 if staffed separately
- **User Story 3 (Phase 5)**: Depends on User Story 2 (T013's `DerivedRelationship`) — cannot start before Phase 4
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Within Each User Story

- Tests are written first and MUST fail before the corresponding implementation task
- Dataclass/function implementation (`derivation.py`) before the `Model` wrapper method
- `Model` wrapper method before the integration (file-immutability) test can meaningfully run
- Story complete (all its tasks checked) before starting the next priority's implementation, if working sequentially

### Parallel Opportunities

- T001 and T002 (Setup) can run in parallel — different files
- T007 and T012 (US1 and US2 unit tests) can run in parallel once Phase 2 is complete — different test functions in the same file, but logically independent; if working sequentially in one file, do them back-to-back instead
- T010 and T015 (US1 and US2 integration tests) can run in parallel — independent test functions
- T019 and T020 (Polish) can run in parallel — different concerns, though T019 touches `pyArchimate.py` and T020 touches `derivation.py`/`model.py`

---

## Parallel Example: Setup

```bash
Task: "Create tests/unit/test_derivation.py with module docstring and imports"
Task: "Create tests/integration/test_derivation_roundtrip.py with module docstring, imports, and a fixture-model helper"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (T003–T006) — CRITICAL, blocks everything else
3. Complete Phase 3: User Story 1 (the scan/lint capability)
4. **STOP and VALIDATE**: run quickstart.md Scenario 1 and the T010 integration test independently
5. This alone closes half of issue #140's request and can ship on its own

### Incremental Delivery

1. Setup + Foundational → shared rule table and chain-walker ready
2. Add User Story 1 → validate independently → the scan/lint capability is usable
3. Add User Story 2 → validate independently → the on-demand query capability is usable (both P1 deliverables from the issue are now complete)
4. Add User Story 3 → validate independently → derived vs. explicit is now guaranteed distinguishable everywhere
5. Polish → public API export, docs, full-suite regression check, coverage gate

---

## Notes

- All work lands in one new module (`src/pyArchimate/derivation.py`) plus two new `Model` methods — there is little true file-level parallelism available; the `[P]` markers above are conservative and mostly apply to the two separate test files.
- Commit after each checkpoint (end of each phase), not after every single task, to keep the git history reviewable.
- Verify each test fails before implementing the corresponding production code (Red-Green-Refactor, constitution Principle II).
