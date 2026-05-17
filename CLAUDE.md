# pyArchimate Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-05-15

## Active Technologies
- Python 3.12 + Poetry, lxml, ruff, pyright, mypy, pytest, behave, pysonar (002-sonarqube-remediation)
- N/A (library — file I/O only) (002-sonarqube-remediation)
- Python 3.10+ (pyproject.toml `requires-python = ">=3.10,<4.0"`); ruff targets 3.12 + `subprocess` (stdlib) for `claude code` CLI invocation; `mistune` (Markdown AST parser) for structural validation; `lxml` (already in project); `pytest` for tutorial verification (003-ai-documentation)
- File I/O only — no database. Outputs: `AI.md` (root), `docs/tutorial.md`, `scripts/README.md` (003-ai-documentation)
- Python 3.10+ (per pyproject.toml) + `zipfile` (stdlib), `lxml` (existing), `pathlib` (stdlib) (007-fix-ouput-file-format-issues)
- File I/O only (local filesystem) (007-fix-ouput-file-format-issues)
- Python 3.10+ (per pyproject.toml `requires-python = ">=3.10,<4.0"`) + lxml (ArchiMate XML parsing), existing pyArchimate view model, poetry (package manager) (011-view-auto-layout)
- File I/O only (views are persisted as XML files within .archimate archives) (011-view-auto-layout)
- Python 3.12 + lxml, xml.etree.ElementTree (stdlib), pyArchimate view model (012-enhance-svg-view)
- File I/O only (SVG output, `.archimate`/`.xml` round-trip) (012-enhance-svg-view)
- Python 3.12 + lxml (XML I/O), existing pyArchimate view model (`src/pyArchimate/`) (013-layout-routing-refactor)
- File I/O only — `.archimate` archives (zip+XML) (013-layout-routing-refactor)

- **Language & Package Manager**: Python 3.10+ with Poetry
- **XML Processing**: lxml (for .archimate and OpenGroup exchange format parsing)
- **YAML**: oyaml (for configuration and metadata)
- **Image Handling**: pillow (for diagram export)
- **Testing**: pytest (unit/integration), behave (BDD acceptance tests)
- **Code Quality**: ruff (linting/formatting), mypy/pyright (type checking)
- **Compliance**: pysonar (code quality auditing)

## Current Feature: ArchiMate v3.x Specification Compliance (004)

**Focus**: Close three critical P1 gaps:
1. Enable BusinessInteraction element creation (currently commented out in ARCHI_CATEGORY)
2. Fix influence strength round-trip metadata preservation (field name inconsistency: `modifier` vs `influenceStrength`)
3. Preserve relationship documentation during import/export

**Key Files Affected**:
- `src/pyArchimate/checker_rules.yml` (enable BusinessInteraction category)
- `src/pyArchimate/readers/archimateReader.py` (normalize field names on read)
- `src/pyArchimate/writers/archiWriter.py`, `archimateWriter.py` (use canonical field names)
- `src/pyArchimate/readers/_archireader_helpers.py` (fix documentation extraction bug)
- `src/pyArchimate/relationship.py` (document metadata fields)

**Test Strategy**: Unit + integration round-trip tests + BDD acceptance scenarios (behave)

## Project Structure

```text
src/pyArchimate/          # Core library
tests/                    # Test suite
├── unit/               # Unit tests
├── integration/        # Integration tests (round-trip fidelity)
└── features/          # BDD feature files and steps
specs/                   # Feature specifications
└── 004-archimate-spec-compliance/  # Current feature documentation
```

## Recent Changes
- 013-layout-routing-refactor: Added Python 3.12 + lxml (XML I/O), existing pyArchimate view model (`src/pyArchimate/`)
- 013-layout-routing-refactor: Added Python 3.12 + lxml (XML I/O), existing pyArchimate view model (`src/pyArchimate/`)
- 013-layout-routing-refactor: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->
