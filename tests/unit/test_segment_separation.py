"""Tests for segment separation enforcement (FR-015, SC-008).

Verify that collinear segments from different connections are separated by
min_segment_gap (default 20px, configurable).
"""

from src.pyArchimate.view.layout.core import RoutingConfig
from src.pyArchimate.view.layout.routing.segment_separation import displace_collinear_segments
from src.pyArchimate.view.layout.utils.geometry import Point


class TestSegmentSeparation20pxDefault:
    """Default min_segment_gap is 20px."""

    def test_routing_config_default_min_segment_gap(self) -> None:
        """Default min_segment_gap is 20.0 (FR-015)."""
        config = RoutingConfig()
        assert config.min_segment_gap == 20.0, "Default min_segment_gap should be 20.0 per FR-015"

    def test_two_collinear_horizontal_segments_separated_20px(self) -> None:
        """Two horizontal overlapping collinear segments are separated by ≥20px.

        Simulates two connections routing through the same corridor.
        The displacement function should offset them by min_segment_gap.
        """
        config = RoutingConfig()

        # Two identical horizontal segments at y=100, x range [0,100]
        # Segment A: (0, 100)→(100, 100) [connection 0]
        # Segment B: (0, 100)→(100, 100) [connection 1] — must be displaced
        waypoints_a = [Point(0, 100), Point(100, 100)]
        waypoints_b = [Point(0, 100), Point(100, 100)]

        result = displace_collinear_segments([waypoints_a, waypoints_b], min_gap=config.min_segment_gap)

        # After displacement, both segments should still be collinear (same x range)
        # but offset in y by min_segment_gap
        seg_a_y = result[0][0].y
        seg_b_y = result[1][0].y
        separation = abs(seg_a_y - seg_b_y)

        assert separation >= config.min_segment_gap, f"Separation {separation}px must be >= {config.min_segment_gap}px"

    def test_two_collinear_vertical_segments_separated_20px(self) -> None:
        """Two vertical overlapping collinear segments are separated by ≥20px."""
        config = RoutingConfig()

        # Two identical vertical segments at x=50, y range [0,100]
        waypoints_a = [Point(50, 0), Point(50, 100)]
        waypoints_b = [Point(50, 0), Point(50, 100)]

        result = displace_collinear_segments([waypoints_a, waypoints_b], min_gap=config.min_segment_gap)

        seg_a_x = result[0][0].x
        seg_b_x = result[1][0].x
        separation = abs(seg_a_x - seg_b_x)

        assert separation >= config.min_segment_gap, f"Separation {separation}px must be >= {config.min_segment_gap}px"


class TestSegmentSeparationCustom5px:
    """Custom min_segment_gap values are honored."""

    def test_custom_5px_gap_accepted(self) -> None:
        """RoutingConfig with min_segment_gap=5 is valid."""
        config = RoutingConfig(min_segment_gap=5.0)
        assert config.min_segment_gap == 5.0

    def test_two_collinear_segments_separated_5px(self) -> None:
        """Two collinear segments separated to ≥5px with custom min_gap=5."""
        waypoints_a = [Point(0, 100), Point(100, 100)]
        waypoints_b = [Point(0, 100), Point(100, 100)]

        result = displace_collinear_segments([waypoints_a, waypoints_b], min_gap=5.0)

        seg_a_y = result[0][0].y
        seg_b_y = result[1][0].y
        separation = abs(seg_a_y - seg_b_y)

        assert separation >= 5.0, f"Separation {separation}px must be >= 5.0px (custom gap)"
