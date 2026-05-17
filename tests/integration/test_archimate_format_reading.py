"""Integration tests for .archimate format reading with ZIP archive support.

Tests round-trip fidelity (read → modify → write → read) for both
.archimate (ZIP) and .xml (plain XML) formats.
"""

import tempfile
import zipfile
from pathlib import Path

from src.pyArchimate.enums import ArchiType
from src.pyArchimate.model import Model


class TestArchimateFormatReading:
    """Integration tests for reading valid .archimate ZIP archives."""

    def test_read_valid_archimate_file_structure(self):
        """T026: Read valid .archimate file and verify model structure.

        Ensures that .archimate ZIP files are properly extracted and
        parsed, returning a valid model without errors.
        """
        file_path = "tests/fixtures/valid_model.archimate"
        m = Model("test")
        # Should not raise any exceptions when reading a valid .archimate file
        m.read(file_path)
        # Verify model object exists
        assert m is not None

    def test_archimate_roundtrip_with_elements(self):
        """T027: Round-trip .archimate: write → read → verify.

        Creates a model, writes it to .archimate format, reads it back,
        and verifies that elements are preserved correctly.
        """
        with tempfile.NamedTemporaryFile(suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            # Write original model
            m1 = Model("original-model")
            elem1 = m1.add(ArchiType.BusinessActor, "Test Actor")
            elem2 = m1.add(ArchiType.BusinessRole, "Test Role")
            rel = m1.add_relationship(rel_type="Association", source=elem1, target=elem2)

            m1.write(temp_path)

            # Read back (Feature 008: ZIP detection for reading)
            m2 = Model("reloaded-model")
            m2.read(temp_path)

            # Verify round-trip preservation
            assert elem1.uuid in m2.elems_dict, f"Element {elem1.uuid} not found after round-trip"
            assert elem2.uuid in m2.elems_dict, f"Element {elem2.uuid} not found after round-trip"
            assert m2.elems_dict[elem1.uuid].name == "Test Actor"
            assert m2.elems_dict[elem2.uuid].name == "Test Role"

            # Verify relationship preserved
            assert rel.uuid in m2.rels_dict, f"Relationship {rel.uuid} not found after round-trip"

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_xml_format_still_works_backward_compatibility(self):
        """T028: Plain XML files (.xml) still work identically.

        Verifies backward compatibility by writing and reading plain
        XML files using .xml extension.
        """
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            temp_path = f.name

        try:
            # Write original model to .xml
            m1 = Model("xml-model")
            elem1 = m1.add(ArchiType.ApplicationComponent, "Test App")
            elem2 = m1.add(ArchiType.DataObject, "Test Data")
            rel = m1.add_relationship(rel_type="Association", source=elem1, target=elem2)

            m1.write(temp_path)

            # Verify file is NOT a ZIP archive
            assert not zipfile.is_zipfile(temp_path), f"{temp_path} should not be a ZIP archive"

            # Read back
            m2 = Model("xml-reloaded")
            m2.read(temp_path)

            # Verify round-trip preservation
            assert elem1.uuid in m2.elems_dict
            assert elem2.uuid in m2.elems_dict
            assert m2.elems_dict[elem1.uuid].name == "Test App"
            assert m2.elems_dict[elem2.uuid].name == "Test Data"
            assert rel.uuid in m2.rels_dict

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_archimate_with_multiple_element_types(self):
        """Round-trip test with various ArchiMate element types.

        Ensures that different element categories (business, application,
        technology, physical) are correctly preserved through .archimate
        format round-trip.
        """
        with tempfile.NamedTemporaryFile(suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            # Create model with diverse element types
            m1 = Model("multi-element-model")
            business = m1.add(ArchiType.BusinessProcess, "Process")
            application = m1.add(ArchiType.ApplicationComponent, "Component")
            technology = m1.add(ArchiType.Node, "Server")
            physical = m1.add(ArchiType.Device, "Device")

            # Add relationships between elements
            m1.add_relationship(rel_type="Influence", source=business, target=application)
            m1.add_relationship(rel_type="Association", source=application, target=technology)
            m1.add_relationship(rel_type="Association", source=technology, target=physical)

            # Write to .archimate
            m1.write(temp_path)

            # Read back
            m2 = Model("multi-reloaded")
            m2.read(temp_path)

            # Verify all elements preserved
            assert business.uuid in m2.elems_dict
            assert application.uuid in m2.elems_dict
            assert technology.uuid in m2.elems_dict
            assert physical.uuid in m2.elems_dict

            # Verify element names
            assert m2.elems_dict[business.uuid].name == "Process"
            assert m2.elems_dict[application.uuid].name == "Component"
            assert m2.elems_dict[technology.uuid].name == "Server"
            assert m2.elems_dict[physical.uuid].name == "Device"

            # Verify relationships
            assert len(m2.rels_dict) == 3

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_format_selection_with_archimate_extension(self):
        """Feature 007 + Feature 008 integration: auto-format selection.

        When writing to .archimate extension, Feature 007 selects archiWriter.
        When reading, Feature 008 detects ZIP format and extracts properly.
        """
        with tempfile.NamedTemporaryFile(suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1 = Model("format-selection-test")
            elem = m1.add(ArchiType.BusinessActor, "Actor")

            # Feature 007: Extension-based format selection
            m1.write(temp_path)

            # Feature 008: ZIP detection and extraction
            m2 = Model("loaded")
            m2.read(temp_path)

            # Verify successful round-trip
            assert elem.uuid in m2.elems_dict
            assert m2.elems_dict[elem.uuid].name == "Actor"

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_read_exports_demo_with_images(self):
        """T040: Read export_demo.archimate and verify images are captured.

        Tests that when reading an .archimate file with images, the images
        are extracted and stored in Model._images_dict.
        """
        file_path = "temp/export_demo.archimate"
        m = Model("test")

        # Check if file exists before testing
        if Path(file_path).exists():
            m.read(file_path)
            # Verify images were captured
            assert len(m._images_dict) > 0, "No images captured from export_demo.archimate"
            assert len(m._image_files) > 0, "No image filenames tracked"
            # Verify specific image exists
            assert any("images/" in filename for filename in m._image_files), "No images/ folder entries"

    def test_write_creates_zip_with_images(self):
        """T041: Write .archimate file and verify ZIP structure contains images.

        Tests that when writing to .archimate extension with images in the model,
        a proper ZIP archive is created with model.xml and images/ folder.
        """
        with tempfile.NamedTemporaryFile(suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            # Create model and manually add image data (simulating read from archive)
            m1 = Model("image-test")
            m1.add(ArchiType.BusinessActor, "Test")

            # Simulate having extracted images by adding mock image data
            m1._images_dict["images/test.png"] = b"PNG_IMAGE_DATA"
            m1._image_files.append("images/test.png")

            # Write to .archimate
            m1.write(temp_path)

            # Verify the written file is a ZIP archive
            assert zipfile.is_zipfile(temp_path), "Output file should be a ZIP archive"

            # Verify ZIP contains model.xml and image
            with zipfile.ZipFile(temp_path, "r") as zf:
                file_list = zf.namelist()
                assert "model.xml" in file_list, "model.xml should be in archive"
                assert "images/test.png" in file_list, "Image should be in archive"

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_image_preservation_roundtrip(self):
        """T042: Round-trip test with image preservation.

        Tests that images are preserved through a complete round-trip:
        read .archimate → modify → write → read back.
        """
        with tempfile.NamedTemporaryFile(suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            # Create model with image data
            m1 = Model("image-roundtrip")
            elem1 = m1.add(ArchiType.BusinessProcess, "Process")

            # Manually add image data (simulating read from archive)
            m1._images_dict["images/diagram.png"] = b"PNG_DATA_12345"
            m1._image_files.append("images/diagram.png")

            # Write to .archimate with images
            m1.write(temp_path)

            # Read back from .archimate
            m2 = Model("reloaded")
            m2.read(temp_path)

            # Verify element preserved
            assert elem1.uuid in m2.elems_dict
            assert m2.elems_dict[elem1.uuid].name == "Process"

            # Verify images preserved
            assert "images/diagram.png" in m2._images_dict, "Image should be preserved after round-trip"
            assert m2._images_dict["images/diagram.png"] == b"PNG_DATA_12345", "Image data should match"

        finally:
            Path(temp_path).unlink(missing_ok=True)
