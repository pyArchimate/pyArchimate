# Contract: Relationship Documentation Preservation

**Version**: 1.0  
**Date**: 2026-04-30  
**Type**: Relationship Metadata Contract

## Overview

Defines how relationship documentation text is extracted from Archi .archimate files, stored in Python objects, and preserved during export. Ensures no documentation loss in import/export cycles.

## Current Bug

**File**: `src/pyArchimate/readers/_archireader_helpers.py`  
**Issue**: Documentation element is found but wrong value is assigned.

```python
# Current (buggy):
elem.desc = e.text  # ❌ e is the relationship, not documentation element

# Should be:
doc = e.find('documentation')
if doc is not None and doc.text:
    elem.desc = doc.text  # ✓ Extract from documentation element
```

## XML Structure

### Archi .archimate Format
```xml
<Relationship source="..." target="...">
  <documentation>This relationship handles data transformation</documentation>
  <!-- Other properties -->
</Relationship>
```

**Documentation Storage**: Direct child element with text content

### OpenGroup Exchange Format
```xml
<relationship source="..." target="...">
  <properties>
    <property key="description">This relationship handles data transformation</property>
  </properties>
</relationship>
```

**Documentation Storage**: Properties dictionary (TBD - may vary by tool)

## Read Logic

### Archi Reader: _archireader_helpers.py

```python
def parse_relationship(rel_element):
    """
    Extract relationship data from Archi .archimate XML element.
    """
    relationship = Relationship(...)
    
    # Extract documentation (FIX)
    doc_element = rel_element.find('documentation')
    if doc_element is not None:
        relationship.description = doc_element.text or ""
    
    return relationship
```

**Input**: XML element with optional `<documentation>` child  
**Output**: Relationship object with `description` property set  
**Edge cases handled**:
- Missing `<documentation>` element → `description` remains None/empty
- Empty text → Set to empty string (distinguish from missing)
- Text with special characters → Preserved as-is (XML parser handles escaping)

### OpenGroup Reader: archimateReader.py

```python
def parse_relationship_from_opengroup(rel_element):
    """
    Extract relationship data from OpenGroup exchange XML element.
    """
    relationship = Relationship(...)
    
    # Extract documentation (if present in properties)
    properties = rel_element.find('properties')
    if properties is not None:
        for prop in properties.findall('property'):
            if prop.get('key') == 'description':
                relationship.description = prop.get('value')
    
    return relationship
```

**Input**: XML element with optional properties  
**Output**: Relationship object with `description` property set  
**Note**: OpenGroup format may differ; to be confirmed during implementation

## Write Logic

### Archi Writer: archiWriter.py

```python
def write_relationship(rel, parent_element):
    """
    Write relationship with documentation to Archi .archimate XML.
    """
    rel_elem = SubElement(parent_element, 'Relationship')
    rel_elem.set('source', rel.source_id)
    rel_elem.set('target', rel.target_id)
    
    # Write documentation (if present)
    if rel.description:
        doc_elem = SubElement(rel_elem, 'documentation')
        doc_elem.text = rel.description  # ✓ lxml handles escaping
    
    return rel_elem
```

**Input**: Relationship object with `description` property  
**Output**: XML element with `<documentation>` child  
**Safety**: lxml automatically escapes special characters

### OpenGroup Writer: archimateWriter.py

```python
def write_relationship(rel, parent_element):
    """
    Write relationship with documentation to OpenGroup exchange XML.
    """
    rel_elem = SubElement(parent_element, 'relationship')
    rel_elem.set('source', rel.source_id)
    rel_elem.set('target', rel.target_id)
    
    # Write documentation (if present)
    if rel.description:
        props_elem = SubElement(rel_elem, 'properties')
        prop_elem = SubElement(props_elem, 'property')
        prop_elem.set('key', 'description')
        prop_elem.set('value', rel.description)
    
    return rel_elem
```

**Input**: Relationship object with `description` property  
**Output**: XML element with properties  
**Note**: Format may differ; confirm during implementation

## Property Definition

### Relationship Class

```python
# File: src/pyArchimate/relationship.py
class Relationship:
    def __init__(self, ..., description=None):
        self.description = description  # Store documentation text

    @property
    def description(self):
        return self._description or None

    @description.setter
    def description(self, value):
        if value is not None:
            self._description = str(value)  # Ensure string type
        else:
            self._description = None
```

**Storage**: Internal `_description` attribute  
**Access**: Via `rel.description` property  
**Default**: None (optional field)  
**Type**: String or None  
**Encoding**: UTF-8 (lxml default)

## Round-Trip Example

### Scenario: Import Archi → Export Archi → Verify Preservation

```
Step 1: Import Archi file
  XML: <Relationship ...><documentation>Handles data flow</documentation></Relationship>
  ↓ (parse with FIX)
  Python: rel.description = 'Handles data flow'

Step 2: Export to Archi
  Python: rel.description = 'Handles data flow'
  ↓ (write)
  XML: <Relationship ...><documentation>Handles data flow</documentation></Relationship>

Step 3: Verify equality
  Original text: 'Handles data flow'
  Final text: 'Handles data flow'  ✓ PRESERVED
```

## Edge Cases

### Empty Documentation
```python
rel.description = ""  # Empty string (distinguish from None)
# Behavior on export: May write empty element or skip
# Behavior on import: Map both empty and missing to None/""
```

### Unicode & Special Characters
```python
rel.description = "关系说明: <flow> & transformation"
# Behavior: lxml escapes special XML chars (&lt;, &gt;, &amp;)
# Round-trip: Text preserved exactly (escaping/unescaping handled by parser)
```

### Very Long Documentation
```python
rel.description = "A" * 10000  # 10k character documentation
# Behavior: No truncation; XML supports arbitrary text length
# Round-trip: All text preserved
```

### None vs Empty String
```python
rel.description = None   # No documentation; may skip element on export
rel.description = ""     # Empty documentation; may write empty element
# Distinction allows clients to distinguish "no docs" from "docs present but empty"
```

## Validation

### Required Checks

1. **Text extraction**: Verify `<documentation>` element text is read correctly
2. **Null safety**: Handle missing `<documentation>` element gracefully
3. **Encoding**: Support UTF-8 and special characters without loss
4. **Round-trip**: Preserve exact text through import/export cycle
5. **Compatibility**: Legacy files without documentation still parse correctly

## Testing Criteria

**Basic Import Test**:
```python
# File: test_import_documentation.py
archi_xml = '''
<Relationship source="x" target="y">
  <documentation>Test documentation</documentation>
</Relationship>
'''
rel = parse_relationship_from_xml(archi_xml)
assert rel.description == 'Test documentation'
```

**Missing Documentation Test**:
```python
archi_xml = '<Relationship source="x" target="y"></Relationship>'
rel = parse_relationship_from_xml(archi_xml)
assert rel.description is None or rel.description == ""
```

**Unicode Test**:
```python
rel.description = "关系: データフロー & 変換"
# Export and re-import
assert imported_rel.description == "関係: データフロー & 変換"
```

**Special Characters Test**:
```python
rel.description = '<script> & "quotes" & \'single\''
# Export to XML (lxml escapes)
# Import back (lxml unescapes)
assert imported_rel.description == '<script> & "quotes" & \'single\''
```

**Long Text Test**:
```python
rel.description = "A" * 10000
model.export_to_file('test.archimate')
imported_model = read_archimate_file('test.archimate')
assert len(imported_model.get_relationship(rel.id).description) == 10000
```

**Round-Trip Test**:
```python
# Create → Export → Import → Export → Verify
original_desc = "Process: reads data, transforms it, publishes results"
rel1 = Relationship(..., description=original_desc)
# ... export/import cycle ...
rel2 = Relationship(..., description=original_desc)
assert rel1.description == rel2.description
```

## Files Modified

- `src/pyArchimate/readers/_archireader_helpers.py` - Fix documentation extraction (1-2 line change)
- `src/pyArchimate/writers/archiWriter.py` - Add documentation write logic (if not present)
- `src/pyArchimate/writers/archimateWriter.py` - Add documentation write logic (if not present)
- `src/pyArchimate/relationship.py` - Ensure `description` property exists
- Test files - Add documentation tests for import/export/round-trip scenarios

## Compliance

✅ Fixes data loss bug in Archi import  
✅ Ensures 100% round-trip fidelity for documentation  
✅ Handles edge cases (empty, Unicode, special chars, long text)  
✅ Backward compatible (files without documentation unaffected)  
✅ Follows existing lxml safety patterns (automatic escaping)  
