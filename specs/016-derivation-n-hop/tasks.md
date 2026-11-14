---

description: "Task list template for feature implementation"
---

# Tasks: Generalize Derivation to N-Hop Chains

**Input**: Design documents from `/specs/016-derivation-n-hop/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/derivation-api.md, quickstart.md (all present)

**Tests**: Included. The project constitution (Principle II, Testing Standards) mandates Red-Green-Refactor TDD and 100% coverage on core business logic, and this feature modifies existing, already-tested core logic (`src/pyArchimate/derivation.py`).

**Organization**: Tasks are grouped by user story (from spec.md) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- File paths are exact, matching plan.md's Project Structure section

## Path Conventions

Single project (library), per plan.md: `src/pyArchimate/`, `tests/unit/`, `tests/integration/`, `tests/features/`, `tests/performance/` at repository root.

---

## Phase 1: Setup

**Purpose**: Establish the regression baseline this feature's safety guarantee (User Story 3, SC-003) is measured against.

- [ ] T001 Run `poetry run pytest tests/unit/test_derivation.py tests/integration/test_derivation_roundtrip.py -v` and `poetry run behave tests/features --tags=derivation` on the current `derivation.py` (pre-this-feature) and record the full pass/fail output as the SC-003 regression baseline (no file changes — this is the reference result later tasks compare against)

**Checkpoint**: Baseline captured — safe to begin modifying `derivation.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Generalize the core chain-discovery engine that every user story (duplicate scan, on-demand query, unchanged-default guarantee) depends on. No user story work can begin until this phase is complete.

**⚠️ CRITICAL**: This phase changes the shared `RelationshipChain` and `find_chains()` that Phases 3–5 all build on.

- [ ] T002 [P] Write failing unit tests in `tests/unit/test_derivation.py` for a generalized `RelationshipChain.legs: list[Relationship]` field (replacing the fixed `leg1`/`leg2` pair) and for `find_chains()` discovering qualifying 3-leg and 4-leg chains when called with `max_chain_length=3` / `max_chain_length=4` (FR-001; SC-001; data-model.md's `RelationshipChain` entity)
- [ ] T003 [P] Write failing unit test in `tests/unit/test_derivation.py` asserting `find_chains(model)` called with no `max_chain_length` argument (default `2`) returns results identical in shape and content to the T001 baseline (FR-010, SC-003)
- [ ] T004 [P] Write failing unit test in `tests/unit/test_derivation.py` for `find_chains(model, max_chain_length=3)` rejecting a 4-element path that revisits an intermediate element (A→B→C→B), generalizing the existing two-step A→B→A self-reference protection to a chain of any length (FR-004; Edge Cases bullet 1)
- [ ] T005 [P] Write failing unit test in `tests/unit/test_derivation.py` confirming a relationship referencing an element absent from the model, placed at hop 3 of a 4-step chain, excludes that chain from `find_chains(model, max_chain_length=4)` — generalizing the existing two-step dangling-reference exclusion (FR-008; Edge Cases bullet 5)
- [ ] T006 Add `DEFAULT_MAX_CHAIN_LENGTH_CEILING: int = 6` module-level constant to `src/pyArchimate/derivation.py`, plus a helper that raises `ValueError` when a caller's `max_chain_length` exceeds it and the keyword-only `allow_exceeding_default_ceiling` is not `True` — quoting contracts/derivation-api.md's constraint verbatim: "Values above DEFAULT_MAX_CHAIN_LENGTH_CEILING require allow_exceeding_default_ceiling=True" (FR-011)
- [ ] T007 Generalize the `RelationshipChain` dataclass in `src/pyArchimate/derivation.py` from `leg1: Relationship` / `leg2: Relationship` fields to `legs: list[Relationship]`, with `intermediate` becoming a property returning the `len(legs) - 1` shared elements between consecutive legs (data-model.md). Preserve `leg1`/`leg2`-style access (e.g. via properties reading `legs[0]`/`legs[-1]`) so existing 2-leg callers relying on those names are unaffected (depends on T002)
- [ ] T008 Rewrite `find_chains()` in `src/pyArchimate/derivation.py` to use the bounded-depth, fused-pruning path-extension algorithm from research.md Decision 1: extend each qualifying relationship one leg at a time via the existing `_index_qualifying_by_source` index (which already excludes dangling references, FR-008), call `derive_pair_type` at every extension step and abandon the path immediately when it returns `None` (FR-003), abandon the path immediately if the next element would already be present in a running visited-element set (FR-004, generalizing the existing `leg2._target == leg1._source` check), and stop extending once `len(legs) == max_chain_length` (FR-001). Accept new `max_chain_length: int = 2` and keyword-only `allow_exceeding_default_ceiling: bool = False` parameters, invoking the T006 ceiling check first (depends on T006, T007)
- [ ] T009 Run T002, T003, T004, and T005 and confirm all now pass; re-run the T001 baseline commands and confirm zero behavioral differences at default settings (SC-003)

**Checkpoint**: Foundation ready — `find_chains()` and `RelationshipChain` now support chains of any length; all downstream user stories can proceed.

---

## Phase 3: User Story 1 - Find redundant explicit relationships that duplicate a longer implied chain (Priority: P1) 🎯 MVP

**Goal**: The existing duplicate scan (`find_duplicate_relationships` / `Model.check_derivable_duplicates`) also reports an explicit relationship that duplicates what a chain of more than two relationships implies, when the caller opts in via `max_chain_length`.

**Independent Test**: Run the duplicate scan against a model containing a qualifying 3-or-more-step chain and an explicit relationship duplicating its implied result, with `max_chain_length` raised; confirm the scan reports it — independently of US2/US3.

### Tests for User Story 1

- [ ] T010 [P] [US1] Write failing unit tests in `tests/unit/test_derivation.py` for `find_duplicate_relationships(model, max_chain_length=3)` flagging a duplicate implied by a 3-step chain, and `find_duplicate_relationships(model, max_chain_length=4)` flagging a duplicate implied by a 4-step chain (FR-005; Acceptance Scenarios 1 and 3; SC-001)
- [ ] T011 [P] [US1] Write failing unit test in `tests/unit/test_derivation.py` for a 3-step chain where the second adjacent pair has no defined derivation rule: `find_duplicate_relationships(model, max_chain_length=3)` must report nothing for that chain, not a partial result based on the first two legs (Acceptance Scenario 4; FR-003, SC-002)
- [ ] T012 [P] [US1] Write failing integration test in `tests/integration/test_derivation_roundtrip.py` for quickstart.md Scenario 1 end-to-end: default call reports nothing, `max_chain_length=3` call reports exactly one `DuplicateFinding` citing a 3-leg chain, and the model/view files remain byte-identical after the scan

### Implementation for User Story 1

- [ ] T013 [US1] Thread `max_chain_length: int = 2` and keyword-only `allow_exceeding_default_ceiling: bool = False` through `find_duplicate_relationships()` in `src/pyArchimate/derivation.py`, passing them to `find_chains()` (FR-005; depends on T008)
- [ ] T014 [US1] Add `max_chain_length: int = 2` and keyword-only `allow_exceeding_default_ceiling: bool = False` to `Model.check_derivable_duplicates()` in `src/pyArchimate/model.py` as a thin pass-through to `find_duplicate_relationships()`, mirroring the existing `include_dependency` wrapper pattern (depends on T013)
- [ ] T015 [US1] Add BDD step definitions for User Story 1's longer-chain duplicate-scan acceptance scenarios in `tests/features/steps/derivation_steps.py`
- [ ] T016 [US1] Run T010, T011, T012, and the new behave scenarios from T015; confirm all pass

**Checkpoint**: User Story 1 is fully functional and independently testable — the duplicate scan now catches longer-chain duplicates when opted in.

---

## Phase 4: User Story 2 - Query the relationship implied between two elements connected only by a longer chain (Priority: P2)

**Goal**: The existing on-demand derivation query (`derive_between` / `Model.derive_relationship`) also returns a result for two elements connected only by a chain of more than two relationships, when the caller opts in via `max_chain_length`.

**Independent Test**: Call the derivation query against a pair of elements known to be connected only by a qualifying 3-or-more-step chain, with `max_chain_length` raised; confirm the result and the full chain cited, and that model/view files are byte-for-byte unchanged — independently of US1/US3.

### Tests for User Story 2

- [ ] T017 [P] [US2] Write failing unit test in `tests/unit/test_derivation.py` for `derive_between(model, a, d, max_chain_length=3)` returning the correctly folded type and citing the full 3-leg chain (FR-006; Acceptance Scenario 1)
- [ ] T018 [P] [US2] Write failing unit test in `tests/unit/test_derivation.py` for a chain containing an adjacent pair with no defined rule yielding `derive_between(..., max_chain_length=3) == []` (Acceptance Scenario 2)
- [ ] T019 [P] [US2] Write failing unit test in `tests/unit/test_derivation.py` for two elements connected by both a qualifying 2-step chain and a separate qualifying 3-step chain: `derive_between(model, a, d, max_chain_length=3)` returns both results independently, each citing its own chain, never merged or ranked (Acceptance Scenario 3; FR-007)
- [ ] T020 [P] [US2] Write failing unit test in `tests/unit/test_derivation.py` for `derive_between(model, a, d, include_dependency=True, max_chain_length=3)` folding correctly across a 3+-hop chain that relies on Influence for one leg, exactly as it would for an all-default-scope chain (Acceptance Scenario 4; FR-009)
- [ ] T021 [P] [US2] Write failing integration test in `tests/integration/test_derivation_roundtrip.py` for quickstart.md Scenario 2 end-to-end: default call returns `[]`, `max_chain_length=3` call returns one `DerivedRelationship` citing a 3-leg chain, and model/view files remain byte-identical after the query

### Implementation for User Story 2

- [ ] T022 [US2] Thread `max_chain_length: int = 2` and keyword-only `allow_exceeding_default_ceiling: bool = False` through `derive_between()` in `src/pyArchimate/derivation.py`, passing them to `find_chains()` (FR-006; depends on T008)
- [ ] T023 [US2] Add `max_chain_length: int = 2` and keyword-only `allow_exceeding_default_ceiling: bool = False` to `Model.derive_relationship()` in `src/pyArchimate/model.py` as a thin pass-through to `derive_between()` (depends on T022)
- [ ] T024 [US2] Add BDD step definitions for User Story 2's longer-chain query acceptance scenarios in `tests/features/steps/derivation_steps.py`
- [ ] T025 [US2] Run T017–T021 and the new behave scenarios from T024; confirm all pass

**Checkpoint**: User Stories 1 AND 2 both work independently — scan and query now cover chains of any opted-in length.

---

## Phase 5: User Story 3 - Existing callers see unchanged behavior unless they opt in (Priority: P3)

**Goal**: Every existing call made with default settings only returns byte-for-byte identical results to the pre-this-feature implementation; a caller sees new longer-chain results only by explicitly raising `max_chain_length`, and only up to the documented ceiling unless they explicitly override it.

**Independent Test**: Re-run the existing (pre-this-feature) test suite and example models through the upgraded module using default settings only; confirm every result matches the T001 baseline — independently of US1/US2's new opt-in behavior.

### Tests for User Story 3

- [ ] T026 [P] [US3] Write failing regression test in `tests/unit/test_derivation.py` that re-runs representative cases from the T001 baseline through the generalized module with default settings only and asserts identical results (Acceptance Scenario 1; SC-003)
- [ ] T027 [P] [US3] Write failing unit test in `tests/unit/test_derivation.py` for a model containing a qualifying longer-than-two-step chain: `Model.check_derivable_duplicates()` and `Model.derive_relationship(a, d)` called with default settings report nothing for that chain; the result only appears once `max_chain_length` is explicitly raised (Acceptance Scenario 2)
- [ ] T028 [P] [US3] Write failing unit test in `tests/unit/test_derivation.py` for `max_chain_length=10` (above `DEFAULT_MAX_CHAIN_LENGTH_CEILING`) raising `ValueError` on `find_chains`/`derive_between`/`find_duplicate_relationships`, and succeeding when `allow_exceeding_default_ceiling=True` is also passed (FR-011; quickstart.md Scenario 5)

### Implementation for User Story 3

- [ ] T029 [US3] Run T026, T027, T028; since User Story 3 is a safety/compatibility guarantee rather than new capability, no new production code is expected here — if any test fails, fix the regression in `src/pyArchimate/derivation.py` or `src/pyArchimate/model.py` introduced by Phases 2–4 before proceeding (depends on T016, T025)
- [ ] T030 [US3] Add BDD step definitions for User Story 3's default-unchanged and explicit-opt-in acceptance scenarios in `tests/features/steps/derivation_steps.py`

**Checkpoint**: All three user stories are independently functional — US1 and US2's new capability is proven additive, never breaking existing callers.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Close the two remaining functional requirements that are documentation-only and don't gate any single user story's independent testability, plus final validation.

- [ ] T031 [P] Correct the module docstring in `src/pyArchimate/derivation.py` to state that the ArchiMate derivation rule is not inherently limited to two hops, and that the prior two-step-only behavior was this project's own deliberate scope decision rather than a reflection of the rule itself (FR-012; research.md Decision 5)
- [ ] T032 [P] Correct `specs/015-derived-relationships/spec.md`'s User Story descriptions and Key Entities section wherever they frame the two-step chain as the full extent of what the derivation rule covers, per the same correction as T031 (FR-012; research.md Decision 5)
- [ ] T033 Review the full `derivation.py` module docstring and all of `specs/015-derived-relationships/spec.md` for any remaining statement implying a two-hop ceiling beyond what T031/T032 corrected; confirm none remain (SC-005; depends on T031, T032)
- [ ] T034 [P] Document how chain-discovery cost grows as chain length and model size/density increase, alongside the `DEFAULT_MAX_CHAIN_LENGTH_CEILING` constant in `src/pyArchimate/derivation.py`, in terms a caller can use to decide how far above the default to raise `max_chain_length` (FR-013)
- [ ] T035 [P] Add an SC-004 benchmark to `tests/performance/test_performance_benchmarks.py`: build a ~1,000-element model (matching the existing `test_large_model_hierarchy_queries_performance` scale) with a mix of 2-step and 3–6-hop qualifying chains, and assert `find_duplicate_relationships(model, max_chain_length=2)` and `find_duplicate_relationships(model, max_chain_length=6)` both complete within the same order-of-magnitude wall-clock bound (research.md Decision 4)
- [ ] T036 Run all five quickstart.md scenarios end-to-end exactly as written and confirm each matches its documented expected outcome
- [ ] T037 Run the full project quality gates: `poetry run ruff check .`, `poetry run ruff format --check .`, `poetry run pyright`, `poetry run mypy`, `poetry run pytest`, `poetry run behave` — all must pass before this feature is considered Done (constitution Quality Gates)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — captures the baseline Phase 5 compares against.
- **Foundational (Phase 2)**: Depends on Setup completion (needs the T001 baseline for T003/T009) — BLOCKS all user stories.
- **User Stories (Phase 3–5)**: All depend on Foundational phase completion.
  - US1 and US2 are independent of each other and may proceed in parallel.
  - US3 depends on US1 and US2's implementation tasks (T016, T025) being done, since it verifies *their* default-call behavior didn't regress — it cannot be meaningfully run before they exist.
- **Polish (Phase 6)**: Depends on all three user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — no dependency on US2.
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — no dependency on US1; may run in parallel with it.
- **User Story 3 (P3)**: Can start only after US1 (T016) and US2 (T025) implementation tasks are done, since its tests assert those stories' default-call behavior is unchanged.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (constitution Principle II).
- `derivation.py` module-level function changes before `model.py` wrapper changes.
- Story's unit + integration tests before its BDD step definitions.
- Story complete (checkpoint) before the next priority story's implementation starts, if working sequentially.

### Parallel Opportunities

- T002, T003, T004, and T005 (Foundational tests) can run in parallel — different test functions, no shared state.
- T010, T011, T012 (US1 tests) can run in parallel.
- T017, T018, T019, T020, T021 (US2 tests) can run in parallel.
- T026, T027, T028 (US3 tests) can run in parallel.
- US1's implementation (T013–T016) and US2's implementation (T022–T025) can proceed in parallel once Foundational (Phase 2) is complete, since they touch different functions (`find_duplicate_relationships` vs. `derive_between`) that only share the already-generalized `find_chains()`.
- T031, T032, T034, T035 (Polish) can all run in parallel — independent files. T033 depends on T031/T032 finishing first.

---

## Parallel Example: Foundational Phase

```bash
# Launch all four foundational test-writing tasks together:
Task: "Write failing unit tests for RelationshipChain.legs and find_chains() N-hop discovery in tests/unit/test_derivation.py"
Task: "Write failing unit test for max_chain_length default=2 regression vs baseline in tests/unit/test_derivation.py"
Task: "Write failing unit test for N-hop cycle-revisit rejection (A→B→C→B) in tests/unit/test_derivation.py"
Task: "Write failing unit test for dangling-reference exclusion at hop 3 of a 4-step chain in tests/unit/test_derivation.py"
```

## Parallel Example: User Story 1 and User Story 2 together

```bash
# Once Phase 2 (Foundational) is checkpointed, both stories' implementation can proceed in parallel:
Task: "Thread max_chain_length through find_duplicate_relationships() in src/pyArchimate/derivation.py"      # US1
Task: "Thread max_chain_length through derive_between() in src/pyArchimate/derivation.py"                    # US2
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (baseline capture).
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories).
3. Complete Phase 3: User Story 1.
4. **STOP and VALIDATE**: Run T010–T012 and confirm the duplicate scan correctly catches longer-chain duplicates when opted in, with zero change to default-call results.
5. Demo/review if ready — this alone closes the single highest-value gap named in GitHub issue #173 (duplicate detection missing longer chains).

### Incremental Delivery

1. Setup + Foundational → generalized chain-discovery engine ready.
2. Add User Story 1 → test independently → MVP.
3. Add User Story 2 → test independently → on-demand query now covers longer chains too.
4. Add User Story 3 → test independently → compatibility guarantee proven, not just assumed.
5. Polish → documentation corrections (FR-012/FR-013) and the SC-004 benchmark ship together with the feature, per FR-012's explicit "MUST ship together with this feature, not be deferred."

### Parallel Team Strategy

With multiple developers: complete Setup + Foundational together first (single shared bottleneck, since both `RelationshipChain` and `find_chains()` are touched); then one developer takes US1, another takes US2 in parallel; a third can begin drafting the Polish-phase documentation corrections (T031/T032) as soon as research.md Decision 5's scope is clear, since they don't depend on US1/US2's code being finished.

---

## Notes

- [P] tasks = different files or independent test functions, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Every entry point gains exactly two new parameters (`max_chain_length`, `allow_exceeding_default_ceiling`) — no other public signature changes.
- Verify tests fail before implementing (Red-Green-Refactor, constitution Principle II).
- Commit after each task or logical group.
- Stop at any checkpoint to validate a story independently.
- `derive_pair_type()` itself is never modified by any task above — every task reuses it unchanged, per FR-002.
