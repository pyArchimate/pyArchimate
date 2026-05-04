"""Force-directed (Spring-Embedder) layout algorithm for ArchiMate views."""

import math
import random
from typing import Any, Dict, Tuple, List
from ..core import LayoutAlgorithm, LayoutConfig, LayoutResult
from ..utils.geometry import Point, Rectangle
from ..utils.edge_utils import normalize_edges
from ..routing.layer_constraints import LayerConstraint, ArchiMateLayer


class ForceDirectedLayout(LayoutAlgorithm):
    """Force-directed layout using Spring-Embedder physics simulation."""

    def __init__(self) -> None:
        """Initialize force-directed layout."""
        self.k_attraction = 0.01  # Spring attraction constant (very weak)
        self.k_repulsion = 2000.0  # Node repulsion constant - strong repulsion
        self.damping = 0.8  # Velocity damping for stability
        self.tolerance = 0.05  # Convergence tolerance (strict)
        self.max_iterations = 500  # Maximum iterations
        self.max_velocity = 150.0  # Maximum velocity per iteration
        self.min_separation = 200.0  # Minimum distance between nodes (increased from 150)

    def apply(self, view: Any, config: LayoutConfig) -> LayoutResult:
        """Apply force-directed layout to a view.

        Args:
            view: View object with nodes and edges
            config: Layout configuration

        Returns:
            LayoutResult with layout metrics
        """
        import time
        start_time = time.time()

        try:
            # Get nodes and edges from view
            nodes = getattr(view, "nodes", [])
            raw_edges = getattr(view, "conns", []) or getattr(view, "edges", [])
            edges = normalize_edges(raw_edges, nodes)

            if not nodes:
                return LayoutResult(
                    success=True,
                    view_id=getattr(view, "id", "unknown"),
                    algorithm_used="force_directed",
                    elements_processed=0,
                    connections_processed=0,
                    layout_time_ms=(time.time() - start_time) * 1000,
                )

            # Initialize positions and velocities
            positions = self._initialize_positions(nodes, config)
            velocities = {node_id: Point(0, 0) for node_id in positions.keys()}

            # Set up layer constraints
            layer_constraint = LayerConstraint()
            for node_id, node in enumerate(nodes):
                element_type = getattr(node, "type", "unknown")
                layer = ArchiMateLayer.from_archimate_type(element_type)
                layer_constraint.assign_layer(node_id, layer)

            # Adaptive iteration limit based on element count
            max_iter = self._get_iteration_limit(len(nodes))

            # Run physics simulation
            converged = False
            iteration = 0
            for iteration in range(max_iter):
                # Calculate forces
                forces = self._calculate_forces(positions, edges, layer_constraint)

                # Update velocities and positions
                max_velocity = 0.0
                for node_id in positions:
                    if node_id in forces:
                        force = forces[node_id]
                        vx = force.x * self.damping
                        vy = force.y * self.damping

                        # Clamp velocity magnitude to prevent explosion
                        v_mag = math.sqrt(vx * vx + vy * vy)
                        if v_mag > self.max_velocity:
                            scale = self.max_velocity / v_mag
                            vx *= scale
                            vy *= scale

                        velocities[node_id] = Point(vx, vy)
                        positions[node_id] = Point(
                            positions[node_id].x + vx,
                            positions[node_id].y + vy,
                        )
                        max_velocity = max(max_velocity, abs(vx), abs(vy))

                # Check for convergence
                if max_velocity < self.tolerance:
                    converged = True
                    break

            # Resolve any remaining overlaps by pushing nodes apart
            positions = self._resolve_overlaps(positions, nodes)

            # Enforce layer constraints
            positions = layer_constraint.enforce_layer_separation(positions, config.spacing)

            # Store positions back to nodes (simulation)
            for i, node in enumerate(nodes):
                if i in positions:
                    pos = positions[i]
                    node.x = pos.x
                    node.y = pos.y

            elapsed_ms = (time.time() - start_time) * 1000

            return LayoutResult(
                success=True,
                view_id=getattr(view, "id", "unknown"),
                algorithm_used="force_directed",
                elements_processed=len(nodes),
                connections_processed=len(edges),
                layout_time_ms=elapsed_ms,
                quality_metrics={
                    "converged": converged,
                    "iterations": iteration + 1,
                    "max_iterations": max_iter,
                },
            )

        except Exception as e:
            import traceback
            elapsed_ms = (time.time() - start_time) * 1000
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            return LayoutResult(
                success=False,
                view_id=getattr(view, "id", "unknown"),
                algorithm_used="force_directed",
                elements_processed=0,
                connections_processed=0,
                layout_time_ms=elapsed_ms,
                error_message=error_msg,
            )

    def _initialize_positions(self, nodes: list, config: LayoutConfig) -> Dict[int, Point]:
        """Initialize node positions randomly or in a grid pattern.

        Args:
            nodes: List of nodes
            config: Layout configuration

        Returns:
            Dict mapping node index to initial position
        """
        positions: Dict[int, Point] = {}
        canvas_width = max(100, len(nodes) * 10)
        canvas_height = canvas_width

        for i in range(len(nodes)):
            # Use existing position if available, otherwise random
            if hasattr(nodes[i], "x") and hasattr(nodes[i], "y"):
                positions[i] = Point(float(nodes[i].x), float(nodes[i].y))
            else:
                x = random.uniform(0, canvas_width)
                y = random.uniform(0, canvas_height)
                positions[i] = Point(x, y)

        return positions

    def _resolve_overlaps(
        self, positions: Dict[int, Point], nodes: List[Any]
    ) -> Dict[int, Point]:
        """Resolve remaining overlaps by pushing overlapping nodes apart.

        Args:
            positions: Current node positions
            nodes: List of nodes (for dimension information)

        Returns:
            Adjusted positions with overlaps resolved
        """
        # Get node dimensions (width/height halves)
        node_dims = {}
        for i, node in enumerate(nodes):
            w = getattr(node, 'w', 100)
            h = getattr(node, 'h', 80)
            node_dims[i] = (w, h)

        # Iteratively push overlapping nodes apart
        max_iterations = 20
        for _ in range(max_iterations):
            any_adjusted = False

            node_ids = list(positions.keys())
            for i in range(len(node_ids)):
                for j in range(i + 1, len(node_ids)):
                    ni = node_ids[i]
                    nj = node_ids[j]

                    pi = positions[ni]
                    pj = positions[nj]

                    w1, h1 = node_dims.get(ni, (100, 80))
                    w2, h2 = node_dims.get(nj, (100, 80))

                    # Check if bounding boxes overlap
                    dx = abs(pi.x - pj.x)
                    dy = abs(pi.y - pj.y)
                    min_dx = (w1 + w2) / 2.0 + 10
                    min_dy = (h1 + h2) / 2.0 + 10

                    if dx < min_dx and dy < min_dy:
                        # Push nodes apart
                        dist = pi.distance_to(pj)
                        if dist > 0.1:
                            direction_x = (pj.x - pi.x) / dist
                            direction_y = (pj.y - pi.y) / dist
                        else:
                            direction_x, direction_y = 1.0, 0.0

                        push = max(min_dx - dx, min_dy - dy) / 2.0 + 15

                        positions[ni] = Point(pi.x - direction_x * push, pi.y - direction_y * push)
                        positions[nj] = Point(pj.x + direction_x * push, pj.y + direction_y * push)
                        any_adjusted = True

            if not any_adjusted:
                break

        return positions

    def _get_iteration_limit(self, node_count: int) -> int:
        """Get adaptive iteration limit based on element count.

        Args:
            node_count: Number of nodes

        Returns:
            Maximum number of iterations
        """
        # More nodes = fewer iterations (due to computational cost)
        if node_count < 50:
            return 500
        elif node_count < 200:
            return 300
        else:
            return 150

    def _calculate_forces(
        self,
        positions: Dict[int, Point],
        edges: list,
        layer_constraint: LayerConstraint,
    ) -> Dict[int, Point]:
        """Calculate forces on each node.

        Args:
            positions: Current node positions
            edges: List of edges/connections
            layer_constraint: Layer constraint system

        Returns:
            Dict mapping node index to force vector
        """
        forces: Dict[int, Point] = {i: Point(0, 0) for i in positions.keys()}

        # Repulsive forces between all pairs
        node_ids = list(positions.keys())
        for i in range(len(node_ids)):
            for j in range(i + 1, len(node_ids)):
                node_i = node_ids[i]
                node_j = node_ids[j]

                p_i = positions[node_i]
                p_j = positions[node_j]

                dist = p_i.distance_to(p_j)
                if dist < 0.1:
                    dist = 0.1

                # Repulsive force magnitude - increases as nodes get closer than min separation
                if dist < self.min_separation:
                    # Strong repulsion when nodes are too close
                    magnitude = self.k_repulsion * (self.min_separation - dist) / (dist * dist)
                else:
                    # Weak repulsion when nodes are far enough apart
                    magnitude = self.k_repulsion / (dist * dist) * 0.1

                # Force direction
                dx = (p_i.x - p_j.x) / dist
                dy = (p_i.y - p_j.y) / dist

                forces[node_i].x += magnitude * dx
                forces[node_i].y += magnitude * dy
                forces[node_j].x -= magnitude * dx
                forces[node_j].y -= magnitude * dy

        # Attractive forces along edges
        for edge in edges:
            # Extract connected nodes (handle different edge formats)
            if isinstance(edge, (tuple, list)) and len(edge) >= 2:
                source_idx, target_idx = edge[0], edge[1]
            else:
                # Skip if edge format is unclear
                continue

            if source_idx not in positions or target_idx not in positions:
                continue

            p_source = positions[source_idx]
            p_target = positions[target_idx]

            dist = p_source.distance_to(p_target)
            if dist < 0.1:
                dist = 0.1

            # Attractive force magnitude
            magnitude = self.k_attraction * dist

            # Force direction
            dx = (p_target.x - p_source.x) / dist
            dy = (p_target.y - p_source.y) / dist

            forces[source_idx].x += magnitude * dx
            forces[source_idx].y += magnitude * dy
            forces[target_idx].x -= magnitude * dx
            forces[target_idx].y -= magnitude * dy

        # Apply layer constraint forces
        for node_i in positions.keys():
            layer_i = layer_constraint.get_layer(node_i)

            for node_j in positions.keys():
                if node_i == node_j:
                    continue

                layer_j = layer_constraint.get_layer(node_j)

                # If node_i should be above node_j but isn't, apply downward force
                if layer_i.layer_order() < layer_j.layer_order():
                    if positions[node_i].y > positions[node_j].y:
                        # Wrong order, apply corrective force
                        forces[node_i].y -= 100  # Push up
                        forces[node_j].y += 100  # Push down

        return forces
