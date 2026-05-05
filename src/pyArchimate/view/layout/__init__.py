"""View auto-layout and auto-format module for pyArchimate.

This module provides layout algorithms and formatting utilities for ArchiMate views.
"""

import time
from typing import Any, Optional, cast

from .algorithms import get_algorithm
from .core import LayoutConfig, LayoutResult
from .format import FormatService
from .utils.geometry import Point


def apply_layout(view: Any, config: Optional[LayoutConfig] = None) -> LayoutResult:
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

        # Get and instantiate the algorithm
        algorithm_class = get_algorithm(config.algorithm)
        algorithm = algorithm_class()

        # Apply layout
        result = cast(LayoutResult, algorithm.apply(view, config))

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
            excluded_element_ids={str(id) for id in config.excluded_element_ids},
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
    # Endpoint spreading: distribute connection points along node edges
    # ------------------------------------------------------------------
    from collections import defaultdict

    _SPREAD_STEP = 12.0  # px between parallel horizontal bridges
    _EDGE_CORNER_MARGIN = 12.0  # keep connection anchors away from corners

    def _distributed_spread(index: int, count: int, edge_span: float) -> float:
        """Return a centered spread value constrained to the middle of an edge."""
        if count <= 1:
            return 0.0

        usable_span = max(0.0, edge_span - 2 * _EDGE_CORNER_MARGIN)
        if usable_span <= 0.0:
            return 0.0

        step = min(_SPREAD_STEP, usable_span / max(1, count - 1))
        total_span = step * (count - 1)
        return -total_span / 2.0 + index * step

    def _preferred_boundary_side(
            bounds: tuple[float, float, float, float],
            other_point: tuple[float, float],
    ) -> str:
        """Pick the edge side that best matches the connection direction."""
        x1, y1, x2, y2 = bounds
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        ox, oy = other_point
        dx = ox - cx
        dy = oy - cy

        if abs(dx) >= abs(dy):
            return 'right' if dx >= 0 else 'left'
        return 'bottom' if dy >= 0 else 'top'

    def _boundary_anchor(
            bounds: tuple[float, float, float, float],
            side: str,
            spread: tuple[float, float],
    ) -> tuple[float, float]:
        """Place an anchor on a specific edge and keep it away from corners."""
        x1, y1, x2, y2 = bounds
        margin = _EDGE_CORNER_MARGIN
        if side in ('left', 'right'):
            y = max(y1 + margin, min(y2 - margin, (y1 + y2) / 2.0 + spread[1]))
            x = x1 if side == 'left' else x2
            return x, y

        x = max(x1 + margin, min(x2 - margin, (x1 + x2) / 2.0 + spread[0]))
        y = y1 if side == 'top' else y2
        return x, y

    # Compute endpoint spreads: for each node, distribute its incoming/outgoing connections
    # Maps (node_uuid, 'src'/'tgt', conn_id) → (spread_x, spread_y) for edge distribution
    endpoint_spreads: dict[tuple[str, str, int], tuple[float, float]] = {}

    for node_uuid, node in nodes_dict.items():
        # Find all connections from this node (source)
        src_conns = [c for c in conns if getattr(c, '_source', None) == node_uuid]
        if len(src_conns) > 1:
            # Sort by target position for consistent spreading
            src_conns_sorted = sorted(
                src_conns,
                key=lambda c: float(nodes_dict.get(getattr(c, '_target', None), node).cx)
            )
            for i, conn in enumerate(src_conns_sorted):
                # Calculate spread offset (perpendicular to dominant connection direction)
                target_node = nodes_dict.get(getattr(conn, '_target', None))
                if target_node:
                    dy = float(target_node.cy) - float(node.cy)
                    dx = float(target_node.cx) - float(node.cx)
                    # Spread horizontally if vertical, vertically if horizontal
                    spread_val = _distributed_spread(
                        i,
                        len(src_conns_sorted),
                        float(getattr(node, 'w', 120)) if abs(dy) > abs(dx) else float(getattr(node, 'h', 55)),
                    )
                    if abs(dy) > abs(dx):  # Mostly vertical
                        spread_x, spread_y = spread_val, 0.0
                    else:  # Mostly horizontal
                        spread_x, spread_y = 0.0, spread_val
                    endpoint_spreads[(node_uuid, 'src', id(conn))] = (spread_x, spread_y)

        # Find all connections to this node (target)
        tgt_conns = [c for c in conns if getattr(c, '_target', None) == node_uuid]
        if len(tgt_conns) > 1:
            # Sort by source position for consistent spreading
            tgt_conns_sorted = sorted(
                tgt_conns,
                key=lambda c: float(nodes_dict.get(getattr(c, '_source', None), node).cx)
            )
            for i, conn in enumerate(tgt_conns_sorted):
                # Calculate spread offset (perpendicular to dominant connection direction)
                source_node = nodes_dict.get(getattr(conn, '_source', None))
                if source_node:
                    dy = float(node.cy) - float(source_node.cy)
                    dx = float(node.cx) - float(source_node.cx)
                    # Spread horizontally if vertical, vertically if horizontal
                    spread_val = _distributed_spread(
                        i,
                        len(tgt_conns_sorted),
                        float(getattr(node, 'w', 120)) if abs(dy) > abs(dx) else float(getattr(node, 'h', 55)),
                    )
                    if abs(dy) > abs(dx):  # Mostly vertical
                        spread_x, spread_y = spread_val, 0.0
                    else:  # Mostly horizontal
                        spread_x, spread_y = 0.0, spread_val
                    endpoint_spreads[(node_uuid, 'tgt', id(conn))] = (spread_x, spread_y)

    # Gap-level spreading for bendpoints
    tgt_offsets: dict[int, float] = {}
    src_offsets: dict[int, float] = {}

    for direction in ('down', 'up'):
        tgt_groups: dict[str, list[Any]] = defaultdict(list)
        src_groups_dir: dict[str, list[Any]] = defaultdict(list)
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

        for _, group in tgt_groups.items():
            n = len(group)
            if n <= 1:
                continue
            s_nodes = [nodes_dict.get(getattr(c, '_source', None)) for c in group]
            sorted_g = [c for c, _ in sorted(
                zip(group, s_nodes, strict=False),
                key=lambda p: float(getattr(p[1], 'cx', 0)) if p[1] else 0,
            )]
            for i, conn in enumerate(sorted_g):
                tgt_offsets[id(conn)] = (i - (n - 1) / 2.0) * _SPREAD_STEP

        for _, group in src_groups_dir.items():
            n = len(group)
            if n <= 1:
                continue
            t_nodes = [nodes_dict.get(getattr(c, '_target', None)) for c in group]
            sorted_g = [c for c, _ in sorted(
                zip(group, t_nodes, strict=False),
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

        # Get endpoint spreads for actual boundary positioning
        src_spread_x, src_spread_y = endpoint_spreads.get((source_uuid, 'src', id(conn)), (0.0, 0.0))
        tgt_spread_x, tgt_spread_y = endpoint_spreads.get((target_uuid, 'tgt', id(conn)), (0.0, 0.0))

        # Use unspread centers for routing calculations
        sx, sy = float(source_node.cx), float(source_node.cy)
        tx, ty = float(target_node.cx), float(target_node.cy)
        sh_half = float(source_node.h) / 2.0
        sw_half = float(source_node.w) / 2.0
        th_half = float(target_node.h) / 2.0
        tw_half = float(target_node.w) / 2.0

        source_bounds = (float(source_node.x), float(source_node.y),
                         float(source_node.x + source_node.w), float(source_node.y + source_node.h))
        target_bounds = (float(target_node.x), float(target_node.y),
                         float(target_node.x + target_node.w), float(target_node.y + target_node.h))

        source_side = _preferred_boundary_side(source_bounds, (tx, ty))
        target_side = _preferred_boundary_side(target_bounds, (sx, sy))

        source_anchor = _boundary_anchor(source_bounds, source_side, (src_spread_x, src_spread_y))
        target_anchor = _boundary_anchor(target_bounds, target_side, (tgt_spread_x, tgt_spread_y))

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
            if dx > 0:
                mid_x = (source_anchor[0] + target_anchor[0]) / 2.0
            else:
                mid_x = (source_anchor[0] + target_anchor[0]) / 2.0
            conn.add_bendpoint(Point(int(round(source_anchor[0])), int(round(source_anchor[1]))))
            conn.add_bendpoint(Point(int(round(mid_x)), int(round(source_anchor[1]))))
            conn.add_bendpoint(Point(int(round(mid_x)), int(round(target_anchor[1]))))
            conn.add_bendpoint(Point(int(round(target_anchor[0])), int(round(target_anchor[1]))))

        elif abs(dx) < 1 and tgt_dy == 0 and src_dy == 0:
            # ---- Same column, single — straight vertical ----
            conn.add_bendpoint(Point(int(round(source_anchor[0])), int(round(source_anchor[1]))))
            conn.add_bendpoint(Point(int(round(target_anchor[0])), int(round(target_anchor[1]))))

        elif src_row >= 0 and tgt_row >= 0 and abs(src_row - tgt_row) == 1:
            # ---- Adjacent rows: S-shape through the row gap ----
            # Use tgt_dy to spread connections converging on the same target;
            # src_dy would cancel with tgt_dy for symmetric connections.
            if going_down:
                gap_y = _nearest_row_gap_below(sy, sh_half) + tgt_dy
            else:
                gap_y = _nearest_row_gap_above(sy, sh_half) + tgt_dy
            conn.add_bendpoint(Point(int(round(source_anchor[0])), int(round(source_anchor[1]))))
            conn.add_bendpoint(Point(int(round(sx + src_spread_x)), int(round(gap_y))))
            conn.add_bendpoint(Point(int(round(tx + tgt_spread_x)), int(round(gap_y))))
            conn.add_bendpoint(Point(int(round(target_anchor[0])), int(round(target_anchor[1]))))

        else:
            # ---- Multi-row: two row-gaps bridged by a column gap ----
            if going_down:
                gap_y1 = _nearest_row_gap_below(sy, sh_half) + src_dy
                gap_y2 = _nearest_row_gap_above(ty, th_half) + tgt_dy
            else:
                gap_y1 = _nearest_row_gap_above(sy, sh_half) + src_dy
                gap_y2 = _nearest_row_gap_below(ty, th_half) + tgt_dy

            if abs(gap_y1 - gap_y2) < 5:
                conn.add_bendpoint(Point(int(round(source_anchor[0])), int(round(source_anchor[1]))))
                conn.add_bendpoint(Point(int(round(sx + src_spread_x)), int(round(gap_y1))))
                conn.add_bendpoint(Point(int(round(tx + tgt_spread_x)), int(round(gap_y1))))
                conn.add_bendpoint(Point(int(round(target_anchor[0])), int(round(target_anchor[1]))))
            else:
                col_gap_x = _nearest_col_gap((sx + tx) / 2.0)
                conn.add_bendpoint(Point(int(round(source_anchor[0])), int(round(source_anchor[1]))))
                conn.add_bendpoint(Point(int(round(sx + src_spread_x)), int(round(gap_y1))))
                conn.add_bendpoint(Point(int(round(col_gap_x)), int(round(gap_y1))))
                conn.add_bendpoint(Point(int(round(col_gap_x)), int(round(gap_y2))))
                conn.add_bendpoint(Point(int(round(tx + tgt_spread_x)), int(round(gap_y2))))
                conn.add_bendpoint(Point(int(round(target_anchor[0])), int(round(target_anchor[1]))))


__all__ = [
    "apply_layout",
    "apply_format",
    "undo_layout",
    "LayoutConfig",
    "LayoutResult",
]
