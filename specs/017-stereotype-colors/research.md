# Phase 0 Research: Stereotype-Based Color Coding

## Decision 1: Effective fill color resolution precedence

**Decision**: When rendering an element (SVG export today; any future renderer going forward), resolve its effective fill color in this order:

1. `Node.fill_color` (the existing per-view explicit override — `src/pyArchimate/view/__init__.py`), if set on that specific view instance.
2. Else `Element.get_fill_color()` (the existing model-level explicit color API — `src/pyArchimate/element.py`), if set.
3. Else the element's assigned stereotype's `Profile.fill_color` (new in this feature), if the element has a profile and that profile has a color configured.
4. Else the existing type-based theme default (`default_color(elem_type, theme)` — `src/pyArchimate/view/__init__.py`), unchanged.

**Rationale**: Investigation of the current codebase found that `Node.fill_color` and `Element.get_fill_color()` are two independently-settable, independently-persisted colors with no relationship to each other today: SVG export (`svg_export.py`) reads only `Node.fill_color`, falling back to the type-based theme default when unset; `Element.get_fill_color()` is persisted (round-tripped as a custom `<property>` on the Archi-native element) but has zero production consumers today — it is write-only from a rendering perspective. Spec FR-004 frames the override as "the element's own explicit fill color," and the spec's class diagram models the explicit color on `Element`, not `Node`. Inserting the stereotype color as a new fallback step *beneath* both existing explicit-color mechanisms satisfies FR-004–FR-006 while changing the resolved color for zero existing models (satisfies SC-005 and Constitution VIII, Durability & Interoperability) — a model that has never used `Element.set_fill_color()` or a stereotype color renders exactly as it does today.

**Alternatives considered**:
- *Consult only `Node.fill_color`, treat `Element.get_fill_color()` as out of scope.* Rejected: would leave `Element.get_fill_color()`/`set_fill_color()` misleading — a caller could "set" a color on an element that still never renders in that color, undermining FR-004 as written.
- *Consult only `Element.get_fill_color()`, ignore the per-view `Node.fill_color`.* Rejected: would silently change the rendered color of every existing model that already uses per-view node coloring, a direct Constitution VIII violation.
- *Let the stereotype color override the per-view `Node.fill_color`.* Rejected: contradicts the user's confirmed precedence decision (explicit colors always win over stereotype defaults) and would surprise anyone who deliberately styled one view differently from another.

## Decision 2: Persisting stereotype color in Open Group Exchange XML

**Decision**: Open Group Exchange XML (written/read by `archimateWriter.py`/`archimateReader.py` — the `http://www.opengroup.org/xsd/archimate/3.0/` namespace) currently has **no** profile/stereotype persistence at all — confirmed by the absence of any "profile" handling in either module. Add it using the format's existing, already-exercised extension mechanism — `propertyDefinitions` at the model root plus per-element `property`/`value` — the same mechanism already used in this codebase for `viewpoint` and the per-element visual-style keys (`fillColor`, `lineColor`, `lineWidth`, `transparency`; see `_write_elem_viewpoints` / `_write_elem_visual_style` in `archimateWriter.py`). Concretely: for each element that has an assigned profile, write **three** element-level properties — `profileId` (the stereotype's UUID), `profile` (the stereotype's name, kept for human readability in the raw XML), and `profileColor` (the stereotype's configured color, if any) — registered as property definitions exactly like `viewpoint` is today. On read, reconstruct `Profile` objects keyed by `profileId` as elements are loaded (not by name — see Clarifications in `spec.md`, 2026-11-28), inferring each profile's `concept` from the type of the element that first referenced it (an element's own `ArchiType` is already known at that point).

**Rationale**: Reuses an established, already round-trip-tested mechanism rather than inventing a new one; the Exchange XML the writer produces declares a strict `xsi:schemaLocation` against the official Open Group XSD, so adding an unrecognized custom element (e.g. a bespoke `<profiles>` block mirroring the Archi-native format's non-standard `<profile>` elements) risks failing validation in external, stricter tools, whereas `property`/`propertyDefinition` are fully schema-legal constructs already used this way. This keeps the change narrowly scoped to exactly what FR-010 requires (persist stereotype name, color, and now identity) rather than building a general-purpose profile/extension framework, consistent with the project's anti-abstraction guidance and the plan's Complexity Tracking note. Keying reconstruction by `profileId` rather than `profile` (name) mirrors how the Archi-native format already keys `<profile>` elements by `id`, and is required per the 2026-11-28 clarification: `model.add_profile()` keys profiles by UUID, not name, so two distinct stereotypes can legitimately share a name while specializing different concept types — deduplicating by name alone would silently merge them and corrupt one profile's color on round-trip.

**Alternatives considered**:
- *Add a dedicated custom `<profiles>` root block*, mirroring the Archi-native writer's non-standard `<profile name= id= conceptType=>` elements. Rejected: not covered by the official Open Group XSD; risks breaking strict external validators; duplicates a mechanism (`property`/`propertyDefinition`) that already works and is already tested.
- *Encode the full profile definition as one compound string value* (e.g. `"<uuid>|Threat|Driver|#E8453C"`) in a single property. Rejected: harder to read/debug in raw XML; the concept doesn't need storing at all since it is always recoverable from the owning element's own type.
- *Deduplicate reconstructed profiles by name only* (the original Phase 0 design). Rejected per the 2026-11-28 clarification: silently merges two legitimately distinct same-named stereotypes that specialize different concept types, risking silent color corruption on round-trip.
- *Skip Exchange XML persistence, restrict FR-010 to the Archi-native format only.* Rejected: contradicts the explicit, user-confirmed requirement (FR-010, SC-003) that stereotype colors round-trip through both supported formats.

## Decision 3: Determining whether a stereotype is "non-standard"

**Decision**: Compare `Profile.name` to the owning element's `ArchiType` enum value, case-insensitively. No new lookup table is needed: `ArchiType` (`src/pyArchimate/enums.py`) is a `StrEnum` whose member values already are the canonical ArchiMate concept names (e.g. `ArchiType.Driver == "Driver"`), and `Element.type` already exposes this string. A stereotype is "non-standard" (and therefore auto-labeled per FR-016) whenever its name, lowercased, differs from the element's type string, lowercased.

**Rationale**: Confirmed directly in `enums.py`; building a separate concept-to-default-label dictionary would duplicate data that already exists and risk drifting out of sync with `ArchiType` as concepts are added or renamed.

**Alternatives considered**:
- *Maintain a separate `{ArchiType: default_label}` mapping.* Rejected: pure duplication of `ArchiType`'s own string values, with no benefit.

## Decision 4: Reusing existing color validation

**Decision**: `Profile.fill_color`'s setter validates using the existing module-level `_normalize_color()` helper (`src/pyArchimate/element.py`) — the same function already used by `Element.set_fill_color()` — rather than writing a second validator.

**Rationale**: Guarantees identical accepted formats (6-digit hex, case-insensitive named color) and identical error messages for both per-element and per-stereotype colors, satisfying FR-002 by construction and avoiding drift between two validators that are supposed to behave identically.

**Alternatives considered**:
- *Write a separate validator scoped to `Profile`.* Rejected: no behavioral difference is required or desired (FR-002 explicitly says "the same color value formats... as it already accepts"), so a second implementation would be pure duplication and a future drift risk.

## Outcome

All `NEEDS CLARIFICATION` items are resolved. No new third-party dependency is required. No constitution violations were identified in plan.md's Constitution Check; Decision 2 directly satisfies the one flagged gate item (Durability & Interoperability for the Exchange XML format).
