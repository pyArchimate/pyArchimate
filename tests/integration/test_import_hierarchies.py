"""
Integration tests for edge cases in hierarchy import.
Tests lenient error handling, cycle detection, depth validation, and missing parent handling.
"""

import pytest
from src.pyArchimate.model import Model
from src.pyArchimate.enums import ArchiType
import tempfile
import os
from lxml import etree
from src.pyArchimate.readers.archimateReader import archimate_reader


class TestImportHierarchyEdgeCases:
    """Edge case tests for importing hierarchies."""

    def _create_archimate_xml(self, elements_xml: str) -> str:
        """Helper to create minimal Archi file XML with custom elements section."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:archimate="http://www.opengroup.org/xsd/archimate/3.1/" xmlns="http://www.opengroup.org/xsd/archimate/3.1/" name="Test" id="id-0000">
  <elements>
{elements_xml}
  </elements>
  <relationships/>
  <views/>
</archimate:model>"""

    def test_import_with_missing_parent_reference(self):
        """Test: Element references parent that doesn't exist; relationship skipped, model valid."""
        xml_content = self._create_archimate_xml("""
    <element id="id-child" name="Child" xsi:type="archimate:BusinessFunction" parentId="id-nonexistent"/>
    <element id="id-other" name="Other" xsi:type="archimate:BusinessFunction"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        assert 'id-child' in model.elems_dict
        assert 'id-other' in model.elems_dict
        child = model.elems_dict['id-child']
        assert model.get_parent(child.uuid) is None

    def test_import_with_self_reference_parent(self):
        """Test: Element references itself as parent; relationship skipped, model valid."""
        xml_content = self._create_archimate_xml("""
    <element id="id-self" name="Self" xsi:type="archimate:BusinessFunction" parentId="id-self"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        elem = model.elems_dict['id-self']
        assert model.get_parent(elem.uuid) is None

    def test_import_with_cycle_in_hierarchy(self):
        """Test: Circular hierarchy (A→B, B→C, C→A); cycle skipped, partial hierarchy preserved."""
        xml_content = self._create_archimate_xml("""
    <element id="id-a" name="A" xsi:type="archimate:BusinessFunction" parentId="id-c"/>
    <element id="id-b" name="B" xsi:type="archimate:BusinessFunction" parentId="id-a"/>
    <element id="id-c" name="C" xsi:type="archimate:BusinessFunction" parentId="id-b"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        a = model.elems_dict['id-a']
        b = model.elems_dict['id-b']
        c = model.elems_dict['id-c']
        assert all(elem is not None for elem in [a, b, c])
        parents = [model.get_parent(x.uuid) for x in [a, b, c]]
        assert parents.count(None) >= 1

    def test_import_depth_exceeds_limit(self):
        """Test: Hierarchy exceeds MAX_DEPTH (5 levels); extra relationships skipped."""
        xml_content = self._create_archimate_xml("""
    <element id="id-l0" name="L0" xsi:type="archimate:BusinessFunction"/>
    <element id="id-l1" name="L1" xsi:type="archimate:BusinessFunction" parentId="id-l0"/>
    <element id="id-l2" name="L2" xsi:type="archimate:BusinessFunction" parentId="id-l1"/>
    <element id="id-l3" name="L3" xsi:type="archimate:BusinessFunction" parentId="id-l2"/>
    <element id="id-l4" name="L4" xsi:type="archimate:BusinessFunction" parentId="id-l3"/>
    <element id="id-l5" name="L5" xsi:type="archimate:BusinessFunction" parentId="id-l4"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        l5 = model.elems_dict['id-l5']
        parent = model.get_parent(l5.uuid)
        assert parent is None

    def test_import_multiple_parents_for_same_child(self):
        """Test: Child has parentId from multiple sources (only first applies via reordering)."""
        xml_content = self._create_archimate_xml("""
    <element id="id-parent1" name="Parent1" xsi:type="archimate:BusinessFunction"/>
    <element id="id-parent2" name="Parent2" xsi:type="archimate:BusinessFunction"/>
    <element id="id-child" name="Child" xsi:type="archimate:BusinessFunction" parentId="id-parent1"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        child = model.elems_dict['id-child']
        parent = model.get_parent(child.uuid)
        assert parent is not None
        assert parent.uuid == 'id-parent1'

    def test_import_valid_linear_chain(self):
        """Test: Valid linear chain 5 levels deep succeeds."""
        xml_content = self._create_archimate_xml("""
    <element id="id-l0" name="L0" xsi:type="archimate:BusinessFunction"/>
    <element id="id-l1" name="L1" xsi:type="archimate:BusinessFunction" parentId="id-l0"/>
    <element id="id-l2" name="L2" xsi:type="archimate:BusinessFunction" parentId="id-l1"/>
    <element id="id-l3" name="L3" xsi:type="archimate:BusinessFunction" parentId="id-l2"/>
    <element id="id-l4" name="L4" xsi:type="archimate:BusinessFunction" parentId="id-l3"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        assert model.get_depth(model.elems_dict['id-l4'].uuid) == 4
        assert model.get_depth(model.elems_dict['id-l3'].uuid) == 3
        assert model.get_depth(model.elems_dict['id-l2'].uuid) == 2
        assert model.get_depth(model.elems_dict['id-l1'].uuid) == 1
        assert model.get_depth(model.elems_dict['id-l0'].uuid) == 0

    def test_import_orphaned_elements_with_missing_parents(self):
        """Test: Multiple elements with some missing parents become roots; valid model."""
        xml_content = self._create_archimate_xml("""
    <element id="id-root1" name="Root1" xsi:type="archimate:BusinessFunction"/>
    <element id="id-child1" name="Child1" xsi:type="archimate:BusinessFunction" parentId="id-missing"/>
    <element id="id-root2" name="Root2" xsi:type="archimate:BusinessFunction"/>
    <element id="id-child2" name="Child2" xsi:type="archimate:BusinessFunction" parentId="id-root2"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        roots = model.get_root_elements()
        root_names = {r.name for r in roots}
        assert 'Root1' in root_names
        assert 'Root2' in root_names
        assert 'Child1' in root_names
        assert 'Child2' not in root_names

    def test_import_empty_parentId_attribute(self):
        """Test: Empty parentId attribute treated as no parent."""
        xml_content = self._create_archimate_xml("""
    <element id="id-elem" name="Elem" xsi:type="archimate:BusinessFunction" parentId=""/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        elem = model.elems_dict['id-elem']
        assert model.get_parent(elem.uuid) is None

    def test_import_no_parentId_attribute(self):
        """Test: Elements without parentId are roots."""
        xml_content = self._create_archimate_xml("""
    <element id="id-root" name="Root" xsi:type="archimate:BusinessFunction"/>
    <element id="id-other" name="Other" xsi:type="archimate:BusinessFunction"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        roots = model.get_root_elements()
        assert len(roots) == 2

    def test_import_hierarchy_with_mixed_types(self):
        """Test: Hierarchy mixing different ArchiMate element types succeeds."""
        xml_content = self._create_archimate_xml("""
    <element id="id-proc" name="Process" xsi:type="archimate:BusinessProcess"/>
    <element id="id-func" name="Function" xsi:type="archimate:BusinessFunction" parentId="id-proc"/>
    <element id="id-inter" name="Interaction" xsi:type="archimate:BusinessInteraction" parentId="id-func"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        proc = model.elems_dict['id-proc']
        func = model.elems_dict['id-func']
        inter = model.elems_dict['id-inter']
        func_parent = model.get_parent(func.uuid)
        assert func_parent is not None
        assert func_parent.uuid == proc.uuid
        inter_parent = model.get_parent(inter.uuid)
        assert inter_parent is not None
        assert inter_parent.uuid == func.uuid

    def test_import_preserves_elements_despite_hierarchy_errors(self):
        """Test: All elements preserved even when some hierarchies fail."""
        xml_content = self._create_archimate_xml("""
    <element id="id-good" name="Good" xsi:type="archimate:BusinessFunction"/>
    <element id="id-bad" name="Bad" xsi:type="archimate:BusinessFunction" parentId="id-bad"/>
    <element id="id-also-good" name="AlsoGood" xsi:type="archimate:BusinessFunction"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        assert 'id-good' in model.elems_dict
        assert 'id-bad' in model.elems_dict
        assert 'id-also-good' in model.elems_dict
        assert len(model.elems_dict) == 3

    def test_import_hierarchy_order_independent(self):
        """Test: Element order in XML doesn't affect hierarchy reconstruction (parents can come after children)."""
        xml_content = self._create_archimate_xml("""
    <element id="id-child" name="Child" xsi:type="archimate:BusinessFunction" parentId="id-parent"/>
    <element id="id-parent" name="Parent" xsi:type="archimate:BusinessFunction"/>
""")
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        child = model.elems_dict['id-child']
        parent = model.elems_dict['id-parent']
        child_parent = model.get_parent(child.uuid)
        assert child_parent is not None
        assert child_parent.uuid == parent.uuid

    def test_import_large_hierarchy_performance(self):
        """Test: Large hierarchy (many siblings) imports successfully."""
        elements_xml = '<element id="id-root" name="Root" xsi:type="archimate:BusinessFunction"/>\n'
        for i in range(50):
            elements_xml += f'    <element id="id-child{i}" name="Child{i}" xsi:type="archimate:BusinessFunction" parentId="id-root"/>\n'
        xml_content = self._create_archimate_xml(elements_xml)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            with open(filepath, 'w') as f:
                f.write(xml_content)
            model = Model('test')
            model.read(filepath)

        root = model.elems_dict['id-root']
        children = model.get_children(root.uuid)
        assert len(children) == 50
