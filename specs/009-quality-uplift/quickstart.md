# Quickstart: 009-quality-uplift

## Environment Setup

```bash
# Install lint/type-checking tools
pip install ruff pyright lxml-stubs types-setuptools types-Pillow

# Or via the project's lint group (if uv is available)
uv sync --group lint
```

## Running the Tools

```bash
# Ruff lint check
cd /workspaces/pyArchimate
ruff check src/ tests/

# Ruff auto-fix (safe fixes only)
ruff check src/ tests/ --fix

# Pyright
pyright src/

# Mypy
mypy src/

# Full pre-commit suite
bash scripts/pre_commit_checks.sh

# SonarCloud issues (requires SONAR_TOKEN in .env)
source .env
curl -u "$SONAR_TOKEN:" \
  "https://sonarcloud.io/api/issues/search?projectKeys=pyArchimate_pyArchimate&severities=CRITICAL,MAJOR,MINOR&statuses=OPEN,CONFIRMED" \
  | python3 -m json.tool | grep -E '"message"|"rule"|"severity"'
```

## Running Tests

```bash
# Unit tests only (fast)
pytest tests/unit/

# Full suite (slower — includes integration and BDD)
bash scripts/pre_push_checks.sh
```

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | All tool config changes land here |
| `sonar-project.properties` | SonarCloud exclusions (do not modify) |
| `src/pyArchimate/readers/_arisamlreader_helpers.py:61` | PIL import issue |
| `src/pyArchimate/writers/archimateWriter.py:390` | `no-any-return` |
| `src/pyArchimate/writers/archiWriter.py:372` | `no-any-return` |

## Commit Sequence

Follow the batch order from `plan.md`:

1. `fix(sonar): resolve remaining SonarCloud issues`
2. `fix(ruff): resolve remaining C901 complexity violations`
3. `fix(ruff): replace PLC0415 global ignore with targeted suppressions`
4. `feat(ruff): enable A (builtin-shadowing) rule set`
5. `feat(ruff): enable N (naming) rule set`
6. `chore(ruff): document UP rule set as deferred`
7. `chore(ruff): document PT rule set as deferred`
8. `fix(pyright): suppress unresolvable PIL import`
9. `fix(pyright): re-enable reportAttributeAccessIssue at error level`
10. `fix(pyright): re-enable reportArgumentType and reportOptionalMemberAccess`
11. `fix(mypy): resolve all baseline type errors`
12. `chore: remove obsolete tool exclusions from pyproject.toml`
