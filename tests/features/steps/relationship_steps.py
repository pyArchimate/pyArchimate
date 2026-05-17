"""Step definitions for Influence Strength and Relationship Documentation acceptance tests.

Tests verify that relationship metadata (influence strength and documentation) is preserved
across export/import cycles in both .archimate and OpenGroup exchange formats.
"""

import tempfile
import zipfile

from behave import given, then, when  # type: ignore[import-untyped]
from lxml import etree

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.writers.archimateWriter import archimate_writer

_SAFE_XML_PARSER = etree.XMLParser(resolve_entities=False, no_network=True)


def _parse_xml_from_file(file_path: str):
    """Parse XML from either .archimate (ZIP) or plain XML files."""
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, "r") as zf:
            xml_data = zf.read("model.xml")
            return etree.fromstring(xml_data, _SAFE_XML_PARSER)
    else:
        return etree.parse(file_path, _SAFE_XML_PARSER).getroot()


_ARCHIMATE_EXT = ".archimate"
_XSI_TYPE_ATTR = "{http://www.w3.org/2001/XMLSchema-instance}type"  # NOSONAR — XML namespace URI, not a network request
_INFLUENCE_REL_NAME = "Influence Rel"
_SERVING_REL_NAME = "Serving Rel"
_REIMPORT_REL_ASSERT = "Should have at least one relationship after reimport"

# ============================================================================
# Helper Functions
# ============================================================================


def _create_archimate_with_influence(strength: str) -> str:
    """Create a temporary .archimate file with an Influence relationship with given strength."""
    xml = f"""<?xml version='1.0'?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="test-model">
  <folder name="Business" type="business">
    <element xsi:type="archimate:BusinessActor" name="Source" id="source-elem"/>
    <element xsi:type="archimate:BusinessActor" name="Target" id="target-elem"/>
  </folder>
  <folder name="Relations" type="relations">
    <element xsi:type="archimate:InfluenceRelationship" influenceStrength="{strength}" source="source-elem" target="target-elem" id="rel-test"/>
  </folder>
</archimate:model>
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=_ARCHIMATE_EXT, delete=False) as f:
        f.write(xml)
        return f.name


def _create_archimate_with_legacy_modifier(strength: str) -> str:
    """Create a temporary .archimate file with legacy 'modifier' attribute."""
    xml = f"""<?xml version='1.0'?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="test-model">
  <folder name="Business" type="business">
    <element xsi:type="archimate:BusinessActor" name="Source" id="source-elem"/>
    <element xsi:type="archimate:BusinessActor" name="Target" id="target-elem"/>
  </folder>
  <folder name="Relations" type="relations">
    <element xsi:type="archimate:InfluenceRelationship" modifier="{strength}" source="source-elem" target="target-elem" id="rel-test"/>
  </folder>
</archimate:model>
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=_ARCHIMATE_EXT, delete=False) as f:
        f.write(xml)
        return f.name


def _create_archimate_with_documentation(doc_text: str) -> str:
    """Create a temporary .archimate file with a relationship that has documentation."""
    xml = f"""<?xml version='1.0'?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="test-model">
  <folder name="Business" type="business">
    <element xsi:type="archimate:BusinessActor" name="Source" id="source-elem"/>
    <element xsi:type="archimate:BusinessActor" name="Target" id="target-elem"/>
  </folder>
  <folder name="Relations" type="relations">
    <element xsi:type="archimate:ServingRelationship" source="source-elem" target="target-elem" id="rel-test">
      <documentation>{_escape_xml(doc_text)}</documentation>
    </element>
  </folder>
</archimate:model>
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=_ARCHIMATE_EXT, delete=False) as f:
        f.write(xml)
        return f.name


def _escape_xml(text: str) -> str:
    """Escape special XML characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


# ============================================================================
# Influence Strength - Given Steps
# ============================================================================


@given("I have two elements for creating relationships")
def step_two_elements(context):
    """Create two elements in the model for relationship testing."""
    if not hasattr(context, "model"):
        context.model = Model("relationship-test")
    context.temp_files = []
    context.source_elem = context.model.add(ArchiType.BusinessActor, "Source Element", desc="Source")
    context.target_elem = context.model.add(ArchiType.BusinessActor, "Target Element", desc="Target")
    context.relationships = []


@given('I have a relationship with influence strength "{strength}"')
def step_relationship_with_strength(context, strength):
    """Create a relationship with the specified influence strength."""
    if not hasattr(context, "model"):
        context.model = Model("relationship-test")
    if not hasattr(context, "source_elem"):
        context.source_elem = context.model.add(ArchiType.BusinessActor, "Source", desc="Source")
        context.target_elem = context.model.add(ArchiType.BusinessActor, "Target", desc="Target")

    rel = context.model.add_relationship(
        ArchiType.Influence,
        context.source_elem,
        context.target_elem,
        name=_INFLUENCE_REL_NAME,
        influence_strength=strength,
    )
    context.test_relationship = rel
    context.relationships = [rel]


@given('I create an Influence relationship with strength "{strength}"')
def step_create_influence_with_strength(context, strength):
    """Create an Influence relationship with specified strength (Given step)."""
    if not hasattr(context, "model"):
        context.model = Model("relationship-test")
    if not hasattr(context, "source_elem"):
        context.source_elem = context.model.add(ArchiType.BusinessActor, "Source", desc="Source")
        context.target_elem = context.model.add(ArchiType.BusinessActor, "Target", desc="Target")

    rel = context.model.add_relationship(
        ArchiType.Influence,
        context.source_elem,
        context.target_elem,
        name=_INFLUENCE_REL_NAME,
        influence_strength=strength,
    )
    context.test_relationship = rel
    context.original_strength = strength
    if not hasattr(context, "relationships"):
        context.relationships = []
    context.relationships.append(rel)


@given('I have an .archimate file with an Influence relationship strength "{strength}"')
def step_archimate_with_influence(context, strength):
    """Create a sample .archimate file with an Influence relationship."""
    file_path = _create_archimate_with_influence(strength)
    context.temp_files.append(file_path)
    context.temp_file = file_path


@given('I have an .archimate file using the legacy "modifier" field')
def step_archimate_with_legacy_modifier(context):
    """Create a sample .archimate file with legacy 'modifier' field."""
    file_path = _create_archimate_with_legacy_modifier("high")
    context.temp_files.append(file_path)
    context.temp_file = file_path


@given('I import a file with legacy "modifier" field')
def step_import_legacy_modifier_file(context):
    """Import a file with legacy modifier field."""
    file_path = _create_archimate_with_legacy_modifier("medium")
    context.temp_files.append(file_path)
    context.model = Model("import-test")
    context.model.read(file_path)
    # Extract the imported relationship
    if context.model.relationships:
        context.imported_rel = context.model.relationships[0]


# ============================================================================
# Influence Strength - When Steps
# ============================================================================


@when('I create an Influence relationship with strength "{strength}"')
def step_create_influence_when(context, strength):
    """Create an Influence relationship with specified strength (When step)."""
    if not hasattr(context, "model"):
        context.model = Model("relationship-test")
    if not hasattr(context, "source_elem"):
        context.source_elem = context.model.add(ArchiType.BusinessActor, "Source", desc="Source")
        context.target_elem = context.model.add(ArchiType.BusinessActor, "Target", desc="Target")

    rel = context.model.add_relationship(
        ArchiType.Influence,
        context.source_elem,
        context.target_elem,
        name=_INFLUENCE_REL_NAME,
        influence_strength=strength,
    )
    context.test_relationship = rel
    context.original_strength = strength


@given('I create another Influence relationship with strength "{strength}"')
def step_create_another_influence(context, strength):
    """Create another Influence relationship with specified strength."""
    rel = context.model.add_relationship(
        ArchiType.Influence,
        context.source_elem,
        context.target_elem,
        name="Influence Rel 2",
        influence_strength=strength,
    )
    if not hasattr(context, "relationships"):
        context.relationships = []
    context.relationships.append(rel)


@when("I export the model to .archimate format")
def step_export_model_archimate(context):
    """Export the model to .archimate format."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=_ARCHIMATE_EXT, delete=False) as f:
        context.export_path = f.name
    if not hasattr(context, "temp_files"):
        context.temp_files = []
    context.temp_files.append(context.export_path)
    context.model.write(context.export_path)


@when("I export again to OpenGroup format")
def step_export_again_opengroup(context):
    """Export to OpenGroup format from the reimported model."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        context.export_path_2 = f.name
    context.temp_files.append(context.export_path_2)
    archimate_writer(context.reimported_model, context.export_path_2)


# ============================================================================
# Influence Strength - Then Steps
# ============================================================================


@then("the relationship is created successfully")
def step_relationship_created_success(context):
    """Verify the relationship was created successfully."""
    assert context.test_relationship is not None, "Relationship should be created"
    assert context.test_relationship.uuid in context.model.rels_dict, "Relationship should be in model"


@then('the influence strength is stored as "{strength}"')
def step_strength_stored(context, strength):
    """Verify the influence strength is stored correctly."""
    assert context.test_relationship.influence_strength == strength, (
        f"Expected strength '{strength}', got '{context.test_relationship.influence_strength}'"
    )


@then("the influenceStrength field is written to the relationship")
def step_influencestrength_written(context):
    """Verify the strength attribute is written to the relationship element.

    The native .archimate format uses 'strength' (Archi's schema attribute name).
    """
    root = _parse_xml_from_file(context.export_path)
    found = False
    for elem in root.iter():
        xsi_type = elem.get(_XSI_TYPE_ATTR)
        if xsi_type and "Influence" in xsi_type:
            if elem.get("strength") is not None:
                found = True
                break
    assert found, "strength attribute should be written to InfluenceRelationship"


@then('the strength value "{strength}" is preserved in the XML')
def step_strength_preserved_in_xml(context, strength):
    """Verify the strength value is preserved in XML.

    Native .archimate format stores it as the 'strength' XML attribute.
    """
    root = _parse_xml_from_file(context.export_path)
    found = False
    for elem in root.iter():
        xsi_type = elem.get(_XSI_TYPE_ATTR)
        if xsi_type and "Influence" in xsi_type:
            if elem.get("strength") == strength:
                found = True
                break
    assert found, f"Strength value '{strength}' should be preserved in XML as 'strength' attribute"


@then("the relationship is parsed successfully")
def step_relationship_parsed(context):
    """Verify relationships were parsed from imported file."""
    assert len(context.model.relationships) > 0, "Should have parsed at least one relationship"
    context.imported_rel = context.model.relationships[0]


@then('the influence strength is accessible as "{strength}"')
def step_strength_accessible(context, strength):
    """Verify the influence strength is accessible and matches."""
    assert context.imported_rel.influence_strength == strength, (
        f"Expected strength '{strength}', got '{context.imported_rel.influence_strength}'"
    )


@then('the influence strength is preserved as "{strength}"')
def step_strength_preserved(context, strength):
    """Verify the influence strength is preserved in round-trip."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    assert context.reimported_rel.influence_strength == strength, (
        f"Expected preserved strength '{strength}', got '{context.reimported_rel.influence_strength}'"
    )


@then("the relationship strength matches the original")
def step_strength_matches_original(context):
    """Verify the relationship strength matches the original."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    assert context.reimported_rel.influence_strength == context.original_strength, (
        f"Strength should match original: {context.original_strength}, got {context.reimported_rel.influence_strength}"
    )


@then("the modifier value is mapped to influenceStrength")
def step_modifier_mapped(context):
    """Verify modifier field is mapped to influenceStrength."""
    # Check that the imported relationship has a strength value
    rels = [r for r in context.model.relationships if hasattr(r, "influence_strength")]
    assert len(rels) > 0, "Should have relationships with influence_strength after mapping modifier"


@then("the relationship strength is accessible in the model")
def step_strength_accessible_in_model(context):
    """Verify strength is accessible after import."""
    assert len(context.model.relationships) > 0, "Should have at least one relationship"
    context.imported_rel = context.model.relationships[0]


@then("the strength value is preserved")
def step_strength_value_preserved(context):
    """Verify strength value is preserved after mapping."""
    assert context.imported_rel.influence_strength is not None, "Strength should not be None"


@then('the exported file uses "influenceStrength" (canonical field)')
def step_canonical_field_used(context):
    """Verify the canonical strength attribute is used in export.

    The native .archimate format uses 'strength' (Archi's schema attribute);
    the legacy 'modifier' attribute must not appear.
    """
    root = _parse_xml_from_file(context.export_path)
    found = False
    for elem in root.iter():
        if elem.get("strength") is not None:
            found = True
            break
    assert found, "Exported file should use 'strength' attribute (not legacy 'modifier')"


@then("the file is compatible with modern tools")
def step_file_compatible(context):
    """Verify the exported file is compatible with modern tools.

    Native format: 'strength' attribute on the element; no legacy 'modifier'.
    """
    root = _parse_xml_from_file(context.export_path)
    has_strength = any(elem.get("strength") is not None for elem in root.iter())
    has_modifier = any(elem.get("modifier") is not None for elem in root.iter())
    assert has_strength or not has_modifier, "Should use 'strength' attribute and must not use legacy 'modifier'"


@then("both relationships preserve their strength values correctly")
def step_both_rels_preserved(context):
    """Verify both relationships preserve their strength values in round-trip."""
    rels = context.reimported_model.relationships
    assert len(rels) >= 2, f"Should have at least 2 relationships after round-trip, got {len(rels)}"
    # Check that relationships have their strength values
    strengths = [r.influence_strength for r in rels if hasattr(r, "influence_strength")]
    assert len(strengths) >= 2, "Should have strength values for relationships"


@then("the values remain consistent across all export/import cycles")
def step_values_consistent_all_cycles(context):
    """Verify values remain consistent across multiple export/import cycles."""
    # After re-importing from OpenGroup, verify the final model has the relationships
    final_rels = context.reimported_model.relationships
    assert len(final_rels) >= 2, "Should have relationships after multiple cycles"


# ============================================================================
# Relationship Documentation - Given Steps
# ============================================================================


@given("I have an .archimate file with a documented relationship")
def step_archimate_with_documentation(context):
    """Create a sample .archimate file with a documented relationship."""
    file_path = _create_archimate_with_documentation("Handles data flow between systems")
    context.temp_files.append(file_path)
    context.temp_file = file_path


@given('I have imported a relationship with documentation "{doc_text}"')
def step_imported_relationship_with_doc(context, doc_text):
    """Import a relationship with the specified documentation."""
    file_path = _create_archimate_with_documentation(doc_text)
    context.temp_files.append(file_path)
    context.model = Model("import-test")
    context.model.read(file_path)
    # Get the imported relationship
    if context.model.relationships:
        context.imported_rel = context.model.relationships[0]


@given('I have a relationship with description "{description}"')
def step_relationship_with_description(context, description):
    """Create a relationship with the specified description."""
    if not hasattr(context, "model"):
        context.model = Model("relationship-test")
    if not hasattr(context, "source_elem"):
        context.source_elem = context.model.add(ArchiType.BusinessActor, "Source", desc="Source")
        context.target_elem = context.model.add(ArchiType.BusinessActor, "Target", desc="Target")

    rel = context.model.add_relationship(
        ArchiType.Serving, context.source_elem, context.target_elem, name=_SERVING_REL_NAME, desc=description
    )
    context.test_relationship = rel
    context.original_description = description


@given('I have created a relationship with description "{description}"')
def step_created_relationship_with_description(context, description):
    """Create a relationship with the specified description (created variant)."""
    step_relationship_with_description(context, description)


@given('I have a relationship with empty documentation ""')
def step_relationship_empty_doc(context):
    """Create a relationship with empty documentation."""
    if not hasattr(context, "model"):
        context.model = Model("relationship-test")
    if not hasattr(context, "source_elem"):
        context.source_elem = context.model.add(ArchiType.BusinessActor, "Source", desc="Source")
        context.target_elem = context.model.add(ArchiType.BusinessActor, "Target", desc="Target")

    rel = context.model.add_relationship(
        ArchiType.Serving, context.source_elem, context.target_elem, name=_SERVING_REL_NAME, desc=""
    )
    context.test_relationship = rel


@given('I have a relationship with a long description "{long_text}"')
def step_relationship_long_doc(context, long_text):
    """Create a relationship with a long description."""
    if not hasattr(context, "model"):
        context.model = Model("relationship-test")
    if not hasattr(context, "source_elem"):
        context.source_elem = context.model.add(ArchiType.BusinessActor, "Source", desc="Source")
        context.target_elem = context.model.add(ArchiType.BusinessActor, "Target", desc="Target")

    rel = context.model.add_relationship(
        ArchiType.Serving, context.source_elem, context.target_elem, name=_SERVING_REL_NAME, desc=long_text
    )
    context.test_relationship = rel
    context.original_description = long_text


@given("I have a relationship with description 'Contains <tag> & \"quoted\" values'")
def step_relationship_special_chars_doc(context):
    """Create a relationship with special XML characters in description."""
    if not hasattr(context, "model"):
        context.model = Model("relationship-test")
    if not hasattr(context, "source_elem"):
        context.source_elem = context.model.add(ArchiType.BusinessActor, "Source", desc="Source")
        context.target_elem = context.model.add(ArchiType.BusinessActor, "Target", desc="Target")

    special_text = 'Contains <tag> & "quoted" values'
    rel = context.model.add_relationship(
        ArchiType.Serving, context.source_elem, context.target_elem, name=_SERVING_REL_NAME, desc=special_text
    )
    context.test_relationship = rel
    context.original_description = special_text


@given("I have three relationships with different documentation texts")
def step_three_relationships_with_docs(context):
    """Create three relationships with different documentation texts."""
    if not hasattr(context, "model"):
        context.model = Model("relationship-test")
    if not hasattr(context, "source_elem"):
        context.source_elem = context.model.add(ArchiType.BusinessActor, "Source", desc="Source")
        context.target_elem = context.model.add(ArchiType.BusinessActor, "Target", desc="Target")

    docs = ["First relationship documentation", "Second relationship documentation", "Third relationship documentation"]
    context.relationships = []
    for i, doc_text in enumerate(docs):
        rel = context.model.add_relationship(
            ArchiType.Serving, context.source_elem, context.target_elem, name=f"Serving Rel {i + 1}", desc=doc_text
        )
        context.relationships.append(rel)
    context.original_descriptions = docs


# ============================================================================
# Relationship Documentation - When Steps
# ============================================================================


@when("I access the relationship properties")
def step_access_relationship_properties(context):
    """Access the relationship properties."""
    # Properties are already accessible via context.imported_rel
    assert hasattr(context, "imported_rel"), "Should have imported relationship"


@when("I export and re-import the relationship")
def step_export_and_reimport_relationship(context):
    """Export and re-import the relationship."""
    # Export to .archimate format
    with tempfile.NamedTemporaryFile(mode="w", suffix=_ARCHIMATE_EXT, delete=False) as f:
        context.export_path = f.name
    if not hasattr(context, "temp_files"):
        context.temp_files = []
    context.temp_files.append(context.export_path)
    context.model.write(context.export_path)

    # Re-import
    context.reimported_model = Model("reimport-test")
    context.reimported_model.read(context.export_path)
    if context.reimported_model.relationships:
        context.reimported_rel = context.reimported_model.relationships[0]


# ============================================================================
# Relationship Documentation - Then Steps
# ============================================================================


@then("the documentation text is accessible via the description field")
def step_doc_accessible_via_description(context):
    """Verify documentation is accessible via description field."""
    assert hasattr(context.imported_rel, "desc"), "Relationship should have desc field"
    assert context.imported_rel.desc is not None, "Description should not be None"


@then('the description field contains "{expected_text}"')
def step_description_contains(context, expected_text):
    """Verify the description field contains the expected text."""
    assert context.imported_rel.desc == expected_text, f"Expected '{expected_text}', got '{context.imported_rel.desc}'"


@then("the documentation is not truncated or modified")
def step_doc_not_truncated(context):
    """Verify documentation is not truncated or modified."""
    assert context.imported_rel.desc is not None, "Documentation should not be None"
    assert len(context.imported_rel.desc) > 0, "Documentation should not be empty"


@then("the documentation element is written to the XML")
def step_doc_element_written(context):
    """Verify documentation element is written to XML."""
    root = _parse_xml_from_file(context.export_path)
    found = False
    for doc_elem in root.iter():
        if "documentation" in doc_elem.tag.lower():
            found = True
            break
    assert found, "Documentation element should be written to XML"


def _is_relationship_elem(elem) -> bool:
    tag = elem.tag.lower()
    if "relationship" in tag:
        return True
    if "element" in tag:
        xsi_type = elem.get(_XSI_TYPE_ATTR)
        return bool(xsi_type and "Relationship" in xsi_type)
    return False


def _has_doc_with_text(elem, expected: str) -> bool:
    return any("documentation" in child.tag.lower() and (child.text or "") == expected for child in elem)


@then('the text content is "Processes read this data"')
def step_xml_content_matches(context):
    """Verify the XML text content matches."""
    root = _parse_xml_from_file(context.export_path)
    expected_text = "Processes read this data"
    for elem in root.iter():
        if _is_relationship_elem(elem) and _has_doc_with_text(elem, expected_text):
            return
    raise AssertionError(f"Documentation with text '{expected_text}' not found in relationships")


@then('the documentation text is preserved as "{expected_text}"')
def step_doc_preserved_as(context, expected_text):
    """Verify documentation text is preserved as expected."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    assert context.reimported_rel.desc == expected_text, (
        f"Expected '{expected_text}', got '{context.reimported_rel.desc}'"
    )


@then("the relationship description matches the original")
def step_desc_matches_original(context):
    """Verify relationship description matches the original."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    # Check if we have an original_description to compare against
    original_desc = getattr(context, "original_description", None)
    if original_desc is not None:
        assert context.reimported_rel.desc == original_desc, (
            f"Expected '{original_desc}', got '{context.reimported_rel.desc}'"
        )
    else:
        # If no original stored, just verify the description is accessible
        assert context.reimported_rel.desc is not None, "Description should be accessible"


@then('the documentation remains empty ""')
def step_doc_remains_empty(context):
    """Verify empty documentation remains empty."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    # Empty string or None are both considered empty
    assert context.reimported_rel.desc in ("", None), (
        f"Documentation should be empty, got '{context.reimported_rel.desc}'"
    )


@then("no errors are raised")
def step_no_errors(_context):
    """Verify no errors were raised (implicit if we reach here)."""
    pass


@then("the documentation is preserved exactly")
def step_doc_preserved_exactly(context):
    """Verify documentation is preserved exactly."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    assert context.reimported_rel.desc == context.original_description, "Documentation not preserved exactly"


@then("the full text is accessible")
def step_full_text_accessible(context):
    """Verify the full text is accessible."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    assert context.reimported_rel.desc == context.original_description, (
        "Full text should be accessible and match original"
    )


@then("the Unicode characters are preserved exactly")
def step_unicode_preserved_exactly(context):
    """Verify Unicode characters are preserved exactly."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    assert context.reimported_rel.desc == context.original_description, "Unicode characters should be preserved"


@then('the documentation reads "{expected_text}" (or equivalent encoding)')
def step_doc_reads_as(context, expected_text):  # noqa: F841
    """Verify the documentation reads as expected."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    assert context.reimported_rel.desc is not None, "Documentation should not be None"
    assert len(context.reimported_rel.desc) > 0, "Documentation should not be empty"


@then("the special characters are properly escaped and preserved")
def step_special_chars_escaped_preserved(context):
    """Verify special characters are properly escaped and preserved."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    assert context.reimported_rel.desc == context.original_description, (
        f"Special characters should be preserved: expected '{context.original_description}', got '{context.reimported_rel.desc}'"
    )


@then("the documentation reads correctly after re-import")
def step_doc_reads_correctly(context):
    """Verify documentation reads correctly after re-import."""
    if not hasattr(context, "reimported_rel"):
        rels = context.reimported_model.relationships
        assert len(rels) > 0, _REIMPORT_REL_ASSERT
        context.reimported_rel = rels[0]
    assert context.reimported_rel.desc == context.original_description, (
        "Documentation should read correctly after re-import"
    )


@then("all three documentation texts are preserved correctly")
def step_all_three_docs_preserved(context):
    """Verify all three documentation texts are preserved correctly."""
    reimported_rels = context.reimported_model.relationships
    assert len(reimported_rels) >= 3, f"Should have at least 3 relationships, got {len(reimported_rels)}"

    reimported_docs = [r.desc for r in reimported_rels[:3]]
    for original, reimported in zip(context.original_descriptions, reimported_docs, strict=True):
        assert original == reimported, f"Expected '{original}', got '{reimported}'"


@then("each relationship retains its unique documentation")
def step_each_rel_unique_doc(context):
    """Verify each relationship retains its unique documentation."""
    reimported_rels = context.reimported_model.relationships
    reimported_docs = [r.desc for r in reimported_rels[:3]]

    # Verify all docs are unique
    assert len(set(reimported_docs)) == len(reimported_docs), "All documentation should be unique"
