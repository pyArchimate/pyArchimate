#!/usr/bin/env python
"""Local semantic search over the generated wiki and its source files.

Everything runs on this machine: fastembed (ONNX, no PyTorch) with
bge-small-en-v1.5, vectors in a local SQLite file. Nothing is sent anywhere.

Run from the repo root (the dir holding wiki/), or pass --root / set
$WIKI_ROOT:

    python tools/semsearch.py index                    # index wiki/ (default)
    python tools/semsearch.py index --scope all        # wiki/ + source files
    python tools/semsearch.py search "how are profiles resolved"
    python tools/semsearch.py search "auth middleware" --scope sources -k 10

Scopes: `wiki` (generated pages + URL caches), `sources` (every repo file any
topic in sources.yaml pulls), `all`.

Semantic search complements Grep, it does not replace it. Use Grep for names,
paths and symbols; use this for "where is the thing that does X" when you
don't know the wording. Results are candidates to read and judge, not
answers -- small embedding models are weak on direction and negation.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import cast

import wiki_common as wc

MODEL = "BAAI/bge-small-en-v1.5"
DIM = 384

# fastembed + numpy are deliberately NOT Poetry dependencies: fastembed has
# never shipped a release whose pillow requirement reaches 13.0 (every
# version through 0.9.1 caps it at <13.0), which conflicts with pyarchimate
# >=2.0.0's pillow>=13.0.0 floor (needed to clear the Pillow CVEs tracked in
# fix(security) commits around 2026-10-25) once both sit in the same unified
# Poetry dependency graph. Rather than block that security fix on fastembed
# publishing a compatible release, this tool manages a private package
# directory of its own for just these two packages, built lazily on first
# use via `pip install --target` (no separate venv/interpreter -- avoids
# needing `ensurepip`, which fails under this workspace's drvfs mount). See
# wiki-librarian/SKILL.md "Semantic search deps".
_TOOLS_DIR = Path(__file__).resolve().parent
_ISOLATED_DEPS_DIR = _TOOLS_DIR / ".venv" / f"py{sys.version_info.major}{sys.version_info.minor}-site-packages"
_ISOLATED_PACKAGES = ("fastembed>=0.7,<0.9", "numpy>=1.24")


def _ensure_isolated_deps() -> None:
    """Make `fastembed`/`numpy` importable, pip-installing them into a
    private directory under `tools/.venv` (gitignored, matches the repo's
    `.venv` pattern) the first time this runs, keyed to the running
    interpreter's version so it's always binary-compatible, then extending
    `sys.path` with it.

    Installs into a fresh staging directory and swaps it into place with a
    single `rename` only once pip exits 0, then drops a marker inside the
    final directory -- a run that's killed mid-install (Ctrl-C, a CI
    timeout) leaves the staging dir behind as debris, never a half-installed
    final dir that a later run's `pip install --target` (which does not
    overwrite existing files) would silently leave mismatched.
    """
    marker = _ISOLATED_DEPS_DIR / ".deps-installed"
    if not marker.exists():
        print("semsearch: installing fastembed/numpy into tools/.venv (first run only)...", file=sys.stderr)
        venv_root = _ISOLATED_DEPS_DIR.parent
        venv_root.mkdir(parents=True, exist_ok=True)
        staging = venv_root / f"{_ISOLATED_DEPS_DIR.name}.staging"
        shutil.rmtree(staging, ignore_errors=True)
        staging.mkdir(parents=True)
        # pip builds packages under $TMPDIR, then renames into --target. On a
        # drvfs/9p workspace mount the default /tmp is a different device, so
        # that rename fails with "Invalid cross-device link". Staging under
        # the target's own tree keeps both on the same filesystem.
        pip_tmp = venv_root / "tmp"
        pip_tmp.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, TMPDIR=str(pip_tmp))
        pip_cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "--target",
            str(staging),
            *_ISOLATED_PACKAGES,
        ]
        try:
            try:
                subprocess.run(pip_cmd, check=True, env=env)
            except subprocess.CalledProcessError:
                # Some sandboxed/drvfs workspace mounts report every path as
                # 0777 owned by the invoking user but still reject the
                # chmod/rename pip's atomic installed-file writes do; retry
                # under sudo, which sidesteps that UID-mapping check. No-op
                # elsewhere -- if `sudo` isn't available or passwordless,
                # this just raises the original-shaped error again.
                if shutil.which("sudo") is None:
                    raise
                subprocess.run(["sudo", "-E", *pip_cmd], check=True, env=env)
            (staging / ".deps-installed").write_text("ok\n", encoding="utf-8")
            shutil.rmtree(_ISOLATED_DEPS_DIR, ignore_errors=True)
            staging.rename(_ISOLATED_DEPS_DIR)
        finally:
            shutil.rmtree(pip_tmp, ignore_errors=True)
            shutil.rmtree(staging, ignore_errors=True)
    if str(_ISOLATED_DEPS_DIR) not in sys.path:
        sys.path.insert(0, str(_ISOLATED_DEPS_DIR))


# bge-small on CPU embeds real-length chunks at only ~1.5/s per process on a
# typical dev box, so `index --scope all` (~750 chunks) is an ~8-minute job
# single-process. fastembed can fan that out across worker *processes*
# (`parallel=N`), but each worker reloads the full ONNX model (~0.7 GB
# resident), so an unbounded fan-out OOM-kills a memory-capped container.
# `_pick_workers()` sizes the pool to free RAM and core count; override with
# $SEMSEARCH_PARALLEL (1 = force in-process; 0 = all cores, fastembed's rule).
EMBED_BATCH = int(os.environ.get("SEMSEARCH_EMBED_BATCH", "32"))

# Measured peak RSS of one fastembed worker at EMBED_BATCH<=32. Override with
# $SEMSEARCH_WORKER_MB if your model or batch size differs.
WORKER_RSS = int(os.environ.get("SEMSEARCH_WORKER_MB", "750")) * 1024 * 1024


def _available_bytes() -> int:
    """Best-effort free memory: cgroup hard limit headroom if capped, else the
    host's MemAvailable. 0 means 'could not tell' (caller falls back to 1 worker)."""
    try:  # cgroup v2
        cap = Path("/sys/fs/cgroup/memory.max").read_text().strip()
        if cap != "max":
            used = int(Path("/sys/fs/cgroup/memory.current").read_text())
            return max(0, int(cap) - used)
    except (OSError, ValueError):
        pass  # not cgroup v2 (or unreadable) -- fall through to the v1 check
    try:  # cgroup v1
        cap_v1 = int(Path("/sys/fs/cgroup/memory/memory.limit_in_bytes").read_text())
        if cap_v1 < (1 << 62):
            used = int(Path("/sys/fs/cgroup/memory/memory.usage_in_bytes").read_text())
            return max(0, cap_v1 - used)
    except (OSError, ValueError):
        pass  # not cgroup v1 either -- fall through to the uncapped-host reading
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) * 1024
    except OSError:
        pass  # /proc/meminfo unreadable (non-Linux, sandboxed) -- caller uses 1 worker
    return 0


def _pick_workers(n_chunks: int) -> int:
    """Fastembed worker count: min of core count, RAM budget (60% of free /
    per-worker RSS), and 'enough batches to be worth a fork'. $SEMSEARCH_PARALLEL
    overrides (passed straight to fastembed: 1 forces in-process, 0 = all cores)."""
    override = os.environ.get("SEMSEARCH_PARALLEL")
    if override is not None:
        return max(0, int(override))
    cores = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else (os.cpu_count() or 1)
    avail = _available_bytes()
    by_mem = int(avail * 0.6 // WORKER_RSS) if avail else 1
    by_work = -(-n_chunks // (EMBED_BATCH * 4))  # want each worker to get a few batches
    return max(1, min(cores, by_mem or 1, by_work))


def _default_root() -> Path:
    """Knowledge-base root: the directory containing wiki/ and raw/.

    Defaults to the current working directory -- the same convention the
    publish/verify tools use -- and is overridable with --root or $WIKI_ROOT.
    The root is deliberately NOT inferred from this file's location, so the
    tools can be bundled in a skill directory separate from the corpus.
    """
    env = os.environ.get("WIKI_ROOT")
    if not env:
        return Path.cwd()
    resolved = Path(env).expanduser().resolve()
    if not resolved.is_dir():
        raise SystemExit(f"$WIKI_ROOT does not point to an existing directory: {env!r}")
    return resolved


REPO = _default_root()
DB_PATH = REPO / "index.sqlite"

# Keep the ~80 MB model cache out of the repo / any synced folder.
CACHE_DIR = Path(
    os.environ.get("SEMSEARCH_CACHE") or Path(os.environ.get("LOCALAPPDATA", Path.home() / ".cache")) / "fastembed"
)

# Target chunk size in words. Small enough that a hit points at something
# specific, large enough to carry context.
TARGET_WORDS = 220
MAX_WORDS = 330


# --------------------------------------------------------------------------
# chunking
# --------------------------------------------------------------------------


class Chunk:
    __slots__ = ("path", "start_line", "end_line", "heading", "text")

    def __init__(self, path: str, start_line: int, end_line: int, heading: str, text: str):
        self.path = path
        self.start_line = start_line
        self.end_line = end_line
        self.heading = heading
        self.text = text

    def embed_text(self) -> str:
        """Heading path is prepended so dates and topic land in the vector."""
        return f"{self.heading}\n\n{self.text}" if self.heading else self.text


def _split_long(lines: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    """Split an oversized run of (lineno, text), preferring blank-line
    boundaries but never letting a chunk grow past MAX_WORDS regardless.

    A section that runs long with no blank line in it at all -- a heading
    followed by many consecutive one-line dated bullets, no blank line
    between them, which is exactly the shape a wiki page has right before
    it's large enough to need archiving -- used to accumulate without limit,
    since the only split point this checked for was a blank line.
    """
    out: list[list[tuple[int, str]]] = []
    cur: list[tuple[int, str]] = []
    words = 0
    for lineno, line in lines:
        n = len(line.split())
        if cur and words + n > MAX_WORDS and not line.strip():
            out.append(cur)
            cur, words = [], 0
            continue
        cur.append((lineno, line))
        words += n
        if (words >= TARGET_WORDS and not line.strip()) or words >= MAX_WORDS:
            out.append(cur)
            cur, words = [], 0
    if cur:
        out.append(cur)
    return [c for c in out if any(ln.strip() for _, ln in c)]


def chunk_markdown(path: Path) -> list[Chunk]:  # noqa: C901 - one linear heading-stack walk
    """One chunk per ##/### section, oversized sections split by paragraph.

    The heading stack is carried onto every chunk, so a chunk split out of
    '## 2023-12-09 -- Perceived double standards' keeps that date attached.
    """
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    rel = path.relative_to(REPO).as_posix()

    start = 0
    # Skip YAML frontmatter, it is metadata not prose.
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break

    title = ""
    stack: dict[int, str] = {}
    sections: list[tuple[str, list[tuple[int, str]]]] = []
    cur: list[tuple[int, str]] = []
    cur_heading = ""

    for i in range(start, len(lines)):
        line = lines[i]
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1:
                title = text
                stack = {}
                continue
            if cur:
                sections.append((cur_heading, cur))
                cur = []
            stack[level] = text
            for lvl in list(stack):
                if lvl > level:
                    del stack[lvl]
            parts = [title] + [stack[k] for k in sorted(stack)]
            cur_heading = " > ".join(p for p in parts if p)
            continue
        cur.append((i + 1, line))

    if cur:
        sections.append((cur_heading, cur))

    chunks: list[Chunk] = []
    for heading, body in sections:
        if not any(ln.strip() for _, ln in body):
            continue
        for piece in _split_long(body):
            text = "\n".join(ln for _, ln in piece).strip()
            if not text:
                continue
            chunks.append(Chunk(rel, piece[0][0], piece[-1][0], heading or title, text))
    return chunks


# Date forms seen in raw/: chat-export timestamps, chat day headers,
# and plain dated log notes.
_MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|"
    "November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)
DATE_PATTERNS = [
    re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s+\d{1,2}:\d{2}"),  # 2/1/25, 4:27 pm -
    re.compile(rf"^-{{2,}}\s*(?:\w+day,\s*)?(\d{{1,2}}\s+(?:{_MONTHS})\s+\d{{4}})\s*-{{2,}}", re.I),
    re.compile(rf"^(\d{{1,2}}\s+(?:{_MONTHS})\s+\d{{4}})\s*$", re.I),  # 15 Nov 2024
    re.compile(r"^(\d{4}-\d{2}-\d{2})\s*$"),
]


def _sniff_date(line: str) -> str | None:
    for pat in DATE_PATTERNS:
        m = pat.match(line.strip())
        if m:
            return m.group(1)
    return None


def chunk_plaintext(path: Path) -> list[Chunk]:  # noqa: C901 - one linear line walk with flush()
    """Word-count windows over a raw note, labelled with the dates they span.

    Raw notes have no headings, so the date range seen inside the window is
    used as the heading equivalent -- that is what makes a hit locatable and
    what lets the librarian tell covered material from new.
    """
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    rel = path.relative_to(REPO).as_posix()

    chunks: list[Chunk] = []
    cur: list[str] = []
    cur_start = 1
    words = 0
    first_date: str | None = None
    last_date: str | None = None
    carried: str | None = None  # last date seen anywhere earlier in the file

    def flush(end_line: int) -> None:
        nonlocal cur, words, first_date, last_date, cur_start, carried
        text = "\n".join(cur).strip()
        if text:
            # A window may contain no date line of its own (long chat day,
            # multi-paragraph journal entry). Inherit the previous window's date
            # rather than emitting an undated chunk -- an undated hit cannot be
            # checked against coverage.ranges.
            start = first_date or carried
            span = [d for d in (start, last_date) if d]
            label = path.stem
            if span:
                uniq = list(dict.fromkeys(span))
                label = f"{label} ({' to '.join(uniq)})"
                if not first_date:
                    label += " [date carried forward]"
            chunks.append(Chunk(rel, cur_start, end_line, label, text))
        if last_date:
            carried = last_date
        cur, words = [], 0
        first_date = last_date = None
        cur_start = end_line + 1

    for i, line in enumerate(lines, start=1):
        d = _sniff_date(line)
        # Prefer breaking on a date boundary once the window is full enough --
        # but break *before* folding this line's date into the window. Applying
        # it first labels the chunk being flushed with a date whose content
        # starts in the next chunk, and that label is what gets checked against
        # a sidecar's coverage.ranges, so an over-claimed end date can make the
        # librarian skip genuinely new material.
        if words >= TARGET_WORDS and (d or not line.strip()):
            flush(i - 1)
        if d:
            last_date = d
            if first_date is None:
                first_date = d
        cur.append(line)
        words += len(line.split())
        if words >= MAX_WORDS:
            flush(i)

    flush(len(lines))
    return chunks


def collect(scope: str) -> list[Path]:
    paths: list[Path] = []
    if scope in ("wiki", "all"):
        paths += sorted((REPO / "wiki").glob("*.md"))
        cache = REPO / "wiki" / ".cache"
        if cache.is_dir():
            paths += sorted(cache.glob("*.md"))
    if scope in ("sources", "all"):
        for rel in wc.all_source_files():
            p = REPO / rel
            if p.is_file():
                paths.append(p)
    seen: set[Path] = set()
    out: list[Path] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def chunk_file(path: Path) -> list[Chunk]:
    return chunk_markdown(path) if path.suffix == ".md" else chunk_plaintext(path)


# --------------------------------------------------------------------------
# storage
# --------------------------------------------------------------------------


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            digest TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            heading TEXT,
            text TEXT NOT NULL,
            vector BLOB NOT NULL
        );
        CREATE INDEX IF NOT EXISTS chunks_path ON chunks(path);
        """
    )
    return db


def digest_of(path: Path) -> str:
    return wc.sha256_file(str(path))


def load_model():
    _ensure_isolated_deps()
    from fastembed import TextEmbedding  # isolated venv, see _ensure_isolated_deps

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return TextEmbedding(model_name=MODEL, cache_dir=str(CACHE_DIR))


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------


def _needs_index(path: Path, rel: str, digest: str, known: dict[str, str], chunked: set[str], force: bool) -> bool:
    """A file needs embedding when forced, new, changed, or recorded with no chunks
    even though it has content -- what an interrupted run under the old ordering left
    behind, and which a digest comparison alone would call up to date."""
    if force or known.get(rel) != digest:
        return True
    return rel not in chunked and bool(chunk_file(path))


def _clear_for_reindex(db: sqlite3.Connection, todo: list[tuple[Path, str]], all_chunks: list[Chunk]) -> None:
    """Forget every changed file before embedding starts, so one that an interrupted
    run leaves incomplete has no digest and is picked up by the next run. A file with
    no chunks to embed is complete already, so its digest goes straight back in."""
    has_chunks = {c.path for c in all_chunks}
    for p, d in todo:
        rel = p.relative_to(REPO).as_posix()
        db.execute("DELETE FROM chunks WHERE path = ?", (rel,))
        db.execute("DELETE FROM files WHERE path = ?", (rel,))
        if rel not in has_chunks:
            db.execute("INSERT INTO files(path, digest) VALUES(?, ?)", (rel, d))
    db.commit()


def _store_embedded(
    db: sqlite3.Connection, chunks: list[Chunk], vectors: Iterable[bytes], digests: dict[str, str]
) -> None:
    """Write embedded `chunks`, committing every EMBED_BATCH rows so an interrupted run
    keeps its progress. A file's digest is recorded only with its last chunk: the digest
    is what marks a file as done, so it must never exist ahead of the chunks it vouches
    for. `digests` maps each repo-relative path to its digest."""
    remaining = Counter(c.path for c in chunks)
    done = 0
    for c, vector in zip(chunks, vectors, strict=True):
        db.execute(
            "INSERT INTO chunks(path, start_line, end_line, heading, text, vector) VALUES(?,?,?,?,?,?)",
            (c.path, c.start_line, c.end_line, c.heading, c.text, vector),
        )
        remaining[c.path] -= 1
        if remaining[c.path] == 0:
            db.execute("INSERT INTO files(path, digest) VALUES(?, ?)", (c.path, digests[c.path]))
        done += 1
        if done % EMBED_BATCH == 0:
            db.commit()
            print(f"  {done}/{len(chunks)} chunks embedded", file=sys.stderr)
    db.commit()


def cmd_index(args: argparse.Namespace) -> int:
    _ensure_isolated_deps()
    import numpy as np  # isolated venv, see _ensure_isolated_deps

    paths = collect(args.scope)
    if not paths:
        print(f"no files found for scope '{args.scope}'", file=sys.stderr)
        return 1

    db = connect()
    known = dict(db.execute("SELECT path, digest FROM files").fetchall())
    chunked = {row[0] for row in db.execute("SELECT DISTINCT path FROM chunks")}

    todo: list[tuple[Path, str]] = []
    for p in paths:
        d = digest_of(p)
        rel = p.relative_to(REPO).as_posix()
        if _needs_index(p, rel, d, known, chunked, args.force):
            todo.append((p, d))

    # Drop chunks for files that no longer exist on disk.
    live = {p.relative_to(REPO).as_posix() for p in collect("all")}
    for rel in set(known) - live:
        db.execute("DELETE FROM chunks WHERE path = ?", (rel,))
        db.execute("DELETE FROM files WHERE path = ?", (rel,))

    if not todo:
        db.commit()
        total = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        print(f"up to date -- {total} chunks, {len(known)} files, nothing to re-embed")
        return 0

    all_chunks: list[Chunk] = []
    for p, _ in todo:
        all_chunks.extend(chunk_file(p))

    _clear_for_reindex(db, todo, all_chunks)

    workers = _pick_workers(len(all_chunks))
    # fastembed quirk: parallel=1 still forks one worker (model reload, no gain),
    # so map "1 worker" onto parallel=None, which embeds in this process.
    parallel = None if workers == 1 else workers
    pool_desc = "in-process" if parallel is None else f"{'all-core' if parallel == 0 else parallel} workers"
    print(
        f"embedding {len(all_chunks)} chunks from {len(todo)} changed file(s) using {MODEL} "
        f"(local, {pool_desc}, batch={EMBED_BATCH})...",
        file=sys.stderr,
    )
    model = load_model()
    embedded = model.embed([c.embed_text() for c in all_chunks], batch_size=EMBED_BATCH, parallel=parallel)

    def normalized(vectors: Iterable[object]) -> Iterable[bytes]:
        for raw in vectors:
            v = np.asarray(raw, dtype=np.float32)
            v /= np.linalg.norm(v) or 1.0
            yield v.tobytes()

    digests = {p.relative_to(REPO).as_posix(): d for p, d in todo}
    _store_embedded(db, all_chunks, normalized(embedded), digests)

    total = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    files = db.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    print(f"indexed {len(all_chunks)} chunks from {len(todo)} file(s); {total} chunks across {files} files total")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    _ensure_isolated_deps()
    import numpy as np  # isolated venv, see _ensure_isolated_deps (mypy already covered this module above)

    if not DB_PATH.exists():
        print("no index yet -- run: python tools/semsearch.py index", file=sys.stderr)
        return 1

    db = connect()
    sql = "SELECT path, start_line, end_line, heading, text, vector FROM chunks"
    params: tuple[str, ...] = ()
    if args.scope == "wiki":
        sql += " WHERE path LIKE 'wiki/%'"
    elif args.scope == "sources":
        sql += " WHERE path NOT LIKE 'wiki/%'"
    if args.path:
        sql += (" AND" if "WHERE" in sql else " WHERE") + " path LIKE ?"
        params = (f"%{args.path}%",)

    rows = db.execute(sql, params).fetchall()
    if not rows:
        print("index is empty for that scope -- run index first", file=sys.stderr)
        return 1

    model = load_model()
    # bge is asymmetric: query_embed applies the required query prefix that
    # passages must NOT have. Using embed() here quietly degrades results.
    qv = np.asarray(next(iter(model.query_embed(args.query))), dtype=np.float32)
    qv /= np.linalg.norm(qv) or 1.0

    mat = np.frombuffer(b"".join(r[5] for r in rows), dtype=np.float32).reshape(len(rows), DIM)
    scores = mat @ qv
    order = np.argsort(-scores)[: args.k]

    for rank, i in enumerate(order, start=1):
        path, s, e, heading, text, _ = rows[i]
        score = float(scores[i])
        if score < args.min_score:
            continue
        snippet = " ".join(text.split())
        if len(snippet) > args.snippet:
            snippet = snippet[: args.snippet].rstrip() + "..."
        print(f"{rank}. {score:.3f}  {path}:{s}-{e}")
        if heading:
            print(f"   [{heading}]")
        print(f"   {snippet}\n")
    return 0


def main() -> int:
    # Wiki headings are full of em-dashes; the default Windows console codepage
    # turns them into replacement chars, which corrupts any anchor slug built
    # from this output.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--root",
        help="knowledge-base root (dir containing wiki/ and raw/); defaults to $WIKI_ROOT or the current directory",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("index", help="build or refresh the local index")
    pi.add_argument("--scope", choices=["wiki", "sources", "all"], default="wiki")
    pi.add_argument("--force", action="store_true", help="re-embed unchanged files too")
    pi.set_defaults(func=cmd_index)

    ps = sub.add_parser("search", help="semantic nearest-neighbour search")
    ps.add_argument("query")
    ps.add_argument("--scope", choices=["wiki", "sources", "all"], default="all")
    ps.add_argument("--path", help="restrict to paths containing this substring")
    ps.add_argument("-k", type=int, default=8, help="number of results (default 8)")
    ps.add_argument("--min-score", type=float, default=0.0)
    ps.add_argument("--snippet", type=int, default=240)
    ps.set_defaults(func=cmd_search)

    args = ap.parse_args()

    # `--root` / `$WIKI_ROOT` chdir to the knowledge-base root; everything here
    # is CWD-relative, so re-derive REPO / DB_PATH from the (possibly new) CWD.
    global REPO, DB_PATH
    wc.apply_root(args.root)
    REPO = _default_root()
    DB_PATH = REPO / "index.sqlite"

    return cast(int, args.func(args))


if __name__ == "__main__":
    sys.exit(main())
