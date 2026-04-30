# Implementation Plan: AI-Optimized Documentation

**Branch**: `003-ai-documentation` | **Date**: 2026-04-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-ai-documentation/spec.md`

## Summary

Deliver three artefacts: a machine-readable `AI.md` reference document at the repository root, a `docs/tutorial.md` for new users, and a Python regeneration script at `scripts/generate_ai_docs.py` that invokes `claude code` to keep `AI.md` in sync with the library. A `tests/integration/test_tutorial.py` suite verifies that every tutorial code snippet executes without error against the current library. `README.md` is updated with navigation links to both new documents.

## Technical Context

**Language/Version**: Python 3.10+ (pyproject.toml `requires-python = ">=3.10,<4.0"`); ruff targets 3.12  
**Primary Dependencies**: `subprocess` (stdlib) for `claude code` CLI invocation; `pymarkdownlnt` (already in `lint` group) for structural validation; `lxml` (already in project); `pytest` for tutorial verification  
**Storage**: File I/O only — no database. Outputs: `AI.md` (root), `docs/tutorial.md`, `scripts/README.md`  
**Testing**: `pytest` for integration tests (`tests/integration/test_tutorial.py`); `pymarkdownlnt` for Markdown linting  
**Target Platform**: Developer workstation (Linux/macOS), `claude code` CLI in PATH; GitHub markdown rendering as primary view target  
**Project Type**: Developer tooling script + documentation artefacts (not a new package or service)  
**Performance Goals**: Generation script completes in under 5 minutes on a standard workstation (SC-003)  
**Constraints**: No hardcoded credentials — API key via `ANTHROPIC_API_KEY` env var (FR-010); Python-only implementation (FR-013); structural validation before overwrite (FR-012); idempotent structural output across consecutive runs (US3-AC3)  
**Scale/Scope**: 1 script (~150–200 LOC), 2 documentation files, 1 integration test module

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | ✅ PASS | Script decomposed into functions < 30 lines; no magic numbers; descriptive naming |
| II. Testing Standards (TDD) | ✅ PASS | Test stubs written before implementation for T003, T004, T015, T009; T008 harness before T007 content |
| III. UX Consistency | ✅ PASS | Single-command invocation; error messages include resolution steps per FR-012 |
| IV. Performance | ✅ PASS | Script is async by nature (subprocess); < 5 min goal is explicit in SC-003 |
| V. Security | ✅ PASS | FR-010 mandates env-var credentials; T015 adds an assertion test confirming no hard-coded secrets; no new dependencies introduce supply-chain risk (`pymarkdownlnt` already in project) |
| VI. State Management | ✅ PASS | State transitions documented in data-model.md: `raw_source → ai_generated → validated_doc` |
| VII. System Integrity | ✅ PASS | FR-012: script MUST NOT overwrite `AI.md` if validation fails; T003 implements this gate |
| VIII. Durability | ✅ PASS | `AI.md` version-controlled alongside source (FR-009); no migration paths required |
| IX. Cross-Platform | ✅ PASS | Developer tool; no UI rendering paths; subprocess call uses PATH resolution |

**No violations requiring justification in Complexity Tracking.**

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-documentation/
├── plan.md              # This file
├── research.md          # Phase 0 output (exists)
├── data-model.md        # Phase 1 output (exists)
├── quickstart.md        # Phase 1 output (exists)
└── tasks.md             # Phase 2 output (exists)
```

### Source Code (repository root)

```text
AI.md                                  # NEW — machine-readable reference (T005, T014)
README.md                              # UPDATED — navigation links to AI.md and tutorial (T011)

scripts/
├── generate_ai_docs.py                # NEW — Python regeneration script (T001, T003, T004, T006, T009, T015)
└── README.md                          # NEW — maintainer instructions (T012)

docs/
└── tutorial.md                        # NEW — new-user tutorial with ArchiMate guidance (T007)

tests/
└── integration/
    └── test_tutorial.py               # NEW — tutorial snippet verification (T002, T008)
```

**Structure Decision**: Single-project layout (existing `scripts/`, `tests/integration/`, `docs/` directories are already present). No new source packages — this feature adds developer tooling and documentation only, with no changes to `src/pyArchimate`.

## Complexity Tracking

> No constitution violations requiring justification.
