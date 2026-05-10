# Tasks: Incremental Code Quality Uplift

**Input**: Design documents from `specs/009-quality-uplift/`  
**Branch**: `009-quality-uplift`  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Research**: [research.md](./research.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- No test tasks generated (spec does not request TDD approach; existing suite must remain green)

---

## Phase 1: Setup

**Purpose**: Ensure tooling is installed and environment is ready for static analysis work.

- [X] T001 Verify `lxml-stubs`, `types-setuptools` are listed in `pyproject.toml` `[dependency-groups] lint`; add `types-Pillow` if missing
- [X] T002 Install lint dependency group in current environment: `pip install lxml-stubs types-setuptools types-Pillow ruff pyright`
- [X] T003 Run baseline checks and record counts: `ruff check src/ --statistics`, `pyright src/`, `mypy src/` — capture outputs for comparison

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the SonarCloud issue list and confirm the pre-commit suite is green before any changes.

**⚠️ CRITICAL**: No story work begins until this phase is complete.

- [X] T004 Query SonarCloud API using `SONAR_TOKEN` from `.env` and save the open issue list: `curl -u "$SONAR_TOKEN:" "https://sonarcloud.io/api/issues/search?projectKeys=pyArchimate_pyArchimate&severities=CRITICAL,MAJOR,MINOR&statuses=OPEN,CONFIRMED" > /tmp/sonar_issues.json`
- [X] T005 Review `/tmp/sonar_issues.json` and append a `## SonarCloud Triage` section to `specs/009-quality-uplift/research.md` containing a table (issue key, rule, severity, file, line) for use in Phase 3
- [X] T006 Run `bash scripts/pre_commit_checks.sh` to confirm baseline suite is green before any changes

**Checkpoint**: Baseline confirmed, SonarCloud triage table ready — story work can now begin.

---

## Phase 3: User Story 1 — Remediate Remaining SonarQube Issues (Priority: P1)

**Goal**: Clear all open SonarCloud issues so the Quality Gate passes.

**Independent Test**: `pysonar --sonar-token=<SONAR_TOKEN>` scan shows Quality Gate = Passed with zero unresolved issues (excluding `tests/legacy_*`).

- [X] T007 [US1] Fix or suppress each **CRITICAL** SonarCloud issue from the triage table in `specs/009-quality-uplift/research.md`; add `# NOSONAR <reason>` for confirmed false positives
- [X] T008 [US1] Fix or suppress each **MAJOR** SonarCloud issue from the triage table in `specs/009-quality-uplift/research.md`
- [X] T009 [US1] Fix or suppress each **MINOR** SonarCloud issue and any security hotspots from the triage table in `specs/009-quality-uplift/research.md`
- [X] T010 [US1] Run `bash scripts/pre_commit_checks.sh` to verify no regressions after all fixes
- [X] T011 [US1] Commit: `fix(sonar): resolve remaining SonarCloud issues`

**Checkpoint**: SonarCloud Quality Gate should now pass. Verify via CI push or local `pysonar` scan.

---

## Phase 4: User Story 2 — Enable Additional Ruff Lint Rules (Priority: P1)

**Goal**: Enable `A`, `N` rule sets; document `UP` and `PT` as deferred; remove `C901` and `PLC0415` global ignores.

**Independent Test**: `ruff check src/ tests/` passes with 0 errors after adding `A` and `N` to the select list and removing `C901`/`PLC0415` from the ignore list.

### Batch 4a — C901 and PLC0415 cleanup

- [X] T012 [US2] Run `ruff check src/ --select C901` to list the 6 remaining complexity violations; fix each by extracting helper functions (private `_` prefix, same file) in the affected source modules
- [X] T013 [US2] Remove `"C901"` from `[tool.ruff.lint] ignore` in `pyproject.toml`; run `ruff check src/` to confirm 0 C901 violations
- [X] T014 [US2] Audit files triggering `PLC0415` (non-top-level import) — run `ruff check src/ --select PLC0415` to identify them; add `# noqa: PLC0415  # dynamic import required: <reason>` at each call site
- [X] T015 [US2] Remove `"PLC0415"` from `[tool.ruff.lint] ignore` in `pyproject.toml`; run `ruff check src/` to confirm 0 PLC0415 violations

### Batch 4b — Enable rule set `A` (builtin shadowing)

- [X] T016 [P] [US2] Run `ruff check src/ --select A`; fix 2× `A001` (builtin variable shadowing) by renaming the offending variables in their source files
- [X] T017 [P] [US2] Fix 4× `A003` (builtin attribute shadowing) by renaming the offending class/instance attributes in their source files
- [X] T018 [US2] Add `"A"` to `[tool.ruff.lint] select` in `pyproject.toml`; run `ruff check src/` to confirm 0 A violations; commit: `feat(ruff): enable A (builtin-shadowing) rule set`

### Batch 4c — Enable rule set `N` (naming conventions)

- [X] T019 [US2] Run `ruff check src/ --select N`; fix 6× `N811` (constant imported as non-constant) by renaming import aliases to `UPPER_CASE` in their source files
- [X] T020 [US2] Fix 1× `N802` (invalid function name) by renaming the function or adding `# noqa: N802  # <reason>` if renaming would break public API
- [X] T021 [US2] Evaluate 11× `N999` (invalid module name — camelCase files): for each, determine if the module can be renamed without breaking imports; rename if safe, otherwise add `# ruff: noqa: N999  # legacy module name preserved for API compatibility` as a file-level banner on the module's first line (per-line `# noqa` cannot suppress N999 since the violation is on the filename, not a source line)
- [X] T022 [US2] Remove `"N999"` from `[tool.ruff.lint] ignore` in `pyproject.toml`; add `"N"` to `[tool.ruff.lint] select`; run `ruff check src/` to confirm 0 unresolved N violations; commit: `feat(ruff): enable N (naming) rule set; remove N999 global ignore`

### Batch 4d — Defer `UP` and `PT`

- [X] T023 [P] [US2] Add deferred TODO comment in `pyproject.toml` under `[tool.ruff.lint] select` for `UP`: `# TODO(009-quality-uplift): Enable UP rule set — 124 violations exceed the 20-violation cap; most are auto-fixable (ruff --fix) but UP042/UP032 need semantic review`
- [X] T024 [P] [US2] Add deferred TODO comment for `PT`: `# TODO(009-quality-uplift): Enable PT rule set — 163 violations exceed cap; primarily PT009 (unittest assertions) in legacy tests`
- [X] T025 [US2] Run `ruff check src/ tests/ --fix` (safe fixes only) then `ruff check src/ tests/` to confirm 0 errors with the full updated select list (A and N active, C901 and PLC0415 removed); commit: `chore(ruff): add UP and PT deferral TODOs; verify full ruff suite green`

**Checkpoint**: `ruff check src/ tests/` passes with A and N active, C901 and PLC0415 removed from ignore list.

---

## Phase 5: User Story 3 — Tighten Pyright Type-Checking (Priority: P2)

**Goal**: Re-enable `reportAttributeAccessIssue`, `reportArgumentType`, and `reportOptionalMemberAccess` at `"error"` level.

**Independent Test**: `pyright src/` passes with 0 errors after all three categories are promoted to `"error"`.

### Batch 5a — Fix baseline pyright error

- [X] T026 [US3] In `src/pyArchimate/readers/_arisamlreader_helpers.py:61`, add `# type: ignore[import-untyped]  # Pillow has no bundled stubs; runtime import is safe` after the PIL import line; run `pyright src/` to confirm 0 errors

### Batch 5b — reportAttributeAccessIssue (3 warnings)

- [X] T027 [US3] Set `reportAttributeAccessIssue = "warning"` in `[tool.pyright]` in `pyproject.toml`; run `pyright src/` and record the 3 warning locations
- [X] T028 [US3] For each of the 3 attribute-access warnings: either fix the underlying type annotation or add `# type: ignore[attr-defined]  # <reason>` at the call site
- [X] T029 [US3] Promote `reportAttributeAccessIssue = "error"` in `pyproject.toml`; run `pyright src/` to confirm 0 errors

### Batch 5c — reportArgumentType and reportOptionalMemberAccess (0 violations each)

- [X] T030 [P] [US3] Set `reportArgumentType = "error"` in `pyproject.toml`; run `pyright src/` to confirm 0 errors (baseline showed 0 additional violations)
- [X] T031 [P] [US3] Set `reportOptionalMemberAccess = "error"` in `pyproject.toml`; run `pyright src/` to confirm 0 errors
- [X] T032 [US3] Run `pyright src/` with all three categories at `"error"` to confirm clean pass; commit: `fix(pyright): re-enable reportAttributeAccessIssue, reportArgumentType, reportOptionalMemberAccess`

**Checkpoint**: `pyright src/` passes with 0 errors and all three previously-suppressed categories enforced at error level.

---

## Phase 6: User Story 4 — Strengthen Mypy Strict Checks (Priority: P2)

**Goal**: Resolve all 10 baseline mypy errors; evaluate and (if feasible) enable `disallow_untyped_defs` and `disallow_untyped_calls`.

**Independent Test**: `mypy src/` passes with 0 errors.

### Batch 6a — Fix baseline mypy errors

- [X] T033 [US4] Confirm `lxml-stubs` and `types-setuptools` are installed (done in T002); run `mypy src/` and verify the `import-untyped` errors for lxml and setuptools are gone
- [X] T034 [US4] Add `# type: ignore[import-untyped]  # Pillow stubs unavailable` to `src/pyArchimate/readers/_arisamlreader_helpers.py:61` for mypy (run after T026; both modify the same line — T026 adds the pyright ignore, T034 extends it to satisfy mypy; merge into a single combined comment if both tools accept it)
- [X] T035 [US4] Fix `no-any-return` error in `src/pyArchimate/writers/archimateWriter.py:390`: add an explicit cast (`cast(str, ...)`) or annotate the return value; verify return type matches function signature
- [X] T036 [P] [US4] Fix `no-any-return` error in `src/pyArchimate/writers/archiWriter.py:372`: same approach as T035
- [X] T037 [US4] Run `mypy src/` to confirm 0 errors; commit: `fix(mypy): resolve all baseline type errors`

### Batch 6b — Evaluate disallow_untyped_defs (deferred — 162 violations)

- [X] T038 [US4] Run `mypy src/ --disallow-untyped-defs` and count violations; record the count
- [X] T039 [US4] Violation count was 162 (> 20 cap): add `# TODO(009-quality-uplift): Enable — 162 violations; deferred as stretch goal` to `disallow_untyped_defs = false` in `pyproject.toml`; commit: `chore(mypy): document disallow_untyped_defs as deferred stretch goal`
- [X] T040 [US4] Run `mypy src/ --disallow-untyped-calls` and count violations; record the count
- [X] T041 [US4] Violation count was 89 (> 20 cap): add `# TODO(009-quality-uplift): Enable — 89 violations; deferred as stretch goal` to `disallow_untyped_calls = false` in `pyproject.toml`; commit: `chore(mypy): document disallow_untyped_calls as deferred stretch goal`

**Checkpoint**: `mypy src/` passes with 0 baseline errors. `disallow_untyped_defs` and `disallow_untyped_calls` each deferred with documented count.

---

## Phase 7: User Story 5 — Remove Obsolete Exclusions from pyproject.toml (Priority: P3)

**Goal**: Ensure every remaining exclusion in `pyproject.toml` is either gone (because fixed in earlier phases) or annotated with an up-to-date justification.

**Independent Test**: `ruff check src/`, `pyright src/`, and `mypy src/` all pass after the audit; `pyproject.toml` contains no uncommented suppression without a justification comment.

- [X] T042 [US5] Audit `[tool.ruff.lint] ignore` in `pyproject.toml`: confirm `C901` and `PLC0415` are absent (removed in Phase 4) and `N999` is absent (removed in Phase 4); confirm `E501` retains its justification comment: `# line-too-long — formatter handles wrapping; not enforced at lint level`
- [X] T043 [US5] Audit `[tool.pyright]` in `pyproject.toml`: confirm `reportAttributeAccessIssue`, `reportArgumentType`, `reportOptionalMemberAccess` are no longer `"none"` (promoted in Phase 5); confirm `reportMissingTypeStubs` retains a justification comment if still present
- [X] T044 [US5] Audit `[tool.mypy]` in `pyproject.toml`: confirm `disallow_untyped_calls = false` and `disallow_untyped_defs = false` each have a justification comment (or have been removed per T039/T041 decisions)
- [X] T045 [US5] Run `bash scripts/pre_commit_checks.sh` to confirm full suite passes after audit; commit: `chore: annotate or remove obsolete tool exclusions in pyproject.toml`

**Checkpoint**: All suppressions are either gone or carry an explanatory comment. No silent exclusions remain.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation update, and feature closure.

- [X] T046 Run full test suite including integration and BDD: `bash scripts/pre_push_checks.sh`; confirm all pass
- [X] T047 [P] Update `specs/009-quality-uplift/checklists/requirements.md` — mark all checklist items complete and add notes on deferred items (UP, PT, disallow_untyped_defs, disallow_untyped_calls) with violation counts
- [X] T048 [P] Update `specs/009-quality-uplift/research.md` with final state: actual SonarCloud issue counts fixed, final ruff rule sets active, final pyright/mypy config
- [X] T049 Commit: `docs(009): update research and checklist with final quality uplift results`

---

## Phase 9: US2 Extension — Enable Ruff `UP` Rule Set

**Goal**: Remove `# TODO(009-quality-uplift)` for UP from `pyproject.toml`; `ruff check` passes with UP active.

**Independent Test**: `ruff check` exits 0 with `"UP"` uncommented in `[tool.ruff.lint] select`.

- [ ] T050 [US2] Add `"UP042"` to `[tool.ruff.lint] ignore` in `pyproject.toml` with comment `# UP042: StrEnum requires Python 3.11+; project supports 3.10+`; run `ruff check --select UP042` to confirm 0 violations reported
- [ ] T051 [US2] Run `ruff check --fix --select UP` to auto-fix 121 violations (UP045/UP037/UP024/UP015/UP035/UP032); verify no test regressions with `pytest tests/`
- [ ] T052 [US2] Run `ruff check --select UP030` and manually fix the remaining format literal (1 violation); run `ruff check --select UP` to confirm 0 remaining violations
- [ ] T053 [US2] Uncomment `"UP"` in `[tool.ruff.lint] select` and remove the `# TODO(009-quality-uplift)` UP comment block from `pyproject.toml`; run `ruff check` to confirm 0 violations; run `pytest tests/` to confirm suite green; commit: `feat(ruff): enable UP (pyupgrade) rule set`

**Checkpoint**: `ruff check` passes with UP active; UP042 globally ignored with justification.

---

## Phase 10: US2 Extension — Enable Ruff `PT` Rule Set

**Goal**: Remove `# TODO(009-quality-uplift)` for PT from `pyproject.toml`; `ruff check` passes with PT active.

**Independent Test**: `ruff check` exits 0 with `"PT"` uncommented in `[tool.ruff.lint] select`.

### Batch 10a — Legacy test exclusion and auto-fix

- [ ] T054 [US2] Add `per-file-ignores` entry to `[tool.ruff.lint]` in `pyproject.toml`: `"tests/legacy_integration/*.py" = ["PT009"]`; run `ruff check --select PT009` to confirm only legacy file triggers and is suppressed (102 violations removed)
- [ ] T055 [US2] Run `ruff check --fix --select PT` to auto-fix PT001 (9× remove fixture parentheses); verify `pytest tests/` still passes

### Batch 10b — PT018 composite assertion fixes

- [ ] T056 [P] [US2] Fix 6× PT018 in `src/pyArchimate/view.py`, `src/pyArchimate/writers/archiWriter.py`, and `src/pyArchimate/writers/archimateWriter.py`: run `ruff check --select PT018 src/` to get current line numbers (they shift after T051 auto-fix), then split each `assert a and b` into two separate assert statements
- [ ] T057 [P] [US2] Fix PT018 in `tests/unit/test_model.py` (5×), `tests/unit/test_view.py` (2×), `tests/unit/test_relationship.py` (1×), `tests/features/steps/business_interaction_steps.py` (1×), `tests/features/steps/p3_steps.py` (1×)

### Batch 10c — PT011 too-broad pytest.raises fixes

- [ ] T058 [P] [US2] Fix 11× PT011 in `tests/unit/test_view.py`: add `match=` regex parameter to each `pytest.raises()` call; use `re.escape()` for literal strings or a pattern matching the expected message
- [ ] T059 [P] [US2] Fix 9× PT011 in `tests/unit/test_model.py`: same approach as T058
- [ ] T060 [P] [US2] Fix PT011 in `tests/unit/test_element.py` (6×), `tests/unit/test_visual_style.py` (2×), `tests/unit/test_writer_registry.py` (2×)
- [ ] T061 [P] [US2] Fix PT011 in `tests/unit/readers/test_archimateReader.py` (3×), `tests/unit/test_relationship.py` (1×), `tests/performance/test_performance_benchmarks.py` (1×)

### Batch 10d — PT006 and enablement

- [ ] T062 [US2] Fix 1× PT006 in `tests/integration/test_tutorial.py`: correct the parametrize names to use a tuple or comma-separated string
- [ ] T063 [US2] Uncomment `"PT"` in `[tool.ruff.lint] select` and remove the `# TODO(009-quality-uplift)` PT comment block from `pyproject.toml`; run `ruff check` to confirm 0 violations; run `pytest tests/` to confirm suite green; commit: `feat(ruff): enable PT (pytest-style) rule set`

**Checkpoint**: `ruff check` passes with PT active; PT009 suppressed for legacy integration tests with justification.

---

## Phase 11: US4 Extension — Mypy `disallow_untyped_defs`

**Goal**: Add type annotations to all 162 unannotated functions in `src/`; remove `# TODO(009-quality-uplift)` for `disallow_untyped_defs`.

**Independent Test**: `mypy src/` passes after setting `disallow_untyped_defs = true` in `pyproject.toml`.

> **Note**: All T064–T071 tasks operate on different files and are parallelizable. However, `view.py` references `model.py` types and `element.py` references `model.py` types — annotate `model.py` first if type inference issues arise.

- [ ] T064 [P] [US4] Add return-type and parameter-type annotations to all unannotated functions in `src/pyArchimate/view.py` (54 violations): run `mypy --config-file pyproject.toml src/pyArchimate/view.py --disallow-untyped-defs` after each method batch to confirm progress
- [ ] T065 [P] [US4] Add type annotations to `src/pyArchimate/model.py` (34 violations): run `mypy --config-file pyproject.toml src/pyArchimate/model.py --disallow-untyped-defs` to verify
- [ ] T066 [P] [US4] Add type annotations to `src/pyArchimate/relationship.py` (25 violations): run `mypy --config-file pyproject.toml src/pyArchimate/relationship.py --disallow-untyped-defs` to verify
- [ ] T067 [P] [US4] Add type annotations to `src/pyArchimate/element.py` (14 violations): run `mypy --config-file pyproject.toml src/pyArchimate/element.py --disallow-untyped-defs` to verify
- [ ] T068 [P] [US4] Add type annotations to `src/pyArchimate/readers/archimateReader.py` (12 violations): run `mypy --config-file pyproject.toml src/pyArchimate/readers/archimateReader.py --disallow-untyped-defs` to verify
- [ ] T069 [P] [US4] Add type annotations to `src/pyArchimate/constants.py` (7 violations) and `src/pyArchimate/writers/__init__.py` (4 violations): run `mypy --config-file pyproject.toml` on both files to verify
- [ ] T070 [P] [US4] Add type annotations to `src/pyArchimate/helpers/properties.py` (4 violations), `src/pyArchimate/logger.py` (3 violations), `src/pyArchimate/readers/archiReader.py` (3 violations): run `mypy --config-file pyproject.toml` on all three to verify
- [ ] T071 [P] [US4] Add type annotations to remaining src files with violations (readers/arisAMLreader.py, readers/_arisamlreader_helpers.py, writers/archimateWriter.py, writers/archiWriter.py, viewpoint_registry.py — ~2 violations each): run `mypy src/ --disallow-untyped-defs` to confirm zero violations across all files
- [ ] T072 [US4] Set `disallow_untyped_defs = true` in `pyproject.toml` and remove the `# TODO(009-quality-uplift)` comment; run `mypy src/` to confirm 0 errors; run `pytest tests/` to confirm suite green; commit: `fix(mypy): enable disallow_untyped_defs — add type annotations to all src functions`

**Checkpoint**: `mypy src/` passes with `disallow_untyped_defs = true`; all 162 functions in src/ are annotated.

---

## Phase 12: US4 Extension — Mypy `disallow_untyped_calls`

**Goal**: Confirm `disallow_untyped_calls` violations resolved by Phase 11; remove `# TODO(009-quality-uplift)` for this flag.

**Independent Test**: `mypy src/` passes after setting `disallow_untyped_calls = true` in `pyproject.toml`.

- [ ] T073 [US4] After Phase 11, run `mypy src/ --disallow-untyped-calls --no-error-summary` and count remaining violations; all 89 prior violations called our own functions, so count should be 0, but verify before proceeding
- [ ] T074 [US4] If residual violations remain (calls to third-party untyped functions): add `# type: ignore[no-untyped-call]  # third-party stub missing: <library>` at each remaining call site; re-run `mypy src/ --disallow-untyped-calls` to confirm 0 errors
- [ ] T075 [US4] Set `disallow_untyped_calls = true` in `pyproject.toml` and remove the `# TODO(009-quality-uplift)` comment; run `mypy src/` to confirm 0 errors; commit: `fix(mypy): enable disallow_untyped_calls`

**Checkpoint**: `mypy src/` passes with both `disallow_untyped_defs = true` and `disallow_untyped_calls = true`.

---

## Phase 13: Final Feature Completion

**Purpose**: Full cross-tool verification; confirm all TODO(009) markers removed.

- [ ] T076 Run `ruff check` — must pass with UP + PT + N + A + all existing rules active
- [ ] T077 Run `pyright src/` — must pass; no regressions from Phase 11 type annotation changes
- [ ] T078 Run `mypy src/` — must pass with `disallow_untyped_defs = true` and `disallow_untyped_calls = true`
- [ ] T079 Run full test suite: `bash scripts/pre_push_checks.sh` — all unit, integration, and BDD tests must pass
- [ ] T080 Confirm `grep -r "TODO(009-quality-uplift)" pyproject.toml` returns no output — all four TODO markers removed; also run `grep legacy_integration sonar-project.properties` to confirm FR-009 exclusion is unchanged
- [ ] T081 Update `specs/009-quality-uplift/spec.md` Remaining Work table to mark all items complete; commit: `docs(009): mark all deferred items resolved — feature complete`

**Checkpoint**: Feature 009 complete. All four `# TODO(009-quality-uplift)` markers gone; ruff (UP+PT+N+A), pyright, mypy all green; full test suite passing.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phases 1–8**: Complete (all tasks [X])
- **Phase 9 (UP)**: Independent — can start now
- **Phase 10 (PT)**: Independent — can start now; T057–T061 can run in parallel with Phase 9
- **Phase 11 (untyped_defs)**: Independent — can start now; T064–T071 are parallel within the phase
- **Phase 12 (untyped_calls)**: Depends on Phase 11 (T073 must follow T072)
- **Phase 13 (final)**: Depends on Phases 9, 10, 11, 12 all complete

### Parallel Opportunities (remaining work)

```bash
# Phases 9, 10, and 11 can all start simultaneously:
Phase 9: T050 → T051 → T052 → T053  (UP rule set)
Phase 10: T054 → T055 → [T056-T061 parallel] → T062 → T063  (PT rule set)
Phase 11: T064-T071 parallel → T072  (disallow_untyped_defs annotations)

# Phase 12 follows Phase 11:
Phase 12: T073 → T074 → T075  (disallow_untyped_calls)

# Phase 13 follows all:
Phase 13: T076-T080 → T081
```

---

## Requirements Traceability Matrix

| Requirement | Type | Task IDs | User Story | Success Criteria |
|-------------|------|----------|------------|-----------------|
| FR-001: All SonarCloud issues reviewed | FR | T007, T008, T009 | US1 | SC-001 |
| FR-002: SonarCloud Quality Gate passes | FR | T010, T011 | US1 | SC-001 |
| FR-003: No new violations introduced | FR | T010, T025, T032, T037, T045, T046, T076–T079 | All | SC-007 |
| FR-004: Each ruff addition committed independently | FR | T013, T015, T018, T022, T025, T053, T063 | US2 | SC-002 |
| FR-005: Pyright staged warning→error | FR | T027–T032 | US3 | SC-003 |
| FR-006: Mypy flags committed independently | FR | T037, T039, T041, T072, T075 | US4 | SC-004 |
| FR-007: Exclusion removal verified by tool run | FR | T042–T045, T053, T063, T072, T075 | US5 | SC-005 |
| FR-008: All suppressions have justification | FR | T007–T009, T014, T021, T026, T034, T044, T050, T054, T074 | All | SC-006 |
| FR-009: tests/legacy_* exclusions unchanged | FR | T054 (per-file-ignore, not removal) | — | — |
| FR-010: Existing tests pass after each batch | FR | T051, T055, T063, T072, T075, T079 | All | SC-007 |
| SC-002: ≥2 ruff rule sets active (UP+PT added) | SC | T053, T063 | US2 | — |
| SC-004: Both mypy flags re-enabled | SC | T072, T075 | US4 | — |
| SC-005: All obsolete exclusions removed | SC | T080 (zero TODO markers) | US5 | — |
| SC-007: Full test suite passes | SC | T079 | All | — |

---

## Implementation Strategy

### Remaining Work (all deferred items)

Execute phases in this order:
1. **Phase 9 + 10 + 11** in parallel (UP rule, PT rule, type annotations)
2. **Phase 12** after Phase 11 (disallow_untyped_calls after defs annotated)
3. **Phase 13** after all above (final validation + feature closure)

### Notes

- [P] tasks operate on different files and have no incomplete-task dependencies
- All suppression comments must include `# <reason>` — no bare `# noqa` or `# type: ignore`
- UP auto-fix (`ruff --fix`) is safe: all 121 auto-fixable violations are mechanical transforms
- PT011 fixes require judgment: add `match=` where exception message is stable; use `# noqa: PT011  # <reason>` only if message is implementation-specific or non-deterministic
- Phase 11 annotation work: prefer concrete types over `Any`; use `Any` only with justification comment
- After Phase 11, `disallow_untyped_calls` violations expected to drop to 0 (all 89 were calls to our own now-annotated functions)
