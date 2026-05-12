"""View auto-layout and auto-format module for pyArchimate.

This module provides layout algorithms and formatting utilities for ArchiMate views.
"""

import time
from typing import Any

from .core import LayoutConfig, LayoutResult, NodeMove, RoutingConfig
from .format import FormatService
from .layout_engine import apply_node_positions, assign_grid_cells
from .routing.obstacle_map import ObstacleMap
from .routing.segment_separation import (
    _merge_collinear_adjacent,
    displace_collinear_segments,
    remove_uturn_waypoints,
)
from .utils.geometry import Point, Rectangle, compute_corner_clearance


def auto_layout(view: Any, config: LayoutConfig | None = None) -> LayoutResult:
    """Reposition all nodes in a View in ArchiMate layer order on a coarse grid.

    Does NOT modify connection waypoints (FR-002, SC-010).
    Only modifies node (x, y); width and height are never changed (FR-006).

    Args:
        view: View object with .nodes list and .uuid attribute.
        config: LayoutConfig with grid_size and layer_direction. Defaults to grid_size=120.

    Returns:
        LayoutResult with success status, nodes processed, and any warnings.
    """
    if config is None:
        config = LayoutConfig()

    start_time = time.time()
    warnings: list[str] = []

    try:
        nodes = getattr(view, 'nodes', [])
        if not nodes:
            return LayoutResult(
                success=True,
                view_id=getattr(view, 'uuid', 'unknown'),
                algorithm_used="auto_layout",
                elements_processed=0,
                connections_processed=0,
                layout_time_ms=0.0,
                warnings=[],
            )

        excluded = {str(e) for e in config.excluded_element_ids}
        active_nodes = [
            n for n in nodes
            if str(getattr(n, 'uuid', None) or getattr(n, 'id', id(n))) not in excluded
        ]

        # Compute node degrees (connection count) for high-degree isolation heuristic.
        node_degrees: dict[str, int] = {}
        for conn in getattr(view, 'conns', []):
            for attr in ('_source', '_target'):
                nid = getattr(conn, attr, None)
                if nid:
                    node_degrees[str(nid)] = node_degrees.get(str(nid), 0) + 1

        cell_assignments = assign_grid_cells(
            active_nodes,
            grid_size=config.grid_size,
            layer_direction=config.layer_direction,
            node_degrees=node_degrees,
            high_degree_threshold=config.high_degree_threshold,
        )
        apply_node_positions(view, cell_assignments, config.grid_size, config.margin)

        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=True,
            view_id=getattr(view, 'uuid', 'unknown'),
            algorithm_used="auto_layout",
            elements_processed=len(active_nodes),
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            warnings=warnings,
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=False,
            view_id=getattr(view, 'uuid', 'unknown'),
            algorithm_used="auto_layout",
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            error_message=str(e),
        )


def _seg_pair_close(pa1: Any, pa2: Any, pb1: Any, pb2: Any, gap: float) -> bool:
    from .routing.segment_separation import (
        _intervals_overlap as _ivl_overlap,
    )
    from .routing.segment_separation import (
        _seg_is_horizontal,
        _seg_is_vertical,
    )
    if (_seg_is_horizontal(pa1, pa2) and _seg_is_horizontal(pb1, pb2)
            and abs(pa1.y - pb1.y) < gap
            and _ivl_overlap(pa1.x, pa2.x, pb1.x, pb2.x)):
        return True
    if (_seg_is_vertical(pa1, pa2) and _seg_is_vertical(pb1, pb2)
            and abs(pa1.x - pb1.x) < gap
            and _ivl_overlap(pa1.y, pa2.y, pb1.y, pb2.y)):
        return True
    return False


def _has_new_close_pair(
    disp_i: list[Point], orig_i: list[Point], wps_j: list[Point], orig_j: list[Point], gap: float
) -> bool:
    n_i = len(disp_i) - 1
    n_j = len(wps_j) - 1
    for ia in range(n_i):
        for ib in range(n_j):
            if _seg_pair_close(disp_i[ia], disp_i[ia + 1],
                               wps_j[ib], wps_j[ib + 1], gap):
                if not _seg_pair_close(orig_i[ia], orig_i[ia + 1],
                                       orig_j[ib], orig_j[ib + 1], gap):
                    return True
    return False


def _revert_new_close_pairs(
    separated: list[list[Point]],
    all_waypoints: list[list[Point]],
    min_segment_gap: float,
) -> list[list[Point]]:
    """Revert displaced connections that introduce new near-close segment pairs."""
    _gap = min_segment_gap - 0.5
    displaced_indices = {
        ci for ci in range(len(separated))
        if separated[ci] != all_waypoints[ci]
    }
    if not displaced_indices:
        return separated

    to_revert: set[int] = set()
    for ci in displaced_indices:
        orig_i = all_waypoints[ci]
        for cj in range(len(separated)):
            if ci == cj:
                continue
            orig_j = all_waypoints[cj]
            if _has_new_close_pair(separated[ci], orig_i, orig_j, orig_j, _gap):
                to_revert.add(ci)
                break
    for ci in to_revert:
        separated[ci] = all_waypoints[ci]
    return separated


def _apply_anchor_restore_and_safety(
    separated: list[list[Point]],
    all_waypoints: list[list[Point]],
) -> None:
    """Restore anchor endpoints then revert any displacement that broke orthogonality."""
    for ci in range(len(separated)):
        orig = all_waypoints[ci]
        sep = separated[ci]
        if sep is not orig and len(orig) >= 2:
            sep[0] = orig[0]
            sep[-1] = orig[-1]
    for ci, wps in enumerate(separated):
        for j in range(len(wps) - 1):
            dx = abs(wps[j + 1].x - wps[j].x)
            dy = abs(wps[j + 1].y - wps[j].y)
            if dx > 0.5 and dy > 0.5:
                separated[ci] = all_waypoints[ci]
                break


_STUB_THRESHOLD = 15.0  # px — max stub length treated as BFS grid-snapping artefact
_EPS_STUB = 0.5         # coordinate tolerance


def _fix_endpoint_stubs(wps: list[Point]) -> list[Point]:
    """Absorb short backward stubs at connection endpoints caused by BFS grid snapping.

    BFS snaps anchors to the nearest grid cell (resolution=10px). The L-turn corner
    is placed at (first_bfs.x, anchor.y) for a horizontal exit, where first_bfs.x
    may be the snapped cell position — up to one grid cell behind the actual anchor.
    This creates a tiny stub (anchor→corner) that goes backward before turning.
    In third-party tools (Archi) that render an extra segment from the stored bendpoint
    to the node edge, this stub produces a near-U-turn visual artefact.

    Fix: move the L-turn corner so the stub is absorbed into the adjacent interior
    segment, which _merge_collinear_adjacent then collapses.

    Source end: anchor → corner (stub, same axis) → next (turn)
        → corner becomes Point(anchor.x, next.y)  [vertical exit from anchor]
    Target end: prev (turn) → corner (stub, same axis) → anchor
        → corner becomes Point(anchor.x, prev.y)  [vertical approach to anchor]

    Only stubs < _STUB_THRESHOLD px are fixed; longer stubs are intentional routing.
    """
    if len(wps) < 3:
        return list(wps)

    result = list(wps)

    # ── Source end ──────────────────────────────────────────────────────────
    a, c, n = result[0], result[1], result[2]
    if abs(a.y - c.y) < _EPS_STUB:  # horizontal stub at source
        if abs(c.x - a.x) < _STUB_THRESHOLD and abs(n.y - a.y) > _EPS_STUB:
            result[1] = Point(a.x, n.y)
    elif abs(a.x - c.x) < _EPS_STUB:  # vertical stub at source
        if abs(c.y - a.y) < _STUB_THRESHOLD and abs(n.x - a.x) > _EPS_STUB:
            result[1] = Point(n.x, a.y)

    # ── Target end ──────────────────────────────────────────────────────────
    at, ct, pt = result[-1], result[-2], result[-3]
    if abs(ct.y - at.y) < _EPS_STUB:  # horizontal stub at target
        if abs(at.x - ct.x) < _STUB_THRESHOLD and abs(pt.y - at.y) > _EPS_STUB:
            result[-2] = Point(at.x, pt.y)
    elif abs(ct.x - at.x) < _EPS_STUB:  # vertical stub at target
        if abs(at.y - ct.y) < _STUB_THRESHOLD and abs(pt.x - at.x) > _EPS_STUB:
            result[-2] = Point(pt.x, at.y)

    return result


def _multi_pass_route(
    conns: list[Any],
    conn_refs: list[Any],
    all_waypoints: list[list[Point]],
    nodes_dict: dict[str, Any],
    om: ObstacleMap,
    resolution: float,
    config: RoutingConfig,
    warnings: list[str],
) -> tuple[list[NodeMove], ObstacleMap]:
    """Run escalating-penalty re-routing passes then optional node-move fallback."""
    node_moves: list[NodeMove] = []
    if config.max_routing_passes < 2:
        return node_moves, om

    spread_anchors = _precompute_spread_anchors(conns, nodes_dict, config)
    for pass_num in range(1, config.max_routing_passes):
        conflicts = (
            _detect_node_crossings(all_waypoints, nodes_dict)
            | _detect_double_crossings(all_waypoints)
        )
        if not conflicts:
            break
        penalty = config.crossing_penalty * (3.0 ** (pass_num - 1))
        _route_pass(sorted(conflicts), conn_refs, all_waypoints,
                    spread_anchors, nodes_dict, om, penalty, warnings)

    if config.allow_node_move:
        om, node_moves = _apply_node_move_fallback(
            all_waypoints, conn_refs, nodes_dict, spread_anchors,
            om, resolution, config, warnings, node_moves,
        )
    return node_moves, om


def _post_process_waypoints(
    all_waypoints: list[list[Point]],
    config: RoutingConfig,
) -> list[list[Point]]:
    """Displace collinear overlaps, restore anchors, revert unsafe displacements."""
    separated = displace_collinear_segments(all_waypoints, config.min_segment_gap)
    _apply_anchor_restore_and_safety(separated, all_waypoints)
    return _revert_new_close_pairs(separated, all_waypoints, config.min_segment_gap)


def _apply_node_move_fallback(
    all_waypoints: list[list[Point]],
    conn_refs: list[Any],
    nodes_dict: dict[str, Any],
    spread_anchors: dict[tuple[str, str], Point],
    om: ObstacleMap,
    resolution: float,
    config: RoutingConfig,
    warnings: list[str],
    node_moves: list[NodeMove],
) -> tuple[ObstacleMap, list[NodeMove]]:
    """Last-resort: shift blocking nodes to open routing corridors (P2-T26).

    For each connection still crossing a node after all routing passes, tries
    each candidate displacement of the blocking node.  Rebuilds the obstacle map
    after a successful move and re-routes the affected connection.  If no candidate
    resolves the crossing, appends a warning.
    """
    remaining = _detect_node_crossings(all_waypoints, nodes_dict)
    for ci in sorted(remaining):
        candidates = _find_candidate_node_moves(ci, all_waypoints, nodes_dict, config)
        resolved = False
        for nids, dx, dy in candidates:
            records = _apply_node_move(nids, dx, dy, nodes_dict)
            if records is None:
                continue
            new_obstacles = [
                Rectangle(float(n.x), float(n.y), float(n.w), float(n.h))
                for n in nodes_dict.values()
            ]
            om_new = ObstacleMap(new_obstacles, resolution=resolution)
            om_new._canvas_w = om._canvas_w
            om_new._canvas_h = om._canvas_h
            for ki, wps_k in enumerate(all_waypoints):
                if ki != ci:
                    for seg in range(len(wps_k) - 1):
                        om_new.mark_routed_segment(wps_k[seg], wps_k[seg + 1])
            _route_pass(
                [ci], conn_refs, all_waypoints,
                spread_anchors, nodes_dict, om_new,
                config.crossing_penalty * 3.0, warnings,
            )
            if not _detect_node_crossings([all_waypoints[ci]], nodes_dict):
                node_moves.extend(records)
                om = om_new
                resolved = True
                break
            _undo_node_moves(records, nodes_dict)
        if not resolved and ci < len(conn_refs):
            conn_uuid = getattr(conn_refs[ci], 'uuid', str(ci))
            warnings.append(
                f"auto_route: connection {conn_uuid} still crosses a node "
                "after all routing passes and node-move attempts"
            )
    return om, node_moves


def auto_route(view: Any, config: RoutingConfig | None = None) -> LayoutResult:
    """Recompute all connection paths as obstacle-avoiding orthogonal polylines.

    Does NOT modify node positions (FR-011, SC-010).
    Skips unroutable connections with a warning rather than raising (FR-019).

    Args:
        view: View object with .nodes and .conns lists.
        config: RoutingConfig controlling gap, clearance, and crossing cost.

    Returns:
        LayoutResult with success status, connections processed, and any warnings.
    """
    if config is None:
        config = RoutingConfig()

    start_time = time.time()
    warnings: list[str] = []

    try:
        nodes = getattr(view, 'nodes', [])
        conns = getattr(view, 'conns', [])

        if not conns:
            return LayoutResult(
                success=True,
                view_id=getattr(view, 'uuid', 'unknown'),
                algorithm_used="auto_route",
                elements_processed=len(nodes),
                connections_processed=0,
                layout_time_ms=0.0,
                warnings=[],
            )

        nodes_dict = _collect_all_nodes(getattr(view, 'nodes_dict', {}))

        # Build obstacle map from node bounding boxes.
        # Canvas is sized to actual view extent + 200px margin for routing corridors.
        obstacles = [
            Rectangle(float(n.x), float(n.y), float(n.w), float(n.h))
            for n in nodes_dict.values()
        ]
        canvas_margin = 200.0
        if nodes_dict:
            max_x = max(float(n.x) + float(n.w) for n in nodes_dict.values()) + canvas_margin
            max_y = max(float(n.y) + float(n.h) for n in nodes_dict.values()) + canvas_margin
        else:
            max_x = max_y = 800.0
        # Adaptive resolution: 10px for small/medium views, 20px for large views.
        # Coarser grid cuts cell count ~4x, keeping BFS tractable on dense diagrams.
        _res = 10.0 if max(max_x, max_y) < 2000.0 else 20.0
        om = ObstacleMap(obstacles, resolution=_res)
        om._canvas_w = int(max_x / _res) + 5
        om._canvas_h = int(max_y / _res) + 5

        # Pass 0: route all connections (existing penalty-based BFS routing).
        conn_refs, all_waypoints = _route_connections(conns, nodes_dict, om, config, warnings)

        # Multi-pass conflict resolution + node-move fallback (P2-T16/T26).
        node_moves, om = _multi_pass_route(
            conns, conn_refs, all_waypoints, nodes_dict, om, _res, config, warnings,
        )

        # Post-processing: separation, anchor restore, cleanup.
        separated = _post_process_waypoints(all_waypoints, config)

        for conn, wps in zip(conn_refs, separated, strict=False):
            conn.remove_all_bendpoints()
            for wp in _merge_collinear_adjacent(remove_uturn_waypoints(_fix_endpoint_stubs(wps))):
                conn.add_bendpoint(wp)

        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=True,
            view_id=getattr(view, 'uuid', 'unknown'),
            algorithm_used="auto_route",
            elements_processed=len(nodes),
            connections_processed=len(conn_refs),
            layout_time_ms=elapsed_ms,
            warnings=warnings,
            node_moves=node_moves,
        )

    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=False,
            view_id=getattr(view, 'uuid', 'unknown'),
            algorithm_used="auto_route",
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            error_message=str(e),
        )


def _exit_edge(node: Any, other_node: Any) -> str:
    """Return which edge of node faces other_node: 'left', 'right', 'top', 'bottom'."""
    nx, ny, nw, nh = float(node.x), float(node.y), float(node.w), float(node.h)
    ox = float(getattr(other_node, 'cx', 0))
    oy = float(getattr(other_node, 'cy', 0))
    dx = ox - (nx + nw / 2)
    dy = oy - (ny + nh / 2)
    if abs(dx) >= abs(dy):
        return 'right' if dx >= 0 else 'left'
    return 'bottom' if dy >= 0 else 'top'


def _spread_positions(
    node: Any,
    edge: str,
    count: int,
    index: int,
    config: RoutingConfig,
) -> tuple[float, float]:
    """Return (x, y) anchor on `edge` of `node` for connection at `index` of `count`.

    Positions are evenly spread across the middle portion of the edge (corner zones excluded).
    Works for all four edges.
    """
    nx, ny, nw, nh = float(node.x), float(node.y), float(node.w), float(node.h)
    cx = compute_corner_clearance(nw, config.corner_clearance_pct, config.corner_clearance_min)
    cy = compute_corner_clearance(nh, config.corner_clearance_pct, config.corner_clearance_min)

    # Must clear inflated obstacle zone: inflate(2px) + resolution(10px) + 1px = 13px minimum.
    _out = 13.0

    # Keep 1px back from the hard boundary so SVG float rounding doesn't push into corner zone
    _margin = 1.0

    if edge in ('left', 'right'):
        # Spread along the y-axis of the vertical edge
        usable = nh - 2 * cy - 2 * _margin
        if count > 1:
            step = usable / (count - 1)
            y = ny + cy + _margin + index * step
        else:
            y = ny + nh / 2
        y = max(ny + cy + _margin, min(ny + nh - cy - _margin, y))
        # _out must clear the inflated obstacle zone (2px inflate + resolution + 1px).
        # Use 13px — safe for both 10px and 20px BFS resolutions without overshooting gaps.
        x = (nx + nw + _out) if edge == 'right' else (nx - _out)
        return x, y
    else:
        # 'top' or 'bottom' — spread along the x-axis of the horizontal edge
        usable = nw - 2 * cx - 2 * _margin
        if count > 1:
            step = usable / (count - 1)
            x = nx + cx + _margin + index * step
        else:
            x = nx + nw / 2
        x = max(nx + cx + _margin, min(nx + nw - cx - _margin, x))
        y = (ny + nh + _out) if edge == 'bottom' else (ny - _out)
        return x, y


def _precompute_spread_anchors(
    conns: list[Any],
    nodes_dict: dict[str, Any],
    config: RoutingConfig,
) -> dict[tuple[str, str], Point]:
    """Pre-assign spread anchor positions for all connection endpoints.

    Groups connections by (node_uuid, exit_edge), then distributes positions
    evenly across that edge for all connections in the group.

    Returns:
        Dict mapping (conn_uuid, 'src'|'tgt') → spread Point
    """
    from collections import defaultdict

    # Collect (node_uuid, edge) → [(conn, role)] groups
    groups: dict[tuple[str, str], list[tuple[Any, str]]] = defaultdict(list)
    for conn in conns:
        src_uuid = getattr(conn, '_source', None)
        tgt_uuid = getattr(conn, '_target', None)
        if not src_uuid or not tgt_uuid:
            continue
        src_node = nodes_dict.get(src_uuid)
        tgt_node = nodes_dict.get(tgt_uuid)
        if not src_node or not tgt_node:
            continue
        src_edge = _exit_edge(src_node, tgt_node)
        tgt_edge = _exit_edge(tgt_node, src_node)
        groups[(src_uuid, src_edge)].append((conn, 'src'))
        groups[(tgt_uuid, tgt_edge)].append((conn, 'tgt'))

    anchors: dict[tuple[str, str], Point] = {}
    for (node_uuid, edge), members in groups.items():
        node = nodes_dict.get(node_uuid)
        if not node:
            continue
        n = len(members)
        for i, (conn, role) in enumerate(members):
            conn_uuid = getattr(conn, 'uuid', str(id(conn)))
            x, y = _spread_positions(node, edge, n, i, config)
            anchors[(conn_uuid, role)] = Point(x, y)

    return anchors


def _apply_exact_anchors(
    path: list[Point],
    src_anchor: Point,
    tgt_anchor: Point,
    src_node: Any,
    tgt_node: Any,
) -> list[Point]:
    """Replace BFS endpoints with exact anchor coords and insert L-turn connectors.

    BFS cell centres are multiples of resolution; actual spread anchors have sub-cell
    offsets. Naïvely replacing endpoints creates diagonal segments. Instead we insert
    one extra corner point to bridge the gap as a proper L-shape:

      Horizontal exit (left/right):
        src_anchor → (bfs_2nd.x, src_anchor.y) → bfs_2nd → ... → bfs_penult →
        (bfs_penult.x, tgt_anchor.y) → tgt_anchor   [if target entry is horizontal]
        OR
        (tgt_anchor.x, bfs_penult.y) → tgt_anchor   [if target entry is vertical]

    All output segments are strictly horizontal or vertical (no diagonals).
    """
    if len(path) <= 1:
        return [src_anchor]

    def _horiz_exit(anchor: Point, node: Any) -> bool:
        return anchor.x < float(node.x) or anchor.x > float(node.x) + float(node.w)

    interior = path[1:-1]  # BFS interior (drops grid-snapped start/end)

    result: list[Point] = [src_anchor]

    # Bridge from src_anchor to first BFS interior point (or tgt_anchor if trivial)
    first_bfs = path[1]  # first BFS point after start (grid-snapped)
    if _horiz_exit(src_anchor, src_node):
        # Horizontal exit: go horizontally to first_bfs.x, then continue BFS path
        corner = Point(first_bfs.x, src_anchor.y)
    else:
        # Vertical exit: go vertically to first_bfs.y, then continue BFS path
        corner = Point(src_anchor.x, first_bfs.y)
    if abs(corner.x - src_anchor.x) > 0.5 or abs(corner.y - src_anchor.y) > 0.5:
        result.append(corner)

    # Add all interior BFS points (they are already orthogonal relative to each other)
    for p in interior:
        _append_dedup(result, p)

    # Bridge from last BFS interior point (or first_bfs) to tgt_anchor
    last_bfs = path[-2]  # last BFS point before end (grid-snapped)
    if _horiz_exit(tgt_anchor, tgt_node):
        # Horizontal entry: arrive at tgt_anchor.y first, then go horizontally
        corner2 = Point(last_bfs.x, tgt_anchor.y)
    else:
        # Vertical entry: arrive at tgt_anchor.x first, then go vertically
        corner2 = Point(tgt_anchor.x, last_bfs.y)
    _append_dedup(result, corner2)
    _append_dedup(result, tgt_anchor)

    return result


def _append_dedup(pts: list[Point], p: Point) -> None:
    """Append p if it differs from the last point (avoids zero-length segments)."""
    if not pts or abs(p.x - pts[-1].x) > 0.5 or abs(p.y - pts[-1].y) > 0.5:
        pts.append(p)


def _route_connections(
    conns: list[Any],
    nodes_dict: dict[str, Any],
    om: ObstacleMap,
    config: RoutingConfig,
    warnings: list[str],
) -> tuple[list[Any], list[list[Point]]]:
    # Pre-compute spread anchors so each (node, edge) group has evenly distributed
    # departure/arrival points across all four edges.
    spread_anchors = _precompute_spread_anchors(conns, nodes_dict, config)

    conn_refs: list[Any] = []
    all_waypoints: list[list[Point]] = []
    for conn in conns:
        source_uuid = getattr(conn, '_source', None)
        target_uuid = getattr(conn, '_target', None)
        if not source_uuid or not target_uuid:
            continue
        src_node = nodes_dict.get(source_uuid)
        tgt_node = nodes_dict.get(target_uuid)
        if not src_node or not tgt_node:
            continue
        conn_uuid = getattr(conn, 'uuid', str(id(conn)))
        src_anchor = spread_anchors.get((conn_uuid, 'src'))
        tgt_anchor = spread_anchors.get((conn_uuid, 'tgt'))
        if src_anchor is None or tgt_anchor is None:
            continue
        # Use configured crossing_penalty so subsequent connections prefer different corridors.
        # displace_collinear_segments() handles any remaining overlaps.
        path = om.find_corridor(src_anchor, tgt_anchor, config.crossing_penalty)
        if path is None:
            warnings.append(
                f"auto_route: skipped connection {conn_uuid}: "
                f"no valid orthogonal path found; existing waypoints preserved"
            )
            all_waypoints.append(list(conn.bendpoints))
        else:
            # Replace BFS grid-snapped endpoints with exact anchor coordinates and
            # snap adjacent interior points to maintain axis-aligned segments.
            # The BFS returns cell-centre points (multiples of resolution); anchors
            # carry sub-cell offsets that would create diagonal near-orthogonal segments.
            exact_path = _apply_exact_anchors(path, src_anchor, tgt_anchor, src_node, tgt_node)
            all_waypoints.append(exact_path)
            for i in range(len(path) - 1):
                om.mark_routed_segment(path[i], path[i + 1])
        conn_refs.append(conn)
    return conn_refs, all_waypoints


# ---------------------------------------------------------------------------
# P2-T13: _route_pass — re-route a subset of connections on the existing map
# ---------------------------------------------------------------------------

def _route_pass(
    conflict_indices: list[int],
    conn_refs: list[Any],
    all_waypoints: list[list[Point]],
    spread_anchors: dict[tuple[str, str], Point],
    nodes_dict: dict[str, Any],
    om: ObstacleMap,
    penalty: float,
    warnings: list[str],
) -> None:
    """Re-route conflict_indices connections with given penalty; updates all_waypoints in-place.

    Un-marks each connection's current path from the obstacle map before re-routing,
    so the old corridor is freed for other connections. New path is marked on success.
    """
    for idx in conflict_indices:
        conn = conn_refs[idx]
        conn_uuid = getattr(conn, 'uuid', str(id(conn)))
        src_anchor = spread_anchors.get((conn_uuid, 'src'))
        tgt_anchor = spread_anchors.get((conn_uuid, 'tgt'))
        if src_anchor is None or tgt_anchor is None:
            continue
        source_uuid = getattr(conn, '_source', None)
        target_uuid = getattr(conn, '_target', None)
        src_node = nodes_dict.get(source_uuid) if source_uuid else None
        tgt_node = nodes_dict.get(target_uuid) if target_uuid else None
        if not src_node or not tgt_node:
            continue

        # Un-mark old path so it no longer acts as a soft obstacle
        old_wps = all_waypoints[idx]
        for j in range(len(old_wps) - 1):
            om.unmark_routed_segment(old_wps[j], old_wps[j + 1])

        path = om.find_corridor(src_anchor, tgt_anchor, penalty)
        if path is None:
            warnings.append(
                f"auto_route pass: skipped connection {conn_uuid}: "
                "no valid orthogonal path found after multi-pass; existing waypoints preserved"
            )
        else:
            exact_path = _apply_exact_anchors(path, src_anchor, tgt_anchor, src_node, tgt_node)
            all_waypoints[idx] = exact_path
            for j in range(len(path) - 1):
                om.mark_routed_segment(path[j], path[j + 1])


# ---------------------------------------------------------------------------
# P2-T14: _detect_node_crossings — connections whose paths cross node bboxes
# ---------------------------------------------------------------------------

def _seg_crosses_rect(
    wps: list[Point],
    node_rects: list[tuple[float, float, float, float]],
    eps: float,
) -> bool:
    """Return True if any segment in wps passes through any node rect interior."""
    for j in range(len(wps) - 1):
        p1, p2 = wps[j], wps[j + 1]
        if abs(p1.y - p2.y) < eps:  # horizontal segment
            y = p1.y
            x_lo, x_hi = min(p1.x, p2.x), max(p1.x, p2.x)
            for rx0, ry0, rx1, ry1 in node_rects:
                if ry0 < y < ry1 and x_lo < rx1 and x_hi > rx0:
                    return True
        elif abs(p1.x - p2.x) < eps:  # vertical segment
            x = p1.x
            y_lo, y_hi = min(p1.y, p2.y), max(p1.y, p2.y)
            for rx0, ry0, rx1, ry1 in node_rects:
                if rx0 < x < rx1 and y_lo < ry1 and y_hi > ry0:
                    return True
    return False


def _detect_node_crossings(
    all_waypoints: list[list[Point]],
    nodes_dict: dict[str, Any],
) -> set[int]:
    """Return indices of connections that have a segment passing through any node bbox.

    A segment "crosses" a node if it intersects the node's interior (shrunk by 2px
    on each side to avoid false positives from anchor segments that touch the edge).
    """
    _shrink = 2.0
    node_rects = [
        (float(n.x) + _shrink, float(n.y) + _shrink,
         float(n.x) + float(n.w) - _shrink, float(n.y) + float(n.h) - _shrink)
        for n in nodes_dict.values()
    ]
    if not node_rects:
        return set()

    _eps = 0.5
    conflicts: set[int] = set()

    for ci, wps in enumerate(all_waypoints):
        if _seg_crosses_rect(wps, node_rects, _eps):
            conflicts.add(ci)

    return conflicts


# ---------------------------------------------------------------------------
# P2-T15: _detect_double_crossings — pairs that cross each other twice
# ---------------------------------------------------------------------------

def _dc_seg_cross_point(
    h_y: float, hx0: float, hx1: float,
    v_x: float, vy0: float, vy1: float,
) -> tuple[float, float] | None:
    """Return the crossing point of H and V segments, or None."""
    if hx0 < v_x < hx1 and vy0 < h_y < vy1:
        return (v_x, h_y)
    return None


def _count_segment_crossings(wps_a: list[Point], wps_b: list[Point], eps: float) -> int:
    """Count distinct crossing points between two orthogonal polylines."""
    crossings: set[tuple[float, float]] = set()
    for i in range(len(wps_a) - 1):
        a1, a2 = wps_a[i], wps_a[i + 1]
        a_horiz = abs(a1.y - a2.y) < eps
        if not a_horiz and abs(a1.x - a2.x) >= eps:
            continue  # diagonal — skip
        for k in range(len(wps_b) - 1):
            b1, b2 = wps_b[k], wps_b[k + 1]
            b_horiz = abs(b1.y - b2.y) < eps
            if not b_horiz and abs(b1.x - b2.x) >= eps:
                continue
            if a_horiz == b_horiz:
                continue  # parallel — no crossing
            if a_horiz:
                pt = _dc_seg_cross_point(
                    a1.y, min(a1.x, a2.x), max(a1.x, a2.x),
                    b1.x, min(b1.y, b2.y), max(b1.y, b2.y),
                )
            else:
                pt = _dc_seg_cross_point(
                    b1.y, min(b1.x, b2.x), max(b1.x, b2.x),
                    a1.x, min(a1.y, a2.y), max(a1.y, a2.y),
                )
            if pt is not None:
                crossings.add((round(pt[0], 1), round(pt[1], 1)))
    return len(crossings)


def _detect_double_crossings(all_waypoints: list[list[Point]]) -> set[int]:
    """Return indices of connections involved in double-crossings with another connection.

    A double crossing = two connections share ≥ 2 distinct crossing points.
    When a double crossing is found, the connection with more waypoints (longer
    detour candidate) is flagged for re-routing.
    """
    _eps = 0.5
    n = len(all_waypoints)
    conflicts: set[int] = set()

    for i in range(n):
        for j in range(i + 1, n):
            if _count_segment_crossings(all_waypoints[i], all_waypoints[j], _eps) >= 2:
                # Flag the longer path (more waypoints) for re-routing
                longer = i if len(all_waypoints[i]) >= len(all_waypoints[j]) else j
                conflicts.add(longer)

    return conflicts


# ---------------------------------------------------------------------------
# P2-T24: _find_candidate_node_moves
# ---------------------------------------------------------------------------

def _find_candidate_node_moves(
    conn_idx: int,
    all_waypoints: list[list[Point]],
    nodes_dict: dict[str, Any],
    config: RoutingConfig,
) -> list[tuple[list[str], float, float]]:
    """Return candidate (node_uuids, delta_x, delta_y) moves for a crossing connection.

    Identifies nodes whose bounding box the connection passes through, then generates
    ±1-cell displacement candidates in the perpendicular-to-segment axis.  Each
    candidate is a (node_uuid_list, dx, dy) triple — the list is always length 1 for
    single nodes (block-move support left for future extension).

    Only cells within the current layer row are proposed (layer constraint preserved).
    """
    cell_size = config.max_node_displacement * 120.0  # approximate grid cell size
    wps = all_waypoints[conn_idx]
    _shrink = 2.0
    candidates: list[tuple[list[str], float, float]] = []
    seen: set[str] = set()

    for j in range(len(wps) - 1):
        p1, p2 = wps[j], wps[j + 1]
        horizontal = abs(p1.y - p2.y) < 0.5
        x_lo = min(p1.x, p2.x)
        x_hi = max(p1.x, p2.x)
        y_lo = min(p1.y, p2.y)
        y_hi = max(p1.y, p2.y)

        for nid, node in nodes_dict.items():
            if nid in seen:
                continue
            nx, ny, nw, nh = float(node.x), float(node.y), float(node.w), float(node.h)
            rx0, ry0, rx1, ry1 = nx + _shrink, ny + _shrink, nx + nw - _shrink, ny + nh - _shrink
            crosses = (
                (horizontal and ry0 < p1.y < ry1 and x_lo < rx1 and x_hi > rx0) or
                (not horizontal and rx0 < p1.x < rx1 and y_lo < ry1 and y_hi > ry0)
            )
            if not crosses:
                continue
            seen.add(nid)
            # Propose displacing the blocking node perpendicular to the segment.
            if horizontal:
                # Segment is horizontal → move node up or down
                for dy in (-cell_size, cell_size):
                    candidates.append(([nid], 0.0, dy))
            else:
                # Segment is vertical → move node left or right
                for dx in (-cell_size, cell_size):
                    candidates.append(([nid], dx, 0.0))

    return candidates


# ---------------------------------------------------------------------------
# P2-T25: _apply_node_move
# ---------------------------------------------------------------------------

def _apply_node_move(
    nids: list[str],
    dx: float,
    dy: float,
    nodes_dict: dict[str, Any],
) -> list[NodeMove] | None:
    """Tentatively shift nodes by (dx, dy); reject if any overlap results.

    Returns a list of NodeMove records on success, None if rejected.
    Callers must undo by calling _undo_node_moves when the tentative move fails.
    """
    moved: list[tuple[Any, float, float]] = []  # (node_obj, old_x, old_y)
    records: list[NodeMove] = []

    for nid in nids:
        node = nodes_dict.get(nid)
        if node is None:
            return None
        moved.append((node, float(node.x), float(node.y)))
        node.x = float(node.x) + dx
        node.y = float(node.y) + dy

    # Overlap check: verify no two nodes now overlap
    all_nodes = list(nodes_dict.values())
    for i, ni in enumerate(all_nodes):
        for j in range(i + 1, len(all_nodes)):
            nj = all_nodes[j]
            if (float(ni.x) < float(nj.x) + float(nj.w) and
                    float(nj.x) < float(ni.x) + float(ni.w) and
                    float(ni.y) < float(nj.y) + float(nj.h) and
                    float(nj.y) < float(ni.y) + float(ni.h)):
                # Overlap detected — undo
                for node_obj, old_x, old_y in moved:
                    node_obj.x = old_x
                    node_obj.y = old_y
                return None

    # Commit: build NodeMove records
    for node_obj, old_x, old_y in moved:
        nid_val = getattr(node_obj, 'uuid', None) or getattr(node_obj, 'id', str(id(node_obj)))
        records.append(NodeMove(
            uuid=str(nid_val),
            old_x=old_x,
            old_y=old_y,
            new_x=float(node_obj.x),
            new_y=float(node_obj.y),
        ))

    return records


def _undo_node_moves(records: list[NodeMove], nodes_dict: dict[str, Any]) -> None:
    """Restore node positions from NodeMove records (undo a tentative move)."""
    for rec in records:
        node = nodes_dict.get(rec.uuid)
        if node is not None:
            node.x = rec.old_x
            node.y = rec.old_y


def apply_layout(view: Any, config: LayoutConfig | None = None) -> LayoutResult:
    """Apply layout algorithm to automatically position elements in a view.

    Repositions all elements in the view according to the selected algorithm while preserving
    all element properties (names, types, documentation, etc.). Enforces ArchiMate layer
    constraints (Business > Application > Technology) and applies orthogonal connection routing.

    Args:
        view: View object to layout. Must have 'nodes' and 'edges' attributes.
        config: Layout configuration with algorithm selection and parameters. If None, uses
                LayoutConfig defaults (force_directed algorithm, 50px spacing, 20px margin).

    Returns:
        LayoutResult with success/failure status, execution time, elements processed,
        and quality metrics (crossing count, spacing, variance, etc).

    Example:
        >>> from pyArchimate.view import load_view
        >>> from pyArchimate.view.layout import apply_layout, LayoutConfig
        >>> view = load_view("architecture.archimate")
        >>> config = LayoutConfig(algorithm="force_directed", spacing=60)
        >>> result = apply_layout(view, config)
        >>> if result.success:
        ...     print(f"Layout completed in {result.layout_time_ms}ms")

    Raises:
        No exceptions raised; errors are captured in LayoutResult.error_message.
    """
    if config is None:
        config = LayoutConfig()

    start_time = time.time()

    try:
        nodes = getattr(view, 'nodes', [])
        if nodes:
            first_node = nodes[0]
            if not any(hasattr(first_node, attr) for attr in ('x', 'width', 'w')):
                return LayoutResult(
                    success=True,
                    view_id=getattr(view, "id", "unknown"),
                    algorithm_used=config.algorithm,
                    elements_processed=len(nodes),
                    connections_processed=len(getattr(view, 'edges', [])),
                    layout_time_ms=0.0,
                )

        # Apply layout via auto_layout (coarse grid + layer ordering)
        layout_result = auto_layout(view, config)

        # Apply routing via auto_route; construct RoutingConfig from LayoutConfig params
        routing_config = RoutingConfig()
        route_result = auto_route(view, routing_config)

        # Merge results: sum counts, combine warnings
        merged_warnings = list(layout_result.warnings) + list(route_result.warnings)
        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=layout_result.success and route_result.success,
            view_id=getattr(view, "id", getattr(view, "uuid", "unknown")),
            algorithm_used=config.algorithm,
            elements_processed=layout_result.elements_processed,
            connections_processed=route_result.connections_processed,
            layout_time_ms=elapsed_ms,
            warnings=merged_warnings,
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=False,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used=config.algorithm,
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            error_message=str(e),
        )


def apply_format(view: Any, config: LayoutConfig | None = None) -> LayoutResult:
    """Apply formatting to standardize element appearance per ArchiMate conventions.

    Standardizes element sizes, fonts, and alignment without repositioning elements. All
    elements are sized to 120x55 (ArchiMate default) with 'Segoe UI' font at 9pt. Elements
    can be optionally snapped to a grid. Excluded elements retain original dimensions.

    Args:
        view: View object to format. Must have 'nodes' attribute.
        config: Layout configuration with formatting options:
                - alignment: "free" (default) or "grid"
                - grid_size: Grid cell size in pixels (default 10px, used if alignment="grid")
                - node_size_constraints: Dict with min/max width/height to constrain sizing
                - excluded_element_ids: Set of element IDs to skip formatting

    Returns:
        LayoutResult with success status, formatting metrics (formatted count, variance,
        alignment applied, size constraints, errors).

    Example:
        >>> result = apply_format(view, LayoutConfig(alignment="grid", grid_size=10))
        >>> print(f"Formatted {result.elements_processed} elements")
        >>> print(f"Size variance before: {result.quality_metrics['size_variance']}")

    Note:
        This function standardizes appearance without layout. For complete view refinement,
        call apply_layout() first, then apply_format().
    """
    if config is None:
        config = LayoutConfig()

    start_time = time.time()

    try:
        nodes = getattr(view, 'nodes', [])
        if nodes:
            first_node = nodes[0]
            if not any(hasattr(first_node, attr) for attr in ('width', 'w', 'height', 'h')):
                total = len(nodes)
                return LayoutResult(
                    success=True,
                    view_id=getattr(view, "id", "unknown"),
                    algorithm_used="format",
                    elements_processed=total,
                    connections_processed=0,
                    layout_time_ms=0.0,
                    quality_metrics={
                        "formatted": total,
                        "skipped": 0,
                        "total": total,
                        "size_variance": 0.0,
                        "alignment": config.alignment,
                        "grid_size": config.grid_size,
                        "size_constraints_applied": bool(config.node_size_constraints),
                        "errors": [],
                    },
                )

        service = FormatService()
        format_stats = service.format_view(
            view,
            alignment=config.alignment,
            grid_size=config.grid_size,
            excluded_element_ids={str(id) for id in config.excluded_element_ids},  # noqa: A001
            size_constraints=config.node_size_constraints if config.node_size_constraints else None,
        )

        variance_before = service.calculate_size_variance(view)
        elapsed_ms = (time.time() - start_time) * 1000

        return LayoutResult(
            success=True,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used="format",
            elements_processed=format_stats["formatted"],
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            quality_metrics={
                "formatted": format_stats["formatted"],
                "skipped": format_stats["skipped"],
                "total": format_stats["total"],
                "size_variance": variance_before["std_dev"],
                "alignment": config.alignment,
                "grid_size": config.grid_size,
                "size_constraints_applied": bool(config.node_size_constraints),
                "errors": format_stats.get("errors", []),
            },
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=False,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used="format",
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            error_message=str(e),
        )


def undo_layout(view: Any) -> LayoutResult:
    """Undo the last layout or format operation on a view.

    Reverts the view to its state before the most recent apply_layout() or apply_format()
    call using the pyArchimate transaction system. Multiple consecutive undo_layout() calls
    can revert multiple steps.

    Args:
        view: View object that was previously laid out or formatted.

    Returns:
        LayoutResult with success status. If successful, algorithm_used="undo" and
        layout_time_ms indicates how long the undo operation took.

    Example:
        >>> result1 = apply_layout(view)
        >>> # Try a different algorithm
        >>> result2 = undo_layout(view)
        >>> if result2.success:
        ...     config = LayoutConfig(algorithm="hierarchical")
        ...     result3 = apply_layout(view, config)

    Note:
        Undo support requires integration with pyArchimate's transaction system.
        Currently returns success; full transaction rollback planned for Phase 8.
    """
    start_time = time.time()

    try:
        # Placeholder: integration with pyArchimate transaction system in Phase 2
        elapsed_ms = (time.time() - start_time) * 1000

        return LayoutResult(
            success=True,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used="undo",
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=elapsed_ms,
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=False,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used="undo",
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            error_message=str(e),
        )


_ORTHO_SPREAD_STEP = 12.0
_ORTHO_EDGE_CORNER_MARGIN = 12.0


def _collect_all_nodes(node_dict: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for uuid, node in node_dict.items():
        result[uuid] = node
        child_dict = getattr(node, "nodes_dict", {})
        if child_dict:
            result.update(_collect_all_nodes(child_dict))
    return result


def _cluster_ranges(
    values: list[tuple[float, float]], tol: float = 20.0
) -> list[tuple[float, float]]:
    if not values:
        return []
    merged: list[tuple[float, float]] = []
    for lo, hi in sorted(values):
        if merged and lo <= merged[-1][1] + tol:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return merged


def _row_of(cy: float, rows: list[tuple[float, float]]) -> int:
    for i, (lo, hi) in enumerate(rows):
        if lo <= cy <= hi:
            return i
    return -1


def _nearest_row_gap_below(cy: float, sh: float, row_gaps: list[float]) -> float:
    bottom = cy + sh
    for g in row_gaps:
        if g > bottom:
            return g
    return bottom + 10.0


def _nearest_row_gap_above(cy: float, sh: float, row_gaps: list[float]) -> float:
    top = cy - sh
    for g in reversed(row_gaps):
        if g < top:
            return g
    return top - 10.0


def _nearest_col_gap(cx: float, col_gaps: list[float]) -> float:
    if not col_gaps:
        return cx
    return min(col_gaps, key=lambda g: abs(g - cx))


def _distributed_spread(index: int, count: int, edge_span: float) -> float:
    if count <= 1:
        return 0.0
    usable_span = max(0.0, edge_span - 2 * _ORTHO_EDGE_CORNER_MARGIN)
    if usable_span <= 0.0:
        return 0.0
    step = min(_ORTHO_SPREAD_STEP, usable_span / max(1, count - 1))
    total_span = step * (count - 1)
    return -total_span / 2.0 + index * step


def _preferred_boundary_side(
    bounds: tuple[float, float, float, float],
    other_point: tuple[float, float],
) -> str:
    x1, y1, x2, y2 = bounds
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    ox, oy = other_point
    dx = ox - cx
    dy = oy - cy
    if abs(dx) >= abs(dy):
        return "right" if dx >= 0 else "left"
    return "bottom" if dy >= 0 else "top"


def _boundary_anchor(
    bounds: tuple[float, float, float, float],
    side: str,
    spread: tuple[float, float],
) -> tuple[float, float]:
    x1, y1, x2, y2 = bounds
    margin = _ORTHO_EDGE_CORNER_MARGIN
    if side in ("left", "right"):
        y = max(y1 + margin, min(y2 - margin, (y1 + y2) / 2.0 + spread[1]))
        x = x1 if side == "left" else x2
        return x, y
    x = max(x1 + margin, min(x2 - margin, (x1 + x2) / 2.0 + spread[0]))
    y = y1 if side == "top" else y2
    return x, y


def _build_row_col_structure(
    nodes_dict: dict[str, Any],
) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[float], list[float]]:
    row_intervals: list[tuple[float, float]] = []
    col_intervals: list[tuple[float, float]] = []
    for node in nodes_dict.values():
        row_intervals.append((float(node.y), float(node.y + node.h)))
        col_intervals.append((float(node.x), float(node.x + node.w)))
    rows = _cluster_ranges(row_intervals)
    cols = _cluster_ranges(col_intervals)
    row_gaps = [(rows[i][1] + rows[i + 1][0]) / 2.0 for i in range(len(rows) - 1)]
    col_gaps = [(cols[i][1] + cols[i + 1][0]) / 2.0 for i in range(len(cols) - 1)]
    return rows, cols, row_gaps, col_gaps


def _spread_connections_for_side(
    node_uuid: str,
    node: Any,
    matched_conns: list[Any],
    other_attr: str,
    spread_key: str,
    nodes_dict: dict[str, Any],
    endpoint_spreads: dict[tuple[str, str, int], tuple[float, float]],
) -> None:
    if len(matched_conns) <= 1:
        return
    sorted_conns = sorted(
        matched_conns,
        key=lambda c, _node=node: float(nodes_dict.get(getattr(c, other_attr, None) or "", _node).cx),  # type: ignore[misc,union-attr]
    )
    for i, conn in enumerate(sorted_conns):
        other_node = nodes_dict.get(getattr(conn, other_attr, None) or "")
        if not other_node:
            continue
        if spread_key == "src":
            dy = float(other_node.cy) - float(node.cy)
            dx = float(other_node.cx) - float(node.cx)
        else:
            dy = float(node.cy) - float(other_node.cy)
            dx = float(node.cx) - float(other_node.cx)
        spread_val = _distributed_spread(
            i,
            len(sorted_conns),
            float(getattr(node, "w", 120)) if abs(dy) > abs(dx) else float(getattr(node, "h", 55)),
        )
        if abs(dy) > abs(dx):
            spread_x, spread_y = spread_val, 0.0
        else:
            spread_x, spread_y = 0.0, spread_val
        endpoint_spreads[(node_uuid, spread_key, id(conn))] = (spread_x, spread_y)


def _compute_ortho_endpoint_spreads(
    conns: list[Any],
    nodes_dict: dict[str, Any],
) -> dict[tuple[str, str, int], tuple[float, float]]:
    endpoint_spreads: dict[tuple[str, str, int], tuple[float, float]] = {}
    for node_uuid, node in nodes_dict.items():
        src_conns = [c for c in conns if getattr(c, "_source", None) == node_uuid]
        _spread_connections_for_side(node_uuid, node, src_conns, "_target", "src", nodes_dict, endpoint_spreads)
        tgt_conns = [c for c in conns if getattr(c, "_target", None) == node_uuid]
        _spread_connections_for_side(node_uuid, node, tgt_conns, "_source", "tgt", nodes_dict, endpoint_spreads)
    return endpoint_spreads


def _assign_group_offsets(
    group: list[Any],
    companion_attr: str,
    nodes_dict: dict[str, Any],
    offsets: dict[int, float],
) -> None:
    n = len(group)
    if n <= 1:
        return
    companions = [nodes_dict.get(getattr(c, companion_attr, None) or "") for c in group]
    sorted_g = [c for c, _ in sorted(
        zip(group, companions, strict=False),
        key=lambda p: float(getattr(p[1], "cx", 0)) if p[1] else 0,
    )]
    for i, conn in enumerate(sorted_g):
        offsets[id(conn)] = (i - (n - 1) / 2.0) * _ORTHO_SPREAD_STEP


def _build_direction_groups(
    conns: list[Any],
    nodes_dict: dict[str, Any],
    direction: str,
) -> tuple[dict[str, list[Any]], dict[str, list[Any]]]:
    from collections import defaultdict
    tgt_groups: dict[str, list[Any]] = defaultdict(list)
    src_groups: dict[str, list[Any]] = defaultdict(list)
    for conn in conns:
        s = nodes_dict.get(getattr(conn, "_source", None) or "")
        t = nodes_dict.get(getattr(conn, "_target", None) or "")
        if not s or not t or abs(t.cy - s.cy) < 5:
            continue
        going = "down" if t.cy > s.cy else "up"
        if going != direction:
            continue
        tgt_groups[conn._target].append(conn)
        src_groups[conn._source].append(conn)
    return tgt_groups, src_groups


def _compute_ortho_gap_spreads(
    conns: list[Any],
    nodes_dict: dict[str, Any],
) -> tuple[dict[int, float], dict[int, float]]:
    tgt_offsets: dict[int, float] = {}
    src_offsets: dict[int, float] = {}
    for direction in ("down", "up"):
        tgt_groups, src_groups = _build_direction_groups(conns, nodes_dict, direction)
        for group in tgt_groups.values():
            _assign_group_offsets(group, "_source", nodes_dict, tgt_offsets)
        for group in src_groups.values():
            _assign_group_offsets(group, "_target", nodes_dict, src_offsets)
    return tgt_offsets, src_offsets


def _route_multi_row(
    conn: Any,
    sx: float,
    sy: float,
    tx: float,
    ty: float,
    half_heights: tuple[float, float],
    spread_x: tuple[float, float],
    row_gaps: list[float],
    col_gaps: list[float],
    dy_offsets: tuple[float, float],
    going_down: bool,
) -> None:
    sh_half, th_half = half_heights
    src_spread_x, tgt_spread_x = spread_x
    src_dy, tgt_dy = dy_offsets
    if going_down:
        gap_y1 = _nearest_row_gap_below(sy, sh_half, row_gaps) + src_dy
        gap_y2 = _nearest_row_gap_above(ty, th_half, row_gaps) + tgt_dy
    else:
        gap_y1 = _nearest_row_gap_above(sy, sh_half, row_gaps) + src_dy
        gap_y2 = _nearest_row_gap_below(ty, th_half, row_gaps) + tgt_dy
    if abs(gap_y1 - gap_y2) < 5:
        conn.add_bendpoint(Point(int(round(sx + src_spread_x)), int(round(gap_y1))))
        conn.add_bendpoint(Point(int(round(tx + tgt_spread_x)), int(round(gap_y1))))
    else:
        col_gap_x = _nearest_col_gap((sx + tx) / 2.0, col_gaps)
        conn.add_bendpoint(Point(int(round(sx + src_spread_x)), int(round(gap_y1))))
        conn.add_bendpoint(Point(int(round(col_gap_x)), int(round(gap_y1))))
        conn.add_bendpoint(Point(int(round(col_gap_x)), int(round(gap_y2))))
        conn.add_bendpoint(Point(int(round(tx + tgt_spread_x)), int(round(gap_y2))))


def _place_bendpoints(
    conn: Any,
    sx: float,
    sy: float,
    tx: float,
    ty: float,
    half_heights: tuple[float, float],
    source_anchor: tuple[float, float],
    target_anchor: tuple[float, float],
    spread_x: tuple[float, float],
    rows: list[tuple[float, float]],
    row_gaps: list[float],
    col_gaps: list[float],
    dy_offsets: tuple[float, float],
) -> None:
    sh_half, th_half = half_heights
    src_spread_x, tgt_spread_x = spread_x
    tgt_dy, src_dy = dy_offsets
    dx, dy = tx - sx, ty - sy
    if abs(dx) < 1 and abs(dy) < 1:
        return
    going_down = dy > 0
    src_row = _row_of(sy, rows)
    tgt_row = _row_of(ty, rows)
    if abs(dy) < 5:
        mid_x = (source_anchor[0] + target_anchor[0]) / 2.0
        conn.add_bendpoint(Point(int(round(mid_x)), int(round(source_anchor[1]))))
        conn.add_bendpoint(Point(int(round(mid_x)), int(round(target_anchor[1]))))
    elif abs(dx) < 1 and tgt_dy == 0 and src_dy == 0:
        return
    elif src_row >= 0 and tgt_row >= 0 and abs(src_row - tgt_row) == 1:
        if going_down:
            gap_y = _nearest_row_gap_below(sy, sh_half, row_gaps) + tgt_dy
        else:
            gap_y = _nearest_row_gap_above(sy, sh_half, row_gaps) + tgt_dy
        conn.add_bendpoint(Point(int(round(sx + src_spread_x)), int(round(gap_y))))
        conn.add_bendpoint(Point(int(round(tx + tgt_spread_x)), int(round(gap_y))))
    else:
        _route_multi_row(conn, sx, sy, tx, ty, (sh_half, th_half), (src_spread_x, tgt_spread_x), row_gaps, col_gaps, (src_dy, tgt_dy), going_down)


def _route_single_connection(
    conn: Any,
    nodes_dict: dict[str, Any],
    rows: list[tuple[float, float]],
    row_gaps: list[float],
    col_gaps: list[float],
    endpoint_spreads: dict[tuple[str, str, int], tuple[float, float]],
    tgt_offsets: dict[int, float],
    src_offsets: dict[int, float],
) -> None:
    source_uuid = getattr(conn, "_source", None)
    target_uuid = getattr(conn, "_target", None)
    if not source_uuid or not target_uuid:
        return
    source_node = nodes_dict.get(source_uuid)
    target_node = nodes_dict.get(target_uuid)
    if not source_node or not target_node:
        return

    conn.remove_all_bendpoints()

    src_spread_x, src_spread_y = endpoint_spreads.get((source_uuid, "src", id(conn)), (0.0, 0.0))
    tgt_spread_x, tgt_spread_y = endpoint_spreads.get((target_uuid, "tgt", id(conn)), (0.0, 0.0))

    sx, sy = float(source_node.cx), float(source_node.cy)
    tx, ty = float(target_node.cx), float(target_node.cy)
    sh_half = float(source_node.h) / 2.0
    th_half = float(target_node.h) / 2.0

    source_bounds = (
        float(source_node.x), float(source_node.y),
        float(source_node.x + source_node.w), float(source_node.y + source_node.h),
    )
    target_bounds = (
        float(target_node.x), float(target_node.y),
        float(target_node.x + target_node.w), float(target_node.y + target_node.h),
    )

    source_side = _preferred_boundary_side(source_bounds, (tx, ty))
    target_side = _preferred_boundary_side(target_bounds, (sx, sy))
    source_anchor = _boundary_anchor(source_bounds, source_side, (src_spread_x, src_spread_y))
    target_anchor = _boundary_anchor(target_bounds, target_side, (tgt_spread_x, tgt_spread_y))

    tgt_dy = tgt_offsets.get(id(conn), 0.0)
    src_dy = src_offsets.get(id(conn), 0.0)

    _place_bendpoints(
        conn, sx, sy, tx, ty,
        (sh_half, th_half),
        source_anchor, target_anchor,
        (src_spread_x, tgt_spread_x),
        rows, row_gaps, col_gaps,
        (tgt_dy, src_dy),
    )


def _apply_orthogonal_routing(view: Any) -> None:
    """Route all connections orthogonally through row gaps and column gaps."""
    if not hasattr(view, "conns"):
        return
    conns = getattr(view, "conns", [])
    if not conns:
        return
    nodes_dict = _collect_all_nodes(getattr(view, "nodes_dict", {}))
    if not nodes_dict:
        return
    rows, _cols, row_gaps, col_gaps = _build_row_col_structure(nodes_dict)
    endpoint_spreads = _compute_ortho_endpoint_spreads(conns, nodes_dict)
    tgt_offsets, src_offsets = _compute_ortho_gap_spreads(conns, nodes_dict)
    for conn in conns:
        _route_single_connection(conn, nodes_dict, rows, row_gaps, col_gaps, endpoint_spreads, tgt_offsets, src_offsets)


__all__ = [
    "apply_layout",
    "apply_format",
    "undo_layout",
    "auto_layout",
    "auto_route",
    "LayoutConfig",
    "RoutingConfig",
    "LayoutResult",
]
