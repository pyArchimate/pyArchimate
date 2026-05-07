# Research: Incremental Code Quality Uplift

**Feature**: 009-quality-uplift | **Date**: 2026-05-03

## Tool Baselines (measured 2026-05-03)

### Ruff

Current config: `select = ["E", "F", "W", "B", "C", "I", "S110"]`  
Current ignore: `["E501", "C901", "N999", "PLC0415"]`

**Baseline**: 0 violations with current config.

| Rule Set | Violations | Fixable (auto) | Cap (20) | Decision |
|----------|-----------|----------------|----------|----------|
| `A` (builtins) | 6 | 0 | Under | **Enable** |
| `N` (naming) | 18 | 0 | Under | **Enable** (targeted suppressions for N999) |
| `UP` (pyupgrade) | 124 | 119 | Over | **Defer** (TODO in pyproject.toml) |
| `PT` (pytest style) | 163 | 9 | Over | **Defer** (TODO in pyproject.toml) |
| `C901` (complexity) | 6 | 0 | Under | **Fix & remove ignore** |

**UP details**: 95× `UP045` (non-pep604-annotation-optional), 14× `UP037` (quoted-annotation), 5× `UP024`, 4× `UP042`, 2× `UP015`, 2× `UP035`, 1× `UP030`, 1× `UP032`

**PT details**: 102× `PT009` (unittest assertions in tests), 35× `PT011`, 16× `PT018`, 9× `PT001`, 1× `PT006`

### Pyright

Current config: `typeCheckingMode = "basic"` with `reportAttributeAccessIssue`, `reportArgumentType`, `reportOptionalMemberAccess` = `"none"`

**Baseline**: 1 error — `PIL` import unresolved in `_arisamlreader_helpers.py:61`

| Category re-enabled | Additional issues |
|--------------------|-------------------|
| `reportAttributeAccessIssue = "warning"` | +3 warnings |
| `reportArgumentType = "warning"` | +0 |
| `reportOptionalMemberAccess = "warning"` | +0 |

**Decision**:
- Fix PIL import (Pillow is a declared dependency; add stubs or targeted `# type: ignore`)
- `reportAttributeAccessIssue`: set to `"warning"`, fix 3 warnings, promote to `"error"`
- `reportArgumentType`: promote directly to `"error"` (0 violations)
- `reportOptionalMemberAccess`: promote directly to `"error"` (0 violations)

### Mypy

Config: `strict = true` but with `disallow_untyped_calls = false`, `disallow_untyped_defs = false`

**Baseline**: 10 errors in 5 files

| Error | File | Root Cause | Fix |
|-------|------|-----------|-----|
| `import-untyped` (setuptools) | `src/setup.py` | stubs not installed | Install `types-setuptools` (already in lint deps) |
| `import-untyped` (lxml.etree, lxml) | `model.py` | stubs not installed | Install `lxml-stubs` (already in lint deps) |
| `import-untyped` (lxml) | `archimateWriter.py`, `archiWriter.py` | same | same |
| `no-any-return` | `archimateWriter.py:390`, `archiWriter.py:372` | function returns `Any` | Add cast or annotation |
| `import-not-found` (PIL) | `_arisamlreader_helpers.py:61` | Pillow has no bundled stubs | `# type: ignore[import-untyped]` or install `types-Pillow` |

**Disabled flags assessment**: Defer `disallow_untyped_defs` and `disallow_untyped_calls` — codebase has large number of unannotated functions; enabling would surface > 20 violations. Document as stretch goal with TODO.

### SonarCloud

API endpoint: `https://sonarcloud.io/api/issues/search?projectKeys=pyArchimate_pyArchimate&severities=CRITICAL,MAJOR,MINOR&statuses=OPEN,CONFIRMED`  
Token: stored in `.env` as `SONAR_TOKEN`

Issues are queried live during implementation. Triage decisions:
- Fix code smells and bugs inline.
- False positives (lxml dynamic type system, `find()` returning `None`): suppress with `# NOSONAR <justification>`.
- Security hotspots: verify context, fix or accept with documented rationale.

## Final State (2026-05-07)

### Ruff

**Active rule sets**: `E`, `F`, `W`, `B`, `C`, `I`, `S110`, `A`, `N`  
**Active ignore**: `["E501"]` — `C901`, `PLC0415`, `N999` removed  
**Result**: 0 violations across `src/` and `tests/`

| Deferred | Violations | TODO in pyproject.toml |
|----------|-----------|------------------------|
| `UP` | 124 | ✓ |
| `PT` | 163 | ✓ |

### Pyright

**Actual outcome**: All three categories set to `"warning"` (not `"error"`)

**Reason**: Pre-commit hook runs `pyright src/ tests/` — test files have 419 violations that block promotion to `"error"`. Promotion to `"error"` requires a separate cleanup pass over the test suite.

| Category | Level | Reason for not promoting to "error" |
|----------|-------|--------------------------------------|
| `reportAttributeAccessIssue` | `warning` | 419 violations in `tests/` |
| `reportArgumentType` | `warning` | same |
| `reportOptionalMemberAccess` | `warning` | same |

### Mypy

**Baseline result**: 0 errors (`mypy src/`)

**Deferred flags**:

| Flag | Violations | Decision |
|------|-----------|----------|
| `disallow_untyped_defs` | 162 | Deferred; TODO comment in pyproject.toml |
| `disallow_untyped_calls` | 89 | Deferred; TODO comment in pyproject.toml |

### SonarCloud

**Status**: Skipped — `SONAR_TOKEN` unavailable in dev environment. T007–T011 remain open for a follow-up pass when CI token is accessible.

## Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Enable `A` and `N` rule sets | Both under 20-violation cap; immediate quality improvement | Enable all 4 at once — rejected (UP/PT exceed cap) |
| Defer `UP` (124 violations) | Exceeds 20-violation cap; most auto-fixable but requires review for UP042/UP032 | Auto-fix all — rejected (unsafe fixes for some UP042 patterns) |
| Defer `PT` (163 violations) | Primarily PT009 (unittest assertions); fixing requires touching legacy test style | Partial enable — rejected (complex per-file ignore setup) |
| Pyright warning→error graduation | Avoids blocking CI mid-sprint while violations are fixed | Directly to "error" — risky if undiscovered violations exist |
| Install lint dependency stubs | `lxml-stubs`, `types-setuptools` already declared in pyproject.toml lint group | Inline `type: ignore` — worse than proper stubs |
| Defer mypy `disallow_untyped_defs` | Large number of unannotated functions; would exceed cap | Enable per-module — complex, deferred as stretch goal |
