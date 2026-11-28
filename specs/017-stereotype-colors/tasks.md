---

description: "Task list for Stereotype-Based Color Coding"
---

# Tasks: Stereotype-Based Color Coding

**Input**: Design documents from `/specs/017-stereotype-colors/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/public-api.md, quickstart.md (all present)

**Tests**: Included — the project constitution's Testing Standards principle (Red-Green-Refactor, non-negotiable) and plan.md's Constitution Check commit to unit, integration round-trip, and behave coverage mapped 1:1 to the spec's 4 user stories.

**Organization**: Tasks are grouped by user story (from spec.md: US1–US4, priorities P1–P4) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- File paths are exact, per plan.md's Project Structure

## Requirements Traceability Matrix

| Requirement ID | Task IDs | User Story | Success Criteria |
|---|---|---|---|
| FR-001–003 | T002, T006, T007 | US1 | SC-001 |
| FR-004 | T009, T013 | US1 / US2 | SC-001, SC-004 |
| FR-005, FR-006 | T008, T009 | US1 | SC-001, SC-002 |
| FR-007 | T008 | US1 | SC-001 |
| FR-008 | T014 | US2 | SC-004 |
| FR-009 | T016, T017, T020 | US3 | SC-003 |
| FR-010 | T018, T019, T021, T022 | US3 | SC-003 |
| FR-011 | T010, T011 | US1 | SC-002 |
| FR-012 | T029 | — | — |
| FR-013 | T030 | — | — |
| FR-014 | T017, T019, T023 | US3 | SC-005 |
| FR-015–018 | T025, T026, T027 | US4 | SC-006 |

## Phase 1: Setup

**Purpose**: Confirm a clean baseline before any change.

- [X] T001 Run `poetry install`, then `poetry run pytest tests/unit tests/integration -q && poetry run behave tests/features` from the repository root, and confirm everything passes before making any change (establishes the pre-feature baseline for the regression check in T033).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Stub the new call sites that every user story needs, satisfying Constitution II's Red-Green-Refactor requirement by giving each story a real signature to write a failing test against before implementing.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 [P] Stub a `fill_color` attribute on `Profile` in `src/pyArchimate/view/__init__.py`: getter returns `None`; setter is a placeholder that does not yet validate or store anything.
- [X] T003 [P] Stub an internal helper on `Element` in `src/pyArchimate/element.py` that is meant to return the assigned `Profile` object, currently always returning `None` (plan.md Project Structure note).
- [X] T004 Stub `Node.get_effective_fill_color()` in `src/pyArchimate/view/__init__.py`, returning `None` unconditionally. Depends on: T002, T003.
- [X] T005 Stub the fill-color lookups in `src/pyArchimate/view/layout/export/svg_export.py` (~lines 569, 727, 745) to call `node.get_effective_fill_color()`, which currently always falls back to `default_color(elem_type, theme)` since the stub returns `None`. Depends on: T004.

**Checkpoint**: Real call sites exist everywhere the user stories need them. Each story can now write a failing test against the actual signature before implementing its behavior.

---

## Phase 3: User Story 1 - Define a default color per stereotype (Priority: P1) 🎯 MVP

**Goal**: Configuring a color on a stereotype makes every element carrying that stereotype render in that color automatically, with no per-element styling.

**Independent Test**: Configure a color on a stereotype, assign it to several elements that have no color of their own, confirm all render in the configured color; clear the stereotype's color, confirm they revert to no fill color.

- [X] T006 [P] [US1] Write unit test: `Profile.fill_color` accepts a 6-digit hex code and a case-insensitive named color, normalizes both, rejects any other value with `ValueError`, and can be cleared back to `None`, in `tests/unit/test_profile_fill_color.py` (FR-001–FR-003). Confirm it FAILS against the T002 stub.
- [X] T007 [US1] Implement `Profile.fill_color`'s setter via the existing `_normalize_color()` helper from `src/pyArchimate/element.py` — the same function `Element.set_fill_color()` already uses (research.md Decision 4). Confirm T006 passes. Depends on: T002, T006.
- [X] T008 [P] [US1] Write unit test: `Node.get_effective_fill_color()` resolves to the assigned stereotype's color when unset elsewhere, applies to multiple elements sharing the stereotype, reflects a **changed** stereotype color (e.g. `"#E8453C"` → `"#F2A900"`) for all of them without touching the elements individually (FR-007), and reverts to `None` once the stereotype's color is cleared (US1 Acceptance Scenarios 1–3); also assert the full precedence order by covering the two remaining branches: `Node.fill_color`, when set, wins over both the element's own `get_fill_color()` and any stereotype color, and `Element.get_fill_color()`, when set and `Node.fill_color` is unset, wins over a stereotype color (FR-004) — in `tests/unit/test_effective_fill_color.py`. Confirm it FAILS against the T004 stub.
- [X] T009 [US1] Implement `Node.get_effective_fill_color()`'s full 4-step resolution from research.md Decision 1 (`Node.fill_color` → `Element.get_fill_color()` → assigned `Profile.fill_color` → `None`) — all four branches. Confirm T008 passes (T008 now covers all four branches). Depends on: T004, T007, T008.
- [X] T010 [US1] Replace the T005 stub wiring in `src/pyArchimate/view/layout/export/svg_export.py` so it uses the now-complete T009 logic. Depends on: T005, T009.
- [X] T011 [US1] Integration test: `view.to_svg()` renders elements carrying a colored stereotype (with no explicit color of their own) using that color in the output SVG, in `tests/integration/test_stereotype_color_svg.py` (FR-011, SC-002). Depends on: T010.
- [X] T012 [US1] BDD scenario "Define a default color per stereotype", mapped 1:1 to US1's acceptance scenarios, in `tests/features/stereotype_color.feature` plus its step definitions.

**Checkpoint**: User Story 1 is fully functional and independently testable — this is the MVP.

---

## Phase 4: User Story 2 - Override a stereotyped element's color individually (Priority: P2)

**Goal**: An element's own explicit fill color always wins over its stereotype's configured color.

**Independent Test**: Give an element its own explicit color while it carries a stereotype with a different configured color; confirm the element keeps its own color; clear the explicit color; confirm it falls back to the stereotype's color.

- [X] T013 [P] [US2] Write unit test: `Node.get_effective_fill_color()` returns the element's own explicit color (set via `Element.set_fill_color()`) even when its stereotype has a different configured color, and falls back to the stereotype's color once the explicit color is cleared, in `tests/unit/test_effective_fill_color.py` (US2 Acceptance Scenarios 1–2). This validates the explicit-override branches of T009's already-complete implementation.
- [X] T014 [P] [US2] Write unit test: reassigning an element with no explicit color from one colored stereotype to a different colored stereotype updates its resolved effective color to the newly assigned stereotype's color, in `tests/unit/test_effective_fill_color.py` (FR-008, US2 Acceptance Scenario 3).
- [X] T015 [US2] BDD scenario "Override a stereotyped element's color individually", mapped 1:1 to US2's acceptance scenarios, in `tests/features/stereotype_color.feature` plus its step definitions.

**Checkpoint**: User Stories 1 and 2 both work independently — override precedence is verified on top of the Foundational resolution chain.

---

## Phase 5: User Story 3 - Stereotype colors survive save and reload (Priority: P3)

**Goal**: A stereotype's configured color persists through a full save/reload round trip in both supported file formats.

**Independent Test**: Configure stereotype colors, save to each supported format, reload, and confirm the colors and their effect on rendering are unchanged; load a model file created before this feature existed and confirm it loads without error with every stereotype's color unset.

- [X] T016 [P] [US3] Serialize `Profile.fill_color` as a new `fillColor` attribute on the existing `<profile name= id= conceptType=>` element in `src/pyArchimate/writers/archiWriter.py` (data-model.md Persistence mapping — Archi-native). Depends on: T007.
- [X] T017 [P] [US3] Deserialize the `fillColor` attribute back into `Profile.fill_color` when reading `<profile>` elements in `src/pyArchimate/readers/archiReader.py` (~lines 84–89), treating its absence as `None` (FR-014). Depends on: T007.
- [X] T018 [P] [US3] Register `profileId`, `profile`, and `profileColor` as new element-level property definitions, and write all three for each element with an assigned profile, in `src/pyArchimate/writers/archimateWriter.py`, following the existing `_write_elem_viewpoints`/`_write_elem_visual_style` pattern (research.md Decision 2). Depends on: T007.
- [X] T019 [US3] Deserialize the `profileId`/`profile`/`profileColor` element properties in `src/pyArchimate/readers/archimateReader.py`, reconstructing `Profile` objects keyed by `profileId` — **not** by name, per the 2026-11-28 clarification in spec.md, since two distinct stereotypes can share a name while specializing different concept types — inferring each profile's `concept` from the first referencing element's `ArchiType`. Depends on: T018.
- [X] T020 [P] [US3] Integration test: round-trip a model with configured stereotype colors through the Archi-native (`.archimate`) format and confirm every color is unchanged after reload, in `tests/integration/test_profile_color_roundtrip.py` (SC-003). Depends on: T016, T017.
- [X] T021 [P] [US3] Integration test: round-trip the same model through the Open Group Exchange XML format and confirm every color is unchanged after reload, in `tests/integration/test_profile_color_roundtrip.py` (SC-003). Depends on: T018, T019.
- [X] T022 [US3] Integration test: two distinct stereotypes that share the same name but specialize different concept types, each with its own configured color, round-trip through the Exchange XML format without either color being merged or lost, in `tests/integration/test_profile_color_roundtrip.py` (2026-11-28 clarification). Depends on: T018, T019.
- [X] T023 [US3] Integration test: an existing fixture file from `tests/integration` created before this feature existed (a) still loads without error via both readers, with every profile's `fill_color` reading `None`, and (b) produces byte-identical SVG output via `view.to_svg()` before and after this feature's changes (SC-005, FR-014). Depends on: T017, T019.
- [X] T024 [US3] BDD scenario "Stereotype colors survive save and reload", mapped 1:1 to US3's acceptance scenarios, in `tests/features/stereotype_color.feature` plus its step definitions.

**Checkpoint**: User Stories 1–3 all work independently — colors configure, override correctly, and persist through both formats, with pre-existing files unaffected.

---

## Phase 6: User Story 4 - Automatically label non-standard stereotypes (Priority: P4)

**Goal**: An element's `«stereotype»` label is rendered automatically, by default, whenever its stereotype's name is non-standard — with no display option required.

**Independent Test**: Export a view with no special display option set, containing one element with a custom (non-standard-named) stereotype and one element with no stereotype, and confirm only the custom-stereotyped element shows a label.

- [X] T025 [US4] Update `_maybe_render_stereotype`/`_render_stereotype` in `src/pyArchimate/view/layout/export/svg_export.py` (~lines 763–784) to render the `«stereotype»` label by default whenever the assigned profile's name, lowercased, differs from the element's `ArchiType` value, lowercased (FR-015–FR-017, research.md Decision 3), while leaving the existing `show_stereotypes=True` force-show-everything behavior unchanged (FR-018).
- [X] T026 [P] [US4] Unit test: the non-standard-stereotype comparison is case-insensitive and correctly classifies a stereotype as standard or non-standard against its concept's `ArchiType` value, in `tests/unit/test_stereotype_label.py`. Depends on: T025.
- [X] T027 [P] [US4] Integration test: `view.to_svg()` with default options renders a `«stereotype»` label for a non-standard stereotype, no label for a standard-named one, and no label for an element with no stereotype; confirm `show_stereotypes=True` still force-renders every assigned stereotype's label regardless, in `tests/integration/test_stereotype_label_svg.py` (SC-006). Depends on: T025.
- [X] T028 [US4] BDD scenario "Automatically label non-standard stereotypes", mapped 1:1 to US4's acceptance scenarios, in `tests/features/stereotype_color.feature` plus its step definitions.

**Checkpoint**: All four user stories are independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T029 [P] Regression test: this feature's changes (T002–T025) do not alter Relationship rendering, styling, or persistence in any way — assert relationship-touching code paths in `archiWriter.py`/`archimateWriter.py`/`svg_export.py` produce unchanged output, in `tests/integration/test_relationships_unaffected.py` (FR-012).
- [X] T030 [P] Regression test: `Element.set_line_color()`/`set_line_width()`/transparency behavior and persistence are unchanged by this feature, in `tests/unit/test_visual_style_unaffected.py` (FR-013).
- [X] T031 [P] Run `poetry run ruff check .`, `poetry run pyright`, and `poetry run mypy src/pyArchimate` and fix any violations introduced by this feature's changes.
- [X] T032 [P] Execute every code block in `quickstart.md` (User Stories 1–4) end-to-end and confirm each assertion holds.
- [X] T033 Run the full regression suite — `poetry run pytest tests/unit tests/integration && poetry run behave tests/features` — and confirm zero regressions against the T001 baseline (Constitution VIII, Durability & Interoperability; SC-005).
- [X] T034 [P] Compatibility test: `apply_profile_styles(view, mapping)` (`src/pyArchimate/helpers/diagram.py`) still wins over an element's automatic stereotype color — since it sets `Node.fill_color` directly (tier 1 of research.md Decision 1) — confirming the two features compose correctly with no special-casing needed, in `tests/integration/test_apply_profile_styles_compat.py`.
- [X] T035 [P] Regression test: deleting a stereotype that elements still reference clears their stereotype assignment (existing deletion behavior) and therefore their stereotype-derived effective color, while leaving any explicit element-level color untouched, in `tests/integration/test_stereotype_deletion_edge_case.py` (spec.md Edge Cases).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (T002/T003 parallel → T004 → T005).
- **User Stories (Phase 3–6)**: All depend on Foundational completion.
  - US1 (Phase 3): depends only on Foundational; implements the complete resolution logic (T009) and SVG wiring (T010).
  - US2 (Phase 4): depends on US1's T009 being complete (its tests validate branches of the same function, not drive new implementation).
  - US3 (Phase 5): depends on Foundational (needs `Profile.fill_color`, T007) plus its own writer/reader tasks; independent of US1/US2 otherwise.
  - US4 (Phase 6): depends only on Foundational being complete as a phase gate; its implementation (T025) is otherwise independent of T002–T010's color mechanism.
- **Polish (Phase 7)**: Depends on all four user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories — the MVP.
- **US2 (P2)**: Depends on US1's T009 (the resolution function) existing and being complete; independently testable once it does.
- **US3 (P3)**: No functional dependency on US1/US2 beyond `Profile.fill_color` existing (T007) — persists whatever it already holds; independently testable.
- **US4 (P4)**: Fully independent of US1–US3 (labeling logic touches different code than color resolution); independently testable.

### Within Each User Story

- Every behavior-adding task is preceded by a test written against a real (stubbed or already-implemented) signature, confirmed to fail before the implementation task that follows it — satisfying Constitution II's Red-Green-Refactor requirement.
- Implementation precedes integration tests within each story's phase.

### Parallel Opportunities

- T002 and T003 (different files: `view/__init__.py` vs `element.py`) can run in parallel.
- T006 and T008 (different test files) can run in parallel once their respective stubs exist.
- T013 and T014 (same test file but independent test cases) can run in parallel.
- T016/T017 (Archi-native writer/reader) and T018 (Exchange XML writer) can all start in parallel once T007 is done; T019 depends on T018.
- T020 and T021 (different format round-trips, same test file but independent test functions) can run in parallel once their respective writer/reader pairs are done.
- T026 and T027 (different test files) can run in parallel once T025 is done.
- T029, T030, T031, T032 (independent checks) can run in parallel.
- Once Phase 2 (Foundational) is complete, US3 and US4 can be worked on in parallel with US1/US2 by different contributors; US2 should start only after US1's T009 lands.

---

## Parallel Example: Foundational Phase

```bash
# T002 and T003 touch different files and have no dependency on each other:
Task: "Stub fill_color attribute on Profile in src/pyArchimate/view/__init__.py"
Task: "Stub Profile-fetch helper on Element in src/pyArchimate/element.py"
```

## Parallel Example: User Story 3

```bash
# T016/T017 (Archi-native) and T018 (Exchange XML writer) are independent of each other:
Task: "Serialize Profile.fill_color as fillColor attribute in src/pyArchimate/writers/archiWriter.py"
Task: "Deserialize fillColor attribute in src/pyArchimate/readers/archiReader.py"
Task: "Register and write profileId/profile/profileColor properties in src/pyArchimate/writers/archimateWriter.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (T002–T005) — stubs every call site.
3. Complete Phase 3: User Story 1 (T006–T012) — builds the real resolution logic test-first and wires SVG export.
4. **STOP and VALIDATE**: Confirm US1's three acceptance scenarios hold.

### Incremental Delivery

1. Setup + Foundational → stubs in place.
2. Add User Story 1 → resolution logic built and tested → MVP demo-able.
3. Add User Story 2 → validate override behavior → demo.
4. Add User Story 3 → validate both-format persistence → demo.
5. Add User Story 4 → validate automatic labeling → demo.
6. Polish (Phase 7) → full regression confirmed, including the FR-012/FR-013 non-regression guards.

### Parallel Team Strategy

With multiple contributors, once Phase 2 (Foundational) is merged:
- Contributor A: User Story 1 (builds the core resolution logic — do this first).
- Contributor B: User Story 3 (writer/reader changes for both formats — largest task count, no dependency on US1's internals).
- Contributor C: User Story 4 (independent labeling logic in `svg_export.py`).
- User Story 2 should start once Contributor A's T009 lands.
