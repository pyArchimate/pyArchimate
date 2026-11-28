#!/usr/bin/env python
"""Expand wiki/sources.yaml into the concrete files and URLs each topic pulls.

Read-only. Run from the repo root (the directory holding wiki/).

    python tools/resolve_sources.py            # human-readable
    python tools/resolve_sources.py --json     # machine-readable

Unmatched globs are reported prominently -- a path glob that matches nothing
is almost always a typo or a moved file, not intent.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import wiki_common as wc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", help="repo root (dir holding wiki/); default: $WIKI_ROOT or the current directory")
    args = ap.parse_args()
    wc.apply_root(args.root)

    if not os.path.isfile(wc.SOURCES_FILE):
        print(f"no {wc.SOURCES_FILE} -- run the librarian to scaffold it", file=sys.stderr)
        return 1

    resolved = wc.resolve_all()
    if args.json:
        print(json.dumps(resolved, indent=2))
        return 0

    any_unmatched = False
    for r in resolved:
        print(f"# {r['name']}  ({r['title']})")
        for f in r["files"]:
            print(f"  file  {f}")
        for u in r["urls"]:
            print(f"  url   {u['url']}  ({u['title']})")
        for g in r["unmatched"]:
            any_unmatched = True
            print(f"  UNMATCHED GLOB  {g}")
        if not (r["files"] or r["urls"]):
            print("  (no sources resolved)")
        print()

    names = [r["name"] for r in resolved]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        print(f"ERROR: duplicate topic name(s): {', '.join(dupes)}", file=sys.stderr)
        return 1
    return 1 if any_unmatched else 0


if __name__ == "__main__":
    sys.exit(main())
