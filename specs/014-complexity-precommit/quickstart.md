# Quickstart: Feature 014 — Fix Code Complexity & Pre-commit Enforcement

## Prerequisites

- Python 3.10+
- Poetry (dependency management)
- git

## Environment Setup

```bash
# Install all dependency groups including dev and testing
poetry install --with dev,testing,lint

# Verify ruff is available
poetry run ruff --version
```

## Running Tests

```bash
# Run the full test suite with coverage
poetry run pytest

# Run only the tests for the files being refactored
poetry run pytest tests/unit/view/layout/ tests/unit/test_segment_separation.py -v --tb=short

# Check coverage for a specific file
poetry run pytest --cov=src/pyArchimate/view/layout --cov-report=term-missing tests/unit/view/layout/
```

## Checking Complexity

```bash
# Check McCabe complexity across the full source tree (C901, max 15)
poetry run ruff check src/ --select C901

# Check a single file
poetry run ruff check src/pyArchimate/view/layout/__init__.py --select C901

# Check formatting
poetry run ruff format --check src/
```

## Coverage Baseline Verification

Before starting any refactoring, verify the current coverage baseline matches the snapshot
in `data-model.md`:

```bash
poetry run pytest --cov=src/pyArchimate --cov-report=term-missing --no-header -q
```

Confirm these files match their baseline percentages before proceeding.

## Installing Pre-commit Hooks (after .pre-commit-config.yaml is created)

```bash
# One-time setup per clone
poetry run pre-commit install

# Verify hooks fire correctly
poetry run pre-commit run --all-files
```

## Verifying Public API Contract

After each file refactoring, confirm the public contract is unbroken:

```bash
# Example for layout module
python3 -c "
from pyArchimate.view.layout import apply_format, apply_layout, auto_layout, auto_route, undo_layout
print('layout API: OK')
"
```

Repeat for each file per `contracts/public-api.md`.

## Running BDD Acceptance Tests

```bash
poetry run behave tests/features/
```

## Checking SonarCloud Violations (requires SONAR_TOKEN in .env)

```bash
# Local scan
pysonar --sonar-token=$(grep SONAR_TOKEN .env | cut -d= -f2)

# Remote API check (no token needed for public project)
curl -s "https://sonarcloud.io/api/issues/search?projectKeys=pyArchimate_pyArchimate&rules=python:S3776&statuses=OPEN" | python3 -m json.tool | grep '"total"'
```

## Commit Convention

All commits on this branch must follow Conventional Commits:

```text
refactor(layout): decompose auto_route into private helpers
test(layout): uplift view/layout/__init__.py coverage to 83%
chore(pre-commit): add .pre-commit-config.yaml with ruff gates
```
