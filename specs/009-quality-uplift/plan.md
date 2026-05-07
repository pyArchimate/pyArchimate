# Implementation Plan: Incremental Code Quality Uplift

**Branch**: `009-quality-uplift` | **Date**: 2026-05-03 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/009-quality-uplift/spec.md`

## Summary

Remediate all remaining SonarCloud issues, incrementally enable four ruff rule sets (`N`, `A`, `UP`, `PT`), re-enable suppressed pyright categories, strengthen mypy strict compliance, and remove obsolete `pyproject.toml` exclusions. Work is executed tool-by-tool in small, independently-passing commits.

## Technical Context

**Language/Version**: Python 3.12 (target; min 3.10)  
**Primary Dependencies**: lxml, oyaml, pillow, ruff, pyright, mypy  
**Storage**: File I/O only (no database)  
**Testing**: pytest (unit/integration), behave (BDD)  
**Target Platform**: Linux (dev container / CI)  
**Project Type**: Library (`src/pyArchimate/`)  
**Performance Goals**: N/A (tooling change only)  
**Constraints**: Every commit must leave the full pre-commit suite green; no new violations introduced  
**Scale/Scope**: ~28 source files, ~10 test modules

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Assessment | Notes |
|-----------|------------|-------|
| I. Code Quality | ✅ Pass | Feature directly improves quality metrics |
| II. Testing Standards | ✅ Pass | All existing tests must remain green; no tests removed |
| III. UX Consistency | ✅ N/A | Library — no user-facing interface changes |
| IV. Performance | ✅ Pass | No runtime code changes in this feature |
| V. Security | ✅ Pass | Sonar security hotspot fixes are included |
| VI. State Management | ✅ N/A | No state transitions affected |
| VII. System Integrity | ✅ Pass | Fixes must not alter observable behaviour |
| VIII. Durability | ✅ Pass | pyproject.toml changes are forward-compatible |
| IX. Cross-Platform | ✅ Pass | Tool config changes apply to all platforms |

No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/009-quality-uplift/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (N/A — no new entities)
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/pyArchimate/          # Core library (~28 .py files)
├── model.py
├── element.py
├── relationship.py
├── view.py
├── readers/
│   ├── archimateReader.py
│   ├── archiReader.py
│   ├── _arisamlreader_helpers.py   # PIL import issue
│   └── ...
└── writers/
    ├── archimateWriter.py           # no-any-return issues
    ├── archiWriter.py               # no-any-return issues
    └── ...

tests/
├── unit/
├── integration/
├── legacy_unit/         # Excluded from static analysis
├── legacy_integration/  # Excluded from static analysis
└── features/            # BDD

pyproject.toml           # Tool config changes land here
sonar-project.properties # SonarCloud exclusions (unchanged)
```

**Structure Decision**: Single-project library layout. No new files needed beyond config edits and targeted source fixes.

## Complexity Tracking

**TDD deviation (Constitution II)**: This feature modifies only tool configuration (`pyproject.toml`) and repairs pre-existing static-analysis violations in existing code. No new business logic is introduced, so the Red-Green-Refactor cycle does not apply. The existing test suite remains the correctness gate; every task includes a tool-run verification step before commit.

---

## Phase 0: Research

*Resolved unknowns captured in [research.md](./research.md).*

---

## Phase 1: Design

### Tool-by-Tool Implementation Plan

Work proceeds in the following order to minimize interference between changes:

#### Batch 1 — SonarCloud Remediation (User Story 1)

1. Query the SonarCloud API (URL in spec References) with the project SONAR_TOKEN from `.env` to retrieve all open CRITICAL/MAJOR/MINOR issues.
2. Triage each issue:
   - **Bug / Code Smell**: Fix inline.
   - **False positive (e.g., lxml dynamic types)**: Add `# NOSONAR <reason>` comment.
   - **Security hotspot**: Verify, fix or accept with justification.
3. Run `scripts/pre_commit_checks.sh` to verify no regressions.
4. Commit: `fix(sonar): resolve remaining SonarCloud issues`

#### Batch 2 — Remove Obsolete Ruff Ignores + Enable C901 (User Story 5 + Story 2 prerequisite)

Current ruff ignore list: `["E501", "C901", "N999", "PLC0415"]`

**C901 (complexity)**: 6 violations remain in src. Each function is evaluated:
- If complexity is addressable (extract helper), fix it.
- Remove `"C901"` from the ignore list once clean.
- Commit: `fix(ruff): resolve remaining C901 complexity violations`

**PLC0415 (non-top-level import)**: Audit dynamic import usage. If the pattern is truly needed, replace the global ignore with a `# noqa: PLC0415  # dynamic import required for <reason>` at the call site. Remove from ignore list.
- Commit: `fix(ruff): replace PLC0415 global ignore with targeted suppressions`

#### Batch 3 — Enable Ruff Rule Set `A` (User Story 2)

Current violations: **6** (within 20-violation cap)
- `A001`: 2 × builtin variable shadowing
- `A003`: 4 × builtin attribute shadowing

Fix each violation (rename the variable/attribute). Add `A` to `[tool.ruff.lint] select`.
- Commit: `feat(ruff): enable A (builtin-shadowing) rule set`

#### Batch 4 — Enable Ruff Rule Set `N` (User Story 2)

Current violations: **18** (within 20-violation cap)
- `N999` (invalid module name): 11 hits — these are the `camelCase` module files already documented in the existing `N999` ignore. Evaluate whether to rename or suppress per-file.
  - If files can be renamed without breaking imports: rename + update all import sites.
  - If renaming breaks external API: add `# noqa: N999` to each affected module's top line and document why.
  - Remove `"N999"` from the global ignore list in either case (replaced by targeted suppressions or eliminated).
- `N811` (constant imported as non-constant): 6 hits — rename the import aliases.
- `N802` (invalid function name): 1 hit — rename or suppress with justification.
- Add `N` to `[tool.ruff.lint] select`.
- Commit: `feat(ruff): enable N (naming) rule set`

#### Batch 5 — Enable Ruff Rule Set `UP` (User Story 2) — Likely Deferred

Current violations: **124** — exceeds 20-violation cap.  
Most are auto-fixable (`ruff check --fix`); however, 5 involve `UP042` (replace-str-enum) and 1 involves `UP030`/`UP032` that require semantic review.

Decision per clarification Q3: defer with documented TODO.
- Add to `pyproject.toml`:
  ```toml
  # TODO(009-quality-uplift): Enable UP rule set once 124 violations are resolved
  # "UP",
  ```
- Commit: `chore(ruff): document UP rule set as deferred (124 violations > 20 cap)`

#### Batch 6 — Enable Ruff Rule Set `PT` (User Story 2) — Deferred

Current violations: **163** — far exceeds 20-violation cap.  
Primarily `PT009` (unittest assertions in pytest, 102 hits) — requires converting all `self.assert*` calls to bare `assert` which touches legacy test files.

Decision: defer with documented TODO.
- Add to `pyproject.toml`:
  ```toml
  # TODO(009-quality-uplift): Enable PT rule set once 163 violations resolved
  # Primarily PT009 (unittest assertions) in legacy tests
  # "PT",
  ```
- Commit: `chore(ruff): document PT rule set as deferred (163 violations > 20 cap)`

#### Batch 7 — Fix Pyright PIL Import Error (Prerequisite for pyright work)

The only pyright error in the baseline is in `_arisamlreader_helpers.py:61`: `Import "PIL" could not be resolved`. Pillow is a declared runtime dependency. Fix by:
- Adding `"PIL"` stubs via `types-pillow` if available, or adding a `# type: ignore[import-untyped]  # Pillow has no bundled stubs` comment.
- Verify `pyright src/` passes with 0 errors.
- Commit: `fix(pyright): suppress unresolvable PIL import`

#### Batch 8 — Re-enable Suppressed Pyright Categories (User Story 3)

After the PIL fix, probe each suppressed category:

| Category | Baseline warnings (with "warning") | Action |
|----------|------------------------------------|--------|
| `reportAttributeAccessIssue` | 3 | Fix or suppress each, then promote to `"error"` |
| `reportArgumentType` | 0 | Promote directly to `"error"` |
| `reportOptionalMemberAccess` | 0 | Promote directly to `"error"` |
| `reportMissingTypeStubs` | (inherited from PIL issue) | Promote to `"warning"` after PIL fixed |

Steps for `reportAttributeAccessIssue`:
1. Set to `"warning"`, run `pyright`, fix or justify each warning.
2. Set to `"error"`, run `pyright`, confirm clean.
3. Commit: `fix(pyright): re-enable reportAttributeAccessIssue at error level`

Steps for `reportArgumentType` and `reportOptionalMemberAccess` (already 0 violations):
1. Set both to `"error"`.
2. Run `pyright`, confirm clean.
3. Commit: `fix(pyright): re-enable reportArgumentType and reportOptionalMemberAccess`

#### Batch 9 — Fix Mypy Errors (User Story 4)

Current mypy errors (10 in 5 files):
- **lxml stubs**: `lxml-stubs` is already in the `lint` dependency group. Ensure it is installed: `pip install lxml-stubs`. This should resolve the lxml import-untyped errors.
- **PIL stubs**: Same fix as Batch 7. Add `types-pillow` or suppress.
- **setuptools stubs**: `types-setuptools` is in the `lint` dependency group. Ensure installed.
- **`no-any-return`** in `archimateWriter.py:390` and `archiWriter.py:372`: Add explicit return-type annotations or cast the return value.

Steps:
1. Install missing stubs: `pip install lxml-stubs types-setuptools types-pillow` (or add to pyproject dependencies if not already).
2. Fix the two `no-any-return` errors with proper casts.
3. Run `mypy src/`, confirm 0 errors.
4. Commit: `fix(mypy): resolve all baseline type errors`

Then evaluate the two disabled flags:
- **`disallow_untyped_defs = false`**: Run `mypy src/ --disallow-untyped-defs` and count errors. If > 20, defer; if ≤ 20, fix and enable.
- **`disallow_untyped_calls = false`**: Same probe. 

#### Batch 10 — Remove Remaining Obsolete pyproject.toml Exclusions (User Story 5)

After the above batches, audit:
- `"E501"` — line-too-long: intentionally kept (formatter handles it). Retain with comment.
- `"C901"` — removed in Batch 2 (or retained with updated comment if deferred).
- `"N999"` — removed in Batch 4 (replaced by targeted suppressions).
- `"PLC0415"` — removed in Batch 2 (replaced by targeted suppressions).
- pyright `reportAttributeAccessIssue/reportArgumentType/reportOptionalMemberAccess`: removed in Batch 8.

Final `pyproject.toml` audit commit: `chore: remove obsolete tool exclusions from pyproject.toml`

### Interface Contracts

This feature makes no changes to the public API of pyArchimate. No contracts document is needed.

### Agent Context Update

Update CLAUDE.md to reference this plan.
