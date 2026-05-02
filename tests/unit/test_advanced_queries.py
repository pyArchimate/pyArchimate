"""Unit tests for advanced hierarchy query methods.

Tests cover get_siblings() and find_by_hierarchy_path() functionality.
"""

import pytest
from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestAdvancedQueries:
    """T054: Advanced query methods (get_siblings, find_by_hierarchy_path)."""

    def test_get_siblings_single_parent_multiple_children(self):
        """Test getting siblings when parent has multiple children."""
        m = Model('test-model')
        parent = m.add(ArchiType.BusinessProcess, 'Parent')
        child1 = m.add(ArchiType.BusinessFunction, 'Child 1')
        child2 = m.add(ArchiType.BusinessFunction, 'Child 2')
        child3 = m.add(ArchiType.BusinessFunction, 'Child 3')

        m.add_child(parent.uuid, child1.uuid)
        m.add_child(parent.uuid, child2.uuid)
        m.add_child(parent.uuid, child3.uuid)

        siblings1 = m.get_siblings(child1.uuid)
        assert len(siblings1) == 2
        sibling_uuids = {s.uuid for s in siblings1}
        assert child2.uuid in sibling_uuids
        assert child3.uuid in sibling_uuids
        assert child1.uuid not in sibling_uuids

    def test_get_siblings_root_element_no_siblings(self):
        """Test that root elements have no siblings."""
        m = Model('test-model')
        root = m.add(ArchiType.BusinessProcess, 'Root')
        siblings = m.get_siblings(root.uuid)
        assert siblings == []

    def test_get_siblings_single_child_no_other_siblings(self):
        """Test element with no siblings."""
        m = Model('test-model')
        parent = m.add(ArchiType.BusinessProcess, 'Parent')
        only_child = m.add(ArchiType.BusinessFunction, 'Only Child')
        m.add_child(parent.uuid, only_child.uuid)

        siblings = m.get_siblings(only_child.uuid)
        assert siblings == []

    def test_get_siblings_missing_element_raises(self):
        """Test that get_siblings raises for missing element."""
        m = Model('test-model')
        with pytest.raises(KeyError):
            m.get_siblings('missing-uuid')

    def test_get_siblings_with_multiple_levels(self):
        """Test get_siblings in multi-level hierarchy."""
        m = Model('test-model')
        grandparent = m.add(ArchiType.BusinessProcess, 'Grandparent')
        parent = m.add(ArchiType.BusinessProcess, 'Parent')
        uncle = m.add(ArchiType.BusinessProcess, 'Uncle')
        child = m.add(ArchiType.BusinessFunction, 'Child')

        m.add_child(grandparent.uuid, parent.uuid)
        m.add_child(grandparent.uuid, uncle.uuid)
        m.add_child(parent.uuid, child.uuid)

        # Parent and Uncle are siblings
        parent_siblings = m.get_siblings(parent.uuid)
        assert len(parent_siblings) == 1
        assert parent_siblings[0].uuid == uncle.uuid

        # Child has no siblings
        child_siblings = m.get_siblings(child.uuid)
        assert child_siblings == []

    def test_find_by_hierarchy_path_single_level(self):
        """Test finding element at root level by name."""
        m = Model('test-model')
        root = m.add(ArchiType.BusinessProcess, 'Root')
        _other = m.add(ArchiType.BusinessProcess, 'Other')

        results = m.find_by_hierarchy_path('/Root')
        assert len(results) == 1
        assert results[0].uuid == root.uuid

    def test_find_by_hierarchy_path_two_levels(self):
        """Test finding element at two levels deep."""
        m = Model('test-model')
        parent = m.add(ArchiType.BusinessProcess, 'Parent')
        child = m.add(ArchiType.BusinessFunction, 'Child')
        m.add_child(parent.uuid, child.uuid)

        results = m.find_by_hierarchy_path('/Parent/Child')
        assert len(results) == 1
        assert results[0].uuid == child.uuid

    def test_find_by_hierarchy_path_three_levels(self):
        """Test finding element at three levels deep."""
        m = Model('test-model')
        grandparent = m.add(ArchiType.BusinessProcess, 'Grandparent')
        parent = m.add(ArchiType.BusinessProcess, 'Parent')
        child = m.add(ArchiType.BusinessFunction, 'Child')

        m.add_child(grandparent.uuid, parent.uuid)
        m.add_child(parent.uuid, child.uuid)

        results = m.find_by_hierarchy_path('/Grandparent/Parent/Child')
        assert len(results) == 1
        assert results[0].uuid == child.uuid

    def test_find_by_hierarchy_path_wildcard_direct_children(self):
        """Test wildcard to find direct children of an element."""
        m = Model('test-model')
        parent = m.add(ArchiType.BusinessProcess, 'Parent')
        child1 = m.add(ArchiType.BusinessFunction, 'Child 1')
        child2 = m.add(ArchiType.BusinessFunction, 'Child 2')
        child3 = m.add(ArchiType.BusinessFunction, 'Child 3')

        m.add_child(parent.uuid, child1.uuid)
        m.add_child(parent.uuid, child2.uuid)
        m.add_child(parent.uuid, child3.uuid)

        results = m.find_by_hierarchy_path('/Parent/*')
        assert len(results) == 3
        result_uuids = {r.uuid for r in results}
        assert child1.uuid in result_uuids
        assert child2.uuid in result_uuids
        assert child3.uuid in result_uuids

    def test_find_by_hierarchy_path_wildcard_all_at_level(self):
        """Test wildcard to match all elements at a given level."""
        m = Model('test-model')
        _root1 = m.add(ArchiType.BusinessProcess, 'Root')
        _root2 = m.add(ArchiType.BusinessProcess, 'Root')

        results = m.find_by_hierarchy_path('/Root')
        assert len(results) == 2

    def test_find_by_hierarchy_path_nonexistent_returns_empty(self):
        """Test that nonexistent path returns empty list."""
        m = Model('test-model')
        _parent = m.add(ArchiType.BusinessProcess, 'Parent')

        results = m.find_by_hierarchy_path('/Parent/Nonexistent')
        assert results == []

    def test_find_by_hierarchy_path_empty_path_returns_empty(self):
        """Test that empty path returns empty list."""
        m = Model('test-model')
        _elem = m.add(ArchiType.BusinessProcess, 'Element')

        results = m.find_by_hierarchy_path('')
        assert results == []

    def test_find_by_hierarchy_path_root_slash_only(self):
        """Test path with only root separator."""
        m = Model('test-model')
        _elem = m.add(ArchiType.BusinessProcess, 'Element')

        results = m.find_by_hierarchy_path('/')
        assert results == []

    def test_find_by_hierarchy_path_with_sibling_elements(self):
        """Test finding element when siblings exist."""
        m = Model('test-model')
        parent = m.add(ArchiType.BusinessProcess, 'Parent')
        child1 = m.add(ArchiType.BusinessFunction, 'Child')
        child2 = m.add(ArchiType.BusinessFunction, 'Child')

        m.add_child(parent.uuid, child1.uuid)
        m.add_child(parent.uuid, child2.uuid)

        results = m.find_by_hierarchy_path('/Parent/Child')
        assert len(results) == 2
        result_uuids = {r.uuid for r in results}
        assert child1.uuid in result_uuids
        assert child2.uuid in result_uuids

    def test_find_by_hierarchy_path_wildcard_nested(self):
        """Test wildcard with nested hierarchy."""
        m = Model('test-model')
        grandparent = m.add(ArchiType.BusinessProcess, 'Grandparent')
        parent1 = m.add(ArchiType.BusinessProcess, 'Parent')
        parent2 = m.add(ArchiType.BusinessProcess, 'Parent')
        grandchild1 = m.add(ArchiType.BusinessFunction, 'Grandchild')
        grandchild2 = m.add(ArchiType.BusinessFunction, 'Grandchild')

        m.add_child(grandparent.uuid, parent1.uuid)
        m.add_child(grandparent.uuid, parent2.uuid)
        m.add_child(parent1.uuid, grandchild1.uuid)
        m.add_child(parent2.uuid, grandchild2.uuid)

        results = m.find_by_hierarchy_path('/Grandparent/Parent/*')
        assert len(results) == 2
        result_uuids = {r.uuid for r in results}
        assert grandchild1.uuid in result_uuids
        assert grandchild2.uuid in result_uuids

    def test_siblings_consistency_with_parent_child(self):
        """Test that siblings are consistent with add_child/get_children."""
        m = Model('test-model')
        parent = m.add(ArchiType.BusinessProcess, 'Parent')
        child1 = m.add(ArchiType.BusinessFunction, 'Child 1')
        child2 = m.add(ArchiType.BusinessFunction, 'Child 2')

        m.add_child(parent.uuid, child1.uuid)
        m.add_child(parent.uuid, child2.uuid)

        # All children should be siblings with each other
        child1_siblings = m.get_siblings(child1.uuid)
        child2_siblings = m.get_siblings(child2.uuid)

        assert child2.uuid in {s.uuid for s in child1_siblings}
        assert child1.uuid in {s.uuid for s in child2_siblings}

        # Siblings should match get_children minus self
        all_children = m.get_children(parent.uuid)
        assert len(child1_siblings) == len(all_children) - 1

    def test_find_by_path_matches_hierarchy(self):
        """Test that find_by_hierarchy_path respects actual hierarchy."""
        m = Model('test-model')
        parent = m.add(ArchiType.BusinessProcess, 'Parent')
        child = m.add(ArchiType.BusinessFunction, 'Child')
        grandchild = m.add(ArchiType.BusinessService, 'Grandchild')

        m.add_child(parent.uuid, child.uuid)
        m.add_child(child.uuid, grandchild.uuid)

        # Should find through correct path
        results = m.find_by_hierarchy_path('/Parent/Child/Grandchild')
        assert len(results) == 1
        assert results[0].uuid == grandchild.uuid

        # Should not find through incorrect path
        results = m.find_by_hierarchy_path('/Parent/Grandchild')
        assert results == []
