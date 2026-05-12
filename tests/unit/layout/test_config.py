"""Unit tests for LayoutConfig customization options."""

import pytest

from src.pyArchimate.view.layout.core import LayoutConfig


class TestLayoutConfigValidation:
    """Test LayoutConfig validation."""

    def test_default_config(self):
        """Test creating default LayoutConfig."""
        config = LayoutConfig()
        assert config.algorithm == "force_directed"
        assert config.spacing == 50.0
        assert config.margin == 20.0
        assert config.alignment == "free"  # Default is "free" (changed from "grid")
        assert config.routing_style == "orthogonal"
        assert config.layer_priority == "mandatory"
        assert config.grid_size == 240.0
        assert config.excluded_element_ids == []
        assert config.node_size_constraints == {}

    def test_custom_spacing(self):
        """Test custom spacing parameter."""
        config = LayoutConfig(spacing=100.0)
        assert config.spacing == 100.0

    def test_invalid_spacing_zero(self):
        """Test spacing validation (must be positive)."""
        with pytest.raises(ValueError, match="spacing must be positive"):
            LayoutConfig(spacing=0)

    def test_invalid_spacing_negative(self):
        """Test spacing validation (must be positive)."""
        with pytest.raises(ValueError, match="spacing must be positive"):
            LayoutConfig(spacing=-10)

    def test_invalid_spacing_too_large(self):
        """Test spacing validation (should not exceed 500)."""
        with pytest.raises(ValueError, match="spacing should not exceed 500"):
            LayoutConfig(spacing=600)

    def test_custom_margin(self):
        """Test custom margin parameter."""
        config = LayoutConfig(margin=50.0)
        assert config.margin == 50.0

    def test_invalid_margin_negative(self):
        """Test margin validation (must be non-negative)."""
        with pytest.raises(ValueError, match="margin must be non-negative"):
            LayoutConfig(margin=-5)

    def test_invalid_margin_too_large(self):
        """Test margin validation (should not exceed 500)."""
        with pytest.raises(ValueError, match="margin should not exceed 500"):
            LayoutConfig(margin=600)

    def test_algorithm_force_directed(self):
        """Test force_directed algorithm option."""
        config = LayoutConfig(algorithm="force_directed")
        assert config.algorithm == "force_directed"

    def test_algorithm_hierarchical(self):
        """Test hierarchical algorithm option."""
        config = LayoutConfig(algorithm="hierarchical")
        assert config.algorithm == "hierarchical"

    def test_invalid_algorithm(self):
        """Test invalid algorithm."""
        with pytest.raises(ValueError, match="Unknown algorithm"):
            LayoutConfig(algorithm="invalid_algo")

    def test_alignment_free(self):
        """Test free alignment option."""
        config = LayoutConfig(alignment="free")
        assert config.alignment == "free"

    def test_alignment_grid(self):
        """Test grid alignment option."""
        config = LayoutConfig(alignment="grid")
        assert config.alignment == "grid"

    def test_invalid_alignment(self):
        """Test invalid alignment."""
        with pytest.raises(ValueError, match="Invalid alignment"):
            LayoutConfig(alignment="invalid")

    def test_grid_size_validation_free_alignment(self):
        """Test grid_size is not validated for free alignment."""
        config = LayoutConfig(alignment="free", grid_size=0)
        assert config.grid_size == 0

    def test_grid_size_validation_grid_alignment(self):
        """Test grid_size validation for grid alignment."""
        with pytest.raises(ValueError, match="grid_size must be positive"):
            LayoutConfig(alignment="grid", grid_size=0)

    def test_grid_size_large_accepted(self):
        """Large grid_size values (e.g. 150) are now valid — no upper bound enforced."""
        config = LayoutConfig(alignment="grid", grid_size=150)
        assert config.grid_size == 150

    def test_routing_style_orthogonal(self):
        """Test orthogonal routing style."""
        config = LayoutConfig(routing_style="orthogonal")
        assert config.routing_style == "orthogonal"

    def test_routing_style_mixed_45(self):
        """Test mixed_45 routing style."""
        config = LayoutConfig(routing_style="mixed_45")
        assert config.routing_style == "mixed_45"

    def test_invalid_routing_style(self):
        """Test invalid routing style."""
        with pytest.raises(ValueError, match="Invalid routing_style"):
            LayoutConfig(routing_style="diagonal")

    def test_layer_priority_mandatory(self):
        """Test mandatory layer priority."""
        config = LayoutConfig(layer_priority="mandatory")
        assert config.layer_priority == "mandatory"

    def test_layer_priority_soft(self):
        """Test soft layer priority."""
        config = LayoutConfig(layer_priority="soft")
        assert config.layer_priority == "soft"

    def test_invalid_layer_priority(self):
        """Test invalid layer priority."""
        with pytest.raises(ValueError, match="Invalid layer_priority"):
            LayoutConfig(layer_priority="hard")

    def test_excluded_element_ids(self):
        """Test excluded element IDs."""
        excluded = [1, 2, 3]
        config = LayoutConfig(excluded_element_ids=excluded)
        assert config.excluded_element_ids == excluded

    def test_invalid_excluded_element_ids(self):
        """Test invalid excluded_element_ids type."""
        with pytest.raises(ValueError, match="excluded_element_ids must be a list"):
            LayoutConfig(excluded_element_ids="not_a_list")

    def test_node_size_constraints_min_width(self):
        """Test node size constraints with min_width."""
        constraints = {"min_width": 100}
        config = LayoutConfig(node_size_constraints=constraints)
        assert config.node_size_constraints == constraints

    def test_node_size_constraints_max_height(self):
        """Test node size constraints with max_height."""
        constraints = {"max_height": 200}
        config = LayoutConfig(node_size_constraints=constraints)
        assert config.node_size_constraints == constraints

    def test_node_size_constraints_all_options(self):
        """Test node size constraints with all options."""
        constraints = {
            "min_width": 50,
            "max_width": 300,
            "min_height": 40,
            "max_height": 250,
        }
        config = LayoutConfig(node_size_constraints=constraints)
        assert config.node_size_constraints == constraints

    def test_invalid_node_size_constraints_key(self):
        """Test invalid node size constraints key."""
        with pytest.raises(ValueError, match="Invalid node_size_constraints keys"):
            LayoutConfig(node_size_constraints={"invalid_key": 100})

    def test_invalid_node_size_constraints_negative_values(self):
        """Test node size constraints with negative values."""
        with pytest.raises(ValueError, match="node_size_constraints values must be non-negative"):
            LayoutConfig(node_size_constraints={"min_width": -100})

    def test_invalid_node_size_constraints_min_max_order(self):
        """Test node size constraints with min > max."""
        with pytest.raises(ValueError, match="node_size_constraints min cannot exceed max"):
            LayoutConfig(node_size_constraints={"min_width": 300, "max_width": 100})

    def test_complete_custom_config(self):
        """Test creating a fully customized LayoutConfig."""
        config = LayoutConfig(
            algorithm="hierarchical",
            spacing=80,
            margin=30,
            alignment="grid",
            grid_size=20,
            routing_style="mixed_45",
            layer_priority="soft",
            excluded_element_ids=[1, 2],
            node_size_constraints={
                "min_width": 80,
                "max_width": 200,
                "min_height": 60,
                "max_height": 150,
            },
        )
        assert config.algorithm == "hierarchical"
        assert config.spacing == 80
        assert config.margin == 30
        assert config.alignment == "grid"
        assert config.grid_size == 20
        assert config.routing_style == "mixed_45"
        assert config.layer_priority == "soft"
        assert config.excluded_element_ids == [1, 2]
        assert config.node_size_constraints["min_width"] == 80
