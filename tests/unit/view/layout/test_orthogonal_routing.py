"""Tests for orthogonal routing utilities."""

from src.pyArchimate.view.layout.routing.orthogonal import (
    apply_barycentric_crossing_reduction,
    count_edge_crossings,
    detect_line_crossings,
    generate_polyline,
    spread_connection_endpoints,
)
from src.pyArchimate.view.layout.utils.geometry import Point


def test_generate_polyline_simple() -> None:
    """Test simple polyline generation."""
    p_start = Point(0, 0)
    p_end = Point(100, 100)

    polyline = generate_polyline(p_start, p_end)

    assert len(polyline) >= 2
    assert polyline[0] == p_start
    assert polyline[-1] == p_end


def test_generate_polyline_horizontal() -> None:
    """Test polyline generation for horizontal line."""
    p_start = Point(0, 50)
    p_end = Point(100, 50)

    polyline = generate_polyline(p_start, p_end)

    assert polyline[0] == p_start
    assert polyline[-1] == p_end


def test_detect_line_crossings_crossing() -> None:
    """Test crossing detection for crossing lines."""
    line1 = (Point(0, 0), Point(100, 100))
    line2 = (Point(0, 100), Point(100, 0))

    # Lines crossing diagonally
    assert detect_line_crossings(line1, line2) is True


def test_detect_line_crossings_parallel() -> None:
    """Test crossing detection for parallel lines."""
    line1 = (Point(0, 0), Point(100, 0))
    line2 = (Point(0, 10), Point(100, 10))

    assert detect_line_crossings(line1, line2) is False


def test_detect_line_crossings_perpendicular() -> None:
    """Test crossing detection for perpendicular lines."""
    line1 = (Point(50, 0), Point(50, 100))
    line2 = (Point(0, 50), Point(100, 50))

    assert detect_line_crossings(line1, line2) is True


def test_count_edge_crossings_no_crossings() -> None:
    """Test edge crossing count with no crossings."""
    edges = [
        (Point(0, 0), Point(100, 0)),
        (Point(0, 20), Point(100, 20)),
    ]

    count = count_edge_crossings(edges)
    assert count == 0


def test_count_edge_crossings_with_crossings() -> None:
    """Test edge crossing count with crossings."""
    edges = [
        (Point(0, 0), Point(100, 100)),
        (Point(0, 100), Point(100, 0)),
    ]

    count = count_edge_crossings(edges)
    assert count == 1


def test_spread_connection_endpoints_single_connection() -> None:
    """Test endpoint spreading with single connection."""
    node_positions = {0: (0, 0), 1: (100, 100)}
    node_sizes = {0: (50, 50), 1: (50, 50)}
    connections = [(0, 1)]

    endpoints = spread_connection_endpoints(node_positions, node_sizes, connections)

    assert (0, 1) in endpoints
    start, end = endpoints[(0, 1)]
    assert isinstance(start, Point)
    assert isinstance(end, Point)


def test_spread_connection_endpoints_multiple() -> None:
    """Test endpoint spreading with multiple connections."""
    node_positions = {0: (50, 50), 1: (150, 50), 2: (250, 50)}
    node_sizes = {0: (40, 40), 1: (40, 40), 2: (40, 40)}
    connections = [(0, 1), (0, 2)]

    endpoints = spread_connection_endpoints(node_positions, node_sizes, connections)

    assert len(endpoints) == 2
    assert (0, 1) in endpoints
    assert (0, 2) in endpoints

    # Both should have endpoints (start and end points)
    start1, _end1 = endpoints[(0, 1)]
    start2, _end2 = endpoints[(0, 2)]

    # Start points should be at different y-positions (different outgoing from node 0)
    assert start1.y != start2.y


def test_apply_barycentric_crossing_reduction() -> None:
    """Test barycentric crossing reduction."""
    node_positions = {
        0: (0, 0),
        1: (100, 0),
        2: (0, 100),
        3: (100, 100),
    }
    connections = [(0, 3), (1, 2)]

    new_positions = apply_barycentric_crossing_reduction(node_positions, connections, iterations=1)

    assert len(new_positions) == 4
    # All positions should still exist
    for node_id in node_positions:
        assert node_id in new_positions


def test_apply_barycentric_preserves_count() -> None:
    """Test that barycentric method preserves node count."""
    node_positions = {i: (i * 50, i * 30) for i in range(10)}
    connections = [(i, (i + 1) % 10) for i in range(10)]

    new_positions = apply_barycentric_crossing_reduction(node_positions, connections, iterations=3)

    assert len(new_positions) == len(node_positions)
