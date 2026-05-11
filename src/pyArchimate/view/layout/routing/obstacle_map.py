"""Grid-inflated obstacle map with corridor BFS and crossing-cost path finding."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..utils.geometry import Point, Rectangle

_INFLATE = 2.0  # px clearance around each node bbox
_MAX_CANVAS = 4000  # default canvas bound when no obstacles provided


@dataclass
class ObstacleMap:
    """Rasterized obstacle map for orthogonal connection routing.

    Nodes are inflated by a small margin, then rasterized to grid cells.
    BFS with optional crossing-cost finds shortest orthogonal paths.
    """

    _obstacles: list[Rectangle]
    resolution: float = 10.0
    _cells: set[tuple[int, int]] = field(default_factory=set, init=False, repr=False)
    _routed: set[tuple[int, int]] = field(default_factory=set, init=False, repr=False)
    _canvas_w: int = field(default=0, init=False)
    _canvas_h: int = field(default=0, init=False)

    def __init__(self, obstacles: list[Rectangle], resolution: float = 10.0) -> None:
        self._obstacles = obstacles
        self.resolution = resolution
        self._cells: set[tuple[int, int]] = set()
        self._routed: set[tuple[int, int]] = set()
        self._canvas_w = int(_MAX_CANVAS / resolution) + 10
        self._canvas_h = int(_MAX_CANVAS / resolution) + 10
        self._build(obstacles)

    def _to_cell(self, x: float, y: float) -> tuple[int, int]:
        return (int(x / self.resolution), int(y / self.resolution))

    def _build(self, obstacles: list[Rectangle]) -> None:
        res = self.resolution
        max_cx = max_cy = 0
        for obs in obstacles:
            x0 = obs.x - _INFLATE
            y0 = obs.y - _INFLATE
            x1 = obs.x + obs.width + _INFLATE
            y1 = obs.y + obs.height + _INFLATE
            cx0 = int(x0 / res)
            cy0 = int(y0 / res)
            cx1 = int(x1 / res) + 1
            cy1 = int(y1 / res) + 1
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
        heap: list[tuple[float, tuple[int, int], str]],
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
        new_cost = cost + move_cost
        nstate = (ncell, ndir)
        inf = float('inf')
        if new_cost < dist.get(nstate, inf):
            dist[nstate] = new_cost
            prev[nstate] = cur_state
            heapq.heappush(heap, (new_cost, ncell, ndir))

    def find_corridor(
        self,
        start: Point,
        end: Point,
        crossing_penalty: float = 1.0,
    ) -> list[Point] | None:
        """Find shortest orthogonal path from start to end avoiding blocked cells.

        Uses Dijkstra/A* with optional crossing_penalty for already-routed segments.
        Returns None if no path exists.
        """
        res = self.resolution
        sc = self._to_cell(start.x, start.y)
        ec = self._to_cell(end.x, end.y)

        if sc == ec:
            return [Point(start.x, start.y)]

        # Dijkstra with direction state to prefer straight segments
        # State: (cell, direction)  direction: 'h' | 'v' | 'n'
        inf = float('inf')
        dist: dict[tuple[tuple[int, int], str], float] = {}
        prev: dict[tuple[tuple[int, int], str], tuple[tuple[int, int], str] | None] = {}
        heap: list[tuple[float, tuple[int, int], str]] = []

        for d in ('h', 'v', 'n'):
            state = (sc, d)
            dist[state] = 0.0
            prev[state] = None
            heapq.heappush(heap, (0.0, sc, d))

        found_state: tuple[tuple[int, int], str] | None = None

        while heap:
            cost, cell, direction = heapq.heappop(heap)
            state = (cell, direction)
            if cost > dist.get(state, inf):
                continue
            if cell == ec:
                found_state = state
                break

            cx, cy = cell
            neighbours = [
                ((cx + 1, cy), 'h'), ((cx - 1, cy), 'h'),
                ((cx, cy + 1), 'v'), ((cx, cy - 1), 'v'),
            ]
            for ncell, ndir in neighbours:
                self._expand_neighbour(ncell, ndir, cost, direction, res, crossing_penalty, dist, prev, heap, state)

        if found_state is None:
            return None

        # Reconstruct cell path
        cell_path: list[tuple[int, int]] = []
        cur: tuple[tuple[int, int], str] | None = found_state
        while cur is not None:
            cell_path.append(cur[0])
            cur = prev.get(cur)
        cell_path.reverse()

        # Convert cells to points, collapsing collinear segments to waypoints
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
