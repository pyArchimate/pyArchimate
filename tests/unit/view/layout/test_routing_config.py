"""Tests for RoutingConfig dataclass."""

import pytest

from src.pyArchimate.view.layout.core import RoutingConfig


class TestRoutingConfigDefaults:
    def test_defaults(self) -> None:
        config = RoutingConfig()
        assert config.node_clearance == 25  # FR-013
        assert config.min_segment_gap == 20.0  # FR-015 updated
        assert config.min_turn_segment == 40  # FR-024
        assert config.corner_clearance_pct == 0.10
        assert config.corner_clearance_min == 4.0
        assert config.crossing_penalty == 3.0


class TestRoutingConfigValidation:
    def test_rejects_negative_min_segment_gap(self) -> None:
        with pytest.raises(ValueError, match="min_segment_gap"):
            RoutingConfig(min_segment_gap=-1.0)

    def test_zero_min_segment_gap_accepted(self) -> None:
        config = RoutingConfig(min_segment_gap=0.0)
        assert config.min_segment_gap == 0.0

    def test_rejects_corner_clearance_pct_above_half(self) -> None:
        with pytest.raises(ValueError, match="corner_clearance_pct"):
            RoutingConfig(corner_clearance_pct=0.51)

    def test_rejects_corner_clearance_pct_zero(self) -> None:
        with pytest.raises(ValueError, match="corner_clearance_pct"):
            RoutingConfig(corner_clearance_pct=0.0)

    def test_rejects_corner_clearance_pct_negative(self) -> None:
        with pytest.raises(ValueError, match="corner_clearance_pct"):
            RoutingConfig(corner_clearance_pct=-0.1)

    def test_rejects_negative_corner_clearance_min(self) -> None:
        with pytest.raises(ValueError, match="corner_clearance_min"):
            RoutingConfig(corner_clearance_min=-1.0)

    def test_zero_corner_clearance_min_accepted(self) -> None:
        config = RoutingConfig(corner_clearance_min=0.0)
        assert config.corner_clearance_min == 0.0

    def test_rejects_negative_crossing_penalty(self) -> None:
        with pytest.raises(ValueError, match="crossing_penalty"):
            RoutingConfig(crossing_penalty=-0.1)

    def test_zero_crossing_penalty_accepted(self) -> None:
        config = RoutingConfig(crossing_penalty=0.0)
        assert config.crossing_penalty == 0.0

    def test_max_corner_clearance_pct_accepted(self) -> None:
        config = RoutingConfig(corner_clearance_pct=0.50)
        assert config.corner_clearance_pct == 0.50
