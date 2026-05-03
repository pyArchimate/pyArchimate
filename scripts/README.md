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

### `build_docs.sh`
Quick incremental build for development. Generates HTML documentation in `docs/build/html/`.

**Usage:**
```bash
./scripts/build_docs.sh [--clean] [--open]
```

**Options:**
- `--clean` — Remove old build and rebuild from scratch
- `--open` — Open documentation in your default browser

**When to use:** During documentation development for fast iteration.

### `build_docs_release.sh`
Full release build with validation. Performs a clean build and validates:
- No broken cross-references
- All documents included in toctree
- No RST syntax errors
- Proper HTML generation

**Usage:**
```bash
./scripts/build_docs_release.sh [--deploy]
```

**When to use:** Before releasing or publishing documentation to ensure quality.

### `create_documentation.sh`
Legacy script. Builds the project's Sphinx documentation into `build/html`. 

**Recommendation:** Use `build_docs.sh` or `build_docs_release.sh` instead for better features and validation.

### `generate_ai_docs.py`

Regenerates `AI.md` from the current state of `docs/` using the Claude CLI.

**When to run:** Re-run whenever the `docs/` folder is updated to keep `AI.md`
in sync with the library.

**Prerequisites:**

- Python 3.10+
- `claude` CLI in `PATH` (install via `pip install claude-code`)
- `ANTHROPIC_API_KEY` environment variable set

**Usage:**

```bash
export ANTHROPIC_API_KEY=<your-key>
python scripts/generate_ai_docs.py
```

The script validates the generated content (required sections and Markdown
syntax) before overwriting `AI.md`. If validation fails, `AI.md` is not
modified and an error is printed to stderr.

---

## Prerequisites

Ensure you have the following installed:
- [Poetry](https://python-poetry.org/) for dependency management.
- Python 3.10+
- `bash` shell.
- `curl` (for diagram rendering).
