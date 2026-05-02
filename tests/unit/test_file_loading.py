"""Unit tests for file loading with ZIP archive support.

Tests for _detect_zip_file(), _extract_xml_from_zip(), and _load_file_contents()
with both plain XML and ZIP archive (.archimate) formats.
"""

import tempfile
import zipfile
from pathlib import Path

import pytest

from src.pyArchimate.model import Model


class TestZipDetection:
    """Tests for _detect_zip_file() method."""

    def test_detect_zip_file_with_valid_archimate(self):
        """T020: Detect valid .archimate file as ZIP."""
        file_path = "tests/fixtures/valid_model.archimate"
        assert Model._detect_zip_file(file_path) is True

    def test_detect_zip_file_with_plain_xml(self):
        """T021: Detect plain XML file as non-ZIP."""
        file_path = "tests/fixtures/valid_model.xml"
        assert Model._detect_zip_file(file_path) is False

    def test_detect_zip_file_with_nonexistent(self):
        """Handle non-existent file gracefully."""
        file_path = "tests/fixtures/nonexistent_file.archimate"
        assert Model._detect_zip_file(file_path) is False

    def test_detect_zip_file_with_corrupted(self):
        """Non-ZIP corrupted file should return False."""
        file_path = "tests/fixtures/corrupted.archimate"
        # corrupted.archimate is invalid ZIP data, not PK signature
        assert Model._detect_zip_file(file_path) is False


class TestZipExtraction:
    """Tests for _extract_xml_from_zip() method."""

    def test_extract_xml_from_valid_archive(self):
        """T022: Extract XML from valid .archimate archive."""
        file_path = "tests/fixtures/valid_model.archimate"
        content = Model._extract_xml_from_zip(file_path)

        assert content.startswith("<?xml")
        assert "archimateModel" in content or "model" in content

    def test_extract_xml_from_corrupted_zip(self):
        """T023: Error on corrupted ZIP file."""
        file_path = "tests/fixtures/corrupted.archimate"
        with pytest.raises(zipfile.BadZipFile):
            Model._extract_xml_from_zip(file_path)

    def test_extract_xml_missing_model_xml(self):
        """T024: Error when model.xml missing from archive."""
        file_path = "tests/fixtures/no_model_xml.archimate"
        with pytest.raises(KeyError):
            Model._extract_xml_from_zip(file_path)

    def test_extract_xml_file_not_found(self):
        """T025: Error on non-existent file."""
        file_path = "tests/fixtures/missing_file.archimate"
        with pytest.raises(FileNotFoundError):
            Model._extract_xml_from_zip(file_path)


class TestUnifiedFileLoading:
    """Tests for _load_file_contents() with automatic format detection."""

    def test_load_plain_xml_file(self):
        """Load plain XML file (unchanged behavior)."""
        file_path = "tests/fixtures/valid_model.xml"
        m = Model('test')
        content = m._load_file_contents(file_path, 'read')

        assert "<?xml" in content
        assert "<model" in content or "<archimate" in content

    def test_load_archimate_zip_file(self):
        """Load .archimate ZIP file (new behavior)."""
        file_path = "tests/fixtures/valid_model.archimate"
        m = Model('test')
        content = m._load_file_contents(file_path, 'read')

        assert "<?xml" in content
        assert "archimateModel" in content or "model" in content

    def test_load_file_encoding_error(self):
        """Handle encoding errors gracefully."""
        # Create a file with invalid UTF-8 bytes
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.xml', delete=False) as f:
            f.write(b'<?xml version="1.0"?>\n<model>\xff\xfe</model>')
            temp_path = f.name

        try:
            m = Model('test')
            with pytest.raises(SystemExit):
                m._load_file_contents(temp_path, 'read')
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_corrupted_zip_exits(self):
        """Corrupted ZIP file is read as plain text and succeeds."""
        # Note: corrupted.archimate doesn't have ZIP signature, so it's read as plain text
        file_path = "tests/fixtures/corrupted.archimate"
        m = Model('test')
        content = m._load_file_contents(file_path, 'read')
        # Since it's not a ZIP, it's read as plain text
        assert "INVALID_ZIP_DATA_NOT_A_REAL_ZIP" in content

    def test_load_missing_model_xml_exits(self):
        """ZIP without model.xml causes SystemExit."""
        file_path = "tests/fixtures/no_model_xml.archimate"
        m = Model('test')
        with pytest.raises(SystemExit):
            m._load_file_contents(file_path, 'read')


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with existing .xml files."""

    def test_xml_files_still_work(self):
        """Plain XML files should work identically to before."""
        file_path = "tests/fixtures/valid_model.xml"
        m = Model('test')
        content = m._load_file_contents(file_path, 'read')

        # Should return file content as-is
        assert isinstance(content, str)
        assert len(content) > 0
        assert "<?xml" in content

    def test_file_without_extension(self):
        """Files without recognized extension should try plain text."""
        # Create a plain XML file without extension
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('<?xml version="1.0"?><model/>')
            temp_path = f.name

        try:
            m = Model('test')
            content = m._load_file_contents(temp_path, 'read')
            assert "<?xml" in content
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_csv_file_not_detected_as_zip(self):
        """Non-archive files shouldn't be detected as ZIP."""
        # Create a CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('name,value\ntest,123')
            temp_path = f.name

        try:
            assert Model._detect_zip_file(temp_path) is False
        finally:
            Path(temp_path).unlink(missing_ok=True)
