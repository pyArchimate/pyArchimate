"""Unit tests for Model hierarchy queries (P3 Phase 2)."""

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestGetParentQuery:
    """Test Model.get_parent() query method."""

    def test_get_parent_with_parent(self):
        """Test get_parent returns parent element."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(parent.uuid, child.uuid)

        result = model.get_parent(child.uuid)

        assert result == parent
        assert result.uuid == parent.uuid

    def test_get_parent_root_returns_none(self):
        """Test get_parent returns None for root element."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")

        result = model.get_parent(root.uuid)

        assert result is None

    def test_get_parent_orphaned_returns_none(self):
        """Test get_parent returns None for orphaned element."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        child = model.add(ArchiType.BusinessFunction, "Child")

        model.add_child(parent.uuid, child.uuid)
        model.remove_child(parent.uuid, child.uuid)

        result = model.get_parent(child.uuid)

        assert result is None


class TestGetChildrenQuery:
    """Test Model.get_children() query method."""

    def test_get_children_empty(self):
        """Test get_children returns empty list for element with no children."""
        model = Model("TestModel")
        elem = model.add(ArchiType.BusinessProcess, "Elem")

        result = model.get_children(elem.uuid)

        assert result == []

    def test_get_children_single(self):
        """Test get_children returns single child."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(parent.uuid, child.uuid)

        result = model.get_children(parent.uuid)

        assert result == [child]

    def test_get_children_multiple(self):
        """Test get_children returns all children."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        children = [
            model.add(ArchiType.BusinessFunction, "Child1"),
            model.add(ArchiType.BusinessFunction, "Child2"),
            model.add(ArchiType.BusinessFunction, "Child3"),
        ]

        for child in children:
            model.add_child(parent.uuid, child.uuid)

        result = model.get_children(parent.uuid)

        assert len(result) == 3
        assert set(result) == set(children)

    def test_get_children_does_not_include_parent(self):
        """Test get_children does not include the parent element."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(parent.uuid, child.uuid)

        result = model.get_children(parent.uuid)

        assert parent not in result


class TestGetAncestorsQuery:
    """Test Model.get_ancestors() query method."""

    def test_get_ancestors_root_returns_empty(self):
        """Test get_ancestors of root returns empty list."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")

        result = model.get_ancestors(root.uuid)

        assert result == []

    def test_get_ancestors_direct_child(self):
        """Test get_ancestors of direct child returns only parent."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(root.uuid, child.uuid)

        result = model.get_ancestors(child.uuid)

        assert result == [root]

    def test_get_ancestors_deeply_nested(self):
        """Test get_ancestors of deeply nested element (excludes self)."""
        model = Model("TestModel")
        elements = [model.add(ArchiType.BusinessProcess, f"Elem{i}") for i in range(5)]

        for i in range(4):
            model.add_child(elements[i].uuid, elements[i + 1].uuid)

        result = model.get_ancestors(elements[4].uuid)

        # Should be in reverse order, excluding the element itself: elem3, elem2, elem1, elem0
        assert result == elements[3::-1]

    def test_get_ancestors_includes_parent_first(self):
        """Test that get_ancestors includes the parent as first item."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(parent.uuid, child.uuid)

        result = model.get_ancestors(child.uuid)

        assert result[0] == parent

    def test_get_ancestors_excludes_non_ancestors(self):
        """Test that get_ancestors doesn't include non-ancestor elements."""
        model = Model("TestModel")
        parent1 = model.add(ArchiType.BusinessProcess, "Parent1")
        parent2 = model.add(ArchiType.BusinessProcess, "Parent2")
        child = model.add(ArchiType.BusinessFunction, "Child")

        model.add_child(parent1.uuid, child.uuid)

        result = model.get_ancestors(child.uuid)

        assert parent2 not in result


class TestGetDescendantsQuery:
    """Test Model.get_descendants() query method."""

    def test_get_descendants_leaf_returns_empty(self):
        """Test get_descendants of leaf element returns empty list."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(parent.uuid, child.uuid)

        result = model.get_descendants(child.uuid)

        assert result == []

    def test_get_descendants_one_level(self):
        """Test get_descendants one level deep."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        children = [
            model.add(ArchiType.BusinessFunction, "Child1"),
            model.add(ArchiType.BusinessFunction, "Child2"),
        ]

        for child in children:
            model.add_child(parent.uuid, child.uuid)

        result = model.get_descendants(parent.uuid)

        assert set(result) == set(children)

    def test_get_descendants_multiple_levels(self):
        """Test get_descendants across multiple levels."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")
        mid1 = model.add(ArchiType.BusinessFunction, "Mid1")
        mid2 = model.add(ArchiType.BusinessFunction, "Mid2")
        leaf1 = model.add(ArchiType.BusinessFunction, "Leaf1")
        leaf2 = model.add(ArchiType.BusinessFunction, "Leaf2")

        model.add_child(root.uuid, mid1.uuid)
        model.add_child(root.uuid, mid2.uuid)
        model.add_child(mid1.uuid, leaf1.uuid)
        model.add_child(mid2.uuid, leaf2.uuid)

        result = model.get_descendants(root.uuid)

        assert set(result) == {mid1, mid2, leaf1, leaf2}

    def test_get_descendants_breadth_first_order(self):
        """Test that get_descendants returns results in breadth-first order."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")
        mid1 = model.add(ArchiType.BusinessFunction, "Mid1")
        mid2 = model.add(ArchiType.BusinessFunction, "Mid2")
        leaf1 = model.add(ArchiType.BusinessFunction, "Leaf1")
        leaf2 = model.add(ArchiType.BusinessFunction, "Leaf2")

        model.add_child(root.uuid, mid1.uuid)
        model.add_child(root.uuid, mid2.uuid)
        model.add_child(mid1.uuid, leaf1.uuid)
        model.add_child(mid2.uuid, leaf2.uuid)

        result = model.get_descendants(root.uuid)

        # BFS order: mid1, mid2 should come before leaves
        mid_indices = [result.index(mid1), result.index(mid2)]
        leaf_indices = [result.index(leaf1), result.index(leaf2)]
        assert max(mid_indices) < min(leaf_indices)

    def test_get_descendants_excludes_self(self):
        """Test that get_descendants does not include the element itself."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(parent.uuid, child.uuid)

        result = model.get_descendants(parent.uuid)

        assert parent not in result


class TestGetDepthQuery:
    """Test Model.get_depth() query method."""

    def test_get_depth_root(self):
        """Test depth of root element is 0."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")

        assert model.get_depth(root.uuid) == 0

    def test_get_depth_direct_child(self):
        """Test depth of direct child is 1."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(parent.uuid, child.uuid)

        assert model.get_depth(child.uuid) == 1

    def test_get_depth_deeply_nested(self):
        """Test depth of deeply nested elements."""
        model = Model("TestModel")
        elements = [model.add(ArchiType.BusinessProcess, f"Elem{i}") for i in range(5)]

        for i in range(4):
            model.add_child(elements[i].uuid, elements[i + 1].uuid)

        for i, elem in enumerate(elements):
            assert model.get_depth(elem.uuid) == i

    def test_get_depth_max_depth(self):
        """Test depth when at maximum allowed nesting."""
        model = Model("TestModel")
        elements = [model.add(ArchiType.BusinessProcess, f"Elem{i}") for i in range(5)]

        for i in range(4):
            model.add_child(elements[i].uuid, elements[i + 1].uuid)

        assert model.get_depth(elements[4].uuid) == 4


class TestGetRootElementsQuery:
    """Test Model.get_root_elements() query method."""

    def test_get_root_elements_single_root(self):
        """Test with single root element."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(root.uuid, child.uuid)

        result = model.get_root_elements()

        assert result == [root]

    def test_get_root_elements_multiple_roots(self):
        """Test with multiple root elements."""
        model = Model("TestModel")
        root1 = model.add(ArchiType.BusinessProcess, "Root1")
        root2 = model.add(ArchiType.BusinessProcess, "Root2")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(root1.uuid, child.uuid)

        result = model.get_root_elements()

        assert set(result) == {root1, root2}

    def test_get_root_elements_no_roots(self):
        """Test with no elements returns empty list."""
        model = Model("TestModel")

        result = model.get_root_elements()

        assert result == []

    def test_get_root_elements_excludes_non_roots(self):
        """Test that get_root_elements doesn't include non-root elements."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(root.uuid, child.uuid)

        result = model.get_root_elements()

        assert child not in result


class TestGetLeafElementsQuery:
    """Test Model.get_leaf_elements() query method."""

    def test_get_leaf_elements_all_leaves(self):
        """Test when all elements are leaves."""
        model = Model("TestModel")
        elem1 = model.add(ArchiType.BusinessProcess, "Elem1")
        elem2 = model.add(ArchiType.BusinessFunction, "Elem2")

        result = model.get_leaf_elements()

        assert set(result) == {elem1, elem2}

    def test_get_leaf_elements_with_hierarchy(self):
        """Test with hierarchical structure."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")
        child1 = model.add(ArchiType.BusinessFunction, "Child1")
        child2 = model.add(ArchiType.BusinessFunction, "Child2")
        model.add_child(root.uuid, child1.uuid)
        model.add_child(root.uuid, child2.uuid)

        result = model.get_leaf_elements()

        assert set(result) == {child1, child2}

    def test_get_leaf_elements_excludes_non_leaves(self):
        """Test that get_leaf_elements doesn't include non-leaf elements."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(root.uuid, child.uuid)

        result = model.get_leaf_elements()

        assert root not in result

    def test_get_leaf_elements_no_leaves(self):
        """Test when no elements are leaves."""
        model = Model("TestModel")

        result = model.get_leaf_elements()

        assert result == []


class TestQueryConsistency:
    """Test consistency between different query methods."""

    def test_parent_child_consistency(self):
        """Test that get_parent and get_children are consistent."""
        model = Model("TestModel")
        parent = model.add(ArchiType.BusinessProcess, "Parent")
        child = model.add(ArchiType.BusinessFunction, "Child")
        model.add_child(parent.uuid, child.uuid)

        assert model.get_parent(child.uuid) == parent
        assert child in model.get_children(parent.uuid)

    def test_ancestors_descendants_consistency(self):
        """Test relationship between ancestors and descendants."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")
        mid = model.add(ArchiType.BusinessFunction, "Mid")
        leaf = model.add(ArchiType.BusinessFunction, "Leaf")

        model.add_child(root.uuid, mid.uuid)
        model.add_child(mid.uuid, leaf.uuid)

        ancestors = model.get_ancestors(leaf.uuid)
        descendants_of_root = model.get_descendants(root.uuid)

        # Ancestors should not include the element itself
        assert leaf not in ancestors
        # But should include its parents
        assert mid in ancestors
        assert root in ancestors
        # Descendants should include leaf
        assert leaf in descendants_of_root

    def test_root_and_leaf_consistency(self):
        """Test consistency of root and leaf detection."""
        model = Model("TestModel")
        root = model.add(ArchiType.BusinessProcess, "Root")
        mid = model.add(ArchiType.BusinessFunction, "Mid")
        leaf = model.add(ArchiType.BusinessFunction, "Leaf")

        model.add_child(root.uuid, mid.uuid)
        model.add_child(mid.uuid, leaf.uuid)

        roots = model.get_root_elements()
        leaves = model.get_leaf_elements()

        assert root in roots
        assert leaf in leaves
        assert mid not in roots
        assert mid not in leaves


class TestQueryOnEmptyModel:
    """Test query behavior on empty or minimal models."""

    def test_queries_on_empty_model(self):
        """Test that queries work correctly on empty model."""
        model = Model("EmptyModel")

        assert model.get_root_elements() == []
        assert model.get_leaf_elements() == []

    def test_single_element_model(self):
        """Test queries on model with single element."""
        model = Model("SingleModel")
        elem = model.add(ArchiType.BusinessProcess, "Elem")

        assert model.get_root_elements() == [elem]
        assert model.get_leaf_elements() == [elem]
        assert model.get_depth(elem.uuid) == 0
        assert model.get_children(elem.uuid) == []
        assert model.get_parent(elem.uuid) is None
