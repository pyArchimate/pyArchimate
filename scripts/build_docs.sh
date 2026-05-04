#!/bin/bash

# Quick documentation build for development
# Usage: ./scripts/build_docs.sh [--clean] [--open]
#
# This script performs an incremental build (faster during development).
# Use --clean for a full rebuild, --open to open in browser.

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

DOCS_DIR="docs"
HTML_DIR="${DOCS_DIR}/build/html"
CLEAN=false
OPEN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --clean)
      CLEAN=true
      shift
      ;;
    --open)
      OPEN=true
      shift
      ;;
    --help)
      echo "Usage: $0 [--clean] [--open] [--help]"
      echo ""
      echo "Options:"
      echo "  --clean   Remove build directory and rebuild from scratch"
      echo "  --open    Open the built documentation in default browser"
      echo "  --help    Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo -e "${BLUE}Building documentation...${NC}"

if [ "$CLEAN" = true ]; then
  rm -rf "${DOCS_DIR}/build"
  echo -e "${GREEN}✓${NC} Cleaned build directory"
fi

# Build with poetry
poetry run sphinx-build -b html "${DOCS_DIR}" "${HTML_DIR}"

echo -e "\n${GREEN}✓ Build complete!${NC}"
echo -e "${BLUE}📁 Documentation: ${HTML_DIR}${NC}"

if [ "$OPEN" = true ]; then
  if command -v open &> /dev/null; then
    open "${HTML_DIR}/index.html"
  elif command -v xdg-open &> /dev/null; then
    xdg-open "${HTML_DIR}/index.html"
  else
    echo "Could not open browser automatically"
  fi
fi
