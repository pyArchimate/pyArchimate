- [how to build a python package] (https://packaging.python.org/en/latest/tutorials/packaging-projects/)

## build the doc
- cd docs
- make html

## build the package
- cd ..
- python -m build

## publish to Pypi (require API token)
- pip install --upgrade twine 
- twine upload dist/*