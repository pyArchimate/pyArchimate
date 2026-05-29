# Tasks: Fix Code Complexity & Pre-commit Enforcement

**Input**: Design documents from `specs/014-complexity-precommit/`  
**Branch**: `014-complexity-precommit`  
**Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story this task belongs to (US0–US3)

---

## Requirements Traceability Matrix

| Req ID | Type | Task IDs | User Story | Success Criteria |
|--------|------|----------|------------|-----------------|
| FR-000 | FR | T003, T004, T005 | US0 | SC-008, SC-009 |
| FR-001 | FR | T006–T015 | US1 | SC-001, SC-002, SC-003 |
| FR-002 | FR | T006–T015 | US1 | SC-006 |
| FR-003 | FR | T012, T015 | US1 | SC-006, SC-010 |
| FR-004 | FR | T017 | US2 | SC-004, SC-005 |
| FR-005 | FR | T016 | US2 | SC-007 |
| FR-006 | FR | T017 | US2 | SC-004 |
| FR-007 | FR | T021 | US2 | SC-007 |
| FR-008 | FR | T017, T019 | US2 | SC-004, SC-005 |

---

## Phase 1: Setup

**Purpose**: Verify tooling is ready and record the coverage baseline before any changes.

- [X] T001 Run `poetry run ruff check src/ --select C901` and confirm all 15 violations are reported across the 8 affected files; save output for reference
- [X] T002 Run `poetry run pytest --cov=src/pyArchimate --cov-report=term-missing -q` and confirm coverage baselines from `data-model.md` match: `view/layout/__init__.py` ≈ 43%, `segment_separation.py` ≈ 71%, all others ≥ 73%

**Checkpoint**: Baselines confirmed — P0 coverage uplift can begin

---

## Phase 2: Foundational — Coverage Uplift (US0, P0 pre-condition)

**Purpose**: Raise test coverage for the two at-risk files to ≥ 80% before any refactoring touches them. FR-000 blocks all US1 refactoring of these files until complete.

**⚠️ CRITICAL**: T013 and T014 (refactoring `segment_separation.py` and `view/layout/__init__.py`) MUST NOT start until T005 is complete.

- [X] T003 [US0] Add tests covering `auto_route()`, `_apply_node_move_fallback()`, `_find_candidate_node_moves()`, and `_apply_node_move()` in `tests/unit/view/layout/test_auto_route.py`; add tests covering `auto_layout()` in `tests/unit/view/layout/test_auto_layout.py` — target: `view/layout/__init__.py` line coverage ≥ 80%
- [X] T004 [P] [US0] Add tests covering `_enforce_min_turn_segment()` (lines 227–289) and `displace_collinear_segments()` edge cases in `tests/unit/test_segment_separation.py` — target: `segment_separation.py` line coverage ≥ 80%
- [X] T005 Run `poetry run pytest --cov=src/pyArchimate/view/layout --cov-report=term-missing -q` and confirm `view/layout/__init__.py` ≥ 80% AND `segment_separation.py` ≥ 80%; DO NOT proceed to T013/T014 until both gates pass

**Checkpoint**: Both P0 files at ≥ 80% coverage — refactoring of at-risk files is now safe

---

## Phase 3: User Story 1 — Refactor Complex Functions (Priority: P1) 🎯 MVP

**Goal**: Resolve all 15 SonarCloud `S3776` cognitive complexity violations by decomposing overly-nested functions into private `_`-prefixed helpers in the same file. No public API changes.

**Independent Test**: Run `poetry run ruff check src/ --select C901` (zero C901 violations) and `poetry run pytest` (all tests pass, no coverage regression).

### Batch A — Safe Files (84%+ coverage, can run immediately in parallel)

- [X] T006 [P] [US1] Refactor `readers/archiReader.py`: decompose `archi_reader()` (triple `findall` loop chains + if/else type detection) — extract `_read_folder_elements(folder, root)` and `_detect_element_type(element)` as private helpers in the same file
- [X] T007 [P] [US1] Refactor `readers/archimateReader.py`: decompose the complex view-reading function — extract `_read_view_elements(view_elem)` and `_read_view_connections(view_elem)` as private helpers in the same file
- [X] T008 [P] [US1] Refactor `model.py`: run `poetry run ruff check src/pyArchimate/model.py --select C901` to identify the specific function, then decompose it into private helpers in the same file
- [X] T009 [P] [US1] Refactor `view/__init__.py`: run `poetry run ruff check src/pyArchimate/view/__init__.py --select C901` to identify the specific function, then decompose it into private helpers in the same file
- [X] T010 [P] [US1] Refactor `view/layout/layout_engine.py`: decompose `assign_grid_cells()` (4-level nested for + layer direction branching) — extract `_assign_vertical_cells(grid, layer)` and `_assign_horizontal_cells(grid, layer)` as private helpers in the same file
- [X] T011 [P] [US1] Refactor `view/layout/export/svg_export.py`: run `poetry run ruff check src/pyArchimate/view/layout/export/svg_export.py --select C901` to identify the specific function, then decompose it into private helpers in the same file
- [X] T012 [US1] After T006–T011: run `poetry run pytest --cov=src/pyArchimate --cov-report=term-missing -q` and confirm all tests pass AND each of the 6 refactored files has coverage ≥ its baseline from `data-model.md`; run `poetry run ruff check src/ --select C901` and confirm no C901 violations remain in those 6 files

### Batch B — At-risk Files (requires T005 complete)

- [X] T013 [US1] Refactor `view/layout/routing/segment_separation.py`: decompose `_enforce_min_turn_segment()` (cognitive complexity 34, lines 227–289, 6-level deep if nesting) — extract `_is_horizontal_segment(seg)`, `_needs_extension(seg, threshold)`, and `_apply_min_turn(seg, direction)` as private helpers in the same file (depends on T005)
- [X] T014 [US1] Refactor `view/layout/__init__.py` — 7 violations, execute in this order to control scope:
  1. `auto_layout()`: extract `_place_layer_nodes(layer, nodes)` and `_handle_layout_exception(exc, context)`
  2. `_find_candidate_node_moves()`: extract `_generate_segment_candidates(seg, nodes)`
  3. `_apply_node_move_fallback()`: extract `_attempt_move(node, delta)` and `_undo_move(node, delta)`
  4. `_apply_node_move()`: extract `_detect_overlap(node_a, node_b)`
  5. `auto_route()`: extract `_route_single_connection(conn, obstacles)` and `_post_process_single_waypoints(conn)`
  6. Remaining 2 violations: identify via `ruff check --select C901` and apply same Extract Helper pattern
  
  All helpers stay in `src/pyArchimate/view/layout/__init__.py` (depends on T005)
- [X] T015 [US1] Run full verification: `poetry run pytest` (all tests pass), `poetry run behave` (all BDD scenarios pass), `poetry run ruff check src/ --select C901` (zero violations), `poetry run ruff check src/` (no other ruff regressions); confirm public API contract per `contracts/public-api.md` by importing all listed symbols

**Checkpoint**: All 15 violations resolved, all tests green, public API unchanged — US1 complete

---

## Phase 4: User Story 2 — Pre-commit Hook Setup (Priority: P2)

**Goal**: Wire `ruff check` and `ruff format --check` as pre-commit gates so complexity violations are caught locally at commit time.

**Independent Test**: Attempt `git commit` with a deliberately complex function (McCabe > 15) — commit must be blocked with a readable error. Attempt `git commit` with clean code — commit must succeed.

- [X] T016 [US2] Add `pre-commit` to `[dependency-groups] dev` in `pyproject.toml` (after the existing `vulture` entry); run `poetry install --with dev` to install
- [X] T017 [US2] Create `.pre-commit-config.yaml` at repository root:
  
```yaml
  repos:
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: <pin to latest release compatible with ruff ≥ 0.14.10>
      hooks:
        - id: ruff        # ruff check — lint + complexity gate (read-only)
        - id: ruff-format # ruff format --check — format gate (read-only)
          args: [--check]
  ```
  
All rule config remains in `pyproject.toml` — do not duplicate settings

- [X] T018 [US2] Run `poetry run pre-commit install` to register hooks in `.git/hooks/pre-commit`
- [X] T019 [US2] Verify hooks fire: run `poetry run pre-commit run --all-files` and confirm it exits 0 (all files already pass after T015)
- [X] T020 [US2] Smoke test: create a scratch file `_test_complexity_gate.py` at repo root with a function that has McCabe complexity > 15, stage it, attempt `git commit`, confirm the commit is blocked and the violation is named in the output; then delete the scratch file
- [X] T021 [US2] Update `how_to_build.md`: add a "Pre-commit hooks" section with the one-line activation command `poetry run pre-commit install` and a note explaining what the hooks check

**Checkpoint**: Pre-commit hooks active and blocking overly-complex commits — US2 complete

---

## Phase 5: User Story 3 — SonarCloud Verification (Priority: P3)

**Goal**: Confirm zero open `python:S3776` issues in the cloud quality scanner after merging.

**Independent Test**: Query the SonarCloud API and confirm the `total` field is `0` for rule `python:S3776`.

- [X] T022 [US3] After merging to main: query SonarCloud API to confirm zero open S3776 violations:

  ```bash
  curl -s "https://sonarcloud.io/api/issues/search?projectKeys=pyArchimate_pyArchimate&rules=python:S3776&statuses=OPEN" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('PASS' if d['total']==0 else f'FAIL: {d[\"total\"]} issues remain')"
  ```

  If violations remain, identify which functions still exceed the cognitive complexity threshold (note: SonarCloud S3776 ≠ ruff C901 — some functions may require further decomposition)

**Checkpoint**: Zero SonarCloud S3776 issues confirmed — US3 complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification across all stories and documentation tidy-up.

- [X] T023 [P] Run `poetry run pre-commit run --all-files` and confirm clean exit on the full codebase
- [X] T024 [P] Verify public API contract for all 8 files per `contracts/public-api.md`: import each listed symbol and confirm no `ImportError` or `AttributeError`
- [X] T025 Run `scripts/pre_push_checks.sh` (integration, security, BDD suites) per `how_to_build.md` pre-push guidance
- [X] T026 Commit all remaining staged changes with a conventional commit message: `chore(014): complete complexity refactoring and pre-commit enforcement`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational / US0)**: Depends on Phase 1 — BLOCKS T013, T014
- **Phase 3 Batch A (US1 safe files)**: Can start after Phase 1 — does NOT wait for Phase 2
- **Phase 3 Batch B (US1 at-risk files)**: MUST wait for Phase 2 (T005) completion
- **Phase 4 (US2 pre-commit)**: Can start after Phase 3 (T015) — needs clean codebase
- **Phase 5 (US3 SonarCloud)**: Requires PR merge and SonarCloud scan completion
- **Phase 6 (Polish)**: After Phase 4 complete

### Task-Level Dependencies

```text
T001 → T002 → (T003 ∥ T004) → T005 → T013 → T014
                                              ↓
T001 → (T006 ∥ T007 ∥ T008 ∥ T009 ∥ T010 ∥ T011) → T012 → T014 → T015
                                                                       ↓
                                                         T016 → T017 → T018 → T019 → T020 → T021
                                                                                                ↓
                                                                                    T022 (post-merge)
```

### Parallel Opportunities

- **T003 ∥ T004**: Coverage uplift for the two at-risk files (different test files)
- **T006 ∥ T007 ∥ T008 ∥ T009 ∥ T010 ∥ T011**: All 6 safe-file refactors (different source files)
- **T023 ∥ T024**: Final verifications (independent)

---

## Parallel Example: Batch A Refactoring (US1)

```bash
# All 6 safe-file refactors can run simultaneously:
Task T006: "Refactor readers/archiReader.py — decompose archi_reader()"
Task T007: "Refactor readers/archimateReader.py — decompose _read_views()"
Task T008: "Refactor model.py — identify and decompose complex function"
Task T009: "Refactor view/__init__.py — identify and decompose complex function"
Task T010: "Refactor view/layout/layout_engine.py — decompose assign_grid_cells()"
Task T011: "Refactor view/layout/export/svg_export.py — identify and decompose complex function"
```

---

## Implementation Strategy

### MVP First (US0 + US1)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: US0 coverage uplift (T003–T005) — critical gate
3. Run Batch A refactors in parallel (T006–T011)
4. Verify Batch A (T012)
5. Run Batch B refactors (T013–T014)
6. Full verification (T015)
7. **STOP and VALIDATE**: `ruff check src/ --select C901` must be clean, all tests green

### Incremental Delivery

1. US0 + US1 → zero ruff C901 violations, full test suite green → MVP ✅
2. US2 → pre-commit hooks installed, contributors protected → Incremental delivery ✅
3. US3 → SonarCloud confirmed clean post-merge → Full acceptance ✅

---

## Notes

- Each refactoring task should be committed individually with `refactor(<module>): <description>`
- Each coverage uplift task should be committed with `test(<module>): uplift coverage to N%`
- After T015: run `poetry run ruff check src/` (not just `--select C901`) to confirm no unintended ruff regressions from the refactoring
- SonarCloud uses cognitive complexity (S3776) which differs from ruff's McCabe (C901). After T015, if ruff is clean but SonarCloud still flags a function, further decomposition is needed — the function may have deeply nested boolean operators or short-circuit conditions that inflate cognitive score without affecting McCabe
- `vulture` (dead code detection) is already in dev deps; it can be added to `.pre-commit-config.yaml` in a future feature — out of scope here
