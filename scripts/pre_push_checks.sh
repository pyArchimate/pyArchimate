#!/bin/bash

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

run_quiet() {
    echo "."
    local label="$1"; shift
    local output
    output=$("$@" 2>&1) || {
        echo "❌ $label failed:"
        echo "$output"
        exit 1
    }
}

run_quiet "pre-commit checks"    poetry run scripts/pre_commit_checks.sh
run_quiet "layer boundary check" poetry run scripts/check_layer_boundaries.py

# --- Code Quality Checks ---
# poetry run pysonar --sonar-token=<token> --exclude .git || true

# --- Security Checks ---
# poetry run snyk test --package-manager=poetry || true

run_quiet "behave acceptance tests" poetry run behave tests/features/
run_quiet "pytest unit (coverage)"  poetry run pytest tests/unit/ --cov-fail-under=80 --cov=src --cov-report=term-missing
run_quiet "pytest integration"      poetry run pytest tests/integration/ tests/fixtures/
run_quiet "pytest legacy"           poetry run pytest tests/legacy_unit/ tests/legacy_integration/ tests/legacy_examples/

echo "✅ Pre-push checks completed."
exit 0
