- [how to build a python package] (https://packaging.python.org/en/latest/tutorials/packaging-projects/)

## Pre-commit hooks

Pre-commit hooks run `ruff check` (lint + complexity gate) and `ruff format --check` (format gate)
on every staged file before a commit is accepted. Hooks are defined in `.pre-commit-config.yaml`
and configured via `pyproject.toml`.

One-time setup per clone:

```bash
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
```

This wires two gates:

- **pre-commit**: ruff lint + format, pymarkdown, vulture — runs on staged files only, fast
- **pre-push**: pyright, mypy, layer boundaries, behave, full pytest suite — runs on every push

To run either gate manually against the entire codebase:

```bash
pre-commit run --all-files                        # commit-stage hooks
pre-commit run --all-files --hook-stage pre-push  # push-stage hooks
```

Any commit that introduces a function exceeding McCabe complexity 15 (`C901`) or
a formatting violation will be blocked with a descriptive error.

## build the doc
- cd docs
- poetry run make html

## release a new version (on master branch)

Versioning is managed by [commitizen](https://commitizen-tools.github.io/commitizen/).
Commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) format
(`fix:`, `feat:`, `feat!:` / `BREAKING CHANGE`) so commitizen can determine the correct
semver increment automatically.

### 1. Merge develop → master and switch to master

```bash
git checkout master
git pull origin master
git checkout develop
git pull origin develop
git merge master          # bring any master fixes into develop first
git checkout master
git merge develop         # fast-forward master to develop HEAD
```

### 2. Check layer boundaries

```bash
poetry run python scripts/check_layer_boundaries.py
```

### 2b. Check SonarCloud for open issues

Requires the code to have been analysed by SonarCloud (happens automatically after a push/PR merge).

```bash
python scripts/check_sonarcloud.py
```

Set `SONAR_TOKEN` in your environment for private project access. Exit code 1 means open issues
exist — resolve them before proceeding.

### 3. Regenerate diagrams

```bash
# Review and update PlantUML sources against current source code
claude -p "Review each of the diagrams in @docs/diagrams/*.puml, compare against @src/pyArchimate, and update as required." --dangerously-skip-permissions

# Re-render to PNG/SVG
bash scripts/render_diagrams.sh
```

### 4. Review AI.md for accuracy

```bash
claude -p "Review @AI.md for accuracy since the last release tag version." --dangerously-skip-permissions
```

### 5. Review spec documents for accuracy

```bash
claude -p "Review @specs/PROJECT_CONSTITUTION.md @specs/PROJECT_SPECIFICATION.md @specs/TECHNICAL.md @specs/NONFUNCTIONALS.md against changes since the last release tag and recommend any updates needed." --dangerously-skip-permissions
```

### 6. Build Sphinx documentation

```bash
poetry run scripts/create_documentation.sh
# or: cd docs && poetry run make html
```

### 7. Commit any regenerated artefacts

```bash
# Check whether anything changed (includes untracked new files)
git status --porcelain

# If there are changes:
git add docs/diagrams/ AI.md docs/
git commit -m "docs: regenerate diagrams, AI.md, and Sphinx docs pre-release"
```

### 8. Run the full test suite

```bash
pre-commit run --all-files --hook-stage pre-push
```

### 9. Regenerate requirements files

`poetry export` requires the export plugin (one-time install):

```bash
poetry self add poetry-plugin-export
```

Then regenerate:

```bash
poetry export --without-hashes -f requirements.txt --with docs -o requirements.txt
git add requirements.txt
git diff --cached --quiet || git commit -m "chore: regenerate requirements files"
```

### 10. Bump version and update changelog

```bash
poetry run cz bump        # bumps [project] version, updates CHANGELOG.md, creates a git tag
```

### 11. Push master and the new tag

```bash
git push origin master --tags
```

### 12. Create GitHub release

Ask Claude to draft release notes based on the previous release as a template:

```
Look at the v<PREV_VERSION> release, particularly the text provided as part of the release,
and do the same for v<NEW_VERSION>. I typically ask for a subject line and summary
of all commits since the last release.
```

Then review the draft and publish:

```bash
gh release create v<NEW_VERSION> --title "v<NEW_VERSION>" --notes "<PASTE NOTES>"
```

Or create directly on GitHub at https://github.com/pyArchimate/pyArchimate/releases/new,
selecting the version tag and pasting the draft.

### 13. Merge master back into develop

```bash
git checkout develop
git pull origin develop
git merge master
git push origin develop
```

## build the package and publish to PyPI

These steps are automated by the `Release` GitHub Actions workflow (`.github/workflows/release.yml`).
Pushing a version tag (step 11 above) triggers the workflow, which builds the sdist/wheel and
publishes to PyPI via OIDC trusted publishing — no API token required.
