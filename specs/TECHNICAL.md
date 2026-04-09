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

## API Testing Patterns (Integration Testing with httpx)

The following patterns and practices have been established for API-level integration testing:

### Test Infrastructure Architecture

- **In-Process ASGI Testing**: Use `httpx.AsyncClient` with `ASGITransport` to test FastAPI applications without spinning up external servers. This provides realistic full-stack coverage with minimal overhead (~2-3 seconds for 7 tests).
- **Deterministic Fixtures**: Create seeded test data via pytest fixtures that:
  - Set up known, repeatable account hierarchies (visible, hidden, placeholder accounts)
  - Provide explicit cleanup (teardown) hooks to ensure test isolation
  - Use fixture-scoped cleanup to prevent test pollution

### JWT Token Management in Tests

- **JWT Helper Utilities**: Create a dedicated `jwt_utils.py` module that:
  - Generates short-lived test tokens matching app configuration
  - Uses the same algorithm/secret as the application (read from environment)
  - Allows test-specific payload customization (user ID, roles, etc.)
  - Does not share implementation with production JWT code to avoid circular dependencies
- **Environment-Driven Configuration**: Read JWT settings from environment variables (`FRICTIONLESS_ARCHITECT_JWT_SECRET`, `FRICTIONLESS_ARCHITECT_JWT_ALGORITHM`) in `conftest.py` so tests adapt to runtime configuration

### Test Data Cleanup and Isolation

- **Fixture Cleanup Strategy**: Use pytest `yield` fixtures with explicit cleanup blocks to:
  - Delete test-created accounts after each test
  - Reset database state (SQLite) to clean slate
  - Ensure tests are truly independent and can run in any order

### Test Assertion Helpers

- **Shared Assertion Utilities**: Create a `helpers.py` module with reusable validators:
  - `assert_http_status(response, expected_code)` - Verify HTTP status without exposing full response details
  - `assert_payload_contains(response, required_keys)` - Validate response structure
  - `reset_test_database(db_session)` - Clean state between tests
  - These helpers reduce duplication and provide consistent error messaging

### Test Module Organization

- **Three-Tier Test Coverage**:
  - **test_accounts.py**: Happy-path and filtering for core resources (2-3 tests)
  - **test_transactions.py**: Business logic and hierarchy effects (2-3 tests)
  - **test_validation.py**: Error paths, auth failures, and edge cases (3-4 tests)
- **Test Naming Convention**: Use explicit, action-oriented names:
  - `test_create_and_get_account` (setup + verify)
  - `test_list_accounts_filters` (feature-specific)
  - `test_unauthorized_request_returns_401` (error case)
- **Parallel Execution**: Organize tests so they can run concurrently:
  - Tests should not share mutable state
  - Use unique IDs for created resources
  - Rely on cleanup fixtures, not test ordering

### CI/CD Integration

- **Test Runner Script**: Create `scripts/run_api_tests.sh` that:
  - Activates the virtual environment
  - Ensures API is running (or skips with graceful exit)
  - Executes pytest with consistent flags (`-v`, `--tb=short`, coverage options)
  - Generates both human-readable and machine-readable output (JUnit XML for CI)
  - Returns appropriate exit codes for pass/fail/skip scenarios
- **GitHub Actions Integration**: Integrate into CI workflows by:
  - Running in an isolated step after dependency installation
  - Setting timeout limits for test suite (5-10 minutes)
  - Collecting coverage reports and artifacts

### Performance and Stability

- **Target Execution Time**: Aim for <5 seconds total for a ~7-test suite (acceptability threshold for dev feedback loop)
- **Flakiness Prevention**:
  - Use `pytest-asyncio` with `asyncio_mode = "auto"` for async test handling
  - Avoid hardcoded timeouts; use application-defined values
  - Ensure database cleanup is deterministic (not time-dependent)
  - Run full suite multiple times locally before committing to verify consistency
- **Code Coverage**: Expect 60-70% coverage for integration tests (more granular coverage via unit tests):
  - API endpoints: 70-80%
  - Models: 90-95%
  - Schemas (DTOs): 100%
  - Services: 50-60% (complementary unit tests for edge cases)

### Requirements Traceability

- **Explicit Mapping**: Maintain a Requirements Traceability Matrix linking:
  - Functional Requirements (FR-001, FR-002, etc.) ? Task IDs
  - Success Criteria (SC-001, SC-002, etc.) ? Test Functions
  - User Stories (US1, US2, US3) ? Test Modules
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

- **Consistent Error Responses**: Define a standard format for API error responses (e.g., JSON structure including error code, message, and details) for predictable client-side handling.
- **Exception Handling**: Implement robust try-except blocks to catch and handle exceptions gracefully, preventing application crashes.
- **Meaningful Error Codes**: Utilize standardized HTTP status codes for API errors and define custom error codes for specific application-level issues.

## Observability and Logging

- **Structured Logging**: Implement structured logging (e.g., JSON format) to facilitate easier parsing and analysis of log data.
- **Log Levels**: Utilize standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) appropriately to categorize messages.
- **Centralized Logging**: Consider strategies for aggregating logs from different services/components into a central system for monitoring and analysis.
- **Metrics Collection**: Instrument the application to collect key performance indicators (KPIs) and system metrics (e.g., request latency, error rates, resource usage) for monitoring and alerting.
- **Distributed Tracing**: For microservices or complex workflows, implement distributed tracing to track requests across multiple services.

## Continuous Integration and Continuous Deployment (CI/CD)

- **Automated Pipelines**: Establish CI/CD pipelines for automated building, testing, linting, and deployment.
- **Build Automation**: Ensure consistent and reproducible builds.
- **Automated Testing**: Integrate all automated tests (unit, integration, BDD) into the CI pipeline to run on every commit.
- **Linting and Formatting**: Integrate `Ruff` or similar tools into the pipeline to enforce code style and quality.
- **Deployment Strategy**: Define clear deployment strategies (e.g., blue-green, canary releases) and automate deployment processes where feasible.

## API Design Principles

- **RESTful Conventions**: Adhere to RESTful principles for API design, including resource-based URLs, appropriate HTTP methods (GET, POST, PUT, DELETE), and status codes.
- **API Versioning**: Implement a clear versioning strategy (e.g., URL path versioning) for managing API evolution.
- **Authentication and Authorization**: Define secure mechanisms for authenticating API consumers and authorizing access to resources.
- **Data Validation**: Utilize `Pydantic V2` for request and response data validation to ensure data integrity.
- **State Transition Enforcement**: When designing APIs for entities modeled as FSMs, use Pydantic models to define valid states and enforce transition rules. Prefer action-based endpoints (e.g., `/resource/{id}/action`) that trigger state changes as side-effects, rather than direct state updates, to maintain workflow integrity.

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

- **Testing Frameworks**: `pytest`, `pytest-mock`, `behave` (for BDD)
- **Linters/Formatters**: `Ruff`
- **Type Checkers**: `MyPy`, `PyRight`
- **Build/Dependency Management**: This repository uses Poetry for dependency/deployment scripts, so prefer `poetry install`, `poetry run`, and pipeline scripts defined in `pyproject.toml`. Keep `requirements.txt` in sync with `pyproject.toml`. Fall back to `uv` only when Poetry lacks the needed capability or when a spec explicitly says so.
- **Package Installation/Running**: `UV`
- **API Framework**: `FastAPI`
- **UI Frameworks**: `Streamlit`, `Chainlit` (for building interactive UIs and LLM-based applications)
- **Messaging/Orchestration**: `CrewAI` (implied by usage context)
- **Utilities for LLM**: `LiteLLM`
- **Data Validation**: `Pydantic V2`

### Python Specifics

- **Dataclass Argument Order**: When defining dataclasses, ensure all non-default arguments (fields without default values) are listed before any arguments with default values. Failing to do so will result in a `TypeError`.
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

To set up `uv`, run:

```bash
sudo apt-get update
pip install --upgrade uv
```

- Initialize a project
  Use this when starting a new Python project.
  - Create a new project with a pyproject.toml.
  `uv init`
  `uv init my-project`
  `uv init --package`
  `uv init --app`

- Env / venv management (uv venv namespace)
  - List venvs: `uv venv list`
  - Create venv: `uv venv create [--python <python>] [--path <path>]`
  - Use/select venv: `uv venv use <name-or-path>`
  - Remove venv: `uv venv remove <name>`
  - Show venv info: `uv venv show <name>`
  - Activate shell for specific venv: `uv venv shell <name>`

- Add dependency
  - uv: `uv add <package> [--group <group>] [--dev] [--version <constraint>]`
  - examples: `uv add requests`, `uv add pytest --group dev`

- Remove dependency
  - uv: `uv remove <package>`

- Install / sync including all groups / extras
  - uv: `poetry update`
  - or to include specific groups: `uv sync --upgrade --groups dev,tests,lint,docs`

- Update dependencies
  - Upgrade one package:
  `uv lock --upgrade-package requests`
  - Upgrade all packages:
  `uv lock --upgrade`
  - Then sync:
  `uv sync`

- Lock dependencies / generate lockfile
  - uv: `uv lock [--no-update]`

- Show dependencies / tree
  - uv: `uv show [--tree] [<package>]`

- Run a command in the venv, run scripts / entry points defined in pyproject
  - uv: `poetry run -- <command>` or `poetry run <command> [args...]`
  - example: `poetry run python`, `poetry run pytest`
  - uv: `poetry run <script-name>` (scripts exposed via project config)

- Spawn a shell in the venv
  - uv: `uv shell`

- Build package
  - uv: `uv build [--format wheel,sdist]`

- Publish package
  - uv: `uv publish [--repository <repo>]`

- Show project info / metadata
  - uv: `uv info`

- Security audit
  - uv: `uv audit`

Notes:

- Flags/option names above follow the uv CLI documented patterns (e.g., `--all`, `--groups`, `--python`). Use `uv <command> --help` for full option lists and exact formatting for your uv version.

## SonarQube

To force a SonarQube check, run:

```bash
sudo apt-get update && sudo apt-get install -y default-jre
pysonar --sonar-token=<token-from-.secrets>
```

You can also query SonarCloud�s public API for the current critical issues list; the token value is stored in the project `.secrets` directory (look for the Sonar token key there) and should not be committed.

```
https://sonarcloud.io/api/issues/search?componentKeys=wolffy-au_frictionless-architect&branch=main&ps=50&p=1&token=<token-from-.secrets>
```

### SonarCloud Remediation Workflow
When new SonarCloud issues appear on `main`, follow this sequence:

1. Pull the latest `main` and request the open issues via the API (same URL as above); review the payload for every problem marked `OPEN`.
2. Implement fixes in the repo so each rule is satisfied (document FastAPI exceptions, tighten validators, simplify routers, adjust services, etc.).
3. Run the full pre-commit suite via `scripts/pre_commit_checks.sh` (this already executes markdown/ruff/pyright/mypy/snyk/behave/pytest).
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
