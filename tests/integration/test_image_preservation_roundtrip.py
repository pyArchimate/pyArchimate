"""Integration tests for image preservation in Archi file round-trip."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from lxml import etree as lxml_etree

from pyArchimate.helpers.parsing import compare_image_data, extract_images_from_archimate


class TestSingleImageRoundTrip:
    """Test single image preservation through round-trip."""

    def setup_method(self):
        """Load test fixture with single image."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "test_single_image.archimate"
        self.tree = lxml_etree.parse(str(fixture_path))
        self.root = self.tree.getroot()

    def test_extract_single_image(self):
        """Test extraction of single image from fixture."""
        images = extract_images_from_archimate(self.root)
        assert len(images) == 1
        assert (
            images[0]
            == "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )

    def test_single_image_serialization_roundtrip(self):
        """Test that single image survives XML serialization."""
        # Extract original images
        images_orig = extract_images_from_archimate(self.root)
        assert len(images_orig) == 1

        # Serialize to string
        xml_string = lxml_etree.tostring(self.root, encoding="unicode")

        # Parse back
        tree_reimp = lxml_etree.fromstring(xml_string)
        images_reimp = extract_images_from_archimate(tree_reimp)

        # Verify exact match
        assert len(images_reimp) == 1
        assert compare_image_data(images_orig[0], images_reimp[0])
        assert images_orig[0] == images_reimp[0]

    def test_single_image_data_integrity(self):
        """Test that image data is valid base64."""
        images = extract_images_from_archimate(self.root)
        assert len(images) == 1
        img_data = images[0]

        # Verify it's valid base64 (can be decoded)
        import base64

        decoded = base64.b64decode(img_data)
        assert len(decoded) > 0  # Should decode to something
        # This is actually a 1x1 PNG, verify minimal PNG structure
        assert decoded[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic number

    def test_view_documentation_with_image(self):
        """Test that view documentation is preserved alongside image."""
        # Find view element
        views = self.root.findall(".//element[@name='TestView']")
        assert len(views) == 1
        view = views[0]

        # Check documentation
        doc = view.find("documentation")
        assert doc is not None
        assert doc.find("content").text == "Test view with embedded image"

        # Check that image is still present
        images = extract_images_from_archimate(self.root)
        assert len(images) == 1


class TestMultipleImagesRoundTrip:
    """Test multiple images preservation through round-trip."""

    def setup_method(self):
        """Load test fixture with multiple images."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "test_multiple_images.archimate"
        self.tree = lxml_etree.parse(str(fixture_path))
        self.root = self.tree.getroot()

    def test_extract_multiple_images(self):
        """Test extraction of multiple images from fixture."""
        images = extract_images_from_archimate(self.root)
        assert len(images) == 2
        assert (
            images[0]
            == "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        assert (
            images[1]
            == "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAE0lEQVQI12P4z8DwHwMx+FAOBgAXnAL9Z8sOKQAAAABJRU5ErkJggg=="
        )

    def test_multiple_images_serialization_roundtrip(self):
        """Test that multiple images survive XML serialization."""
        # Extract original images
        images_orig = extract_images_from_archimate(self.root)
        assert len(images_orig) == 2

        # Serialize to string
        xml_string = lxml_etree.tostring(self.root, encoding="unicode")

        # Parse back
        tree_reimp = lxml_etree.fromstring(xml_string)
        images_reimp = extract_images_from_archimate(tree_reimp)

        # Verify exact match (both count and data)
        assert len(images_reimp) == 2
        assert compare_image_data(images_orig[0], images_reimp[0])
        assert compare_image_data(images_orig[1], images_reimp[1])
        assert images_orig == images_reimp

    def test_multiple_images_order_preserved(self):
        """Test that image order is preserved through round-trip."""
        images_orig = extract_images_from_archimate(self.root)

        # Serialize and re-parse multiple times
        for _ in range(3):
            xml_string = lxml_etree.tostring(self.root, encoding="unicode")
            tree = lxml_etree.fromstring(xml_string)
            images = extract_images_from_archimate(tree)

            # Verify order is consistent
            assert images == images_orig

    def test_multiple_images_all_valid_base64(self):
        """Test that all image data is valid base64."""
        images = extract_images_from_archimate(self.root)
        assert len(images) == 2

        import base64

        for i, img_data in enumerate(images):
            decoded = base64.b64decode(img_data)
            assert len(decoded) > 0
            # Both are PNG files
            assert decoded[:8] == b"\x89PNG\r\n\x1a\n", f"Image {i} is not a valid PNG"

    def test_view_documentation_with_multiple_images(self):
        """Test that view documentation is preserved with multiple images."""
        views = self.root.findall(".//element[@name='TestViewMultiImage']")
        assert len(views) == 1
        view = views[0]

        # Check documentation
        doc = view.find("documentation")
        assert doc is not None
        content = doc.find("content")
        assert content is not None
        assert content.text == "Test view with multiple embedded images"

        # Check that all images are still present
        images = extract_images_from_archimate(self.root)
        assert len(images) == 2
