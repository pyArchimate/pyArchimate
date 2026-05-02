#!/bin/bash

set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

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

run_quiet "poetry update"   poetry update
run_quiet "poetry install"  poetry install
run_quiet "poetry sync"     poetry sync
run_quiet "pymarkdown lint" poetry run pymarkdownlnt fix *.md specs/*.md
run_quiet "ruff check"      poetry run ruff check src/ tests/ --fix
run_quiet "pyright"         poetry run pyright src/ tests/
run_quiet "mypy"            poetry run mypy src/
run_quiet "pytest unit"     poetry run pytest tests/unit/

echo "✅ Pre-commit checks completed."
echo "Run scripts/pre_push_checks.sh before merging to exercise api, integration, and security suites."
exit 0
