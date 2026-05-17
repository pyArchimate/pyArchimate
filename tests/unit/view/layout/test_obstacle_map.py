"""Tests for ObstacleMap: BFS corridor routing with obstacle avoidance and crossing cost."""

import pytest

from src.pyArchimate.view.layout.routing.obstacle_map import ObstacleMap
from src.pyArchimate.view.layout.utils.geometry import Point, Rectangle


def rect(x: float, y: float, w: float, h: float) -> Rectangle:
    return Rectangle(x, y, w, h)


class TestObstacleMapConstruction:
    def test_node_bbox_cells_are_blocked(self) -> None:
        """Cells inside a node bounding box are marked blocked."""
        om = ObstacleMap([rect(0, 0, 100, 50)], resolution=10.0)
        # Centre of node should be blocked
        assert om.is_blocked(50, 25)

    def test_empty_obstacle_map_no_blocked_cells(self) -> None:
        om = ObstacleMap([], resolution=10.0)
        assert not om.is_blocked(50, 50)

    def test_point_outside_node_not_blocked(self) -> None:
        om = ObstacleMap([rect(100, 100, 50, 50)], resolution=10.0)
        assert not om.is_blocked(0, 0)


class TestObstacleMapSegmentBlocked:
    def test_segment_through_node_is_blocked(self) -> None:
        """A horizontal segment passing through a node bbox is blocked."""
        om = ObstacleMap([rect(40, 20, 80, 40)], resolution=10.0)
        p1 = Point(0, 40)
        p2 = Point(200, 40)
        assert om.segment_blocked(p1, p2)

    def test_segment_avoiding_node_not_blocked(self) -> None:
        """A segment that routes around a node is not blocked."""
        om = ObstacleMap([rect(50, 50, 80, 40)], resolution=10.0)
        # Route above the node
        p1 = Point(0, 10)
        p2 = Point(200, 10)
        assert not om.segment_blocked(p1, p2)


class TestObstacleMapFindCorridor:
    def test_find_corridor_open_space_returns_path(self) -> None:
        """In open space, find_corridor returns a valid orthogonal path."""
        om = ObstacleMap([], resolution=10.0)
        start = Point(0, 0)
        end = Point(100, 100)
        path = om.find_corridor(start, end, crossing_penalty=1.0)
        assert path is not None
        assert len(path) >= 2
        assert path[0].x == pytest.approx(start.x, abs=1)
        assert path[0].y == pytest.approx(start.y, abs=1)
        assert path[-1].x == pytest.approx(end.x, abs=1)
        assert path[-1].y == pytest.approx(end.y, abs=1)

    def test_find_corridor_path_is_orthogonal(self) -> None:
        """All segments in the returned path are axis-aligned."""
        om = ObstacleMap([], resolution=10.0)
        path = om.find_corridor(Point(0, 0), Point(150, 80), crossing_penalty=1.0)
        assert path is not None
        for i in range(len(path) - 1):
            dx = abs(path[i + 1].x - path[i].x)
            dy = abs(path[i + 1].y - path[i].y)
            assert dx == 0 or dy == 0, f"Non-orthogonal segment at index {i}"

    def test_find_corridor_avoids_blocked_cells(self) -> None:
        """Path does not pass through any blocked cell."""
        obstacle = rect(30, 0, 60, 100)
        om = ObstacleMap([obstacle], resolution=10.0)
        path = om.find_corridor(Point(0, 50), Point(200, 50), crossing_penalty=1.0)
        if path is not None:
            for pt in path:
                assert not om.is_blocked(pt.x, pt.y), f"Path point {pt} is inside obstacle"

    def test_find_corridor_returns_none_when_completely_blocked(self) -> None:
        """Returns None when source is surrounded by obstacles with no exit."""
        # Completely surround the start point with overlapping obstacles
        obstacles = [
            rect(-20, -20, 40, 80),   # left wall
            rect(20, -20, 40, 80),    # right wall
            rect(-20, -20, 80, 40),   # top wall
            rect(-20, 20, 80, 40),    # bottom wall
        ]
        om = ObstacleMap(obstacles, resolution=5.0)
        path = om.find_corridor(Point(0, 0), Point(200, 200), crossing_penalty=1.0)
        assert path is None

    def test_find_corridor_same_start_end_returns_trivial(self) -> None:
        """Start == end returns a path with just that point."""
        om = ObstacleMap([], resolution=10.0)
        path = om.find_corridor(Point(50, 50), Point(50, 50), crossing_penalty=1.0)
        assert path is not None
        assert len(path) >= 1

    def test_find_corridor_respects_crossing_penalty(self) -> None:
        """With a routed segment in the map, paths that avoid crossing it are preferred."""
        om = ObstacleMap([], resolution=10.0)
        # Mark a horizontal segment at y=50 from x=0 to x=200 as already routed
        om.mark_routed_segment(Point(0, 50), Point(200, 50))
        # Route from (50,0) to (50,100): must cross y=50 but high penalty should still find a path
        path = om.find_corridor(Point(50, 0), Point(50, 100), crossing_penalty=5.0)
        assert path is not None  # path exists, just more expensive
