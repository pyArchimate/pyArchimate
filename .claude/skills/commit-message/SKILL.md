---
name: commit-message
description: Write and check git commit messages against the Conventional Commits standard and this repo's internal conventions (allowed types, package/area scopes, `v$version` tags, commitizen config). Use whenever you are about to `git commit`, are asked to fix or reword a commit message, or need to audit the messages on a branch before opening a PR.
---

# commit-message

This repo enforces [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
through commitizen (`[tool.commitizen]` in `pyproject.toml`, `cz_conventional_commits`).
Releases and the changelog are driven from commit history, so a malformed message is a
real defect, not a style nit.

`references/standard.md` is the authoritative internal spec — allowed types, the scope
list, subject rules, footer rules, and how commitizen consumes them. Read it before
writing or judging a message.

## Writing a commit message

1. Run `git status` and `git diff --staged` (or `git diff` if nothing is staged yet).
   Decide whether the staged change is *one* logical change. If it is two, say so and
   propose splitting it rather than writing a vague subject that spans both.
2. Pick the **type** and optional **scope** from `references/standard.md`. Scope is a
   `src/pyArchimate/` submodule (`model`, `derivation`, `readers`, `writers`, …) or a
   top-level area (`agents`, `skills`, `devcontainer`, `specs`, `ci`, …). When in doubt
   whether a scope exists, grep the list in the reference and recent history:
   `git log --format='%s' -50`.
3. Write the subject: `<type>(<scope>)?: <description>` — imperative mood, lower-case
   first word, no trailing period, ≤ 72 chars.
4. Add a body only when the *why* is not obvious from the diff. Wrap at 72 columns,
   separate from the subject with a blank line.
5. Footers: `BREAKING CHANGE: <what and migration>` for any incompatible change (or a
   `!` after type/scope), `Refs: #123` / `Closes: #123` for issue links. Keep the
   `Co-Authored-By:` and session trailers the harness appends.
6. Validate before committing — see below.

## Checking a message

Prefer the tool if it is installed, fall back to the manual checklist otherwise.

```bash
# single message (string or file)
poetry run cz check --message "$(git log -1 --pretty=%B)"      # last commit
poetry run cz check --message "feat(agents): add commit-message skill"
# a range, e.g. everything this branch adds over master (every PR here targets master)
poetry run cz check --rev-range "$(git merge-base origin/master HEAD)..HEAD"
```

If `cz` is unavailable (`poetry run cz` fails), check by hand
against `references/standard.md`:

- subject matches `^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9_-]+\))?!?: .+`
- description is imperative, lower-case, no full stop, ≤ 72 chars
- scope (if present) is in the allowed list
- body (if present) is separated by a blank line and wrapped
- a breaking change has either `!` or a `BREAKING CHANGE:` footer, never only prose

Report each offending commit as `<short-sha> <subject>` with the specific rule it
breaks and a corrected version. Do **not** rewrite published history yourself — for
commits already pushed, propose the reworded messages and let the user decide whether
to rebase.

## Fixing

- Not yet committed: just write the message correctly.
- Last local commit: `git commit --amend` with the corrected message.
- Several local commits: hand the user a `git rebase` plan (reword lines) with the new
  messages filled in; the environment has no interactive rebase, so spell out each
  `git commit --amend` / `git rebase --continue` step or provide a script.

## Guardrails

- Never `git push --force*` to rewrite messages on a shared branch without explicit
  user approval.
- Never invent a scope. If the change needs a scope that does not exist yet, add it to
  `references/standard.md` in the same commit and note it.
- Do not "helpfully" widen a commit's stated impact — if the diff is one bug fix,
  `fix:` it, don't `feat:` it.
