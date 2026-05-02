#!/usr/bin/env bash
# Release script: regenerate diagrams + docs, bump version, push tag.
# Must be run from the master branch with a clean working tree.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# ---------------------------------------------------------------------------
# Guard: must be on master with a clean working tree
# ---------------------------------------------------------------------------
current_branch=$(git symbolic-ref --short HEAD)
if [[ "$current_branch" != "master" ]]; then
    echo "❌ Must be on master (currently on '$current_branch'). Aborting." >&2
    exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "❌ Working tree has uncommitted changes. Commit or stash them first." >&2
    exit 1
fi

echo "✅ On master with clean working tree."

echo ""
echo "📐 Checking layer boundaries..."
poetry run scripts/check_layer_boundaries.py

echo ""
echo "📐 Regenerating diagrams..."
claude -p "Review each of the diagrams in @docs/diagrams/*.puml, compare against @src/pyArchimate, and update as required." --dangerously-skip-permissions

# ---------------------------------------------------------------------------
# Step 1: Regenerate PlantUML diagrams
# ---------------------------------------------------------------------------
echo ""
echo "📐 Rerendering diagrams..."
poetry run scripts/render_diagrams.sh

# ---------------------------------------------------------------------------
# Step 3: Build Sphinx documentation
# ---------------------------------------------------------------------------
echo ""
echo "📚 Building Sphinx documentation..."
poetry run scripts/create_documentation.sh

# ---------------------------------------------------------------------------
# Step 2: Regenerate AI.md
# ---------------------------------------------------------------------------
echo ""
echo "🤖 Regenerating AI.md..."
claude -p "Review @AI.md for accuracy since the last release tag version." --dangerously-skip-permissions

# ---------------------------------------------------------------------------
# Step 4: Commit any updated artefacts before bumping
# ---------------------------------------------------------------------------
if ! git diff --quiet; then
    echo ""
    echo "💾 Committing updated artefacts (diagrams, AI.md, docs)..."
    git add docs/diagrams/ AI.md build/html -f
    git commit -m "docs: regenerate diagrams, AI.md, and Sphinx docs pre-release"
fi

# ---------------------------------------------------------------------------
# Step 5: Full test suite — safety gate before tagging
# ---------------------------------------------------------------------------
echo ""
echo "🧪 Running test suite..."
poetry run scripts/pre_push_checks.sh

# ---------------------------------------------------------------------------
# Step 6: Commitizen version bump (updates pyproject.toml + CHANGELOG + tag)
# ---------------------------------------------------------------------------
echo ""
echo "🔖 Bumping version..."
poetry run cz bump

# ---------------------------------------------------------------------------
# Step 7: Push commits and the new version tag
# ---------------------------------------------------------------------------
echo ""
echo "🚀 Pushing to origin/master..."
git push && git push --tags

echo ""
echo "✅ Release complete."
