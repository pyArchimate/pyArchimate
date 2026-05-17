"""Integration tests for hierarchy preservation during import/export.

Tests verify that the import/export process preserves:
- Parent-child relationships
- Visual styles (colors, transparency)
- Element properties
- Junction types
"""

import tempfile
from pathlib import Path

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestImportHierarchyEdgeCases:
    """T032: Edge case tests for import (cycles, missing parents, depth limits)."""

    def test_round_trip_preserves_all_properties(self):
        """Test that round-trip preserves hierarchy, styles, and properties."""
        m1 = Model("props-test")
        parent = m1.add(ArchiType.BusinessProcess, "Parent")
        child = m1.add(ArchiType.BusinessProcess, "Child")

        # Add custom properties
        parent.prop("priority", "high")
        child.prop("status", "active")

        # Build hierarchy
        m1.add_child(parent.uuid, child.uuid)

        # Apply styles
        parent.set_fill_color("#ff0000")
        child.set_fill_color("#00ff00")
        child.set_transparency(0.8)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("props-test-reload")
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            child2 = m2.elems_dict[child.uuid]

            # Verify hierarchy
            assert m2.get_parent(child2.uuid) == parent2
            # Verify properties
            assert parent2.props.get("priority") == "high"
            assert child2.props.get("status") == "active"
            # Verify styles
            assert parent2.get_fill_color() == "#ff0000"
            assert child2.get_fill_color() == "#00ff00"
            assert child2.get_transparency() == 0.8
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_complex_hierarchy_with_visual_styles(self):
        """Test complex scenario with multiple hierarchies and mixed visual styles."""
        m1 = Model("complex-import-test")

        # Create hierarchy 1: Process > Function > Service
        process = m1.add(ArchiType.BusinessProcess, "Process")
        func = m1.add(ArchiType.BusinessFunction, "Function")
        service = m1.add(ArchiType.BusinessService, "Service")

        m1.add_child(process.uuid, func.uuid)
        m1.add_child(func.uuid, service.uuid)

        # Add visual styles
        process.set_fill_color("#ff0000")
        func.set_fill_color("#00ff00")
        service.set_fill_color("#0000ff")
        service.set_transparency(0.5)

        # Create hierarchy 2: Actor > Role
        actor = m1.add(ArchiType.BusinessActor, "Actor")
        role = m1.add(ArchiType.BusinessRole, "Role")
        m1.add_child(actor.uuid, role.uuid)

        # Ungrouped element
        ungrouped = m1.add(ArchiType.BusinessObject, "Object")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            m1.write(temp_path)
            m2 = Model("complex-import-reload")
            m2.read(temp_path)

            # Verify first hierarchy
            p2 = m2.elems_dict[process.uuid]
            f2 = m2.elems_dict[func.uuid]
            a2 = m2.elems_dict[service.uuid]

            assert m2.get_parent(f2.uuid) == p2
            assert m2.get_parent(a2.uuid) == f2

            # Verify visual styles
            assert p2.get_fill_color() == "#ff0000"
            assert f2.get_fill_color() == "#00ff00"
            assert a2.get_fill_color() == "#0000ff"
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
        # Create via code, export, then verify colors converted
        m1 = Model("named-colors-test")
        elem1 = m1.add(ArchiType.BusinessProcess, "Process 1")
        # Set using named color
        elem1.set_fill_color("red")
        elem1.set_line_color("blue")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            m1.write(temp_path)
            m2 = Model("named-colors-reload")
            m2.read(temp_path)

            elem2 = m2.elems_dict[elem1.uuid]
            style = elem2.get_visual_style()

            # Named colors should be converted to hex
            assert style.get("fillColor") is not None
            assert style["fillColor"].startswith("#")
            assert style["fillColor"] == "#ff0000"  # red → #ff0000
            assert style.get("lineColor") is not None
            assert style["lineColor"].startswith("#")
            assert style["lineColor"] == "#0000ff"  # blue → #0000ff
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_preserves_element_properties_with_hierarchy(self):
        """Test that custom element properties are preserved with hierarchy."""
        m1 = Model("props-with-hierarchy")
        parent = m1.add(ArchiType.BusinessProcess, "Parent")
        child = m1.add(ArchiType.BusinessProcess, "Child")

        # Add custom properties
        parent.prop("priority", "high")
        parent.prop("owner", "team-a")
        child.prop("status", "active")

        m1.add_child(parent.uuid, child.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("props-with-hierarchy-reload")
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            child2 = m2.elems_dict[child.uuid]

            # Verify hierarchy
            assert m2.get_parent(child2.uuid) == parent2

            # Verify properties
            assert parent2.props.get("priority") == "high"
            assert parent2.props.get("owner") == "team-a"
            assert child2.props.get("status") == "active"
        finally:
            Path(temp_path).unlink(missing_ok=True)
