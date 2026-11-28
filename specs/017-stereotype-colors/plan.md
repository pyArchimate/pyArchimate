# Implementation Plan: Stereotype-Based Color Coding

**Branch**: `017-stereotype-colors` | **Date**: 2026-11-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/017-stereotype-colors/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add an optional `fill_color` attribute to `Profile` (stereotype), so elements that carry a stereotype render in that color by default. An element's own explicit fill color still wins when set. The color must persist through both the Archi-native (`.archimate`) and Open Group Exchange XML formats. Separately, make the existing `«stereotype»` SVG label render automatically, by default, whenever a stereotype's name is non-standard (differs case-insensitively from its concept type's default label — the `ArchiType` enum value itself), instead of requiring the existing `show_stereotypes=True` export flag for every stereotype or none.

## Technical Context

**Language/Version**: Python 3.11+ (project `requires-python = ">=3.11,<3.15"`; ruff targets 3.12)

**Primary Dependencies**: lxml (XML I/O for `.archimate` and Open Group Exchange formats), stdlib `xml.etree.ElementTree` (SVG export), existing pyArchimate model (`src/pyArchimate/`) — no new third-party dependency required

**Storage**: File I/O only — `.archimate` archives (zip+XML) and standalone Open Group Exchange XML files; no database

**Testing**: pytest (unit + integration, including round-trip fidelity tests), behave (BDD acceptance scenarios)

**Target Platform**: Cross-platform Python library (Linux/macOS/Windows), consumed as an installed package or via CLI tooling built on it

**Project Type**: Library (single project; no frontend/backend split)

**Performance Goals**: Resolving an element's effective fill color and stereotype-label visibility must be O(1) relative to model size per element (a dict lookup plus a handful of attribute reads) — consistent with the project's existing per-element styling and SVG export performance

**Constraints**: Must not change behavior for any model file created before this feature existed (Constitution VIII, Durability & Interoperability); must not alter Relationship rendering/behavior in any way (out of scope per spec FR-012); must not remove or weaken the existing explicit "always show stereotype labels" export flag (spec FR-018, Assumptions)

**Scale/Scope**: Touches `Profile` (new attribute), `Element`/`Node` color resolution, the Archi-native writer/reader, the Open Group Exchange writer/reader (new: profiles are not currently persisted in this format at all — see research.md), and the SVG exporter's stereotype-label logic. No other subsystem (layout, routing, checker rules) is affected.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Applicability | Assessment |
|-----------|----------------|------------|
| I. Code Quality | Yes | New logic is a small, self-contained color/label resolution function per entity; no magic numbers; reuses existing `_normalize_color` validation rather than duplicating it. |
| II. Testing Standards | Yes | Unit tests for `Profile.fill_color` validation and the resolution precedence (element > stereotype > none); integration round-trip tests for both file formats; behave scenarios mapped 1:1 to the spec's 4 user stories. |
| III. UX Consistency | Yes | Reuses the existing color value format (hex/named) and existing `set_fill_color`/`get_fill_color` getter/setter idiom; error messages for invalid stereotype colors reuse the existing `_normalize_color` `ValueError` message format. |
| IV. Performance | Yes | Resolution is O(1) per element (direct attribute/dict lookups); no new I/O or loops over the full model per element. |
| V. Security | N/A | No new user input surface beyond an existing validated color string API; no secrets, network, or filesystem paths involved. |
| VI. State Management | Yes | `Profile.fill_color` has a simple two-state lifecycle (unset/configured) with no intermediate states; element stereotype reassignment already has defined semantics (spec FR-008) that this feature follows without inventing new transition rules. |
| VII. System Integrity & Accuracy | Yes | Resolution precedence is deterministic and specified exactly (FR-004–FR-006, FR-015–FR-017); round-trip tests (SC-003) make the persistence behavior verifiable. |
| VIII. Durability & Interoperability | Yes — key gate | The Open Group Exchange format currently has **no** profile/stereotype persistence at all (see research.md). This feature must introduce one without breaking existing Exchange XML round-trips for files that don't use stereotypes; migration path: new optional elements only, ignored by readers that don't recognize them, consistent with the format's extension model. |
| IX. Cross-Platform Consistency | N/A | Pure library logic; no platform-specific rendering or OS-dependent behavior introduced. |

**Initial gate result**: PASS, with one flagged research item (Exchange XML has no existing profile persistence mechanism to extend — Phase 0 must decide how to add one) rather than a constitution violation.

## Project Structure

### Documentation (this feature)

```text
specs/017-stereotype-colors/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── public-api.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/pyArchimate/
├── view/
│   └── __init__.py              # Profile class (+ new fill_color attribute);
│                                 # Node.fill_color resolution chain updated
├── element.py                   # Element.get_fill_color/set_fill_color (existing,
│                                 # consulted by the new resolution chain); profile_name
│                                 # / profile_id (existing); new helper to fetch the
│                                 # Profile object itself, not just its name/id
├── model.py                     # Model.add_profile / get_profile (existing; color
│                                 # passed through on creation/update)
├── enums.py                     # ArchiType (existing; its string values ARE the
│                                 # concept "default label" used for the non-standard
│                                 # stereotype comparison — no new lookup table needed)
├── writers/
│   ├── archiWriter.py            # Serialize Profile.fill_color into the existing
│                                 # <profile> element (Archi-native format)
│   └── archimateWriter.py        # NEW: serialize Profile (name/concept/fill_color)
│                                 # into Open Group Exchange XML — currently absent
├── readers/
│   ├── archiReader.py            # Deserialize Profile.fill_color from <profile>
│   ├── _archireader_helpers.py   # (if color restoration needs a shared helper)
│   └── archimateReader.py        # NEW: deserialize Profile from Open Group
│                                 # Exchange XML — currently absent
└── view/layout/export/
    └── svg_export.py             # _maybe_render_stereotype: compare stereotype name
                                 # to concept's ArchiType value (case-insensitively)
                                 # instead of only checking show_stereotypes

tests/
├── unit/                        # Profile.fill_color validation; resolution precedence;
│                                 # non-standard stereotype name comparison
├── integration/                 # Round-trip tests: both file formats, with and
│                                 # without stereotype colors, pre-existing files
└── features/                    # BDD scenarios for the spec's 4 user stories
```

**Structure Decision**: Single-project library layout (already established by the repository). No new top-level directories. Changes are additive to existing modules (`view/__init__.py`, `element.py`, `model.py`, the two writer/reader pairs, and the SVG exporter); the one new piece of surface area is Open Group Exchange XML profile support, which did not exist before this feature and is scoped narrowly to profiles (name, concept, color) rather than a general extension mechanism.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations identified. The only notable complexity — adding profile persistence to the Open Group Exchange writer/reader where none existed — is required directly by spec FR-010 and is not a deviation from a simpler alternative; it is scoped to the minimum needed (profile name, concept type, and the new color) rather than building a general-purpose extension framework.
