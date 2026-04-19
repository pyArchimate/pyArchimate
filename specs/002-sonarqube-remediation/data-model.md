# Data Model: SonarQube Critical Issue Remediation

**Branch**: `002-sonarqube-remediation` | **Date**: 2026-04-19

This is a code-quality remediation feature, not a data feature. This document maps the decomposition model — which functions are extracted into which helpers — and the configuration change model.

---

## 1. SonarCloud Configuration Change

### `sonar-project.properties` — Delta

| Key | Current Value | New Value |
|-----|--------------|-----------|
| `sonar.exclusions` | `src/pyArchimate/_legacy.py` | `src/pyArchimate/_legacy.py,tests/legacy_*/**` |
| `sonar.test.exclusions` | `tests/legacy_*/**__init__.py` *(malformed)* | `tests/legacy_*/**` |

---

## 2. Rule S5727 — Identity Check Fixes

File: `tests/unit/writers/test_archimateWriter.py`

| Line | Current | Fix |
|------|---------|-----|
| 22 | `assert views is not None` | Verify against SonarCloud; add `# NOSONAR` or replace with truthy assertion if flagged |
| 24 | `assert diagrams is not None` | Same as above |
| 26 | `assert view_el is not None` | Same as above |
| 28 | `assert view_el.find(...) is not None` | Same as above |

---

## 3. Rule S1192 — String Constant Extraction

File: `src/pyArchimate/writers/archimateWriter.py`

| Literal | Occurrences | Constant Name |
|---------|-------------|---------------|
| `'ns:item'` | 4 | `_NS_ITEM` |

---

## 4. Rule S1186 — Empty Function Fix

File: `tests/features/steps/placeholder_steps.py`

| Line | Fix |
|------|-----|
| 6 | Add `# TODO: implement acceptance test step` inside function body |

---

## 5. Rule S5754 — Bare Except / File Deletion

| Action | File |
|--------|------|
| Delete after confirming zero live callers | `src/pyArchimate/_legacy.py` |

---

## 6. Rule S3776 — Cognitive Complexity Decomposition Map

### 6a. `src/pyArchimate/element.py`

| Original Function (line) | Original Complexity | Extracted Helpers | Target File |
|--------------------------|--------------------|--------------------|-------------|
| TBD (line 267) | 16 | `_resolve_<concern>` | Same file |

### 6b. `src/pyArchimate/view.py`

| Original Function (line) | Original Complexity | Extracted Helpers | Target File |
|--------------------------|--------------------|--------------------|-------------|
| TBD (line 153) | 17 | `_compute_<x>` | Same file |
| TBD (line 519) | 22 | `_compute_<x>`, `_layout_<x>` | Same file |
| TBD (line 597) | 44 | Multiple `_render_<x>` helpers | Same file |
| TBD (line 699) | 16 | `_resolve_<x>` | Same file |
| TBD (line 1006) | 23 | `_process_<x>` helpers | Same file |

### 6c. `src/pyArchimate/writers/archiWriter.py`

| Original Function (line) | Original Complexity | Extracted Helpers | Target File |
|--------------------------|--------------------|--------------------|-------------|
| TBD (line 23) | 162 | `_write_<section>` per XML section | Same file |

### 6d. `src/pyArchimate/writers/archimateWriter.py`

| Original Function (line) | Original Complexity | Extracted Helpers | Target File |
|--------------------------|--------------------|--------------------|-------------|
| TBD (line 35) | 180 | `_write_<section>` per XML section | Same file |

### 6e. `src/pyArchimate/readers/archiReader.py` *(FR-009 exception)*

| Original Function (line) | Original Complexity | Extracted Helpers | Target File |
|--------------------------|--------------------|--------------------|-------------|
| TBD (line 21) | 254 | `_parse_<element_type>` per ArchiMate concept | `_archireader_helpers.py` (new sibling) |

### 6f. `src/pyArchimate/readers/arisAMLreader.py` *(FR-009 exception)*

| Original Function (line) | Original Complexity | Extracted Helpers | Target File |
|--------------------------|--------------------|--------------------|-------------|
| TBD (line 85) | 259 | `_parse_<aris_type>` per AML element type | `_arisamlreader_helpers.py` (new sibling) |

---

## 7. New Test Artifact

| File | Purpose |
|------|---------|
| `tests/integration/test_writer_fidelity.py` | Round-trip read→write→compare for each writer using fixture files |

---

## 8. Constraints

- All extracted helpers: private (prefixed `_`), `snake_case`, type-annotated.
- New sibling helper modules (`_archireader_helpers.py`, `_arisamlreader_helpers.py`): not exported from `src/pyArchimate/readers/__init__.py`.
- All helper names resolved to real function names during implementation (TBD above updated in tasks.md).
- No changes to `tests/legacy_*/**`.
