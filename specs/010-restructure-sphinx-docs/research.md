# Research: Restructure Sphinx Documentation

**Feature**: 010-restructure-sphinx-docs  
**Date**: 2026-05-03

## Decisions

### 1. Markdown integration — myst-parser vs RST conversion

**Decision**: Add `myst-parser` to Sphinx extensions; keep `tutorial/tutorial.md` as Markdown.

**Rationale**: `tutorial/tutorial.md` is 589 lines already structured with Basic/Intermediate/Advanced headings. Converting to RST is lossy (tables, code blocks differ) and creates a maintenance burden. `myst-parser` is the canonical Sphinx solution and works with the existing RTD theme. Sphinx `source_suffix` mapping routes `.md` files transparently.

**Alternatives considered**:
- Convert to RST — rejected: ~2 hours of manual reformat, ongoing diff noise, no benefit
- RST `.. include::` wrapper with `.. literalinclude::` — rejected: loses Sphinx toctree integration (page won't appear in nav)
- Separate documentation site (MkDocs) — rejected: out of scope per spec assumptions

### 2. Three-tier navigation architecture

**Decision**: Three `toctree` sections in `index.rst` using RTD theme sidebar labels: "Basic Usage", "Intermediate / Architecture", "Advanced / API Reference". One hidden toctree for `changelog`, `src`, `p3-quick-reference`.

**Rationale**: RTD theme renders `toctree` `:caption:` values as sidebar section headers — no custom CSS or JavaScript required. Satisfies FR-001 directly. Hidden toctree keeps legacy pages reachable by URL without cluttering navigation.

**Alternatives considered**:
- Separate Sphinx projects per tier — rejected: cross-references between tiers require intersphinx, adds complexity
- Custom HTML theme with tier badges — rejected: over-engineered; RTD `:caption:` is sufficient for FR-001

### 3. Broken reference resolution

**Decision**: Recreate all deleted guide/example files rather than editing their referencing files.

**Rationale**: `api/element.rst`, `api/model.rst`, and `changelog.rst` contain references to files deleted on this branch. Recreating the target files is the correct fix — the content belongs in those locations (guides/, examples/, p3-quick-reference.rst). Editing the referencing files to remove useful cross-references would degrade documentation quality.

**Specific broken refs fixed by recreation**:
- `docs/guides/element-hierarchy.rst` — referenced by `api/model.rst` (See Also) and `api/element.rst` (body)
- `docs/guides/visual-styling.rst` — referenced by `api/element.rst` (See Also)
- `docs/guides/junction-types.rst` — referenced by `api/element.rst` (See Also)
- `docs/examples/hierarchy_examples.rst` — referenced by `api/model.rst` (See Also)
- `docs/examples/styling_examples.rst` — referenced by `api/element.rst` (See Also)
- `docs/p3-quick-reference.rst` — referenced by `changelog.rst` (v1.3.0 section)

### 4. diagrams.rst fate

**Decision**: Keep `diagrams.rst` unchanged; include it in `architecture.rst` via `.. include:: diagrams.rst`. Remove direct reference from `index.rst` (already removed in current branch state).

**Rationale**: `diagrams.rst` contains PlantUML image directives with relative paths that work from the `docs/` root. Including it verbatim in `architecture.rst` is safe. The page remains reachable through `architecture.rst` in the Intermediate tier without duplicating content.

### 5. myst-parser dependency management

**Decision**: Add `myst-parser` to `docs/requirements.txt` and to the `docs` optional-dependency group in `pyproject.toml`.

**Rationale**: Keeps dependency declaration consistent with existing pattern (sphinx and sphinx-rtd-theme are both declared in docs group). Build systems (Read the Docs, CI) using `pip install -r docs/requirements.txt` will pick it up automatically.

### 6. viewpoints documentation gap

**Decision**: Create `docs/api/viewpoints.rst` with manual overview + `automodule` for `pyArchimate.viewpoint` and `pyArchimate.viewpoint_registry`.

**Rationale**: Both modules are part of the public API (used by `Model.get_viewpoints()`, `Element.assign_viewpoint()`, etc.) but have no doc pages. Adding them closes the FR-005 gap and provides the standard viewpoints table for FR-006 (domain concepts).

### 7. api/element.rst and api/model.rst enhancements

**Decision**: Both files require edits for **FR-005 enhancement** (not fixes): Add "New to this topic?" context notes at the top per the clarification on deep-link navigation. Broken refs to guides/examples are fixed by recreating target files (Decision #3), not by editing these files.

**Rationale**: The files have no stale or broken `:doc:` paths; all refs to `../guides/*` and `../examples/*` will resolve after recreation. However, FR-005 clarification (Q5) requires each Advanced API page to include a "New to this topic?" note linking to the relevant Intermediate guide. This is an enhancement for better UX, not a fix.

**Specific enhancements**:
- `api/element.rst`: Add "New to this topic?" note linking to `guides/visual-styling` and `guides/junction-types`
- `api/model.rst`: Add "New to this topic?" note linking to `guides/element-hierarchy`