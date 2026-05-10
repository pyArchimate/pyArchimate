# Research: 009 Quality Uplift — Deferred TODO Resolution

**Date**: 2026-05-07 (updated from 2026-05-03 baseline)
**Branch**: `009-quality-uplift`

## Tool Audit Results (current state — 2026-05-07)

### Ruff UP Rule Set

**Decision**: Enable with one global ignore entry (UP042).

**Rationale**: 121 of 126 violations are auto-fixable. UP042 (`replace-str-enum`) cannot be applied because `StrEnum` requires Python 3.11+ but `pyproject.toml` declares `requires-python = ">=3.10,<4.0"`. Adding UP042 to the global ignore preserves 3.10 compatibility.

**Violation breakdown**:
| Rule | Count | Auto-fix | Notes |
|------|-------|----------|-------|
| UP045 | 95 | Yes | `Optional[X]` → `X \| None`; view.py(46), element.py(28), model.py(22), others |
| UP037 | 14 | Yes | Remove quotes from annotations |
| UP024 | 5 | Yes | `os.error` → `OSError` |
| UP042 | 4 | No | enums.py only — StrEnum incompatible with Python 3.10 support |
| UP015 | 3 | Yes | Redundant open modes |
| UP035 | 3 | Yes | Deprecated imports |
| UP030 | 1 | No | Format literal — manual fix |
| UP032 | 1 | Yes | f-string |

**Alternatives considered**:
- Raise `requires-python` to 3.11+: Rejected — too broad a breaking change for this sprint.
- Per-file `# noqa: UP042` on enums.py: Possible; global ignore preferred since StrEnum is never available on 3.10 regardless of file.

---

### Ruff PT Rule Set

**Decision**: Enable with `per-file-ignores` for legacy integration tests (PT009 only).

**Rationale**: 102 of 163 violations are PT009 (unittest-style assertions) concentrated entirely in `tests/legacy_integration/test_pyArchimate_legacy.py`. This file is preserved as-is per project policy (FR-009). Adding PT009 to per-file-ignores is semantically correct — legacy tests intentionally use unittest assertion style.

Remaining 61 violations after legacy ignore are in active unit tests and source files:
| Rule | Count | Strategy |
|------|-------|----------|
| PT011 | 35 | Add `match=` param to `pytest.raises()` calls; noqa with justification if message not deterministic |
| PT018 | 16 | Split compound assertions (`assert a and b` → two assertions) |
| PT001 | 9 | Auto-fixable (remove fixture `()`) |
| PT006 | 1 | Manual parametrize name fix |

**Alternatives considered**:
- Defer PT entirely: Rejected — spec requires all 4 TODO markers removed.
- Global PT011 ignore: Rejected — violations are real quality issues; `match=` adds test precision.

---

### Mypy `disallow_untyped_defs`

**Decision**: Add type annotations to all 162 unannotated functions in src/.

**Rationale**: All violations are in pyArchimate library code (not tests). Annotations improve IDE experience, enable downstream pyright checks, and are the correct long-term fix.

**File-level violation counts**:
| File | Count |
|------|-------|
| src/pyArchimate/view.py | 54 |
| src/pyArchimate/model.py | 34 |
| src/pyArchimate/relationship.py | 25 |
| src/pyArchimate/element.py | 14 |
| src/pyArchimate/readers/archimateReader.py | 12 |
| src/pyArchimate/constants.py | 7 |
| src/pyArchimate/writers/__init__.py | 4 |
| src/pyArchimate/helpers/properties.py | 4 |
| src/pyArchimate/logger.py | 3 |
| src/pyArchimate/readers/archiReader.py | 3 |
| others (~5 files) | ~2 each |

**Alternatives considered**:
- Per-module `[[tool.mypy.overrides]]` to disable per file: Rejected — leaves spirit of flag unmet.
- Enable in CI only: Rejected — spec requires pyproject.toml flag enabled.

---

### Mypy `disallow_untyped_calls`

**Decision**: Resolve as a consequence of `disallow_untyped_defs` fix; confirm count after Phase C.

**Rationale**: Sampling the 89 violations shows all are calls to our own unannotated functions (`_initialize_archimate_metadata`, `register_writer`, `_is_valid_uuid`, `set_id`, `check_valid_relationship`, `add_profile`, etc.). Once Phase C adds annotations to these functions, `no-untyped-call` errors disappear. No external library stubs are the source.

**Risk**: If residual violations remain after Phase C (calls to oyaml/lxml functions lacking stubs), suppress with `# type: ignore[no-untyped-call]  # third-party stub missing`.

---

## Phase Dependencies

```
Phase A (UP)   ─────────────────────────────┐
Phase B (PT)   ─────────────────────────────┤─── Phase E (verify all)
Phase C (untyped_defs) ─── Phase D (untyped_calls)
```

Phases A, B, C are independent. Phase D depends on Phase C.
