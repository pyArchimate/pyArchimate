# Data Model: Fix .archimate Format File Reading

## Overview
This feature does not introduce new entities or data structures. It enhances the file I/O layer to properly handle `.archimate` ZIP archive format while maintaining compatibility with `.xml` plain text format.

## File Format Entities

### FileFormat (Enumeration)
Represents detected file format type:
- `ZIP` - Binary ZIP archive (`.archimate` format)
- `XML` - Plain text XML (`.xml` format)
- `UNKNOWN` - Format could not be determined

**Usage**: Internal enum for routing file loading logic, not exposed in public API.

## Data Flow Changes

### Current Flow (Feature 007 - Broken)
```
Model.read(file_path)
  ├─ _prepare_reader(file_path)
  │  ├─ _detect_format_from_extension() → Returns reader class
  │  ├─ _load_file_contents(file_path) → Reads as UTF-8 text
  │  │  ├─ open(file_path, 'r', encoding='utf-8')
  │  │  └─ fd.read() → ❌ FAILS for ZIP files (UnicodeDecodeError)
  │  └─ Parse XML string
  └─ Call appropriate reader with XML root
```

### Fixed Flow (Feature 008)
```
Model.read(file_path)
  ├─ _prepare_reader(file_path)
  │  ├─ _detect_format_from_extension() → Returns reader class
  │  ├─ _load_file_contents(file_path) → Smart format detection
  │  │  ├─ _detect_zip_file(file_path) → Check magic bytes (PK)
  │  │  ├─ If ZIP:
  │  │  │  ├─ _extract_xml_from_zip(file_path)
  │  │  │  ├─ zipfile.ZipFile(file_path, 'r')
  │  │  │  ├─ Extract model.xml → UTF-8 string ✅
  │  │  │  └─ Return XML content
  │  │  └─ Else (plain XML):
  │  │     ├─ open(file_path, 'r', encoding='utf-8')
  │  │     └─ Return file content
  │  ├─ Parse XML string
  │  └─ Match reader to root element type
  └─ Call appropriate reader with XML root
```

## Method Signatures

### _detect_zip_file(file_path: str) → bool
**Purpose**: Detect if file is ZIP archive using magic bytes

**Logic**:
1. Open file in binary mode
2. Read first 2 bytes
3. Check if bytes == `0x504B` (ASCII 'PK')
4. Return boolean

**Error Handling**: Return False on any I/O error (file not found, permission denied)

**Example**:
```python
_detect_zip_file("model.archimate")  # Returns: True
_detect_zip_file("model.xml")         # Returns: False
```

### _extract_xml_from_zip(file_path: str) → str
**Purpose**: Extract XML content from `.archimate` ZIP archive

**Logic**:
1. Open ZIP file: `zipfile.ZipFile(file_path, 'r')`
2. List contents to find `model.xml`
3. Read XML file as binary
4. Decode to string (UTF-8)
5. Return XML string

**Error Handling**:
- `FileNotFoundError`: File doesn't exist
- `zipfile.BadZipFile`: Archive is corrupted
- `KeyError`: `model.xml` not in archive → "Invalid .archimate file"
- `UnicodeDecodeError`: XML encoding issue

**Example**:
```python
xml_content = _extract_xml_from_zip("model.archimate")
# Returns: '<?xml version="1.0"...'
```

### _load_file_contents(file_path: str, operation: str) → str
**Purpose**: Load file contents with automatic format detection (REFACTORED)

**Logic** (NEW):
1. Check if file is ZIP using `_detect_zip_file()`
2. If ZIP: Call `_extract_xml_from_zip()` and return
3. Else: Open as plain text UTF-8 and return

**Error Handling**: 
- Maintains existing error messages for backward compatibility
- Adds informative error for invalid `.archimate` structure

**Example**:
```python
# For .archimate files (ZIP)
content = _load_file_contents("model.archimate", "read")
# Internally calls _extract_xml_from_zip()

# For .xml files (plain XML)
content = _load_file_contents("model.xml", "read")
# Reads as plain text, same as before
```

## No Changes to Existing Entities

The following remain unchanged:
- `Model` class - Same interface, same behavior for `.xml` files
- `Element` class - No changes
- `Relationship` class - No changes
- `Reader/Writer` classes - No changes
- XML parsing pipeline - No changes

## Validation Rules

**File Format Validation**:
- `.archimate` files MUST be valid ZIP archives
- ZIP archive MUST contain `model.xml` at root level
- `model.xml` MUST be valid UTF-8 encoded XML
- XML root element MUST match a registered reader (archimate/model/archimateModel)

**Error Messages**:
- Corrupted ZIP: "Invalid .archimate file - ZIP archive is corrupted"
- Missing model.xml: "Invalid .archimate file - model.xml not found in archive"
- Encoding error: "File encoding error - unable to decode XML as UTF-8"

## Backward Compatibility

✅ **Fully backward compatible**:
- `.xml` files read identically to current implementation
- No API changes to public Model class
- Existing tests unchanged (except new tests added)
- Feature 007 format detection still works

## Performance Notes

**File Detection**: Negligible overhead (2-byte read)
**ZIP Extraction**: Same as manual ZIP opening (stdlib zipfile is optimized)
**Memory**: Single XML string in memory (same as current approach)
**No impact on round-trip fidelity**
