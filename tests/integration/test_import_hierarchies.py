"""Integration tests for hierarchy edge cases during import.

Tests verify that the import process handles edge cases gracefully:
- Missing parent elements (lenient skip)
- Invalid hierarchy references (ignored with warning)
- Complex scenarios (mixed grouping, properties, viewpoints)
"""

import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestImportHierarchyEdgeCases:
    """T032: Edge case tests for import (cycles, missing parents, depth limits)."""

    def test_import_missing_parent_element_skipped(self):
        """Test that missing parent references are skipped with warning during import."""
        # Create XML with reference to non-existent parent
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:Model xmlns:archimate="http://www.opengroup.org/xsd/archimate/3.0/"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="test-missing-parent">
  <elements>
    <element identifier="elem-1" xsi:type="archimate:BusinessProcess">
      <name>Process 1</name>
    </element>
    <element identifier="elem-2" xsi:type="archimate:BusinessProcess" parentId="non-existent-uuid">
      <name>Process 2</name>
    </element>
  </elements>
</archimate:Model>'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name

        try:
            m = Model('missing-parent-test')
            m.read(temp_path)

            # Elements should exist but without hierarchy
            assert 'elem-1' in m.elems_dict
            assert 'elem-2' in m.elems_dict
            elem2 = m.elems_dict['elem-2']
            assert m.get_parent(elem2.uuid) is None
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_with_invalid_hierarchy_continues(self):
        """Test that invalid hierarchy entries are skipped without breaking import."""
        m1 = Model('invalid-hierarchy-source')
        p1 = m1.add(ArchiType.BusinessProcess, 'P1')
        p2 = m1.add(ArchiType.BusinessProcess, 'P2')
        p3 = m1.add(ArchiType.BusinessProcess, 'P3')

        # Valid hierarchy
        m1.add_child(p1.uuid, p2.uuid)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.archimate', delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)

            # Manually inject invalid parentId by modifying XML
            tree = ET.parse(temp_path)
            root = tree.getroot()
            ns = {'archimate': 'http://www.opengroup.org/xsd/archimate/3.0/'}
            elements = root.findall('.//archimate:element', ns)
            # Add an invalid parentId to p3
            for elem in elements:
                if elem.get('identifier') == p3.uuid:
                    elem.set('parentId', 'invalid-uuid-xyz')

            with open(temp_path, 'wb') as f:
                tree.write(f)

            # Import should continue despite invalid hierarchy
            m2 = Model('invalid-hierarchy-reload')
            m2.read(temp_path)

            # Valid hierarchy should be preserved
            p2_2 = m2.elems_dict[p2.uuid]
            p1_2 = m2.elems_dict[p1.uuid]
            assert m2.get_parent(p2_2.uuid) == p1_2

            # Invalid element should exist but not be grouped
            p3_2 = m2.elems_dict[p3.uuid]
            assert m2.get_parent(p3_2.uuid) is None
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_visual_style_with_invalid_color_skipped(self):
        """Test that invalid colors in visual styles are skipped with warning."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:Model xmlns:archimate="http://www.opengroup.org/xsd/archimate/3.0/"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="test-invalid-color">
  <elements>
    <element identifier="elem-1" xsi:type="archimate:BusinessProcess">
      <name>Process 1</name>
      <properties>
        <property key="fillColor"><value>#ff0000</value></property>
        <property key="lineColor"><value>invalid-color-xyz</value></property>
      </properties>
    </element>
  </elements>
</archimate:Model>'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name

        try:
            m = Model('invalid-color-test')
            m.read(temp_path)

            elem = m.elems_dict['elem-1']
            style = elem.get_visual_style()

            # Valid color should be applied
            assert style.get('fillColor') == '#ff0000'
            # Invalid color should be skipped
            assert 'lineColor' not in style
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_visual_style_with_out_of_range_values_skipped(self):
        """Test that out-of-range transparency/lineWidth values are skipped."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:Model xmlns:archimate="http://www.opengroup.org/xsd/archimate/3.0/"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="test-invalid-ranges">
  <elements>
    <element identifier="elem-1" xsi:type="archimate:BusinessProcess">
      <name>Process 1</name>
      <properties>
        <property key="transparency"><value>1.5</value></property>
        <property key="lineWidth"><value>-5</value></property>
      </properties>
    </element>
  </elements>
</archimate:Model>'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name

        try:
            m = Model('invalid-ranges-test')
            m.read(temp_path)

            elem = m.elems_dict['elem-1']
            style = elem.get_visual_style()

            # Out-of-range values should be skipped
            assert 'transparency' not in style
            assert 'lineWidth' not in style
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_complex_hierarchy_with_visual_styles(self):
        """Test complex scenario with multiple hierarchies and mixed visual styles."""
        m1 = Model('complex-import-test')

        # Create hierarchy 1: Process > Function > Service
        p = m1.add(ArchiType.BusinessProcess, 'Process')
        f = m1.add(ArchiType.BusinessFunction, 'Function')
        a = m1.add(ArchiType.BusinessService, 'Service')

        m1.add_child(p.uuid, f.uuid)
        m1.add_child(f.uuid, a.uuid)

        # Add visual styles
        p.set_fill_color('#ff0000')
        f.set_fill_color('#00ff00')
        a.set_fill_color('#0000ff')
        a.set_transparency(0.5)

        # Create hierarchy 2: Actor > Role
        actor = m1.add(ArchiType.BusinessActor, 'Actor')
        role = m1.add(ArchiType.BusinessRole, 'Role')
        m1.add_child(actor.uuid, role.uuid)

        # Ungrouped element
        ungrouped = m1.add(ArchiType.BusinessObject, 'Object')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.archimate', delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model('complex-import-reload')
            m2.read(temp_path)

            # Verify first hierarchy
            p2 = m2.elems_dict[p.uuid]
            f2 = m2.elems_dict[f.uuid]
            a2 = m2.elems_dict[a.uuid]

            assert m2.get_parent(f2.uuid) == p2
            assert m2.get_parent(a2.uuid) == f2

            # Verify visual styles
            assert p2.get_fill_color() == '#ff0000'
            assert f2.get_fill_color() == '#00ff00'
            assert a2.get_fill_color() == '#0000ff'
            assert a2.get_transparency() == 0.5

            # Verify second hierarchy
            actor2 = m2.elems_dict[actor.uuid]
            role2 = m2.elems_dict[role.uuid]
            assert m2.get_parent(role2.uuid) == actor2

            # Verify ungrouped element
            ungrouped2 = m2.elems_dict[ungrouped.uuid]
            assert m2.get_parent(ungrouped2.uuid) is None
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_named_colors_converted_to_hex(self):
        """Test that named colors are converted to hex during import."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:Model xmlns:archimate="http://www.opengroup.org/xsd/archimate/3.0/"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="test-named-colors">
  <elements>
    <element identifier="elem-1" xsi:type="archimate:BusinessProcess">
      <name>Process 1</name>
      <properties>
        <property key="fillColor"><value>red</value></property>
        <property key="lineColor"><value>blue</value></property>
      </properties>
    </element>
  </elements>
</archimate:Model>'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name

        try:
            m = Model('named-colors-test')
            m.read(temp_path)

            elem = m.elems_dict['elem-1']
            style = elem.get_visual_style()

            # Named colors should be converted to hex
            assert style.get('fillColor') is not None
            assert style['fillColor'].startswith('#')
            assert style.get('lineColor') is not None
            assert style['lineColor'].startswith('#')
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_preserves_element_properties_with_hierarchy(self):
        """Test that custom element properties are preserved with hierarchy."""
        m1 = Model('props-with-hierarchy')
        parent = m1.add(ArchiType.BusinessProcess, 'Parent')
        child = m1.add(ArchiType.BusinessProcess, 'Child')

        # Add custom properties
        parent.prop('priority', 'high')
        parent.prop('owner', 'team-a')
        child.prop('status', 'active')

        m1.add_child(parent.uuid, child.uuid)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.archimate', delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model('props-with-hierarchy-reload')
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            child2 = m2.elems_dict[child.uuid]

            # Verify hierarchy
            assert m2.get_parent(child2.uuid) == parent2

            # Verify properties
            assert parent2.props.get('priority') == 'high'
            assert parent2.props.get('owner') == 'team-a'
            assert child2.props.get('status') == 'active'
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_self_referencing_parent_skipped(self):
        """Test that self-referencing parentId is skipped gracefully."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:Model xmlns:archimate="http://www.opengroup.org/xsd/archimate/3.0/"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="test-self-ref">
  <elements>
    <element identifier="elem-1" xsi:type="archimate:BusinessProcess" parentId="elem-1">
      <name>Process 1</name>
    </element>
  </elements>
</archimate:Model>'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name

        try:
            m = Model('self-ref-test')
            m.read(temp_path)

            # Element should exist but with no parent (self-ref rejected)
            elem = m.elems_dict['elem-1']
            assert m.get_parent(elem.uuid) is None
        finally:
            Path(temp_path).unlink(missing_ok=True)
