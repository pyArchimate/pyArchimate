# Commit message standard (internal)

Baseline: **Conventional Commits 1.0.0**. Enforced by commitizen
(`[tool.commitizen]` in `pyproject.toml`, ruleset `cz_conventional_commits`).
This file records the repo-specific choices layered on top.

## Format

```
<type>(<scope>)?<!>?: <description>

<body>

<footers>
```

Only the subject line is mandatory.

## Types

| Type       | Use for                                                        | Bumps |
|------------|---------------------------------------------------------------|-------|
| `feat`     | a new capability, user- or agent-visible                       | minor |
| `fix`      | a bug fix                                                      | patch |
| `docs`     | documentation only (README, ARCHITECTURE, specs prose, skills) | –     |
| `style`    | formatting/whitespace, no code-behaviour change                | –     |
| `refactor` | code change that neither fixes a bug nor adds a feature        | –     |
| `perf`     | performance improvement                                        | patch |
| `test`     | adding or correcting tests only                                | –     |
| `build`    | build system, dependencies, packaging, devcontainer            | –     |
| `ci`       | CI config (`.github/`, workflows) and gate/audit scripts under `scripts/`, speed-ups and fixes included | – |
| `chore`    | maintenance that fits nothing above (lockfile pins, cleanup)   | –     |
| `revert`   | reverts a previous commit; body has `Refs: <sha>`              | –     |

> **Agents and skills:** a change to `.claude/agents/` or `.claude/skills/` that
> alters behaviour (new input, step, command or gate) is `feat(agents|skills)` or
> `fix(agents|skills)`. Wording or clarification only is `docs(agents|skills)`.

A `!` before the colon, or a `BREAKING CHANGE:` footer, marks an incompatible
change and forces a major bump regardless of type.

## Scopes

Optional but expected when a change is localised. Lower-case, `[a-z0-9_-]+`.
pyArchimate is a single package (no monorepo), so scopes name either a
`src/pyArchimate/` submodule or a cross-cutting area of the repo:

**Library scopes** — a `src/pyArchimate/` submodule or concern:

- `model` — `model.py` (the `Model` class and its checks)
- `derivation` — `derivation.py` (derived-relationship computation)
- `readers` / `writers` — `readers/`, `writers/` (Archi `.archimate` / Open
  Group Exchange `.xml` round-trip)
- `viewpoint` — `viewpoint.py`, `viewpoint_registry.py`
- `svg` — SVG view rendering
- `routing` — view layout / connection routing
- `relationship` — `relationship.py` (metamodel legality, derivation)
- `element` — `element.py`
- `helpers` — `helpers/`

**Area scopes** — cross-cutting parts of the repo:

- `agents` — `.claude/agents/` and `.claude/skills/`
- `skills` — a single skill when `agents` is too broad
- `devcontainer` — `.devcontainer/`
- `speckit` — Spec Kit integration, `.specify/`
- `specs` — feature specs under `specs/`
- `wiki` — the generated `wiki/` (content produced by the `wiki-librarian` skill)
- `ci` — `.github/workflows/`, release/versioning plumbing
- `scripts` — gate and audit scripts under `scripts/`
- `tests` — test-suite changes not tied to one library scope
- `docs` — `docs/` build tooling itself (Sphinx config, `build_docs*.sh`) —
  content-only doc edits use the `docs:` *type* instead, with no scope needed
- `deps` / `deps-dev` — dependency bumps (`chore(deps):`, `chore(deps-dev):`)

Omit the scope for genuinely repo-wide changes. Add a new scope to this list
in the same commit that first needs it.

## Subject rules

- imperative mood: "add", "fix", "remove" — not "added" / "adds"
- lower-case first word (after the colon)
- no trailing period
- ≤ 72 characters including the `type(scope):` prefix
- describe the change, not the file touched ("prevent duplicate scope" not
  "edit validator.py")

## Body

- required only when the reason for the change is not evident from the diff
- blank line between subject and body
- wrap at 72 columns
- explain *why* and any non-obvious *how*; the diff already shows *what*

## Footers

- `BREAKING CHANGE: <description + migration path>` — mandatory prose for any
  `!`-marked commit
- `Refs: #<n>`, `Closes: #<n>`, `Fixes: #<n>` — issue links
- `Co-Authored-By:` and `Claude-Session:` / harness trailers — keep as appended
- `Revert: <sha>` on `revert` commits

## Tags & versioning

- release tags are `v$version` (`tag_format = "v$version"`), PEP 440 /
  `poetry-dynamic-versioning`, semver style
- `cz bump` reads the log since the last tag, applies the bump implied by the
  types above, and updates the changelog (`update_changelog_on_bump = true`);
  its own `bump: version <A> → <B>` commit is tool-generated and exempt from
  the type list, like `Merge` commits
- never hand-edit the changelog or move a `v*` tag

## Tooling

```bash
poetry run cz check --message "<msg>"             # lint one message
poetry run cz check --rev-range <base>..HEAD      # lint a range
poetry run cz commit                              # interactive prompt
poetry run cz bump                                # version bump + changelog from history
```

`cz check` is the only automated enforcement — there is no `commit-msg` git hook and
nothing in `.pre-commit-config.yaml` runs it, so it must be invoked explicitly (this
skill, or by hand) rather than relied on to catch a bad message automatically. It
checks Conventional Commits structure (type/scope/`!`/subject shape) but not this
file's repo-specific rules — imperative mood, the scope list above, body wrap — so
still check those by hand per the "Checking a message" steps in `SKILL.md`.

commitizen is declared in the `dev` dependency group (`poetry install --with dev`).
If `poetry run cz` does not work, fall back to the regex/checklist in the
`commit-message` skill.
