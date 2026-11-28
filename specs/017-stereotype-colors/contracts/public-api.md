# Public API Contract: Stereotype-Based Color Coding

pyArchimate is a library, not a service — its "contract" is the Python API surface consumers (and the SVG exporter) rely on. This documents the additions/changes this feature makes to that surface. No existing public signature is removed or renamed.

## `Profile` (`pyarchimate.view.Profile` / `src/pyArchimate/view/__init__.py`)

### New attribute: `fill_color`

```python
profile = model.add_profile(name="Threat", concept="Driver")

profile.fill_color                      # -> None (unset by default; FR-003, FR-014)
profile.fill_color = "#E8453C"          # set a color; FR-001
profile.fill_color                      # -> "#e8453c" (normalized; FR-002)
profile.fill_color = "DarkOrange"       # named colors accepted, case-insensitive; FR-002
profile.fill_color = "not-a-color"      # raises ValueError; FR-002
profile.fill_color = None               # clears back to unset; FR-003
```

**Contract**:
- Getter returns `str | None`.
- Setter accepts `str | None`; a non-`None` value is validated and normalized exactly as `Element.set_fill_color()` does (same accepted formats, same `ValueError` on invalid input).
- Setting to `None` always succeeds and clears the color.

## `Element` / `Node` — effective fill color resolution

No new public method is strictly required to satisfy the spec's user-facing behavior (SVG export must use the resolved color automatically, FR-011), but a new read-only helper is added for callers who want the resolved value directly without exporting:

```python
node.get_effective_fill_color()   # -> str | None
```

**Contract**:
- Returns, in order (see `research.md` Decision 1):
  1. `node.fill_color`, if set.
  2. Else the underlying element's `get_fill_color()`, if set.
  3. Else the underlying element's assigned `Profile.fill_color`, if the element has a profile and that profile has a color configured.
  4. Else `None` (the caller — e.g. the SVG exporter — applies the existing type-based theme default exactly as it does today).
- Never raises for a well-formed `Node`; a `Node` with no concept, no profile, or no explicit colors simply resolves to `None` (unchanged current behavior, FR-006).

## `View.to_svg()` (`pyarchimate.view.View.to_svg`)

### Changed default behavior (no signature change)

```python
view.to_svg(filepath)                                  # default: non-standard stereotypes auto-labeled (FR-016/FR-017)
view.to_svg(filepath, show_stereotypes=True)            # unchanged: force every stereotype label, standard or not (FR-018)
```

**Contract**:
- `show_stereotypes` keeps its existing name, default (`False`), and type (`bool`); its meaning when `True` is unchanged (force-show every element's stereotype label).
- When `show_stereotypes=False` (the default, including when the caller omits it entirely), the exporter now shows the `«stereotype»` label for any element whose assigned profile's name differs, case-insensitively, from the element's `ArchiType` value (FR-016), and shows no label otherwise (FR-017) — a behavior change from "never shown unless the flag is `True`" to "shown automatically when non-standard."
- An element with no assigned profile never shows a label by default, with the flag unset, or with the flag `True` applied with no profile present — unchanged (edge case: "no stereotype assigned").

## Persistence (not a Python API, but a file-format contract)

### Archi-native (`.archimate`)

- The `<profile>` element gains an optional `fillColor` attribute: `<profile name="Threat" id="..." conceptType="Driver" fillColor="#e8453c"/>`.
- Absent `fillColor` → `Profile.fill_color` is `None` on read (backward compatible, FR-014).

### Open Group Exchange XML

- New, previously-absent: each element with an assigned profile gains `profileId` (the stereotype's UUID), `profile` (name), and (if the profile has a color) `profileColor` properties, registered via the existing `propertyDefinitions` mechanism (see `research.md` Decision 2 and `data-model.md`).
- On read, profiles are reconstructed keyed by `profileId`, not by name — two distinct stereotypes sharing a name but specializing different concept types are correctly kept separate (2026-11-28 clarification in `spec.md`).
- A file with no such properties → no profiles reconstructed on read (backward compatible — matches current behavior exactly, since no file written before this feature could have had them).

## Backward compatibility guarantee

Every signature named above either is entirely new (`Profile.fill_color`, `get_effective_fill_color()`) or keeps its existing name, parameter list, and default value (`to_svg(show_stereotypes=False)`). No caller using only the pre-existing API surface observes any behavior change, except the two explicitly spec'd, intentional ones: (1) a stereotype's configured color now appears where no color appeared before, and only when a profile is actually configured with one; (2) non-standard stereotype labels now appear by default where none appeared before, and only for non-standard names.
