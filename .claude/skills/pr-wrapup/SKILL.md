---
name: pr-wrapup
description: 'Wrap up a GitHub issue and its PR once the PR is merged — verify the merge, check the issue acceptance criteria against the base branch, delete the remote branch, close the issue with a summary comment, remove the local worktree and branches, prune, and report leftovers. Use for "PR merged, clean up", "wrap up issue #N", "/pr-wrapup <PR#>".'
---

# pr-wrapup

Post-merge housekeeping for one PR and the issue(s) it fixes. Every destructive step is
gated on **proof the work is in the base branch** — never delete a branch or worktree on
the strength of "the user said it merged".

Inputs: a PR number (preferred) or an issue number (find the PR with
`gh pr list --state merged --search "<issue#>"`). Always pass
`-R pyArchimate/pyArchimate` to `gh` — the worktrees can trip git's
"dubious ownership" check, which makes `gh` fail to infer the repo.

## 1. Verify the merge

```bash
gh pr view <PR> -R pyArchimate/pyArchimate \
  --json state,mergedAt,mergeCommit,baseRefName,headRefName,headRefOid,closingIssuesReferences,url
```

- `state` must be `MERGED`. Anything else → stop and report.
- Note `baseRefName`. Every PR in this repo — feature, bugfix, dependabot, even CI-sync
  PRs — targets **`master`** directly (verified via `gh pr list --json baseRefName`; CI
  only triggers on `pull_request: branches: [master]`). GitHub auto-closes `Closes #N`
  issues on merge to the default branch, which is `master`, so step 4 is usually a
  no-op here — but still check: a squash/rebase merge or a PR body missing the closing
  keyword can leave the issue open anyway.
- `git fetch --prune origin`, then prove the local branch holds nothing unmerged:
  - local tip == `headRefOid` (nothing committed locally after the PR's last push), **and**
  - `git merge-base --is-ancestor <headRefOid> origin/<base>` succeeds (merge commit /
    rebase-merge). For a **squash** merge that check fails by design — instead confirm
    `git diff <headRefOid> <mergeCommit> --stat` is empty or only shows changes that
    landed on the base after the branch point.
  - Any local-only commits or an unexplained diff → stop and show them.

## 2. Check the acceptance criteria

A merged PR proves the branch landed, not that the issue is done. For each linked issue
still `OPEN`, check it against the base branch before anything closes it:

```bash
gh issue view <N> -R pyArchimate/pyArchimate --json title,body,state
```

- Pull out the criteria: an "Acceptance criteria" section or `- [ ]` checkboxes first.
  With neither, fall back to the "Scope" bullets (respecting "Out of scope"). With no
  usable criteria at all, tell the user and use the issue title as the single criterion.
- Check each one against **`origin/<base>`** (after step 1's fetch), not the worktree:
  `git grep <pattern> origin/<base> -- <paths>`, `git show origin/<base>:<path>`,
  `git log origin/<base> --oneline -- <path>`. For "no more X" criteria, grep for X and
  expect no hits (exclude generated or historical paths like `wiki/` and `docs/adr/` when
  that is the intent).
- Show the user a table: criterion → **met / partly met / not met** → evidence
  (`path:line` or commit SHA, or the command whose empty output proves an absence).
- All met → go on. Otherwise stop and ask which of these the user wants: open a
  follow-up issue for the gaps, leave the issue open, or close it anyway with the gaps
  noted in the close comment.

## 3. Delete the remote branch

Skip if GitHub already deleted it (`git ls-remote --heads origin <head>` is empty).

```bash
git push origin --delete <headRefName>
```

## 4. Close the issue with a comment

For each linked issue still `OPEN` (`gh issue view <N> --json state`) that passed step 2,
or that the user chose to close with gaps noted — skip any they chose to leave open:

- Draft a short comment in the scratchpad:
  ``Fixed by #<PR> (merged into `<base>` as <short mergeCommit>).`` plus one to three
  lines on what changed and any ADR / follow-up issue. Reuse the PR body's summary;
  don't restate the whole PR. Add one line on what step 2 checked (e.g. "Acceptance
  criteria verified against `master`: 4/4 met."), and list any gaps the user chose to
  close with.
- Show the draft to the user, then:

```bash
gh issue close <N> -R pyArchimate/pyArchimate --reason completed \
  --comment "$(cat <scratchpad>/issue-<N>-close.md)"
```

If the issue was already closed (default-branch PR), don't add a duplicate comment.

## 5. Remove the local worktree

Run from the **main checkout** (`/workspaces/pyArchimate`), never from inside
the worktree being removed — the session's cwd disappears with it, so use absolute paths
from here on.

```bash
git worktree list                        # find the worktree for <headRefName>
git -C <worktree> status --porcelain     # must be empty; otherwise stop and show it
```

Poetry venvs live outside the worktree, in `{cache-dir}/virtualenvs` (check with
`poetry config virtualenvs.path`), keyed by a hash of the worktree's absolute path — so a
venv created by `poetry install` inside this worktree is never cleaned up by deleting the
directory; it just becomes an orphaned entry in that cache. Remove it **before** the
directory goes, since Poetry needs to read the worktree's `pyproject.toml` to resolve
which venv(s) belong to it:

```bash
poetry -C <worktree> env remove --all
```

Skip with no error if `poetry env list -C <path>` shows nothing — not every worktree had
`poetry install` run in it.

```bash
git worktree remove <worktree>
```

On this drvfs mount `git worktree remove` often unregisters the worktree but fails to
delete the directory (`Permission denied`). After checking the path is exactly the
worktree you meant (not the main checkout, not a sibling), finish with
`sudo rm -rf <worktree>` and then `git worktree prune`.

## 6. Delete local branches

```bash
git branch -d <headRefName>     # -D only after step 1 proved it merged (squash merges need -D)
```

Also delete any scratch branches made for this work (e.g. `backup/<issue>-before-reword`)
— list them with `git branch --list '*<issue#>*'`, show the user, and delete with `-D`.

If git fails with `could not lock config file .git/config: Operation not permitted`
(drvfs EPERM when removing upstream tracking), repeat the command as
`sudo git -c safe.directory='*' <command>`.

## 7. Prune and report

```bash
git worktree prune
git fetch --prune origin
git -C /workspaces/pyArchimate status -sb   # is local <base> behind?
```

Finish with a short report of what was done (with SHAs), then the **leftovers**:

- local `<base>` behind `origin/<base>` → suggest `git pull --ff-only` (don't run it if
  the checkout has uncommitted or staged changes that aren't yours).
- follow-ups listed in the PR body (open issues for them if the user agrees).
- generated docs that now describe stale behaviour (`wiki/` pages → run `wiki-librarian`
  on the affected topic).
- advisories from `scripts/check_snyk.py` / `scripts/check_sonarcloud.py` or reviewers
  that weren't acted on.
- CI checks that were red but accepted (e.g. Snyk quota), so they aren't mistaken for
  new failures later.

## Guardrails

- Remote actions (branch delete, issue comment/close) are outward-facing: confirm with
  the user once for the set, unless they already asked for exactly these steps.
- Never force-delete a branch, `rm -rf` a directory, or close an issue before step 1
  passes.
- Never close an issue before its acceptance criteria are verified against the base
  branch (step 2), unless the user explicitly chose to close it with the gaps noted.
- Never touch changes you didn't make in the main checkout (stray staged files, other
  worktrees) — report them instead.
- Don't reopen, edit, or re-merge the PR; this skill only tidies up after it.
