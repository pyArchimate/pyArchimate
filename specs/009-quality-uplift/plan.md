# Implementation Plan: Incremental Code Quality Uplift (009)

**Branch**: `009-quality-uplift` | **Date**: 2026-05-07 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/009-quality-uplift/spec.md`

## Summary

Resolve all four deferred `# TODO(009-quality-uplift)` items in `pyproject.toml`: enable the ruff `UP` and `PT` rule sets, and re-enable `disallow_untyped_defs` and `disallow_untyped_calls` in mypy. Approach: auto-fix where possible, mechanical fixes for test-style rules, add type annotations to all unannotated src functions (which resolves both mypy flags in sequence). SonarCloud remediation and ruff `N`/`A` rules already completed in prior commits.

## Technical Context

**Language/Version**: Python 3.10+ (requires-python), ruff targets py312  
**Primary Dependencies**: ruff 0.11+, mypy 2.0+, pyright, pytest, behave  
**Storage**: N/A — file I/O only  
**Testing**: pytest (unit/integration), behave (BDD)  
**Target Platform**: Linux/macOS developer workstations + CI  
**Project Type**: Library  
**Performance Goals**: N/A — quality tooling only  
**Constraints**: `requires-python = ">=3.10,<4.0"` limits use of Python 3.11+ builtins (StrEnum); ruff target-version = py312 is for lint purposes, not minimum runtime  
**Scale/Scope**: 28 source files; ~162 untyped functions; 126 UP violations; 163 PT violations

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | PASS | This feature directly improves code quality |
| II. Testing Standards | PASS | All existing tests must continue to pass; PT fixes improve test quality |
| III. User Experience Consistency | N/A | Developer tooling feature |
| IV. Performance Requirements | N/A | No runtime changes |
| V. Security Practices | PASS | No sensitive data changes |
| VI. State Management | N/A | No state transitions |
| VII. System Integrity & Accuracy | PASS | Type annotations improve accuracy guarantees |
| VIII. Durability & Interoperability | PASS | No API changes; type annotations aid integration |
| IX. Cross-Platform Consistency | PASS | Tool config changes are platform-neutral |

**Gate result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/009-quality-uplift/
├── plan.md              # This file
├── research.md          # Phase 0 output (tool audit results)
├── tasks.md             # Phase 2 output (/speckit-tasks)
└── spec.md              # Feature specification
```

### Source Code (affected files)

```text
pyproject.toml                          # ruff/mypy config changes

src/pyArchimate/
├── enums.py                            # UP042 noqa (StrEnum), UP045 auto-fix
├── view.py                             # 54 untyped-defs, 46 UP045 auto-fix
├── model.py                            # 34 untyped-defs, 22 UP045 auto-fix
├── relationship.py                     # 25 untyped-defs, UP045 auto-fix
├── element.py                          # 14 untyped-defs, 28 UP045 auto-fix
├── constants.py                        # 7 untyped-defs, UP045/UP035 auto-fix
├── helpers/properties.py               # 4 untyped-defs
├── writers/__init__.py                 # 4 untyped-defs
├── logger.py                           # 3 untyped-defs
├── readers/archimateReader.py          # 12 untyped-defs, UP045 auto-fix
├── readers/archiReader.py              # 3 untyped-defs
├── readers/_arisamlreader_helpers.py   # 9 UP045 auto-fix
└── ...                                 # remaining readers/writers

tests/
├── legacy_integration/
│   └── test_pyArchimate_legacy.py      # per-file-ignore PT009 (102 violations)
├── unit/
│   ├── test_model.py                   # PT011/PT018 fixes
│   ├── test_view.py                    # PT011/PT018 fixes
│   ├── test_element.py                 # PT011/PT018 fixes
│   ├── test_relationship.py            # PT011/PT018 fixes
│   └── ...                             # remaining PT fixes
└── ...
```

**Structure Decision**: Existing project structure; no new directories or files created.

## Complexity Tracking

No constitution violations requiring justification.

## Implementation Phases

### Phase A — Ruff UP Rule Set (auto-fix + 2 manual decisions)

**Violations**: 126 total (121 auto-fixable, 5 manual)

| Rule | Count | Fix Strategy |
|------|-------|-------------|
| UP045 | 95 | `ruff --fix` — `Optional[X]` → `X \| None` |
| UP037 | 14 | `ruff --fix` — remove quotes from annotations |
| UP024 | 5 | `ruff --fix` — `os.error` → `OSError` |
| UP042 | 4 | **Ignore** — `StrEnum` requires Python 3.11+; project supports 3.10+. Add `UP042` to global ruff `ignore` list. |
| UP015 | 3 | `ruff --fix` — remove redundant open modes |
| UP035 | 3 | `ruff --fix` — update deprecated imports |
| UP030 | 1 | **Manual** — fix format literal |
| UP032 | 1 | `ruff --fix` |

**Steps**:
1. Add `"UP042"` to `tool.ruff.lint.ignore` with comment `# StrEnum requires Python 3.11+; project supports 3.10+`
2. Run `ruff check --fix --select UP` (fixes 121)
3. Manually fix UP030 (1 format literal)
4. Uncomment `"UP"` in `tool.ruff.lint.select`
5. Verify `ruff check` passes with UP enabled

### Phase B — Ruff PT Rule Set (per-file-ignore + mechanical fixes)

**Violations**: 163 total → 61 after legacy exclusion → 10 after auto-fix + manual

| Rule | Count | Location | Fix Strategy |
|------|-------|----------|-------------|
| PT009 | 102 | `tests/legacy_integration/` only | per-file-ignore (unittest-style tests preserved by policy) |
| PT011 | 35 | unit tests | Add `match=` param to `pytest.raises()` or `# noqa: PT011` with justification per case |
| PT018 | 16 | unit tests + src | Split `assert a and b` → `assert a\nassert b` |
| PT001 | 9 | unit tests | `ruff --fix` — remove fixture parentheses |
| PT006 | 1 | unit tests | Manual — fix parametrize name format |

**Steps**:
1. Add `per-file-ignores` entry: `"tests/legacy_integration/*.py" = ["PT009"]`
2. Run `ruff check --fix --select PT` (fixes PT001 x9)
3. Fix PT018 (16): mechanically split compound assertions
4. Fix PT011 (35): add `match=` where regex is clear; use `# noqa: PT011  # broad raise is intentional` where not
5. Fix PT006 (1): manual parametrize fix
6. Uncomment `"PT"` in `tool.ruff.lint.select`
7. Verify `ruff check` passes with PT enabled

### Phase C — Mypy `disallow_untyped_defs` (add type annotations)

**Violations**: 162 across 13 source files (view.py 54, model.py 34, relationship.py 25, element.py 14, archimateReader.py 12, constants.py 7, writers/__init__.py 4, helpers/properties.py 4, logger.py 3, archiReader.py 3, others ~2)

**Strategy**: Add return-type and parameter-type annotations to all 162 unannotated functions. Work file-by-file, largest first. Use `Any` sparingly with justification; prefer concrete types or `object`.

**Steps**:
1. Enable `disallow_untyped_defs = true` in pyproject.toml (temporarily comment out `false`)
2. File-by-file: run `mypy src/pyArchimate/<file>.py` after each batch of annotations
3. Order: view.py → model.py → relationship.py → element.py → archimateReader.py → constants.py → writers/__init__.py → helpers/properties.py → logger.py → remaining files
4. Remove `disallow_untyped_defs = false` line and `# TODO(009-quality-uplift)` comment
5. Verify `mypy src/` passes

### Phase D — Mypy `disallow_untyped_calls` (resolves after Phase C)

**Violations**: 89 — all calling our own unannotated functions (confirmed by sampling). Once Phase C adds annotations to those functions, these violations disappear.

**Steps**:
1. After Phase C, re-run `mypy src/ --disallow-untyped-calls` to confirm remaining count
2. If 0 (expected): remove `disallow_untyped_calls = false` and TODO comment
3. If residual violations remain: add `# type: ignore[no-untyped-call]  # <justification>` per call site
4. Verify `mypy src/` passes with both flags enabled

### Phase E — Verification

1. `ruff check` — must pass (UP + PT + N + A + all existing rules)
2. `pyright` — must pass (no regressions from type annotation changes)
3. `mypy src/` — must pass with `disallow_untyped_defs = true` and `disallow_untyped_calls = true`
4. `pytest tests/` — full test suite must pass
5. Confirm zero `# TODO(009-quality-uplift)` markers remain in `pyproject.toml`
