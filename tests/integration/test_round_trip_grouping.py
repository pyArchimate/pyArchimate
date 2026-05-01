"""
Integration tests for round-trip import/export of element grouping.
Tests that hierarchies and parent-child relationships are preserved through export → import cycles.
"""

import pytest
from src.pyArchimate.model import Model
from src.pyArchimate.enums import ArchiType
import tempfile
import os


class TestRoundTripGrouping:
    """Round-trip tests for element grouping (parent-child relationships)."""

    def test_round_trip_simple_parent_child(self):
        """Test: Export model with parent-child, import, verify hierarchy preserved."""
        model1 = Model('test_hierarchy')
        parent = model1.add(ArchiType.BusinessProcess, 'Parent', desc='Parent process')
        child = model1.add(ArchiType.BusinessFunction, 'Child', desc='Child function')
        model1.add_child(parent.uuid, child.uuid)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        parent_elem = model2.get_parent(child.uuid)
        assert parent_elem is not None
        assert parent_elem.uuid == parent.uuid
        assert len(model2.get_children(parent.uuid)) == 1
        assert model2.get_children(parent.uuid)[0].uuid == child.uuid

    def test_round_trip_multiple_children(self):
        """Test: Parent with multiple children, export, import, verify all relationships preserved."""
        model1 = Model('test_multi')
        parent = model1.add(ArchiType.BusinessProcess, 'Parent')
        children = [
            model1.add(ArchiType.BusinessFunction, f'Child{i}')
            for i in range(3)
        ]
        for child in children:
            model1.add_child(parent.uuid, child.uuid)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        imported_children = model2.get_children(parent.uuid)
        assert len(imported_children) == 3
        imported_child_uuids = {c.uuid for c in imported_children}
        original_child_uuids = {c.uuid for c in children}
        assert imported_child_uuids == original_child_uuids

    def test_round_trip_nested_hierarchy(self):
        """Test: 3-level hierarchy (root→parent→child), export, import, verify depth and relationships."""
        model1 = Model('test_nested')
        root = model1.add(ArchiType.BusinessProcess, 'Root')
        parent = model1.add(ArchiType.BusinessFunction, 'Parent')
        child = model1.add(ArchiType.BusinessFunction, 'Child')
        model1.add_child(root.uuid, parent.uuid)
        model1.add_child(parent.uuid, child.uuid)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        assert model2.get_depth(child.uuid) == 2
        assert model2.get_depth(parent.uuid) == 1
        assert model2.get_depth(root.uuid) == 0
        child_parent = model2.get_parent(child.uuid)
        assert child_parent is not None
        assert child_parent.uuid == parent.uuid
        parent_parent = model2.get_parent(parent.uuid)
        assert parent_parent is not None
        assert parent_parent.uuid == root.uuid

    def test_round_trip_preserves_element_properties(self):
        """Test: Parent-child hierarchy preserved alongside other element properties."""
        model1 = Model('test_props')
        parent = model1.add(ArchiType.BusinessProcess, 'Parent', desc='Parent description')
        child = model1.add(ArchiType.BusinessFunction, 'Child', desc='Child description')
        model1.add_child(parent.uuid, child.uuid)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        imported_parent = model2.elems_dict[parent.uuid]
        imported_child = model2.elems_dict[child.uuid]
        assert imported_parent.name == 'Parent'
        assert imported_parent.desc == 'Parent description'
        assert imported_child.name == 'Child'
        assert imported_child.desc == 'Child description'
        imported_child_parent = model2.get_parent(imported_child.uuid)
        assert imported_child_parent is not None
        assert imported_child_parent.uuid == imported_parent.uuid

    def test_round_trip_multiple_roots_with_children(self):
        """Test: Multiple root elements each with children, export, import, verify structure."""
        model1 = Model('test_multi_roots')
        root1 = model1.add(ArchiType.BusinessProcess, 'Root1')
        child1 = model1.add(ArchiType.BusinessFunction, 'Child1')
        root2 = model1.add(ArchiType.BusinessProcess, 'Root2')
        child2 = model1.add(ArchiType.BusinessFunction, 'Child2')
        model1.add_child(root1.uuid, child1.uuid)
        model1.add_child(root2.uuid, child2.uuid)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        roots = model2.get_root_elements()
        assert len(roots) == 2
        root_uuids = {r.uuid for r in roots}
        assert root1.uuid in root_uuids
        assert root2.uuid in root_uuids
        child1_parent = model2.get_parent(child1.uuid)
        assert child1_parent is not None
        assert child1_parent.uuid == root1.uuid
        child2_parent = model2.get_parent(child2.uuid)
        assert child2_parent is not None
        assert child2_parent.uuid == root2.uuid

    def test_round_trip_descendants_preserved(self):
        """Test: Full subtree (all descendants) preserved through round-trip."""
        model1 = Model('test_descendants')
        root = model1.add(ArchiType.BusinessProcess, 'Root')
        level1_a = model1.add(ArchiType.BusinessFunction, 'L1A')
        level1_b = model1.add(ArchiType.BusinessFunction, 'L1B')
        level2_a = model1.add(ArchiType.BusinessFunction, 'L2A')
        model1.add_child(root.uuid, level1_a.uuid)
        model1.add_child(root.uuid, level1_b.uuid)
        model1.add_child(level1_a.uuid, level2_a.uuid)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        descendants = model2.get_descendants(root.uuid)
        assert len(descendants) == 3
        descendant_uuids = {d.uuid for d in descendants}
        assert level1_a.uuid in descendant_uuids
        assert level1_b.uuid in descendant_uuids
        assert level2_a.uuid in descendant_uuids

    def test_round_trip_leaf_elements(self):
        """Test: Leaf elements (no children) identified correctly after import."""
        model1 = Model('test_leaves')
        root = model1.add(ArchiType.BusinessProcess, 'Root')
        child = model1.add(ArchiType.BusinessFunction, 'Child')
        leaf = model1.add(ArchiType.BusinessFunction, 'Leaf')
        model1.add_child(root.uuid, child.uuid)
        model1.add_child(child.uuid, leaf.uuid)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        leaves = model2.get_leaf_elements()
        leaf_uuids = {l.uuid for l in leaves}
        assert leaf.uuid in leaf_uuids
        assert child.uuid not in leaf_uuids
        assert root.uuid not in leaf_uuids

    def test_round_trip_ancestors_preserved(self):
        """Test: Full ancestry chain (all ancestors) preserved through round-trip."""
        model1 = Model('test_ancestors')
        root = model1.add(ArchiType.BusinessProcess, 'Root')
        level1 = model1.add(ArchiType.BusinessFunction, 'Level1')
        level2 = model1.add(ArchiType.BusinessFunction, 'Level2')
        model1.add_child(root.uuid, level1.uuid)
        model1.add_child(level1.uuid, level2.uuid)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        ancestors = model2.get_ancestors(level2.uuid)
        assert len(ancestors) == 3
        assert ancestors[0].uuid == level2.uuid
        assert ancestors[1].uuid == level1.uuid
        assert ancestors[2].uuid == root.uuid

    def test_round_trip_max_depth_preserved(self):
        """Test: Elements at maximum depth (4 levels deep) preserved through round-trip."""
        model1 = Model('test_max_depth')
        elements = []
        for i in range(4):
            elem = model1.add(ArchiType.BusinessFunction, f'Level{i}')
            elements.append(elem)
            if i > 0:
                model1.add_child(elements[i - 1].uuid, elem.uuid)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        for i, elem in enumerate(elements):
            imported_depth = model2.get_depth(elem.uuid)
            assert imported_depth == i

    def test_round_trip_no_orphaning_of_children(self):
        """Test: Children not orphaned during round-trip; parent-child relationships intact."""
        model1 = Model('test_no_orphan')
        parent = model1.add(ArchiType.BusinessProcess, 'Parent')
        child1 = model1.add(ArchiType.BusinessFunction, 'Child1')
        child2 = model1.add(ArchiType.BusinessFunction, 'Child2')
        model1.add_child(parent.uuid, child1.uuid)
        model1.add_child(parent.uuid, child2.uuid)

        child1_parent = model1.get_parent(child1.uuid)
        child2_parent = model1.get_parent(child2.uuid)
        assert child1_parent is not None
        assert child2_parent is not None
        original_child_parents = {
            child1.uuid: child1_parent.uuid,
            child2.uuid: child2_parent.uuid
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        for child_uuid, orig_parent_uuid in original_child_parents.items():
            imported_parent = model2.get_parent(child_uuid)
            assert imported_parent is not None
            assert imported_parent.uuid == orig_parent_uuid

    def test_round_trip_siblings_structure(self):
        """Test: Sibling relationships (shared parent) preserved through round-trip."""
        model1 = Model('test_siblings')
        parent = model1.add(ArchiType.BusinessProcess, 'Parent')
        child1 = model1.add(ArchiType.BusinessFunction, 'Child1')
        child2 = model1.add(ArchiType.BusinessFunction, 'Child2')
        child3 = model1.add(ArchiType.BusinessFunction, 'Child3')
        for child in [child1, child2, child3]:
            model1.add_child(parent.uuid, child.uuid)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        children = model2.get_children(parent.uuid)
        assert len(children) == 3
        parent_uuids = set()
        for c in children:
            c_parent = model2.get_parent(c.uuid)
            assert c_parent is not None
            parent_uuids.add(c_parent.uuid)
        assert len(parent_uuids) == 1
        assert parent_uuids.pop() == parent.uuid

    def test_round_trip_model_with_hierarchy_and_relationships(self):
        """Test: Hierarchy coexists with relationships; both preserved through round-trip."""
        model1 = Model('test_hierarchy_and_rels')
        parent = model1.add(ArchiType.BusinessProcess, 'Parent')
        child = model1.add(ArchiType.BusinessFunction, 'Child')
        other = model1.add(ArchiType.BusinessFunction, 'Other')
        model1.add_child(parent.uuid, child.uuid)
        model1.add_relationship(source=child.uuid, target=other.uuid, rel_type=ArchiType.Serving)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        child_parent = model2.get_parent(child.uuid)
        assert child_parent is not None
        assert child_parent.uuid == parent.uuid
        rels = list(model2.rels_dict.values())
        assert len(rels) == 1
        assert rels[0].source == child.uuid
        assert rels[0].target == other.uuid

    def test_round_trip_idempotent(self):
        """Test: Multiple round-trips preserve structure (idempotency)."""
        model1 = Model('test_idempotent')
        root = model1.add(ArchiType.BusinessProcess, 'Root')
        child = model1.add(ArchiType.BusinessFunction, 'Child')
        model1.add_child(root.uuid, child.uuid)

        for _ in range(3):
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, 'test.archimate')
                model1.write(filepath)
                model_next = Model('imported')
                model_next.read(filepath)
                next_child_parent = model_next.get_parent(child.uuid)
                assert next_child_parent is not None
                assert next_child_parent.uuid == root.uuid
                model1 = model_next

    def test_round_trip_with_empty_model(self):
        """Test: Empty model with no hierarchies imports cleanly."""
        model1 = Model('empty')
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.archimate')
            model1.write(filepath)
            model2 = Model('imported')
            model2.read(filepath)

        assert len(model2.elems_dict) == 0
        assert model2.get_root_elements() == []
