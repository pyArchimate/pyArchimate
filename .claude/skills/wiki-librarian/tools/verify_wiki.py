"""Verify the generated wiki is structurally sound and honest about its sources.

Run at the end of every librarian run, alongside build_status.py:

    python tools/verify_wiki.py

Exit code is 0 when clean, 1 when there is at least one ERROR.

The wiki is a derived cache. build_status.py answers "is a page stale?"; this
answers the other seam -- "does what got generated hang together?":

ERROR   a topic in sources.yaml has no page file
ERROR   a page file exists for no topic (and is not index.md)
ERROR   a topic page is not linked from wiki/index.md
ERROR   a repo-file citation on a page points at a path that does not exist
ERROR   .build-log.yaml lists a topic that sources.yaml does not (orphan)
ERROR   .build-log.yaml has no entry for a topic that has a page
REVIEW  a page has no citations at all (synthesis with nothing cited)
REVIEW  a page frontmatter lists a source not in the topic's resolved set
REVIEW  a URL cache file on disk that no topic references
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
from typing import Any

import wiki_common as wc

# (level, name, detail) -- level is "ERROR" or "REVIEW".
Finding = tuple[str, str, str]


def _read(path: str) -> str:
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _frontmatter_sources(text: str) -> list[str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return []
    import yaml

    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return []
    out = []
    for s in fm.get("sources") or []:
        out.append(re.sub(r"\s*\(retrieved.*?\)\s*$", "", str(s)).strip())
    return out


def check_topic_page_log(resolved: dict[str, Any], pages: dict[str, Any], log_topics: dict[str, Any]) -> list[Finding]:
    found: list[Finding] = []
    for name in resolved:
        if name not in pages:
            found.append(("ERROR", name, "topic has no page file wiki/%s.md" % name))
        elif name not in log_topics:
            found.append(("ERROR", name, "page exists but no .build-log.yaml entry"))
    for name in pages:
        if name not in resolved:
            found.append(("ERROR", name, "page wiki/%s.md has no topic in sources.yaml" % name))
    for name in log_topics:
        if name not in resolved:
            found.append(("ERROR", name, "in .build-log.yaml but not sources.yaml (orphan)"))
    return found


def check_index_links(resolved: dict[str, Any], pages: dict[str, Any]) -> list[Finding]:
    index_text = _read(wc.INDEX_FILE) if os.path.isfile(wc.INDEX_FILE) else ""
    linked = set(re.findall(r"\]\(\s*([A-Za-z0-9._-]+)\.md\s*\)", index_text))
    return [
        ("ERROR", name, "not linked from wiki/index.md") for name in resolved if name in pages and name not in linked
    ]


def check_page(name: str, path: str, resolved: dict[str, Any]) -> list[Finding]:
    found: list[Finding] = []
    text = _read(path)
    cites = wc.CITE_FILE_RE.findall(text)
    if name in resolved and not cites:
        found.append(("REVIEW", name, "page has no repo-file citations"))
    for rel in sorted(set(cites)):
        if not os.path.isfile(rel):
            found.append(("ERROR", name, "citation points at missing path: %s" % rel))
    if name in resolved:
        declared_ok = set(resolved[name]["files"]) | {u["url"] for u in resolved[name]["urls"]}
        for s in _frontmatter_sources(text):
            if s not in declared_ok:
                found.append(("REVIEW", name, "frontmatter source not in resolved set: %s" % s))
    return found


def check_stray_caches(resolved: dict[str, Any]) -> list[Finding]:
    if not os.path.isdir(wc.CACHE_DIR):
        return []
    referenced = {wc.url_cache_path(u["url"]) for r in resolved.values() for u in r["urls"]}
    found: list[Finding] = []
    for f in sorted(os.listdir(wc.CACHE_DIR)):
        p = os.path.join(wc.CACHE_DIR, f)
        if p not in referenced:
            found.append(("REVIEW", "(cache)", "unreferenced URL cache file: %s" % p))
    return found


def collect_findings() -> list[Finding]:
    resolved = {r["name"]: r for r in wc.resolve_all()}
    log_topics = wc.load_build_log().get("topics") or {}
    pages = {os.path.basename(p)[:-3]: p for p in wc.iter_wiki_pages()}

    found = check_topic_page_log(resolved, pages, log_topics)
    found += check_index_links(resolved, pages)
    for name, path in pages.items():
        found += check_page(name, path, resolved)
    found += check_stray_caches(resolved)

    counts = (len(resolved), len(pages), len(log_topics))
    print("topics: %d   pages: %d   build-log entries: %d" % counts)
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", help="repo root (dir holding wiki/); default: $WIKI_ROOT or the current directory")
    args = ap.parse_args()
    wc.apply_root(args.root)

    if not os.path.isdir(wc.WIKI_DIR):
        print("no wiki/ -- run from the repo root", file=sys.stderr)
        return 1

    found = collect_findings()
    errors = [f for f in found if f[0] == "ERROR"]
    reviews = [f for f in found if f[0] == "REVIEW"]

    print("=" * 72)
    print("ERRORS: %d     REVIEW: %d" % (len(errors), len(reviews)))
    print("=" * 72)
    for level, name, detail in errors + reviews:
        print("  %-6s %-22s %s" % (level, name, detail))
    if not found:
        print("  every topic has a linked page, and every citation resolves")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
