#!/bin/bash

# Exit immediately if any command fails.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "💡 Running pre-push checks (includes pre-commit and heavier suites)..."
poetry run scripts/pre_commit_checks.sh
poetry run scripts/check_layer_boundaries.py

# --- Code Quality Checks ---
# echo "Running code quality scan..."
# poetry run pysonar --sonar-token=<token> --exclude .git || true

# --- Security Checks ---
# echo "Running security scan..."
# poetry run snyk test --package-manager=poetry || true

echo "Running behave acceptance tests..."
poetry run behave tests/features/

echo "Running pytest suites..."
poetry run pytest tests/unit/ --cov-fail-under=80 --cov=src --cov-report=term-missing
poetry run pytest tests/integration/ tests/fixtures/
poetry run pytest tests/legacy_unit/ tests/legacy_integration/ tests/legacy_examples/

echo "Pre-push checks passed successfully."
echo "✅ Pre-push checks completed."
exit 0
