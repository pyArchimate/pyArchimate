# Feature 008 Research: .archimate ZIP Archive Format

## Investigation Results

### .archimate Format Structure
**Decision**: Treat `.archimate` files as ZIP archives per Archi tool specification

**Rationale**:
- Archi tool (source of format) uses ZIP for `.archimate` files
- Enables bundling XML + images + metadata in single file
- Standard ZIP format with `PK` magic bytes (0x504B)
- Well-documented by Archi tool community

**Evidence**:

```bash
$ file /Users/xavier/PycharmProjects/pyArchimate/temp/export_demo.archimate
Zip archive data, at least v2.0 to extract, compression method=deflate
```

### Archive Contents Analysis
`.archimate` ZIP typically contains:
- `model.xml` - Main ArchiMate model document (required)
- `diagrams.xml` - View/diagram definitions
- `metadata.xml` - Metadata and tool information
- `*.png` - Diagram preview images
- `folder/` - Nested folder structures for organization

### Detection Method
**Decision**: Use magic bytes (file signature) for format detection

**Rationale**:
- More reliable than extension-only detection
- Works with renamed files
- Single byte check (0x504B = 'PK')
- Standard approach across file type detection

**Alternatives Considered**:
- Extension-only detection: Fails if file renamed, less robust
- Try/catch ZIP open: Works but less efficient, no early detection
- MIME type sniffing: Overkill for local files, adds complexity

### ZIP Extraction Strategy
**Decision**: Extract `model.xml` from archive root

**Rationale**:
- `model.xml` is guaranteed main document per format spec
- Other files (images, metadata) not needed for model parsing
- Simpler implementation with lower error surface
- Compatible with existing XML parsing pipeline

**Error Handling**:
- Corrupted ZIP → Informative error message
- Missing `model.xml` → Error: "Invalid .archimate file structure"
- Invalid XML → Existing parser error handling applies

### Python Implementation
**Decision**: Use standard `zipfile` module from stdlib

**Rationale**:
- No new dependencies required
- Stable, well-tested implementation
- Available in all Python versions used by pyArchimate (3.10+)
- Handles edge cases (corrupt archives, encryption, etc.)

**Code Pattern**:

```python
import zipfile

# Detect
with open(file_path, 'rb') as f:
    magic = f.read(2)
    is_zip = magic == b'PK'

# Extract
if is_zip:
    with zipfile.ZipFile(file_path, 'r') as zf:
        with zf.open('model.xml') as xml_file:
            content = xml_file.read().decode('utf-8')
else:
    # Plain XML reading
```

## Related Standards & Specifications
- ZIP Format: PKWARE specification (widely documented)
- Archi Tool: Open source reference implementation
- ArchiMate: OpenGroup specification (format-agnostic)

## Testing Implications
- Create `.archimate` test files via archi_writer + ZIP wrapping
- Use Python zipfile to create mock archives for testing
- Verify both valid and invalid archive handling
- Ensure extraction preserves encoding

## Backward Compatibility
- Existing `.xml` (OpenGroup Exchange) files unaffected
- Feature 007 format selection enhanced, not changed
- All existing tests should pass without modification
- No API changes required
