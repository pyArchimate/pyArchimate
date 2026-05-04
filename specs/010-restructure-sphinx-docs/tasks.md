# Implementation Tasks: Restructure Sphinx Documentation

**Feature**: 010-restructure-sphinx-docs  
**Branch**: `010-restructure-sphinx-docs`  
**Date**: 2026-05-04 (updated from 2026-05-03)  

---

## Task Breakdown

### Phase 1: Setup & Dependencies

Enable Markdown support in Sphinx (blocking all other work).

- [x] T001 Add `myst-parser` to `docs/requirements.txt`
- [x] T002 Add `myst-parser` to `[dependency-groups] docs` in `pyproject.toml`
- [x] T003 Update `docs/conf.py`: add `myst_parser` to extensions list
- [x] T004 Update `docs/conf.py`: add `source_suffix` mapping for `.rst` and `.md` files
- [x] T051 Add `pa11y` to `[dependency-groups] docs` in `pyproject.toml` (required for SC-008 WCAG verification)
- [x] T052 Configure `sphinx.ext.doctest` in `docs/conf.py`: add to extensions list + add `doctest_global_setup = "from pyArchimate import Model, Element, View, Relationship"` (required for SC-005 / FR-009)

**Completion Test**: `poetry run make html` succeeds; `poetry run python -c "import myst_parser"` passes; `poetry run make doctest` runs without configuration error

---

### Phase 2: Foundational Navigation Structure

Rebuild the documentation index to support three-tier navigation (blocking all page creation).

- [x] T005 Rewrite `docs/index.rst`: create three `toctree` sections (Basic Usage, Intermediate / Architecture, Advanced / API Reference)
- [x] T006 [P] Create `docs/hierarchy-styling-overview.rst` stub (one-page redirect to hierarchy, styling, and junction guides)
- [x] T007 [P] Verify all three toctree sections reference valid pages (no forward-reference errors in next phase)

**Completion Test**: `make clean html` produces zero `document isn't included in any toctree` warnings; sidebar displays three labeled sections

---

### Phase 3: User Story 1 — Basic Usage (P1 - New User Learns Basic Concepts)

Goal: Users can start with pyArchimate in under 2 minutes (SC-001).

#### 3.1 Basic Landing Pages

- [x] T008 [P] [US1] Create `docs/getting-started.rst`: Installation (1-liner) + Minimal Working Example (15-line code block from tutorial.md §2-3) + What's Next links
- [x] T009 [P] [US1] Create `docs/concepts.rst`: The Three Layers table + Elements (ArchiType + shim note) + Relationships (type table) + Views/Diagrams + Viewpoints (brief) + Properties
- [x] T010 [P] [US1] Add tier label (`.. note::`) to `docs/getting-started.rst` top: "ℹ️ **Basic Usage**"
- [x] T011 [P] [US1] Add tier label (`.. note::`) to `docs/concepts.rst` top: "ℹ️ **Basic Usage**"

#### 3.2 Wire Tutorial into Sphinx

- [x] T012 [US1] Verify `docs/tutorial/tutorial.md` is discoverable by Sphinx (no edits needed; `myst-parser` + `source_suffix` handle it)

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

- [x] T013 [P] [US2] Create `docs/architecture.rst`: Package Structure table (module → responsibility) + Layered Dependencies prose + `.. include:: diagrams.rst` + Extension Points section
- [x] T014 [P] [US2] Create `docs/guides/extending.rst`: Custom Readers (registry pattern) + Custom Writers (enum pattern) + Custom Properties/Profiles + Logging Integration + Import Shim notes
- [x] T015 [P] [US2] Add tier label (`.. note::`) to `docs/architecture.rst` top: "🔧 **Intermediate / Architecture**"
- [x] T016 [P] [US2] Add tier label (`.. note::`) to `docs/guides/extending.rst` top: "🔧 **Intermediate / Architecture**"

#### 4.2 Recreate Deleted Guides (fix broken refs from api/*.rst)

- [x] T017 [P] [US2] Create `docs/guides/element-hierarchy.rst`: Overview + Creating Hierarchies (add_child, max depth 5) + Querying (get_parent/children/ancestors/descendants/depth/find_by_hierarchy_path) + Removing + Round-Trip Preservation + See Also → `api/model` + `examples/hierarchy_examples`
- [x] T018 [P] [US2] Create `docs/guides/visual-styling.rst`: Color Model + Per-Element Styling (set/get fill/line/transparency) + Bulk Styling (set_visual_style dict) + Model-wide Themes (default_theme) + Round-Trip + See Also → `api/element` + `examples/styling_examples`
- [x] T019 [P] [US2] Create `docs/guides/junction-types.rst`: What Is Junction + Supported Types table (AND/OR/XOR) + Set/Get + Typical Patterns + See Also → `api/element`
- [x] T020 [P] [US2] Add tier label (`.. note::`) to each guide top: "🔧 **Intermediate / Architecture**"

#### 4.3 Recreate Deleted Examples (fix broken refs from guides/*.rst)

- [x] T021 [P] [US2] Create `docs/examples/hierarchy_examples.rst`: 4 self-contained code blocks (3-level parent-child, path wildcard, subtree walk, cycle detection); all code valid against current API
- [x] T022 [P] [US2] Create `docs/examples/styling_examples.rst`: 4 self-contained code blocks (hex + named colors, bulk set_visual_style, theme + override, round-trip verification); all code valid against current API
- [x] T023 [P] [US2] Add tier label (`.. note::`) to each example top: "🔧 **Intermediate / Architecture**"

#### 4.4 Update concepts.rst with full content

- [x] T024 [US2] Expand `docs/concepts.rst`: Add Viewpoints section listing all 13 standard viewpoints (slug, name, description); cross-ref to `api/viewpoints`
- [x] T025 [US2] Verify all concept definitions use canonical terminology from spec clarifications
- [x] T053 [P] [US2] Audit existing `docs/api/*.rst` pages for FR-008 compliance: verify each page groups content by module/capability (not raw filename); reorganize any page that lists functions by file rather than purpose

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

- [x] T026 [P] [US3] Create `docs/api/viewpoints.rst`: Overview (get_viewpoints, get_elements_by_viewpoint, assign_viewpoint, remove_viewpoint) + Standard Viewpoints table (13 slugs + names + descriptions from viewpoint_registry.py) + Code Example + `.. automodule::` for pyArchimate.viewpoint + pyArchimate.viewpoint_registry
- [x] T027 [P] [US3] Add tier label (`.. note::`) to `docs/api/viewpoints.rst` top: "⚙️ **Advanced / API Reference**" with "New to this topic?" link to `guides/extending`

#### 5.2 Add "New to this topic?" notes to existing Advanced API pages

- [x] T028 [P] [US3] Add "New to this topic?" note at top of `docs/api/element.rst` linking to `guides/visual-styling` and `guides/junction-types`
- [x] T029 [P] [US3] Add "New to this topic?" note at top of `docs/api/model.rst` linking to `guides/element-hierarchy`

#### 5.3 Verify API examples & doctest setup (cross-phase)

*Note: T030–T032 are validation tasks for code examples created in US1 and US2. Grouped here in Phase 5 for dependency ordering (doctest setup requires all example pages to exist), but not labeled with [US#] to indicate cross-story scope.*

- [x] T030 Add Sphinx doctest directives to `docs/getting-started.rst` code example (required for SC-005; validates US1 example; depends on T052)
- [x] T031 Verify round-trip example in `docs/api/model.rst` is marked as doctest-able (required for SC-005; validates US2 example; depends on T052)
- [x] T032 Document in `docs/api/element.rst` which examples are doctest-validated vs. review-validated per clarification (cross-phase validation)
- [x] T054 [P] [US3] Scan `src/pyArchimate/` for public APIs raising `DeprecationWarning`; add `.. deprecated::` directive with deprecation version and recommended replacement to each corresponding page in `docs/api/` (FR-010, SC-009)

**Completion Test**:
- `make doctest` passes on Getting Started + round-trip examples
- All three Advanced API pages visible in sidebar under "Advanced / API Reference"
- Each Advanced page includes "New to this topic?" note with working links
- `make clean html` zero warnings

**Independent Success Criterion**: SC-005 (code examples validated) + FR-005 (complete API reference with hybrid approach)

---

### Phase 6: Cross-Cutting & Verification

Final integration and validation.

- [x] T033 [P] Extract all public APIs from `src/pyArchimate/` (modules, classes, functions) and cross-check against documented APIs in `docs/` (generated by autodoc + manual pages); report any gaps (SC-003 verification)
- [x] T034 [P] Verify all 15 doc files created/modified match plan.md file list
- [x] T035 [P] Run `make clean html 2>&1 | grep -E "WARNING|ERROR|error" | grep -v "duplicate.*pyarchimate"` → zero output
- [x] T036 [P] Verify all broken `:doc:` refs from original branch are now resolved
- [x] T037 Run full Sphinx build: `make clean html` completes in <60s
- [x] T038 Spot-check cross-references: follow 5 "See Also" links + 3 "New to this topic?" links → all resolve
- [x] T039 Run `pa11y` on `docs/_build/html/index.html` and 3 key pages (getting-started, architecture, api/model); fix any WCAG 2.1 Level AA failures reported (SC-008)
- [x] T040 Search test: Verify Sphinx search index includes concepts + API names (SC-006)
- [x] T055 [P] Verify SC-009: confirm all deprecated public APIs surfaced by T054 have a visible `.. deprecated::` notice in `docs/_build/html/`; zero deprecated APIs appear without a migration note

**Completion Test**: 
- `make clean html` exits with code 0, zero warning/error output
- HTML site renders in browser; all three tiers visible in sidebar with correct labels
- No broken links (verified via Sphinx warnings)
- Search functionality works for concepts + API terms

---

### Phase 7: PlantUML Diagram Audit & Regeneration

Update all architecture PlantUML diagrams to reflect current pyArchimate library state.

- [x] T041 [P] Audit `docs/diagrams/context.puml` and `c4_context.puml` against current integration points; verify system boundaries match actual readers/writers/external tools
- [x] T042 [P] Audit `docs/diagrams/package.puml` and `c4_container.puml` against current module structure; verify package hierarchy (pyArchimate, readers, writers, helpers, model) is accurate
- [x] T043 [P] Audit `docs/diagrams/component.puml` and `c4_component.puml` against current public API; verify Element, Relationship, Model, View classes and their interfaces are correctly represented
- [x] T044 [P] Audit `docs/diagrams/class.puml` against current source; verify class relationships, inheritance, and method signatures match `src/pyArchimate/`
- [x] T045 [P] Audit `docs/diagrams/deployment.puml` and `c4_deployment.puml` against current deployment model (Read the Docs, RTD theme, Python 3.10+); update if infrastructure changes
- [x] T046 [P] Audit remaining diagrams (`object.puml`, `composite.puml`, `state.puml`, `sequence.puml`, `activity.puml`, `communication.puml`) for relevance to current library; mark deprecated if no longer used
- [x] T047 [P] Update all `.puml` source files with current architecture; commit changes
- [x] T048 Run `scripts/render_diagrams.sh` to regenerate all `.png` files from updated `.puml` sources
- [x] T049 Verify all `.png` files regenerated successfully (check file timestamps + visual inspection of key diagrams)
- [x] T050 Verify `docs/_build/html/architecture.html` displays diagrams correctly with correct image paths post-build

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
| FR-008 | Functional | T005, T013, T014, T053 | US1, US2 | SC-004 |
| FR-009 | Functional | T021, T022, T030, T031, T032, T052 | US2, US3 | SC-005 |
| FR-010 | Functional | T054, T055 | US3 | SC-009 |
| SC-001 | Success | T008, T010, T012 | US1 | Test: 2-min Getting Started runnable |
| SC-002 | Success | T005, T010, T011, T015, T016, T020, T027, T038 | US1, US2, US3 | Test: Sidebar shows 3 labeled sections |
| SC-003 | Success | T017–T032, T033 | US2, US3 | Test: Every API has signature + example (verified by T033) |
| SC-004 | Success | T013, T015, T024, T025 | US2 | Test: Package structure matches source |
| SC-005 | Success | T030, T031, T032 | US3 | Test: `make doctest` passes |
| SC-006 | Success | T040 | US3 | Test: Search finds concepts + APIs |
| SC-007 | Success | T035, T038 | All | Test: Zero broken ref warnings |
| SC-008 | Success | T039, T051 | All | Test: `pa11y` reports zero WCAG 2.1 AA failures |
| SC-009 | Success | T054, T055 | US3 | Test: Zero deprecated APIs without `.. deprecated::` notice |

---

## Dependency Graph

```
Phase 1: T001 → T002 → T003 → T004 → T051, T052 [parallel]
         ↓
Phase 2: T005 (blocks all other page tasks)
         ↓ T006, T007 [P]
         ↓
Phase 3: T008–T012 [P] (can run in parallel; no inter-deps)
         ↓
Phase 4: T013–T025, T053 [P] (T024–T025 depend on T024, but mostly parallel)
         ↓
Phase 5: T026–T032, T054 [P] (T030–T031 depend on T052; T028–T029 depend on T026)
         ↓
Phase 6: T033–T040, T055 [P] (verification; some require all prior tasks complete)
```

**Critical path**: T001 → T004 → T052 → T005 → {T008–T012 || T013–T025 || T026–T032} → T033–T040

**Parallelizable tasks by story** (after Phase 2):
- **US1 (Phase 3)**: T008, T009, T010, T011, T012 can run in parallel (no file dependencies)
- **US2 (Phase 4)**: T013, T014, T017–T023, T053 can run mostly in parallel; T024–T025 should complete last
- **US3 (Phase 5)**: T026, T027, T028, T029, T054 can run in parallel; T030–T032 should complete last

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

- **Phase 1** (Setup): 6 tasks (T001–T004, T051–T052)
- **Phase 2** (Foundational): 3 tasks
- **Phase 3** (US1): 5 tasks
- **Phase 4** (US2): 14 tasks (adds T053 FR-008 audit)
- **Phase 5** (US3): 8 tasks (adds T054 deprecated API directives)
- **Phase 6** (Verification): 9 tasks (T039 updated for pa11y; adds T055 SC-009 check)
- **Phase 7** (PlantUML Diagrams): 10 tasks (diagram audit + regeneration)

**Total**: 55 tasks (15 file creations/modifications in docs/, 10 diagram updates, 30 verification/integration/setup tasks)

**Parallelizable**: 34 tasks (marked with `[P]`)

**Estimated effort**: 6–7 hours for full feature including diagrams; 2–3 hours for MVP (US1 docs only)