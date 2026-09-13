# Implementation Plan: Derived Relationships (Scan & Render-Time Computation)

**Branch**: `worktree-issue-140` | **Date**: 2026-09-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-derived-relationships/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a read-only "derivation" capability to the pyArchimate library: (1) a model-level scan that reports explicit relationships duplicating what a two-step relationship chain already implies per the ArchiMate 3.2 §3.5 derivation rule, and (2) an on-demand query that computes the implied relationship between two elements from such a chain without persisting it. Both are implemented as a new `derivation` module holding the derivation-rule table and chain-walking logic, exposed through the existing `Model` class (mirroring the existing `check_invalid_relationships` pattern) and the public `pyArchimate` API facade. No new dependencies, no changes to file formats, no writes to model or view files.

## Technical Context

**Language/Version**: Python 3.10+ (per `pyproject.toml` `requires-python = ">=3.10,<4.0"`; ruff targets 3.12)
**Primary Dependencies**: None new — stdlib only (`dataclasses`, `enum`, `itertools`), plus existing `pyArchimate` modules (`model.py`, `relationship.py`, `enums.py`, `constants.py`)
**Storage**: N/A — library, file I/O only via the existing `Model`/reader classes; this feature performs no writes
**Testing**: pytest (unit tests for the derivation-rule table and chain-walking; integration tests proving model/view files are byte-identical before and after a scan or query)
**Target Platform**: Cross-platform library (Linux/macOS/Windows), same as the rest of pyArchimate
**Project Type**: Library (single project) — no CLI or web surface exists today for checker-style capabilities; this feature follows that precedent
**Performance Goals**: Scan/query cost scales with the number of relationships touching each element (same order as the existing `Model.check_invalid_relationships`); no new numeric target was requested, so parity with existing checker methods is the bar
**Constraints**: MUST NOT mutate the source model or any view file (FR-004, FR-006); MUST NOT introduce new relationship persistence formats or writer changes
**Scale/Scope**: Models with up to tens of thousands of relationships, consistent with the library's existing checker methods and the constitution's O(n) performance-awareness principle

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Code Quality**: New logic lives in one focused module (`derivation.py`) with small, single-purpose functions (chain discovery, rule lookup, duplicate matching), following the existing `relationship.py`/`model.py` style. PASS.
- **II. Testing Standards**: Plan includes unit tests for the derivation-rule table (every supported type-pair combination, including the "no derivation defined" cells) and integration tests for file-immutability (SC-002) and duplicate-detection accuracy (SC-001). Tests are written before implementation per Red-Green-Refactor. PASS.
- **III. UX Consistency**: The scan and query follow the existing `Model.check_invalid_*` method naming/return-shape convention, so callers already familiar with `check_invalid_relationships` get a predictable interface. PASS.
- **IV. Performance**: No operation here does network or async-worthy I/O; chain-walking is bounded by relationship count per element, matching the existing checker methods' complexity class. PASS.
- **V. Security**: No new external input parsing, no new file I/O, no new attack surface. PASS.
- **VI. State Management**: This feature introduces no new persisted state or lifecycle — its outputs are explicitly transient (FR-006), which is the point of the feature. PASS.
- **VII. System Integrity & Accuracy**: PASS. The derivation-rule table (DR2, DR3, DR5, DR7, DR8) is transcribed directly from Appendix B of a primary copy of the ArchiMate 3.2 Specification, verified on 2026-09-13 (see research.md Decision 1, "Status"), and unit-tested cell-by-cell against that verified table so results are reproducible and traceable to the specific rule and page that authorizes each one. This closes an earlier open item: an initial version of this table (built from secondary web sources only, since the primary spec's pages required authentication unavailable at planning time) contained two real errors — treating `Serving` as a structural relationship instead of a dependency relationship, and over-generalizing dynamic-dynamic combination beyond the one rule (DR8) the specification actually defines — both found and corrected during primary-source verification.
- **VIII. Durability & Interoperability**: No existing format, writer, or reader behavior changes; this is purely additive and read-only, so no migration path is needed. PASS.
- **IX. Cross-Platform Consistency**: Pure Python stdlib logic with no OS-specific behavior. PASS.

No violations requiring Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/015-derived-relationships/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── derivation-api.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
# Option 1: Single project (library) — matches existing pyArchimate layout

src/pyArchimate/
├── derivation.py              # NEW: derivation-rule table, chain walking, DerivedRelationship,
│                               #      DuplicateFinding, find_duplicate_relationships(), derive_between()
├── model.py                   # MODIFIED: add Model.check_derivable_duplicates() and
│                               #           Model.derive_relationship() thin wrappers, mirroring
│                               #           the existing check_invalid_relationships() pattern
├── pyArchimate.py              # MODIFIED: re-export the new public names (facade convention)
├── relationship.py             # UNCHANGED: reused for concept-type lookups only
├── enums.py                    # UNCHANGED: reused ArchiType values
└── constants.py                 # UNCHANGED: reused RELATIONSHIP_KEYS / ARCHI_CATEGORY

tests/
├── unit/
│   └── test_derivation.py      # NEW: derivation-rule table + chain-walking unit tests
└── integration/
    └── test_derivation_roundtrip.py  # NEW: file-immutability + duplicate-detection scenarios
```

**Structure Decision**: Single-project library layout (matches the existing `src/pyArchimate/` structure). No new top-level packages, no CLI, no web/service split — this feature adds one new module plus thin integration points on `Model`, consistent with how `check_invalid_relationships` was added previously.

## Complexity Tracking

*No constitution violations — table not needed.*
