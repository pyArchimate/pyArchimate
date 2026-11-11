#!/bin/bash
set -e

# Configuration - Set GITHUB_TOKEN in your environment before running
# export GITHUB_TOKEN="your_github_personal_access_token"
OWNER="pyArchimate"
REPO="pyArchimate"
WORKFLOW_ID="$1"
PER_PAGE=100
NETWORK_TIMEOUT=30

# Validate required environment variable
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "ERROR: GITHUB_TOKEN environment variable is not set" >&2
  echo "Please set it before running this script:" >&2
  echo "  export GITHUB_TOKEN='your_github_personal_access_token'" >&2
  exit 1
fi

list() {
  curl -s -m "$NETWORK_TIMEOUT" \
    -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$OWNER/$REPO/actions/workflows" \
    | jq -r '.workflows[] | "\(.id) \(.name) \(.path)"'
}

delete_runs() {
  local workflow_id="$1"
  PAGE=1
  while :; do
    echo "Fetching runs from page $PAGE for workflow $workflow_id..."
    RUNS=$(curl -s -m "$NETWORK_TIMEOUT" \
      -H "Authorization: token $GITHUB_TOKEN" \
      "https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$workflow_id/runs?per_page=$PER_PAGE&page=$PAGE" \
      | jq '.workflow_runs[]?.id' || true)

    if [[ -z "$RUNS" ]]; then
      echo "No more runs to delete for workflow $workflow_id. Done."
      break
    fi

    for RUN_ID in $RUNS; do
      echo "Deleting run ID: $RUN_ID"
      if ! curl -s -m "$NETWORK_TIMEOUT" -X DELETE \
        -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID" > /dev/null; then
        echo "WARNING: Failed to delete run $RUN_ID" >&2
      fi
    done

    ((PAGE++))
    sleep 1
  done
}

list | awk -F'[^0-9]+' '{ print $1 }' | while read -r workflow_id; do
  delete_runs "$workflow_id"
done
