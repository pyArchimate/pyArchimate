# Feature Specification: Incremental Code Quality Uplift

**Feature Branch**: `009-quality-uplift`  
**Created**: 2026-05-03  
**Status**: Draft  
**Input**: User description: "I want to do a quality uplift, remediating the remaining issues in sonarqube and incrementally enabling more checks in ruff, pyright and mypy. There are some exclusions in @pyproject.toml I would like to remove also as I think they are now obsolete."

## References

- **SonarCloud outstanding issues**: `https://sonarcloud.io/api/issues/search?projectKeys=pyArchimate_pyArchimate&severities=CRITICAL,MAJOR,MINOR&statuses=OPEN,CONFIRMED`
- **SonarCloud project**: `pyArchimate_pyArchimate`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Remediate Remaining SonarQube Issues (Priority: P1)

A developer opening the SonarCloud dashboard for pyArchimate sees a residual set of code smells, bugs, and security hotspots that survived the earlier `002-sonarqube-remediation` sprint. Resolving these issues brings the project to a clean SonarCloud Quality Gate and eliminates technical debt accumulated since the last remediation cycle.

**Why this priority**: A clean Quality Gate is the most visible code quality signal for contributors and CI. Unresolved issues grow stale and harder to fix as the codebase evolves.

**Independent Test**: Run the SonarCloud scan on the branch after each batch of fixes; the issue count drops toward zero and no new violations are introduced.

**Acceptance Scenarios**:

1. **Given** unresolved SonarCloud issues remain from the `002` sprint, **When** each issue is reviewed and either fixed or justified with a suppression comment, **Then** the SonarCloud Quality Gate status transitions to "Passed" with zero new issues.
2. **Given** a SonarCloud issue is a confirmed false positive, **When** a suppression comment (`# NOSONAR` or equivalent) is added with an explanatory note, **Then** the issue no longer appears in the active issues list and the justification is visible in the code.
3. **Given** a code change resolves a SonarCloud issue, **When** the fix is committed, **Then** no new SonarCloud issues are introduced in the same file or related modules.

---

### User Story 2 - Enable Additional Ruff Lint Rules (Priority: P1)

A developer running `ruff check` on the codebase wants the linter to enforce a wider set of rules beyond the current baseline (`E`, `F`, `W`, `B`, `C`, `I`, `S110`). The four targeted rule sets are `UP` (pyupgrade), `N` (naming conventions), `A` (shadowing builtins), and `PT` (pytest style). Each is attempted incrementally; if a rule set surfaces more than 20 violations it is deferred to a follow-up feature with a documented TODO rather than abandoned.

**Why this priority**: Ruff runs on every save and in CI; expanding the rule set has immediate payoff and is the lowest-friction quality lever available.

**Independent Test**: Enable one rule set at a time, run `ruff check`, resolve all newly reported violations, then commit. Each commit leaves the codebase in a fully passing state for the enabled rules.

**Acceptance Scenarios**:

1. **Given** the `C901` complexity rule is currently ignored, **When** the ignore is removed after reducing cognitive complexity in prior work (feature `002`), **Then** `ruff check` passes with no C901 violations, confirming the ignore is truly obsolete.
2. **Given** a new rule set (e.g., `UP`) is added to the `select` list, **When** `ruff check` is run, **Then** either zero violations are reported or each violation is resolved before the rule set is committed as active.
3. **Given** the `N999` (module name) ignore is in place, **When** the codebase is audited, **Then** if all module files now conform to the naming convention the ignore is removed; otherwise it is retained with a documented reason.
4. **Given** the `PLC0415` (non-top-level import) ignore is in place, **When** the dynamic-import pattern that necessitated it is reviewed, **Then** it is removed if no longer needed or retained with a comment explaining the pattern.

---

### User Story 3 - Tighten Pyright Type-Checking Configuration (Priority: P2)

A developer running `pyright` on the codebase sees several categories of type errors that are currently silenced by broad `"none"` settings (e.g., `reportAttributeAccessIssue`, `reportArgumentType`, `reportOptionalMemberAccess`). Re-enabling these categories one at a time and resolving the underlying type errors improves IDE feedback, catches real bugs, and moves the project toward full static type safety.

**Why this priority**: Type errors hidden by pyright suppression flags represent latent runtime bugs. Enabling them incrementally avoids a large disruptive flag-day.

**Independent Test**: Re-enable one pyright category at a time, run `pyright`, resolve all newly reported errors, then commit. Each commit leaves pyright passing with the newly enabled category.

**Acceptance Scenarios**:

1. **Given** `reportAttributeAccessIssue = "none"`, **When** this setting is changed to `"warning"` or `"error"`, **Then** `pyright` passes (possibly after type annotation fixes or `# type: ignore` suppressions with justifications).
2. **Given** `reportArgumentType = "none"`, **When** this setting is re-enabled, **Then** all previously hidden argument-type mismatches are either corrected or explicitly suppressed with justifications.
3. **Given** `reportOptionalMemberAccess = "none"`, **When** this setting is re-enabled, **Then** all optional-member accesses are guarded with appropriate null checks or casts.

---

### User Story 4 - Strengthen Mypy Strict Checks (Priority: P2)

A developer running `mypy` observes that despite `strict = true` in `pyproject.toml`, several strictness flags are explicitly disabled (`disallow_untyped_calls = false`, `disallow_untyped_defs = false`). Re-enabling these flags incrementally and adding missing type annotations brings mypy into genuine strict compliance.

**Why this priority**: Mypy strictness flags have a compounding effect: enabling them surfaces annotation gaps that, once fixed, improve both pyright and IDE tooling simultaneously.

**Independent Test**: Enable one flag at a time, run `mypy src/`, resolve all newly reported errors, then commit. Each commit leaves `mypy` passing.

**Acceptance Scenarios**:

1. **Given** `disallow_untyped_defs = false`, **When** this is changed to `true`, **Then** `mypy src/` passes after adding return-type and parameter-type annotations to all previously unannotated functions.
2. **Given** `disallow_untyped_calls = false`, **When** this is changed to `true`, **Then** all calls to untyped functions are resolved either by annotating the callee or by adding explicit `# type: ignore` suppressions with justifications.
3. **Given** `warn_return_any = true` is already enabled, **When** the other strict flags are fully enabled, **Then** no function returns `Any` without an explicit documented reason.

---

### User Story 5 - Remove Obsolete Exclusions from pyproject.toml (Priority: P3)

> **Scope note**: This story is a final audit pass that verifies the `pyproject.toml` outcomes of US2 (ruff), US3 (pyright), and US4 (mypy). It does not re-execute those changes — it confirms they landed correctly and that every remaining suppression carries a justification comment.

A developer reviewing `pyproject.toml` notices several lint/type-check ignores and exclusions that were added as workarounds during earlier development phases (e.g., `C901`, `N999`, `PLC0415` in ruff; suppressed pyright categories). Each exclusion is audited: if the underlying issue is now resolved, the exclusion is removed; if still needed, a comment is added explaining why it remains.

**Why this priority**: Obsolete suppressions silently hide future regressions. Removing them ensures the tool chain enforces the rules it appears to enforce.

**Independent Test**: Remove one exclusion at a time, run the relevant tool (`ruff check`, `pyright`, `mypy`), and confirm it passes. Restore the exclusion if the tool fails and document the remaining gap.

**Acceptance Scenarios**:

1. **Given** `"C901"` is in the ruff ignore list, **When** it is removed, **Then** `ruff check` passes, confirming no functions exceed the complexity threshold.
2. **Given** `"N999"` is in the ruff ignore list, **When** it is removed, **Then** `ruff check` passes, confirming all module names conform to naming conventions.
3. **Given** `"PLC0415"` is in the ruff ignore list, **When** it is removed or replaced with a file-level suppression for the specific dynamic-import pattern, **Then** `ruff check` passes.
4. **Given** pyright has `reportAttributeAccessIssue = "none"` et al., **When** these are removed after the type fixes in Story 3, **Then** `pyright` passes without them.

---

### Edge Cases

- A SonarCloud issue may be a legitimate false positive due to lxml's dynamic type system; in such cases a suppression with an explanatory comment is acceptable.
- Enabling a new ruff rule set may conflict with existing code patterns that are intentional (e.g., the dynamic-import pattern covered by `PLC0415`); these must be explicitly retained and documented.
- Some mypy strictness flags may not be achievable without invasive refactoring; in such cases the flag remains disabled with a documented ticket reference.
- Removing a pyright suppression may expose issues in third-party stubs rather than project code; those should be suppressed at the call site with a comment referencing the stub limitation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All remaining SonarCloud issues MUST be reviewed; each is either fixed or suppressed with an inline justification comment.
- **FR-002**: After remediation, the SonarCloud Quality Gate MUST pass with zero unresolved issues (excluding legacy test exclusions already in `sonar-project.properties`).
- **FR-003**: No fix MAY introduce new SonarCloud violations, ruff errors, pyright errors, or mypy errors.
- **FR-004**: Each ruff rule set addition MUST be committed independently with a passing `ruff check` at the time of commit.
- **FR-005**: Each pyright category re-enablement MUST be committed independently with a passing `pyright` run at the time of commit.
- **FR-006**: Each mypy strictness flag re-enablement MUST be committed independently with a passing `mypy src/` run at the time of commit.
- **FR-007**: Each obsolete `pyproject.toml` exclusion removal MUST be verified by running the relevant tool and confirming it passes before committing.
- **FR-008**: Any suppression comment added (`# NOSONAR`, `# type: ignore`, `# noqa`) MUST include a brief justification explaining why the suppression is appropriate.
- **FR-009**: The `tests/legacy_*` directories MUST remain excluded from SonarCloud analysis (existing `sonar-project.properties` exclusions are not modified).
- **FR-010**: All existing tests MUST continue to pass after each change batch.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: SonarCloud Quality Gate transitions to "Passed" with zero unresolved issues in the active codebase (excluding legacy test directories).
- **SC-002**: All four required ruff rule sets (`UP`, `N`, `A`, `PT`) are either active with `ruff check` passing, or deferred with a documented TODO; at least two are active at feature completion.
- **SC-003**: At least two currently-suppressed pyright categories are re-enabled: first confirmed passing at `"warning"` level, then promoted to `"error"` level with `pyright` passing.
- **SC-004**: At least one currently-disabled mypy strictness flag (`disallow_untyped_defs`, `disallow_untyped_calls`) is re-enabled and `mypy src/` passes with no errors; if both flags produce more than 20 violations when probed, each is deferred with a documented violation-count TODO in `pyproject.toml` and SC-004 is considered conditionally met (mirroring the ruff deferral policy in FR-004).
- **SC-005**: At least one obsolete `pyproject.toml` exclusion is removed and the relevant tool continues to pass.
- **SC-006**: Every suppression comment added as part of this work includes a justification (zero unexplained suppressions introduced).
- **SC-007**: The full test suite (unit, integration, BDD) continues to pass at the conclusion of the feature.

## Remaining Work (Deferred Items)

The following items were scoped and probed during this feature but exceed the 20-violation cap policy or require deeper refactoring. They MUST be resolved before this feature is considered complete.

| Item | Location | Violations | Blocker |
|------|----------|-----------|---------|
| Enable ruff `UP` (pyupgrade) rule set | `pyproject.toml:121` | 124 | UP042/UP032 need semantic review; most others auto-fixable |
| Enable ruff `PT` (pytest style) rule set | `pyproject.toml:124` | 163 | Primarily PT009 unittest assertions in legacy tests |
| Enable mypy `disallow_untyped_calls` | `pyproject.toml:101` | 89 | Requires annotating callee functions or adding justified `# type: ignore` |
| Enable mypy `disallow_untyped_defs` | `pyproject.toml:102` | 162 | Requires adding return-type and parameter annotations to unannotated functions |

**Acceptance**: Feature is complete only when all four `# TODO(009-quality-uplift)` markers are removed from `pyproject.toml` and the corresponding tools pass.

---

## Assumptions

- The SonarCloud project key is `pyArchimate_pyArchimate`; open issues are queried via the API at the URL in the References section above. The existing CI/CD pipeline triggers a scan on push to the feature branch (consistent with feature `002`).
- The `002-sonarqube-remediation` feature has already been merged; this feature targets only the residual issues that remain after that work.
- The `C901` (complexity) ignore in ruff may be removable because feature `002` decomposed the most complex functions; this will be verified empirically.
- `disallow_untyped_defs` in mypy may require significant annotation work; it is treated as a stretch goal — partial enablement (e.g., per-module overrides) is acceptable if full enablement proves too invasive.
- Changes are batched by tool category (SonarQube fixes → ruff rule additions → pyright re-enablement → mypy strictness → exclusion removals) to keep diffs reviewable.
- The `tests/legacy_*` directories are intentionally excluded from static analysis tools and that exclusion policy does not change.
