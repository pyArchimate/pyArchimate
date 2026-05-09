"""Orthogonal connection routing for layout operations."""

from typing import Dict, List, Tuple

from ..utils.geometry import Point, Rectangle
from ..utils.graph import detect_crossings


def generate_polyline(
    p_start: Point,
    p_end: Point,
    obstacles: List[Rectangle] | None = None,
    routing_style: str = "orthogonal",
) -> List[Point]:
    """Generate a polyline (path) between two points.

    Args:
        p_start: Starting point
        p_end: Ending point
        obstacles: List of rectangles to avoid (optional)
        routing_style: "orthogonal" (0°/90°) or "mixed_45" (allow ±45° angles)

    Returns:
        List of waypoints forming the polyline
    """
    if obstacles is None:
        obstacles = []

    # Determine if 45-degree angles can be used
    allow_45_degree = routing_style == "mixed_45"

    waypoints = [p_start]

    if allow_45_degree:
        # Mixed routing: try 45-degree angle if it simplifies the path
        dx = abs(p_end.x - p_start.x)
        dy = abs(p_end.y - p_start.y)

        if dx > 0 and dy > 0:
            # Use 45-degree diagonal if roughly equal distances
            if 0.5 < dx / dy < 2.0:
                mid_point = Point(p_end.x, p_start.y)
                waypoints.append(mid_point)
            else:
                # Use orthogonal fallback
                mid_x = (p_start.x + p_end.x) / 2
                mid_point = Point(mid_x, p_start.y)
                waypoints.append(mid_point)
        else:
            # Straight line
            pass
    else:
        # Standard orthogonal routing: horizontal then vertical
        mid_x = (p_start.x + p_end.x) / 2
        mid_point = Point(mid_x, p_start.y)
        waypoints.append(mid_point)

    # Final point
    waypoints.append(p_end)

    return waypoints


def detect_line_crossings(
    line1: Tuple[Point, Point],
    line2: Tuple[Point, Point],
) -> bool:
    """Detect if two line segments cross.

    Args:
        line1: Tuple of (start_point, end_point)
        line2: Tuple of (start_point, end_point)

    Returns:
        True if lines cross, False otherwise
    """
    p1, p2 = line1
    p3, p4 = line2

    return detect_crossings(
        ((p1.x, p1.y), (p2.x, p2.y)),
        ((p3.x, p3.y), (p4.x, p4.y)),
    )


def count_edge_crossings(edges: List[Tuple[Point, Point]]) -> int:
    """Count total number of edge crossings.

    Args:
        edges: List of edges (each edge is tuple of Points)

    Returns:
        Total crossing count
    """
    crossings = 0
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            if detect_line_crossings(edges[i], edges[j]):
                crossings += 1
    return crossings


def _connection_ratio(index: int, count: int) -> float:
    if count > 1:
        return index / (count - 1)
    return 0.5


def spread_connection_endpoints(
    node_positions: Dict[int, Tuple[float, float]],
    node_sizes: Dict[int, Tuple[float, float]],
    connections: List[Tuple[int, int]],
) -> Dict[Tuple[int, int], Tuple[Point, Point]]:
    """Distribute connection endpoints equally around node edges.

    Args:
        node_positions: Dict of node_id -> (x, y) center position
        node_sizes: Dict of node_id -> (width, height)
        connections: List of (source_id, target_id) connections

    Returns:
        Dict mapping (source_id, target_id) to (start_point, end_point)
    """
    endpoints: Dict[Tuple[int, int], Tuple[Point, Point]] = {}

    # Group connections by source and target
    outgoing_per_node: Dict[int, List[int]] = {}
    incoming_per_node: Dict[int, List[int]] = {}

    for source, target in connections:
        if source not in outgoing_per_node:
            outgoing_per_node[source] = []
        outgoing_per_node[source].append(target)

        if target not in incoming_per_node:
            incoming_per_node[target] = []
        incoming_per_node[target].append(source)

    # Calculate endpoint positions
    for source, target in connections:
        source_pos = node_positions.get(source, (0, 0))
        target_pos = node_positions.get(target, (0, 0))
        source_size = node_sizes.get(source, (50, 50))
        target_size = node_sizes.get(target, (50, 50))

        # Get which outgoing connection this is from source
        outgoing_list = outgoing_per_node.get(source, [])
        connection_index = outgoing_list.index(target) if target in outgoing_list else 0
        num_outgoing = len(outgoing_list)

        # Get which incoming connection this is to target
        incoming_list = incoming_per_node.get(target, [])
        incoming_index = incoming_list.index(source) if source in incoming_list else 0
        num_incoming = len(incoming_list)

        # Calculate source endpoint (distribute along right edge)
        source_rect = Rectangle(
            source_pos[0] - source_size[0] / 2,
            source_pos[1] - source_size[1] / 2,
            source_size[0],
            source_size[1],
        )
        ratio = _connection_ratio(connection_index, num_outgoing)
        source_endpoint = Point(
            source_rect.x + source_rect.width,
            source_rect.y + source_rect.height * ratio,
        )

        # Calculate target endpoint (distribute along left edge)
        target_rect = Rectangle(
            target_pos[0] - target_size[0] / 2,
            target_pos[1] - target_size[1] / 2,
            target_size[0],
            target_size[1],
        )
        ratio = _connection_ratio(incoming_index, num_incoming)
        target_endpoint = Point(
            target_rect.x,
            target_rect.y + target_rect.height * ratio,
        )

        endpoints[(source, target)] = (source_endpoint, target_endpoint)

    return endpoints


def apply_barycentric_crossing_reduction(
    node_positions: Dict[int, Tuple[float, float]],
    connections: List[Tuple[int, int]],
    iterations: int = 5,
) -> Dict[int, Tuple[float, float]]:
    """Apply barycentric method to reduce crossing count.

    Args:
        node_positions: Current node positions
        connections: List of connections
        iterations: Number of optimization iterations

    Returns:
        Updated node positions with reduced crossings
    """
    positions = dict(node_positions)

    # Simple barycentric: move nodes toward center of connected nodes
    for _ in range(iterations):
        # Group connections by node
        neighbors: Dict[int, List[int]] = {}
        for source, target in connections:
            if source not in neighbors:
                neighbors[source] = []
            neighbors[source].append(target)

            if target not in neighbors:
                neighbors[target] = []
            neighbors[target].append(source)

        # Move nodes toward neighbors' barycenter
        new_positions = dict(positions)
        for node_id, neighbor_ids in neighbors.items():
            if not neighbor_ids:
                continue

            avg_x = sum(positions[n][0] for n in neighbor_ids if n in positions) / len(neighbor_ids)
            avg_y = sum(positions[n][1] for n in neighbor_ids if n in positions) / len(neighbor_ids)

            # Move partially toward average
            x, y = positions[node_id]
            new_positions[node_id] = (
                x + 0.1 * (avg_x - x),
                y + 0.1 * (avg_y - y),
            )

        positions = new_positions

    return positions
