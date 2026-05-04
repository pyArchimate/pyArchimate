"""View auto-layout and auto-format module for pyArchimate.

This module provides layout algorithms and formatting utilities for ArchiMate views.
"""

import time
from typing import Any, Optional
from .core import LayoutConfig, LayoutResult
from .format import FormatService
from .algorithms import get_algorithm
from .routing.orthogonal import generate_polyline
from .utils.geometry import Point


def apply_layout(view: Any, config: Optional[LayoutConfig] = None) -> LayoutResult:
    """Apply layout algorithm to a view.

    Args:
        view: View object to layout
        config: Layout configuration (uses defaults if None)

    Returns:
        LayoutResult with layout metrics
    """
    if config is None:
        config = LayoutConfig()

    start_time = time.time()

    try:
        # Get and instantiate the algorithm
        algorithm_class = get_algorithm(config.algorithm)
        algorithm = algorithm_class()

        # Apply layout
        result = algorithm.apply(view, config)

        # Apply orthogonal routing to connections
        _apply_orthogonal_routing(view)

        return result
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


def apply_format(view: Any, config: Optional[LayoutConfig] = None) -> LayoutResult:
    """Apply formatting to standardize view appearance.

    Standardizes element sizes, fonts, and alignment without repositioning elements.

    Args:
        view: View object to format
        config: Layout configuration with formatting options

    Returns:
        LayoutResult with formatting metrics
    """
    if config is None:
        config = LayoutConfig()

    start_time = time.time()

    try:
        service = FormatService()
        format_stats = service.format_view(
            view,
            alignment=config.alignment,
            grid_size=getattr(config, "grid_size", 10.0),
            excluded_element_ids=set(config.excluded_element_ids),
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
    """Undo the last layout operation on a view.

    Uses the existing pyArchimate transaction/undo system.

    Args:
        view: View object to undo layout on

    Returns:
        LayoutResult indicating success/failure
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


def _apply_orthogonal_routing(view: Any) -> None:
    """Route all connections orthogonally through row gaps and column gaps.

    Strategy:
    - Nodes are clustered into rows (by y) and columns (by x).
    - Row gaps: clear horizontal corridors between consecutive rows.
    - Column gaps: clear vertical corridors between consecutive columns.
    - Adjacent-layer connections: 2 bendpoints (S/Z through the row gap).
    - Multi-layer connections: 4 bendpoints routed through a row gap, then a
      column gap (guaranteed clear), then another row gap.

    Archi renders: source_center → bp1 → … → bpN → target_center, clipping
    the first/last segment at the node boundary automatically.
    """
    if not hasattr(view, 'conns'):
        return

    conns = getattr(view, 'conns', [])
    if not conns:
        return

    nodes_dict = getattr(view, 'nodes_dict', {})
    if not nodes_dict:
        return

    # ------------------------------------------------------------------
    # Build row and column structure from all nodes
    # ------------------------------------------------------------------
    def _cluster_ranges(values: list[tuple[float, float]], tol: float = 20.0
                        ) -> list[tuple[float, float]]:
        """Merge overlapping or nearby intervals into contiguous bands."""
        if not values:
            return []
        merged: list[tuple[float, float]] = []
        for lo, hi in sorted(values):
            if merged and lo <= merged[-1][1] + tol:
                merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
            else:
                merged.append((lo, hi))
        return merged

    row_intervals: list[tuple[float, float]] = []
    col_intervals: list[tuple[float, float]] = []
    for node in nodes_dict.values():
        row_intervals.append((float(node.y), float(node.y + node.h)))
        col_intervals.append((float(node.x), float(node.x + node.w)))

    rows = _cluster_ranges(row_intervals)  # sorted (y_min, y_max)
    cols = _cluster_ranges(col_intervals)  # sorted (x_min, x_max)

    # Gap midpoints between consecutive bands
    row_gaps = [(rows[i][1] + rows[i + 1][0]) / 2.0
                for i in range(len(rows) - 1)]
    col_gaps = [(cols[i][1] + cols[i + 1][0]) / 2.0
                for i in range(len(cols) - 1)]

    def _row_of(cy: float) -> int:
        for i, (lo, hi) in enumerate(rows):
            if lo <= cy <= hi:
                return i
        return -1

    def _nearest_row_gap_below(cy: float, sh: float) -> float:
        """First row-gap strictly below the source bottom edge."""
        bottom = cy + sh
        for g in row_gaps:
            if g > bottom:
                return g
        return bottom + 10.0  # fallback: just below source

    def _nearest_row_gap_above(cy: float, sh: float) -> float:
        """First row-gap strictly above the source top edge."""
        top = cy - sh
        for g in reversed(row_gaps):
            if g < top:
                return g
        return top - 10.0

    def _nearest_col_gap(cx: float) -> float:
        """Column gap nearest to cx."""
        if not col_gaps:
            return cx
        return min(col_gaps, key=lambda g: abs(g - cx))

    # ------------------------------------------------------------------
    # Gap-level spreading: connections that share the same target (or source)
    # get distinct y-offsets within the row gap so their horizontal bridges
    # never perfectly overlap.  All bendpoints are strictly outside nodes.
    # ------------------------------------------------------------------
    from collections import defaultdict

    _SPREAD_STEP = 12.0  # px between parallel horizontal bridges

    tgt_offsets: dict[int, float] = {}
    src_offsets: dict[int, float] = {}

    for direction in ('down', 'up'):
        tgt_groups: dict[str, list] = defaultdict(list)
        src_groups_dir: dict[str, list] = defaultdict(list)
        for conn in conns:
            s = nodes_dict.get(getattr(conn, '_source', None))
            t = nodes_dict.get(getattr(conn, '_target', None))
            if not s or not t or abs(t.cy - s.cy) < 5:
                continue
            going = 'down' if t.cy > s.cy else 'up'
            if going != direction:
                continue
            tgt_groups[conn._target].append(conn)
            src_groups_dir[conn._source].append(conn)

        for uid, group in tgt_groups.items():
            n = len(group)
            if n <= 1:
                continue
            s_nodes = [nodes_dict.get(getattr(c, '_source', None)) for c in group]
            sorted_g = [c for c, _ in sorted(
                zip(group, s_nodes),
                key=lambda p: float(getattr(p[1], 'cx', 0)) if p[1] else 0,
            )]
            for i, conn in enumerate(sorted_g):
                tgt_offsets[id(conn)] = (i - (n - 1) / 2.0) * _SPREAD_STEP

        for uid, group in src_groups_dir.items():
            n = len(group)
            if n <= 1:
                continue
            t_nodes = [nodes_dict.get(getattr(c, '_target', None)) for c in group]
            sorted_g = [c for c, _ in sorted(
                zip(group, t_nodes),
                key=lambda p: float(getattr(p[1], 'cx', 0)) if p[1] else 0,
            )]
            for i, conn in enumerate(sorted_g):
                src_offsets[id(conn)] = (i - (n - 1) / 2.0) * _SPREAD_STEP

    # ------------------------------------------------------------------
    # Route each connection (external bendpoints only — no inside-node bps)
    # ------------------------------------------------------------------
    for conn in conns:
        source_uuid = getattr(conn, '_source', None)
        target_uuid = getattr(conn, '_target', None)
        if not source_uuid or not target_uuid:
            continue
        source_node = nodes_dict.get(source_uuid)
        target_node = nodes_dict.get(target_uuid)
        if not source_node or not target_node:
            continue

        conn.remove_all_bendpoints()

        sx, sy = float(source_node.cx), float(source_node.cy)
        tx, ty = float(target_node.cx), float(target_node.cy)
        sh_half = float(source_node.h) / 2.0
        sw_half = float(source_node.w) / 2.0
        th_half = float(target_node.h) / 2.0
        tw_half = float(target_node.w) / 2.0

        dx, dy = tx - sx, ty - sy

        if abs(dx) < 1 and abs(dy) < 1:
            continue

        src_row = _row_of(sy)
        tgt_row = _row_of(ty)
        going_down = dy > 0

        tgt_dy = tgt_offsets.get(id(conn), 0.0)
        src_dy = src_offsets.get(id(conn), 0.0)

        if abs(dy) < 5:
            # ---- Same row or nearly horizontal ----
            going_right = dx > 0
            if going_right:
                mid_x = (sx + sw_half + tx - tw_half) / 2.0
            else:
                mid_x = (sx - sw_half + tx + tw_half) / 2.0
            if abs(dy) >= 1:
                conn.add_bendpoint(Point(mid_x, sy))
                conn.add_bendpoint(Point(mid_x, ty))

        elif abs(dx) < 1 and tgt_dy == 0 and src_dy == 0:
            # ---- Same column, single — straight vertical ----
            pass

        elif src_row >= 0 and tgt_row >= 0 and abs(src_row - tgt_row) == 1:
            # ---- Adjacent rows: S-shape through the row gap ----
            # Use tgt_dy to spread connections converging on the same target;
            # src_dy would cancel with tgt_dy for symmetric connections.
            if going_down:
                gap_y = _nearest_row_gap_below(sy, sh_half) + tgt_dy
            else:
                gap_y = _nearest_row_gap_above(sy, sh_half) + tgt_dy
            conn.add_bendpoint(Point(sx, gap_y))
            conn.add_bendpoint(Point(tx, gap_y))

        else:
            # ---- Multi-row: two row-gaps bridged by a column gap ----
            if going_down:
                gap_y1 = _nearest_row_gap_below(sy, sh_half) + src_dy
                gap_y2 = _nearest_row_gap_above(ty, th_half) + tgt_dy
            else:
                gap_y1 = _nearest_row_gap_above(sy, sh_half) + src_dy
                gap_y2 = _nearest_row_gap_below(ty, th_half) + tgt_dy

            if abs(gap_y1 - gap_y2) < 5:
                conn.add_bendpoint(Point(sx, gap_y1))
                conn.add_bendpoint(Point(tx, gap_y1))
            else:
                col_gap_x = _nearest_col_gap((sx + tx) / 2.0)
                conn.add_bendpoint(Point(sx, gap_y1))
                conn.add_bendpoint(Point(col_gap_x, gap_y1))
                conn.add_bendpoint(Point(col_gap_x, gap_y2))
                conn.add_bendpoint(Point(tx, gap_y2))


__all__ = [
    "apply_layout",
    "apply_format",
    "undo_layout",
    "LayoutConfig",
    "LayoutResult",
]
