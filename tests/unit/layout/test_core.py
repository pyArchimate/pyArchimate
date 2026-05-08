"""Tests for layout core module (LayoutConfig, LayoutResult)."""

import pytest

from src.pyArchimate.view.layout.core import LayoutAlgorithm, LayoutConfig, LayoutResult


def test_layout_config_defaults() -> None:
    """Test LayoutConfig default values."""
    config = LayoutConfig()
    assert config.algorithm == "force_directed"
    assert config.spacing == 50.0
    assert config.margin == 20.0
    assert config.alignment == "free"
    assert config.excluded_element_ids == []
    assert config.routing_style == "orthogonal"


def test_layout_config_custom_values() -> None:
    """Test LayoutConfig with custom values."""
    config = LayoutConfig(
        algorithm="hierarchical",
        spacing=100.0,
        margin=30.0,
        alignment="grid",
        excluded_element_ids=["elem1", "elem2"],
    )
    assert config.algorithm == "hierarchical"
    assert config.spacing == 100.0
    assert config.margin == 30.0
    assert config.alignment == "grid"
    assert config.excluded_element_ids == ["elem1", "elem2"]


def test_layout_config_validation_spacing() -> None:
    """Test LayoutConfig spacing validation."""
    with pytest.raises(ValueError, match="spacing must be positive"):
        LayoutConfig(spacing=0)

    with pytest.raises(ValueError, match="spacing must be positive"):
        LayoutConfig(spacing=-10)


def test_layout_config_validation_margin() -> None:
    """Test LayoutConfig margin validation."""
    with pytest.raises(ValueError, match="margin must be non-negative"):
        LayoutConfig(margin=-1)


def test_layout_config_validation_algorithm() -> None:
    """Test LayoutConfig algorithm validation."""
    with pytest.raises(ValueError, match="Unknown algorithm"):
        LayoutConfig(algorithm="unknown_algo")


def test_layout_config_validation_alignment() -> None:
    """Test LayoutConfig alignment validation."""
    with pytest.raises(ValueError, match="Invalid alignment"):
        LayoutConfig(alignment="invalid")


def test_layout_config_validation_routing_style() -> None:
    """Test LayoutConfig routing_style validation."""
    with pytest.raises(ValueError, match="Invalid routing_style"):
        LayoutConfig(routing_style="invalid_style")


def test_layout_result_success() -> None:
    """Test LayoutResult for successful layout."""
    result = LayoutResult(
        success=True,
        view_id="view1",
        algorithm_used="force_directed",
        elements_processed=50,
        connections_processed=30,
        layout_time_ms=1500.0,
    )
    assert result.success is True
    assert result.view_id == "view1"
    assert result.elements_processed == 50
    assert result.connections_processed == 30


def test_layout_result_failure() -> None:
    """Test LayoutResult for failed layout."""
    result = LayoutResult(
        success=False,
        view_id="view1",
        algorithm_used="force_directed",
        elements_processed=0,
        connections_processed=0,
        layout_time_ms=100.0,
        error_message="Layout failed: timeout",
    )
    assert result.success is False
    assert result.error_message == "Layout failed: timeout"


def test_layout_algorithm_abstract() -> None:
    """Test that LayoutAlgorithm is abstract."""
    with pytest.raises(TypeError):
        LayoutAlgorithm()  # type: ignore
