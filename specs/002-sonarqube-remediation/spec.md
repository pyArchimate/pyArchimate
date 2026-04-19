# Feature Specification: SonarQube Critical Issue Remediation

**Feature Branch**: `002-sonarqube-remediation`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: User description: "pyArchimate is analysed continuously by SonarCloud (project key `pyArchimate_pyArchimate`). Remediate the SonarQube errors found at https://sonarcloud.io/api/issues/search?componentKeys=pyArchimate_pyArchimate&ps=50&p=1"

## Clarifications

### Session 2026-04-16

- Q: Should `_legacy.py` be deleted (after confirming no live callers) or refactored in place? → A: Delete it after verifying no live callers exist.
- Q: Where should helper functions extracted from complex functions be placed? → A: Private functions (prefixed `_`) in the same file as the original.
- Q: When is SonarCloud verification triggered to confirm fixes? → A: Once at the end, after all fixes are complete.
- Q: How should fixes be batched into commits? → A: One commit per rule category (S5727 → S1192 → S5754 → S2208 → S1186 → S3776).
- Q: What is the policy if refactoring introduces new SonarCloud violations? → A: Block — no commit may introduce any new violation.

### Session 2026-04-19

- Q: How will `tests/legacy_*` files be excluded from SonarCloud's issue count? → A: Add exclusion patterns to `sonar-project.properties` (e.g., `sonar.exclusions=tests/legacy_*/**`).
- Q: For extreme-complexity files (original score > 100), must helpers remain in the same file per FR-009? → A: Exception allowed — a `_<module>_helpers.py` private sibling module is acceptable for `arisAMLreader.py` and `archiReader.py`.
- Q: How is the final SonarCloud verification scan triggered to confirm SC-001? → A: Automated — the existing CI/CD pipeline triggers the scan on push to the branch.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fix Identity Check Comparisons in Tests (Priority: P1)

A developer running the test suite sees that test assertions use `is`/`is not` for value equality checks. Python's `is` operator tests object identity, not equality, so these checks pass by coincidence (for small integers and interned strings) rather than correctness. Replacing them with `==`/`!=` produces logically correct assertions that will not break when Python's memory optimisations change.

**Why this priority**: These are in test files and represent logical errors. Incorrect assertions give false confidence in the test suite and may mask real bugs. They are also the simplest to fix with no risk of behaviour change.

**Independent Test**: Run the full test suite before and after the change; all tests must pass and SonarCloud must report zero S5727 violations.

**Acceptance Scenarios**:

1. **Given** a test file uses `assert result is True`, **When** the assertion is changed to `assert result == True` (or `assert result`), **Then** the assertion still passes for correct behaviour and the SonarCloud S5727 rule no longer flags that line.
2. **Given** SonarCloud flags an `is not None` check on an lxml `find()` result as a false positive (because lxml type stubs declare the return type as non-optional), **When** a `# NOSONAR` comment is added to that line, **Then** the violation is suppressed without altering runtime semantics — `find()` does return `None` at runtime when the element is absent.
3. **Given** all identity-check violations are resolved, **When** SonarCloud analyses the project, **Then** zero S5727 CRITICAL issues are reported.

---

### User Story 2 - Fix Duplicate String Literals (Priority: P2)

A developer reading reader and writer modules encounters the same string literal repeated four or more times inline. Extracting these into named module-level constants makes the intent clear, reduces copy-paste errors on future edits, and satisfies the S1192 rule.

**Why this priority**: Low-risk change that improves readability and eliminates magic strings. Does not alter runtime behaviour.

**Independent Test**: Each affected module can be updated and tested in isolation; existing unit and integration tests must pass without modification.

**Acceptance Scenarios**:

1. **Given** `'ns:item'` appears 4 times in `archimateWriter.py`, **When** it is replaced with a named constant `_NS_ITEM`, **Then** the module's behaviour is identical and SonarCloud no longer reports S1192 for that file.

*Note*: `arisAMLreader.py` S1192 scenarios (`'Pos.X'`, `'Pos.Y'`, `'AttrDef.Type'`) are no longer present as CRITICAL violations in SonarCloud as of 2026-04-19; they are assumed already resolved and are out of scope for this remediation.

---

### User Story 3 - Fix Bare Except Clauses (Priority: P2)

A developer maintaining error-handling code finds bare `except:` clauses that catch every possible exception, including `SystemExit` and `KeyboardInterrupt`. Specifying an exception class (at minimum `Exception`) prevents inadvertent suppression of signals and makes error handling intent explicit.

**Why this priority**: Bare excepts are a logic hazard that can mask crashes or prevent clean shutdown. The fix is targeted and low-risk.

**Independent Test**: Affected files can be updated and their test suites run independently; the change must not alter observable error-handling behaviour for the tested cases.

**Acceptance Scenarios**:

1. **Given** `src/pyArchimate/_legacy.py` is confirmed dead code and deleted, **When** the deletion is committed, **Then** the S5754 violation in that file is automatically resolved.
2. **Given** `tests/legacy_integration/test_pyArchimate_legacy.py` is part of the legacy test suite, **When** the remediation is performed, **Then** this file is NOT modified, and its violations are ignored in SonarCloud.

---

### User Story 4 - Fix Wildcard Imports (Priority: Out of Scope)

**Note**: This story is out of scope as it only affects legacy example and integration test files (`tests/legacy_*`), which are excluded from remediation to ensure backward compatibility.

**Acceptance Scenarios**:

1. **Given** legacy files use `import *`, **When** the remediation is complete, **Then** these files remain unchanged and their S2208 violations are ignored in SonarCloud.

---

### User Story 5 - Add Comment to Empty Placeholder Function (Priority: P3)

A developer browsing BDD step definitions finds an empty `placeholder_steps.py` function with no explanation. Adding a comment stating the function is intentionally a stub satisfies the S1186 rule and communicates intent to future contributors.

**Why this priority**: Trivial single-line change with no behavioural impact.

**Independent Test**: The BDD test suite runs and the S1186 violation no longer appears in SonarCloud.

**Acceptance Scenarios**:

1. **Given** `tests/features/steps/placeholder_steps.py` line 6 contains an empty function body, **When** a `# TODO: implement step` (or equivalent explanatory comment) is added inside the function, **Then** the S1186 violation is resolved and the BDD suite continues to run.

---

### User Story 6 - Reduce Cognitive Complexity of Core Functions (Priority: P1)

A developer reading core modules (`archiReader.py`, `archimateReader.py`, `arisAMLreader.py`, `archiWriter.py`, `archimateWriter.py`, `model.py`, `view.py`, `relationship.py`, `element.py`, `csvWriter.py`, `check_layer_boundaries.py`) encounters monolithic functions with complexity scores ranging from 16 to 259, well above the allowed threshold of 15. Breaking these functions into focused, well-named helpers makes the code understandable, testable in isolation, and maintainable.

**Why this priority**: High-complexity functions are the largest source of CRITICAL violations (10 open issues) and represent the highest maintenance risk in the codebase. Reader and writer functions with complexity above 100 are especially urgent.

**Independent Test**: Each refactored module has its own unit/integration tests. After refactoring, all existing tests must pass; the public API of each module must remain unchanged.

**Acceptance Scenarios**:

1. **Given** `archiReader.py:21` has a function with complexity 254, **When** it is decomposed into focused helper functions each with complexity ≤ 15, **Then** all existing tests for that reader pass, the public interface is unchanged, and SonarCloud reports no S3776 violation for that file.
2. **Given** `archimateWriter.py:35` has a function with complexity 180, **When** it is refactored into smaller functions, **Then** writer tests pass, output format is identical, and the S3776 violation is resolved.
3. *(Already resolved — not present in current SonarCloud CRITICAL list as of 2026-04-19)*: `model.py:651` complexity 95 was previously flagged; assumed resolved in prior work.
4. **Given** all 10 open S3776 violations are addressed, **When** SonarCloud analyses the project, **Then** zero S3776 CRITICAL issues remain.
5. **Given** `_legacy.py` is confirmed to have no live callers, **When** the file is deleted, **Then** all S3776 violations in that file are automatically resolved with no test regressions.

---

### Edge Cases

- `_legacy.py` MUST be deleted after confirming no live callers exist (grep all imports and usages across the codebase); this eliminates 13 violations in one step. Do not refactor in place.
- Some `is` comparisons in test files may correctly be testing object identity (e.g., checking a singleton or a specific cached instance); review each case individually before changing to `==`.
- Wildcard imports may pull in names that are not explicitly referenced in the file but are needed at runtime; audit the actual usage before restricting imports.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All identity-check (S5727) violations in non-legacy code MUST be resolved by replacing value-equality `is`/`is not` comparisons with `==`/`!=` where appropriate.
- **FR-002**: The 1 open duplicate-string-literal (S1192) violation MUST be resolved by extracting the repeated literal `'ns:item'` in `archimateWriter.py` into a named module-level constant `_NS_ITEM`.
- **FR-003**: The bare-except (S5754) violation in `_legacy.py` MUST be resolved (via file deletion). Violations in `tests/legacy_*` are excluded.
- **FR-004**: Wildcard-import (S2208) violations are OUT OF SCOPE as they only occur in legacy files.
- **FR-012**: `tests/legacy_*` files MUST be excluded from SonarCloud analysis via `sonar.exclusions=tests/legacy_*/**` in `sonar-project.properties`; this ensures their violations do not count toward SC-001.
- **FR-005**: The empty-function (S1186) violation MUST be resolved by adding an explanatory comment or completing the implementation.
- **FR-006**: All 10 open cognitive-complexity (S3776) violations MUST be resolved by decomposing each over-threshold function into smaller helpers, with each helper having a complexity score ≤ 15.
- **FR-007**: All existing unit, integration, and BDD tests MUST continue to pass after every remediation change.
- **FR-011**: No commit during remediation may introduce any new SonarCloud violation of any severity. Each commit must leave the codebase with fewer or equal violations than before.
- **FR-008**: The public API of every affected production module MUST remain unchanged (no breaking changes to function signatures, class interfaces, or module exports).
- **FR-009**: Refactored helpers MUST be private functions (prefixed `_`) defined in the same file as the original function. **Exception**: for modules whose original cognitive complexity exceeds 100 (`arisAMLreader.py`, `archiReader.py`), a private sibling module named `_<module>_helpers.py` in the same package directory is acceptable.
- **FR-010**: `_legacy.py` MUST be deleted after confirming zero live callers (no active imports or usages anywhere in the codebase). Refactoring in place is not acceptable.

### Key Entities

- **SonarCloud Rule**: A code-quality rule identified by a key (e.g., `python:S3776`) with a defined severity and remediation action.
- **Cognitive Complexity Score**: A numeric measure of how hard a function is to understand; must not exceed 15 after remediation.
- **Module-level Constant**: A named variable defined at module scope to replace repeated string literals; naming must follow project conventions (UPPER_SNAKE_CASE).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The CI/CD pipeline SonarCloud scan triggered by the final push to `002-sonarqube-remediation` reports zero CRITICAL-severity issues for the `pyArchimate_pyArchimate` component.
- **SC-002**: The full test suite (unit, integration, BDD) passes with no regressions introduced by the remediation.
- **SC-003**: No function in the production codebase has a cognitive complexity score greater than 15.
- **SC-004**: Total estimated remediation debt falls from 1,731 minutes to 0 minutes as reported by SonarCloud.
- **SC-005**: All public module APIs remain backward-compatible (confirmed by existing tests passing without modification).
- **SC-006**: `tests/legacy_*` directories are **not** modified.

## Assumptions

- The SonarCloud token and project key (`pyArchimate_pyArchimate`) remain valid throughout the remediation effort.
- The CI/CD pipeline is already configured to trigger a SonarCloud scan on every push; no pipeline changes are required to satisfy SC-001.
- `_legacy.py` will be deleted (not refactored) once confirmed to have no live callers; this is the agreed disposition.
- The allowed cognitive complexity threshold is 15, as specified in the SonarCloud rule configuration for this project.
- Fixes are committed one rule category at a time in this order: S5727 (identity checks) → S1192 (string constants) → S5754 (bare excepts) → S2208 (wildcard imports) → S1186 (empty function) → S3776 (cognitive complexity). Each category produces exactly one commit.
- `tests/legacy_*` directories are **not** in scope for this remediation even though they contribute to the CRITICAL issue count; they are excluded via `sonar.exclusions=tests/legacy_*/**` in `sonar-project.properties`.
- The project uses Python 3; idiomatic Python 3 patterns (e.g., `isinstance` checks, f-strings) may be used in refactored code where appropriate.
