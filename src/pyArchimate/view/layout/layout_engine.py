"""Pure node-arrangement logic: layer classification, grid snapping, collision resolution."""

from __future__ import annotations

from typing import Any

from .routing.layer_constraints import ArchiMateLayer


def get_layer_priority(element_type: str) -> int:
    """Return layer priority (0=topmost) for an ArchiMate element type string."""
    if not element_type:
        return 6
    layer = ArchiMateLayer.from_archimate_type(element_type)
    order = layer.layer_order()
    # Remap ArchiMateLayer.OTHER (3) to priority 6 to leave room for physical/implementation
    return order if order < 3 else 6


def _place_node_vertical(
    nid: str,
    is_high: bool,
    col: int,
    current_row: int,
    occupied: set[tuple[int, int]],
    assignments: dict[str, tuple[int, int]],
    max_cols: int,
) -> tuple[int, int, int]:
    """Place one node in vertical mode; return (new_col, new_current_row, cell_row)."""
    if is_high:
        if col > 0:
            col += 1  # gap before high-degree node
        cell = _next_free_cell_row_major(col, current_row, occupied, max_cols)
        assignments[nid] = cell
        occupied.add(cell)
        occupied.add((cell[0] + 1, cell[1]))  # isolation pad on right
        col = cell[0] + 2
    else:
        cell = _next_free_cell_row_major(col, current_row, occupied, max_cols)
        assignments[nid] = cell
        occupied.add(cell)
        col = cell[0] + 1
    if col >= max_cols:
        col = 0
        current_row = cell[1] + 1
    return col, current_row, cell[1]


def _assign_vertical_band(
    layer_nodes: list[Any],
    current_row: int,
    occupied: set[tuple[int, int]],
    assignments: dict[str, tuple[int, int]],
    max_cols: int,
    _degrees: dict[str, int],
    high_degree_threshold: int,
) -> int:
    """Place one layer band vertically; return the next available row after this band."""
    col = 0
    band_max_row = current_row
    for node in layer_nodes:
        nid = getattr(node, "uuid", None) or getattr(node, "id", None) or str(id(node))
        is_high = _degrees.get(nid, 0) >= high_degree_threshold
        col, current_row, row = _place_node_vertical(nid, is_high, col, current_row, occupied, assignments, max_cols)
        band_max_row = max(band_max_row, row)
    return band_max_row + 2  # leave one empty row between layers


def _assign_horizontal_band(
    layer_nodes: list[Any],
    current_col: int,
    occupied: set[tuple[int, int]],
    assignments: dict[str, tuple[int, int]],
    max_cols: int,
) -> int:
    """Place one layer band horizontally; return the next available column after this band."""
    row = 0
    band_max_col = current_col
    for node in layer_nodes:
        nid = getattr(node, "uuid", None) or getattr(node, "id", None) or str(id(node))
        cell = _next_free_cell_col_major(current_col, row, occupied, max_cols)
        assignments[nid] = cell
        occupied.add(cell)
        row = cell[1] + 1
        if row >= max_cols:
            row = 0
            current_col = cell[0] + 1
        band_max_col = max(band_max_col, cell[0])
    return band_max_col + 2  # leave one empty column between layers


def assign_grid_cells(
    nodes: list[Any],
    layer_direction: str,
    max_cols: int = 8,
    node_degrees: dict[str, int] | None = None,
    high_degree_threshold: int = 5,
) -> dict[str, tuple[int, int]]:
    """Assign each node a (col, row) grid cell with collision-free row-major placement.

    Nodes are grouped by layer priority (ascending), then placed in rows within each layer band.
    High-degree nodes (degree >= high_degree_threshold) receive 1-cell isolation padding on
    each horizontal side within their row, reducing routing bottlenecks (RQ-06).

    Args:
        nodes: List of node objects with .uuid and .type attributes.
        layer_direction: "vertical" (layers stack top-to-bottom) or "horizontal" (left-to-right).
        max_cols: Maximum nodes per row within a layer band.
        node_degrees: Dict mapping node UUID to connection degree. None = no isolation.
        high_degree_threshold: Min degree to qualify for row isolation (default 5).

    Returns:
        Dict mapping node UUID to (col, row) cell coordinate.
    """
    _degrees = node_degrees or {}

    # Group nodes by layer priority
    groups: dict[int, list[Any]] = {}
    for node in nodes:
        prio = get_layer_priority(getattr(node, "type", "") or "")
        groups.setdefault(prio, []).append(node)

    assignments: dict[str, tuple[int, int]] = {}
    occupied: set[tuple[int, int]] = set()

    if layer_direction == "vertical":
        current_row = 0
        for prio in sorted(groups.keys()):
            current_row = _assign_vertical_band(
                groups[prio], current_row, occupied, assignments, max_cols, _degrees, high_degree_threshold
            )
    else:
        current_col = 0
        for prio in sorted(groups.keys()):
            current_col = _assign_horizontal_band(groups[prio], current_col, occupied, assignments, max_cols)

    return assignments


def _next_free_cell_row_major(
    start_col: int,
    start_row: int,
    occupied: set[tuple[int, int]],
    max_cols: int,
) -> tuple[int, int]:
    """Find next free cell starting from (start_col, start_row), advancing row-major."""
    col, row = start_col % max_cols, start_row
    while True:
        cell = (col, row)
        if cell not in occupied:
            return cell
        col += 1
        if col >= max_cols:
            col = 0
            row += 1


def _next_free_cell_col_major(
    start_col: int,
    start_row: int,
    occupied: set[tuple[int, int]],
    max_rows: int,
) -> tuple[int, int]:
    """Find next free cell starting from (start_col, start_row), advancing column-major."""
    col, row = start_col, start_row % max_rows
    while True:
        cell = (col, row)
        if cell not in occupied:
            return cell
        row += 1
        if row >= max_rows:
            row = 0
            col += 1


def apply_node_positions(
    view: Any,
    cell_assignments: dict[str, tuple[int, int]],
    grid_size: float,
    margin: float,
) -> None:
    """Write (x, y) to each node from grid cell assignments.

    Only modifies x and y. Width and height are never changed (FR-006).
    """
    for node in view.nodes:
        nid = getattr(node, "uuid", None) or getattr(node, "id", None) or str(id(node))
        cell = cell_assignments.get(nid)
        if cell is None:
            continue
        col, row = cell
        node.x = int(margin + col * grid_size)
        node.y = int(margin + row * grid_size)
