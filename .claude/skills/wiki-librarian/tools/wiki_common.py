"""Shared helpers for the wiki build/verify tooling.

The wiki is a derived cache. `wiki/sources.yaml` declares topics and their
sources (repo file globs + external URLs); the `wiki-librarian` skill
synthesizes one `wiki/<name>.md` page per topic; `wiki/.build-log.yaml`
fingerprints every source so a later run rebuilds only what changed. These
helpers are the one place that parses those files, computes fingerprints, and
resolves globs -- the tools duplicated their own copies once and drifted, which
is what this module exists to prevent.

All paths are relative to the current working directory, which must be the
repo root (the directory holding `wiki/`).
"""

from __future__ import annotations

import glob
import hashlib
import io
import os
import re
from typing import Any

import yaml

WIKI_DIR = "wiki"
SOURCES_FILE = os.path.join(WIKI_DIR, "sources.yaml")
BUILD_LOG = os.path.join(WIKI_DIR, ".build-log.yaml")
CACHE_DIR = os.path.join(WIKI_DIR, ".cache")
INDEX_FILE = os.path.join(WIKI_DIR, "index.md")

# Directories never worth globbing for sources or scanning for coverage.
IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".cache",
    "dist",
    "build",
    ".claude",
    "wiki",
}


def apply_root(cli_root: str | None) -> None:
    """`chdir` to an explicit knowledge-base root, if one was given.

    Every tool resolves paths relative to the current directory, which must be
    the repo root (the directory holding `wiki/`). `--root` on the CLI or
    `$WIKI_ROOT` in the environment overrides that -- and because everything is
    CWD-relative, a `chdir` is the whole of it. No-op when neither is set.

    The value is resolved (symlinks/`..` collapsed) and checked to actually be
    a directory before `chdir`, rather than handed to the OS call raw -- both
    a human `--root` typo and a value an agent constructs from other data
    should fail with a clear message, not an ambiguous OS error or a silent
    cwd change to something unexpected.
    """
    root = cli_root or os.environ.get("WIKI_ROOT")
    if not root:
        return
    resolved = os.path.realpath(os.path.expanduser(root))
    if not os.path.isdir(resolved):
        raise SystemExit(f"--root/$WIKI_ROOT does not point to an existing directory: {root!r}")
    os.chdir(resolved)


def load_yaml(path: str, default: Any = None) -> Any:
    if not os.path.exists(path):
        return default
    with io.open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or default


def load_topics() -> list[dict[str, Any]]:
    doc = load_yaml(SOURCES_FILE, {}) or {}
    return doc.get("topics") or []


def load_build_log() -> dict[str, Any]:
    return load_yaml(BUILD_LOG, {}) or {}


# --------------------------------------------------------------------------
# fingerprints
# --------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    """Hex sha256 of a file's bytes. The one place the tooling hashes a file."""
    with open(path, "rb") as fh:
        return sha256_bytes(fh.read())


def file_fingerprint(path: str) -> dict[str, Any] | None:
    """`{sha256, lines}` for a repo file, or None if it does not exist.

    `lines` counts newline-terminated lines plus a trailing partial line, so
    it matches `wc -l` + 1 for a file with no final newline -- a cheap second
    signal a human can eyeball in the build log.
    """
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as fh:
        data = fh.read()
    lines = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    return {"sha256": sha256_bytes(data), "lines": lines}


def url_cache_path(url: str) -> str:
    """Deterministic cache-file path for a URL source's fetched markdown."""
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return os.path.join(CACHE_DIR, f"{h}.md")


# --------------------------------------------------------------------------
# source resolution
# --------------------------------------------------------------------------


def _norm(p: str) -> str:
    return os.path.normpath(p).replace(os.sep, "/")


def resolve_topic(topic: dict[str, Any]) -> dict[str, Any]:
    """Expand a topic's declared sources into concrete items.

    Returns:
        {
          "name": str, "title": str, "description": str,
          "files": [rel path, ...],          # sorted, existing files only
          "urls":  [{"url", "title"}, ...],   # declaration order
          "unmatched": [glob, ...],           # path globs that matched nothing
        }
    """
    files: set[str] = set()
    urls: list[dict[str, Any]] = []
    unmatched: list[str] = []
    for src in topic.get("sources") or []:
        if not isinstance(src, dict):
            continue
        if "url" in src:
            urls.append({"url": src["url"], "title": src.get("title") or src["url"]})
            continue
        pat = src.get("path")
        if not pat:
            continue
        hits = [h for h in glob.glob(pat, recursive=True) if os.path.isfile(h)]
        if not hits:
            unmatched.append(pat)
        files.update(_norm(h) for h in hits)
    return {
        "name": topic.get("name", ""),
        "title": topic.get("title") or topic.get("name", ""),
        "description": topic.get("description", ""),
        "files": sorted(files),
        "urls": urls,
        "unmatched": sorted(set(unmatched)),
    }


def resolve_all() -> list[dict[str, Any]]:
    return [resolve_topic(t) for t in load_topics()]


def all_source_files() -> list[str]:
    """Every repo file referenced by any topic, de-duplicated and sorted."""
    seen: set[str] = set()
    for r in resolve_all():
        seen.update(r["files"])
    return sorted(seen)


def page_path(name: str) -> str:
    return os.path.join(WIKI_DIR, f"{name}.md")


# --------------------------------------------------------------------------
# build-log diffing
# --------------------------------------------------------------------------


def _diff_fingerprints(current: dict[str, str], logged: dict[str, Any], noun: str) -> list[str]:
    """Compare {key: path-to-fingerprint} against a logged {key: {sha256}} map.

    `current` maps each present source key (repo path, or URL) to the file whose
    content hash is authoritative now (the file itself, or its URL cache).
    """
    reasons: list[str] = []
    cur, old = set(current), set(logged)
    reasons += [f"{noun} added: {k}" for k in sorted(cur - old)]
    reasons += [f"{noun} removed: {k}" for k in sorted(old - cur)]
    for key in sorted(cur & old):
        fp = file_fingerprint(current[key])
        if not fp:
            reasons.append(f"{noun} content unavailable: {key}")
        elif fp["sha256"] != (logged[key] or {}).get("sha256"):
            reasons.append(f"{noun} changed: {key}")
    return reasons


def topic_status(resolved: dict[str, Any], log: dict[str, Any]) -> tuple[str, list[str]]:
    """Classify one resolved topic against the build log.

    Returns (status, reasons) where status is one of NEW, STALE, FRESH.
    ORPHAN is detected separately (log entries with no matching topic).
    """
    entry = (log.get("topics") or {}).get(resolved["name"])
    if not entry:
        return "NEW", ["no build-log entry"]

    logged = entry.get("sources") or {}
    reasons = _diff_fingerprints({p: p for p in resolved["files"]}, logged.get("files") or {}, "source")
    reasons += _diff_fingerprints(
        {u["url"]: url_cache_path(u["url"]) for u in resolved["urls"]},
        logged.get("urls") or {},
        "url",
    )
    if not os.path.isfile(page_path(resolved["name"])):
        reasons.append("page file missing")

    return ("STALE", reasons) if reasons else ("FRESH", [])


def orphan_topics(log: dict[str, Any]) -> list[str]:
    live = {t.get("name") for t in load_topics()}
    return sorted(n for n in (log.get("topics") or {}) if n not in live)


# --------------------------------------------------------------------------
# misc
# --------------------------------------------------------------------------

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# A repo-file citation: (`path/to/file.ext`...) or (`path/to/file.ext:12-34`)
CITE_FILE_RE = re.compile(r"\(`([^`\n]+?\.[A-Za-z0-9]+)(?::\d+(?:-\d+)?)?`(?:\s+[^)]*)?\)")


def iter_wiki_pages() -> list[str]:
    if not os.path.isdir(WIKI_DIR):
        return []
    return sorted(os.path.join(WIKI_DIR, f) for f in os.listdir(WIKI_DIR) if f.endswith(".md") and f != "index.md")
