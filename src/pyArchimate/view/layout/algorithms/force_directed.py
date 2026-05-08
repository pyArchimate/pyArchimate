"""Force-directed (Spring-Embedder) layout algorithm for ArchiMate views."""

import math
import random
from typing import Any, Dict, List

from ..core import LayoutAlgorithm, LayoutConfig, LayoutResult
from ..routing.layer_constraints import ArchiMateLayer, LayerConstraint
from ..utils.edge_utils import normalize_edges
from ..utils.geometry import Point


class ForceDirectedLayout(LayoutAlgorithm):
    """Force-directed layout using Spring-Embedder physics simulation."""

    def __init__(self) -> None:
        """Initialize force-directed layout."""
        self.k_attraction = 0.01  # Spring attraction constant (very weak)
        self.k_repulsion = 2000.0  # Node repulsion constant - strong repulsion
        self.damping = 0.8  # Velocity damping for stability
        self.tolerance = 0.1  # Convergence tolerance (increased from 0.05 for faster exit)
        self.max_iterations = 500  # Maximum iterations
        self.max_velocity = 150.0  # Maximum velocity per iteration
        self.min_separation = 200.0  # Minimum distance between nodes (increased from 150)

    def apply(self, view: Any, config: LayoutConfig) -> LayoutResult:  # noqa: C901
        """Apply force-directed layout to a view.

        Args:
            view: View object with nodes and edges
            config: Layout configuration (supports spacing, excluded_element_ids, layer_priority)

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

            # Build set of excluded element IDs
            excluded_ids = set(config.excluded_element_ids)

            # Filter edges to only include those not connected to excluded nodes
            filtered_edges = [e for e in edges if e[0] not in excluded_ids and e[1] not in excluded_ids]

            if not nodes:
                return LayoutResult(
                    success=True,
                    view_id=getattr(view, "id", "unknown"),
                    algorithm_used="force_directed",
                    elements_processed=0,
                    connections_processed=0,
                    layout_time_ms=(time.time() - start_time) * 1000,
                )

            # Adjust repulsion constant based on spacing config
            self.min_separation = config.spacing + 100

            # Initialize positions and velocities
            positions = self._initialize_positions(nodes, config)
            velocities = {node_id: Point(0, 0) for node_id in positions.keys()}

            # Set up layer constraints with priority handling
            layer_constraint = LayerConstraint()
            for node_id, node in enumerate(nodes):
                element_type = getattr(node, "type", "unknown")
                layer = ArchiMateLayer.from_archimate_type(element_type)
                layer_constraint.assign_layer(node_id, layer)

            # Adaptive iteration limit based on element count
            max_iter = self._get_iteration_limit(len(nodes))

            # Run physics simulation (excluding specified elements)
            converged = False
            iterations_completed = 0
            for i, _ in enumerate(range(max_iter)):
                iterations_completed = i
                # Calculate forces (skip excluded nodes)
                forces = self._calculate_forces(positions, filtered_edges, layer_constraint)

                # Update velocities and positions (skip excluded nodes)
                max_velocity = 0.0
                for node_id in positions:
                    if node_id in excluded_ids:
                        continue

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
            positions = self._resolve_overlaps(positions, nodes, excluded_ids)

            # Enforce layer constraints (mandatory or soft based on config)
            if config.layer_priority == "mandatory":
                positions = layer_constraint.enforce_layer_separation_with_exclusions(positions, config.spacing, excluded_ids)

            # Layer clamping can reintroduce collisions, so make one final pass.
            positions = self._resolve_overlaps(positions, nodes, excluded_ids)

            # Store positions back to nodes (skip excluded)
            # Convert to integers for Archi XML compatibility
            for i, node in enumerate(nodes):
                if i not in excluded_ids and i in positions:
                    pos = positions[i]
                    node.x = int(round(pos.x))
                    node.y = int(round(pos.y))

            elapsed_ms = (time.time() - start_time) * 1000

            return LayoutResult(
                success=True,
                view_id=getattr(view, "id", "unknown"),
                algorithm_used="force_directed",
                elements_processed=len(nodes) - len(excluded_ids),
                connections_processed=len(filtered_edges),
                layout_time_ms=elapsed_ms,
                quality_metrics={
                    "converged": converged,
                    "iterations": iterations_completed + 1,
                    "max_iterations": max_iter,
                    "excluded_elements": len(excluded_ids),
                    "spacing": config.spacing,
                    "layer_priority": config.layer_priority,
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

    def _initialize_positions(self, nodes: list[Any], config: LayoutConfig) -> Dict[int, Point]:
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
        self, positions: Dict[int, Point], nodes: List[Any], excluded_ids: set[int] | None = None
    ) -> Dict[int, Point]:
        """Resolve remaining overlaps by pushing overlapping nodes apart.

        Args:
            positions: Current node positions
            nodes: List of nodes (for dimension information)
            excluded_ids: Set of node IDs to exclude from adjustment

        Returns:
            Adjusted positions with overlaps resolved
        """
        if excluded_ids is None:
            excluded_ids = set()

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

                    # Skip excluded nodes
                    if ni in excluded_ids or nj in excluded_ids:
                        continue

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

    def _calculate_forces(  # noqa: C901
        self,
        positions: Dict[int, Point],
        edges: list[Any],
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

        # Apply layer constraint forces (optimized to only check different layers)
        node_ids = list(positions.keys())
        for i in range(len(node_ids)):
            node_i = node_ids[i]
            layer_i = layer_constraint.get_layer(node_i)

            # Only compare with nodes in different layers to reduce O(n²) overhead
            for j in range(i + 1, len(node_ids)):
                node_j = node_ids[j]
                layer_j = layer_constraint.get_layer(node_j)

                # Skip if same layer
                if layer_i.layer_order() == layer_j.layer_order():
                    continue

                # If node_i should be above node_j but isn't, apply corrective force
                if layer_i.layer_order() < layer_j.layer_order():
                    if positions[node_i].y > positions[node_j].y:
                        # Wrong order, apply corrective force (reduced to prevent instability)
                        forces[node_i].y -= 50  # Push up
                        forces[node_j].y += 50  # Push down

        return forces
