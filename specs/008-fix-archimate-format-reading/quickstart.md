# Quickstart: Test Scenarios for .archimate Format Reading

## Test Scenarios Overview

This document outlines test scenarios for Feature 008 implementation. Tests are organized by user story and test level (unit, integration).

## US1: Detect and Extract ZIP Archives

### Unit Tests: ZIP Detection

**TC-US1-001: Detect valid ZIP file (magic bytes)**
```python
def test_detect_zip_file_with_valid_archimate():
    file_path = "tests/fixtures/valid_model.archimate"
    assert Model._detect_zip_file(file_path) == True
```

**TC-US1-002: Detect plain XML file (not ZIP)**
```python
def test_detect_zip_file_with_xml():
    file_path = "tests/fixtures/valid_model.xml"
    assert Model._detect_zip_file(file_path) == False
```

**TC-US1-003: Non-existent file returns False**
```python
def test_detect_zip_file_missing_file():
    file_path = "tests/fixtures/nonexistent.archimate"
    assert Model._detect_zip_file(file_path) == False
```

**TC-US1-004: Permission denied returns False**
```python
def test_detect_zip_file_permission_denied():
    # Create file with no read permissions
    file_path = "tests/fixtures/no_read.archimate"
    os.chmod(file_path, 0o000)
    assert Model._detect_zip_file(file_path) == False
    os.chmod(file_path, 0o644)  # Restore for cleanup
```

### Unit Tests: ZIP Extraction

**TC-US1-005: Extract model.xml from valid archive**
```python
def test_extract_xml_from_valid_zip():
    file_path = "tests/fixtures/valid_model.archimate"
    content = Model._extract_xml_from_zip(file_path)
    assert content.startswith("<?xml")
    assert "<archimateModel" in content or "<model" in content
```

**TC-US1-006: Error on corrupted ZIP file**
```python
def test_extract_xml_from_corrupted_zip():
    file_path = "tests/fixtures/corrupted.archimate"
    with pytest.raises(zipfile.BadZipFile):
        Model._extract_xml_from_zip(file_path)
```

**TC-US1-007: Error when model.xml missing from archive**
```python
def test_extract_xml_missing_model_xml():
    file_path = "tests/fixtures/no_model_xml.archimate"
    with pytest.raises(KeyError):
        Model._extract_xml_from_zip(file_path)
```

**TC-US1-008: Error on non-existent file**
```python
def test_extract_xml_file_not_found():
    file_path = "tests/fixtures/missing.archimate"
    with pytest.raises(FileNotFoundError):
        Model._extract_xml_from_zip(file_path)
```

## US2: Unified File Loading

### Unit Tests: _load_file_contents Refactoring

**TC-US2-001: Load plain XML file (unchanged behavior)**
```python
def test_load_file_contents_xml():
    file_path = "tests/fixtures/opengroup.xml"
    content = Model()._load_file_contents(file_path, 'read')
    assert "<?xml" in content
    assert "<model" in content
```

**TC-US2-002: Load .archimate ZIP file (new behavior)**
```python
def test_load_file_contents_archimate():
    file_path = "tests/fixtures/archi_native.archimate"
    content = Model()._load_file_contents(file_path, 'read')
    assert "<?xml" in content
    assert "<archimateModel" in content or "<model" in content
```

**TC-US2-003: Consistent error messages for missing files**
```python
def test_load_file_contents_missing_file():
    m = Model('test')
    with pytest.raises(SystemExit):
        m._load_file_contents("nonexistent.xml", 'read')
```

**TC-US2-004: Encoding error in plain XML**
```python
def test_load_file_contents_encoding_error():
    # Create XML with non-UTF-8 bytes
    file_path = "tests/fixtures/bad_encoding.xml"
    m = Model('test')
    with pytest.raises(SystemExit):
        m._load_file_contents(file_path, 'read')
```

## US3: Comprehensive Testing & Integration

### Integration Tests: Round-trip with ZIP

**TC-US3-001: Read .archimate file and verify structure**
```python
def test_read_archimate_file():
    file_path = "tests/fixtures/demo_model.archimate"
    m = Model('loaded')
    m.read(file_path)
    
    assert len(m.elems_dict) > 0
    assert len(m.rels_dict) > 0
    assert m.name is not None
```

**TC-US3-002: Write then read .archimate file (round-trip)**
```python
def test_archimate_round_trip():
    m1 = Model('original')
    elem = m1.add(ArchiType.BusinessActor, 'Test Actor')
    
    with tempfile.NamedTemporaryFile(suffix='.archimate', delete=False) as f:
        temp_path = f.name
    
    try:
        m1.write(temp_path)  # Feature 007 auto-detection
        
        m2 = Model('reloaded')
        m2.read(temp_path)   # Feature 008 ZIP handling
        
        assert elem.uuid in m2.elems_dict
        assert m2.elems_dict[elem.uuid].name == 'Test Actor'
    finally:
        os.unlink(temp_path)
```

**TC-US3-003: XML file still works (backward compatibility)**
```python
def test_xml_round_trip_still_works():
    m1 = Model('xml-test')
    elem = m1.add(ArchiType.BusinessRole, 'Test Role')
    
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as f:
        temp_path = f.name
    
    try:
        m1.write(temp_path)
        m2 = Model('xml-reloaded')
        m2.read(temp_path)
        
        assert elem.uuid in m2.elems_dict
    finally:
        os.unlink(temp_path)
```

### Integration Tests: Error Cases

**TC-US3-004: Helpful error for .archimate without model.xml**
```python
def test_invalid_archimate_structure_error():
    file_path = "tests/fixtures/broken_archimate.archimate"
    m = Model('test')
    with pytest.raises(SystemExit) as exc_info:
        m.read(file_path)
    # Verify error message mentions .archimate structure
```

**TC-US3-005: Different element types round-trip correctly**
```python
def test_multiple_element_types_archimate():
    m1 = Model('multi-element')
    
    # Add various element types
    business = m1.add(ArchiType.BusinessProcess, 'Process')
    app = m1.add(ArchiType.ApplicationComponent, 'App')
    tech = m1.add(ArchiType.Node, 'Server')
    
    with tempfile.NamedTemporaryFile(suffix='.archimate', delete=False) as f:
        temp_path = f.name
    
    try:
        m1.write(temp_path)
        m2 = Model('reload-multi')
        m2.read(temp_path)
        
        assert business.uuid in m2.elems_dict
        assert app.uuid in m2.elems_dict
        assert tech.uuid in m2.elems_dict
    finally:
        os.unlink(temp_path)
```

### Integration Tests: Feature 007 Compatibility

**TC-US3-006: Smart format selection works with ZIP**
```python
def test_format_selection_archimate_extension():
    # Feature 007's format selection + Feature 008's ZIP handling
    m = Model('test')
    
    # Write with .archimate extension (Feature 007 auto-selects archiWriter)
    with tempfile.NamedTemporaryFile(suffix='.archimate', delete=False) as f:
        temp_path = f.name
    
    # Manually write a test .archimate file
    # Then read it (Feature 008 detects ZIP and extracts)
    m.read(temp_path)
```

**TC-US3-007: All existing 737 tests still pass**
```python
# Run: python -m pytest tests/ -v
# Expected: 737 passed, 0 failed
```

## Test File Fixtures Required

### fixtures/
```
valid_model.archimate        # Valid Archi .archimate ZIP with model.xml
archi_native.archimate       # Native Archi format (test export)
opengroup.xml                # Valid OpenGroup Exchange XML
corrupted.archimate          # Corrupted ZIP file
no_model_xml.archimate       # Valid ZIP but missing model.xml
bad_encoding.xml             # XML file with non-UTF-8 bytes
broken_archimate.archimate   # ZIP with malformed model.xml
demo_model.archimate         # Complete model for round-trip tests
```

## Manual Testing Checklist

- [ ] Open real Archi tool `.archimate` file in pyArchimate
- [ ] Verify structure matches Archi tool export
- [ ] Round-trip with Archi tool (export → read → write → Archi reads)
- [ ] Error message clarity for corrupted files
- [ ] Performance acceptable for large models (>10k elements)
- [ ] File permission errors handled gracefully

## Known Limitations (Out of Scope)

- Nested ZIP structures (not supported by Archi)
- Custom XML structure within ZIP (must be standard Archi format)
- Encrypted/password-protected ZIP files (not in Archi spec)
- Partial archive extraction (must extract full model.xml)
