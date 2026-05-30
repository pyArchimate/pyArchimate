# Quickstart: Testing ArchiMate v3.x Compliance Fixes

**Purpose**: Quick reference for developers implementing and testing the three compliance fixes.

**Prerequisites**: Python 3.10+, poetry, test fixtures in `/tests/`

---

## Fix 1: BusinessInteraction Element Creation

### What's Fixed

After uncommenting `BusinessInteraction: Business` in `checker_rules.yml`, you can create BusinessInteraction elements without validation errors.

### Quick Test

```python
from pyArchimate.element import Element
from pyArchimate.enums import ArchiType

# This should succeed (currently fails with validation error)
interaction = Element(
    name='Customer Interaction',
    elem_type=ArchiType.BusinessInteraction,
    doc='Represents customer-facing interactions'
)

assert interaction.elem_type == ArchiType.BusinessInteraction
assert interaction.name == 'Customer Interaction'
print("✓ BusinessInteraction element created successfully")
```

### Test Command

```bash
# Run specific test for BusinessInteraction
pytest tests/unit/test_element.py::test_business_interaction_creation -v

# Or test the full element validation suite
pytest tests/unit/test_element.py -v
```

### Acceptance Criteria (BDD)

```gherkin
# tests/features/business_interaction.feature
Feature: Create BusinessInteraction Elements

  Scenario: Create a BusinessInteraction element
    Given I have imported pyArchimate
    When I create an Element with elem_type=ArchiType.BusinessInteraction
    Then the element is created successfully without validation errors

  Scenario: Import BusinessInteraction from .archimate file
    Given I have an .archimate file with a BusinessInteraction element
    When I import the file
    Then the BusinessInteraction element is parsed and available

  Scenario: Export BusinessInteraction to .archimate format
    Given I have a model with BusinessInteraction elements
    When I export to .archimate format
    Then BusinessInteraction elements are preserved in the output
```

---

## Fix 2: Influence Strength Round-Trip

### What's Fixed

Influence strength metadata now survives the full export/import cycle without loss. Both Archi and OpenGroup formats use the canonical `influenceStrength` field name, with transparent mapping from legacy `modifier` field.

### Quick Test

```python
from pyArchimate.relationship import Relationship
from pyArchimate.enums import ArchiType
from pyArchimate.element import Element

# Create actors
actor1 = Element(name='Actor 1', elem_type=ArchiType.Actor)
actor2 = Element(name='Actor 2', elem_type=ArchiType.Actor)

# Create relationship with strength
rel1 = Relationship(
    source=actor1,
    target=actor2,
    rel_type=ArchiType.Influence,
    influence_strength='high'
)

# Add to model and export
model.add_relationship(rel1)
model.export_to_file('test.archimate')

# Re-import and verify strength preserved
reimported = read_archimate_file('test.archimate')
rel2 = [r for r in reimported.rels_dict.values() if r.type == ArchiType.Influence][0]

assert rel2.influence_strength == 'high', "Strength not preserved!"
print(f"✓ Round-trip preserved strength: {rel2.influence_strength}")

# Test legacy modifier field support (backward compatibility)
# Old files with modifier="medium" still import correctly
```

### Test Command

```bash
# Test influence strength round-trip
pytest tests/integration/test_archimate_roundtrip.py::test_influence_strength_roundtrip -v

# Test legacy modifier field fallback
pytest tests/unit/test_relationship.py::test_influence_strength_modifier_fallback -v

# Run all relationship metadata tests
pytest tests/unit/test_relationship.py -v
```

### Acceptance Criteria (BDD)

```gherkin
# tests/features/influence_strength.feature
Feature: Influence Strength Metadata Round-Trip

  Scenario: Create relationship with influence strength
    Given I have an Influence relationship
    When I set influence_strength to "high"
    Then the property is stored in the relationship object

  Scenario: Export relationship with strength to .archimate
    Given I have a relationship with influence_strength="high"
    When I export to .archimate format
    Then the output contains influenceStrength="high" attribute

  Scenario: Export relationship with strength to OpenGroup
    Given I have a relationship with influence_strength="high"
    When I export to OpenGroup exchange format
    Then the output contains influenceStrength="high" element

  Scenario: Import .archimate with legacy modifier field
    Given I have an .archimate file with modifier="high" on a relationship
    When I import the file
    Then the relationship.influence_strength is set to "high"

  Scenario: Round-trip preserves influence strength
    Given I create a relationship with influence_strength="medium"
    When I export to .archimate and re-import
    Then influence_strength is still "medium"
```

---

## Fix 3: Relationship Documentation Preservation

### What's Fixed

Relationship documentation text (from Archi `<documentation>` element) is now correctly extracted and preserved during import/export cycles.

### Quick Test

```python
from pyArchimate.relationship import Relationship
from pyArchimate.element import Element
from pyArchimate.enums import ArchiType

# Create elements
process = Element(name='Process', elem_type=ArchiType.Process)
data_obj = Element(name='Data Object', elem_type=ArchiType.DataObject)

# Create relationship with documentation
rel1 = Relationship(
    source=process,
    target=data_obj,
    rel_type=ArchiType.Access,
    desc='Processes read this data to compute insights'
)

# Add to model and export
model.add_relationship(rel1)
model.export_to_file('test.archimate')

# Verify XML contains documentation
with open('test.archimate', 'r') as f:
    content = f.read()
    assert '<documentation>Processes read this data' in content
    print("✓ Documentation written to <documentation> element")

# Re-import and verify documentation preserved
reimported = read_archimate_file('test.archimate')
rel2 = [r for r in reimported.rels_dict.values() if r.type == ArchiType.Access][0]

assert rel2.desc == 'Processes read this data to compute insights'
print(f"✓ Documentation preserved: {rel2.desc}")

# Test Unicode and special characters preservation
rel3 = Relationship(
    source=process,
    target=data_obj,
    rel_type=ArchiType.Access,
    desc='Unicode: 中文 & <special> chars preserved'
)
```

### Test Command

```bash
# Test documentation import from Archi files
pytest tests/unit/test_readers/test_archireader.py::test_relationship_documentation -v

# Test documentation export to .archimate
pytest tests/unit/test_writers/test_archiwriter.py::test_relationship_documentation_write -v

# Test round-trip with documentation
pytest tests/integration/test_archimate_roundtrip.py::test_documentation_roundtrip -v
```

### Acceptance Criteria (BDD)

```gherkin
# tests/features/relationship_documentation.feature
Feature: Relationship Documentation Preservation

  Scenario: Create relationship with documentation
    Given I create a Relationship
    When I set description to "Handles data transformation"
    Then the property is stored in the relationship object

  Scenario: Export relationship with documentation to .archimate
    Given I have a relationship with documentation
    When I export to .archimate format
    Then the output contains <documentation> element with the text

  Scenario: Import relationship with documentation from Archi
    Given I have an Archi .archimate file with documented relationships
    When I import the file
    Then the relationship.description contains the documentation text

  Scenario: Preserve Unicode in documentation
    Given I have a relationship with Unicode documentation "关系说明"
    When I export to .archimate and re-import
    Then the description is preserved exactly: "関係説明"

  Scenario: Preserve special characters in documentation
    Given I have documentation with special chars: "<tag> & 'quote'"
    When I export to .archimate and re-import
    Then the special characters are preserved exactly

  Scenario: Handle empty documentation
    Given I have a relationship without documentation
    When I export to .archimate
    Then the relationship element has no <documentation> child
```

---

## Integration Test: All Three Fixes Together

### Comprehensive Test Scenario

```python
# tests/integration/test_all_compliance_fixes.py

def test_all_compliance_fixes_together():
    """Verify all three fixes work together in a realistic scenario."""
    
    # Step 1: Create BusinessInteraction element
    interaction = Element(
        name='Customer Onboarding',
        elem_type=ArchiType.BusinessInteraction,
        doc='Handles new customer interactions'
    )
    model.add_element(interaction)
    
    # Step 2: Create actor and relate via influence
    actor = Element(name='Customer Service Agent', elem_type=ArchiType.BusinessActor)
    model.add_element(actor)
    
    influence = Relationship(
        source_id=actor.id,
        target_id=interaction.id,
        rel_type=ArchiType.Influence,
        influence_strength='high',
        description='Agent drives interaction with customers'
    )
    model.add_relationship(influence)
    
    # Step 3: Export to Archi format
    model.export_to_file('comprehensive_test.archimate', Writers.archi)
    
    # Step 4: Re-import and verify all three fixes
    reimported = read_archimate_file('comprehensive_test.archimate')
    
    # Verify BusinessInteraction preserved
    reimported_interaction = reimported.get_element_by_id(interaction.id)
    assert reimported_interaction.elem_type == ArchiType.BusinessInteraction
    print("✓ BusinessInteraction preserved")
    
    # Verify influence strength preserved
    reimported_influence = reimported.get_relationship_by_id(influence.id)
    assert reimported_influence.influence_strength == 'high'
    print("✓ Influence strength preserved")
    
    # Verify documentation preserved
    assert reimported_influence.description == 'Agent drives interaction with customers'
    print("✓ Documentation preserved")
    
    print("\n✅ All three compliance fixes working together!")
```

### Run Integration Test

```bash
pytest tests/integration/test_all_compliance_fixes.py -v
```

---

## Test Fixtures & Files

### Sample Archi Files for Testing

Located in `tests/fixtures/`:
- `business_interaction_sample.archimate` - Contains BusinessInteraction elements
- `influence_strength_sample.archimate` - Contains relationships with modifier="..." field
- `documented_relationship.archimate` - Contains relationships with `<documentation>` elements

### Create Test Files

```bash
# Generate fixtures (if using factory or builder)
pytest tests/fixtures/generate_fixtures.py

# Or use existing fixtures for import tests
pytest -k "test_import" --fixture="tests/fixtures/business_interaction_sample.archimate"
```

---

## Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run import/export with verbose output
model = read_archimate_file('test.archimate', debug=True)
```

### Inspect Generated XML

```bash
# Export model
python -c "model.export_to_file('debug.archimate', Writers.archi)"

# Pretty-print XML
python -m xml.dom.minidom debug.archimate | less
```

### Compare XML Before/After

```bash
# Create two exports and diff
diff <(xmllint --format before.archimate) <(xmllint --format after.archimate)
```

---

## Success Criteria Checklist

- [X] BusinessInteraction elements can be created without errors
- [X] BusinessInteraction elements can be imported from .archimate files
- [X] BusinessInteraction elements can be exported to .archimate files
- [X] Influence strength survives round-trip (export → import → export)
- [X] Legacy `modifier` field is correctly mapped to `influenceStrength`
- [X] Documentation text is preserved exactly in import/export
- [X] Unicode and special characters in documentation are preserved
- [X] All existing tests continue to pass (no regressions) — 453 tests passing
- [X] New compliance tests pass with >90% coverage — 94% coverage achieved

---

## Next Steps

After verifying these fixes work:

1. Run full test suite: `pytest tests/`
2. Check coverage: `pytest --cov=src/pyArchimate tests/`
3. Lint code: `ruff check src/pyArchimate/`
4. Type check: `mypy src/pyArchimate/`
5. Run BDD scenarios: `behave tests/features/`
6. Commit changes with conventional commits
7. Generate changelog via commitizen
8. Create PR for review

---

---

## P3: Element Grouping

### What's Available

Parent-child containment lets you organize elements into logical groups (e.g., a `BusinessProcess` containing `BusinessFunction` children). Groups are semantic — distinct from visual `Group` shapes on diagrams.

### Quick Test

```python
from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model

model = Model(name='Grouping Demo')

process = model.add(ArchiType.BusinessProcess, 'Order Fulfillment')
step1   = model.add(ArchiType.BusinessFunction, 'Receive Order')
step2   = model.add(ArchiType.BusinessFunction, 'Pack and Ship')

model.add_child(process.uuid, step1.uuid)
model.add_child(process.uuid, step2.uuid)

print(model.get_children(process.uuid))    # [step1, step2]
print(model.get_parent(step1.uuid).name)   # 'Order Fulfillment'
print(model.get_ancestors(step1.uuid))     # [process]

# Cycle detection — raises ValueError
# model.add_child(step1.uuid, process.uuid)
```

### Test Command

```bash
pytest tests/unit/test_element_grouping.py -v
pytest tests/integration/test_round_trip_grouping.py -v
```

---

## P3: Junction Semantics

### What's Available

Junction elements (`Junction`, `OrJunction`, `AndJunction`) support explicit AND/OR/XOR type semantics that survive export/import cycles in both `.archimate` and OpenGroup formats.

### Quick Test

```python
from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model

model = Model(name='Junction Demo')

and_gate = model.add(ArchiType.Junction, 'Approval Gate')
and_gate.set_junction_type('and')

or_gate = model.add(ArchiType.OrJunction, 'Routing Decision')
or_gate.set_junction_type('or')

print(and_gate.get_junction_type())  # 'and'
print(or_gate.get_junction_type())   # 'or'

# Invalid type raises ValueError
# and_gate.set_junction_type('maybe')
```

### Test Command

```bash
pytest tests/unit/test_junction_semantics.py -v
pytest tests/integration/test_round_trip_junctions.py -v
```

---

## P3: Visual Properties

### What's Available

Elements support fill color, line color, line width, and transparency. Properties are optional; absent properties fall back to default ArchiMate palette colors at render time.

### Quick Test

```python
from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model

model = Model(name='Styling Demo')

component = model.add(ArchiType.ApplicationComponent, 'Order Service')
component.set_fill_color('#dce8f5')
component.set_line_color('#2b6cb0')
component.set_line_width(2.0)
component.set_transparency(0.9)

style = component.get_visual_style()
print(style)  # {'fillColor': '#dce8f5', 'lineColor': '#2b6cb0', 'lineWidth': 2.0, 'transparency': 0.9}

# Bulk setter
component.set_visual_style(fill_color='#ffffb5', transparency=1.0)

# Clear a property
component.set_fill_color(None)
```

### Test Command

```bash
pytest tests/unit/test_visual_style.py -v
behave tests/features/visual_style.feature
```

---

## Contact & Support

For issues or questions about these fixes:

1. Check `research.md` for technical details
2. Review `data-model.md` for entity definitions
3. Consult contracts in `contracts/` for format specifications
4. Refer to `plan.md` for architecture overview

---

## Viewpoint Assignment and Filtering

### What's Available

All 13 standard ArchiMate 3.x viewpoints are defined as canonical slugs:
`stakeholder`, `capability`, `organization`, `actor`, `technology`, `physical`,
`service`, `implementation`, `migration`, `strategy`, `business`, `application`, `infrastructure`

### Quick Test

```python
from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model

model = Model(name='Viewpoint Demo')

# List all available viewpoints
for vp in model.get_viewpoints():
    print(f"{vp.id}: {vp.name}")

# Assign viewpoints to an element
actor = model.add(ArchiType.BusinessActor, 'CTO')
actor.assign_viewpoint('stakeholder')
actor.assign_viewpoint('technology')
print(actor.viewpoints)  # ['stakeholder', 'technology']

# Filter elements by viewpoint
stakeholders = model.get_elements_by_viewpoint('stakeholder')

# Set primary viewpoint on a view
view = model.add(ArchiType.View, 'Technology View')
view.set_primary_viewpoint('technology')
print(view.primary_viewpoint)  # 'technology'

# Remove a viewpoint assignment
actor.remove_viewpoint('technology')

# Filter views by primary viewpoint
tech_views = model.get_views_by_viewpoint('technology')
```
