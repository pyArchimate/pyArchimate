---
name: pr-preflight
description: 'Pre-flight checklist for a branch about to become a PR — refresh docs/wiki/diagrams against the real diff, run an autofix pass, confirm the quality/security/commit gates, open the PR as a draft, then watch CI and fix failures before marking it ready for human review. Use for "get this ready for a PR", "preflight this branch", "/pr-preflight".'
allowed-tools: Bash(gh pr create:*)
---

# pr-preflight

Run this on a `feature/**` / `bugfix/**` branch once the code changes are done, before
opening (or pushing further commits to) its PR. It is the mirror image of `pr-wrapup`:
that skill cleans up *after* a PR lands; this one gets a branch *into* PR-worthy shape
first. There is no repo-wide scheduled audit here — everything below is scoped to this
branch's own diff, checked by hand or with the project's own scripts/gates.

Nothing here is destructive and everything stays on the current branch: no merges, no
pushes to `master`, no issue/PR state changes. Commit as you go, in focused Conventional
Commits (`commit-message` skill ruleset) — don't bundle the whole preflight into one
commit.

Inputs: nothing required. Optionally a base ref to diff against (default: where the
branch forked from `master`, via `git merge-base HEAD origin/master`).

Every PR in this repo — feature, bugfix, dependabot, even CI-sync PRs — targets
**`master`** directly (verified via `gh pr list --json baseRefName`); CI
(`.github/workflows/ci.yml`) only triggers on `pull_request: branches: [master]`, so a
PR opened against anything else never runs CI at all. `develop` exists as a branch but
is not the PR base.

## 1. Scope the diff

```bash
git fetch origin master
BASE="$(git merge-base HEAD origin/master)"
git diff --stat "$BASE"...HEAD
git log --oneline "$BASE"..HEAD
```

Everything below is scoped to the files this range touches — this is a preflight for
*this branch's* change, not a repo-wide sweep. If the branch is still mid-work (code
changes clearly unfinished), say so and stop; don't run the rest against a half-built
diff.

## 2. Autofix pass

Run the project's own pre-commit hooks over the touched files before any manual review,
so style/lint noise doesn't show up as review comments. `scripts/pre_commit_checks.sh` /
`scripts/pre_push_checks.sh` are legacy and superseded (`scripts/README.md`) — use the
real hooks instead:

```bash
pre-commit run --all-files                        # ruff lint+format, pymarkdown, vulture
pre-commit run --all-files --hook-stage pre-push   # + pyright, mypy, layer boundaries, behave, pytest
```

If either reports fixes applied, re-stage and commit them as their own `style:`/`fix:`
commit before continuing.

For a deeper pass than lint-level autofix — reuse/simplification/efficiency cleanups and
correctness bugs in the diff itself — run the `code-review` skill with `--fix` scoped to
this branch's diff:

```text
/code-review --fix HEAD
```

Review what it changed before committing — `--fix` applies findings to the working tree,
it doesn't commit for you.

## 3. Refresh documentation and diagrams for what this branch touched

There's no scheduled audit for this — check by hand, scoped to the diff:

- **Docstrings / README / Sphinx docs (`docs/`)**: if the diff adds or changes a public
  function, class, or user-facing behaviour, check its docstring and any `docs/*.rst`
  page describing it are still accurate. Rebuild locally to check: `scripts/build_docs.sh`
  (fast, incremental) or `scripts/build_docs_release.sh` (full validation — broken
  cross-refs, toctree coverage).
- **`AI.md`**: if `docs/` changed, re-run `scripts/generate_ai_docs.py` (needs the
  `claude` CLI and `ANTHROPIC_API_KEY`) to keep it in sync.
- **Diagrams**: if the diff touches a `.puml` diagram, run `diagram-plantuml` to
  regenerate it — don't leave stale `.svg`/`.puml` output committed alongside changed
  source. `scripts/render_diagrams.sh` renders `docs/diagrams/*.puml` directly if
  that's all that's needed.
- **Wiki**: if the diff touches a file or doc a `wiki/sources.yaml` topic sources from,
  run the `wiki-librarian` skill on just that topic (not a full repo rebuild) so `wiki/`
  doesn't go stale the moment this PR merges. Skip entirely if nothing touched sources a
  topic.

Commit regenerated artefacts separately from the autofix commit, e.g.
`docs: refresh docs/diagrams for <this change>`.

## 4. Spec check

If the branch implements or changes behaviour a spec under `specs/**` describes, confirm
the spec still matches (or update it via `speckit-analyze` / by hand) — scoped to the one
spec this branch is for, not the whole `specs/` tree.

## 5. Commit message check

```bash
poetry run cz check --rev-range "$BASE"..HEAD
```

`cz check` only validates Conventional Commits structure, not this repo's scope list or
imperative-mood convention — follow the `commit-message` skill's "Checking a message"
steps for the full check. Reword any non-conforming commit now, while the branch is
still yours to rewrite — there's no `commit-msg` hook catching this later, and
`pr-wrapup` assumes it's already clean by the time a PR opens.

## 6. Quality and security spot-check

Not a substitute for CI — just enough to not open a PR with an obvious, already-known
issue:

```bash
poetry run ruff check .
poetry run pyright
poetry run mypy src/        # matches the pre-commit hook's own entry; `mypy .` errors on
                             # a duplicate-module-name clash from the top-level src/ layout
python scripts/check_sonarcloud.py
python scripts/check_snyk.py
gh api repos/{owner}/{repo}/dependabot/alerts --jq '[.[] | select(.state=="open")]'
```

If this surfaces something non-trivial to fix, don't scope-creep the branch over it —
note the follow-up in the PR description instead.

## 7. Final gate, push, and open the PR as a draft

```bash
pre-commit run --all-files --hook-stage pre-push
git push origin HEAD
gh pr create --base master --fill --draft   # or update the existing PR
```

If the hook stage fails, fix and re-run — don't push a red branch. This is the only
point in this skill that runs the full push-stage gate locally. Open as a **draft**: the
PR exists so CI runs against it, but it isn't yet asking anyone for review — that only
happens once §8 is clean.

## 8. Watch CI and fix before requesting review

```bash
gh pr checks --watch
```

CI (`.github/workflows/ci.yml`) re-runs pytest + behave across the OS matrix plus a
SonarCloud scan. Don't re-run the full pre-push hook stage again in this loop — it's slow
and CI is about to tell you the same thing. For any failing check:

```bash
gh run view --log-failed
```

Fix the cause on this branch with the narrowest tool that confirms the fix — re-run just
the specific failing check locally (e.g. `poetry run pytest <failing test file>`,
`poetry run ruff check <file>`) rather than the whole gate — then commit (small, focused
— same Conventional Commits discipline as everywhere else in this skill), push, and
re-watch CI. Repeat until green. Only fall back to a full local pre-push hook run if CI
itself is flaking in a way that makes watching it unproductive.

Stop and hand back instead of looping forever if a failure is genuinely outside this
skill's remit (unrelated flake, missing secret, a fix that would need a major/breaking
dependency bump) — report it in the PR description rather than forcing a fix.

Once every check is green, mark the PR ready for human review:

```bash
gh pr ready
```

This is the point the branch is actually asking someone to look at it. Before this,
nothing here requests review.

## Guardrails

- Everything stays on the current branch; never touch `master` directly from here.
- Scope every check to this branch's diff (`git merge-base HEAD origin/master`), not the
  whole repo.
- Commit in small, focused Conventional Commits as each step finishes, not one giant
  "preflight" commit.
- If a step surfaces something bigger than this branch's scope (a repo-wide doc gap, a
  structural refactor idea, a vulnerability in an unrelated dependency), note it as a
  follow-up rather than pulling it into this PR.
- Don't push and open the PR (§7) until §§2-6 are clean.
- The §7 pre-push hook stage runs once, before the first push. The §8 fix/push/re-watch
  loop checks only the specific thing that failed, not the whole gate again — CI already
  reruns it in full.
- The PR opens as a **draft** and only gets marked ready (§8) once CI is green — never
  call `gh pr ready` while a check is still red or hasn't run yet.
- Never merge; `pr-preflight`'s job ends at `gh pr ready` — the merge decision stays
  human.
