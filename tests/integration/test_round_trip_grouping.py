"""Integration tests for hierarchy and visual style round-trip fidelity.

Tests verify that element hierarchy (parentId) and visual properties
(fillColor, lineColor, lineWidth, transparency) survive export/import cycles
without loss or corruption. Tests cover single/multiple hierarchy levels,
mixed grouping + visual styles, and preservation with viewpoints.
"""

import tempfile
from pathlib import Path

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestRoundTripGrouping:
    """T031: Round-trip tests for element grouping (15+ tests)."""

    def test_single_parent_child_hierarchy_roundtrip(self):
        """Test basic parent-child relationship survives export/import."""
        m1 = Model("grouping-basic")
        parent = m1.add(ArchiType.BusinessProcess, "Parent Process")
        child = m1.add(ArchiType.BusinessProcess, "Child Process")

        m1.add_child(parent.uuid, child.uuid)

        # Export and reimport
        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-basic-reload")
            m2.read(temp_path)

            # Verify hierarchy preserved
            parent2 = m2.elems_dict[parent.uuid]
            child2 = m2.elems_dict[child.uuid]
            assert m2.get_parent(child2.uuid) == parent2
            assert child2 in m2.get_children(parent2.uuid)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_multi_child_hierarchy_roundtrip(self):
        """Test parent with multiple children survives round-trip."""
        m1 = Model("grouping-multi")
        parent = m1.add(ArchiType.BusinessProcess, "Parent")
        child1 = m1.add(ArchiType.BusinessProcess, "Child 1")
        child2 = m1.add(ArchiType.BusinessProcess, "Child 2")
        child3 = m1.add(ArchiType.BusinessProcess, "Child 3")

        m1.add_child(parent.uuid, child1.uuid)
        m1.add_child(parent.uuid, child2.uuid)
        m1.add_child(parent.uuid, child3.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-multi-reload")
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            children2 = m2.get_children(parent2.uuid)
            assert len(children2) == 3
            child_uuids = {c.uuid for c in children2}
            assert child1.uuid in child_uuids
            assert child2.uuid in child_uuids
            assert child3.uuid in child_uuids
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_nested_hierarchy_two_levels_roundtrip(self):
        """Test nested hierarchy (depth=2) survives round-trip."""
        m1 = Model("grouping-nested-2")
        root = m1.add(ArchiType.BusinessProcess, "Root")
        middle = m1.add(ArchiType.BusinessProcess, "Middle")
        leaf = m1.add(ArchiType.BusinessProcess, "Leaf")

        m1.add_child(root.uuid, middle.uuid)
        m1.add_child(middle.uuid, leaf.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-nested-2-reload")
            m2.read(temp_path)

            leaf2 = m2.elems_dict[leaf.uuid]
            middle2 = m2.elems_dict[middle.uuid]
            root2 = m2.elems_dict[root.uuid]

            # Verify parent chain
            assert m2.get_parent(leaf2.uuid) == middle2
            assert m2.get_parent(middle2.uuid) == root2
            assert m2.get_parent(root2.uuid) is None
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_nested_hierarchy_three_levels_roundtrip(self):
        """Test nested hierarchy (depth=3) survives round-trip."""
        m1 = Model("grouping-nested-3")
        level1 = m1.add(ArchiType.BusinessProcess, "Level 1")
        level2 = m1.add(ArchiType.BusinessProcess, "Level 2")
        level3 = m1.add(ArchiType.BusinessProcess, "Level 3")
        level4 = m1.add(ArchiType.BusinessProcess, "Level 4")

        m1.add_child(level1.uuid, level2.uuid)
        m1.add_child(level2.uuid, level3.uuid)
        m1.add_child(level3.uuid, level4.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-nested-3-reload")
            m2.read(temp_path)

            level4_2 = m2.elems_dict[level4.uuid]
            ancestors = m2.get_ancestors(level4_2.uuid)
            # get_ancestors returns [parent, grandparent, ..., root] (excludes element itself)
            assert len(ancestors) == 3
            assert ancestors[0].uuid == level3.uuid
            assert ancestors[1].uuid == level2.uuid
            assert ancestors[2].uuid == level1.uuid
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_mixed_grouped_ungrouped_elements_roundtrip(self):
        """Test model with grouped and ungrouped elements roundtrips correctly."""
        m1 = Model("grouping-mixed")
        root1 = m1.add(ArchiType.BusinessProcess, "Root 1")
        child1 = m1.add(ArchiType.BusinessProcess, "Child 1")
        ungrouped1 = m1.add(ArchiType.BusinessProcess, "Ungrouped 1")
        ungrouped2 = m1.add(ArchiType.BusinessProcess, "Ungrouped 2")

        m1.add_child(root1.uuid, child1.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-mixed-reload")
            m2.read(temp_path)

            root1_2 = m2.elems_dict[root1.uuid]
            child1_2 = m2.elems_dict[child1.uuid]
            ungrouped1_2 = m2.elems_dict[ungrouped1.uuid]
            ungrouped2_2 = m2.elems_dict[ungrouped2.uuid]

            # Verify hierarchy
            assert m2.get_parent(child1_2.uuid) == root1_2
            assert m2.get_parent(ungrouped1_2.uuid) is None
            assert m2.get_parent(ungrouped2_2.uuid) is None
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_grouping_with_visual_styles_roundtrip(self):
        """Test grouping + visual styles preserved together in round-trip."""
        m1 = Model("grouping-visual")
        parent = m1.add(ArchiType.BusinessProcess, "Parent")
        child = m1.add(ArchiType.BusinessProcess, "Child")

        # Set visual styles
        parent.set_fill_color("#ff0000")
        parent.set_line_color("#00ff00")
        parent.set_line_width(2.5)

        child.set_fill_color("#0000ff")
        child.set_transparency(0.5)

        # Create hierarchy
        m1.add_child(parent.uuid, child.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-visual-reload")
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            child2 = m2.elems_dict[child.uuid]

            # Verify hierarchy
            assert m2.get_parent(child2.uuid) == parent2

            # Verify visual styles
            parent_style = parent2.get_visual_style()
            assert parent_style.get("fillColor") == "#ff0000"
            assert parent_style.get("lineColor") == "#00ff00"
            assert parent_style.get("lineWidth") == 2.5

            child_style = child2.get_visual_style()
            assert child_style.get("fillColor") == "#0000ff"
            assert child_style.get("transparency") == 0.5
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_grouping_with_viewpoints_roundtrip(self):
        """Test grouping + viewpoints preserved together in round-trip."""
        m1 = Model("grouping-viewpoint")
        parent = m1.add(ArchiType.BusinessProcess, "Parent")
        child = m1.add(ArchiType.BusinessProcess, "Child")

        # Add viewpoints (using valid viewpoint slugs)
        parent.assign_viewpoint("business")
        child.assign_viewpoint("capability")

        # Create hierarchy
        m1.add_child(parent.uuid, child.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-viewpoint-reload")
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            child2 = m2.elems_dict[child.uuid]

            # Verify hierarchy
            assert m2.get_parent(child2.uuid) == parent2

            # Verify viewpoints
            assert "business" in parent2.viewpoints
            assert "capability" in child2.viewpoints
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_orphaning_on_delete_preserved_roundtrip(self):
        """Test that orphaned children are preserved when parent deleted."""
        m1 = Model("grouping-orphan")
        parent = m1.add(ArchiType.BusinessProcess, "Parent")
        child1 = m1.add(ArchiType.BusinessProcess, "Child 1")
        child2 = m1.add(ArchiType.BusinessProcess, "Child 2")

        m1.add_child(parent.uuid, child1.uuid)
        m1.add_child(parent.uuid, child2.uuid)

        # Delete parent - children should be orphaned
        parent.delete()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-orphan-reload")
            m2.read(temp_path)

            # Verify parent deleted
            assert parent.uuid not in m2.elems_dict

            # Verify children exist and have no parent
            child1_2 = m2.elems_dict[child1.uuid]
            child2_2 = m2.elems_dict[child2.uuid]
            assert m2.get_parent(child1_2.uuid) is None
            assert m2.get_parent(child2_2.uuid) is None
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_named_color_preservation_in_hierarchy_roundtrip(self):
        """Test named colors are converted to hex and preserved in hierarchy."""
        m1 = Model("grouping-named-color")
        parent = m1.add(ArchiType.BusinessProcess, "Parent")
        child = m1.add(ArchiType.BusinessProcess, "Child")

        # Set using named colors
        parent.set_fill_color("red")
        child.set_fill_color("blue")

        m1.add_child(parent.uuid, child.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-named-color-reload")
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            child2 = m2.elems_dict[child.uuid]

            # Hierarchy preserved
            assert m2.get_parent(child2.uuid) == parent2

            # Colors preserved (as hex)
            assert parent2.get_fill_color() is not None
            assert child2.get_fill_color() is not None
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_transparency_preservation_in_hierarchy_roundtrip(self):
        """Test transparency is preserved in grouped elements."""
        m1 = Model("grouping-transparency")
        parent = m1.add(ArchiType.BusinessProcess, "Parent")
        child = m1.add(ArchiType.BusinessProcess, "Child")

        parent.set_transparency(0.7)
        child.set_transparency(0.3)

        m1.add_child(parent.uuid, child.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-transparency-reload")
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            child2 = m2.elems_dict[child.uuid]

            # Hierarchy preserved
            assert m2.get_parent(child2.uuid) == parent2

            # Transparency preserved
            assert parent2.get_transparency() == 0.7
            assert child2.get_transparency() == 0.3
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_wide_hierarchy_roundtrip(self):
        """Test wide hierarchy (parent with many children) roundtrips correctly."""
        m1 = Model("grouping-wide")
        parent = m1.add(ArchiType.BusinessProcess, "Parent")
        children = [m1.add(ArchiType.BusinessProcess, f"Child {i}") for i in range(10)]

        for child in children:
            m1.add_child(parent.uuid, child.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-wide-reload")
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            children2 = m2.get_children(parent2.uuid)
            assert len(children2) == 10
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_deep_hierarchy_roundtrip(self):
        """Test deep hierarchy (depth=5) roundtrips correctly."""
        m1 = Model("grouping-deep")
        elements = [m1.add(ArchiType.BusinessProcess, f"Level {i}") for i in range(5)]

        # Create chain
        for i in range(len(elements) - 1):
            m1.add_child(elements[i].uuid, elements[i + 1].uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-deep-reload")
            m2.read(temp_path)

            # Verify depth: get_ancestors returns [parent, grandparent, ..., root] (excludes element itself)
            leaf2 = m2.elems_dict[elements[-1].uuid]
            ancestors2 = m2.get_ancestors(leaf2.uuid)
            assert len(ancestors2) == 4  # 4 ancestors (5 elements - 1 for self)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_different_element_types_in_hierarchy_roundtrip(self):
        """Test hierarchy with mixed element types (BusinessProcess, BusinessActor, etc.)."""
        m1 = Model("grouping-mixed-types")
        bp = m1.add(ArchiType.BusinessProcess, "Process")
        ba = m1.add(ArchiType.BusinessActor, "Actor")
        bf = m1.add(ArchiType.BusinessFunction, "Function")

        m1.add_child(bp.uuid, ba.uuid)
        m1.add_child(ba.uuid, bf.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name
        try:
            m1.write(temp_path)
            m2 = Model("grouping-mixed-types-reload")
            m2.read(temp_path)

            bp2 = m2.elems_dict[bp.uuid]
            ba2 = m2.elems_dict[ba.uuid]
            bf2 = m2.elems_dict[bf.uuid]

            assert m2.get_parent(ba2.uuid) == bp2
            assert m2.get_parent(bf2.uuid) == ba2
        finally:
            Path(temp_path).unlink(missing_ok=True)
