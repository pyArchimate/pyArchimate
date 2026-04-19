# Implementation Plan: SonarQube Critical Issue Remediation

**Branch**: `002-sonarqube-remediation` | **Date**: 2026-04-19 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/002-sonarqube-remediation/spec.md`

---

## Summary

Remediate all 16 CRITICAL SonarCloud violations (1,731 min debt) in the `pyArchimate_pyArchimate` component. The work covers four rule categories: S3776 (cognitive complexity — 10 functions), S5727 (identity checks — 4 test assertions), S1192 (string literal duplication — 1 constant), and S1186 (empty function — 1 stub). Execution is sequenced from least-risky to highest-risk changes, with output-fidelity tests added before any writer is refactored.

---

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: Poetry, lxml, ruff, pyright, mypy, pytest, behave, pysonar  
**Storage**: N/A (library — file I/O only)  
**Testing**: pytest (unit + integration), behave (BDD)  
**Target Platform**: Linux (library; CI via GitHub Actions)  
**Project Type**: Library  
**Performance Goals**: N/A — refactoring only; no throughput or latency targets  
**Constraints**: Public API unchanged (FR-008); writer output semantically identical after refactoring (R-003); 80% unit test coverage floor maintained (FR-007)  
**Scale/Scope**: 16 violations across 8 production files; ~1,731 min estimated debt

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked post-design below.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | ✅ PASS | S3776 fixes directly reduce complexity; extracted helpers follow single-responsibility |
| II. Testing Standards | ✅ PASS | All existing tests must pass; writer fidelity tests added before refactoring (R-003) |
| III. UX Consistency | ✅ N/A | No user-facing interface changes |
| IV. Performance | ✅ PASS | No performance-critical paths changed |
| V. Security | ✅ PASS | No auth/input-validation changes |
| VI. State Management | ✅ PASS | No state model changes |
| VII. System Integrity | ⚠️ RISK → MITIGATED | Writer output must be byte-equivalent after refactoring; mitigated by `test_writer_fidelity.py` (R-003) |
| VIII. Durability & Interoperability | ⚠️ RISK → MITIGATED | Reader/writer file format contracts must be preserved; mitigated by fidelity tests and fixture comparison |
| IX. Cross-Platform Consistency | ✅ N/A | Pure Python library; no UI or platform-specific paths |

**Post-design re-check**: Principles VII and VIII risks are mitigated by the fidelity test added in Phase 1. No constitution violations remain unjustified.

---

## Project Structure

### Documentation (this feature)

```text
specs/002-sonarqube-remediation/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (affected files)

```text
sonar-project.properties          ← add legacy exclusions (FR-012)

src/pyArchimate/
├── element.py                    ← S3776: 1 function (complexity 16)
├── view.py                       ← S3776: 5 functions (complexities 17–44)
├── readers/
│   ├── archiReader.py            ← S3776: 1 function (complexity 254)
│   ├── _archireader_helpers.py   ← NEW: private helpers (FR-009 exception)
│   ├── arisAMLreader.py          ← S3776: 1 function (complexity 259)
│   └── _arisamlreader_helpers.py ← NEW: private helpers (FR-009 exception)
└── writers/
    ├── archiWriter.py            ← S3776: 1 function (complexity 162)
    └── archimateWriter.py        ← S3776: 1 function (complexity 180) + S1192: 1 constant

tests/
├── unit/writers/
│   └── test_archimateWriter.py   ← S5727: 4 identity checks (lines 22, 24, 26, 28)
├── integration/
│   └── test_writer_fidelity.py   ← NEW: round-trip output comparison
└── features/steps/
    └── placeholder_steps.py      ← S1186: 1 empty function

# NOT modified:
tests/legacy_*/**                 ← excluded from SonarCloud via sonar-project.properties
```

**Structure Decision**: Single-project layout; helpers for extreme-complexity readers placed in `_<module>_helpers.py` sibling modules within the same package directory. No new packages or public modules introduced.

---

## Implementation Phases

### Phase A — Low-Risk Fixes (no logic change)

**Commit 1**: `fix(sonar): exclude legacy tests from sonarcloud analysis`
- Update `sonar-project.properties`:
  - `sonar.exclusions` → add `,tests/legacy_*/**`
  - `sonar.test.exclusions` → replace malformed value with `tests/legacy_*/**`
- Verify: push and confirm legacy test violations no longer appear in SonarCloud CRITICAL list

**Commit 2**: `fix(tests): replace identity checks with equality assertions (S5727)`
- `tests/unit/writers/test_archimateWriter.py` lines 22, 24, 26, 28
- Investigate actual SonarCloud violation message; apply one of:
  - Replace `assert x is not None` with `assert x is not None` + `# NOSONAR` (if lxml-specific false positive)
  - Replace with truthy assertion `assert x` (if semantics allow)
- Run `pytest tests/unit/writers/test_archimateWriter.py`

**Commit 3**: `fix(writers): extract duplicate string literal to constant (S1192)`
- `src/pyArchimate/writers/archimateWriter.py`: extract `'ns:item'` → `_NS_ITEM = 'ns:item'`
- Run `pytest tests/unit/writers/`

**Commit 4**: `fix(legacy): delete _legacy.py after confirming no live callers (S5754)`
- `grep -r "_legacy" src/ tests/` to confirm zero live imports
- Delete `src/pyArchimate/_legacy.py`
- Run full test suite

**Commit 5**: `fix(bdd): add comment to placeholder step function (S1186)`
- `tests/features/steps/placeholder_steps.py` line 6: add `# TODO: implement acceptance test step` inside function body
- Run `behave tests/features/`

---

### Phase B — Writer Refactoring (medium risk)

**Pre-condition**: Add fidelity tests before any writer changes.

**Commit 6**: `test(integration): add writer round-trip fidelity tests`
- Create `tests/integration/test_writer_fidelity.py`
- For each writer: read fixture → write to temp → compare canonical XML trees
- Fixtures: `tests/fixtures/myModel.archimate`, `tests/fixtures/test.archimate`
- Verify all fidelity tests pass against current (unmodified) writers

**Commit 7**: `refactor(writers): reduce archimateWriter cognitive complexity (S3776)`
- `src/pyArchimate/writers/archimateWriter.py:35` — complexity 180 → ≤ 15
- Extract `_write_elements`, `_write_relationships`, `_write_views`, `_write_nodes`, `_write_connections`, `_write_properties` private helpers
- Run `pytest tests/unit/writers/test_archimateWriter.py tests/integration/test_writer_fidelity.py`

**Commit 8**: `refactor(writers): reduce archiWriter cognitive complexity (S3776)`
- `src/pyArchimate/writers/archiWriter.py:23` — complexity 162 → ≤ 15
- Extract `_write_folder`, `_write_element`, `_write_relationship`, `_write_view`, `_write_style` private helpers
- Run `pytest tests/unit/writers/ tests/integration/test_writer_fidelity.py`

---

### Phase C — View & Element Refactoring (medium risk)

**Commit 9**: `refactor(view): reduce cognitive complexity below 15 (S3776)`
- `src/pyArchimate/view.py` — 4 functions (lines 153, 519, 597, 699, 1006)
- Extract focused `_compute_*` / `_layout_*` / `_render_*` helpers in same file
- Run `pytest tests/unit/test_view.py`

**Commit 10**: `refactor(element): reduce cognitive complexity below 15 (S3776)`
- `src/pyArchimate/element.py:267` — complexity 16 → ≤ 15
- Minimal extraction (1 point over threshold)
- Run `pytest tests/unit/test_element.py`

---

### Phase D — Reader Refactoring (highest risk, most debt)

**Commit 11**: `refactor(readers): reduce archiReader cognitive complexity (S3776)`
- `src/pyArchimate/readers/archiReader.py:21` — complexity 254 → ≤ 15
- Create `src/pyArchimate/readers/_archireader_helpers.py` with `_parse_<type>` helpers
- Run `pytest tests/unit/readers/test_archiReader.py tests/legacy_unit/readers/test_archiReader.py`

**Commit 12**: `refactor(readers): reduce arisAMLreader cognitive complexity (S3776)`
- `src/pyArchimate/readers/arisAMLreader.py:85` — complexity 259 → ≤ 15
- Create `src/pyArchimate/readers/_arisamlreader_helpers.py` with `_parse_<aris_type>` helpers
- Run `pytest tests/unit/readers/test_arisAMLreader.py tests/legacy_unit/readers/test_arisAMLreader.py`

**Commit 13**: `refactor(readers): reduce archimateReader cognitive complexity (S3776)` *(if needed)*
- Check SonarCloud after commit 12; fix any remaining S3776 on `archimateReader.py` if present

---

### Final Verification

**Commit 14 (if needed)**: Any remaining clean-up.

- Run `bash scripts/pre_push_checks.sh` — all checks must pass
- Run `poetry run pysonar --sonar-token=$SONAR_TOKEN` — local scan must show zero CRITICAL issues
- Push branch — CI/CD SonarCloud scan confirms SC-001

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| New `_archireader_helpers.py` module | `archiReader.py` complexity 254 — extracting all helpers into same file would create a 700+ line file making navigation worse, not better | FR-009 explicitly permits this exception for complexity > 100; keeping all in one file doesn't help readability |
| New `_arisamlreader_helpers.py` module | `arisAMLreader.py` complexity 259 — same reasoning as above | Same as above |
| New `test_writer_fidelity.py` | Constitution VIII requires interoperability contracts preserved; no existing golden-file test exists | Structural-only tests are insufficient to catch subtle serialization regressions |
