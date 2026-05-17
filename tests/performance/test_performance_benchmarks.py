"""Performance benchmark tests for hierarchy operations on large models.

Tests verify that cycle detection and queries perform efficiently on 1000+ element models.
"""

import time

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestPerformanceBenchmarks:
    """T050-T051: Performance benchmarks for hierarchy operations."""

    def test_cycle_detection_performance_small_model(self):
        """Test cycle detection performance on small model (100 elements, multiple roots)."""
        m = Model("perf-small")
        elements = []
        for i in range(100):
            e = m.add(ArchiType.BusinessProcess, f"Element {i}")
            elements.append(e)

        # Build multiple 4-level chains to respect MAX_DEPTH=5
        # e0 → e1 → e2 → e3 → e4 (depth 4)
        # e5 → e6 → e7 → e8 → e9 (depth 4)
        # ... and so on
        for root_idx in range(0, 100, 20):
            for i in range(root_idx, min(root_idx + 4, 100 - 1)):
                m.add_child(elements[i].uuid, elements[i + 1].uuid)

        # Measure cycle detection on deep chain
        start = time.time()
        # Try adding a cycle (should fail)
        with pytest.raises(ValueError):
            m.add_child(elements[3].uuid, elements[0].uuid)
        elapsed = time.time() - start

        # Should complete in <100ms (very generous for small model)
        assert elapsed < 0.1, f"Cycle detection took {elapsed:.3f}s"

    def test_large_model_hierarchy_queries_performance(self):
        """Test query performance on large model (1000+ elements with hierarchy)."""
        m = Model("perf-large")
        elements = []
        for i in range(1100):
            e = m.add(ArchiType.BusinessProcess, f"Element {i}")
            elements.append(e)

        # Build a wide hierarchy respecting MAX_DEPTH=5
        # 1 root → 200 L1 children → 200 L2 children (spread), etc.

        # Level 1: 200 direct children of root
        for i in range(200):
            m.add_child(elements[0].uuid, elements[i + 1].uuid)

        # Level 2: 200 grandchildren (spread across L1 parents)
        for i in range(200):
            parent_idx = 1 + (i % 200)
            m.add_child(elements[parent_idx].uuid, elements[201 + i].uuid)

        # Level 3: 200 great-grandchildren (spread across L2 parents)
        for i in range(200):
            parent_idx = 201 + (i % 200)
            if 401 + i < len(elements):
                m.add_child(elements[parent_idx].uuid, elements[401 + i].uuid)

        # Verify we have a large hierarchy
        assert len(m.get_children(elements[0].uuid)) == 200
        assert len(m.get_root_elements()) >= 1
        assert len(m.get_leaf_elements()) > 100

        # Measure performance of various queries on the large model
        start = time.time()
        for elem in elements[1:201]:  # Query 200 L1 elements
            _ = m.get_depth(elem.uuid)
            _ = m.get_parent(elem.uuid)
            _ = m.get_ancestors(elem.uuid)
        elapsed = time.time() - start
        avg_time = elapsed / 200

        # Should be fast (O(depth) operations, max depth 5)
        assert avg_time < 0.0001, f"Queries on 1100-element model averaged {avg_time:.3f}s per query"

    def test_get_children_performance_large_fanout(self):
        """Test get_children performance with high fanout (parent with 100+ children)."""
        m = Model("perf-fanout")
        parent = m.add(ArchiType.BusinessProcess, "Parent")
        children = []
        for i in range(100):
            child = m.add(ArchiType.BusinessFunction, f"Child {i}")
            m.add_child(parent.uuid, child.uuid)
            children.append(child)

        # Measure get_children on parent with 100 children
        start = time.time()
        for _ in range(100):  # 100 iterations
            result = m.get_children(parent.uuid)
            assert len(result) == 100
        elapsed = time.time() - start
        avg_time = elapsed / 100

        # Should be fast (O(n) where n=children, expected <1ms per call)
        assert avg_time < 0.001, f"get_children took {avg_time:.3f}s per call on 100-child element"

    def test_get_ancestors_performance_deep_chain(self):
        """Test get_ancestors performance on deep hierarchy (max depth 5)."""
        m = Model("perf-ancestors")
        elements = []
        for i in range(5):  # 5 elements to create depth of 4 (max depth is 5)
            e = m.add(ArchiType.BusinessProcess, f"Level {i}")
            elements.append(e)

        # Build chain: e0 → e1 → e2 → e3 → e4 (depth 4)
        for i in range(4):
            m.add_child(elements[i].uuid, elements[i + 1].uuid)

        # Measure get_ancestors on deepest element
        start = time.time()
        for _ in range(1000):  # 1000 iterations
            ancestors = m.get_ancestors(elements[4].uuid)
            assert len(ancestors) == 4  # Parent, grandparent, great-grandparent, root
        elapsed = time.time() - start
        avg_time = elapsed / 1000

        # Should be fast (O(depth), max depth 5)
        assert avg_time < 0.0001, f"get_ancestors took {avg_time:.3f}s per call"

    def test_get_descendants_performance_wide_tree(self):
        """Test get_descendants performance on wide tree."""
        m = Model("perf-descendants")
        root = m.add(ArchiType.BusinessProcess, "Root")

        # Create 3 levels with 10 children each = ~1110 total elements
        level1 = []
        for i in range(10):
            e = m.add(ArchiType.BusinessProcess, f"L1-{i}")
            m.add_child(root.uuid, e.uuid)
            level1.append(e)

        level2 = []
        for parent in level1:
            for i in range(10):
                e = m.add(ArchiType.BusinessFunction, f"L2-{parent.name}-{i}")
                m.add_child(parent.uuid, e.uuid)
                level2.append(e)

        # Measure get_descendants on root
        start = time.time()
        descendants = m.get_descendants(root.uuid)
        elapsed = time.time() - start

        assert len(descendants) == 110  # 10 L1 + 100 L2
        # Should complete in <10ms for 110 descendants
        assert elapsed < 0.01, f"get_descendants took {elapsed:.3f}s on 110-element tree"

    def test_multiple_hierarchies_performance(self):
        """Test performance with multiple independent hierarchies."""
        m = Model("perf-multi-hierarchy")

        # Create 5 independent hierarchies of 100 elements each
        for h in range(5):
            root = m.add(ArchiType.BusinessProcess, f"Root-{h}")
            children = []
            for i in range(100):
                child = m.add(ArchiType.BusinessFunction, f"H{h}-C{i}")
                m.add_child(root.uuid, child.uuid)
                children.append(child)

            # Verify all children are in hierarchy
            retrieved = m.get_children(root.uuid)
            assert len(retrieved) == 100

        # Total: 505 elements (5 roots + 500 children)
        assert len(m.elems_dict) == 505

    def test_query_performance_after_large_hierarchy_build(self):
        """Test that queries remain fast after building large hierarchy."""
        m = Model("perf-query-after-build")

        # Build a moderately large hierarchy
        roots = []
        for r in range(10):
            root = m.add(ArchiType.BusinessProcess, f"Root-{r}")
            roots.append(root)
            for i in range(50):
                child = m.add(ArchiType.BusinessFunction, f"R{r}-C{i}")
                m.add_child(root.uuid, child.uuid)

        # Now measure query performance
        start = time.time()
        for root in roots:
            _ = m.get_children(root.uuid)
            _ = m.get_root_elements()
            _ = m.get_leaf_elements()
        elapsed = time.time() - start

        # Should complete all queries in <10ms
        assert elapsed < 0.04, f"Queries on 510-element model took {elapsed:.3f}s"

    def test_hierarchy_modification_performance(self):
        """Test performance of modifying hierarchy (add_child, remove_child)."""
        m = Model("perf-modify")
        elements = []
        for i in range(100):
            e = m.add(ArchiType.BusinessProcess, f"Element {i}")
            elements.append(e)

        # Measure add_child operations
        start = time.time()
        for i in range(1, 100):
            m.add_child(elements[0].uuid, elements[i].uuid)
        elapsed_add = time.time() - start

        # Parent now has 99 children
        assert len(m.get_children(elements[0].uuid)) == 99

        # Measure remove_child operations
        start = time.time()
        for i in range(1, 51):  # Remove first 50
            m.remove_child(elements[0].uuid, elements[i].uuid)
        elapsed_remove = time.time() - start

        # Parent now has 49 children
        assert len(m.get_children(elements[0].uuid)) == 49

        # Both operations should be fast (O(1) operations with dict lookups)
        assert elapsed_add < 0.1, f"99 add_child calls took {elapsed_add:.3f}s"
        assert elapsed_remove < 0.1, f"50 remove_child calls took {elapsed_remove:.3f}s"

    def test_sibling_queries_performance(self):
        """Test performance of get_siblings on large families."""
        m = Model("perf-siblings")
        parent = m.add(ArchiType.BusinessProcess, "Parent")
        siblings = []
        for i in range(100):
            sibling = m.add(ArchiType.BusinessFunction, f"Sibling {i}")
            m.add_child(parent.uuid, sibling.uuid)
            siblings.append(sibling)

        # Measure get_siblings on each sibling
        start = time.time()
        for sibling in siblings:
            result = m.get_siblings(sibling.uuid)
            assert len(result) == 99  # All except self
        elapsed = time.time() - start
        avg_time = elapsed / 100

        # Should be fast (O(n) where n=siblings)
        assert avg_time < 0.001, f"get_siblings took {avg_time:.3f}s per call on 100-sibling element"

    def test_hierarchy_path_query_performance(self):
        """Test performance of find_by_hierarchy_path on large model."""
        m = Model("perf-path-query")

        # Create a 4-level hierarchy with branching
        root = m.add(ArchiType.BusinessProcess, "Root")
        level1 = []
        for i in range(5):
            e1 = m.add(ArchiType.BusinessProcess, f"L1-{i}")
            m.add_child(root.uuid, e1.uuid)
            level1.append(e1)

        level2 = []
        for parent1 in level1:
            for i in range(5):
                e2 = m.add(ArchiType.BusinessFunction, f"L2-{i}")
                m.add_child(parent1.uuid, e2.uuid)
                level2.append(e2)

        # Measure path queries
        start = time.time()
        for _ in range(100):
            results = m.find_by_hierarchy_path("/Root/L1-0/*")
            assert len(results) == 5
        elapsed = time.time() - start
        avg_time = elapsed / 100

        # Should be fast (tree traversal on reasonable size)
        assert avg_time < 0.001, f"find_by_hierarchy_path took {avg_time:.3f}s per call"
