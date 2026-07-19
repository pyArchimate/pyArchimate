# Technical Specifications and Guidelines

This document consolidates technical specifications, patterns, utilities, and preferred libraries. It provides specific guidance that complements the high-level principles outlined in the *SpecKit Constitution* (`.specify\memory\constitution.md`).

## Code Style

- **Indentation**: 4 spaces; no tabs.
- **Line Length**: Maximum 120 characters; break after operators; use backslash for line continuation.
- **Naming Conventions**:
  - Variables and functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`
  - Avoid single-character variable names (except loop counters).
- **Comments**:
  - Single-line: `#`
  - Docstrings: `"""`
  - Comment complex logic.
  - Update comments when code changes.

## File Structure

- **File Naming**: Descriptive names in `snake_case`.
- **Modularity**: Keep related functionality in the same module.
- **Separation of Concerns**: Separate concerns into different files.
- **Reusability**: Separate reusable components into different packages.
- **Package Initialization**: Use `__init__.py` for package initialization.

## Patterns and Practices

- **Model and View Building Patterns**:
  - `Model.add()` accepts Profile instances as `concept_type`, automatically extracting `ArchiType` and uuid without restatement, enabling more fluent model construction.
  - `View.adjust()` moves and/or resizes nodes by accepting the node itself, its element, or its element UUID as the reference argument, reducing caller boilerplate for incremental diagram updates.
  - `Model.check_invalid_relationships()` re-validates every relationship in the model against the ArchiMate metamodel and returns offending UUIDs, exposed via `pyArchimate.helpers.properties` and the top-level public API for pre-export validation.
- **Testing**:
  - Write tests for all new functionality.
  - Stub functions to facilitate testing before production code is fully implemented.
  - Aim for greater than 90% test coverage.
  - Test positive and negative cases.
  - Use descriptive test function names.
    - *See SpecKit Constitution II. Testing Standards for core principles.*
- **Documentation**:
  - Document all public functions with docstrings.
  - Include type hints where appropriate.
  - Keep documentation up-to-date with code changes.
  - Use Google-style docstrings.
- **Version Control**:
  - Commit frequently with meaningful messages.
  - Use present tense in commit messages.
  - Follow semantic versioning.
  - Keep commits small and focused.
  - Use `commitizen` for managing version changes.
  - Adopt the Conventional Commits specification for commit message structure (e.g., feat, fix, refactor, chore) to ensure consistency and facilitate automated changelog generation.
  - Ensure every commit on your branch already follows Conventional Commits so that Commitizen can reliably infer the version bump (patch/minor/major) and update the changelog.
- **Security**:
  - *For overarching security principles, refer to SpecKit Constitution V. Security Practices.*
- **Performance**:
  - Avoid unnecessary computations.
  - Use efficient data structures.
  - Profile code when performance is critical.
  - Consider memory usage for large datasets.
    - *Refer to SpecKit Constitution IV. Performance Requirements for fundamental guidelines.*
- **Code Quality**:
  - Keep functions small and focused.
  - Avoid code duplication.
  - Use meaningful variable names.
  - Write readable and maintainable code.
  - Use strict type casting.
  - Use native types (e.g., `list`, `dict`) over `typing` library equivalents (e.g., `List`, `Dict`).
    - *For broader quality principles, see SpecKit Constitution I. Code Quality.*
- **Diagramming**:
  - When documenting in UML and C4, use PlantUML and C4-PlantUML.
  - Primarily focus on structural representation.
  - When documenting instance information, use appropriate diagram types such as UML Object diagrams, and include examples in parentheses.
- **Shell Scripting Best Practices**:
  - Use `set -euo pipefail` for robust script execution.
  - Implement explicit error checking and informative logging for commands.
  - Prefer using helper functions for common operations (e.g., `run_command`).

## Automated Code Uplift and Quality Improvement

The concept of using autonomous agents to uplift code quality and incrementally increase test coverage involves leveraging AI-driven tools and automated processes for iterative improvement. It is designed for an iterative development process where an AI coding assistant works alongside static analysis and test coverage tools.

### Core Concepts

- **Isolated Development Environment**: Employs `git worktree` to establish an isolated branch for modifications, preventing interference with the main codebase. A dedicated Python virtual environment (`venv`) is also established to manage dependencies specifically for this uplift process, ensuring consistency and reproducibility.

- **AI-Assisted Fixing**: Integrates with an AI coding assistant (e.g., Aider) configured for autonomous operations, including auto-accepting suggestions, auto-committing fixes, and performing automated linting and testing. Specific parameters for the AI model must be clearly defined to tailor its interventions effectively.

- **Iterative Static Analysis and Correction**: The core workflow involves:
    1. Running static type checking using a chosen static analysis tool on individual files.
    2. If the static analysis tool reports errors, these are relayed to the AI assistant along with the file path for contextual awareness.
    3. The AI assistant attempts to resolve the reported errors autonomously, applying context-aware recommendations.
    4. Following corrections, the file is re-evaluated using the static analysis tool. This loop continues until the tool reports no errors, ensuring compliance with type safety and quality standards.

- **Incremental Test Coverage Enhancement**: The process consists of:
    1. Evaluating the current state of test coverage within the codebase.
    2. Identifying specific code segments (such as functions, branches, or files) that lack sufficient test coverage.
    3. Generating targeted test cases for these segments, potentially utilizing AI assistance to comprehend code behavior and formulate precise assertions.
    4. Integrating the newly generated tests into the existing test suite and verifying their successful execution to ensure an overall increase in test coverage.

- **Configuration Management**: Specific configuration files are dynamically generated to tailor the AI assistant's behavior, encompassing parameters like the selected AI model and enabling autonomous capabilities. This flexibility allows adaptation to varying project needs and workflows.

- **Outcome Metrics and Considerations**: To gauge the success of this automated process, metrics such as reduced bug counts, improvement in test pass rates, and time savings in code reviews should be established and monitored. Additionally, potential challenges such as dependency conflicts and AI reasoning errors should be anticipated and addressed proactively.

## XML Round-Trip Testing and Field Mapping Patterns

The following patterns ensure data fidelity when reading, modifying, and writing XML-based ArchiMate formats:

### Round-Trip Fidelity Testing

- **Test Structure**: Create integration tests that verify export/import cycles:
  1. Create model with specific data (elements, relationships, metadata)
  2. Export to target format (.archimate or OpenGroup XML)
  3. Re-import the exported file
  4. Assert that imported data matches original exactly (or within expected transformations)
  5. Export again and compare to previous export (ensuring idempotency)

- **Metadata Preservation**: When testing round-trip fidelity for metadata fields:
  - Create test fixtures with known metadata values in test files (place in `tests/fixtures/`)
  - Verify field names are correctly mapped during import (canonical Python names in model)
  - Verify field names are correctly written during export (format-specific names in XML)
  - Test both happy path (valid values) and edge cases (empty, special characters, Unicode)

### Field Name Mapping (Multi-Format Support)

- **Canonical Field Storage**: Store metadata using Python snake_case field names internally (e.g., `influence_strength`, `description`)
- **Format-Specific Mapping**: When reading/writing different formats:
  - `.archimate` format (Archi tool): Use format-specific field names in XML (e.g., `influenceStrength`, `<documentation>` element)
  - OpenGroup exchange format: Use format-specific field names (e.g., `influenceStrength` attribute)
  - Map these format names to canonical Python names when importing; reverse map when exporting
  
- **Legacy Field Support**: When importing, support deprecated/legacy field names with fallback logic:
  - Example: Read `modifier` field if `influenceStrength` is missing, store as `influence_strength`
  - Document the fallback chain (primary name → legacy names)
  - Always write using the primary/canonical name on export (ensuring forward compatibility)

- **Implementation Location**: Place mapping logic in reader helpers (e.g., `_archireader_helpers.py`)
  - Create helper functions for field extraction: `extract_field(elem, primary_name, *legacy_names)`
  - This centralizes mapping rules and reduces duplication across readers

### Test Fixture Management

- **Fixture Directory**: Store sample ArchiMate files in `tests/fixtures/`
  - Include files with known metadata (influence strength values, documentation text)
  - Include files with edge cases (empty fields, Unicode characters, special XML characters, long text)
  - Include files created by external tools (Archi) to verify interoperability

- **Fixture Naming**: Use descriptive names to indicate fixture purpose:
  - `business_interaction_simple.archimate` - Basic element with no metadata
  - `influence_relationship_with_strength.archimate` - Relationship with strength metadata
  - `documented_relationship_unicode.archimate` - Relationship with Unicode documentation

### Connection and Annotation Connector Patterns

- **Connection Property Null-Safety**: Connection properties (`concept`, `type`, `name`) return `None` for annotation-only connectors (e.g., note-to-element lines) instead of raising `KeyError` on missing reference. Guard metamodel endpoint checks with `has_valid_ref` to avoid `AttributeError` when processing synthetic connectors.
- **Annotation Connectors**: `View.connect_note()` creates purely visual connectors from Label/Note nodes to other nodes without requiring a backing `Relationship`. These connectors render in SVG with null-safe property access and omit the `archimateRelationship` attribute during XML export, matching Archi's behavior.
- **Auto-Resolve Endpoints**: `View.add_connection()` auto-resolves source/target nodes from a relationship's own source/target concepts when those node arguments are omitted, reducing boilerplate when adding connections to views.
- **Node Reference Resolution**: `View._resolve_view_node()` is a shared helper for resolving a node from a Node object, an Element, or a UUID — used by both `View.adjust()` and `View.connect_note()` to normalize caller input.

### SVG Export Configuration

- **Stereotype Label Rendering**: `SVGExportService.show_stereotypes` flag (default `False`) enables rendering of `«ProfileName»` labels above element names in smaller italic font, following ArchiMate specialization notation. Exposed via `View.to_svg(show_stereotypes=True)`.
- **Note/Label Rendering**: Label nodes render as folded-corner sticky notes using two `<path>` elements (body and dog-ear) with left-aligned text, replacing previous rectangular fallback rendering.
- **Profile Style Application**: `apply_profile_styles(view, mapping)` applies profile-specific fill/line/font colors across all view nodes recursively. Mapping values can be a plain hex string (fill only) or a dict with `fill_color`, `line_color`, and `font_color` keys.
- **Enum Handling**: `_get_short_type_name()` strips ArchiType enum prefix before applying suffix trimming so relationship labels render correctly regardless of whether `conn.type` returns an enum or string.

### P3 Implementation Patterns

The following patterns were established during the P3 notation support implementation and should be followed for future metadata extensions:

#### Element Hierarchy (Containment)

- Parent-child relationships are stored at the **Model** level in two complementary dicts: `_element_hierarchy` (child→parent) and `_element_children` (parent→children). The `Element` holds a back-reference `_parent_uuid` for O(1) parent lookup.
- Serialization uses a `parentId` XML attribute on `<element>` tags. Both the Archi `.archimate` format (`archiWriter.py`) and the OpenGroup Exchange format (`archimateWriter.py`) write and read `parentId`, so round-trip fidelity is guaranteed in both formats.
- **Cascade rule**: Deleting a parent orphans children; it never cascades deletes. Document this explicitly in any code that deletes elements.
- Always use `model.add_child()` (not direct dict mutation) so both dicts stay in sync and cycle detection runs.

#### Junction Type Semantics

- Junction type is stored as a lowercase string (`'and'`, `'or'`, `'xor'`) on `Element.junction_type`, not as a separate class.
- Use `set_junction_type()` — never set `element.junction_type` directly — so validation runs.
- The two formats serialize junctions differently: `archiWriter` writes a `type` attribute plus a `junctionType` property (only for `elem_type == "Junction"`); `archimateWriter` encodes OR/AND semantics directly in `xsi:type` (`OrJunction`/`AndJunction`) and only writes a `junctionType` property for plain `Junction` elements as a fallback. On import, the `junctionType` property is applied last and overrides any type inferred from `xsi:type`.

#### Visual Style Properties

- Visual properties are stored in `Element._visual_style: dict` using camelCase XML keys (`fillColor`, `lineColor`, `lineWidth`, `transparency`) to eliminate a mapping step during serialization.
- Colors are normalized to lowercase 6-digit hex at **set time** (inside `set_fill_color()`/`set_line_color()`) via `_normalize_color()`, not during XML serialization. Never store raw color strings — always go through the setter.
- Absent key = property not set. `None` argument to a setter removes the key. Do not inject default values into `_visual_style`; apply defaults at render time only.
- This property-dict pattern (introduced for viewpoints, reused for visual styles) is the preferred approach for optional element metadata: unrecognised property keys during import fall through to `elem.prop(key, value)` and are stored as regular element properties, preserving them for round-trips without breaking the import.

### Requirements Traceability

- **Explicit Mapping**: Maintain a Requirements Traceability Matrix linking:
  - Functional Requirements (FR-001, FR-002, etc.) → Task IDs
  - Success Criteria (SC-001, SC-002, etc.) → Test Functions
  - User Stories (US1, US2, US3) → Test Modules
- **Verification**: Use this matrix to verify:
  - 100% of requirements have corresponding tasks
  - 100% of tasks are marked complete
  - 100% of success criteria are tested
- **Location**: Store in tasks.md as an early-reference table to reduce artifact navigation

### Documentation and Contributor Onboarding

- **Quickstart Guide**: Create `specs/<feature>/quickstart.md` with:
  - Environment setup steps (virtualenv, dependencies)
  - Required environment variable configuration
  - Command to run tests locally
  - How to interpret results (passing vs. failing)
  - How to run individual tests or subsets
- **Test Module README**: Include `tests/api/README.md` that:
  - Describes fixture locations and purposes
  - Lists all helper utilities
  - Provides examples of common test patterns
  - Links to full specification and quickstart
- **AGENTS.md Integration**: Tag the test suite in AGENTS.md with:
  - Complete project structure showing test organization
  - Full command reference for running tests
  - Current coverage and performance metrics
  - Dependencies and prerequisites
- **Architecture Diagram Discipline**: When a feature affects module boundaries, package exports, or architecture behavior, update the relevant PlantUML sources under `docs/diagrams` (e.g., `package.puml`, `class.puml`, `component.puml`), rerun `scripts/render_diagrams.sh`/`scripts/create_documentation.sh`, and list the affected diagrams in the feature spec so the published docs always match the code.

## Error Management

- **Exception Handling**: Use the custom exceptions `ArchimateConceptTypeError` and `ArchimateRelationshipError` for validation failures; let them propagate to callers rather than swallowing silently.
- **Logging over printing**: Use `pyArchimate.logger` (backed by stdlib `logging`) for all diagnostic output. Callers control verbosity via `log_set_level()`.

## Observability and Logging

- **Log Levels**: Use standard levels (DEBUG, INFO, WARNING, ERROR) via `pyArchimate.logger`. WARNING and above indicate actionable problems (broken references, invalid relationships).
- **Centralized config**: All logging configuration is routed through `helpers/logging.py`; never call `logging.basicConfig()` inside library code.

## Continuous Integration and Continuous Deployment (CI/CD)

- **Automated Pipelines**: Establish CI/CD pipelines for automated building, testing, linting, and deployment.
- **Build Automation**: Ensure consistent and reproducible builds.
- **Automated Testing**: Integrate all automated tests (unit, integration, BDD) into the CI pipeline to run on every commit.
- **Linting and Formatting**: Integrate `Ruff` or similar tools into the pipeline to enforce code style and quality.
- **Deployment Strategy**: Define clear deployment strategies (e.g., blue-green, canary releases) and automate deployment processes where feasible.
- **Behave Tag Filtering**: Configure default tag exclusions in `pyproject.toml` under `[tool.behave]` — this is the single source of truth applied to all invocations (pre-commit, CI, VS Code extension). Do not duplicate the flag in individual scripts. Scenarios tagged `@wip` signal unimplemented step definitions; running them produces `status="error"` in JUnit XML which tools like `behave-vsc` cannot parse.

```toml
[tool.behave]
paths = ["tests/features/"]
tags = ["not @wip"]
```

## Project Configuration

- **pyproject.toml**: Adhere to [PEP 621](https://peps.python.org/pep-0621/) for defining project metadata and configuration.

## Software Architectural Patterns

- **Model-View-Controller (MVC)**: A common pattern for structuring applications, separating concerns into model (data and business logic), view (UI), and controller (handles input and updates).
- **Two-Tier and Three-Tier Architectures**: Understand and apply standard architectural patterns for client-server applications, separating presentation, application logic, and data management layers as appropriate for the solution.
- **Finite State Machines (FSM)**: Employ FSMs to model entities with distinct states and transitions, ensuring predictable lifecycles, data integrity, and controlled workflows. This pattern is especially useful for entities with complex operational states or governance processes.

## Domain-Driven Design (DDD)

- **Ubiquitous Language**: Establish and use a common language shared by developers and domain experts throughout the project.
- **Bounded Contexts**: Define clear boundaries for different parts of the domain model, managing complexity and allowing for independent evolution.
- **Aggregates and Entities**: Design domain models around aggregates to enforce invariants and manage consistency. FSMs often complement DDD by managing the state of aggregates or entities.

## Utilities and Frameworks

- **Testing Frameworks**: `pytest`, `pytest-mock`, `behave` (for BDD), `pytest-asyncio`, `pytest-cov`
- **Linters/Formatters**: `Ruff` (rules: E, F, W, B, C, I, S110, A, N, ARG, UP; max-complexity 15)
- **Dead Code Detection**: `vulture` (run with `--min-confidence 80`)
- **Type Checkers**: `MyPy` (strict mode, `disallow_untyped_defs/calls` currently disabled — see `009-quality-uplift`), `PyRight` (basic mode)
- **Markdown Linting**: `pymarkdownlnt`
- **Build/Dependency Management**: Poetry — prefer `poetry install`, `poetry run`, and pipeline scripts defined in `pyproject.toml`. Keep `requirements.txt` in sync via the push-stage pre-commit hook. Fall back to `uv` only when Poetry lacks the needed capability.
- **XML Processing**: `lxml`
- **YAML**: `oyaml`
- **Image Handling**: `pillow`

### Python Specifics

- **Dataclass Argument Order**: When defining dataclasses, ensure all non-default arguments (fields without default values) are listed before any arguments with default values. Failing to do so will result in a `TypeError`.
- **Side-Effect Imports**: When importing a module solely for its decorator side effects (e.g., Behave step registration), use `from package import module` rather than `import package.module.path`. The latter form binds only the top-level package name, which CodeQL flags as unused. Declare `__all__` in the aggregator file to satisfy both ruff (F401) and CodeQL:

```python
from tests.features.layout import auto_format_steps, auto_layout_steps
__all__ = ["auto_format_steps", "auto_layout_steps"]
```

- **Explicit Re-Exports**: Use `from module import Name as Name` (same-name alias) when building a public API shim. Ruff recognises this pattern as an intentional re-export and does not raise F401 — `# noqa: F401` is redundant on these lines.
- **Avoiding Circular Imports**: Be mindful of import dependencies between modules. A common pitfall occurs when module A imports from module B, and module B simultaneously imports from module A, leading to `ImportError`. Refactor code to break these cycles, often by moving shared logic or type hints to a separate, lower-level module.
- **Import Style for `src` Layouts**: For projects using a `src` layout (where application code resides in a `src` directory), ensure `src` is correctly added to `PYTHONPATH` (e.g., via `pyproject.toml` or build tools). Subsequently, remove redundant `src.` prefixes from import statements (e.g., use `from frictionless_architect.models.module import ...` instead of `from src.models.module import ...`) for cleaner, more idiomatic Python.
- **Mypy Configuration for `src` Layouts**: For projects utilizing a `src` directory structure, correctly configuring `mypy` in `pyproject.toml` is crucial to avoid "Duplicate module named" or `[import-untyped]` errors.
  - **Module Name Collisions**: Ensure that Python files within different subdirectories of `src` (e.g., `src/models/account.py` and `src/schemas/account.py`) do not share the same base filename (e.g., `account.py`). If they do, rename one (e.g., `account_schema.py`) and update all corresponding import statements to prevent `mypy` from flagging duplicate module names.
  - **Package Discovery**: Use `mypy_path = "src"` to instruct `mypy` to find top-level modules (like `models`, `schemas`, `services`, `api`) directly within `src`.
  - **Explicit Package Listing**: Combine `mypy_path = "src"` with `packages = ["models", "schemas", "services", "api", "tests"]` within the `[tool.mypy]` section to explicitly tell `mypy` which packages (relative to `mypy_path`) to type-check, including the `tests` directory. Avoid `files = ["src", "tests"]` when using `mypy_path` and `packages` as it can lead to duplicate processing.

### Testing

- **Static Analysis vs. Runtime Exception Tests**: When writing tests that specifically aim to assert a `TypeError` or other runtime exceptions for syntactically incorrect code (e.g., missing required arguments in a constructor call), static analysis tools like `pyright` may flag these test calls as errors. To satisfy static analyzers, consider providing valid but semantically "empty" or "invalid" values (e.g., empty strings for required string fields) and then validate these values with runtime logic (e.g., using `__post_init__` in dataclasses to raise `ValueError`).
- Write tests for all new functionality.
- Stub functions to facilitate testing before production code is fully implemented.
- Aim for greater than 90% test coverage.
- Test positive and negative cases.
- Use descriptive test function names.
  - *See SpecKit Constitution II. Testing Standards for core principles.*

## Testing Layout

Unit tests live under `tests/unit/...`, so there is one `test_<module>.py` file per production module.

## Dependency Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management.

- Add dependency
  - `poetry add <package>`
  - `poetry add <package> --group dev`
  - examples: `poetry add requests`, `poetry add pytest --group dev`

- Remove dependency
  - `poetry remove <package>`

- Install all groups
  - `poetry install --with dev,testing,lint,docs`
  - or just the default groups: `poetry install`

- Update dependencies
  - Upgrade one package: `poetry add <package>@latest`
  - Upgrade all packages: `poetry update`

- Lock dependencies / regenerate lockfile
  - `poetry lock`

- Show dependencies / tree
  - `poetry show`
  - `poetry show --tree`

- Run a command in the venv
  - `poetry run <command> [args...]`
  - examples: `poetry run python`, `poetry run pytest`

- Spawn a shell in the venv
  - `poetry shell`

- Build package
  - `poetry build`

- Publish package
  - `poetry publish [--repository <repo>]`

- Show project info / metadata
  - `poetry env info`

Notes:

- All dependency groups are defined in `[dependency-groups]` in `pyproject.toml`. Use `poetry <command> --help` for full option lists.

## SonarQube

To force a SonarQube check, run:

```bash
sudo apt-get update && sudo apt-get install -y default-jre
pysonar --sonar-token=<token-from-.secrets>
```

You can also query SonarCloud public API for the current critical issues list; the token value is stored in the project `.env` file (look for the SONAR_TOKEN key there) and should not be committed.

```text
https://sonarcloud.io/api/issues/search?projectKeys=pyArchimate_pyArchimate&severities=BLOCKER,CRITICAL,MAJOR,MINOR&statuses=OPEN,CONFIRMED
```

### Local Tool Coverage for SonarCloud Rules

The table below maps common SonarCloud rules to the local tools that catch them at pre-commit time. Use this to configure tooling so issues are caught before CI rather than after.

| SonarCloud Rule | Description | Local Tool | Notes |
|---|---|---|---|
| S1172 | Unused function parameter | ruff `ARG` | Enabled for `src/`; excluded from `tests/` (mocks, BDD steps) |
| S1940 | Chained `startswith`/`endswith` | _(no ruff equivalent)_ | Fix manually: use tuple arg `str.startswith(("a", "b"))` |
| S3776 | Cognitive complexity > 15 | ruff `C901` (`max-complexity=15`) | C901 measures McCabe complexity — different metric, may not flag same functions |
| Unused global variable | Module-level dead code | `vulture --min-confidence 80` | Gap: vulture skips `_`-prefixed constants by design; CodeQL is authoritative |
| Wildcard `import *` | Namespace pollution | ruff `F403` | Already enabled; do not suppress with `# noqa` — fix the import instead |

### SonarCloud Remediation Workflow

When new SonarCloud issues appear on `main`, follow this sequence:

1. Pull the latest `main` and request the open issues via the API (same URL as above); review the payload for every problem marked `OPEN`.
2. Implement fixes in the repo so each rule is satisfied (document FastAPI exceptions, tighten validators, simplify routers, adjust services, etc.).
3. Run the full pre-commit suite via `pre-commit run --all-files --hook-stage pre-push` (executes
   pyright, mypy, layer boundaries, behave, pytest unit/integration/legacy).
4. Stage the modified files and commit with a conventional summary such as `fix: resolve SonarCloud issues`.
5. Push the updated commit to `origin/main` so SonarCloud can re-scan.

## Snyk

To force a Snyk check, run:

```bash
npm install -g snyk@latest
snyk auth <token>
snyk test --command=python3
```

## Specification and Requirements Management

Experience from implementing feature 002-add-api-pytests has revealed critical practices for managing specifications, plans, and tasks effectively:

### Artifact Consistency and Traceability

- **Three-Tier Artifact Model**:
  - **spec.md**: Functional Requirements (FR), Non-Functional Requirements (NFR), Success Criteria (SC), User Stories
  - **plan.md**: Architecture choices, data models, technical strategy, phased approach
  - **tasks.md**: Concrete task breakdown, implementation sequencing, test mapping
  - Each artifact must remain in sync; inconsistencies create confusion during implementation
- **Requirement Numbering**: Assign stable identifiers to requirements (e.g., FR-001, SC-001) and reference them consistently across all artifacts. Avoid implicit requirements or vague references.
- **Requirement Validation**:
  - FR/SC must be measurable (avoid vague terms like "fast" or "scalable" without units)
  - Placeholder terms (TODO, TKTK, ???) must be resolved before implementation
  - User stories must have explicit acceptance criteria linked to success criteria

### Requirements Traceability Matrix

- **Mandatory Component**: After task generation, create a table mapping Requirements ? Tasks:
  - Columns: Requirement ID, Type (FR/NFR), Task IDs, User Story, Success Criteria
  - Validates 100% of requirements are covered by tasks
  - Validates no orphaned tasks exist without requirement linkage
  - Serves as implementation verification checklist
- **Update Strategy**: Maintain the matrix in tasks.md as the primary reference. Update it whenever requirements change, new tasks are added, or mappings are discovered incorrect.
- **Example Structure**:
  
  ```markdown
  | FR-001 | API test infrastructure | T001-T006 | Setup | SC-001, SC-002 |
  | FR-002 | Account creation endpoint | T007-T010 | US1 | SC-002 |
  ```

### Documentation-First Approach

- **Specification Before Implementation**: Write spec.md, plan.md, and tasks.md *before* coding to clarify scope, detect conflicts early, and enable team review.
- **Quickstart Guides**: Create feature-specific quickstart guides (`specs/<feature>/quickstart.md`) that provide step-by-step setup, environment variables, test commands, and failure modes.
- **Artifact Interconnection**: Link artifacts explicitly with cross-references between spec.md, plan.md, and tasks.md to show how design decisions address requirements and how phases map to task groupings.

### Constitution Alignment Verification

- **Non-Negotiable Principles**: Before implementation, verify compliance with project constitution:
  - System Integrity & Accuracy (VII): Validate computations, flows, and state transitions for correctness
  - Durability & Interoperability (VIII): Protect data continuity and integration contracts
  - Cross-Platform Consistency (IX): Avoid OS-specific code and verify UI/behavioral parity
  - Code Quality (I), Testing (II), Security (V): Build in from day 1
- **Constitution Violations**: Any conflict must be resolved *before* implementation starts�never proceed if a constitution principle is violated.

### Quality Gate Patterns

- **Analysis Before Implementation**: Run cross-artifact analysis tools (e.g., speckit.analyze) after task generation to detect ambiguities, duplications, unmapped tasks, terminology inconsistencies, and constitution violations.
- **High-Signal Findings**: Prioritize by severity:
  - CRITICAL: Constitution violations, missing artifacts, zero-coverage requirements
  - HIGH: Duplicate/conflicting requirements, untestable acceptance criteria
  - MEDIUM: Terminology drift, missing non-functional coverage
  - LOW: Style/wording improvements
- **Remediation**: Address CRITICAL/HIGH findings before implementation; track MEDIUM/LOW as post-implementation refinements.
