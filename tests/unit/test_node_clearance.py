"""Tests for FR-013: Node clearance zone (25px default)."""

from src.pyArchimate.view.layout.core import RoutingConfig
from src.pyArchimate.view.layout.routing.obstacle_map import ObstacleMap
from src.pyArchimate.view.layout.utils.geometry import Point, Rectangle


class TestNodeClearance25px:
    """Verify obstacle inflation with 25px clearance."""

    def test_node_edge_grazing_blocked(self):
        """Segment grazing node edge (0px gap) blocked."""
        # Node at (100, 100) size 120×55
        obstacles = [Rectangle(x=100, y=100, width=120, height=55)]
        config = RoutingConfig(node_clearance=25)
        om = ObstacleMap(obstacles=obstacles, resolution=10.0, config=config)

        # Segment 0px from right edge (x=220 + 0) should be blocked
        assert om.segment_blocked(Point(220, 127), Point(220, 150))

    def test_node_24px_gap_blocked(self):
        """Segment at 24px from node side still blocked."""
        obstacles = [Rectangle(x=100, y=100, width=120, height=55)]
        config = RoutingConfig(node_clearance=25)
        om = ObstacleMap(obstacles=obstacles, resolution=10.0, config=config)

        # Segment at x=220+24=244 should be blocked (within 25px)
        assert om.segment_blocked(Point(244, 127), Point(244, 150))

    def test_node_30px_gap_passes(self):
        """Segment at 30px from node side passes (grid-aligned)."""
        obstacles = [Rectangle(x=100, y=100, width=120, height=55)]
        config = RoutingConfig(node_clearance=25)
        om = ObstacleMap(obstacles=obstacles, resolution=10.0, config=config)

        # Node right edge is at 220. With 25px clearance, inflated edge is 245.
        # With 10px resolution, the cell boundary rounds up to 250 (cell 25 boundary).
        # Segment at x=250 (30px from edge) is in cell 25, which is not blocked.
        assert not om.segment_blocked(Point(250, 127), Point(250, 150))


class TestNodeClearanceNonDefault:
    """Verify non-default clearance values."""

    def test_clearance_10px_custom(self):
        """RoutingConfig(node_clearance=10) produces 10px inflation, not 25px."""
        obstacles = [Rectangle(x=100, y=100, width=120, height=55)]
        config = RoutingConfig(node_clearance=10)
        om = ObstacleMap(obstacles=obstacles, resolution=10.0, config=config)

        # Node right edge at 220. With 10px clearance, inflated edge is 230.
        # Cells up to cell 23 (covering [230, 240)) are blocked due to int truncation.
        # Segment at x=220 (0px from edge) is in cell 22, blocked.
        assert om.segment_blocked(Point(220, 127), Point(220, 150))

        # Segment at x=240 (20px from edge) is in cell 24, not blocked.
        assert not om.segment_blocked(Point(240, 127), Point(240, 150))
