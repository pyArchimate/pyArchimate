"""Grid-inflated obstacle map with corridor BFS and crossing-cost path finding."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any

from ..core import RoutingConfig
from ..utils.geometry import Point, Rectangle

_MAX_CANVAS = 4000  # default canvas bound when no obstacles provided


@dataclass
class ObstacleMap:
    """Rasterized obstacle map for orthogonal connection routing.

    Nodes are inflated by config.node_clearance (default 25px), then rasterized to grid cells.
    BFS with optional crossing-cost finds shortest orthogonal paths.
    """

    _obstacles: list[Rectangle]
    resolution: float = 10.0
    _cells: set[tuple[int, int]] = field(default_factory=set, init=False, repr=False)
    _routed: set[tuple[int, int]] = field(default_factory=set, init=False, repr=False)
    _canvas_w: int = field(default=0, init=False)
    _canvas_h: int = field(default=0, init=False)
    _node_clearance: float = field(default=25.0, init=False)

    def __init__(
        self, obstacles: list[Rectangle], resolution: float = 10.0, config: RoutingConfig | None = None
    ) -> None:
        self._obstacles = obstacles
        self.resolution = resolution
        self._cells: set[tuple[int, int]] = set()
        self._routed: set[tuple[int, int]] = set()
        if config is None:
            config = RoutingConfig()
        self._node_clearance = config.node_clearance
        # Default canvas; will be updated in _build() based on actual obstacle extents
        self._canvas_w = max(10, int(_MAX_CANVAS / max(resolution, 1.0)))
        self._canvas_h = max(10, int(_MAX_CANVAS / max(resolution, 1.0)))
        self._build(obstacles)

    def _to_cell(self, x: float, y: float) -> tuple[int, int]:
        return (int(x / self.resolution), int(y / self.resolution))

    def _build(self, obstacles: list[Rectangle]) -> None:
        res = self.resolution
        clearance = self._node_clearance
        max_cx = max_cy = 0
        for obs in obstacles:
            x0 = obs.x - clearance
            y0 = obs.y - clearance
            x1 = obs.x + obs.width + clearance
            y1 = obs.y + obs.height + clearance
            # Block every cell that physically overlaps the inflated bbox.
            # Cell cx covers [cx*res, (cx+1)*res). It overlaps obstacle if cx*res < x1.
            # Equivalently, max cx is ceil(x1/res) - 1 = int((x1-eps)/res).
            cx0 = int(x0 / res)
            cy0 = int(y0 / res)
            cx1 = int(x1 / res)      # last cell whose left edge is < x1
            cy1 = int(y1 / res)
            for cx in range(cx0, cx1 + 1):
                for cy in range(cy0, cy1 + 1):
                    self._cells.add((cx, cy))
            max_cx = max(max_cx, cx1 + 10)
            max_cy = max(max_cy, cy1 + 10)
        if obstacles:
            self._canvas_w = max(max_cx, _MAX_CANVAS // int(res))
            self._canvas_h = max(max_cy, _MAX_CANVAS // int(res))

    def is_blocked(self, x: float, y: float) -> bool:
        """Return True if the point (x, y) is inside an inflated obstacle cell."""
        return self._to_cell(x, y) in self._cells

    def segment_blocked(self, p1: Point, p2: Point) -> bool:
        """Return True if the axis-aligned segment p1→p2 passes through any blocked cell."""
        res = self.resolution
        if abs(p1.y - p2.y) < 1e-6:
            # horizontal
            y = (p1.y + p2.y) / 2
            x_start = min(p1.x, p2.x)
            x_end = max(p1.x, p2.x)
            x = x_start
            while x <= x_end + res:
                if self._to_cell(x, y) in self._cells:
                    return True
                x += res
        else:
            # vertical
            x = (p1.x + p2.x) / 2
            y_start = min(p1.y, p2.y)
            y_end = max(p1.y, p2.y)
            y = y_start
            while y <= y_end + res:
                if self._to_cell(x, y) in self._cells:
                    return True
                y += res
        return False

    def mark_routed_segment(self, p1: Point, p2: Point) -> None:
        """Mark cells along a routed segment so future paths can account for crossings."""
        res = self.resolution
        if abs(p1.y - p2.y) < 1e-6:
            y = (p1.y + p2.y) / 2
            x = min(p1.x, p2.x)
            x_end = max(p1.x, p2.x)
            while x <= x_end + res:
                self._routed.add(self._to_cell(x, y))
                x += res
        else:
            x = (p1.x + p2.x) / 2
            y = min(p1.y, p2.y)
            y_end = max(p1.y, p2.y)
            while y <= y_end + res:
                self._routed.add(self._to_cell(x, y))
                y += res

    def unmark_routed_segment(self, p1: Point, p2: Point) -> None:
        """Remove cells along a previously routed segment from the routed set.

        Used by multi-pass routing to un-mark a connection's old path before
        re-routing it, so the path no longer acts as a soft obstacle.
        """
        res = self.resolution
        if abs(p1.y - p2.y) < 1e-6:
            y = (p1.y + p2.y) / 2
            x = min(p1.x, p2.x)
            x_end = max(p1.x, p2.x)
            while x <= x_end + res:
                self._routed.discard(self._to_cell(x, y))
                x += res
        else:
            x = (p1.x + p2.x) / 2
            y = min(p1.y, p2.y)
            y_end = max(p1.y, p2.y)
            while y <= y_end + res:
                self._routed.discard(self._to_cell(x, y))
                y += res

    def _expand_neighbour(
        self,
        ncell: tuple[int, int],
        ndir: str,
        cost: float,
        direction: str,
        res: float,
        crossing_penalty: float,
        dist: dict[tuple[tuple[int, int], str], float],
        prev: dict[tuple[tuple[int, int], str], tuple[tuple[int, int], str] | None],
        heap: list[Any],
        cur_state: tuple[tuple[int, int], str],
    ) -> None:
        nx, ny = ncell
        if nx < 0 or ny < 0 or nx > self._canvas_w or ny > self._canvas_h:
            return
        if ncell in self._cells:
            return
        move_cost = res
        if ncell in self._routed:
            move_cost += crossing_penalty * res
        if direction not in ('n', ndir):
            move_cost += res * 0.1
        new_g = cost + move_cost
        nstate = (ncell, ndir)
        inf = float('inf')
        if new_g < dist.get(nstate, inf):
            dist[nstate] = new_g
            prev[nstate] = cur_state
            # A* priority: f = g + Manhattan heuristic
            hx, hy = self._ec
            h = (abs(nx - hx) + abs(ny - hy)) * res
            heapq.heappush(heap, (new_g + h, new_g, ncell, ndir))

    def _init_search(
        self,
        sc: tuple[int, int],
        ec: tuple[int, int],
        res: float,
    ) -> tuple[
        dict[tuple[tuple[int, int], str], float],
        dict[tuple[tuple[int, int], str], tuple[tuple[int, int], str] | None],
        list[Any],
    ]:
        """Initialise A* data structures and push start states onto the heap."""
        dist: dict[tuple[tuple[int, int], str], float] = {}
        prev: dict[tuple[tuple[int, int], str], tuple[tuple[int, int], str] | None] = {}
        heap: list[Any] = []
        hx, hy = ec
        for d in ('h', 'v', 'n'):
            state = (sc, d)
            dist[state] = 0.0
            prev[state] = None
            h0 = (abs(sc[0] - hx) + abs(sc[1] - hy)) * res
            heapq.heappush(heap, (h0, 0.0, sc, d))
        return dist, prev, heap

    def find_corridor(
        self,
        start: Point,
        end: Point,
        crossing_penalty: float = 1.0,
    ) -> list[Point] | None:
        """Find shortest orthogonal path from start to end avoiding blocked cells.

        Uses A* with Manhattan heuristic and optional crossing_penalty.
        Returns None if no path exists or search exceeds the cell budget.
        """
        res = self.resolution
        sc = self._to_cell(start.x, start.y)
        ec = self._to_cell(end.x, end.y)

        if sc == ec:
            return [Point(start.x, start.y)]

        # Budget: allow up to 36× Manhattan distance in visited states.
        # When crossing_penalty > 0, the fallback (penalty=0) guarantees a path is
        # found even if this budget is exceeded. 36× was empirically sufficient for
        # typical diagrams. Dense diagrams that exceed it fall back gracefully.
        # Minimum 500 ensures tiny connections always get enough budget.
        manhattan = abs(sc[0] - ec[0]) + abs(sc[1] - ec[1])
        if crossing_penalty > 0:
            max_visited = max(500, manhattan * 20)
        else:
            max_visited = max(1000, manhattan * 36)

        # A* with direction state to prefer straight segments.
        # Heap entries: (f=g+h, g, cell, direction)
        # dist stores g-values; stale-entry check uses g vs dist[state].
        inf = float('inf')
        self._ec = ec  # store for heuristic access in _expand_neighbour
        dist, prev, heap = self._init_search(sc, ec, res)

        found_state: tuple[tuple[int, int], str] | None = None
        visited = 0

        while heap:
            _f, g, cell, direction = heapq.heappop(heap)
            state = (cell, direction)
            if g > dist.get(state, inf):
                continue
            if cell == ec:
                found_state = state
                break
            visited += 1
            if visited > max_visited:
                break  # give up — connection is likely unroutable

            cx, cy = cell
            neighbours = [
                ((cx + 1, cy), 'h'), ((cx - 1, cy), 'h'),
                ((cx, cy + 1), 'v'), ((cx, cy - 1), 'v'),
            ]
            for ncell, ndir in neighbours:
                self._expand_neighbour(ncell, ndir, g, direction, res, crossing_penalty, dist, prev, heap, state)

        if found_state is None and crossing_penalty > 0:
            # Fallback: retry without penalty to guarantee a path is always found.
            # This means the connection may share a corridor with another, but the
            # displacement pass will separate them afterward.
            return self.find_corridor(start, end, crossing_penalty=0.0)
        if found_state is None:
            return None

        return self._reconstruct_path(found_state, prev, res)

    def _reconstruct_path(
        self,
        found_state: tuple[tuple[int, int], str],
        prev: dict[tuple[tuple[int, int], str], tuple[tuple[int, int], str] | None],
        res: float,
    ) -> list[Point]:
        """Reconstruct waypoint list from A* prev-map and compress collinear runs."""
        cell_path: list[tuple[int, int]] = []
        cur: tuple[tuple[int, int], str] | None = found_state
        while cur is not None:
            cell_path.append(cur[0])
            cur = prev.get(cur)
        cell_path.reverse()
        raw = [Point(c[0] * res, c[1] * res) for c in cell_path]
        return _compress_waypoints(raw)


def _compress_waypoints(pts: list[Point]) -> list[Point]:
    """Collapse collinear sequences to just endpoints."""
    if len(pts) <= 2:
        return pts
    result = [pts[0]]
    for i in range(1, len(pts) - 1):
        prev_p = pts[i - 1]
        cur_p = pts[i]
        nxt_p = pts[i + 1]
        going_h = abs(cur_p.y - prev_p.y) < 1e-6
        next_h = abs(nxt_p.y - cur_p.y) < 1e-6
        if going_h != next_h:
            result.append(cur_p)
    result.append(pts[-1])
    return result
