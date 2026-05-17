"""Step definitions for ArchiMate 3.x BusinessInteraction acceptance tests.

Tests create, import, and export BusinessInteraction elements across .archimate
and OpenGroup exchange formats, verifying round-trip fidelity and spec compliance.
"""

import tempfile
import zipfile

from behave import given, then, when  # type: ignore[import-untyped]
from lxml import etree

from src.pyArchimate import ArchiType
from src.pyArchimate.constants import ARCHI_CATEGORY
from src.pyArchimate.model import Model
from src.pyArchimate.writers.archimateWriter import archimate_writer

_SAFE_XML_PARSER = etree.XMLParser(resolve_entities=False, no_network=True)
_OPENGROUP_NS = "http://www.opengroup.org/xsd/archimate/3.0/"  # NOSONAR — XML namespace URI, not a network request
_TEST_BI_NAME = "Test Interaction"


def _parse_xml_from_file(file_path: str):
    """Parse XML from either .archimate (ZIP) or plain XML files."""
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, "r") as zf:
            xml_data = zf.read("model.xml")
            return etree.fromstring(xml_data, _SAFE_XML_PARSER)
    else:
        return etree.parse(file_path, _SAFE_XML_PARSER).getroot()


# Helper: Create sample .archimate file with BusinessInteraction
def _create_archimate_with_bi(name: str, desc: str) -> str:
    """Create a temporary .archimate file with a BusinessInteraction element."""
    xml = f"""<?xml version='1.0'?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="test-model">
  <folder name="Business">
    <element xsi:type="archimate:BusinessInteraction" name="{name}" id="bi-test">
      <documentation>{desc}</documentation>
    </element>
  </folder>
</archimate:model>
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
        f.write(xml)
        return f.name


def _create_opengroup_with_bi(name: str, desc: str) -> str:
    """Create a temporary OpenGroup exchange file with a BusinessInteraction element."""
    xml = f"""<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/'
       xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>test-model</name>
  <elements>
    <element identifier="bi-test" xsi:type="BusinessInteraction">
      <name>{name}</name>
      <documentation>{desc}</documentation>
    </element>
  </elements>
  <relationships/>
  <views><diagrams/></views>
</model>
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml)
        return f.name


# ============================================================================
# Given Steps
# ============================================================================


@given("I have a fresh pyArchimate model")
def step_fresh_model(context):
    """Create a new empty model for testing."""
    context.model = Model("bdd-test")
    context.temp_files = []
    context.bi_element = None


@given("BusinessInteraction is enabled in the schema")
def step_bi_enabled(context):
    """Verify BusinessInteraction is registered in ARCHI_CATEGORY."""
    assert "BusinessInteraction" in ARCHI_CATEGORY, "BusinessInteraction should be registered in ARCHI_CATEGORY"
    assert ARCHI_CATEGORY["BusinessInteraction"] == "Business", "BusinessInteraction should map to Business layer"


@given("I have an .archimate file containing a BusinessInteraction element")
def step_archimate_with_bi(context):
    """Create a sample .archimate file with BusinessInteraction."""
    file_path = _create_archimate_with_bi(_TEST_BI_NAME, "Test description")
    context.temp_files.append(file_path)
    context.temp_file = file_path


@given("I have an OpenGroup exchange file containing a BusinessInteraction element")
def step_opengroup_with_bi(context):
    """Create a sample OpenGroup exchange file with BusinessInteraction."""
    file_path = _create_opengroup_with_bi(_TEST_BI_NAME, "Test description")
    context.temp_files.append(file_path)
    context.temp_file = file_path


@given("I have a model with BusinessInteraction elements")
def step_model_with_bi(context):
    """Add a BusinessInteraction element to the test model."""
    if not hasattr(context, "model"):
        context.model = Model("bdd-test")
    context.bi_element = context.model.add(
        ArchiType.BusinessInteraction, _TEST_BI_NAME, desc="Test element description"
    )


@given('I create a BusinessInteraction element named "{name}"')
def step_create_bi_given(context, name):
    """Create a BusinessInteraction element (used as Given in Scenario 4)."""
    if not hasattr(context, "model"):
        context.model = Model("bdd-test")
    context.bi_element = context.model.add(ArchiType.BusinessInteraction, name, desc="Created element")
    context.original_element = context.bi_element


# ============================================================================
# When Steps
# ============================================================================


@when('I create a BusinessInteraction element named "{name}"')
def step_create_bi_when(context, name):
    """Create a BusinessInteraction element (used as When in Scenario 1)."""
    if not hasattr(context, "model"):
        context.model = Model("bdd-test")
    context.bi_element = context.model.add(ArchiType.BusinessInteraction, name, desc="Created element")


@when("I import the file")
def step_import_file(context):
    """Import the file into the model."""
    if not hasattr(context, "model"):
        context.model = Model("import-test")
    context.model.read(context.temp_file)


@when("I export to .archimate format")
def step_export_archimate(context):
    """Export the model to .archimate format."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
        context.export_path = f.name
    context.temp_files.append(context.export_path)
    context.model.write(context.export_path)


@when("I export to OpenGroup exchange format")
def step_export_opengroup(context):
    """Export the model to OpenGroup exchange format."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        context.export_path = f.name
    context.temp_files.append(context.export_path)
    archimate_writer(context.model, context.export_path)


@when("I re-import the exported file")
def step_reimport_file(context):
    """Re-import the previously exported file."""
    context.reimported_model = Model("reimport-test")
    context.reimported_model.read(context.export_path)


# ============================================================================
# Then Steps
# ============================================================================


@then("the element is created without validation errors")
def step_created_without_errors(context):
    """Verify the element was created successfully."""
    assert context.bi_element is not None, "Element should be created"


@then("the element type is BusinessInteraction")
def step_element_type_is_bi(context):
    """Verify the element type is BusinessInteraction."""
    assert context.bi_element.type == ArchiType.BusinessInteraction, (
        f"Expected BusinessInteraction, got {context.bi_element.type}"
    )


@then("the element is stored in the model")
def step_element_in_model(context):
    """Verify the element is stored in the model's elements dict."""
    assert context.bi_element.uuid in context.model.elems_dict, "Element should be stored in model"


@then("the BusinessInteraction element is parsed successfully")
def step_bi_parsed(context):
    """Verify BusinessInteraction was parsed from imported file."""
    bi_elements = [e for e in context.model.elements if e.type == ArchiType.BusinessInteraction]
    assert len(bi_elements) > 0, "Should have parsed at least one BusinessInteraction element"
    context.imported_bi = bi_elements[0]


@then("the element is available in the model")
def step_element_available(context):
    """Verify the element is accessible in the model."""
    assert hasattr(context, "imported_bi"), "Element should be available"
    assert context.imported_bi.uuid in context.model.elems_dict, "Element should be in model dict"


@then("the element properties are preserved")
def step_properties_preserved(context):
    """Verify element properties are preserved during import."""
    assert context.imported_bi.name == _TEST_BI_NAME, f"Expected 'Test Interaction', got {context.imported_bi.name}"


@then("the BusinessInteraction elements are written to the file")
def step_bi_written_to_file(context):
    """Verify BusinessInteraction elements were written to exported file."""
    root = _parse_xml_from_file(context.export_path)
    # Check all elements for BusinessInteraction type
    found = False
    for elem in root.iter():
        xsi_type = elem.get(
            "{http://www.w3.org/2001/XMLSchema-instance}type"
        )  # NOSONAR — XML namespace URI, not a network request
        if xsi_type and "BusinessInteraction" in xsi_type:
            found = True
            break
    assert found, "BusinessInteraction should be written to file"


@then("the exported file is valid ArchiMate XML")
def step_valid_archimate_xml(context):
    """Verify the exported file is valid ArchiMate XML (.archimate Archi tool format)."""
    root = _parse_xml_from_file(context.export_path)
    assert root is not None, (
        "File should be valid XML"
    )  # NOSONAR — lxml stubs omit Optional; getroot() returns None at runtime for empty docs
    # .archimate files use Archi tool namespace, OpenGroup files use OpenGroup namespace
    archi_ns = "http://www.archimatetool.com/archimate"
    assert "archimate" in root.nsmap and (
        root.nsmap.get("archimate") == archi_ns or root.nsmap.get("archimate") == _OPENGROUP_NS
    ), "Should have ArchiMate namespace"


@then("the exported file is valid OpenGroup XML")
def step_valid_opengroup_xml(context):
    """Verify the exported OpenGroup file is valid XML."""
    root = _parse_xml_from_file(context.export_path)
    assert root is not None, (
        "File should be valid XML"
    )  # NOSONAR — lxml stubs omit Optional; getroot() returns None at runtime for empty docs
    # Check for opengroup namespace
    assert _OPENGROUP_NS in root.nsmap.values(), "Should have OpenGroup namespace"


@then("the BusinessInteraction element type is preserved")
def step_bi_type_preserved(context):
    """Verify BusinessInteraction type is preserved in .archimate export."""
    root = _parse_xml_from_file(context.export_path)
    # Check all elements for BusinessInteraction type attribute
    found = False
    for elem in root.iter():
        xsi_type = elem.get(
            "{http://www.w3.org/2001/XMLSchema-instance}type"
        )  # NOSONAR — XML namespace URI, not a network request
        if xsi_type and "BusinessInteraction" in xsi_type:
            found = True
            break
    assert found, "BusinessInteraction type should be preserved in XML"


@then("the element type mapping is correct")
def step_type_mapping_correct(context):
    """Verify BusinessInteraction type mapping in OpenGroup export."""
    root = _parse_xml_from_file(context.export_path)
    # Find all elements with BusinessInteraction type
    bi_elems = root.findall(
        ".//{http://www.opengroup.org/xsd/archimate/3.0/}element[@{http://www.w3.org/2001/XMLSchema-instance}type='BusinessInteraction']"
    )  # NOSONAR — XML namespace URIs in XPath, not network requests
    assert len(bi_elems) > 0, "BusinessInteraction type mapping should be correct"


@then("the BusinessInteraction element is present in the reimported model")
def step_bi_in_reimported(context):
    """Verify BusinessInteraction is present after round-trip."""
    bi_elements = [e for e in context.reimported_model.elements if e.type == ArchiType.BusinessInteraction]
    assert len(bi_elements) > 0, "BusinessInteraction should be present after round-trip"
    context.reimported_bi = bi_elements[0]


@then("the element properties match the original")
def step_properties_match_original(context):
    """Verify element properties match original after round-trip."""
    assert context.reimported_bi.name == context.original_element.name, "Name should match original"
    # Compare types - both should be BusinessInteraction
    assert context.reimported_bi.type == context.original_element.type, "Type should match original"


@then("the element type remains BusinessInteraction")
def step_type_remains_bi(context):
    """Verify element type remains BusinessInteraction after round-trip."""
    assert context.reimported_bi.type == ArchiType.BusinessInteraction, "Type should remain BusinessInteraction"


@then("the BusinessInteraction elements are correctly mapped and written")
def step_bi_correctly_mapped(context):
    """Verify BusinessInteraction elements are correctly mapped in OpenGroup export."""
    root = _parse_xml_from_file(context.export_path)
    # Find BusinessInteraction elements in OpenGroup format
    bi_elems = root.findall(
        ".//{http://www.opengroup.org/xsd/archimate/3.0/}element[@{http://www.w3.org/2001/XMLSchema-instance}type='BusinessInteraction']"
    )  # NOSONAR — XML namespace URIs in XPath, not network requests
    assert len(bi_elems) > 0, "BusinessInteraction should be correctly mapped and written"
