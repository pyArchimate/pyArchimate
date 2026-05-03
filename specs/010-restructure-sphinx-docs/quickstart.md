# Quickstart: Restructure Sphinx Documentation

**Feature**: 010-restructure-sphinx-docs  
**Date**: 2026-05-03

## Environment Setup

```bash
# Install docs dependencies (includes myst-parser after this feature)
pip install -r docs/requirements.txt

# Or via Poetry
poetry install --with docs
```

## Build the Documentation

```bash
cd docs

# Full clean build (use this to verify zero warnings)
make clean html

# Incremental build (faster during development)
make html
```

## Verify Build Passes

```bash
cd docs
make clean html 2>&1 | grep -E "WARNING|ERROR|error" | grep -v "duplicate.*pyarchimate"
# Expected: (no output — zero warnings)
```

## View the Built Docs

```bash
# macOS
open docs/_build/html/index.html

# Linux
xdg-open docs/_build/html/index.html
```

## Check Specific Issues

```bash
# Check for broken :doc: references
make html 2>&1 | grep "undefined label\|unknown document"

# Check for pages not in any toctree
make html 2>&1 | grep "isn't included in any toctree"

# Full warning list (excluding known duplicate-ref noise)
make html 2>&1 | grep -i warning | grep -v "duplicate.*pyarchimate"
```

## Common Problems

| Problem | Cause | Fix |
|---------|-------|-----|
| `Extension error: No module named 'myst_parser'` | myst-parser not installed | `pip install myst-parser` |
| `WARNING: document isn't included in any toctree` | New file not in index.rst | Add to appropriate toctree in index.rst |
| `WARNING: unknown document 'guides/…'` | Guide file not created | Create the missing file |
| `WARNING: duplicate object description` | Suppressed by `ref.python` in conf.py | Expected for pyArchimate shim |

## Implementation Order

Follow the sequence in `plan.md § Implementation Sequence` to avoid forward-reference errors during incremental builds.