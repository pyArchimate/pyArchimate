#!/bin/bash

set -euo pipefail

if ! command -v plantuml &>/dev/null; then
  echo "Error: 'plantuml' binary not found in PATH." >&2
  echo "Install it with: sudo apt-get install plantuml  or  brew install plantuml" >&2
  exit 1
fi

for file in docs/diagrams/*.puml; do
  if [[ ! -f "$file" ]]; then
    echo "Missing $file, skipping." >&2
    continue
  fi
  echo "Rendering $file"
  plantuml -tpng -o "$(pwd)/docs/diagrams" "$file"
  echo "Rendered docs/diagrams/$(basename "${file%.*}.png")"
done
