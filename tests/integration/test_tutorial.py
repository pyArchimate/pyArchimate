"""Integration tests for docs/tutorial.md code examples (FR-014).

Extracts all Python fenced code blocks from the tutorial and executes each
one, asserting that none raise an exception. Blocks run in isolated namespaces
so they do not share state.
"""
import re
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TUTORIAL_PATH = _REPO_ROOT / "docs" / "tutorial.md"


def _extract_python_blocks(text: str) -> list[str]:
    return re.findall(r"```python\n(.*?)```", text, re.DOTALL)


def _tutorial_blocks() -> list[tuple[int, str]]:
    content = _TUTORIAL_PATH.read_text(encoding="utf-8")
    return list(enumerate(_extract_python_blocks(content), start=1))


@pytest.mark.parametrize("index,block", _tutorial_blocks())
def test_tutorial_code_block(index: int, block: str, tmp_path: Path) -> None:
    """Each Python block in docs/tutorial.md must execute without raising."""
    namespace: dict = {
        "__builtins__": __builtins__,
        "tmp_path": tmp_path,
    }
    sys.path.insert(0, str(_REPO_ROOT / "src"))
    try:
        exec(compile(block, f"tutorial_block_{index}", "exec"), namespace)  # noqa: S102
    finally:
        if str(_REPO_ROOT / "src") in sys.path:
            sys.path.remove(str(_REPO_ROOT / "src"))
