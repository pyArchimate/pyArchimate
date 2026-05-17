# Tasks: AI-Optimized Documentation

## Feature
003-ai-documentation

## Phase 1: Setup
- [X] T001 Create `scripts/generate_ai_docs.py` scaffolding
- [X] T002 Initialize `tests/integration/test_tutorial.py`

## Phase 2: Foundational
- [X] T003 Implement Markdown structural validation (header checks) in `scripts/generate_ai_docs.py`
- [X] T004 Implement error handling for `claude code` execution in `scripts/generate_ai_docs.py`
- [X] T015 Implement and test environment-variable credential reading in `scripts/generate_ai_docs.py` (FR-010); add a test asserting no credentials are hard-coded

## Phase 3: AI Consumption of Library Context (US1) [US1]
- [X] T005 [P] Create initial draft of `AI.md` based on spec baseline
- [X] T006 Implement logic to extract docs context for `claude code` in `scripts/generate_ai_docs.py`
- [X] T014 Add "Non-Conformances" section to `AI.md` listing known deviations from the current ArchiMate standard and Archi import/export compatibility gaps (FR-016)

## Phase 4: New User Tutorial (US2) [US2]
- [X] T007 Create `docs/tutorial/tutorial.md` with step-by-step ArchiMate model examples, including ArchiMate standard background guidance with references (FR-015) in a collapsible section for experienced users
- [X] T008 [P] [US2] Implement tutorial code snippet verification in `tests/integration/test_tutorial.py`

## Phase 5: Automated Documentation Regeneration (US3) [US3]
- [X] T009 Implement full regeneration script logic in `scripts/generate_ai_docs.py`
- [X] T010 Verify idempotency of the generation script

## Phase 6: README Discoverability (US4) [US4]
- [X] T011 Update `README.md` to include links to `AI.md` and `docs/tutorial/tutorial.md`

## Final Phase: Polish & Cross-Cutting
- [X] T012 Add documentation instructions for maintainers in `scripts/README.md`
- [X] T013 Final validation of all success criteria (SC-001 to SC-006)

---

## Dependencies & Parallel Execution

### Story Execution Order
US1 → US2 → US3 → US4

### Parallel Opportunities [P]
- T005, T006 (US1 context gathering; T014 sequential after T005)
- T008 (US2 testing infrastructure)

### Implementation Strategy
MVP scope: US1 (AI.md creation and regeneration script basics). Incremental delivery follows with tutorial content (US2), automation maturity (US3), and final polish (US4).
