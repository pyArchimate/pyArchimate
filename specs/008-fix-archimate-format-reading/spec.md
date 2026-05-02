# Feature 008: Fix .archimate Format File Reading - ZIP Archive Support

## Feature Overview
Fix critical bug in Model.read() that fails to properly handle `.archimate` format files which are ZIP archives, not plain XML. Currently throws `UnicodeDecodeError` when attempting to read `.archimate` files.

## Root Cause Analysis
- `.archimate` format files are ZIP archives containing XML and related resources
- Model._load_file_contents() attempts to read as plain UTF-8 text
- ZIP binary format starts with `0x504B` (PK), triggering UTF-8 decode failure
- Feature 007's format selection detects `.archimate` extension but doesn't handle ZIP extraction

## User Stories

### US1: Detect and Extract ZIP Archives [P1]
**Goal**: Handle `.archimate` ZIP format files correctly

**Acceptance Criteria**:
- Detect if file is ZIP archive by magic bytes (PK signature)
- Extract XML content from archive root
- Properly handle missing or malformed archives
- Throw meaningful error messages for invalid files

**Test Scenarios**:
- Read valid `.archimate` file with ZIP structure
- Read `.archimate` file with nested directories
- Error handling for corrupted ZIP files
- Error handling for ZIP files without valid XML

### US2: Unified File Loading [P2]
**Goal**: Refactor _load_file_contents to handle both plain XML and ZIP formats

**Acceptance Criteria**:
- Single method detects format and loads appropriately
- Backward compatible with existing `.xml` files
- Clear separation of concerns (detection vs. loading)
- Type hints and documentation updated

**Test Scenarios**:
- Load `.xml` file (OpenGroup Exchange)
- Load `.archimate` file (Archi native)
- Load file with unusual encoding
- Load non-existent file with proper error

### US3: Comprehensive Testing [P3]
**Goal**: Ensure round-trip fidelity with ZIP archive support

**Acceptance Criteria**:
- Integration tests for both formats
- Round-trip preservation verified
- Error cases handled gracefully
- All existing tests pass

## Implementation Notes
- Use Python `zipfile` module (stdlib, already available)
- Detect ZIP with magic bytes before attempting open
- Extract and parse XML from archive's main document
- Maintain backward compatibility with Feature 007 format selection

## Related Features
- Feature 007: Smart file format selection (depends on this fix)
- Feature 004: ArchiMate v3.x compliance (will benefit from proper ZIP handling)
