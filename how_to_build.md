- [how to build a python package] (https://packaging.python.org/en/latest/tutorials/packaging-projects/)

## build the doc
- cd docs
- make html

## release a new version (on master branch)

Versioning is managed by [commitizen](https://commitizen-tools.github.io/commitizen/).
Commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) format
(`fix:`, `feat:`, `feat!:` / `BREAKING CHANGE`) so commitizen can determine the correct
semver increment automatically.

```bash
git checkout master
git pull origin master
cz bump --changelog      # bumps [project] version, updates CHANGELOG.md, creates a git tag
git push origin master --tags
```

## build the package
- cd ..
- python -m build

## publish to Pypi (require API token)
- pip install --upgrade twine
- twine upload dist/*
