---
name: wiki-librarian
description: Builds and refreshes wiki/ — a derived, regenerable project wiki synthesized from repo files (globbed from root and subdirectories) and external documents referenced by URL. wiki/sources.yaml declares topics and their sources; each topic becomes one synthesized prose page with citations back to its sources; wiki/.build-log.yaml fingerprints every source so a re-run rebuilds only what changed. Use when the user says "run the librarian" / "run wiki-librarian" or asks to build, generate, or refresh the wiki. Scaffolds wiki/ automatically when it doesn't exist yet.
---

# Librarian

Builds `wiki/` — a **derived cache**. Nothing in `wiki/` is hand-authored
content; every page is synthesized from declared sources and can be
regenerated. The source of truth is the repo itself (plus any external URLs
listed in `wiki/sources.yaml`), never the wiki.

## Model

- `wiki/sources.yaml` — the one file a human edits. Declares `topics`; each
  topic has a `name`, `title`, and a `sources` list. A source is either a
  `path` (a glob, relative to the repo root, `**` allowed) or a `url` (an
  external document, optionally with a `title`).
- `wiki/<name>.md` — one synthesized prose page per topic, with YAML
  frontmatter and citations. Generated; overwrite freely on rebuild.
- `wiki/index.md` — generated links to every topic page.
- `wiki/.build-log.yaml` — per topic: the resolved source files and URLs with
  content fingerprints (sha256 + line count) and the build date. This is what
  makes "rebuild only what changed" possible.
- `wiki/.cache/<hash>.md` — the fetched markdown of each `url` source, so a
  build is reproducible and a URL's content change is detectable. Committed.
- `index.sqlite` — gitignored local semantic index (see "Semantic search").

## The tools

Scripts ship under `tools/` (shared `wiki_common.py`). They operate on `wiki/`
**relative to the current directory** — run them from the repo root (the
directory holding `wiki/`). **Always invoke them with `poetry run python`** —
`pyyaml`, used by all of them, lives in the Poetry venv, not the system
interpreter, so bare `python` fails with `ModuleNotFoundError`.

**Semantic search deps:** `numpy` + `fastembed` (for `semsearch.py` only) are
deliberately *not* Poetry dependencies — every released `fastembed` caps
`pillow` at `<13.0`, which would conflict with `pyarchimate`'s `pillow>=13.0`
floor in the same unified Poetry graph. `semsearch.py` instead manages its
own private copy of just those two packages under `tools/.venv` (gitignored),
`pip install --target`-ed in on first use and added to `sys.path` — no action
needed, but the first `index`/`search` after a fresh checkout takes longer
while it bootstraps.
`semsearch.py`'s model cache lands outside the repo — override with
`$SEMSEARCH_CACHE`. It sizes its embedding worker pool to free RAM and core
count automatically; `$SEMSEARCH_PARALLEL` overrides it (`1` = force single
in-process, `0` = all cores), `$SEMSEARCH_EMBED_BATCH` sets the batch / commit
granularity (default 32).

```bash
poetry run python tools/resolve_sources.py         # sources.yaml -> resolved files/URLs per topic, unmatched globs
poetry run python tools/build_status.py            # per topic: FRESH / STALE / NEW / ORPHAN vs .build-log.yaml
poetry run python tools/build_status.py --check    # same, exit non-zero if anything needs a rebuild
poetry run python tools/build_status.py --coverage # also list repo docs matched by no topic
poetry run python tools/verify_wiki.py             # pages exist, linked from index, citations resolve, log consistent
poetry run python tools/semsearch.py index --scope all
```

`build_status.py` and `verify_wiki.py` are read-only. Page generation is done
by you (this skill), not a script — synthesis is the whole point.

## Steps

### 1. Scaffold if `wiki/` is absent

If there is no `wiki/` directory (or no `wiki/sources.yaml`):

1. Create `wiki/` and `wiki/.cache/`.
2. **Auto-discover candidate sources**: glob the repo for documentation —
   `*.md` at root, `docs/**`, `architecture/**`, `specs/**`, `*.md` in
   notable subdirectories — and any other obvious knowledge files. Ignore
   `.git`, `node_modules`, virtualenvs, lockfiles, `.claude/`, generated
   output, and anything in `.gitignore`.
3. Draft `wiki/sources.yaml` grouping the discovered files into a proposed
   topic map (see "Writing sources.yaml" below). Group by subject, not by
   directory — one topic may pull from several locations.
4. **Stop and show the user the proposed `sources.yaml`.** Do not generate
   pages yet. Let them add/remove topics, adjust globs, or add `url` sources.
   Resume at step 2 once they confirm.

On a repo that already has `wiki/sources.yaml`, skip this step entirely.

### 2. Resolve and diff

1. Run `poetry run python tools/resolve_sources.py` and read it. Report any
   unmatched globs to the user — a glob matching nothing is usually a typo or a
   moved file, not intentional.
2. Run `poetry run python tools/build_status.py`. It classifies each topic:
   - **NEW** — no build-log entry; must be built.
   - **STALE** — a source file's fingerprint changed, a source was
     added/removed, or a URL's cached content changed; must be rebuilt.
   - **FRESH** — every source matches the build log; skip unless `--force`.
   - **ORPHAN** — a build-log entry (and possibly a page) for a topic no
     longer in `sources.yaml`. Delete the page and its log entry, and drop
     its link from `index.md`. Mention it in the report.
3. If the user asked for a full rebuild, or passed `--force`, treat every
   topic as STALE.

### 3. Build each NEW/STALE topic

For each topic to build:

1. **Gather sources.** Read every resolved source file. For each `url`
   source, fetch it (WebFetch), write the returned markdown to its
   `wiki/.cache/<hash>.md` path, and read that. If a fetch fails, use the
   existing cache file if present and note the staleness in the page
   frontmatter; if there is no cache either, skip that URL and flag it.
2. **Synthesize the page** — see "Writing a topic page" below. This is a
   genuine digest: read the sources, understand the topic, and write a clear
   reference page in your own words. Do not paste source prose. Every
   non-obvious claim carries a citation to where it came from.
3. **Write `wiki/<name>.md`**, overwriting any previous version.
4. **Record the build** in `wiki/.build-log.yaml`: the topic's `title`,
   `page`, `built` date, and under `sources` every resolved file with its
   fingerprint (`sha256`, `lines`) and every URL with its `title`,
   `retrieved` date, and content `sha256`. `wiki_common.file_fingerprint`
   and the resolver give you these — match their shape exactly so
   `build_status.py` can diff them.

### 4. Index and finish

1. Regenerate `wiki/index.md` — a short intro line noting the wiki is
   generated, then a link + one-line description per topic page, in
   `sources.yaml` order.
2. Set/update the top of `.build-log.yaml`: `generated` (today),
   `generator` (your model id, e.g. `claude-sonnet-5`).
3. **Editor pass.** If any page was built this run, run the `wiki-editor`
   skill over exactly those pages (plus `index.md` for its link check). Run
   it before verification so `verify_wiki.py` checks the edited pages. Carry
   anything the editor flagged but couldn't fix into the run report.
4. Run `poetry run python tools/verify_wiki.py` and `poetry run python
   tools/build_status.py --check`. Act on every finding — a run is not done
   until both exit clean or every remaining finding has been explained to the
   user. Do not report a page as built on the strength of having written a log
   entry.
5. Run `poetry run python tools/semsearch.py index --scope all` so the next run
   searches a current index. The embed step is
   CPU-bound (order minutes for a full `--scope all`); it auto-sizes its worker
   pool to available RAM so it should not OOM. If it still is, set
   `$SEMSEARCH_PARALLEL=1` or fall back to `--scope wiki`, and say so in the
   report.
6. Report what was built/skipped/removed, what the editor pass changed or
   flagged, any unmatched globs, any failed URL fetches, and — if a page
   crossed ~500 lines — suggest a split (see "Oversized pages").

## Writing sources.yaml

```yaml
# wiki/sources.yaml — declares what the wiki is built from.
# Edit this file; everything else under wiki/ is generated.
topics:
  - name: architecture            # -> wiki/architecture.md, must be a slug
    title: Architecture Overview
    description: How the platform is layered and why.   # used in index.md
    sources:
      - path: ARCHITECTURE.md
      - path: architecture/**/*.md
      - path: TECHNICAL.md
  - name: external-standards
    title: External Standards
    description: The OSCAL and ArchiMate specs the platform targets.
    sources:
      - url: https://pages.nist.gov/OSCAL/
        title: OSCAL Documentation
      - path: sample-data/schema/*.xsd
```

- `name` must be a filename-safe slug and unique. It fixes the page path.
- Prefer a few broad globs over listing every file — new matching files then
  get picked up automatically (and `build_status.py --coverage` flags docs
  that no topic covers).
- A `url` source is fetched at build time and cached. Use it for external
  specs, upstream docs, RFCs — anything outside the repo the wiki should
  summarize and link to.
- Keep topics subject-shaped and non-overlapping. If two topics would pull
  the same file to say the same thing, merge them.

## Writing a topic page

The page is a **synthesized reference**, not an extract and not a fact log.

```markdown
---
title: Architecture Overview
generated: 2026-08-29
generator: claude-sonnet-5
sources:
  - ARCHITECTURE.md
  - architecture/data-flow.md
  - https://pages.nist.gov/OSCAL/  (retrieved 2026-08-29)
---

> Generated by `wiki-librarian` from the sources above. Edit `wiki/sources.yaml`
> and rebuild rather than editing this page.

## Layers

The platform separates ... into three layers (`ARCHITECTURE.md` §Layers).
The governance layer owns ... while code lives under `platform/`
(`ARCHITECTURE.md` §Repository layout).

## Data flow

Requests enter through the FastAPI app (`src/app/main.py:20-58`) ...
```

Rules:

- **Digest, don't copy.** Explain the topic in your own words. Short exact
  quotes are fine when the precise wording matters (a defined term, a
  constitutional rule); keep them under a sentence and quote-marked.
- **Cite every non-obvious claim.** For a repo file: `` (`path/to/file.md`
  §Heading) `` for prose, `` (`path/to/file.py:40-58`) `` for code. For a
  URL source: `` ([OSCAL Documentation](https://...), retrieved DATE) ``.
  Citations are plain references, not footnotes.
- **Frontmatter** lists every source and each URL's retrieval date.
- **Structure by subject** with `##`/`###` headings. No dated-bullet
  format — that was the old personal-library model and does not apply here.
- **Cross-link** related topic pages with `[Title](other-name.md)`.
- **Say when sources disagree** rather than silently picking one — "`README.md`
  describes X as planned; `ARCHITECTURE.md` §Y treats it as current."
- **Don't invent.** If the sources don't answer something the page should
  cover, write a short "Not covered by current sources" note instead of
  guessing. Flag these in the run report.
- Keep the page to what its sources support. Length follows the material;
  if a page passes ~500 lines, see "Oversized pages".

## Refreshing (the common case)

Most runs are re-runs. Step 2's `build_status.py` does the work: it
fingerprints every current source and compares to `.build-log.yaml`.

- A doc edited in the repo → its topic goes STALE → rebuild that one page.
- A new file matching an existing glob → topic goes STALE (source added).
- A URL whose fetched content changed → topic goes STALE.
- Nothing changed → FRESH → skip, and the run is nearly a no-op.

Only rebuild what the diff flags unless the user asks for a full rebuild.
Always finish with the `wiki-editor` pass over rebuilt pages, then
`verify_wiki.py`, `build_status.py --check`, and `semsearch index`.

## Semantic search

`tools/semsearch.py` provides local semantic search over `wiki/` and the
resolved source files (`--scope wiki` / `--scope sources` / `--scope all`).
It runs entirely on this machine (fastembed/ONNX, `bge-small-en-v1.5`,
vectors in a gitignored `index.sqlite`) — no part of the corpus leaves the
machine.

```bash
poetry run python tools/semsearch.py search "how are OSCAL profiles resolved" --scope all -k 8
poetry run python tools/semsearch.py index --scope all   # refresh; skips unchanged files
```

Use it alongside `Grep`, not instead of it: `Grep` for literal names, paths,
symbols; semantic search for "where is the thing that does X" when you don't
know the wording. Treat hits as candidates to open. A flat score cluster
around 0.6 means nothing matched well; a real hit stands clear at 0.70+.

Refresh the index at the end of any run that changed wiki or source content.

## Oversized pages

If a topic page grows past ~500 lines, the topic is too broad. Don't archive
by year (that was the dated-log model). Instead split the topic in
`sources.yaml` into two or more narrower topics with disjoint source globs,
then rebuild. Suggest this in the run report; don't restructure
`sources.yaml` unprompted in the same run unless the user asked.

## Never

- Hand-author content into a `wiki/*.md` page — it will be overwritten. Put
  the intent into `sources.yaml` (a new topic, a new source) instead.
- Edit or delete the repo files that serve as sources.
- Leave `.build-log.yaml` out of sync with what was actually generated.
