"""Comprehensive round-trip fidelity tests for Phase 4.

Tests verify 100% fidelity when exporting and importing complex models
with hierarchy, visual styles, properties, and viewpoints combined.
"""

import tempfile
from pathlib import Path

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestRoundTripFidelity:
    """T038-T039: Comprehensive round-trip fidelity validation (5+ scenarios)."""

    def test_complete_business_process_hierarchy_roundtrip(self):
        """Test complete business process hierarchy with all properties."""
        m1 = Model("complete-bp-hierarchy")

        # Create multi-level hierarchy with diverse element types
        process = m1.add(ArchiType.BusinessProcess, "Main Process", desc="Top level")
        process.prop("owner", "team-a")
        process.set_fill_color("#e8f4f8")

        function = m1.add(ArchiType.BusinessFunction, "Function 1", desc="Sub function")
        function.prop("priority", "high")
        function.set_line_color("#0066cc")
        function.set_line_width(2.0)

        service = m1.add(ArchiType.BusinessService, "Service A")
        service.set_transparency(0.8)
        service.assign_viewpoint("business")

        # Build hierarchy
        m1.add_child(process.uuid, function.uuid)
        m1.add_child(function.uuid, service.uuid)

        # Export and import
        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("complete-bp-reload")
            m2.read(temp_path)

            # Verify all properties preserved
            proc2 = m2.elems_dict[process.uuid]
            func2 = m2.elems_dict[function.uuid]
            svc2 = m2.elems_dict[service.uuid]

            # Hierarchy
            assert m2.get_parent(func2.uuid) == proc2
            assert m2.get_parent(svc2.uuid) == func2

            # Basic properties
            assert proc2.name == "Main Process"
            assert proc2.desc == "Top level"
            assert proc2.props.get("owner") == "team-a"

            assert func2.props.get("priority") == "high"

            # Visual styles
            assert proc2.get_fill_color() == "#e8f4f8"
            assert func2.get_line_color() == "#0066cc"
            assert func2.get_line_width() == 2.0
            assert svc2.get_transparency() == 0.8

            # Viewpoints
            assert "business" in svc2.viewpoints
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_actor_role_group_hierarchy_roundtrip(self):
        """Test actor-role grouping hierarchy with visual differentiation."""
        m1 = Model("actor-role-groups")

        # Create actor-role hierarchy
        actor = m1.add(ArchiType.BusinessActor, "Executive", desc="C-level")
        actor.set_fill_color("#ff6b6b")
        actor.set_transparency(0.9)

        role1 = m1.add(ArchiType.BusinessRole, "CEO", desc="Chief executive")
        role1.set_fill_color("#ff8787")
        role1.prop("seniority", "5")

        role2 = m1.add(ArchiType.BusinessRole, "CFO", desc="Chief financial")
        role2.set_fill_color("#ff8787")
        role2.prop("seniority", "4")

        # Build hierarchy
        m1.add_child(actor.uuid, role1.uuid)
        m1.add_child(actor.uuid, role2.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("actor-role-reload")
            m2.read(temp_path)

            actor2 = m2.elems_dict[actor.uuid]
            role1_2 = m2.elems_dict[role1.uuid]
            role2_2 = m2.elems_dict[role2.uuid]

            # Verify hierarchy and properties
            children = m2.get_children(actor2.uuid)
            assert len(children) == 2
            child_uuids = {c.uuid for c in children}
            assert role1.uuid in child_uuids
            assert role2.uuid in child_uuids

            # Verify unique properties preserved
            assert role1_2.props.get("seniority") == "5"
            assert role2_2.props.get("seniority") == "4"

            # Visual styles
            assert actor2.get_fill_color() == "#ff6b6b"
            assert role1_2.get_fill_color() == "#ff8787"
            assert role2_2.get_fill_color() == "#ff8787"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_mixed_element_types_with_relationships_roundtrip(self):
        """Test hierarchy with relationships between elements in different groups."""
        m1 = Model("mixed-elements-relations")

        # Create two process groups
        p1 = m1.add(ArchiType.BusinessProcess, "Process 1")
        p1.set_fill_color("#e3f2fd")
        s1 = m1.add(ArchiType.BusinessService, "Service for P1")
        m1.add_child(p1.uuid, s1.uuid)

        p2 = m1.add(ArchiType.BusinessProcess, "Process 2")
        p2.set_fill_color("#f3e5f5")
        s2 = m1.add(ArchiType.BusinessService, "Service for P2")
        m1.add_child(p2.uuid, s2.uuid)

        # Create relationships between groups
        rel = m1.add_relationship(source=p1, target=p2, rel_type=ArchiType.Flow, desc="Process flow")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("mixed-reload")
            m2.read(temp_path)

            p1_2 = m2.elems_dict[p1.uuid]
            p2_2 = m2.elems_dict[p2.uuid]
            s1_2 = m2.elems_dict[s1.uuid]
            s2_2 = m2.elems_dict[s2.uuid]
            rel_2 = m2.rels_dict[rel.uuid]

            # Verify hierarchies
            assert m2.get_parent(s1_2.uuid) == p1_2
            assert m2.get_parent(s2_2.uuid) == p2_2

            # Verify relationships
            assert rel_2.source == p1_2
            assert rel_2.target == p2_2
            assert rel_2.desc == "Process flow"

            # Verify visual styles
            assert p1_2.get_fill_color() == "#e3f2fd"
            assert p2_2.get_fill_color() == "#f3e5f5"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_deep_hierarchy_with_all_visual_properties_roundtrip(self):
        """Test 5-level deep hierarchy with all visual properties applied."""
        m1 = Model("deep-visual-hierarchy")

        elements = []
        colors = ["#ffebee", "#ffcdd2", "#ef9a9a", "#e57373", "#ef5350"]

        for i in range(5):
            e = m1.add(ArchiType.BusinessProcess, f"Level {i}")
            e.set_fill_color(colors[i])
            e.set_line_width(float(i + 1))
            e.set_transparency(1.0 - (i * 0.1))
            elements.append(e)

        # Create chain
        for i in range(len(elements) - 1):
            m1.add_child(elements[i].uuid, elements[i + 1].uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("deep-visual-reload")
            m2.read(temp_path)

            # Verify chain
            for i in range(len(elements)):
                elem2 = m2.elems_dict[elements[i].uuid]
                if i > 0:
                    assert m2.get_parent(elem2.uuid) == m2.elems_dict[elements[i - 1].uuid]

                # Verify all visual properties
                assert elem2.get_fill_color() == colors[i]
                assert elem2.get_line_width() == float(i + 1)
                assert abs(elem2.get_transparency() - (1.0 - (i * 0.1))) < 0.01
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_wide_hierarchy_with_diverse_styling_roundtrip(self):
        """Test wide hierarchy (10+ children) with diverse visual styles."""
        m1 = Model("wide-diverse-styling")

        parent = m1.add(ArchiType.BusinessProcess, "Parent")
        parent.set_fill_color("#fff3e0")

        # Define colors palette
        colors = ["#fff9c4", "#fff59d", "#fff176", "#ffee58", "#ffeb3b"]

        # Create 10 children with varying visual styles
        for i in range(10):
            child = m1.add(ArchiType.BusinessFunction, f"Function {i}")

            # Cycle through colors
            child.set_fill_color(colors[i % len(colors)])

            # Vary line width
            child.set_line_width(float((i % 3) + 1))

            # Alternate transparency
            child.set_transparency(0.7 if i % 2 == 0 else 0.9)

            m1.add_child(parent.uuid, child.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("wide-diverse-reload")
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            children2 = m2.get_children(parent2.uuid)
            assert len(children2) == 10

            # Verify each child's properties (order may vary, so check against original elements)
            children2_uuids = {c.uuid for c in children2}
            expected_colors = {colors[i % len(colors)] for i in range(10)}
            expected_widths = {float((i % 3) + 1) for i in range(10)}

            actual_colors = {m2.elems_dict[uuid].get_fill_color() for uuid in children2_uuids}
            actual_widths = {m2.elems_dict[uuid].get_line_width() for uuid in children2_uuids}
            actual_trans = {m2.elems_dict[uuid].get_transparency() for uuid in children2_uuids}

            assert actual_colors == expected_colors
            assert actual_widths == expected_widths
            # Check transparency with small tolerance
            for trans in actual_trans:
                assert trans in {0.7, 0.9}
        finally:
            Path(temp_path).unlink(missing_ok=True)
