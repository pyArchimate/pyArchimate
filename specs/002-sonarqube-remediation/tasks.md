# Tasks: SonarQube Critical Issue Remediation

**Input**: Design documents from `/specs/002-sonarqube-remediation/`  
**Branch**: `002-sonarqube-remediation`  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Data Model**: [data-model.md](data-model.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1–US6 from spec.md)

> **Phase ordering note**: Phases are ordered by user-story priority (P1 before P2 before P3). This means US6 (S3776, P1) appears before US2 (S1192, P2) and US3 (S5754, P2), which differs from the rule-category commit order stated in `spec.md` Assumptions (S5727 → S1192 → S5754 → S1186 → S3776).
>
> **Solo developer**: Follow the spec commit order — complete T004–T005 (S5727), then T015 (S1192), then T016 (S5754), then T017 (S1186), then T006–T014 (S3776). This minimises per-commit SonarCloud delta and matches the stated assumption.
>
> **Team**: Parallelise by story priority as shown in these phases — US1 and US6a/US6c can proceed concurrently; US2 and US3 can follow in parallel once US6b writers are done.

---

## Phase 1: Setup

**Purpose**: Fix SonarCloud configuration so legacy violations are excluded and progress is measurable from the first push.

- [ ] T001 Update `sonar-project.properties`: add `tests/legacy_*/**` to `sonar.exclusions` and replace malformed `sonar.test.exclusions` with `tests/legacy_*/**`

**Checkpoint**: Push branch; confirm legacy test violations no longer appear in SonarCloud CRITICAL list.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infrastructure required before writer or reader refactoring can be validated safely.

⚠️ **CRITICAL**: T002 must be complete before any Phase 4 (US6) writer tasks begin.

- [ ] T002 Create `tests/integration/test_writer_fidelity.py`: round-trip read→write→compare canonical XML using `tests/fixtures/myModel.archimate` and `tests/fixtures/test.archimate` fixtures for both `archi_writer` and `archimate_writer`
- [ ] T003 Audit `src/pyArchimate/_legacy.py` for live callers: run `grep -r "_legacy\|from.*_legacy\|import.*_legacy" src/ tests/` and document result in a code comment in the deletion commit message

**Checkpoint**: `poetry run pytest tests/integration/test_writer_fidelity.py` passes against unmodified writers.

---

## Phase 3: User Story 1 — Fix Identity Check Comparisons (Priority: P1)

**Goal**: Remove S5727 violations in `test_archimateWriter.py`; all 4 identity-check assertions corrected.

**Independent Test**: `poetry run pytest tests/unit/writers/test_archimateWriter.py` passes; SonarCloud reports zero S5727 violations.

- [ ] T004 [US1] Investigate S5727 violations at lines 22, 24, 26, 28 of `tests/unit/writers/test_archimateWriter.py`: determine whether SonarCloud flags `is not None` against lxml results as a false positive or a valid violation, then apply the minimum-change fix (truthy assertion `assert x` if semantics allow, or `# NOSONAR` if genuinely a false positive)
- [ ] T005 [US1] Verify `poetry run pytest tests/unit/writers/test_archimateWriter.py` passes and commit as `fix(tests): replace identity checks with equality assertions (S5727)`

**Checkpoint**: Zero S5727 violations visible in next SonarCloud scan.

---

## Phase 4: User Story 6 — Reduce Cognitive Complexity (Priority: P1)

**Goal**: All 10 S3776 violations resolved; every function in production code has complexity ≤ 15.

**Independent Test**: `poetry run pytest tests/unit/ tests/integration/` passes; SonarCloud reports zero S3776 violations.

### US6a — Quick wins: element.py and view.py

- [ ] T006 [P] [US6] Refactor `src/pyArchimate/element.py:267` (complexity 16 → ≤ 15): extract the 1-point-over-threshold logic into a private `_<descriptive_name>` helper in the same file; run `poetry run pytest tests/unit/test_element.py`
- [ ] T007 [P] [US6] Refactor `src/pyArchimate/view.py:153` (complexity 17 → ≤ 15): extract helper(s) in same file; run `poetry run pytest tests/unit/test_view.py`
- [ ] T008 [US6] Refactor `src/pyArchimate/view.py:519` (complexity 22 → ≤ 15): extract `_compute_*` / `_layout_*` helpers in same file
- [ ] T009 [US6] Refactor `src/pyArchimate/view.py:597` (complexity 44 → ≤ 15): extract multiple `_render_*` helpers in same file
- [ ] T010 [US6] Refactor `src/pyArchimate/view.py:699` (complexity 16 → ≤ 15) and `view.py:1006` (complexity 23 → ≤ 15): extract helpers in same file; commit all view.py changes as `refactor(view): reduce cognitive complexity below 15 (S3776)`

**Checkpoint**: `poetry run pytest tests/unit/test_view.py tests/unit/test_element.py` passes. Then run `poetry run pytest tests/unit/ tests/integration/` to confirm no cross-module regressions before proceeding (FR-007).

### US6b — Writer refactoring (fidelity tests must pass first — see T002)

- [ ] T011 [US6] Refactor `src/pyArchimate/writers/archimateWriter.py:35` (complexity 180 → ≤ 15): extract `_write_elements`, `_write_relationships`, `_write_views`, `_write_nodes`, `_write_connections`, `_write_properties` as private helpers in same file; run `poetry run pytest tests/unit/writers/test_archimateWriter.py tests/integration/test_writer_fidelity.py`
- [ ] T012 [US6] Refactor `src/pyArchimate/writers/archiWriter.py:23` (complexity 162 → ≤ 15): extract `_write_folder`, `_write_element`, `_write_relationship`, `_write_view`, `_write_style` as private helpers in same file; run `poetry run pytest tests/unit/writers/test_archiWriter.py tests/integration/test_writer_fidelity.py`; commit both writer changes as `refactor(writers): reduce cognitive complexity below 15 (S3776)`

**Checkpoint**: All writer unit tests and fidelity tests pass; output is semantically identical to pre-refactor. Then run `poetry run pytest tests/unit/ tests/integration/` to confirm no cross-module regressions (FR-007).

### US6c — Reader refactoring (highest risk, most debt)

- [ ] T013 [US6] Create `src/pyArchimate/readers/_archireader_helpers.py`: extract per-element-type `_parse_<type>(node, model)` helpers from `archiReader.py:21` (complexity 254 → ≤ 15 in each function); update `archiReader.py` to import from the new sibling module; run `poetry run pytest tests/unit/readers/test_archiReader.py tests/legacy_unit/readers/test_archiReader.py`
- [ ] T014 [US6] Create `src/pyArchimate/readers/_arisamlreader_helpers.py`: extract per-AML-element-type `_parse_<aris_type>(node, model)` helpers from `arisAMLreader.py:85` (complexity 259 → ≤ 15 in each function); update `arisAMLreader.py` to import; run `poetry run pytest tests/unit/readers/test_arisAMLreader.py tests/legacy_unit/readers/test_arisAMLreader.py`; commit both reader changes as `refactor(readers): reduce cognitive complexity below 15 (S3776)`
- [ ] T022 [US6] Verify `src/pyArchimate/readers/_archireader_helpers.py` achieves ≥ 80% unit test coverage: run `poetry run pytest tests/unit/readers/test_archiReader.py --cov=src/pyArchimate/readers/_archireader_helpers --cov-report=term-missing`; if coverage < 80%, add targeted unit tests in `tests/unit/readers/test_archireader_helpers.py`
- [ ] T023 [US6] Verify `src/pyArchimate/readers/_arisamlreader_helpers.py` achieves ≥ 80% unit test coverage: run `poetry run pytest tests/unit/readers/test_arisAMLreader.py --cov=src/pyArchimate/readers/_arisamlreader_helpers --cov-report=term-missing`; if coverage < 80%, add targeted unit tests in `tests/unit/readers/test_arisamlreader_helpers.py`

**Checkpoint**: All reader unit and legacy unit tests pass; `poetry run pytest tests/unit/ tests/integration/` green; both new helper modules at ≥ 80% coverage.

---

## Phase 5: User Story 2 — Fix Duplicate String Literals (Priority: P2)

**Goal**: S1192 violation in `archimateWriter.py` resolved; `'ns:item'` replaced by a named constant.

**Independent Test**: `poetry run pytest tests/unit/writers/test_archimateWriter.py tests/integration/test_writer_fidelity.py` passes; SonarCloud reports zero S1192 violations.

- [ ] T015 [US2] Extract `'ns:item'` → `_NS_ITEM = 'ns:item'` module-level constant at the top of `src/pyArchimate/writers/archimateWriter.py`; replace all 4 occurrences; run `poetry run pytest tests/unit/writers/test_archimateWriter.py`; commit as `fix(writers): extract duplicate string literal to constant (S1192)`

**Checkpoint**: Zero S1192 violations in next SonarCloud scan.

---

## Phase 6: User Story 3 — Fix Bare Except Clauses (Priority: P2)

**Goal**: S5754 violation resolved by deleting `_legacy.py` (confirmed dead code).

**Independent Test**: `poetry run pytest tests/unit/ tests/integration/` passes after deletion; SonarCloud reports zero S5754 violations.

- [ ] T016 [US3] Confirm zero live callers of `src/pyArchimate/_legacy.py` using the audit result from T003; delete the file; run the full unit and integration test suite to confirm no regressions; commit as `fix(legacy): delete _legacy.py with no live callers (S5754)`

**Checkpoint**: Zero S5754 violations in next SonarCloud scan.

---

## Phase 7: User Story 5 — Add Comment to Empty Placeholder Function (Priority: P3)

**Goal**: S1186 violation resolved; placeholder BDD step has an explanatory comment.

**Independent Test**: `poetry run behave tests/features/` passes; SonarCloud reports zero S1186 violations.

- [ ] T017 [US5] Add `# TODO: implement acceptance test step` (or equivalent intent comment) inside the empty function body at line 6 of `tests/features/steps/placeholder_steps.py`; run `poetry run behave tests/features/`; commit as `fix(bdd): add comment to placeholder step function (S1186)`

**Checkpoint**: Zero S1186 violations in next SonarCloud scan.

---

## Phase 8: Polish & Verification

**Purpose**: Full-suite validation and SonarCloud confirmation that all CRITICAL issues are resolved.

- [ ] T018 Run `bash scripts/pre_push_checks.sh` and confirm all gates pass (ruff, pyright, mypy, pytest unit 80% coverage, legacy unit, integration, behave); then run `poetry run radon cc src/ -s -n C` and confirm zero Grade D/F functions remain across all production modules including new helper modules (SC-003)
- [ ] T019 [P] Run local SonarCloud scan: `poetry run pysonar --sonar-token=$SONAR_TOKEN`; confirm zero CRITICAL issues reported
- [ ] T020 [P] Update `specs/002-sonarqube-remediation/data-model.md`: fill in the TBD helper function names with actual names used during implementation
- [ ] T021 Push `002-sonarqube-remediation` to origin; confirm CI/CD SonarCloud scan reports zero CRITICAL issues (SC-001)

**Checkpoint**: SC-001 through SC-006 all confirmed green. Feature complete.

---

## Requirements Traceability Matrix

| Requirement | Type | Task(s) | User Story | Success Criteria |
|-------------|------|---------|------------|-----------------|
| FR-001 | Functional | T004, T005 | US1 | SC-001, SC-002 |
| FR-002 | Functional | T015 | US2 | SC-001, SC-002 |
| FR-003 | Functional | T003, T016 | US3 | SC-001, SC-002 |
| FR-004 | Functional | *(out of scope)* | US4 | SC-006 |
| FR-005 | Functional | T017 | US5 | SC-001, SC-002 |
| FR-006 | Functional | T006–T014, T022, T023 | US6 | SC-001, SC-002, SC-003 |
| FR-007 | Functional | All tasks | All | SC-002 |
| FR-008 | Functional | T002, T011–T014 | US6 | SC-002, SC-005 |
| FR-009 | Functional | T013, T014 | US6 | SC-002 |
| FR-010 | Functional | T003, T016 | US3 | SC-001 |
| FR-011 | Functional | All tasks | All | SC-001 |
| FR-012 | Functional | T001 | Setup | SC-001 |

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: No dependencies — can start in parallel with Phase 1
- **Phase 3 (US1)**: No dependencies on Phases 1–2
- **Phase 4 US6a (element/view)**: No dependencies on Phases 1–2; can start after Phase 3
- **Phase 4 US6b (writers)**: **Requires T002** (fidelity tests) before T011, T012
- **Phase 4 US6c (readers)**: No dependency on US6b; can start after US6a
- **Phase 5 (US2)**: T015 touches `archimateWriter.py` — must complete after T011 (US6b) to avoid merge conflicts
- **Phase 6 (US3)**: Requires T003 audit result
- **Phase 7 (US5)**: No dependencies — can be done at any point
- **Phase 8 (Polish)**: Requires all prior phases complete

### User Story Dependencies

- **US1 (P1)**: Independent — start anytime
- **US6a (P1)**: Independent — start anytime (after US1 ideally)
- **US6b (P1)**: Depends on T002 (fidelity tests)
- **US6c (P1)**: Independent of US6b — can run in parallel
- **US2 (P2)**: Schedule after T011 to avoid conflicting edits to `archimateWriter.py`
- **US3 (P2)**: Depends on T003 audit
- **US5 (P3)**: Fully independent — can be done at any time

### Parallel Opportunities

- T001 and T002 can run in parallel (different files)
- T006 and T007 can run in parallel (different files in `view.py` vs `element.py`)
- T013 and T014 can run in parallel (different reader files, different helper modules)
- T019 and T020 can run in parallel (different concerns)

---

## Parallel Example: US6 Reader Tasks

```bash
# T013 and T014 can execute simultaneously — different files, no shared state:
Task: "Refactor archiReader.py + create _archireader_helpers.py (T013)"
Task: "Refactor arisAMLreader.py + create _arisamlreader_helpers.py (T014)"
```

---

## Implementation Strategy

### MVP Scope (US1 only — fastest to ship)

1. T001 — Fix sonar config
2. T004, T005 — Fix S5727 identity checks
3. Push and confirm 4 fewer CRITICAL issues on SonarCloud

### Full Delivery (recommended order)

1. Phase 1 + 2 (T001–T003) — foundation
2. Phase 3 (T004–T005) — US1, quick
3. Phase 4 US6a (T006–T010) — element + view, medium risk
4. Phase 5 (T015) — US2, trivial (must be after T011 to avoid conflict; swap if US2 done before writers)
5. Phase 6 (T016) — US3, trivial
6. Phase 7 (T017) — US5, trivial
7. Phase 4 US6b (T011–T012) — writers, medium risk (fidelity tests as safety net)
8. Phase 4 US6c (T013–T014) — readers, highest risk
9. Phase 8 (T018–T021) — verify and push

---

## Notes

- **[P]** tasks operate on different files with no shared dependencies — safe to parallelize
- Each task produces exactly one conventional commit (see `quickstart.md` for message format)
- Never commit if `bash scripts/pre_push_checks.sh` fails (FR-011)
- Writer tasks (T011, T012) are guarded by fidelity tests in T002 — do not skip T002
- If any refactored function still exceeds complexity 15 after first attempt, decompose further before committing
- `tests/legacy_*/**` must never be modified (FR-007, SC-006)
