"""Integration tests for view documentation round-trip fidelity."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from lxml import etree as lxml_etree


def create_minimal_view_element(documentation_text: str | None) -> lxml_etree._Element:
    """Create a minimal ArchimateDiagramModel element with optional documentation."""
    view = lxml_etree.Element("ArchimateDiagramModel")
    view.set("id", "view-1")
    view.set("name", "TestView")

    if documentation_text is not None:
        doc = lxml_etree.SubElement(view, "documentation")
        doc.text = documentation_text

    return view


def test_view_documentation_present():
    """Test that view documentation element is correctly structured."""
    view = create_minimal_view_element("Test documentation")
    doc = view.find("documentation")
    assert doc is not None
    assert doc.text == "Test documentation"


def test_view_documentation_empty():
    """Test that empty view documentation is handled."""
    view = create_minimal_view_element("")
    doc = view.find("documentation")
    assert doc is not None
    assert doc.text == ""


def test_view_documentation_none():
    """Test that view without documentation has no element."""
    view = create_minimal_view_element(None)
    doc = view.find("documentation")
    assert doc is None


def test_view_documentation_roundtrip_with_text():
    """Test that view documentation text survives XML serialization."""
    original_text = "This is the view documentation"
    view_orig = create_minimal_view_element(original_text)

    # Serialize to XML
    xml_string = lxml_etree.tostring(view_orig, encoding="unicode")

    # Parse back from string
    view_reimp = lxml_etree.fromstring(xml_string)

    # Verify exact match
    doc_orig = view_orig.find("documentation")
    doc_reimp = view_reimp.find("documentation")

    assert doc_orig is not None
    assert doc_reimp is not None
    assert doc_orig.text == doc_reimp.text
    assert doc_orig.text == original_text


def test_view_documentation_roundtrip_empty():
    """Test that empty view documentation survives XML serialization.

    Note: Empty text ("") may serialize as None when parsed back due to XML spec.
    Both are semantically equivalent for empty documentation.
    """
    view_orig = create_minimal_view_element("")

    # Serialize to XML
    xml_string = lxml_etree.tostring(view_orig, encoding="unicode")

    # Parse back from string
    view_reimp = lxml_etree.fromstring(xml_string)

    # Verify exact match (empty text and None are equivalent)
    doc_orig = view_orig.find("documentation")
    doc_reimp = view_reimp.find("documentation")

    assert doc_orig is not None
    assert doc_reimp is not None
    # Empty string serializes to None when re-parsed (XML spec)
    assert (doc_orig.text or "") == (doc_reimp.text or "")


def test_view_documentation_with_special_characters():
    """Test that view documentation with special characters is preserved."""
    special_text = "Documentation with <special> & \"characters\" 'and' entities"
    view_orig = create_minimal_view_element(special_text)

    # Serialize to XML
    xml_string = lxml_etree.tostring(view_orig, encoding="unicode")

    # Parse back from string
    view_reimp = lxml_etree.fromstring(xml_string)

    # Verify exact match (lxml handles escaping automatically)
    doc_orig = view_orig.find("documentation")
    doc_reimp = view_reimp.find("documentation")

    assert doc_orig is not None
    assert doc_reimp is not None
    assert doc_orig.text == doc_reimp.text
    assert doc_orig.text == special_text


def test_view_documentation_multiline():
    """Test that multiline view documentation is preserved."""
    multiline_text = "Line 1\nLine 2\nLine 3"
    view_orig = create_minimal_view_element(multiline_text)

    # Serialize to XML
    xml_string = lxml_etree.tostring(view_orig, encoding="unicode")

    # Parse back from string
    view_reimp = lxml_etree.fromstring(xml_string)

    # Verify exact match
    doc_orig = view_orig.find("documentation")
    doc_reimp = view_reimp.find("documentation")

    assert doc_orig is not None
    assert doc_reimp is not None
    assert doc_orig.text == doc_reimp.text
    assert doc_orig.text == multiline_text
    assert "\n" in doc_orig.text


def test_view_documentation_long_text():
    """Test that long view documentation is preserved."""
    long_text = "X" * 1000  # 1000 character documentation
    view_orig = create_minimal_view_element(long_text)

    # Serialize to XML
    xml_string = lxml_etree.tostring(view_orig, encoding="unicode")

    # Parse back from string
    view_reimp = lxml_etree.fromstring(xml_string)

    # Verify exact match
    doc_orig = view_orig.find("documentation")
    doc_reimp = view_reimp.find("documentation")

    assert doc_orig is not None
    assert doc_reimp is not None
    assert doc_orig.text == doc_reimp.text
    assert doc_orig.text is not None
    assert len(doc_orig.text) == 1000
