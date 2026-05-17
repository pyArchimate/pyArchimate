# Feature Specification: Fix Code Complexity & Pre-commit Enforcement

**Feature Branch**: `014-complexity-precommit`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: User description: "Fix Code Complexity & Pre-commit Enforcement"

## User Scenarios & Testing *(mandatory)*

### User Story 0 - Coverage uplift for under-tested files (Priority: P0 — pre-condition)

Before any refactoring begins, the two files with both low coverage and the most violations must have their test coverage raised to a level where the test suite can reliably catch broken behaviour.

- `view/layout/__init__.py` — 43% coverage, 7 of the 15 violations. At 43%, half the complex code paths are untested; a refactor here could silently break behaviour.
- `view/layout/routing/segment_separation.py` — 71% coverage, contains the single worst function (cognitive complexity 34).

All other affected files are at 84% or above and can be refactored directly.

**Why this priority**: Refactoring without adequate test coverage is high-risk. The test suite is the only safety net; if it does not exercise the code being restructured, it cannot detect regressions.

**Independent Test**: Run the coverage tool against just these two files and confirm both reach ≥ 80% line coverage before any complexity refactoring is attempted.

**Acceptance Scenarios**:

1. **Given** `view/layout/__init__.py` currently has 43% line coverage, **When** new tests are added, **Then** line coverage for that file reaches ≥ 80% and all new tests pass.
2. **Given** `view/layout/routing/segment_separation.py` currently has 71% line coverage, **When** new tests are added, **Then** line coverage for that file reaches ≥ 80% and all new tests pass.
3. **Given** both files reach ≥ 80% coverage, **When** the complexity refactoring is performed, **Then** the test suite detects any unintended behaviour change.

---

### User Story 1 - Developer refactors overly-complex functions (Priority: P1)

A contributor working on the library encounters a function in the layout engine that is deeply nested and hard to follow. After this feature, the contributor can decompose it into smaller, well-named private helpers without changing any public API — and the existing test suite confirms behaviour is unchanged.

**Why this priority**: Cognitive complexity is the root cause of all 15 CRITICAL SonarCloud violations. Fixing them is the primary deliverable and unblocks the quality gate.

**Independent Test**: Run `pytest` and `behave` against each refactored file. If all tests pass and SonarCloud no longer flags the function, the story is complete.

**Acceptance Scenarios**:

1. **Given** a function in `view/layout/__init__.py` with cognitive complexity > 15, **When** it is decomposed into private helper functions, **Then** all unit and BDD tests pass and the function no longer appears in SonarCloud's open issues list.
2. **Given** `view/layout/routing/segment_separation.py` contains a function with cognitive complexity 34, **When** it is refactored, **Then** complexity drops to ≤ 15 and no public interface changes.
3. **Given** any of the 8 affected files has been refactored, **When** the linting tool is run against the source directory, **Then** no complexity violations are reported.

---

### User Story 2 - New contributor is blocked when introducing a complex function (Priority: P2)

A developer adds a new function that is deeply nested. Before their commit is recorded, the pre-commit hook runs the linter and rejects the commit, displaying a clear error that names the file and line number.

**Why this priority**: Without an early gate, complexity regressions are invisible until a cloud scan — which may be hours later. Catching them locally at commit time costs nothing.

**Independent Test**: Create a scratch branch, write a deliberately complex function, attempt `git commit`, and confirm the commit is blocked with a readable error message.

**Acceptance Scenarios**:

1. **Given** pre-commit hooks are installed in the developer's local clone, **When** a developer commits a file containing a function with McCabe complexity > 15, **Then** the commit is rejected and the offending function is identified in the error output.
2. **Given** pre-commit hooks are active, **When** a developer commits a file that passes all complexity checks, **Then** the commit succeeds without delay.
3. **Given** a new contributor clones the repo and runs the documented setup command, **When** they attempt a commit, **Then** the hooks fire automatically without any additional manual step.

---

### User Story 3 - Maintainer verifies zero SonarCloud violations after release (Priority: P3)

After merging this feature, the project maintainer opens the SonarCloud dashboard and confirms there are no open CRITICAL issues under the cognitive complexity rule.

**Why this priority**: This is the final acceptance criterion for the whole feature. It depends on P1 being fully complete and SonarCloud completing a new analysis pass.

**Independent Test**: Query SonarCloud's issue search API for the project and confirm the response contains zero open issues for the cognitive complexity rule.

**Acceptance Scenarios**:

1. **Given** all 15 affected functions have been refactored, **When** SonarCloud completes its next analysis scan, **Then** zero open issues remain for the cognitive complexity rule.
2. **Given** the pre-commit hooks are active, **When** a developer pushes a branch, **Then** CI confirms the linting check passes before a pull request can be merged.

---

### Edge Cases

- What happens when a helper function extracted from a complex function itself becomes too complex? (Each helper must also satisfy the ≤ 15 threshold independently.)
- How does the pre-commit hook behave when no virtual environment is active? (The hook must resolve the project's installed linter, not a system-level one.)
- What if a developer bypasses the pre-commit hook with a force flag? (Acceptable; the gate is a guardrail, not a hard block — the cloud quality scan serves as the final enforcer.)
- What happens when `pre-commit` is not yet installed in a developer's environment? (Setup documentation must include the install step; the hook cannot self-install.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-000**: Line coverage for `view/layout/__init__.py` and `view/layout/routing/segment_separation.py` MUST reach ≥ 80% before any complexity refactoring is performed on those files.
- **FR-001**: The codebase MUST have zero functions with cognitive complexity > 15 in the 8 files identified by the SonarCloud scan (rule `python:S3776`).
- **FR-002**: Refactored functions MUST be decomposed into private helper functions without altering any public method signatures, return types, or observable behaviour. All extracted helpers MUST remain in the same file as the original function (module-private, prefixed `_`); no new sub-modules may be created as part of this refactoring.
- **FR-003**: All existing unit tests and BDD acceptance tests MUST pass after each individual file refactoring. Line coverage for each of the 6 files already at 84%+ MUST finish at or above its pre-refactor level.
- **FR-004**: A pre-commit configuration file MUST be created at the repository root, wiring both the linter (`ruff check`) and the formatter check (`ruff format --check`) to run on staged Python files before every commit.
- **FR-005**: The `pre-commit` package MUST be added to the developer dependency group in the project's dependency manifest.
- **FR-006**: The existing linter configuration MUST NOT be modified — the complexity rule and threshold of 15 are already correctly configured.
- **FR-007**: Developer setup documentation MUST include a single command to activate the pre-commit hooks after cloning the repository.
- **FR-008**: The pre-commit configuration MUST be self-contained and work without network access after the initial hook installation.

### Key Entities

- **Complex function**: Any function whose cognitive complexity (SonarCloud `S3776`) or McCabe complexity (linter `C901`) exceeds 15.
- **Private helper**: A module-level or class-level function extracted to hold a logical sub-unit of a previously complex function, not part of the public API.
- **Pre-commit hook**: A git lifecycle script that runs the linter on staged Python files and prevents the commit if any violation is found.
- **Pre-commit config**: The declarative file at the repository root defining which hooks run and against which file patterns.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero open quality violations for the cognitive complexity rule in the project after the feature is merged, verified by the cloud quality scanner.
- **SC-002**: The linting tool exits with no complexity violations when run against the full source directory on the merged branch.
- **SC-003**: All 15 previously flagged functions have individual cognitive complexity ≤ 15, confirmed by re-scanning.
- **SC-004**: A commit containing a function exceeding the complexity threshold is blocked within 5 seconds of the `git commit` invocation.
- **SC-005**: A commit containing only compliant code completes the pre-commit stage in under 10 seconds on a standard developer machine.
- **SC-006**: Full unit test and BDD acceptance test suite passes with no new failures after all refactoring is complete.
- **SC-010**: Line coverage for each of the 6 files at 84%+ before this feature does not drop below its pre-refactor baseline after refactoring is complete.
- **SC-008**: Line coverage for `view/layout/__init__.py` reaches ≥ 80% before refactoring begins.
- **SC-009**: Line coverage for `view/layout/routing/segment_separation.py` reaches ≥ 80% before refactoring begins.
- **SC-007**: A new contributor can activate the pre-commit hooks with a single documented command after cloning.

## Clarifications

### Session 2026-05-17

- Q: Where should extracted private helpers live? → A: Same file as the original function (module-private, `_` prefix); no new sub-modules.
- Q: Should the pre-commit hook enforce formatting as well as linting? → A: Yes — both `ruff check` (linting/complexity) and `ruff format --check` (formatting) run on staged files.
- Q: Should the 6 files already at 84%+ coverage be protected from regression after refactoring? → A: Yes — each must finish at or above its pre-refactor coverage level.

## Assumptions

- The 8 files identified in the SonarCloud report are the complete set of violations; no additional files exceed the threshold at the time of implementation.
- `view/layout/__init__.py` is at 43% line coverage and `view/layout/routing/segment_separation.py` is at 71% — both require coverage uplift before refactoring. All other affected files are at 84%+.
- Coverage data is from the most recent `build/coverage.xml` report; actual figures should be verified before implementation begins.
- All affected functions are internal implementation details; no public API changes are required to achieve compliant complexity.
- The linter's McCabe complexity (C901) and the cloud scanner's cognitive complexity (S3776) use different algorithms — passing the local linting check is a necessary but not sufficient condition for clearing the cloud violations. Manual verification via the cloud scanner remains required after merging.
- Contributors are expected to have `git` installed and basic familiarity with running setup commands.
- Pre-commit hooks are opt-in for existing contributors; hooks will not auto-install — developers must run the setup command once per clone.
- CI already runs the linter; the pre-commit hook provides an earlier local gate only.
- No new runtime dependencies are introduced — the pre-commit tool is a developer-only setup dependency.
- Type-checking tools (mypy/pyright) are not included in the pre-commit hook for this feature due to latency; this can be revisited in a future quality uplift.
