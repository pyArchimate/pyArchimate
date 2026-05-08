"""Unit tests for SVG z-order sorting with nested nodes."""

from src.pyArchimate.model import Model
from src.pyArchimate.view import View
from src.pyArchimate.view.layout.export.svg_export import SVGExportService


class TestSVGZOrderSorting:
    """Test suite for SVGExportService._sort_nodes_by_hierarchy()."""

    def test_sort_parents_before_children(self):
        """Verify parents in output list before their children."""
        # Setup
        model = Model()
        view = View(name="Test View", uuid="test-view", parent=model)
        model.views_dict[view.uuid] = view

        # Create parent and child nodes
        parent_node = view.add(ref=None, x=100, y=100, w=200, h=200,
                               node_type='Label', label='Parent')
        child_node = parent_node.add(ref=None, x=20, y=20, w=100, h=100,
                                     node_type='Label', label='Child')

        # Execute sort
        service = SVGExportService()
        sorted_nodes = service._sort_nodes_by_hierarchy(view)

        # Verify: parent appears before child in sorted list
        parent_idx = next(i for i, n in enumerate(sorted_nodes) if n.uuid == parent_node.uuid)
        child_idx = next(i for i, n in enumerate(sorted_nodes) if n.uuid == child_node.uuid)

        assert parent_idx < child_idx, "Parent should appear before child in sorted order"
        assert sorted_nodes[0] == parent_node, "First node should be the parent"
        assert sorted_nodes[1] == child_node, "Second node should be the child"

    def test_sort_preserves_view_root_nodes(self):
        """Verify nodes with View parent maintain compatibility."""
        # Setup
        model = Model()
        view = View(name="Test View", uuid="test-view", parent=model)
        model.views_dict[view.uuid] = view

        # Create multiple root-level nodes
        node1 = view.add(ref=None, x=0, y=0, w=100, h=100, node_type='Label', label='Node1')
        node2 = view.add(ref=None, x=150, y=0, w=100, h=100, node_type='Label', label='Node2')
        node3 = view.add(ref=None, x=300, y=0, w=100, h=100, node_type='Label', label='Node3')

        # Execute sort
        service = SVGExportService()
        sorted_nodes = service._sort_nodes_by_hierarchy(view)

        # Verify: root nodes appear in sorted list, count matches
        assert len(sorted_nodes) == 3, "Should have 3 root nodes"
        node_uuids = {n.uuid for n in sorted_nodes}
        assert node1.uuid in node_uuids, "Node1 should be in sorted list"
        assert node2.uuid in node_uuids, "Node2 should be in sorted list"
        assert node3.uuid in node_uuids, "Node3 should be in sorted list"

    def test_sort_handles_deep_nesting(self):
        """Verify deeply nested nodes maintain hierarchy without stack overflow."""
        # Setup: Create nested structure: root -> parent1 -> parent2 -> child
        model = Model()
        view = View(name="Test View", uuid="test-view", parent=model)
        model.views_dict[view.uuid] = view

        root = view.add(ref=None, x=0, y=0, w=300, h=300,
                        node_type='Label', label='Root')
        parent1 = root.add(ref=None, x=50, y=50, w=200, h=200,
                           node_type='Label', label='Parent1')
        parent2 = parent1.add(ref=None, x=50, y=50, w=100, h=100,
                              node_type='Label', label='Parent2')
        child = parent2.add(ref=None, x=10, y=10, w=80, h=80,
                            node_type='Label', label='Child')

        # Execute sort
        service = SVGExportService()
        sorted_nodes = service._sort_nodes_by_hierarchy(view)

        # Verify: all nodes appear in correct order
        assert len(sorted_nodes) == 4, "Should have 4 nodes (root, 2 parents, 1 child)"

        indices = {n.uuid: i for i, n in enumerate(sorted_nodes)}
        assert indices[root.uuid] < indices[parent1.uuid], "Root before Parent1"
        assert indices[parent1.uuid] < indices[parent2.uuid], "Parent1 before Parent2"
        assert indices[parent2.uuid] < indices[child.uuid], "Parent2 before Child"

    def test_sort_empty_node_list(self):
        """Verify edge case with no nodes."""
        # Setup: Empty view
        model = Model()
        view = View(name="Empty View", uuid="empty-view", parent=model)
        model.views_dict[view.uuid] = view

        # Execute sort
        service = SVGExportService()
        sorted_nodes = service._sort_nodes_by_hierarchy(view)

        # Verify: returns empty list without error
        assert sorted_nodes == [], "Empty view should return empty node list"

    def test_sort_single_node(self):
        """Verify single node case."""
        # Setup
        model = Model()
        view = View(name="Test View", uuid="test-view", parent=model)
        model.views_dict[view.uuid] = view

        node = view.add(ref=None, x=0, y=0, w=100, h=100,
                        node_type='Label', label='SingleNode')

        # Execute sort
        service = SVGExportService()
        sorted_nodes = service._sort_nodes_by_hierarchy(view)

        # Verify
        assert len(sorted_nodes) == 1, "Should have 1 node"
        assert sorted_nodes[0] == node, "Node should be in sorted list"

    def test_sort_prevents_duplicates(self):
        """Verify no duplicate nodes in sorted output."""
        # Setup: Create parent with multiple children
        model = Model()
        view = View(name="Test View", uuid="test-view", parent=model)
        model.views_dict[view.uuid] = view

        parent = view.add(ref=None, x=0, y=0, w=300, h=300,
                          node_type='Label', label='Parent')
        child1 = parent.add(ref=None, x=10, y=10, w=100, h=100,
                            node_type='Label', label='Child1')
        child2 = parent.add(ref=None, x=120, y=10, w=100, h=100,
                            node_type='Label', label='Child2')

        # Execute sort
        service = SVGExportService()
        sorted_nodes = service._sort_nodes_by_hierarchy(view)

        # Verify: no duplicates and correct count
        node_uuids = [n.uuid for n in sorted_nodes]
        assert len(node_uuids) == len(set(node_uuids)), "Should not have duplicate nodes"
        assert len(sorted_nodes) == 3, "Should have exactly 3 nodes"
        # Verify parent and children are present
        assert parent.uuid in node_uuids, "Parent should be in sorted list"
        assert child1.uuid in node_uuids, "Child1 should be in sorted list"
        assert child2.uuid in node_uuids, "Child2 should be in sorted list"

    def test_sort_multiple_siblings(self):
        """Verify correct ordering with multiple sibling nodes."""
        # Setup: Create parent with multiple children
        model = Model()
        view = View(name="Test View", uuid="test-view", parent=model)
        model.views_dict[view.uuid] = view

        parent = view.add(ref=None, x=0, y=0, w=400, h=200,
                          node_type='Label', label='Parent')
        child1 = parent.add(ref=None, x=10, y=10, w=80, h=80, node_type='Label', label='Child1')
        child2 = parent.add(ref=None, x=100, y=10, w=80, h=80, node_type='Label', label='Child2')
        child3 = parent.add(ref=None, x=190, y=10, w=80, h=80, node_type='Label', label='Child3')

        # Execute sort
        service = SVGExportService()
        sorted_nodes = service._sort_nodes_by_hierarchy(view)

        # Verify: parent before all children
        parent_idx = next(i for i, n in enumerate(sorted_nodes) if n.uuid == parent.uuid)
        child_indices = {
            child1.uuid: next(i for i, n in enumerate(sorted_nodes) if n.uuid == child1.uuid),
            child2.uuid: next(i for i, n in enumerate(sorted_nodes) if n.uuid == child2.uuid),
            child3.uuid: next(i for i, n in enumerate(sorted_nodes) if n.uuid == child3.uuid),
        }

        for child_idx in child_indices.values():
            assert parent_idx < child_idx, "Parent should appear before child"
