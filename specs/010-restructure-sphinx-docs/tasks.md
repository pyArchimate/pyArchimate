# Implementation Tasks: Restructure Sphinx Documentation

**Feature**: 010-restructure-sphinx-docs  
**Branch**: `010-restructure-sphinx-docs`  
**Date**: 2026-05-03  

---

## Task Breakdown

### Phase 1: Setup & Dependencies

Enable Markdown support in Sphinx (blocking all other work).

- [ ] T001 Add `myst-parser` to `docs/requirements.txt`
- [ ] T002 Add `myst-parser` to `pyproject.toml` docs optional-dependency group
- [ ] T003 Update `docs/conf.py`: add `myst_parser` to extensions list
- [ ] T004 Update `docs/conf.py`: add `source_suffix` mapping for `.rst` and `.md` files

**Completion Test**: `pip install -r docs/requirements.txt && python -c "import myst_parser"` succeeds without error

---

### Phase 2: Foundational Navigation Structure

Rebuild the documentation index to support three-tier navigation (blocking all page creation).

- [ ] T005 Rewrite `docs/index.rst`: create three `toctree` sections (Basic Usage, Intermediate / Architecture, Advanced / API Reference)
- [ ] T006 [P] Create `docs/hierarchy-styling-overview.rst` stub (one-page redirect to hierarchy, styling, and junction guides)
- [ ] T007 [P] Verify all three toctree sections reference valid pages (no forward-reference errors in next phase)

**Completion Test**: `make clean html` produces zero `document isn't included in any toctree` warnings; sidebar displays three labeled sections

---

### Phase 3: User Story 1 — Basic Usage (P1 - New User Learns Basic Concepts)

Goal: Users can start with pyArchimate in under 2 minutes (SC-001).

#### 3.1 Basic Landing Pages

- [ ] T008 [P] [US1] Create `docs/getting-started.rst`: Installation (1-liner) + Minimal Working Example (15-line code block from tutorial.md §2-3) + What's Next links
- [ ] T009 [P] [US1] Create `docs/concepts.rst`: The Three Layers table + Elements (ArchiType + shim note) + Relationships (type table) + Views/Diagrams + Viewpoints (brief) + Properties
- [ ] T010 [P] [US1] Add tier label (`.. note::`) to `docs/getting-started.rst` top: "ℹ️ **Basic Usage**"
- [ ] T011 [P] [US1] Add tier label (`.. note::`) to `docs/concepts.rst` top: "ℹ️ **Basic Usage**"

#### 3.2 Wire Tutorial into Sphinx

- [ ] T012 [US1] Verify `docs/tutorial/tutorial.md` is discoverable by Sphinx (no edits needed; `myst-parser` + `source_suffix` handle it)

**Completion Test**: 
- New user can open `docs/_build/html/getting-started.html`, copy the code example, run it successfully
- `concepts.rst` defines all terms used in getting-started example
- `make clean html` zero warnings
- Three Basic Usage pages visible in sidebar under "Basic Usage" section

**Independent Success Criterion**: SC-001 (2-minute Getting Started runnable) + SC-002 (visible tier separation)

---

### Phase 4: User Story 2 — Intermediate Usage (P2 - Architect & Extend)

Goal: Users understand the architecture and can extend/integrate pyArchimate (SC-003, SC-004).

#### 4.1 Architecture & Guides

- [ ] T013 [P] [US2] Create `docs/architecture.rst`: Package Structure table (module → responsibility) + Layered Dependencies prose + `.. include:: diagrams.rst` + Extension Points section
- [ ] T014 [P] [US2] Create `docs/guides/extending.rst`: Custom Readers (registry pattern) + Custom Writers (enum pattern) + Custom Properties/Profiles + Logging Integration + Import Shim notes
- [ ] T015 [P] [US2] Add tier label (`.. note::`) to `docs/architecture.rst` top: "🔧 **Intermediate / Architecture**"
- [ ] T016 [P] [US2] Add tier label (`.. note::`) to `docs/guides/extending.rst` top: "🔧 **Intermediate / Architecture**"

#### 4.2 Recreate Deleted Guides (fix broken refs from api/*.rst)

- [ ] T017 [P] [US2] Create `docs/guides/element-hierarchy.rst`: Overview + Creating Hierarchies (add_child, max depth 5) + Querying (get_parent/children/ancestors/descendants/depth/find_by_hierarchy_path) + Removing + Round-Trip Preservation + See Also → `api/model` + `examples/hierarchy_examples`
- [ ] T018 [P] [US2] Create `docs/guides/visual-styling.rst`: Color Model + Per-Element Styling (set/get fill/line/transparency) + Bulk Styling (set_visual_style dict) + Model-wide Themes (default_theme) + Round-Trip + See Also → `api/element` + `examples/styling_examples`
- [ ] T019 [P] [US2] Create `docs/guides/junction-types.rst`: What Is Junction + Supported Types table (AND/OR/XOR) + Set/Get + Typical Patterns + See Also → `api/element`
- [ ] T020 [P] [US2] Add tier label (`.. note::`) to each guide top: "🔧 **Intermediate / Architecture**"

#### 4.3 Recreate Deleted Examples (fix broken refs from guides/*.rst)

- [ ] T021 [P] [US2] Create `docs/examples/hierarchy_examples.rst`: 4 self-contained code blocks (3-level parent-child, path wildcard, subtree walk, cycle detection); all code valid against current API
- [ ] T022 [P] [US2] Create `docs/examples/styling_examples.rst`: 4 self-contained code blocks (hex + named colors, bulk set_visual_style, theme + override, round-trip verification); all code valid against current API
- [ ] T023 [P] [US2] Add tier label (`.. note::`) to each example top: "🔧 **Intermediate / Architecture**"

#### 4.4 Update concepts.rst with full content

- [ ] T024 [US2] Expand `docs/concepts.rst`: Add Viewpoints section listing all 13 standard viewpoints (slug, name, description); cross-ref to `api/viewpoints`
- [ ] T025 [US2] Verify all concept definitions use canonical terminology from spec clarifications

**Completion Test**:
- Developer can read Architecture Overview and map package structure to source files in `src/pyArchimate/`
- Developer can follow Extending guide and understand where to hook in custom readers/writers
- All code examples in guides + examples are runnable and valid
- `make clean html` zero warnings; all `:doc:` refs resolve
- Sidebar shows 4 guide pages + 2 example pages under "Intermediate / Architecture"

**Independent Success Criterion**: SC-003 (API documented with examples) + SC-004 (package structure mapped)

---

### Phase 5: User Story 3 — Advanced API Reference (P3 - Power Users & Contributors)

Goal: Comprehensive API documentation with design rationale (SC-003, SC-005).

#### 5.1 Advanced API Pages

- [ ] T026 [P] [US3] Create `docs/api/viewpoints.rst`: Overview (get_viewpoints, get_elements_by_viewpoint, assign_viewpoint, remove_viewpoint) + Standard Viewpoints table (13 slugs + names + descriptions from viewpoint_registry.py) + Code Example + `.. automodule::` for pyArchimate.viewpoint + pyArchimate.viewpoint_registry
- [ ] T027 [P] [US3] Add tier label (`.. note::`) to `docs/api/viewpoints.rst` top: "⚙️ **Advanced / API Reference**" with "New to this topic?" link to `guides/extending`

#### 5.2 Add "New to this topic?" notes to existing Advanced API pages

- [ ] T028 [P] [US3] Add "New to this topic?" note at top of `docs/api/element.rst` linking to `guides/visual-styling` and `guides/junction-types`
- [ ] T029 [P] [US3] Add "New to this topic?" note at top of `docs/api/model.rst` linking to `guides/element-hierarchy`

#### 5.3 Verify API examples & doctest setup (cross-phase)

*Note: T030–T032 are validation tasks for code examples created in US1 and US2. Grouped here in Phase 5 for dependency ordering (doctest setup requires all example pages to exist), but not labeled with [US#] to indicate cross-story scope.*

- [ ] T030 Add Sphinx doctest directives to `docs/getting-started.rst` code example (required for SC-005; validates US1 example)
- [ ] T031 Verify round-trip example in `docs/api/model.rst` is marked as doctest-able (required for SC-005; validates US2 example)
- [ ] T032 Document in `docs/api/element.rst` which examples are doctest-validated vs. review-validated per clarification (cross-phase validation)

**Completion Test**:
- `make doctest` passes on Getting Started + round-trip examples
- All three Advanced API pages visible in sidebar under "Advanced / API Reference"
- Each Advanced page includes "New to this topic?" note with working links
- `make clean html` zero warnings

**Independent Success Criterion**: SC-005 (code examples validated) + FR-005 (complete API reference with hybrid approach)

---

### Phase 6: Cross-Cutting & Verification

Final integration and validation.

- [ ] T033 [P] Extract all public APIs from `src/pyArchimate/` (modules, classes, functions) and cross-check against documented APIs in `docs/` (generated by autodoc + manual pages); report any gaps (SC-003 verification)
- [ ] T034 [P] Verify all 15 doc files created/modified match plan.md file list
- [ ] T035 [P] Run `make clean html 2>&1 | grep -E "WARNING|ERROR|error" | grep -v "duplicate.*pyarchimate"` → zero output
- [ ] T036 [P] Verify all broken `:doc:` refs from original branch are now resolved
- [ ] T037 Run full Sphinx build: `make clean html` completes in <60s
- [ ] T038 Spot-check cross-references: follow 5 "See Also" links + 3 "New to this topic?" links → all resolve
- [ ] T039 Accessibility check: Verify WCAG 2.1 Level AA compliance via RTD theme defaults (SC-008)
- [ ] T040 Search test: Verify Sphinx search index includes concepts + API names (SC-006)

**Completion Test**: 
- `make clean html` exits with code 0, zero warning/error output
- HTML site renders in browser; all three tiers visible in sidebar with correct labels
- No broken links (verified via Sphinx warnings)
- Search functionality works for concepts + API terms

---

### Phase 7: PlantUML Diagram Audit & Regeneration

Update all architecture PlantUML diagrams to reflect current pyArchimate library state.

- [ ] T041 [P] Audit `docs/diagrams/context.puml` and `c4_context.puml` against current integration points; verify system boundaries match actual readers/writers/external tools
- [ ] T042 [P] Audit `docs/diagrams/package.puml` and `c4_container.puml` against current module structure; verify package hierarchy (pyArchimate, readers, writers, helpers, model) is accurate
- [ ] T043 [P] Audit `docs/diagrams/component.puml` and `c4_component.puml` against current public API; verify Element, Relationship, Model, View classes and their interfaces are correctly represented
- [ ] T044 [P] Audit `docs/diagrams/class.puml` against current source; verify class relationships, inheritance, and method signatures match `src/pyArchimate/`
- [ ] T045 [P] Audit `docs/diagrams/deployment.puml` and `c4_deployment.puml` against current deployment model (Read the Docs, RTD theme, Python 3.10+); update if infrastructure changes
- [ ] T046 [P] Audit remaining diagrams (`object.puml`, `composite.puml`, `state.puml`, `sequence.puml`, `activity.puml`, `communication.puml`) for relevance to current library; mark deprecated if no longer used
- [ ] T047 [P] Update all `.puml` source files with current architecture; commit changes
- [ ] T048 Run `scripts/render_diagrams.sh` to regenerate all `.png` files from updated `.puml` sources
- [ ] T049 Verify all `.png` files regenerated successfully (check file timestamps + visual inspection of key diagrams)
- [ ] T050 Verify `docs/_build/html/architecture.html` displays diagrams correctly with correct image paths post-build

**Completion Test**:
- All 15 `.puml` files reviewed and updated for accuracy
- All 15 corresponding `.png` files regenerated with recent timestamps
- `docs/_build/html/diagrams/` directory contains all PNG files
- `docs/architecture.rst` includes diagrams via image directives; images display in built HTML
- PlantUML diagrams in docs website match current source code structure

**Dependency**: Requires T013–T015 (architecture.rst creation) to be complete so diagrams are included in final build.

**Independent Success Criterion**: SC-004 (package structure documented) — diagrams visually represent the package structure and relationships.

---

## Requirements Traceability Matrix

| Requirement | Type | Tasks | User Story | Success Criteria |
|-------------|------|-------|-----------|-----------------|
| FR-001 | Functional | T005, T010, T011, T015, T016, T020, T027 | US1, US2, US3 | SC-002 |
| FR-002 | Functional | T008, T010, T012 | US1 | SC-001 |
| FR-003 | Functional | T013, T015 | US2 | SC-004 |
| FR-004 | Functional | T014, T016 | US2 | SC-003 |
| FR-005 | Functional | T017–T032 | US2, US3 | SC-003, SC-005 |
| FR-006 | Functional | T009, T011, T024, T025 | US1, US2 | SC-003 |
| FR-007 | Functional | T005, T006, T040 | US1, US2, US3 | SC-006 |
| FR-008 | Functional | T005, T013, T014 | US1, US2 | SC-004 |
| FR-009 | Functional | T021, T022, T030, T031, T032 | US2, US3 | SC-005 |
| SC-001 | Success | T008, T010, T012 | US1 | Test: 2-min Getting Started runnable |
| SC-002 | Success | T005, T010, T011, T015, T016, T020, T027, T038 | US1, US2, US3 | Test: Sidebar shows 3 labeled sections |
| SC-003 | Success | T017–T032, T033 | US2, US3 | Test: Every API has signature + example (verified by T033) |
| SC-004 | Success | T013, T015, T024, T025 | US2 | Test: Package structure matches source |
| SC-005 | Success | T030, T031, T032 | US3 | Test: `make doctest` passes |
| SC-006 | Success | T040 | US3 | Test: Search finds concepts + APIs |
| SC-007 | Success | T035, T038 | All | Test: Zero broken ref warnings |
| SC-008 | Success | T039 | All | Test: WCAG 2.1 Level AA compliance |

---

## Dependency Graph

```
Phase 1: T001 → T002 → T003 → T004
         ↓
Phase 2: T005 (blocks all other page tasks)
         ↓ T006, T007 [P]
         ↓
Phase 3: T008–T012 [P] (can run in parallel; no inter-deps)
         ↓
Phase 4: T013–T025 [P] (T024–T025 depend on T024, but mostly parallel)
         ↓
Phase 5: T026–T032 [P] (T028–T029 depend on T026 existing, others independent)
         ↓
Phase 6: T033–T039 [P] (verification; some require all prior tasks complete)
```

**Critical path**: T001 → T004 → T005 → {T008–T012 || T013–T025 || T026–T032} → T033–T039

**Parallelizable tasks by story** (after Phase 2):
- **US1 (Phase 3)**: T008, T009, T010, T011, T012 can run in parallel (no file dependencies)
- **US2 (Phase 4)**: T013, T014, T017–T023 can run mostly in parallel; T024–T025 should complete last
- **US3 (Phase 5)**: T026, T027, T028, T029 can run in parallel; T030–T032 should complete last

---

## Parallel Execution Examples

### Minimal MVP (US1 Only)
1. Run Phase 1 (T001–T004) sequentially
2. Run Phase 2 (T005–T007) sequentially
3. Run Phase 3 (T008–T012) in parallel
4. Run T033–T039 for final verification

**Time estimate**: ~2–3 hours (setup + 6 file writes + verification)

### Full Feature (US1 → US2 → US3)
1. Phase 1–2 sequentially
2. Phase 3 in parallel (4 tasks)
3. Phase 4 in parallel (13 tasks grouped: architecture + guides + examples)
4. Phase 5 in parallel (7 tasks grouped: API + notes + doctest)
5. Phase 6 in parallel (7 tasks)

**Time estimate**: ~5–6 hours (setup + 14 new files + 3 modified files + verification)

---

## Implementation Strategy

### MVP Scope (Recommended for Initial Merge)

Focus on **US1 (Basic Usage)** to unblock new user onboarding:

- Deliver: T001–T012 (setup + index structure + getting-started + concepts + tutorial wiring)
- Not delivered: US2 & US3 (intermediate/advanced deferred to follow-up feature)
- Rationale: Get the "Getting Started" experience live fast; architecture/API docs can follow
- Risk: If deferred too long, incomplete experience; recommend US2 in immediate follow-up PR

### Full Feature Scope

Deliver all three user stories (T001–T039) in a single PR:

- Rationale: Dependencies tightly coupled; delivering US1-only leaves broken cross-refs (api/ pages link to guides/ that don't exist)
- Risk: Larger PR; may require split across two PRs if review is slow
- Recommendation: Full feature in one branch is cleanest; merge when complete

---

## Test Plan (Optional - Requested via Clarification Q2)

**Phase 3 Testing (US1)**:
- Unit test: Copy code from `getting-started.rst`, run it in isolation → Model created, exported successfully
- Integration test: Follow tutorial.md sections 1–10 → all examples runnable

**Phase 4 Testing (US2)**:
- Integration test: Follow Extending guide, create custom reader/writer → integrated into Model correctly
- Round-trip test: Import/export models with hierarchy + styles → properties preserved exactly

**Phase 5 Testing (US3)**:
- Doctest: `make doctest` on getting-started + round-trip examples → all pass
- Accessibility audit: Browser WCAG 2.1 validator on RTD site → Level AA passed

**All Phases**:
- Sphinx build: `make clean html` → exit 0, zero warnings
- Link check: `sphinx-build -W -b linkcheck docs docs/_build/linkcheck` → zero broken refs

---

## Task Count Summary

- **Phase 1** (Setup): 4 tasks
- **Phase 2** (Foundational): 3 tasks
- **Phase 3** (US1): 5 tasks
- **Phase 4** (US2): 13 tasks
- **Phase 5** (US3): 7 tasks
- **Phase 6** (Verification): 8 tasks (includes new T033 for SC-003 verification)
- **Phase 7** (PlantUML Diagrams): 10 tasks (diagram audit + regeneration)

**Total**: 50 tasks (15 file creations/modifications in docs/, 10 diagram updates, 25 verification/integration tasks)

**Parallelizable**: 31 tasks (marked with `[P]` — includes 9 audit tasks in Phase 7)

**Estimated effort**: 6–7 hours for full feature including diagrams; 2–3 hours for MVP (US1 docs only)