"""Unit tests for parsing helper functions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from pyArchimate.helpers.parsing import compare_image_data, extract_images_from_archimate, parse_bool


class TestParseBoolean:
    """Test parse_bool() function with various inputs."""

    def test_parse_bool_true_values(self):
        """Test that true values are correctly parsed."""
        assert parse_bool("true") is True
        assert parse_bool("TRUE") is True
        assert parse_bool("True") is True
        assert parse_bool("TrUe") is True
        assert parse_bool("1") is True

    def test_parse_bool_false_values(self):
        """Test that false values are correctly parsed."""
        assert parse_bool("false") is False
        assert parse_bool("FALSE") is False
        assert parse_bool("False") is False
        assert parse_bool("FaLsE") is False
        assert parse_bool("0") is False

    def test_parse_bool_edge_cases(self):
        """Test edge cases and invalid inputs."""
        assert parse_bool(None) is False
        assert parse_bool("") is False
        assert parse_bool("   ") is False
        assert parse_bool("random") is False
        assert parse_bool("yes") is False
        assert parse_bool("no") is False
        assert parse_bool("on") is False
        assert parse_bool("off") is False

    def test_parse_bool_whitespace_handling(self):
        """Test that whitespace is properly trimmed."""
        assert parse_bool("  true  ") is True
        assert parse_bool("\ttrue\t") is True
        assert parse_bool("\ntrue\n") is True
        assert parse_bool("  false  ") is False
        assert parse_bool("\t1\t") is True
        assert parse_bool("  0  ") is False

    def test_parse_bool_consistency_with_xml_schema(self):
        """Test compliance with W3C XML Schema xsd:boolean."""
        # Canonical forms
        assert parse_bool("true") is True
        assert parse_bool("false") is False
        # Alternative forms per xsd:boolean
        assert parse_bool("1") is True
        assert parse_bool("0") is False


class TestCompareImageData:
    """Test compare_image_data() function."""

    def test_identical_data(self):
        """Test that identical base64 strings match."""
        data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        assert compare_image_data(data, data) is True

    def test_different_data(self):
        """Test that different base64 strings don't match."""
        data1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        data2 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P8/AwAJ+gL+Ktt7/QAAAABJRU5ErkJggg=="
        assert compare_image_data(data1, data2) is False

    def test_none_handling(self):
        """Test that None values are handled correctly."""
        assert compare_image_data(None, None) is True
        assert compare_image_data("data", None) is False
        assert compare_image_data(None, "data") is False

    def test_empty_string(self):
        """Test empty string comparison."""
        assert compare_image_data("", "") is True
        assert compare_image_data("", "data") is False
        assert compare_image_data("data", "") is False

    def test_case_sensitivity(self):
        """Test that comparison is case-sensitive (base64 is binary)."""
        data_lower = "abc123=="
        data_upper = "ABC123=="
        # Base64 is case-sensitive
        assert compare_image_data(data_lower, data_upper) is False
        assert compare_image_data(data_lower, data_lower) is True


class TestExtractImages:
    """Test extract_images_from_archimate() function."""

    def test_extract_no_images(self):
        """Test extraction from element with no images."""
        from lxml import etree

        root = etree.Element("root")
        result = extract_images_from_archimate(root)
        assert result == []

    def test_extract_single_image_from_element(self):
        """Test extraction of single image element."""
        from lxml import etree

        root = etree.Element("root")
        etree.SubElement(root, "image", data="dGVzdGRhdGE=")  # "testdata" in base64
        result = extract_images_from_archimate(root)
        assert result == ["dGVzdGRhdGE="]

    def test_extract_multiple_images(self):
        """Test extraction of multiple image elements."""
        from lxml import etree

        root = etree.Element("root")
        etree.SubElement(root, "image", data="aW1hZ2UxAA==")
        etree.SubElement(root, "image", data="aW1hZ2UyAA==")
        result = extract_images_from_archimate(root)
        assert len(result) == 2
        assert "aW1hZ2UxAA==" in result
        assert "aW1hZ2UyAA==" in result

    def test_extract_images_nested(self):
        """Test extraction of nested image elements."""
        from lxml import etree

        root = etree.Element("root")
        child = etree.SubElement(root, "child")
        etree.SubElement(child, "image", data="bmVzdGVkAA==")
        result = extract_images_from_archimate(root)
        assert result == ["bmVzdGVkAA=="]

    def test_extract_images_missing_data(self):
        """Test that images without data attribute are skipped."""
        from lxml import etree

        root = etree.Element("root")
        etree.SubElement(root, "image")  # No data attribute
        etree.SubElement(root, "image", data="dmFsaWQA")
        result = extract_images_from_archimate(root)
        assert result == ["dmFsaWQA"]
