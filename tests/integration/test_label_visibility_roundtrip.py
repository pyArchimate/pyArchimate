"""Integration tests for label visibility round-trip fidelity."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from lxml import etree as lxml_etree


def create_minimal_archi_connection_element(visibility: str) -> lxml_etree._Element:
    """Create a minimal sourceConnection element with nameVisible feature."""
    connection = lxml_etree.Element("sourceConnection")
    connection.set("id", "conn-1")
    connection.set("source", "node-1")
    connection.set("target", "node-2")
    connection.set("archimateRelationship", "rel-1")

    feature = lxml_etree.SubElement(connection, "feature")
    feature.set("name", "nameVisible")
    feature.set("value", visibility)

    return connection


def test_label_visibility_false_element():
    """Test that nameVisible='false' feature is correctly extracted."""
    conn = create_minimal_archi_connection_element("false")
    feature = conn.find("feature[@name='nameVisible']")
    assert feature is not None
    assert feature.get("value") == "false"


def test_label_visibility_true_element():
    """Test that nameVisible='true' feature is correctly extracted."""
    conn = create_minimal_archi_connection_element("true")
    feature = conn.find("feature[@name='nameVisible']")
    assert feature is not None
    assert feature.get("value") == "true"


def test_label_visibility_roundtrip_false():
    """Test that label visibility=false is preserved through XML serialization."""
    conn_orig = create_minimal_archi_connection_element("false")

    # Serialize to XML
    xml_string = lxml_etree.tostring(conn_orig, encoding="unicode")

    # Parse back from string
    conn_reimp = lxml_etree.fromstring(xml_string)

    # Verify exact match
    feature_orig = conn_orig.find("feature[@name='nameVisible']")
    feature_reimp = conn_reimp.find("feature[@name='nameVisible']")

    assert feature_orig is not None
    assert feature_reimp is not None
    assert feature_orig.get("value") == feature_reimp.get("value")
    assert feature_orig.get("value") == "false"


def test_label_visibility_roundtrip_true():
    """Test that label visibility=true is preserved through XML serialization."""
    conn_orig = create_minimal_archi_connection_element("true")

    # Serialize to XML
    xml_string = lxml_etree.tostring(conn_orig, encoding="unicode")

    # Parse back from string
    conn_reimp = lxml_etree.fromstring(xml_string)

    # Verify exact match
    feature_orig = conn_orig.find("feature[@name='nameVisible']")
    feature_reimp = conn_reimp.find("feature[@name='nameVisible']")

    assert feature_orig is not None
    assert feature_reimp is not None
    assert feature_orig.get("value") == feature_reimp.get("value")
    assert feature_orig.get("value") == "true"


def test_parse_bool_with_archimate_data():
    """Test parse_bool with real Archi boolean values."""
    from pyArchimate.helpers.parsing import parse_bool

    # Test with nameVisible values
    assert parse_bool("true") is True
    assert parse_bool("false") is False
    assert parse_bool("TRUE") is True
    assert parse_bool("FALSE") is False

    # Test robustness with whitespace
    assert parse_bool("  true  ") is True
    assert parse_bool("  false  ") is False
