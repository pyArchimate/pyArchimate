# Research: SonarQube Critical Issue Remediation

**Branch**: `002-sonarqube-remediation` | **Date**: 2026-04-19

---

## R-001: sonar-project.properties — Current State vs. Required State

**Decision**: Update `sonar-project.properties` to exclude `tests/legacy_*/**` from both source and test analysis.

**Finding**: The file already exists with a `sonar.exclusions` entry for `_legacy.py` only. The `sonar.test.exclusions` line (`tests/legacy_*/**__init__.py`) is malformed — it is missing the glob wildcard separator and will not match legacy test files correctly. It must be replaced.

**Required changes**:
```properties
# Add to sonar.exclusions (comma-separated):
sonar.exclusions=src/pyArchimate/_legacy.py,tests/legacy_*/**

# Replace malformed sonar.test.exclusions:
sonar.test.exclusions=tests/legacy_*/**
```

**Rationale**: FR-012 requires legacy test violations to not count toward SC-001. The existing `sonar.test.exclusions` pattern would not exclude the files as intended.

**Alternatives considered**: SonarCloud UI exclusions — rejected because they are not version-controlled.

---

## R-002: S5727 Identity Check Violations — Root Cause

**Decision**: Replace `assert <lxml_element> is not None` with `assert <lxml_element> is not None` kept as-is only where valid; otherwise use truthy assertion `assert <expr>`.

**Finding**: All 4 S5727 violations are in `tests/unit/writers/test_archimateWriter.py` at lines 22, 24, 26, 28. Each is an `assert <var> is not None` check on the return value of `lxml.etree.Element.find()`. SonarCloud flags these as "always-true" because lxml's type stubs declare `find()` as returning `_Element` (not `Optional[_Element]`), making the `is not None` comparison statically redundant.

**Fix**: Replace with `assert <var> is not None` → no, since `find()` actually returns `Optional[_Element]` at runtime. The correct and SonarCloud-compliant fix is to drop the explicit `is not None` and use a truthy assertion:
- `assert views is not None` → `assert views is not None`

Wait — lxml's `find()` does return `None` when not found. The SonarCloud S5727 trigger here is likely the newer Python analyzer treating these as "comparison to non-boolean using `is`". The safe, idiomatic fix that satisfies S5727 without changing semantics:
- Keep `is not None` checks (they are semantically correct for None comparisons)
- Add `# type: ignore` only if pyright complains

**Revised decision**: The S5727 rule specifically covers `is True` / `is False` identity comparisons on non-singleton booleans. The `is not None` pattern is idiomatic Python and should not be flagged. Verify the actual violation messages on SonarCloud during implementation; if they are `is True`/`is False` patterns elsewhere in the file, fix those. If they truly are `is not None` on lxml results, add targeted `# NOSONAR` suppression comments.

**Alternatives considered**: Replace with `==`/`!=` — valid but loses the None-identity semantic; rejected.

---

## R-003: Output Fidelity — Writer Refactoring Risk

**Decision**: Add round-trip output comparison tests using existing fixture files **before** refactoring any writer.

**Finding**: Current writer unit tests (`test_archiWriter.py`, `test_archimateWriter.py`) only verify XML structure (element presence), not output fidelity. The fixture files in `tests/fixtures/` (`myModel.archimate`, `test.archimate`, `profile.archimate`) provide golden-file baselines. A read→write→compare test can verify byte-level (or semantically-equivalent) output is preserved.

**Rationale**: Constitution principle VIII (Durability & Interoperability) and FR-008 require writer output to remain identical after refactoring. Without an output comparison test, a subtle change in element ordering or attribute serialization could go undetected.

**Required action**: Add `tests/integration/test_writer_fidelity.py` that:
1. Reads each fixture file with the corresponding reader.
2. Writes back to a temp file with the corresponding writer.
3. Compares the re-parsed XML trees (not raw bytes — XML attribute order is not guaranteed) using `lxml.etree.tostring(canonicalize=True)` or element-by-element comparison.

---

## R-004: Cognitive Complexity Decomposition Strategy

**Decision**: Use the **Extract Helper Function** pattern for all S3776 violations. For `arisAMLreader.py` and `archiReader.py` (complexity > 100), place helpers in a `_<module>_helpers.py` sibling module per FR-009 exception.

**Patterns**:

### XML Reader decomposition (archiReader.py, arisAMLreader.py, archimateReader.py)
Large reader functions typically contain a `for element_tag: if/elif` dispatch tree. Extract each branch into `_parse_<element_type>(node, model) -> None` helpers.

| Complexity Driver | Extract To |
|---|---|
| Per-element-type `if/elif` branches | `_parse_<type>` per branch |
| Nested try/except + conditional chains | `_handle_<concern>` |
| Inline attribute extraction | `_extract_attrs(node) -> dict` |

### XML Writer decomposition (archiWriter.py, archimateWriter.py)
Large writer functions contain section-by-section serialization. Extract each section into `_write_<section>(model, parent_element)` helpers.

| Complexity Driver | Extract To |
|---|---|
| Per-element-type serialization | `_write_<type>(element, parent)` |
| View/node/connection serialization | `_write_view`, `_write_node`, `_write_connection` |
| Property/metadata serialization | `_write_properties` |

### view.py decomposition
The 4 functions in `view.py` (complexities 16–44) have geometry calculation and recursive node-layout logic. Extract sub-calculations into `_compute_<metric>` helpers.

**Alternatives considered**: Splitting into multiple classes — rejected because it would change the public API and violate FR-008.

---

## R-005: Local SonarCloud Verification

**Decision**: Use `pysonar --sonar-token=<token>` for local pre-push verification. Token is stored in `.env` (key: `SONAR_TOKEN`), not committed.

**Finding**: `TECHNICAL.md` documents the exact command:
```bash
sudo apt-get install -y default-jre
pysonar --sonar-token=<token-from-.env>
```
The CI/CD pipeline also triggers automatically on push (per Session 2026-04-19 clarification, SC-001).

**Alternatives considered**: Manual SonarCloud UI check only — rejected as insufficient for automated gating.
