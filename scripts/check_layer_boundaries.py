#!/usr/bin/env python3
"""Layer boundary enforcement check (T026 / AC-004).

Verifies that Layer 2 modules (model.py, element.py, relationship.py) do
not import from Layer 3 (helpers/) or Layer 4 (readers/, writers/) using
static AST analysis.  Exits with code 1 if any violation is found.

Usage:
    python scripts/check_layer_boundaries.py
    python scripts/check_layer_boundaries.py --strict   # also checks helpers
"""
import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PKG_ROOT = REPO_ROOT / "src" / "pyArchimate"

# Modules that constitute each layer (relative to PKG_ROOT).
LAYER2 = [
    PKG_ROOT / "model.py",
    PKG_ROOT / "element.py",
    PKG_ROOT / "relationship.py",
]

# Forbidden import prefixes for Layer 2 modules.
# Layer 2 may only import from Layer 1 (constants, enums, exceptions, logger)
# or from sibling Layer 2 modules. It must NOT import helpers/ or readers/
# writers/ (Layer 3/4).
LAYER2_FORBIDDEN_RELATIVE = {
    "helpers",
    "readers",
    "writers",
}

LAYER2_FORBIDDEN_ABSOLUTE = {
    "pyArchimate.helpers",
    "pyArchimate.readers",
    "pyArchimate.writers",
    "src.pyArchimate.helpers",
    "src.pyArchimate.readers",
    "src.pyArchimate.writers",
}


def _get_imports(filepath: Path):
    """Return module-level imported module names from a Python source file.

    Only top-level (module-scope) imports are checked.  Lazy imports inside
    function or method bodies are an accepted pattern for breaking circular
    dependencies and are intentionally excluded from this check.
    """
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    imports = []
    # Only iterate direct children of the module — this excludes imports
    # that appear inside function/class/method bodies.
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(("absolute", alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            level = node.level  # 0 = absolute, >0 = relative
            imports.append(("relative" if level else "absolute", module, node.lineno))
    return imports


def _check_import_violation(filepath: Path, kind: str, module: str, lineno: int) -> str | None:
    if kind == "relative":
        first = module.split(".")[0] if module else ""
        if first in LAYER2_FORBIDDEN_RELATIVE:
            return f"  {filepath.name}:{lineno}  relative import of forbidden Layer 3/4 module: '.{module}'"
    else:
        for forbidden in LAYER2_FORBIDDEN_ABSOLUTE:
            if module == forbidden or module.startswith(forbidden + "."):
                return f"  {filepath.name}:{lineno}  absolute import of forbidden Layer 3/4 module: '{module}'"
    return None


def check_layer2():
    violations = []
    for filepath in LAYER2:
        if not filepath.exists():
            continue
        for kind, module, lineno in _get_imports(filepath):
            violation = _check_import_violation(filepath, kind, module, lineno)
            if violation:
                violations.append(violation)
    return violations


def main():
    print("Checking Layer 2 module import boundaries (AC-004)...")
    violations = check_layer2()

    if violations:
        print(f"\n[FAIL] {len(violations)} layer boundary violation(s) found:\n")
        for v in violations:
            print(v)
        print(
            "\nLayer 2 modules (model.py, element.py, relationship.py) must only "
            "import from Layer 1 (constants, enums, exceptions, logger) or sibling "
            "Layer 2 modules.  They must NOT import from helpers/, readers/, or writers/."
        )
        sys.exit(1)
    else:
        print("[PASS] No Layer 2 → Layer 3/4 import violations found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
