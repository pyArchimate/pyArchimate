# Feature Specification: SonarQube Critical Issue Remediation

**Feature Branch**: `002-sonarqube-remediation`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: User description: "Remediate the SonarQube errors found at https://sonarcloud.io/api/issues/search?componentKeys=pyArchimate_pyArchimate&severities=CRITICAL&ps=50&p=1"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fix Identity Check Comparisons in Tests (Priority: P1)

A developer running the test suite sees that test assertions use `is`/`is not` for value equality checks. Python's `is` operator tests object identity, not equality, so these checks pass by coincidence (for small integers and interned strings) rather than correctness. Replacing them with `==`/`!=` produces logically correct assertions that will not break when Python's memory optimisations change.

**Why this priority**: These are in test files and represent logical errors. Incorrect assertions give false confidence in the test suite and may mask real bugs. They are also the simplest to fix with no risk of behaviour change.

**Independent Test**: Run the full test suite before and after the change; all tests must pass and SonarCloud must report zero S5727 violations.

**Acceptance Scenarios**:

1. **Given** a test file uses `assert result is True`, **When** the assertion is changed to `assert result == True` (or `assert result`), **Then** the assertion still passes for correct behaviour and the SonarCloud S5727 rule no longer flags that line.
2. **Given** a test file uses `assert value is not None`, **When** the assertion is retained as-is (identity check against `None` is idiomatic and correct), **Then** SonarCloud does not flag it as a violation.
3. **Given** all identity-check violations are resolved, **When** SonarCloud analyses the project, **Then** zero S5727 CRITICAL issues are reported.

---

### User Story 2 - Fix Duplicate String Literals (Priority: P2)

A developer reading reader and writer modules encounters the same string literal repeated four or more times inline. Extracting these into named module-level constants makes the intent clear, reduces copy-paste errors on future edits, and satisfies the S1192 rule.

**Why this priority**: Low-risk change that improves readability and eliminates magic strings. Does not alter runtime behaviour.

**Independent Test**: Each affected module can be updated and tested in isolation; existing unit and integration tests must pass without modification.

**Acceptance Scenarios**:

1. **Given** `'ns:item'` appears 4 times in `archimateWriter.py`, **When** it is replaced with a named constant, **Then** the module's behaviour is identical and SonarCloud no longer reports S1192 for that file.
2. **Given** `'Pos.X'` and `'Pos.Y'` each appear 4 times in `arisAMLreader.py`, **When** they are replaced with named constants, **Then** parsing behaviour is identical and the S1192 violations are resolved.
3. **Given** `'AttrDef.Type'` appears 4 times in `arisAMLreader.py`, **When** it is replaced with a named constant, **Then** the S1192 violation is resolved.

---

### User Story 3 - Fix Bare Except Clauses (Priority: P2)

A developer maintaining error-handling code finds bare `except:` clauses that catch every possible exception, including `SystemExit` and `KeyboardInterrupt`. Specifying an exception class (at minimum `Exception`) prevents inadvertent suppression of signals and makes error handling intent explicit.

**Why this priority**: Bare excepts are a logic hazard that can mask crashes or prevent clean shutdown. The fix is targeted and low-risk.

**Independent Test**: Affected files can be updated and their test suites run independently; the change must not alter observable error-handling behaviour for the tested cases.

**Acceptance Scenarios**:

1. **Given** `src/pyArchimate/_legacy.py` contains a bare `except:`, **When** it is changed to `except Exception:`, **Then** the S5754 violation is resolved and existing tests continue to pass.
2. **Given** `tests/legacy_integration/test_pyArchimate_legacy.py:476` contains a bare `except:`, **When** it is changed to `except Exception:`, **Then** the S5754 violation is resolved and the integration tests continue to pass.

---

### User Story 4 - Fix Wildcard Imports (Priority: P2)

A developer working in legacy example and integration test files finds `from module import *` statements. These pollute the local namespace, make it hard to trace where names come from, and violate the S2208 rule. Replacing them with explicit imports makes dependencies clear.

**Why this priority**: Low-risk; affects only legacy example and integration test files with no impact on production code.

**Independent Test**: The two affected files can be updated independently; tests in those files must still execute successfully.

**Acceptance Scenarios**:

1. **Given** `tests/legacy_examples/Archi2Aris.py` uses `import *`, **When** only the actually-used names are imported explicitly, **Then** the script runs successfully and the S2208 violation is resolved.
2. **Given** `tests/legacy_integration/test_pyArchimate_legacy.py` uses `import *`, **When** only the actually-used names are imported explicitly, **Then** all integration tests pass and the S2208 violation is resolved.

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

**Why this priority**: High-complexity functions are the largest source of CRITICAL violations (35+ issues) and represent the highest maintenance risk in the codebase. Reader and writer functions with complexity above 100 are especially urgent.

**Independent Test**: Each refactored module has its own unit/integration tests. After refactoring, all existing tests must pass; the public API of each module must remain unchanged.

**Acceptance Scenarios**:

1. **Given** `archiReader.py:21` has a function with complexity 254, **When** it is decomposed into focused helper functions each with complexity ≤ 15, **Then** all existing tests for that reader pass, the public interface is unchanged, and SonarCloud reports no S3776 violation for that file.
2. **Given** `archimateWriter.py:35` has a function with complexity 180, **When** it is refactored into smaller functions, **Then** writer tests pass, output format is identical, and the S3776 violation is resolved.
3. **Given** `model.py:651` has a function with complexity 95, **When** it is decomposed, **Then** model tests pass and the S3776 violation is resolved.
4. **Given** all 35+ S3776 violations are addressed, **When** SonarCloud analyses the project, **Then** zero S3776 CRITICAL issues remain.
5. **Given** `_legacy.py` contains multiple high-complexity functions, **When** they are refactored (or the file is removed if fully superseded), **Then** legacy tests pass and the S3776 violations in that file are resolved.

---

### Edge Cases

- Functions in `_legacy.py` may be partially superseded by the recent modularisation work; verify whether each function is still called before refactoring, and prefer removal over refactoring if the code is dead.
- Some `is` comparisons in test files may correctly be testing object identity (e.g., checking a singleton or a specific cached instance); review each case individually before changing to `==`.
- Wildcard imports may pull in names that are not explicitly referenced in the file but are needed at runtime; audit the actual usage before restricting imports.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All 13 identity-check (S5727) violations MUST be resolved by replacing value-equality `is`/`is not` comparisons with `==`/`!=` where appropriate.
- **FR-002**: All 6 duplicate-string-literal (S1192) violations MUST be resolved by extracting repeated literals into named module-level constants.
- **FR-003**: Both bare-except (S5754) violations MUST be resolved by specifying `Exception` (or a more specific exception class) in every `except` clause.
- **FR-004**: Both wildcard-import (S2208) violations MUST be resolved by replacing `import *` with explicit named imports.
- **FR-005**: The empty-function (S1186) violation MUST be resolved by adding an explanatory comment or completing the implementation.
- **FR-006**: All 35+ cognitive-complexity (S3776) violations MUST be resolved by decomposing each over-threshold function into smaller helpers, with each helper having a complexity score ≤ 15.
- **FR-007**: All existing unit, integration, and BDD tests MUST continue to pass after every remediation change.
- **FR-008**: The public API of every affected production module MUST remain unchanged (no breaking changes to function signatures, class interfaces, or module exports).
- **FR-009**: Refactored helpers MUST be placed in the same module as the original function unless a clearly better module boundary exists.
- **FR-010**: Changes to `_legacy.py` MUST be assessed for whether the code is still in active use before refactoring; dead code SHOULD be removed rather than refactored.

### Key Entities

- **SonarCloud Rule**: A code-quality rule identified by a key (e.g., `python:S3776`) with a defined severity and remediation action.
- **Cognitive Complexity Score**: A numeric measure of how hard a function is to understand; must not exceed 15 after remediation.
- **Module-level Constant**: A named variable defined at module scope to replace repeated string literals; naming must follow project conventions (UPPER_SNAKE_CASE).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: SonarCloud reports zero CRITICAL-severity issues for the `pyArchimate_pyArchimate` component after all changes are merged.
- **SC-002**: The full test suite (unit, integration, BDD) passes with no regressions introduced by the remediation.
- **SC-003**: No function in the production codebase has a cognitive complexity score greater than 15.
- **SC-004**: Total estimated remediation debt falls from 1,731 minutes to 0 minutes as reported by SonarCloud.
- **SC-005**: All public module APIs remain backward-compatible (confirmed by existing tests passing without modification).

## Assumptions

- The SonarCloud token and project key (`pyArchimate_pyArchimate`) remain valid throughout the remediation effort.
- `_legacy.py` functions flagged by SonarCloud are still reachable from production or test code; if they are dead code, removal is preferred over refactoring.
- The allowed cognitive complexity threshold is 15, as specified in the SonarCloud rule configuration for this project.
- Refactoring will be done incrementally per rule category (identity checks → string constants → bare excepts → wildcard imports → empty function → cognitive complexity) to allow focused code review.
- `tests/legacy_*` directories are in scope for this remediation because they contribute to the CRITICAL issue count; however, refactoring scope is limited to the specific violations and does not include a full rewrite of legacy tests.
- The project uses Python 3; idiomatic Python 3 patterns (e.g., `isinstance` checks, f-strings) may be used in refactored code where appropriate.
