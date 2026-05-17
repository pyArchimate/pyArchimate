# Project Utility Scripts

This directory contains scripts for maintaining code quality, architectural integrity, and generating project documentation.

## Git Hook Setup

Hooks are managed by [pre-commit](https://pre-commit.com/) and configured in `.pre-commit-config.yaml`.
One-time setup per clone:

```bash
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
```

This wires two gates:

- **pre-commit**: ruff lint + format, pymarkdown, vulture — runs on staged files only, fast
- **pre-push**: pyright, mypy, layer boundaries, behave, full pytest suite — runs on every push

To run either gate manually:

```bash
pre-commit run --all-files                        # commit-stage hooks
pre-commit run --all-files --hook-stage pre-push  # push-stage hooks
```

> **Legacy scripts**: `pre_commit_checks.sh` and `pre_push_checks.sh` are superseded by the
> pre-commit hooks above and kept only for reference. Do not use them directly.

---

## Script Catalog

### `check_layer_boundaries.py`

Enforces the project's architectural layering rules (e.g., Layer 2 must not import from Layers 3
or 4). Run automatically by the pre-push hook; also callable directly:

```bash
poetry run python scripts/check_layer_boundaries.py
```

### `check_sonarcloud.py`

Queries the SonarCloud API for open issues on the `pyArchimate_pyArchimate` project and exits
non-zero if any are found. Run as part of the release checklist (step 2b in `how_to_build.md`).

```bash
python scripts/check_sonarcloud.py
```

Set `SONAR_TOKEN` in your environment for private project or rate-limit avoidance.

### `render_diagrams.sh`

Renders all `.puml` files in `docs/diagrams/` to `.png` using the PlantUML web service.
Requires `curl`.

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

**Recommendation:** Use `build_docs.sh` or `build_docs_release.sh` instead for better features
and validation.

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
