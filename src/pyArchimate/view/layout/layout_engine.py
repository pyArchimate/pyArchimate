"""Pure node-arrangement logic: layer classification, grid snapping, collision resolution."""

from __future__ import annotations

from typing import Any

from .routing.layer_constraints import ArchiMateLayer

# Extended layer priority map including all ArchiMate layers
_LAYER_PRIORITY: dict[str, int] = {
    "motivation": 0,
    "business": 1,
    "application": 2,
    "technology": 3,
    "physical": 4,
    "implementation": 5,
    "migration": 5,
}

_ROWS_PER_LAYER = 3  # max nodes per row within a layer band before wrapping


def get_layer_priority(element_type: str) -> int:
    """Return layer priority (0=topmost) for an ArchiMate element type string."""
    if not element_type:
        return 6
    layer = ArchiMateLayer.from_archimate_type(element_type)
    order = layer.layer_order()
    # Remap ArchiMateLayer.OTHER (3) to priority 6 to leave room for physical/implementation
    return order if order < 3 else 6


def assign_grid_cells(
    nodes: list[Any],
    grid_size: float,
    layer_direction: str,
    max_cols: int = 8,
) -> dict[str, tuple[int, int]]:
    """Assign each node a (col, row) grid cell with collision-free row-major placement.

    Nodes are grouped by layer priority (ascending), then placed in rows within each layer band.
    When two nodes would occupy the same cell, the second advances in row-major order.

    Args:
        nodes: List of node objects with .uuid and .type attributes.
        grid_size: Size of each grid cell in pixels.
        layer_direction: "vertical" (layers stack top-to-bottom) or "horizontal" (left-to-right).
        max_cols: Maximum nodes per row within a layer band.

    Returns:
        Dict mapping node UUID to (col, row) cell coordinate.
    """
    # Group nodes by layer priority
    groups: dict[int, list[Any]] = {}
    for node in nodes:
        prio = get_layer_priority(getattr(node, 'type', '') or '')
        groups.setdefault(prio, []).append(node)

    assignments: dict[str, tuple[int, int]] = {}
    occupied: set[tuple[int, int]] = set()

    if layer_direction == "vertical":
        # Layers stack top-to-bottom; each layer band starts at a new row
        current_row = 0
        for prio in sorted(groups.keys()):
            layer_nodes = groups[prio]
            col = 0
            band_start_row = current_row
            band_max_row = band_start_row
            for node in layer_nodes:
                nid = getattr(node, 'uuid', None) or getattr(node, 'id', None) or str(id(node))
                cell = _next_free_cell_row_major(col, current_row, occupied, max_cols, band_start_row)
                assignments[nid] = cell
                occupied.add(cell)
                col = cell[0] + 1
                if col >= max_cols:
                    col = 0
                    current_row = cell[1] + 1
                band_max_row = max(band_max_row, cell[1])
            current_row = band_max_row + 2  # leave one empty row between layers
    else:
        # Horizontal: layers stack left-to-right; each layer band starts at a new column
        current_col = 0
        for prio in sorted(groups.keys()):
            layer_nodes = groups[prio]
            row = 0
            band_start_col = current_col
            band_max_col = band_start_col
            for node in layer_nodes:
                nid = getattr(node, 'uuid', None) or getattr(node, 'id', None) or str(id(node))
                cell = _next_free_cell_col_major(current_col, row, occupied, max_cols, band_start_col)
                assignments[nid] = cell
                occupied.add(cell)
                row = cell[1] + 1
                if row >= max_cols:
                    row = 0
                    current_col = cell[0] + 1
                band_max_col = max(band_max_col, cell[0])
            current_col = band_max_col + 2  # leave one empty column between layers

    return assignments


def _next_free_cell_row_major(
    start_col: int,
    start_row: int,
    occupied: set[tuple[int, int]],
    max_cols: int,
    band_start_row: int,
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
    band_start_col: int,
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
        nid = getattr(node, 'uuid', None) or getattr(node, 'id', None) or str(id(node))
        cell = cell_assignments.get(nid)
        if cell is None:
            continue
        col, row = cell
        node.x = int(margin + col * grid_size)
        node.y = int(margin + row * grid_size)
