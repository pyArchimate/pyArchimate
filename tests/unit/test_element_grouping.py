"""Unit tests for Element grouping (P3 Phase 2)."""

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestAddChildBasic:
    """Test basic add_child functionality."""

    def test_add_child_valid(self):
        """Test adding a valid child to a parent."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(parent.uuid, child.uuid)

        assert child.parent_uuid == parent.uuid
        assert model._element_hierarchy[child.uuid] == parent.uuid
        assert child.uuid in model._element_children[parent.uuid]

    def test_add_multiple_children(self):
        """Test adding multiple children to same parent."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child1 = model.add(ArchiType.BusinessFunction, 'Child1')
        child2 = model.add(ArchiType.BusinessFunction, 'Child2')

        model.add_child(parent.uuid, child1.uuid)
        model.add_child(parent.uuid, child2.uuid)

        assert len(model.get_children(parent.uuid)) == 2
        assert child1.parent_uuid == parent.uuid
        assert child2.parent_uuid == parent.uuid

    def test_add_child_different_types(self):
        """Test adding children of different element types."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        func = model.add(ArchiType.BusinessFunction, 'Function')
        interaction = model.add(ArchiType.BusinessInteraction, 'Interaction')

        model.add_child(parent.uuid, func.uuid)
        model.add_child(parent.uuid, interaction.uuid)

        children = model.get_children(parent.uuid)
        assert len(children) == 2
        assert func in children
        assert interaction in children


class TestAddChildErrors:
    """Test add_child error conditions."""

    def test_add_child_parent_not_found(self):
        """Test error when parent UUID doesn't exist."""
        model = Model('TestModel')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        with pytest.raises(KeyError, match="Parent element .* not found"):
            model.add_child('nonexistent-uuid', child.uuid)

    def test_add_child_child_not_found(self):
        """Test error when child UUID doesn't exist."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')

        with pytest.raises(KeyError, match="Child element .* not found"):
            model.add_child(parent.uuid, 'nonexistent-uuid')

    def test_add_child_already_has_parent(self):
        """Test error when child already has a parent."""
        model = Model('TestModel')
        parent1 = model.add(ArchiType.BusinessProcess, 'Parent1')
        parent2 = model.add(ArchiType.BusinessProcess, 'Parent2')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(parent1.uuid, child.uuid)

        with pytest.raises(ValueError, match="already has parent"):
            model.add_child(parent2.uuid, child.uuid)

    def test_add_child_self_reference(self):
        """Test error when element tries to be its own parent."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Element')

        with pytest.raises(ValueError, match="Cycle detected"):
            model.add_child(elem.uuid, elem.uuid)

    def test_add_child_direct_cycle(self):
        """Test error when adding would create a direct cycle."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(parent.uuid, child.uuid)

        with pytest.raises(ValueError, match="Cycle detected"):
            model.add_child(child.uuid, parent.uuid)

    def test_add_child_indirect_cycle(self):
        """Test error when adding would create an indirect cycle."""
        model = Model('TestModel')
        root = model.add(ArchiType.BusinessProcess, 'Root')
        mid = model.add(ArchiType.BusinessFunction, 'Mid')
        leaf = model.add(ArchiType.BusinessFunction, 'Leaf')

        model.add_child(root.uuid, mid.uuid)
        model.add_child(mid.uuid, leaf.uuid)

        with pytest.raises(ValueError, match="Cycle detected"):
            model.add_child(leaf.uuid, root.uuid)

    def test_add_child_depth_exceeded(self):
        """Test error when max depth is exceeded."""
        model = Model('TestModel')

        elements = [model.add(ArchiType.BusinessProcess, f'Elem{i}') for i in range(6)]

        # Create chain of 4 relationships (depths 0-4), which should succeed
        for i in range(4):
            model.add_child(elements[i].uuid, elements[i+1].uuid)

        # Try to add 5th relationship (elements[4] → elements[5]),
        # which would create depth 5, exceeding MAX_DEPTH=5
        with pytest.raises(ValueError, match="Max nesting depth"):
            model.add_child(elements[4].uuid, elements[5].uuid)


class TestRemoveChild:
    """Test remove_child functionality."""

    def test_remove_child_valid(self):
        """Test removing a valid parent-child relationship."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(parent.uuid, child.uuid)
        model.remove_child(parent.uuid, child.uuid)

        assert child.parent_uuid is None
        assert child.uuid not in model._element_hierarchy
        assert child.uuid not in model._element_children.get(parent.uuid, set())

    def test_remove_child_not_parent(self):
        """Test error when removing non-parent relationship."""
        model = Model('TestModel')
        parent1 = model.add(ArchiType.BusinessProcess, 'Parent1')
        parent2 = model.add(ArchiType.BusinessProcess, 'Parent2')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(parent1.uuid, child.uuid)

        with pytest.raises(ValueError, match="is not a child of"):
            model.remove_child(parent2.uuid, child.uuid)

    def test_remove_child_parent_not_found(self):
        """Test error when parent UUID doesn't exist."""
        model = Model('TestModel')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        with pytest.raises(KeyError):
            model.remove_child('nonexistent-uuid', child.uuid)

    def test_remove_child_child_not_found(self):
        """Test error when child UUID doesn't exist."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')

        with pytest.raises(KeyError):
            model.remove_child(parent.uuid, 'nonexistent-uuid')


class TestDepth:
    """Test depth calculation."""

    def test_depth_root_element(self):
        """Test depth of root element (should be 0)."""
        model = Model('TestModel')
        root = model.add(ArchiType.BusinessProcess, 'Root')

        assert model.get_depth(root.uuid) == 0

    def test_depth_direct_child(self):
        """Test depth of direct child (should be 1)."""
        model = Model('TestModel')
        root = model.add(ArchiType.BusinessProcess, 'Root')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(root.uuid, child.uuid)

        assert model.get_depth(child.uuid) == 1

    def test_depth_nested_elements(self):
        """Test depth of deeply nested elements."""
        model = Model('TestModel')
        elements = [model.add(ArchiType.BusinessProcess, f'Elem{i}') for i in range(5)]

        for i in range(4):
            model.add_child(elements[i].uuid, elements[i+1].uuid)

        assert model.get_depth(elements[0].uuid) == 0
        assert model.get_depth(elements[1].uuid) == 1
        assert model.get_depth(elements[4].uuid) == 4


class TestElementDeletion:
    """Test element deletion and orphaning."""

    def test_delete_orphans_children(self):
        """Test that deleting parent orphans its children."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(parent.uuid, child.uuid)
        parent.delete()

        assert child.parent_uuid is None
        assert child.uuid not in model._element_hierarchy

    def test_delete_with_multiple_children(self):
        """Test that deleting parent with multiple children orphans all."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child1 = model.add(ArchiType.BusinessFunction, 'Child1')
        child2 = model.add(ArchiType.BusinessFunction, 'Child2')

        model.add_child(parent.uuid, child1.uuid)
        model.add_child(parent.uuid, child2.uuid)

        parent.delete()

        assert child1.parent_uuid is None
        assert child2.parent_uuid is None

    def test_delete_nested_preserves_hierarchy(self):
        """Test that deleting middle element preserves grandchildren."""
        model = Model('TestModel')
        grandparent = model.add(ArchiType.BusinessProcess, 'GrandParent')
        parent = model.add(ArchiType.BusinessFunction, 'Parent')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(grandparent.uuid, parent.uuid)
        model.add_child(parent.uuid, child.uuid)

        parent.delete()

        assert child.parent_uuid is None
        assert child in model.elems_dict.values()


class TestCycleDetection:
    """Test cycle detection in complex scenarios."""

    def test_no_cycle_linear_chain(self):
        """Test that linear chain doesn't create cycles."""
        model = Model('TestModel')
        elements = [model.add(ArchiType.BusinessProcess, f'Elem{i}') for i in range(5)]

        for i in range(4):
            model.add_child(elements[i].uuid, elements[i+1].uuid)

        assert model._would_create_cycle(elements[4].uuid, elements[0].uuid) is True

    def test_cycle_detection_three_way(self):
        """Test cycle detection in three-element scenario."""
        model = Model('TestModel')
        a = model.add(ArchiType.BusinessProcess, 'A')
        b = model.add(ArchiType.BusinessProcess, 'B')
        c = model.add(ArchiType.BusinessProcess, 'C')

        model.add_child(a.uuid, b.uuid)
        model.add_child(b.uuid, c.uuid)

        assert model._would_create_cycle(c.uuid, a.uuid) is True


class TestGetParent:
    """Test get_parent method."""

    def test_get_parent_existing(self):
        """Test getting parent of element with parent."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(parent.uuid, child.uuid)

        assert model.get_parent(child.uuid) == parent

    def test_get_parent_root(self):
        """Test getting parent of root element returns None."""
        model = Model('TestModel')
        root = model.add(ArchiType.BusinessProcess, 'Root')

        assert model.get_parent(root.uuid) is None


class TestGetChildren:
    """Test get_children method."""

    def test_get_children_empty(self):
        """Test getting children of element with no children."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        assert model.get_children(elem.uuid) == []

    def test_get_children_one(self):
        """Test getting single child."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(parent.uuid, child.uuid)

        assert model.get_children(parent.uuid) == [child]

    def test_get_children_multiple(self):
        """Test getting multiple children."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child1 = model.add(ArchiType.BusinessFunction, 'Child1')
        child2 = model.add(ArchiType.BusinessFunction, 'Child2')
        child3 = model.add(ArchiType.BusinessFunction, 'Child3')

        model.add_child(parent.uuid, child1.uuid)
        model.add_child(parent.uuid, child2.uuid)
        model.add_child(parent.uuid, child3.uuid)

        children = model.get_children(parent.uuid)
        assert len(children) == 3
        assert set(children) == {child1, child2, child3}


class TestGetAncestors:
    """Test get_ancestors method."""

    def test_get_ancestors_root(self):
        """Test ancestors of root element (should be empty)."""
        model = Model('TestModel')
        root = model.add(ArchiType.BusinessProcess, 'Root')

        ancestors = model.get_ancestors(root.uuid)
        assert ancestors == []

    def test_get_ancestors_direct_child(self):
        """Test ancestors of direct child (should be just parent)."""
        model = Model('TestModel')
        root = model.add(ArchiType.BusinessProcess, 'Root')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(root.uuid, child.uuid)

        ancestors = model.get_ancestors(child.uuid)
        assert ancestors == [root]

    def test_get_ancestors_nested(self):
        """Test ancestors of deeply nested element (excludes self)."""
        model = Model('TestModel')
        elements = [model.add(ArchiType.BusinessProcess, f'Elem{i}') for i in range(5)]

        for i in range(4):
            model.add_child(elements[i].uuid, elements[i+1].uuid)

        ancestors = model.get_ancestors(elements[4].uuid)
        # Should be [elem3, elem2, elem1, elem0] - excludes elem4 itself
        assert ancestors == elements[:4][::-1]


class TestGetDescendants:
    """Test get_descendants method."""

    def test_get_descendants_leaf(self):
        """Test descendants of leaf element (should be empty)."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(parent.uuid, child.uuid)

        assert model.get_descendants(child.uuid) == []

    def test_get_descendants_one_level(self):
        """Test descendants one level deep."""
        model = Model('TestModel')
        parent = model.add(ArchiType.BusinessProcess, 'Parent')
        child1 = model.add(ArchiType.BusinessFunction, 'Child1')
        child2 = model.add(ArchiType.BusinessFunction, 'Child2')

        model.add_child(parent.uuid, child1.uuid)
        model.add_child(parent.uuid, child2.uuid)

        descendants = model.get_descendants(parent.uuid)
        assert set(descendants) == {child1, child2}

    def test_get_descendants_multiple_levels(self):
        """Test descendants across multiple levels."""
        model = Model('TestModel')
        root = model.add(ArchiType.BusinessProcess, 'Root')
        mid1 = model.add(ArchiType.BusinessFunction, 'Mid1')
        mid2 = model.add(ArchiType.BusinessFunction, 'Mid2')
        leaf1 = model.add(ArchiType.BusinessFunction, 'Leaf1')
        leaf2 = model.add(ArchiType.BusinessFunction, 'Leaf2')

        model.add_child(root.uuid, mid1.uuid)
        model.add_child(root.uuid, mid2.uuid)
        model.add_child(mid1.uuid, leaf1.uuid)
        model.add_child(mid2.uuid, leaf2.uuid)

        descendants = model.get_descendants(root.uuid)
        assert set(descendants) == {mid1, mid2, leaf1, leaf2}


class TestGetRootElements:
    """Test get_root_elements method."""

    def test_get_root_elements_single(self):
        """Test with single root element."""
        model = Model('TestModel')
        root = model.add(ArchiType.BusinessProcess, 'Root')
        child = model.add(ArchiType.BusinessFunction, 'Child')

        model.add_child(root.uuid, child.uuid)

        roots = model.get_root_elements()
        assert roots == [root]

    def test_get_root_elements_multiple(self):
        """Test with multiple root elements."""
        model = Model('TestModel')
        root1 = model.add(ArchiType.BusinessProcess, 'Root1')
        root2 = model.add(ArchiType.BusinessProcess, 'Root2')
        child1 = model.add(ArchiType.BusinessFunction, 'Child1')

        model.add_child(root1.uuid, child1.uuid)

        roots = model.get_root_elements()
        assert set(roots) == {root1, root2}


class TestGetLeafElements:
    """Test get_leaf_elements method."""

    def test_get_leaf_elements_all_leaves(self):
        """Test with all elements being leaves."""
        model = Model('TestModel')
        elem1 = model.add(ArchiType.BusinessProcess, 'Elem1')
        elem2 = model.add(ArchiType.BusinessFunction, 'Elem2')

        leaves = model.get_leaf_elements()
        assert set(leaves) == {elem1, elem2}

    def test_get_leaf_elements_with_hierarchy(self):
        """Test with hierarchical structure."""
        model = Model('TestModel')
        root = model.add(ArchiType.BusinessProcess, 'Root')
        child1 = model.add(ArchiType.BusinessFunction, 'Child1')
        child2 = model.add(ArchiType.BusinessFunction, 'Child2')

        model.add_child(root.uuid, child1.uuid)
        model.add_child(root.uuid, child2.uuid)

        leaves = model.get_leaf_elements()
        assert set(leaves) == {child1, child2}
