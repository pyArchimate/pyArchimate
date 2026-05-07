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

- [ ] T004 Query SonarCloud API using `SONAR_TOKEN` from `.env` and save the open issue list: `curl -u "$SONAR_TOKEN:" "https://sonarcloud.io/api/issues/search?projectKeys=pyArchimate_pyArchimate&severities=CRITICAL,MAJOR,MINOR&statuses=OPEN,CONFIRMED" > /tmp/sonar_issues.json`
- [ ] T005 Review `/tmp/sonar_issues.json` and append a `## SonarCloud Triage` section to `specs/009-quality-uplift/research.md` containing a table (issue key, rule, severity, file, line) for use in Phase 3
- [X] T006 Run `bash scripts/pre_commit_checks.sh` to confirm baseline suite is green before any changes

**Checkpoint**: Baseline confirmed, SonarCloud triage table ready — story work can now begin.

---

## Phase 3: User Story 1 — Remediate Remaining SonarQube Issues (Priority: P1)

**Goal**: Clear all open SonarCloud issues so the Quality Gate passes.

**Independent Test**: `pysonar --sonar-token=<SONAR_TOKEN>` scan shows Quality Gate = Passed with zero unresolved issues (excluding `tests/legacy_*`).

- [ ] T007 [US1] Fix or suppress each **CRITICAL** SonarCloud issue from the triage table in `specs/009-quality-uplift/research.md`; add `# NOSONAR <reason>` for confirmed false positives
- [ ] T008 [US1] Fix or suppress each **MAJOR** SonarCloud issue from the triage table in `specs/009-quality-uplift/research.md`
- [ ] T009 [US1] Fix or suppress each **MINOR** SonarCloud issue and any security hotspots from the triage table in `specs/009-quality-uplift/research.md`
- [ ] T010 [US1] Run `bash scripts/pre_commit_checks.sh` to verify no regressions after all fixes
- [ ] T011 [US1] Commit: `fix(sonar): resolve remaining SonarCloud issues`

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

### Batch 6b — Evaluate disallow_untyped_defs (stretch goal)

- [X] T038 [US4] Run `mypy src/ --disallow-untyped-defs` and count violations; record the count
- [X] T039 [US4] If violation count ≤ 20: fix all unannotated function signatures in the affected files, set `disallow_untyped_defs = true` in `pyproject.toml`, run `mypy src/` to confirm clean, commit: `fix(mypy): enable disallow_untyped_defs`; if > 20: add `# TODO(009-quality-uplift): Enable disallow_untyped_defs — <N> violations; deferred as stretch goal` to `pyproject.toml` and commit: `chore(mypy): document disallow_untyped_defs as deferred stretch goal`
- [X] T040 [US4] Run `mypy src/ --disallow-untyped-calls` and count violations; record the count
- [X] T041 [US4] If violation count ≤ 20: fix all call sites, set `disallow_untyped_calls = true` in `pyproject.toml`, run `mypy src/` to confirm clean, commit: `fix(mypy): enable disallow_untyped_calls`; if > 20: add `# TODO(009-quality-uplift): Enable disallow_untyped_calls — <N> violations; deferred as stretch goal` to `pyproject.toml` and commit: `chore(mypy): document disallow_untyped_calls as deferred stretch goal`

**Checkpoint**: `mypy src/` passes with 0 baseline errors. `disallow_untyped_defs` and `disallow_untyped_calls` each either enabled or deferred with documented count.

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

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 (triage table must exist)
- **US2 (Phase 4)**: Independent of US1; depends on Phase 2 only
- **US3 (Phase 5)**: Independent of US1/US2; depends on Phase 2 only (T026 can run in parallel with US1/US2)
- **US4 (Phase 6)**: T034 depends on T026 completion (same line in `_arisamlreader_helpers.py:61`); T040/T041 follow T039; otherwise independent
- **US5 (Phase 7)**: Depends on Phase 4 (ruff ignores removed), Phase 5 (pyright categories re-enabled), Phase 6 (mypy flags documented) — must be last story phase
- **Polish (Phase 8)**: Depends on all story phases

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories
- **US2 (P1)**: No dependency on US1; can run in parallel with US1
- **US3 (P2)**: No dependency on US1/US2; can start after foundational
- **US4 (P2)**: T034 coordinate with T026 (PIL comment in same file); otherwise independent
- **US5 (P3)**: Must follow US2, US3, US4 to audit the final state of pyproject.toml

### Within Each Phase

- Batches are sequential within a phase (4a → 4b → 4c → 4d)
- Tasks marked [P] within a batch can run in parallel
- Always run the suite check before committing (T010, T025, T032, T037, T045)

### Parallel Opportunities

```bash
# US1 and US2 can run in parallel after Phase 2:
Task: T007-T011 (SonarCloud fixes)
Task: T012-T025 (Ruff rule enablement)

# Within Phase 5 Batch 5c:
Task: T030 (reportArgumentType → "error")
Task: T031 (reportOptionalMemberAccess → "error")

# Within Phase 6 Batch 6a:
Task: T035 (archimateWriter.py no-any-return)
Task: T036 (archiWriter.py no-any-return)
```

---

## Requirements Traceability Matrix

| Requirement | Type | Task IDs | User Story | Success Criteria |
|-------------|------|----------|------------|-----------------|
| FR-001: All SonarCloud issues reviewed | FR | T007, T008, T009 | US1 | SC-001 |
| FR-002: SonarCloud Quality Gate passes | FR | T010, T011 | US1 | SC-001 |
| FR-003: No new violations introduced | FR | T010, T025, T032, T037, T045, T046 | All | SC-007 |
| FR-004: Each ruff addition committed independently | FR | T013, T015, T018, T022, T025 | US2 | SC-002 |
| FR-005: Pyright staged warning→error | FR | T027–T032 | US3 | SC-003 |
| FR-006: Mypy flags committed independently | FR | T037, T039, T040, T041 | US4 | SC-004 |
| FR-007: Exclusion removal verified by tool run | FR | T042–T045 | US5 | SC-005 |
| FR-008: All suppressions have justification | FR | T007–T009, T014, T021, T026, T034, T044 | All | SC-006 |
| FR-009: tests/legacy_* exclusions unchanged | FR | (policy — no task needed) | — | — |
| FR-010: Existing tests pass after each batch | FR | T006, T010, T025, T032, T037, T045, T046 | All | SC-007 |
| SC-001: SonarCloud Gate → Passed | SC | T011 | US1 | — |
| SC-002: ≥2 ruff rule sets active | SC | T018, T022 | US2 | — |
| SC-003: ≥2 pyright categories at "error" | SC | T029, T030, T031 | US3 | — |
| SC-004: ≥1 mypy flag re-enabled | SC | T037, T039, T040, T041 | US4 | — |
| SC-005: ≥1 obsolete exclusion removed | SC | T042, T043 | US5 | — |
| SC-006: Zero unexplained suppressions | SC | T047 (checklist audit) | All | — |
| SC-007: Full test suite passes | SC | T046 | All | — |

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (query SonarCloud)
3. Complete Phase 3: US1 — SonarCloud remediation
4. **STOP and VALIDATE**: `pysonar` scan shows Quality Gate = Passed
5. Continue to US2 if time allows

### Incremental Delivery

1. Setup + Foundational → baseline confirmed
2. US1 (SonarCloud) → Quality Gate clean
3. US2 (Ruff A + N) → linter coverage expanded
4. US3 (Pyright) → type safety improved
5. US4 (Mypy) → strict compliance strengthened
6. US5 (Exclusion audit) → no silent suppressions
7. Polish → feature complete

---

## Notes

- [P] tasks operate on different files and have no incomplete-task dependencies
- All suppression comments must include `# <reason>` — no bare `# noqa` or `# type: ignore`
- Commit after each batch (not after each individual task) to keep history readable
- UP and PT rule sets are deliberately deferred — TODO comments in `pyproject.toml` document why
- T039 (disallow_untyped_defs) branches based on violation count discovered at runtime
