# API Contract: Fix .archimate Format File Reading

## Public API Changes

**Status**: ✅ NO PUBLIC API CHANGES

This feature enhances internal file loading behavior without modifying the public API.

## Existing Public Interface (Unchanged)

### Model.read(file_path: str) → None
**Signature**: Same as current implementation  
**Behavior**: Enhanced to handle both `.xml` and `.archimate` formats transparently  
**Error Handling**: Improved error messages for invalid files

**Example**:

```python
from src.pyArchimate import Model

# Read OpenGroup Exchange format (plain XML)
m = Model('from-xml')
m.read('model.xml')  # Works exactly as before

# Read Archi native format (ZIP archive) - NOW WORKS
m = Model('from-archimate')
m.read('model.archimate')  # No longer throws UnicodeDecodeError
```

### Model.write(file_path: str, writer=None) → None
**No Changes**: Already works correctly (Feature 007)

### Model.merge(file_path: str) → None
**No Changes**: Already works correctly

## Internal Methods (Private, Not Part of Contract)

The following private methods are added/refactored:
- `Model._detect_zip_file(file_path: str) → bool`
- `Model._extract_xml_from_zip(file_path: str) → str`
- `Model._load_file_contents(file_path: str, operation: str) → str` (refactored)

**Note**: These are implementation details. Changes to these methods do not constitute a public API change.

## Error Handling

### New/Improved Error Messages

**Corrupted .archimate file**:

```
ERROR: Invalid .archimate file - ZIP archive is corrupted
File: /path/to/model.archimate
```

**Missing model.xml in archive**:

```
ERROR: Invalid .archimate file - model.xml not found in archive
File: /path/to/model.archimate
```

**Encoding error in extracted XML**:

```
ERROR: File encoding error - unable to decode XML as UTF-8
File: /path/to/model.archimate
```

## Backward Compatibility

✅ **100% Backward Compatible**

- Existing `.xml` file handling identical to current behavior
- No changes to Model class public interface
- No changes to Element, Relationship, View, or other public classes
- Existing code requires zero modifications
- All existing tests pass without changes

## Feature 007 Integration

Feature 008 complements Feature 007:

| Feature | Responsibility |
|---------|---|
| **Feature 007** | Detect file format from extension and select appropriate reader/writer |
| **Feature 008** | Handle ZIP archive extraction for `.archimate` files during read |

**Flow**:
1. User calls `model.read("file.archimate")`
2. Feature 007: Detects `.archimate` extension → selects archiReader
3. Feature 008: Detects ZIP format → extracts XML from archive
4. archiReader: Parses XML and populates model

Both features work together seamlessly with no public API changes.

## Testing Contract

✅ **Regression Testing**: All 737+ existing tests pass without modification
✅ **New Tests**: Feature 008 adds unit and integration tests (separate suite)
✅ **Round-trip**: `.archimate` files can be read, modified, and written back

## SLA/Performance Contract

- **File detection overhead**: <1ms (2-byte read)
- **ZIP extraction overhead**: Same as system unzip (~10-100ms for typical models)
- **No impact on .xml file reading performance**
- **Memory footprint**: Single XML string (same as current)

## Deprecation/Future Versions

No deprecations in this feature. Implementation details may change in future versions, but public API remains stable.
