# Project Utility Scripts

This directory contains scripts for maintaining code quality, architectural integrity, and generating project documentation.

## Git Hook Setup

Automate your workflow by integrating these scripts into your Git lifecycle.

### Pre-commit Hook

The `pre_commit_checks.sh` script performs fast checks (linting, formatting, type-checking, and unit tests) that should pass before every commit.

To set it up:

```bash
ln -sf ../../scripts/pre_commit_checks.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Pre-push Hook

The `pre_push_checks.sh` script runs the full test suite, including integration and acceptance tests. It is recommended to run this before pushing to a remote or merging a PR.

To set it up as a pre-push hook:

```bash
ln -sf ../../scripts/pre_push_checks.sh .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

---

## Script Catalog

### `pre_commit_checks.sh`
The primary developer workflow script. It performs:
- Dependency synchronization via Poetry.
- Markdown linting (`pymarkdownlnt`).
- Python linting and formatting (`ruff`).
- Static type checking (`pyright` and `mypy`).
- Unit tests (`pytest tests/unit/`).

### `pre_push_checks.sh`
A heavier suite intended for CI or pre-push gates. It includes:
- All checks from `pre_commit_checks.sh`.
- Architectural boundary enforcement.
- Acceptance tests (`behave`).
- Integration, API, and Security test suites.
- Code coverage reporting.

### `check_layer_boundaries.py`
Enforces the project's architectural layering rules (e.g., Layer 2 must not import from Layers 3 or 4). This is called automatically by `pre_push_checks.sh`.

### `render_diagrams.sh`
Renders all `.puml` files in `docs/diagrams/` to `.png` using the PlantUML web service. Requires `curl`.

### `create_documentation.sh`
Builds the project's Sphinx documentation into `build/html`.

---

## Prerequisites

Ensure you have the following installed:
- [Poetry](https://python-poetry.org/) for dependency management.
- Python 3.10+
- `bash` shell.
- `curl` (for diagram rendering).
