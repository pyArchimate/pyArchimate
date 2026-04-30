"""Security tests: verify no credentials are hard-coded in scripts (FR-010, T015)."""
import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"

_HARDCODED_PATTERNS = [
    r"sk-ant-[A-Za-z0-9\-_]{20,}",
    r'ANTHROPIC_API_KEY\s*=\s*["\'][^"\']{10,}["\']',
]


def test_no_hardcoded_credentials_in_generate_script() -> None:
    script = (_SCRIPTS_DIR / "generate_ai_docs.py").read_text(encoding="utf-8")
    for pattern in _HARDCODED_PATTERNS:
        assert not re.search(pattern, script), (
            f"Potential hardcoded credential matching {pattern!r}"
        )
