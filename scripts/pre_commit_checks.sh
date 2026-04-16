#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

echo "Starting pre-commit checks..."
echo "Updating dependency locks to the latest compatible versions..."
poetry update
poetry install
poetry sync

echo "Running pre-commit checks..."

# --- Linting and Formatting Check ---
echo "Running pymarkdown lint..."
# Runs pymarkdown for linting markdown files. Assumes pymarkdown is executable in the environment.
poetry run pymarkdownlnt fix *.md specs/*.md

echo "Running ruff check..."
# Runs ruff for linting and formatting checks across the project.
poetry run ruff check src/ --fix

echo "Running pyright..."
# Runs pyright for static type checking. Assumes pyright is executable in the environment.
poetry run pyright src/

# --- Static Type Checking ---
echo "Running mypy..."
# Runs mypy on the src directory for static type checking.
poetry run mypy src/

# --- Unit Tests ---
echo "Running pytest unit tests..."
poetry run pytest tests/unit/


echo "Pre-commit checks passed successfully."
echo "✅ Pre-commit checks completed."
echo "Run scripts/pre_push_checks.sh before merging to exercise api, integration, and security suites."
exit 0
