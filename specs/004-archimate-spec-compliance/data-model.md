# Data Model: ArchiMate v3.x Compliance

**Phase**: 1 - Design  
**Date**: 2026-04-30  
**Status**: Design specification

---

## Entity: BusinessInteraction (Element subtype)

**Description**: An ArchiMate business layer element representing business-level interaction concepts.

**Source**: ArchiMate 3.x specification; already present in pyArchimate `ArchiType` enum.

**Properties**:
- `name` (string, required): Element identifier
- `elem_type` (ArchiType): Set to `ArchiType.BusinessInteraction`
- `doc` / `description` (string, optional): Documentation text
- `properties` (dict): Optional key-value metadata

**Validation Rules**:
- `elem_type` must be registered in `ARCHI_CATEGORY` (checklist: uncomment in checker_rules.yml)
- Once registered, Element.__init__ will validate and accept it without errors

**Relationships**:
- Inherits all standard ArchiMate relationship types (influences, realizes, associates, etc.)
- No new relationship types specific to BusinessInteraction

**Lifecycle**:
1. Create: `Element(name='Interaction X', elem_type=ArchiType.BusinessInteraction)`
2. Relate: Add relationships to other elements via relationship rules
3. Export: Serialize to .archimate or OpenGroup exchange format
4. Import: Deserialize from external files

**Example Usage**:

```python
from pyArchimate.element import Element
from pyArchimate.enums import ArchiType

interaction = Element(
    name='Customer Service Interaction',
    elem_type=ArchiType.BusinessInteraction,
    doc='Represents customer-service interactions'
)
model.add_element(interaction)
```

---

## Entity: InfluenceRelationship (Relationship enhancement)

**Description**: A relationship that carries strength metadata (influence level) between two elements.

**Properties**:
- `source_id` (string): Source element ID
- `target_id` (string): Target element ID
- `rel_type` (ArchiType): Relationship type (e.g., Influence)
- `influence_strength` (string): Strength value (e.g., "high", "medium", "low" or numeric)
- `properties` (dict): Additional metadata

**Field Mapping** (canonical: `influence_strength`):
| Layer | Field Name | Storage |
|-------|-----------|---------|
| Python | `influence_strength` | Relationship property |
| OpenGroup XML | `influenceStrength` | Element attribute/text |
| Archi .archimate | `influenceStrength` | Element attribute (with fallback to `modifier` on read) |

**Validation Rules**:
- `influence_strength` value must conform to ArchiMate spec (valid values: TBD in implementation)
- Optional field (relationships may not have strength metadata)

**Round-Trip Behavior**:

```
Create: Relationship(influence_strength='high')
  ↓ (export to .archimate)
Write: <Relationship ... influenceStrength="high" />
  ↓ (import from .archimate)
Read: Maps influenceStrength → influence_strength property
  ↓ (export again)
Write: <Relationship ... influenceStrength="high" /> ✓ Preserved
```

**Legacy Compatibility**:
- Reader checks for `influenceStrength` first
- Falls back to `modifier` field if `influenceStrength` not found
- Stores result in `influence_strength` property (consistent)
- On export, always writes as `influenceStrength` (canonical form)

**Example Usage**:

```python
from pyArchimate.relationship import Relationship
from pyArchimate.enums import ArchiType

influence = Relationship(
    source_id='actor1',
    target_id='actor2',
    rel_type=ArchiType.Influence,
    influence_strength='high'
)
model.add_relationship(influence)
```

---

## Entity: DocumentedRelationship (Relationship enhancement)

**Description**: A relationship that carries documentation metadata (description/notes) about the relationship purpose.

**Properties**:
- `source_id` (string): Source element ID
- `target_id` (string): Target element ID
- `rel_type` (ArchiType): Relationship type
- `description` (string, optional): Documentation text
- `properties` (dict): Additional metadata

**Field Mapping** (canonical: `description`):
| Layer | Field Name | Storage |
|-------|-----------|---------|
| Python | `description` | Relationship property |
| Archi .archimate | `<documentation>` XML element text | XML text node |

**Preservation Rules**:
- Document exact text content without modification
- Handle encoding properly (UTF-8, special XML characters)
- Support empty documentation (empty string)
- Support long documentation (no truncation)

**Import Logic**:

```python
# In _archireader_helpers.py, relationship parser:
documentation_element = relationship_xml.find('documentation')
if documentation_element is not None:
    relationship.description = documentation_element.text  # Extract text
```

**Export Logic**:

```python
# In writers:
if relationship.description:
    doc_elem = SubElement(rel_xml, 'documentation')
    doc_elem.text = relationship.description
```

**Round-Trip Behavior**:

```
Import: <Relationship><documentation>Handles data flow between systems</documentation></Relationship>
  ↓ (store)
Python: relationship.description = "Handles data flow between systems"
  ↓ (export)
Write: <Relationship><documentation>Handles data flow between systems</documentation></Relationship> ✓ Preserved
```

**Edge Cases**:
- Empty documentation: `relationship.description = ""` (valid)
- Unicode characters: "关系説明" (should preserve exactly)
- Special XML characters: `<>&"'` (must be escaped by XML writer)
- Very long text: Support arbitrary length (no truncation)

**Example Usage**:

```python
relationship = Relationship(
    source_id='process1',
    target_id='data1',
    rel_type=ArchiType.Access,
    description='Processes read this data to compute insights'
)
model.add_relationship(relationship)
```

---

## Validation Constraints

**BusinessInteraction Validation**:
- Element creation must pass `ARCHI_CATEGORY` check
- Error message if category not found (currently raises exception)
- Once uncommented in checker_rules.yml, validation succeeds

**Influence Strength Validation**:
- Optional field (not required)
- If present, value must match ArchiMate specification constraints
- No type conversion (stored as string to match spec field type)

**Documentation Validation**:
- Optional field (not required)
- Stored as string (XML parser provides text)
- No length limits (XML can handle arbitrary text)
- Encoding: UTF-8 (lxml default)

---

## State Transitions

No new state transitions introduced. All entities follow existing ArchiMate element/relationship lifecycles.

**Element Lifecycle** (BusinessInteraction):

```
NEW → CREATED → RELATED → EXPORTED → IMPORTED → (cycle repeats)
```

**Relationship Lifecycle** (with metadata):

```
NEW → CREATED → (with properties) → EXPORTED → IMPORTED → (properties preserved)
```

---

## Integration Points

**With Element class** (`src/pyArchimate/element.py`):
- BusinessInteraction validation hook: `ARCHI_CATEGORY[elem_type]`
- No new fields required; uses base Element properties

**With Relationship class** (`src/pyArchimate/relationship.py`):
- New properties: `influence_strength`, `description`
- Existing `properties` dict can hold additional metadata
- No new methods required

**With Readers** (`src/pyArchimate/readers/*.py`):
- archimateReader: Extract `influenceStrength` (with `modifier` fallback)
- _archireader_helpers: Extract `<documentation>` element text
- Mapping: Field name → Python property

**With Writers** (`src/pyArchimate/writers/*.py`):
- archiWriter: Write `influenceStrength` to .archimate format
- archimateWriter: Write `influenceStrength` to OpenGroup format
- Mapping: Python property → Field name

---

## Testing Strategy

**Unit Tests** (Isolation) - 8 tests completed:
- [X] Create BusinessInteraction element → verify no validation error (test_create_business_interaction)
- [X] Import BusinessInteraction from both .archimate and OpenGroup formats
- [X] Export BusinessInteraction to both .archimate and OpenGroup formats
- [X] Create Relationship with influence_strength → verify property stored
- [X] Read from XML with `modifier` → verify fallback works (test_influence_strength_legacy_modifier_fallback)
- [X] Write to XML → verify field names used (test_influence_strength_field_consistency)
- [X] Create Relationship with documentation → verify property stored
- [X] Read documentation from `<documentation>` element → verify correct extraction

**Integration Tests** (Round-trip) - 6 tests completed:
- [X] Create BusinessInteraction → export → import → verify identical (test_business_interaction_roundtrip)
- [X] Create Relationship with strength → export → import → verify strength preserved (test_influence_strength_complete_roundtrip)
- [X] Import legacy file with `modifier` → export as `influenceStrength` → verify compatibility
- [X] Create Relationship with documentation → export → import → verify documentation preserved (test_relationship_documentation_roundtrip)
- [X] Test all edge cases: Unicode, special chars, long text (test_relationship_documentation_all_edge_cases)
- [X] All three fixes together in single model (test_all_three_fixes_together)

**Acceptance Tests** (BDD) - 25 scenarios completed:
- [X] business_interaction.feature: 4 scenarios for element creation and export/import
- [X] influence_strength.feature: 9 scenarios for round-trip and legacy field support
- [X] relationship_documentation.feature: 12 scenarios for documentation preservation and edge cases

**Coverage Results**:
- Total Tests: 453 (unit, integration, BDD combined)
- Coverage: 94% (target was 90%+)
- All tests passing ✓
- No regressions detected ✓
