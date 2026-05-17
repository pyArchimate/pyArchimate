"""Integration tests for smart file format selection.

Tests verify that the extension-based format auto-selection works correctly
for both .archimate (Archi native) and .xml (OpenGroup Exchange) formats.
Round-trip tests ensure data preservation across format boundaries.
"""

import tempfile
import zipfile
from pathlib import Path

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestArchimateFormatSelection:
    """Test .archimate file format selection and round-trip fidelity."""

    def test_write_archimate_extension_uses_archi_writer(self):
        """Writing to .archimate file uses Archi native format writer."""
        m = Model("test-archimate-format")
        elem = m.add(ArchiType.BusinessActor, "Sales Team", desc="Primary sales group")
        elem.prop("department", "Sales")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            # Write with .archimate extension (should auto-select archi writer)
            m.write(temp_path)

            # Verify file was created as ZIP archive and contains Archi format markers
            assert zipfile.is_zipfile(temp_path), "File should be a ZIP archive"
            with zipfile.ZipFile(temp_path, "r") as zf:
                # Extract model.xml and check for Archi format markers
                xml_data = zf.read("model.xml")
                content = xml_data.decode("utf-8")
                # Archi format uses archimate: namespace (not OpenGroup)
                assert "archimate:" in content or "xmlns:archimate" in content or "<archimatemodel" in content.lower()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_read_archimate_extension_uses_archi_reader(self):
        """Reading from .archimate file uses Archi native format reader."""
        # Create and write in archi format
        m1 = Model("test-archi-read")
        elem = m1.add(ArchiType.BusinessRole, "Manager", desc="Management role")
        elem.prop("level", "3")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)

            # Read back with auto-detection (should use archi reader)
            m2 = Model("test-archi-read-result")
            m2.read(temp_path)

            # Verify data was preserved
            assert elem.uuid in m2.elems_dict
            loaded_elem = m2.elems_dict[elem.uuid]
            assert loaded_elem.name == "Manager"
            assert loaded_elem.desc == "Management role"
            assert loaded_elem.props.get("level") == "3"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_archimate_roundtrip_preserves_elements(self):
        """Round-trip .archimate files preserve all elements and properties."""
        m1 = Model("archimate-roundtrip")
        actor = m1.add(ArchiType.BusinessActor, "Finance Dept", desc="Finance team")
        process = m1.add(ArchiType.BusinessProcess, "Budget Review", desc="Annual review")
        service = m1.add(ArchiType.BusinessService, "Financial Advisory", desc="Advice service")

        actor.prop("cost_center", "CC001")
        process.prop("frequency", "annual")
        service.prop("sla", "99.9%")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("archimate-roundtrip-loaded")
            m2.read(temp_path)

            # All three elements should exist
            assert actor.uuid in m2.elems_dict
            assert process.uuid in m2.elems_dict
            assert service.uuid in m2.elems_dict

            # Verify properties
            loaded_actor = m2.elems_dict[actor.uuid]
            assert loaded_actor.props.get("cost_center") == "CC001"

            loaded_process = m2.elems_dict[process.uuid]
            assert loaded_process.props.get("frequency") == "annual"

            loaded_service = m2.elems_dict[service.uuid]
            assert loaded_service.props.get("sla") == "99.9%"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_archimate_roundtrip_preserves_relationships(self):
        """Round-trip .archimate files preserve relationships between elements."""
        m1 = Model("archimate-rel-roundtrip")
        org = m1.add(ArchiType.BusinessActor, "Organization", desc="The org")
        role = m1.add(ArchiType.BusinessRole, "Director", desc="Director role")

        rel = m1.add_relationship(source=org, target=role, rel_type=ArchiType.Assignment, name="Director Assignment")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("archimate-rel-loaded")
            m2.read(temp_path)

            # Relationship should exist
            assert rel.uuid in m2.rels_dict
            loaded_rel = m2.rels_dict[rel.uuid]
            assert loaded_rel.name == "Director Assignment"
            assert loaded_rel.source.uuid == org.uuid
            assert loaded_rel.target.uuid == role.uuid
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestXMLFormatSelection:
    """Test .xml file format selection and round-trip fidelity."""

    def test_write_xml_extension_uses_archimate_writer(self):
        """Writing to .xml file uses OpenGroup Exchange format writer."""
        m = Model("test-xml-format")
        m.add(ArchiType.ApplicationComponent, "API Gateway", desc="REST API gateway")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_path = f.name

        try:
            # Write with .xml extension (should auto-select archimate writer)
            m.write(temp_path)

            # Verify file was created and contains OpenGroup format markers
            with open(temp_path) as f:
                content = f.read()
                # OpenGroup format uses archimate3.xsd schema location
                assert "archimate3.xsd" in content or "<model" in content or "xmlns=" in content
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_read_xml_extension_uses_archimate_reader(self):
        """Reading from .xml file uses OpenGroup Exchange format reader."""
        # Create and write in OpenGroup format
        m1 = Model("test-xml-read")
        elem = m1.add(ArchiType.ApplicationService, "Auth Service", desc="Authentication service")
        elem.prop("version", "2.0")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)

            # Read back with auto-detection (should use archimate reader)
            m2 = Model("test-xml-read-result")
            m2.read(temp_path)

            # Verify data was preserved
            assert elem.uuid in m2.elems_dict
            loaded_elem = m2.elems_dict[elem.uuid]
            assert loaded_elem.name == "Auth Service"
            assert loaded_elem.desc == "Authentication service"
            assert loaded_elem.props.get("version") == "2.0"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_xml_roundtrip_preserves_elements(self):
        """Round-trip .xml files preserve all elements and properties."""
        m1 = Model("xml-roundtrip")
        app = m1.add(ArchiType.ApplicationComponent, "Web App", desc="Frontend application")
        data = m1.add(ArchiType.DataObject, "User Data", desc="User information")
        svc = m1.add(ArchiType.ApplicationService, "Data API", desc="Data service")

        app.prop("framework", "React")
        data.prop("schema_version", "1.2")
        svc.prop("protocol", "REST")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("xml-roundtrip-loaded")
            m2.read(temp_path)

            # All three elements should exist
            assert app.uuid in m2.elems_dict
            assert data.uuid in m2.elems_dict
            assert svc.uuid in m2.elems_dict

            # Verify properties
            loaded_app = m2.elems_dict[app.uuid]
            assert loaded_app.props.get("framework") == "React"

            loaded_data = m2.elems_dict[data.uuid]
            assert loaded_data.props.get("schema_version") == "1.2"

            loaded_svc = m2.elems_dict[svc.uuid]
            assert loaded_svc.props.get("protocol") == "REST"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_xml_roundtrip_preserves_relationships(self):
        """Round-trip .xml files preserve relationships between elements."""
        m1 = Model("xml-rel-roundtrip")
        web = m1.add(ArchiType.ApplicationComponent, "Web App", desc="Web application")
        api = m1.add(ArchiType.ApplicationService, "Backend API", desc="API service")

        rel = m1.add_relationship(source=api, target=web, rel_type=ArchiType.Serving, name="API Serves Web")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("xml-rel-loaded")
            m2.read(temp_path)

            # Relationship should exist
            assert rel.uuid in m2.rels_dict
            loaded_rel = m2.rels_dict[rel.uuid]
            assert loaded_rel.name == "API Serves Web"
            assert loaded_rel.source.uuid == api.uuid
            assert loaded_rel.target.uuid == web.uuid
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestFormatAutoDetection:
    """Test format auto-detection with edge cases."""

    def test_default_to_opengroup_without_extension(self):
        """Files without recognized extension default to OpenGroup format."""
        m = Model("test-no-ext")
        elem = m.add(ArchiType.BusinessProcess, "Process", desc="A process")

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name
        # Remove any extension
        no_ext_path = temp_path.split(".")[0]

        try:
            m.write(no_ext_path)
            # Should use OpenGroup format by default
            m2 = Model("test-no-ext-loaded")
            m2.read(no_ext_path)
            assert elem.uuid in m2.elems_dict
        finally:
            Path(no_ext_path).unlink(missing_ok=True)

    def test_case_insensitive_extension_detection(self):
        """Extension detection should be case-insensitive."""
        m1 = Model("test-case-insensitive")
        elem = m1.add(ArchiType.BusinessActor, "Actor", desc="Test actor")

        # Test uppercase .ARCHIMATE
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ARCHIMATE", delete=False) as f:
            temp_path_upper = f.name

        try:
            m1.write(temp_path_upper)
            m2 = Model("test-case-loaded")
            m2.read(temp_path_upper)
            assert elem.uuid in m2.elems_dict
        finally:
            Path(temp_path_upper).unlink(missing_ok=True)

        # Test mixed case .Xml
        m3 = Model("test-mixed-case")
        elem3 = m3.add(ArchiType.BusinessRole, "Role", desc="Test role")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".Xml", delete=False) as f:
            temp_path_mixed = f.name

        try:
            m3.write(temp_path_mixed)
            m4 = Model("test-mixed-loaded")
            m4.read(temp_path_mixed)
            assert elem3.uuid in m4.elems_dict
        finally:
            Path(temp_path_mixed).unlink(missing_ok=True)
