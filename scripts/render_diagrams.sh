#!/bin/bash

set -euo pipefail

server_base="${PLANTUML_SERVER:-https://www.plantuml.com/plantuml}"

plantuml_encode() {
  python3 - "$1" <<'PY'
import sys, zlib, base64

std_b64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
puml_b64 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'

with open(sys.argv[1], 'r', encoding='utf-8') as fd:
    data = fd.read()
compressor = zlib.compressobj(level=-1, wbits=-15)
compressed = compressor.compress(data.encode('utf-8')) + compressor.flush()
encoded = base64.b64encode(compressed).decode('utf-8').rstrip('=')
translated = encoded.translate(str.maketrans(std_b64, puml_b64))
print(translated)
PY
}

for file in docs/diagrams/*.puml; do
  echo "Rendering $file"
  if [ ! -f "$file" ]; then
    echo "Missing $file, skipping." >&2
    continue
  fi
  encoded=$(plantuml_encode "$file")
  output="docs/diagrams/$(basename "${file%.*}.png")"
  curl -s -L --retry 3 "${server_base}/png/${encoded}" -o "$output"
  echo "Rendered $output"
  sleep 0.2
done
