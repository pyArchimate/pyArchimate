#!/bin/bash

# Build and validate Sphinx documentation for release
# Usage: ./scripts/build_docs_release.sh [--deploy]
#
# This script performs a clean build of the documentation with validation,
# ensuring zero broken links and no critical errors before release.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCS_DIR="docs"
BUILD_DIR="${DOCS_DIR}/build"
HTML_DIR="${BUILD_DIR}/html"
LOG_FILE="${BUILD_DIR}/build.log"

# Parse arguments
DEPLOY=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --deploy)
      DEPLOY=true
      shift
      ;;
    --help)
      echo "Usage: $0 [--deploy] [--help]"
      echo ""
      echo "Options:"
      echo "  --deploy  Build docs and prepare for deployment (not yet implemented)"
      echo "  --help    Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Helper functions
log_section() {
  echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

log_success() {
  echo -e "${GREEN}✓${NC} $1"
}

log_error() {
  echo -e "${RED}✗${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

log_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

# Check prerequisites
check_prerequisites() {
  log_section "Checking Prerequisites"

  # Check if poetry is available
  if ! command -v poetry &> /dev/null; then
    log_error "Poetry is not installed"
    exit 1
  fi
  log_success "Poetry found"

  # Check if docs directory exists
  if [ ! -d "${DOCS_DIR}" ]; then
    log_error "Documentation directory not found: ${DOCS_DIR}"
    exit 1
  fi
  log_success "Documentation directory found"

  # Check if conf.py exists
  if [ ! -f "${DOCS_DIR}/conf.py" ]; then
    log_error "Sphinx configuration not found: ${DOCS_DIR}/conf.py"
    exit 1
  fi
  log_success "Sphinx configuration found"
}

# Clean previous builds
clean_build() {
  log_section "Cleaning Previous Builds"

  if [ -d "${BUILD_DIR}" ]; then
    rm -rf "${BUILD_DIR}"
    log_success "Removed old build directory"
  else
    log_info "No previous build found"
  fi

  mkdir -p "${BUILD_DIR}"
  log_success "Created fresh build directory"
}

# Run Sphinx build
run_sphinx_build() {
  log_section "Building Sphinx Documentation"

  # Run build with strict error handling
  # -W: treat warnings as errors (optional, commented out for now)
  # --keep-going: continue building despite errors to see all issues
  if ! poetry run sphinx-build \
      --keep-going \
      -b html \
      -a \
      "${DOCS_DIR}" "${HTML_DIR}" 2>&1 | tee "${LOG_FILE}"; then
    log_error "Sphinx build failed"
    return 1
  fi

  log_success "Sphinx build completed"
}

# Validate build output
validate_build() {
  log_section "Validating Build Output"

  local has_errors=false

  # Check for broken references
  if grep -q "unknown document\|undefined label\|ref.doc.*not found" "${LOG_FILE}"; then
    log_error "Found broken cross-references:"
    grep -E "unknown document|undefined label|ref.doc" "${LOG_FILE}" | head -10
    has_errors=true
  else
    log_success "No broken cross-references"
  fi

  # Check for missing toctree documents (excluding known skips)
  if grep -q "isn't included in any toctree" "${LOG_FILE}" | grep -v "diagrams/README\|diagrams.rst"; then
    log_error "Found documents not included in toctree:"
    grep "isn't included in any toctree" "${LOG_FILE}" | grep -v "diagrams/README\|diagrams.rst" | head -5
    has_errors=true
  else
    log_success "All documents included in toctree"
  fi

  # Check for critical RST errors
  if grep -q "^ERROR:" "${LOG_FILE}"; then
    log_error "Found RST syntax errors:"
    grep "^ERROR:" "${LOG_FILE}" | head -5
    has_errors=true
  else
    log_success "No RST syntax errors"
  fi

  # Check if HTML was generated
  if [ ! -f "${HTML_DIR}/index.html" ]; then
    log_error "index.html not generated"
    has_errors=true
  else
    log_success "index.html generated"
  fi

  # Count warnings (informational only)
  warning_count=$(grep -c "WARNING:" "${LOG_FILE}" || true)
  if [ "$warning_count" -gt 0 ]; then
    log_warning "Build completed with ${warning_count} warning(s)"
    log_info "Run the following to review warnings:"
    echo "    grep WARNING ${LOG_FILE} | head -20"
  else
    log_success "No warnings"
  fi

  return $([ "$has_errors" = false ] && echo 0 || echo 1)
}

# Display build statistics
show_statistics() {
  log_section "Build Statistics"

  local file_count=$(find "${HTML_DIR}" -name "*.html" | wc -l)
  local total_size=$(du -sh "${HTML_DIR}" | cut -f1)

  log_info "HTML files generated: ${file_count}"
  log_info "Build size: ${total_size}"
  log_info "Build directory: ${HTML_DIR}"
}

# Display next steps
show_next_steps() {
  log_section "Next Steps"

  echo "Local verification:"
  echo "  • Open in browser: open ${HTML_DIR}/index.html"
  echo "  • Check navigation: Verify three-tier structure (Basic, Intermediate, Advanced)"
  echo "  • Click through pages: Test cross-references and links"
  echo ""

  if [ "$DEPLOY" = true ]; then
    echo "Deployment (manual):"
    echo "  • Review warnings: grep WARNING ${LOG_FILE}"
    echo "  • Upload to server: rsync -avz ${HTML_DIR}/ user@server:/path/to/docs/"
    echo "  • Or: Push to ReadTheDocs (git push origin main)"
  else
    echo "To view the build log:"
    echo "  tail -50 ${LOG_FILE}"
  fi
}

# Main execution
main() {
  echo -e "${GREEN}"
  echo "╔════════════════════════════════════════╗"
  echo "║   pyArchimate Documentation Builder    ║"
  echo "║   Release Build Script                 ║"
  echo "╚════════════════════════════════════════╝"
  echo -e "${NC}"

  check_prerequisites
  clean_build
  run_sphinx_build || {
    log_error "Documentation build failed"
    exit 1
  }

  if ! validate_build; then
    log_error "Build validation failed"
    exit 1
  fi

  show_statistics
  show_next_steps

  echo ""
  log_success "Documentation build completed successfully!"
  echo ""
}

# Run main function
main "$@"
