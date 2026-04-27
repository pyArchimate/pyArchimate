# Tasks: AI-Optimized Documentation

## Feature
003-ai-documentation

## Phase 1: Setup
- [ ] T001 Create `scripts/generate_ai_docs.py` scaffolding
- [ ] T002 Initialize `tests/integration/test_tutorial.py`

## Phase 2: Foundational
- [ ] T003 Implement Markdown structural validation (header checks) in `scripts/generate_ai_docs.py`
- [ ] T004 Implement error handling for `claude code` execution in `scripts/generate_ai_docs.py`

## Phase 3: AI Consumption of Library Context (US1) [US1]
- [ ] T005 [P] Create initial draft of `AI.md` based on spec baseline
- [ ] T006 Implement logic to extract docs context for `claude code` in `scripts/generate_ai_docs.py`

## Phase 4: New User Tutorial (US2) [US2]
- [ ] T007 Create `docs/tutorial.md` with step-by-step ArchiMate model examples
- [ ] T008 [P] [US2] Implement tutorial code snippet verification in `tests/integration/test_tutorial.py`

## Phase 5: Automated Documentation Regeneration (US3) [US3]
- [ ] T009 Implement full regeneration script logic in `scripts/generate_ai_docs.py`
- [ ] T010 Verify idempotency of the generation script

## Phase 6: README Discoverability (US4) [US4]
- [ ] T011 Update `README.md` to include links to `AI.md` and `docs/tutorial.md`

## Final Phase: Polish & Cross-Cutting
- [ ] T012 Add documentation instructions for maintainers in `scripts/README.md`
- [ ] T013 Final validation of all success criteria (SC-001 to SC-006)

---

## Dependencies & Parallel Execution

### Story Execution Order
US1 → US2 → US3 → US4

### Parallel Opportunities [P]
- T005, T006 (US1 context gathering)
- T008 (US2 testing infrastructure)

### Implementation Strategy
MVP scope: US1 (AI.md creation and regeneration script basics). Incremental delivery follows with tutorial content (US2), automation maturity (US3), and final polish (US4).
EOF
,file_path: