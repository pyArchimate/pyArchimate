#!/usr/bin/env python3
"""Generate or regenerate AI.md using the claude code CLI.

Run: python scripts/generate_ai_docs.py
Prerequisites: claude CLI in PATH, ANTHROPIC_API_KEY set in environment.
See scripts/README.md for full usage instructions (FR-008).
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AI_MD_PATH = REPO_ROOT / "AI.md"
DOCS_DIR = REPO_ROOT / "docs"
CLAUDE_TIMEOUT = 300  # seconds — SC-003: must complete within 5 minutes

_NOT_MODIFIED = "AI.md was NOT modified."

REQUIRED_SECTIONS = [
    "Summary",
    "Overview",
    "Core Purpose",
    "Conceptual Model",
    "Features",
    "Use Cases",
    "Strengths",
    "Limitations",
    "Non-Conformances",
]


def get_api_key() -> str:
    """Return ANTHROPIC_API_KEY from environment if set, else empty string.

    Not required when running inside an authenticated Claude Code session —
    the claude CLI uses its own stored credentials in that case.
    """
    return os.environ.get("ANTHROPIC_API_KEY", "")


def build_context() -> str:
    """Collect docs/ markdown files as context string for claude (T006)."""
    parts: list[str] = []
    if DOCS_DIR.exists():
        for md_file in sorted(DOCS_DIR.glob("**/*.md")):
            parts.append(f"## {md_file.name}\n\n{md_file.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(parts) if parts else "(No documentation found in docs/.)"


def validate_markdown_structure(content: str) -> list[str]:
    """Return list of missing required section names (FR-012)."""
    headers = re.findall(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)
    headers_lower = [h.strip().lower() for h in headers]
    return [s for s in REQUIRED_SECTIONS if not any(s.lower() in h for h in headers_lower)]


def validate_markdown_syntax(content: str) -> bool:
    """Run pymarkdownlnt scan on content; return True if no errors (FR-012)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp_path = f.name
    try:
        result = subprocess.run(
            ["pymarkdown", "scan", tmp_path],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def run_claude(prompt: str) -> str:
    """Invoke claude CLI with prompt; raise RuntimeError on failure (FR-007)."""
    env = {**os.environ}
    key = get_api_key()
    if key:
        env["ANTHROPIC_API_KEY"] = key
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        env=env,
        timeout=CLAUDE_TIMEOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude exited {result.returncode}: {result.stderr.strip()}")
    if not result.stdout.strip():
        raise RuntimeError("claude returned empty output")
    return result.stdout


def generate_ai_md() -> None:
    """Orchestrate generation: build context → call claude → validate → write (FR-007, FR-012)."""
    context = build_context()
    sections = ", ".join(REQUIRED_SECTIONS)
    prompt = (
        "Generate a structured AI.md file for the pyArchimate Python library. "
        f"It MUST contain these top-level # headings: {sections}. "
        "No conversational language, filler phrases, or first-person narrative. "
        f"Base content strictly on this documentation:\n\n{context}"
    )

    print("Invoking claude to generate AI.md...")
    try:
        content = run_claude(prompt)
    except RuntimeError as exc:
        print(f"ERROR: Generation failed — {exc}", file=sys.stderr)
        print(_NOT_MODIFIED, file=sys.stderr)
        sys.exit(1)

    missing = validate_markdown_structure(content)
    if missing:
        print(f"ERROR: Output missing required sections: {missing}", file=sys.stderr)
        print(_NOT_MODIFIED, file=sys.stderr)
        sys.exit(1)

    if not validate_markdown_syntax(content):
        print("ERROR: Output failed Markdown syntax validation.", file=sys.stderr)
        print(_NOT_MODIFIED, file=sys.stderr)
        sys.exit(1)

    AI_MD_PATH.write_text(content, encoding="utf-8")
    print(f"✓ AI.md updated at {AI_MD_PATH}")


if __name__ == "__main__":
    generate_ai_md()
