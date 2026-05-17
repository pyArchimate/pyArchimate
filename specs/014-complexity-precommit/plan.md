# Implementation Plan: Fix Code Complexity & Pre-commit Enforcement

**Branch**: `014-complexity-precommit` | **Date**: 2026-05-17 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/014-complexity-precommit/spec.md`

## Summary

Resolve all 15 CRITICAL SonarCloud `python:S3776` (cognitive complexity) violations across 8 source
files by decomposing overly-nested functions into private in-file helpers, preceded by a coverage
uplift for the two under-tested hotspot files. Simultaneously introduce `.pre-commit-config.yaml`
wiring `ruff check` + `ruff format --check` on staged files, add `pre-commit` to the dev dependency
group, and document the one-line hook activation command. No new modules, no public API changes.

## Technical Context

**Language/Version**: Python 3.10–3.14 (per `pyproject.toml requires-python`)  
**Primary Dependencies**: ruff ≥ 0.14.10 (already in `lint` group); `pre-commit` (new, dev group)  
**Storage**: File I/O only — `.archimate` archives (zip + XML)  
**Testing**: pytest (unit/integration), behave (BDD acceptance), pytest-cov (coverage)  
**Target Platform**: Linux, macOS, Windows (pre-commit hook must be cross-platform)  
**Project Type**: Library  
**Performance Goals**: Pre-commit stage ≤ 10 seconds on developer machine (SC-005); blocking commit ≤ 5 seconds (SC-004)  
**Constraints**: No public API changes (FR-002); no new sub-modules (clarification Q1); all helpers stay in-file  
**Scale/Scope**: 8 files, 15 functions, ~150 minutes SonarCloud-estimated remediation effort

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | ✅ Pass | This feature directly targets the violation. Helpers must be ≤ 30 lines, descriptively named per TECHNICAL.md |
| II. Testing Standards | ✅ Pass | Coverage uplift (P0) before any refactoring; 80% floor for at-risk files; TDD cycle applies |
| III. UX Consistency | N/A | Library — no user interface changes |
| IV. Performance | ✅ Pass | SC-004/SC-005 bound pre-commit timing; simpler functions reduce call-graph overhead |
| V. Security | N/A | No new external inputs or auth surfaces |
| VI. State Management | N/A | No entity lifecycle changes |
| VII. System Integrity & Accuracy | ✅ Pass | FR-002 prohibits API changes; FR-003 requires tests pass after every file |
| VIII. Durability & Interoperability | ✅ Pass | No format changes; no new modules; helpers stay in-file |
| IX. Cross-Platform Consistency | ✅ Pass | `.pre-commit-config.yaml` must be tested on Linux/macOS/Windows |
| PROJECT III (pyproject.toml single source of truth) | ✅ Pass | `astral-sh/ruff-pre-commit` reads `pyproject.toml` — no config duplication |

**All gates clear. No violations.**

## Project Structure

### Documentation (this feature)

```text
specs/014-complexity-precommit/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── public-api.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
src/pyArchimate/
├── model.py                              # 1 violation — refactor in place
├── view/
│   ├── __init__.py                       # 1 violation — refactor in place
│   └── layout/
│       ├── __init__.py                   # 7 violations — refactor in place (primary hotspot)
│       ├── layout_engine.py              # 1 violation — refactor in place
│       ├── export/
│       │   └── svg_export.py             # 1 violation — refactor in place
│       └── routing/
│           └── segment_separation.py     # 1 violation — refactor in place (worst function)
└── readers/
    ├── archimateReader.py                # 1 violation — refactor in place
    └── archiReader.py                    # 1 violation — refactor in place

tests/
├── unit/
│   ├── view/layout/
│   │   ├── test_auto_layout.py           # extend for P0 coverage uplift
│   │   └── test_auto_route.py            # extend for P0 coverage uplift
│   └── test_segment_separation.py        # extend for P0 coverage uplift
└── [all other existing test files]       # must not regress (SC-010)

.pre-commit-config.yaml                   # NEW — ruff check + ruff format --check
pyproject.toml                            # UPDATE — add pre-commit to [dependency-groups] dev
how_to_build.md                           # UPDATE — add hook activation command
```

**Structure Decision**: Single-project layout (Option 1). No new modules. All extracted helpers are
private (`_`-prefixed), co-located in the same file as the refactored function, per clarification Q1.

## Complexity Tracking

No constitution violations to justify.

---

## Phase 0: Research

### Findings

#### Affected Functions (by file)

| File | Function | SonarCloud Complexity | McCabe Est. | Lines | Dominant Pattern |
|------|----------|-----------------------|-------------|-------|-----------------|
| `view/layout/__init__.py` | `auto_route()` | > 15 | ~25 | 113 | 4-level nested for + nested if + try/except |
| `view/layout/__init__.py` | `auto_layout()` | > 15 | ~15 | 76 | 3-level nested if + 2-level nested for |
| `view/layout/__init__.py` | `_find_candidate_node_moves()` | > 15 | ~15 | 57 | Double nested loop over segments × nodes |
| `view/layout/__init__.py` | `_apply_node_move_fallback()` | > 15 | ~14 | 60 | Triple nested loop, fallback chains |
| `view/layout/__init__.py` | `_apply_node_move()` | > 15 | ~14 | 50 | Overlap detection with nested node iteration |
| `view/layout/__init__.py` | _(2 more TBD)_ | > 15 | TBD | TBD | TBD |
| `view/layout/routing/segment_separation.py` | `_enforce_min_turn_segment()` | 34 (worst) | ~13 | 62 | 6-level deep if nesting, while loop |
| `view/layout/layout_engine.py` | `assign_grid_cells()` | > 15 | ~14 | 72 | 4-level nested for, layer direction branching |
| `view/layout/export/svg_export.py` | _(TBD at impl)_ | > 15 | TBD | TBD | TBD |
| `view/__init__.py` | _(TBD at impl)_ | > 15 | TBD | TBD | TBD |
| `readers/archimateReader.py` | `_read_views()` | > 15 | ~11 | 28 | Two-pass XML traversal |
| `readers/archiReader.py` | `archi_reader()` | > 15 | ~15 | 41 | Triple `findall` loop chains + if/else type detection |
| `model.py` | _(TBD at impl)_ | > 15 | TBD | TBD | TBD |

> Note: SonarCloud cognitive complexity (S3776) and ruff McCabe complexity (C901) use different
> algorithms. A function may clear C901 but still fail S3776. Both must be verified post-refactor.

#### Pre-commit Tool Decision

- **Decision**: Use `astral-sh/ruff-pre-commit` hooks
- **Rationale**: Official ruff hooks, actively maintained, read `pyproject.toml` for all config,
  no duplication of rules required. Single repo dependency avoids version drift.
- **Alternatives considered**: Local `ruff` hook via `language: system` — rejected because it
  requires the developer's venv to be active, breaking cold-clone workflows.

#### Ruff Hook Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v<pin to latest ruff-pre-commit release compatible with ruff ≥ 0.14.10>
    hooks:
      - id: ruff            # runs ruff check (read-only, exits non-zero on violation)
      - id: ruff-format     # runs ruff format (read-only with --check flag below)
        args: [--check]
```

All rule configuration (including `C901`, `max-complexity = 15`, `select`, `ignore`) comes from
`pyproject.toml` `[tool.ruff.lint]` — no settings are duplicated in `.pre-commit-config.yaml`.

#### Coverage Baseline (from `build/coverage.xml`)

| File | Current Coverage | P0 Target | Risk |
|------|-----------------|-----------|------|
| `view/layout/__init__.py` | 43% | ≥ 80% | High — must uplift first |
| `view/layout/routing/segment_separation.py` | 71% | ≥ 80% | Medium — must uplift first |
| `view/layout/layout_engine.py` | 86% | ≥ 86% (no regression) | Low |
| `view/layout/export/svg_export.py` | 73% | ≥ 73% (no regression) | Medium |
| `view/__init__.py` | 88% | ≥ 88% (no regression) | Low |
| `readers/archimateReader.py` | 98% | ≥ 98% (no regression) | Negligible |
| `readers/archiReader.py` | 84% | ≥ 84% (no regression) | Low |
| `model.py` | 96% | ≥ 96% (no regression) | Negligible |

---

## Phase 1: Design & Contracts

### Refactoring Strategy (per file)

#### `view/layout/__init__.py` — 7 violations

Apply the **Extract Helper** pattern for each complex function. All helpers are `_`-prefixed and
remain in the same file.

| Complex Function | Extracted Helpers (proposed) | Rationale |
|-----------------|------------------------------|-----------|
| `auto_route()` | `_route_single_connection()`, `_post_process_single_waypoints()` | Isolate the per-connection routing body from the outer loop |
| `auto_layout()` | `_place_layer_nodes()`, `_handle_layout_exception()` | Separate layer iteration from exception recovery |
| `_find_candidate_node_moves()` | `_generate_segment_candidates()` | Extract inner loop body into a function with clear inputs/outputs |
| `_apply_node_move_fallback()` | `_attempt_move()`, `_undo_move()` | Separate attempt phase from rollback phase |
| `_apply_node_move()` | `_detect_overlap()` | Extract overlap detection predicate |
| _(remaining 2 functions)_ | TBD at implementation time | Follow same Extract Helper pattern |

#### `view/layout/routing/segment_separation.py` — 1 violation (complexity 34)

`_enforce_min_turn_segment()` at line 227 has 6-level deep if nesting. Extract:
- `_is_horizontal_segment(seg)` — orientation predicate
- `_needs_extension(seg, threshold)` — extension condition predicate
- `_apply_min_turn(seg, direction)` — mutation logic

#### `view/layout/layout_engine.py` — 1 violation

`assign_grid_cells()`: extract layer-direction-specific logic into `_assign_vertical_cells()` and
`_assign_horizontal_cells()`, called conditionally.

#### `view/layout/export/svg_export.py` — 1 violation

TBD at implementation — apply Extract Helper once the specific function is confirmed via ruff output.

#### `view/__init__.py` — 1 violation

TBD at implementation — apply Extract Helper once the specific function is confirmed.

#### `readers/archimateReader.py` — 1 violation

`_read_views()`: extract the two-pass logic into `_read_view_elements()` and
`_read_view_connections()` helpers.

#### `readers/archiReader.py` — 1 violation

`archi_reader()`: extract the three sequential `findall` traversals into
`_read_folder_elements()`, consolidating type detection into a dispatch helper.

#### `model.py` — 1 violation

TBD at implementation — apply Extract Helper once the specific function is confirmed.

### Implementation Sequence (dependency order)

Execute file-by-file. Run `pytest` + coverage after each file. No file is touched unless its P0
coverage gate is met.

```
[P0] Uplift: view/layout/__init__.py tests → ≥ 80%
[P0] Uplift: segment_separation.py tests → ≥ 80%
[P1] Refactor: readers/archiReader.py          (84% — safe)
[P1] Refactor: readers/archimateReader.py       (98% — safe)
[P1] Refactor: model.py                         (96% — safe)
[P1] Refactor: view/__init__.py                 (88% — safe)
[P1] Refactor: view/layout/layout_engine.py     (86% — safe)
[P1] Refactor: view/layout/export/svg_export.py (73% — safe after confirming no regression)
[P1] Refactor: view/layout/routing/segment_separation.py  (after P0 uplift)
[P1] Refactor: view/layout/__init__.py          (after P0 uplift — last, most complex)
[P2] Pre-commit: add .pre-commit-config.yaml
[P2] Pre-commit: update pyproject.toml (dev dep)
[P2] Pre-commit: update how_to_build.md
```

### Data Model

No new domain entities. The only new artifact is the pre-commit configuration file.

**Pre-commit configuration structure**:

```
.pre-commit-config.yaml
  repos[]
    repo: astral-sh/ruff-pre-commit   (external hook repo)
    rev: <pinned version>
    hooks[]
      id: ruff                         (check-only lint gate)
      id: ruff-format                  (check-only format gate, args: [--check])
```

All behaviour is governed by `pyproject.toml` `[tool.ruff]` sections — the config file is a
thin wiring layer only.

### Public API Contract

FR-002 prohibits changes to any public symbol in the 8 affected files. The contract is: every
name currently importable without a leading `_` from these modules must remain importable with the
same signature after refactoring.

See `contracts/public-api.md` for the enumerated symbol list.
