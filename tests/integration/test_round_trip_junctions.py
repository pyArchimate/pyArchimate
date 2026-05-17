"""Integration tests for junction type round-trip (export/import) functionality.

Tests verify that junction types are preserved during XML export/import cycles.
"""

import tempfile
from pathlib import Path

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestRoundTripJunctions:
    """T046-T047: Round-trip junction type preservation."""

    def test_single_junction_type_and_roundtrip(self):
        """Test AND junction type preservation on round-trip."""
        m1 = Model("test-and-junction")
        junction = m1.add(ArchiType.Junction, "AND Junction")
        junction.set_junction_type("and")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("test-and-reload")
            m2.read(temp_path)

            junction2 = m2.elems_dict[junction.uuid]
            assert junction2.get_junction_type() == "and"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_single_junction_type_or_roundtrip(self):
        """Test OR junction type preservation on round-trip."""
        m1 = Model("test-or-junction")
        junction = m1.add(ArchiType.Junction, "OR Junction")
        junction.set_junction_type("or")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("test-or-reload")
            m2.read(temp_path)

            junction2 = m2.elems_dict[junction.uuid]
            assert junction2.get_junction_type() == "or"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_single_junction_type_xor_roundtrip(self):
        """Test XOR junction type preservation on round-trip."""
        m1 = Model("test-xor-junction")
        junction = m1.add(ArchiType.Junction, "XOR Junction")
        junction.set_junction_type("xor")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("test-xor-reload")
            m2.read(temp_path)

            junction2 = m2.elems_dict[junction.uuid]
            assert junction2.get_junction_type() == "xor"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_multiple_junctions_different_types_roundtrip(self):
        """Test multiple junctions with different types."""
        m1 = Model("test-multi-junctions")
        and_j = m1.add(ArchiType.Junction, "AND")
        or_j = m1.add(ArchiType.Junction, "OR")
        xor_j = m1.add(ArchiType.Junction, "XOR")

        and_j.set_junction_type("and")
        or_j.set_junction_type("or")
        xor_j.set_junction_type("xor")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("test-multi-reload")
            m2.read(temp_path)

            and_j2 = m2.elems_dict[and_j.uuid]
            or_j2 = m2.elems_dict[or_j.uuid]
            xor_j2 = m2.elems_dict[xor_j.uuid]

            assert and_j2.get_junction_type() == "and"
            assert or_j2.get_junction_type() == "or"
            assert xor_j2.get_junction_type() == "xor"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_junction_with_properties_roundtrip(self):
        """Test junction with both junction type and custom properties."""
        m1 = Model("test-junction-props")
        junction = m1.add(ArchiType.Junction, "Junction with Props")
        junction.set_junction_type("and")
        junction.prop("condition", "all-must-pass")
        junction.prop("timeout", "5000")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("test-junction-props-reload")
            m2.read(temp_path)

            junction2 = m2.elems_dict[junction.uuid]
            assert junction2.get_junction_type() == "and"
            assert junction2.props.get("condition") == "all-must-pass"
            assert junction2.props.get("timeout") == "5000"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_junction_with_visual_style_roundtrip(self):
        """Test junction with both junction type and visual styles."""
        m1 = Model("test-junction-visual")
        junction = m1.add(ArchiType.Junction, "Styled Junction")
        junction.set_junction_type("or")
        junction.set_fill_color("#ff6b6b")
        junction.set_line_color("#cc0000")
        junction.set_line_width(2.0)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("test-junction-visual-reload")
            m2.read(temp_path)

            junction2 = m2.elems_dict[junction.uuid]
            assert junction2.get_junction_type() == "or"
            assert junction2.get_fill_color() == "#ff6b6b"
            assert junction2.get_line_color() == "#cc0000"
            assert junction2.get_line_width() == 2.0
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_junction_in_hierarchy_roundtrip(self):
        """Test junction type preservation with element hierarchy."""
        m1 = Model("test-junction-hierarchy")
        parent = m1.add(ArchiType.BusinessProcess, "Parent Process")
        junction = m1.add(ArchiType.Junction, "Decision Point")
        child = m1.add(ArchiType.BusinessProcess, "Child Process")

        junction.set_junction_type("xor")
        m1.add_child(parent.uuid, junction.uuid)
        m1.add_child(junction.uuid, child.uuid)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("test-junction-hierarchy-reload")
            m2.read(temp_path)

            parent2 = m2.elems_dict[parent.uuid]
            junction2 = m2.elems_dict[junction.uuid]
            child2 = m2.elems_dict[child.uuid]

            # Verify hierarchy
            assert m2.get_parent(junction2.uuid) == parent2
            assert m2.get_parent(child2.uuid) == junction2

            # Verify junction type
            assert junction2.get_junction_type() == "xor"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_junction_without_type_roundtrip(self):
        """Test that junction without explicit type remains unset on round-trip."""
        m1 = Model("test-untyped-junction")
        junction = m1.add(ArchiType.Junction, "Untyped Junction")
        # Don't set junction type

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("test-untyped-reload")
            m2.read(temp_path)

            junction2 = m2.elems_dict[junction.uuid]
            assert junction2.get_junction_type() is None
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_junction_type_with_relationships_roundtrip(self):
        """Test junction type with incoming and outgoing relationships."""
        m1 = Model("test-junction-rels")
        process1 = m1.add(ArchiType.BusinessProcess, "Process 1")
        junction = m1.add(ArchiType.Junction, "Decision")
        process2 = m1.add(ArchiType.BusinessProcess, "Process 2")

        junction.set_junction_type("and")

        # Create relationships
        rel1 = m1.add_relationship(source=process1, target=junction, rel_type=ArchiType.Flow, desc="Decision point")
        rel2 = m1.add_relationship(source=junction, target=process2, rel_type=ArchiType.Flow, desc="Both paths taken")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".archimate", delete=False) as f:
            temp_path = f.name

        try:
            m1.write(temp_path)
            m2 = Model("test-junction-rels-reload")
            m2.read(temp_path)

            junction2 = m2.elems_dict[junction.uuid]
            rel1_2 = m2.rels_dict[rel1.uuid]
            rel2_2 = m2.rels_dict[rel2.uuid]

            # Verify junction type
            assert junction2.get_junction_type() == "and"

            # Verify relationships
            assert rel1_2.target == junction2
            assert rel2_2.source == junction2
        finally:
            Path(temp_path).unlink(missing_ok=True)
