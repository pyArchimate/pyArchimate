# pyArchimate Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-30

## Active Technologies

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

- **004-archimate-spec-compliance** (current): ArchiMate v3.x compliance fixes (BusinessInteraction, influence strength, relationship documentation)
- **002-sonarqube-remediation**: Code quality improvements (linting, type checking)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current feature plan:
`specs/004-archimate-spec-compliance/plan.md`
<!-- SPECKIT END -->
