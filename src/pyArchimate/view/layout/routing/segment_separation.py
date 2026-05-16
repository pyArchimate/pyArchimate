"""Collinear segment detection and displacement for orthogonal connection routing."""

from __future__ import annotations

from ..utils.geometry import Point

_EPSILON = 0.5  # tolerance for coordinate comparison (only detect truly collinear segments)


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


def _find_overlap_components(
    overlaps: list[tuple[int, int, int, int, str]],
) -> list[list[tuple[int, int]]]:
    """Return connected components of (conn_idx, seg_idx) pairs from overlaps list."""
    from collections import defaultdict

    adjacency: dict[tuple[int, int], set[tuple[int, int]]] = defaultdict(set)
    for ci, si, cj, sj, _axis in overlaps:
        adjacency[(ci, si)].add((cj, sj))
        adjacency[(cj, sj)].add((ci, si))

    visited: set[tuple[int, int]] = set()
    components: list[list[tuple[int, int]]] = []
    for node in adjacency:
        if node in visited:
            continue
        component: list[tuple[int, int]] = []
        queue = [node]
        while queue:
            cur = queue.pop()
            if cur in visited:
                continue
            visited.add(cur)
            component.append(cur)
            queue.extend(adjacency[cur] - visited)
        components.append(component)
    return components


def displace_collinear_segments(
    all_waypoints: list[list[Point]],
    min_gap: float,
) -> list[list[Point]]:
    """Displace overlapping collinear segments so all are separated by at least min_gap.

    Groups segments that share the same corridor (same axis-coordinate and overlapping
    range) into clusters, then spreads the whole cluster evenly around the original
    coordinate. This handles N > 2 concurrent overlapping segments correctly.
    """
    if min_gap <= 0:
        return all_waypoints

    overlaps = detect_collinear_overlaps(all_waypoints)
    if not overlaps:
        return all_waypoints

    components = _find_overlap_components(overlaps)

    # Assign evenly-spread offsets within each component.
    # The component members are sorted deterministically to produce stable output.
    offsets: dict[tuple[int, int], float] = {}
    for component in components:
        n = len(component)
        if n <= 1:
            continue
        # Sort by (conn_idx, seg_idx) for determinism
        members = sorted(component)
        # Spread: member[i] gets offset = (i - (n-1)/2) * min_gap
        for i, key in enumerate(members):
            offsets[key] = (i - (n - 1) / 2.0) * min_gap

    # Apply offsets
    result = [list(wps) for wps in all_waypoints]
    for (ci, si), offset in offsets.items():
        if ci >= len(result) or si >= len(result[ci]) - 1:
            continue
        wps = result[ci]
        p1, p2 = wps[si], wps[si + 1]
        if _seg_is_horizontal(p1, p2):
            new_p1 = Point(p1.x, p1.y + offset)
            new_p2 = Point(p2.x, p2.y + offset)
        else:
            new_p1 = Point(p1.x + offset, p1.y)
            new_p2 = Point(p2.x + offset, p2.y)
        result[ci][si] = new_p1
        result[ci][si + 1] = new_p2

    return result


def _merge_collinear_adjacent(waypoints: list[Point]) -> list[Point]:
    """Remove redundant intermediate waypoints where three consecutive points share the same axis.

    Collapses A→B→C into A→C when AB and BC are on the same axis (same x or same y),
    regardless of direction. Does not alter endpoints. Iterates until stable.
    """
    if len(waypoints) < 3:
        return list(waypoints)
    changed = True
    pts = list(waypoints)
    while changed:
        changed = False
        result: list[Point] = [pts[0]]
        i = 1
        while i < len(pts) - 1:
            prev = result[-1]
            cur = pts[i]
            nxt = pts[i + 1]
            same_horiz = abs(prev.y - cur.y) < _EPSILON and abs(cur.y - nxt.y) < _EPSILON
            same_vert = abs(prev.x - cur.x) < _EPSILON and abs(cur.x - nxt.x) < _EPSILON
            if same_horiz or same_vert:
                changed = True  # skip cur — it's redundant
            else:
                result.append(cur)
            i += 1
        result.append(pts[-1])
        pts = result
    return pts


def remove_uturn_waypoints(waypoints: list[Point]) -> list[Point]:
    """Remove intermediate waypoints that cause U-turns on the same axis.

    A U-turn occurs when three consecutive waypoints are collinear (same x or y)
    but the direction reverses — e.g. going right then left then right again.
    The intermediate point is redundant and the segment can be simplified.
    Iterates until stable (a single pass may expose new U-turns after removal).
    """
    if len(waypoints) < 3:
        return list(waypoints)
    changed = True
    pts = list(waypoints)
    while changed:
        changed = False
        result: list[Point] = [pts[0]]
        for i in range(1, len(pts) - 1):
            prev = result[-1]
            cur = pts[i]
            nxt = pts[i + 1]
            horiz_uturn = (
                abs(prev.y - cur.y) < _EPSILON
                and abs(cur.y - nxt.y) < _EPSILON
                and (cur.x - prev.x) * (nxt.x - cur.x) < 0
            )
            vert_uturn = (
                abs(prev.x - cur.x) < _EPSILON
                and abs(cur.x - nxt.x) < _EPSILON
                and (cur.y - prev.y) * (nxt.y - cur.y) < 0
            )
            if horiz_uturn or vert_uturn:
                changed = True
            else:
                result.append(cur)
        result.append(pts[-1])
        pts = result
    return pts


def _enforce_min_turn_segment(waypoints: list[Point], min_len: float) -> list[Point]:
    """Enforce minimum length for post-turn segments (FR-024, SC-012).

    Extends segments following 90° bends to at least min_len by moving the post-turn
    endpoint. Skips terminal arrival segment (last segment before target attachment).

    A 90° bend is detected when consecutive segments are orthogonal but
    perpendicular: horizontal→vertical or vertical→horizontal.

    Terminal segment = last segment (index len(pts)-2 to len(pts)-1).
    Do NOT extend terminal arrival segment even if it's shorter than min_len.

    Args:
        waypoints: List of waypoints defining the path
        min_len: Minimum allowed segment length (default 40px per FR-024)

    Returns:
        Modified waypoints with post-turn segments extended to >= min_len.
        WARNING: Extended waypoints must not cross node boundaries.
    """
    if len(waypoints) < 3 or min_len <= 0:
        return list(waypoints)

    result = list(waypoints)
    i = 0
    while i < len(result) - 2:
        p1, p2, p3 = result[i], result[i + 1], result[i + 2]

        # Detect 90° bend: segments are perpendicular (h→v or v→h)
        seg_h_then_v = (abs(p1.y - p2.y) < _EPSILON and abs(p2.x - p3.x) < _EPSILON)
        seg_v_then_h = (abs(p1.x - p2.x) < _EPSILON and abs(p2.y - p3.y) < _EPSILON)

        if seg_h_then_v or seg_v_then_h:
            # Skip terminal segment (last segment before target attachment)
            is_terminal = (i + 2 == len(result) - 1)
            if is_terminal:
                i += 1
                continue

            # Measure post-turn segment length (p2→p3)
            curr_len = (
                abs(p3.y - p2.y) if seg_h_then_v else abs(p3.x - p2.x)
            )

            if curr_len < min_len:
                # Extend p3 along post-turn axis to enforce min_len
                # Moving p3 along its own axis (vertical or horizontal) preserves orthogonality
                if seg_h_then_v:
                    # Vertical segment: extend p3.y away from p2
                    if p3.y > p2.y:
                        result[i + 2] = Point(p3.x, p2.y + min_len)
                    else:
                        result[i + 2] = Point(p3.x, p2.y - min_len)
                else:
                    # Horizontal segment: extend p3.x away from p2
                    if p3.x > p2.x:
                        result[i + 2] = Point(p2.x + min_len, p3.y)
                    else:
                        result[i + 2] = Point(p2.x - min_len, p3.y)

        i += 1

    return result
