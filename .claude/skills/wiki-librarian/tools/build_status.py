#!/usr/bin/env python
"""Diff wiki/sources.yaml against wiki/.build-log.yaml: what needs rebuilding.

Read-only. Run from the repo root (the directory holding wiki/).

    python tools/build_status.py             # per-topic status + reasons
    python tools/build_status.py --check     # exit 1 if any topic is NEW/STALE/ORPHAN
    python tools/build_status.py --coverage  # also list repo docs no topic covers

Statuses:
    NEW     no build-log entry yet -- must be built
    STALE   a source changed / was added / removed, or the page is missing
    FRESH   every source matches the build log -- skip unless --force
    ORPHAN  build-log (and maybe page) for a topic no longer in sources.yaml
"""

from __future__ import annotations

import argparse
import os
import sys

import wiki_common as wc

DOC_EXT = {".md", ".rst", ".txt", ".adoc"}


def _walk_docs() -> list[str]:
    out: list[str] = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in wc.IGNORE_DIRS and not d.startswith(".")]
        for f in files:
            if os.path.splitext(f)[1].lower() in DOC_EXT:
                out.append(os.path.normpath(os.path.join(root, f)).replace(os.sep, "/"))
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    ap.add_argument("--root", help="repo root (dir holding wiki/); default: $WIKI_ROOT or the current directory")
    args = ap.parse_args()
    wc.apply_root(args.root)

    if not os.path.isfile(wc.SOURCES_FILE):
        print(f"no {wc.SOURCES_FILE} -- run the librarian to scaffold it", file=sys.stderr)
        return 1

    log = wc.load_build_log()
    resolved = wc.resolve_all()
    needs_build = 0

    for r in resolved:
        status, reasons = wc.topic_status(r, log)
        if status in ("NEW", "STALE"):
            needs_build += 1
        print(f"{status:6}  {r['name']}")
        for why in reasons:
            print(f"          - {why}")

    for name in wc.orphan_topics(log):
        needs_build += 1
        print(f"ORPHAN  {name}")
        print("          - in build log but not sources.yaml; delete page + entry")

    if args.coverage:
        # Exact: the set every topic's path globs actually resolve to, not an
        # fnmatch approximation (fnmatch does not honour '**' or '/').
        covered = set(wc.all_source_files())
        uncovered = [d for d in _walk_docs() if d not in covered]
        print("\n# repo docs matched by no topic:")
        for d in uncovered:
            print(f"  {d}")
        if not uncovered:
            print("  (none)")

    if args.check and needs_build:
        print(f"\n{needs_build} topic(s) need a rebuild", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
