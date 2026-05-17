# Data Model: Feature 014 — Fix Code Complexity & Pre-commit Enforcement

This feature introduces no new domain entities and modifies no existing data formats.
The only structural artifact added is the pre-commit configuration.

---

## Pre-commit Configuration Entity

**File**: `.pre-commit-config.yaml` (repository root)

| Field | Type | Value | Notes |
|-------|------|-------|-------|
| `repos[].repo` | string | `https://github.com/astral-sh/ruff-pre-commit` | Official ruff hooks repo |
| `repos[].rev` | string | pinned semver tag | Must be compatible with `ruff ≥ 0.14.10` |
| `repos[].hooks[0].id` | string | `ruff` | Runs `ruff check` — lint + complexity gate |
| `repos[].hooks[1].id` | string | `ruff-format` | Runs `ruff format --check` — format gate |
| `repos[].hooks[1].args` | list | `["--check"]` | Makes format check read-only (no auto-rewrite) |

All ruff rule configuration is sourced from `pyproject.toml` `[tool.ruff]` sections.
No configuration is duplicated in `.pre-commit-config.yaml`.

---

## Coverage Baseline Snapshot

Recorded at feature start (2026-05-17) from `build/coverage.xml`.
These are the minimum acceptable values post-refactoring (SC-010).

| File | Baseline Coverage | P0 Gate |
|------|-----------------|---------|
| `view/layout/__init__.py` | 43% | ≥ 80% (must uplift) |
| `view/layout/routing/segment_separation.py` | 71% | ≥ 80% (must uplift) |
| `view/layout/layout_engine.py` | 86% | ≥ 86% (no regression) |
| `view/layout/export/svg_export.py` | 73% | ≥ 73% (no regression) |
| `view/__init__.py` | 88% | ≥ 88% (no regression) |
| `readers/archimateReader.py` | 98% | ≥ 98% (no regression) |
| `readers/archiReader.py` | 84% | ≥ 84% (no regression) |
| `model.py` | 96% | ≥ 96% (no regression) |

---

## Helper Function Naming Convention

All extracted helpers follow this pattern (per clarification Q1 and TECHNICAL.md naming rules):

- Prefix: `_` (private, not exported)
- Case: `snake_case`
- Location: same `.py` file as the function being refactored
- Purpose naming: verb + noun describing the sub-operation (e.g., `_route_single_connection`,
  `_detect_overlap`, `_is_horizontal_segment`)
