"""Force-directed (Spring-Embedder) layout algorithm for ArchiMate views."""

import math
import random
from typing import Any, Dict, Tuple
from ..core import LayoutAlgorithm, LayoutConfig, LayoutResult
from ..utils.geometry import Point, Rectangle
from ..routing.layer_constraints import LayerConstraint, ArchiMateLayer


class ForceDirectedLayout(LayoutAlgorithm):
    """Force-directed layout using Spring-Embedder physics simulation."""

    def __init__(self) -> None:
        """Initialize force-directed layout."""
        self.k_attraction = 0.5  # Spring attraction constant
        self.k_repulsion = 5000.0  # Node repulsion constant
        self.damping = 0.85  # Velocity damping for stability
        self.tolerance = 1.0  # Convergence tolerance
        self.max_iterations = 1000  # Maximum iterations

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
            edges = getattr(view, "edges", [])

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
                        velocities[node_id] = Point(
                            force.x * self.damping,
                            force.y * self.damping,
                        )
                        positions[node_id] = Point(
                            positions[node_id].x + velocities[node_id].x,
                            positions[node_id].y + velocities[node_id].y,
                        )
                        max_velocity = max(max_velocity, abs(velocities[node_id].x), abs(velocities[node_id].y))

                # Check for convergence
                if max_velocity < self.tolerance:
                    converged = True
                    break

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
            elapsed_ms = (time.time() - start_time) * 1000
            return LayoutResult(
                success=False,
                view_id=getattr(view, "id", "unknown"),
                algorithm_used="force_directed",
                elements_processed=0,
                connections_processed=0,
                layout_time_ms=elapsed_ms,
                error_message=str(e),
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

                # Repulsive force magnitude
                magnitude = self.k_repulsion / (dist * dist)

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
