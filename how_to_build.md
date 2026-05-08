- [how to build a python package] (https://packaging.python.org/en/latest/tutorials/packaging-projects/)

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
poetry run scripts/check_layer_boundaries.py
```

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

### 5. Build Sphinx documentation

```bash
poetry run scripts/create_documentation.sh
# or: cd docs && poetry run make html
```

### 6. Commit any regenerated artefacts

```bash
# Check whether anything changed (includes untracked new files)
git status --porcelain

# If there are changes:
git add docs/diagrams/ AI.md docs/
git commit -m "docs: regenerate diagrams, AI.md, and Sphinx docs pre-release"
```

### 7. Run the full test suite

```bash
poetry run scripts/pre_push_checks.sh
```

### 8. Regenerate requirements files

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

### 9. Bump version and update changelog

```bash
poetry run cz bump        # bumps [project] version, updates CHANGELOG.md, creates a git tag
```

### 10. Push master and the new tag

```bash
git push origin master --tags
```

### 11. Merge master back into develop

```bash
git checkout develop
git pull origin develop
git merge master
git push origin develop
```

## build the package and publish to PyPI

These steps are automated by the `Release` GitHub Actions workflow (`.github/workflows/release.yml`).
Pushing a version tag (step 10 above) triggers the workflow, which builds the sdist/wheel and
publishes to PyPI via OIDC trusted publishing — no API token required.
