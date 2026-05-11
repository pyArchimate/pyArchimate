"""Collinear segment detection and displacement for orthogonal connection routing."""

from __future__ import annotations

from ..utils.geometry import Point

_EPSILON = 0.5  # tolerance for coordinate comparison


def _segments_from_waypoints(waypoints: list[Point]) -> list[tuple[Point, Point]]:
    """Return list of (p1, p2) axis-aligned segments from a waypoint list."""
    if len(waypoints) < 2:
        return []
    return [(waypoints[i], waypoints[i + 1]) for i in range(len(waypoints) - 1)]


def _seg_is_horizontal(p1: Point, p2: Point) -> bool:
    return abs(p1.y - p2.y) < _EPSILON


def _seg_is_vertical(p1: Point, p2: Point) -> bool:
    return abs(p1.x - p2.x) < _EPSILON


def _intervals_overlap(a0: float, a1: float, b0: float, b1: float) -> bool:
    """Return True if [min(a0,a1), max(a0,a1)] overlaps [min(b0,b1), max(b0,b1)]."""
    lo_a, hi_a = min(a0, a1), max(a0, a1)
    lo_b, hi_b = min(b0, b1), max(b0, b1)
    return lo_a < hi_b and lo_b < hi_a


def _check_pair(p1a: Point, p2a: Point, p1b: Point, p2b: Point) -> str | None:
    """Return 'h', 'v', or None if segments are collinear-overlapping."""
    if _seg_is_horizontal(p1a, p2a) and _seg_is_horizontal(p1b, p2b):
        if abs(p1a.y - p1b.y) < _EPSILON:
            if _intervals_overlap(p1a.x, p2a.x, p1b.x, p2b.x):
                return 'h'
    elif _seg_is_vertical(p1a, p2a) and _seg_is_vertical(p1b, p2b):
        if abs(p1a.x - p1b.x) < _EPSILON:
            if _intervals_overlap(p1a.y, p2a.y, p1b.y, p2b.y):
                return 'v'
    return None


def detect_collinear_overlaps(
    all_waypoints: list[list[Point]],
) -> list[tuple[int, int, int, int, str]]:
    """Detect pairs of segments from different connections that are collinear and overlapping.

    Args:
        all_waypoints: List of waypoint lists, one per connection.

    Returns:
        List of (conn_i, seg_i, conn_j, seg_j, axis) where axis is 'h' or 'v'.
    """
    overlaps: list[tuple[int, int, int, int, str]] = []

    # Build indexed segment list
    indexed: list[tuple[int, int, Point, Point]] = []
    for ci, wps in enumerate(all_waypoints):
        for si, (p1, p2) in enumerate(_segments_from_waypoints(wps)):
            indexed.append((ci, si, p1, p2))

    n = len(indexed)
    for i in range(n):
        ci, si, p1a, p2a = indexed[i]
        for j in range(i + 1, n):
            cj, sj, p1b, p2b = indexed[j]
            if ci == cj:
                continue  # same connection

            axis = _check_pair(p1a, p2a, p1b, p2b)
            if axis is not None:
                overlaps.append((ci, si, cj, sj, axis))

    return overlaps


def displace_collinear_segments(
    all_waypoints: list[list[Point]],
    min_gap: float,
) -> list[list[Point]]:
    """Displace overlapping collinear segments so they are separated by at least min_gap.

    Modifies waypoints in-place by shifting collinear segment pairs perpendicularly.
    Returns the updated waypoint lists.
    """
    if min_gap <= 0:
        return all_waypoints

    overlaps = detect_collinear_overlaps(all_waypoints)
    if not overlaps:
        return all_waypoints

    # Track per-segment displacement offset
    # Key: (conn_idx, seg_idx), value: perpendicular offset applied
    offsets: dict[tuple[int, int], float] = {}

    for ci, si, cj, sj, _axis in overlaps:
        # Assign offsets: move first +gap/2, second -gap/2
        off_i = offsets.get((ci, si), 0.0)
        off_j = offsets.get((cj, sj), 0.0)
        if abs(off_i - off_j) < min_gap:
            half = min_gap / 2.0
            offsets[(ci, si)] = half
            offsets[(cj, sj)] = -half

    # Apply offsets to waypoints
    result = [list(wps) for wps in all_waypoints]
    for (ci, si), offset in offsets.items():
        if ci >= len(result) or si >= len(result[ci]) - 1:
            continue
        wps = result[ci]
        p1, p2 = wps[si], wps[si + 1]
        if _seg_is_horizontal(p1, p2):
            # Shift perpendicular = shift y
            new_p1 = Point(p1.x, p1.y + offset)
            new_p2 = Point(p2.x, p2.y + offset)
        else:
            # Shift perpendicular = shift x
            new_p1 = Point(p1.x + offset, p1.y)
            new_p2 = Point(p2.x + offset, p2.y)
        result[ci][si] = new_p1
        result[ci][si + 1] = new_p2

    return result
