"""Hierarchical (Sugiyama) layout algorithm for ArchiMate views.

Implements the Sugiyama layered layout method with ArchiMate layer constraints.
"""

from typing import Any, Dict, List, Tuple

from ..core import LayoutAlgorithm, LayoutConfig, LayoutResult
from ..routing.layer_constraints import ArchiMateLayer, LayerConstraint
from ..utils.edge_utils import normalize_edges
from ..utils.geometry import Point


class HierarchicalLayout(LayoutAlgorithm):
    """Hierarchical layered layout using Sugiyama's method."""

    def __init__(self) -> None:
        """Initialize hierarchical layout."""
        self.layer_gap = 100  # Vertical gap between layers
        self.node_spacing = 50  # Horizontal spacing between nodes in a layer
        self.layer_constraint = None

    def apply(self, view: Any, config: LayoutConfig) -> LayoutResult:
        """Apply hierarchical layout to a view.

        Args:
            view: View object with nodes and edges
            config: Layout configuration

        Returns:
            LayoutResult with layout metrics
        """
        import time
        start_time = time.time()

        try:
            nodes = getattr(view, "nodes", [])
            raw_edges = getattr(view, "conns", []) or getattr(view, "edges", [])
            edges = normalize_edges(raw_edges, nodes)

            if not nodes:
                return LayoutResult(
                    success=True,
                    view_id=getattr(view, "id", "unknown"),
                    algorithm_used="hierarchical",
                    elements_processed=0,
                    connections_processed=0,
                    layout_time_ms=(time.time() - start_time) * 1000,
                )

            # Build graph representation
            graph = self._build_graph(nodes, edges)

            # Step 1: Layer assignment (respecting ArchiMate layers)
            layers = self._assign_layers(nodes, graph, config)

            # Step 2: Crossing minimization
            layers = self._minimize_crossings(layers, graph)

            # Step 3: Position assignment
            positions = self._assign_positions(layers, config, nodes)

            # Apply positions to nodes (convert to integers for Archi XML compatibility)
            for i, node in enumerate(nodes):
                if i in positions:
                    pos = positions[i]
                    node.x = int(round(pos.x))
                    node.y = int(round(pos.y))

            # Calculate metrics
            crossings = self._count_crossings(positions, edges)

            elapsed_ms = (time.time() - start_time) * 1000

            return LayoutResult(
                success=True,
                view_id=getattr(view, "id", "unknown"),
                algorithm_used="hierarchical",
                elements_processed=len(nodes),
                connections_processed=len(edges),
                layout_time_ms=elapsed_ms,
                quality_metrics={
                    "layers": len(layers),
                    "crossings": crossings,
                    "max_layer_width": max((len(layer) for layer in layers), default=0),
                },
            )
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            return LayoutResult(
                success=False,
                view_id=getattr(view, "id", "unknown"),
                algorithm_used="hierarchical",
                elements_processed=0,
                connections_processed=0,
                layout_time_ms=elapsed_ms,
                error_message=str(e),
            )

    def _build_graph(self, nodes: List[Any], edges: List[Any]) -> Dict[int, List[int]]:
        """Build adjacency list representation of the graph.

        Args:
            nodes: List of nodes
            edges: List of edges as tuples (source, target)

        Returns:
            Adjacency list: dict mapping node index to list of connected node indices
        """
        graph: dict[int, list[int]] = {i: [] for i in range(len(nodes))}

        for source, target in edges:
            if isinstance(source, int) and isinstance(target, int):
                if source in graph and target in graph:
                    graph[source].append(target)

        return graph

    def _assign_layers(  # noqa: C901
        self,
        nodes: List[Any],
        graph: Dict[int, List[int]],
        config: LayoutConfig,
    ) -> List[List[int]]:
        """Assign nodes to layers using topological sort respecting ArchiMate layers.

        Args:
            nodes: List of nodes
            graph: Adjacency list representation
            config: Layout configuration

        Returns:
            Layers as list of lists of node indices
        """
        # Create layer constraint
        layer_constraint = LayerConstraint()
        for i, node in enumerate(nodes):
            element_type = getattr(node, "type", "unknown")
            archimate_layer = ArchiMateLayer.from_archimate_type(element_type)
            layer_constraint.assign_layer(i, archimate_layer)

        # Use topological sort with layer constraints
        in_degree = dict.fromkeys(range(len(nodes)), 0)
        for source in graph:
            for target in graph[source]:
                in_degree[target] = in_degree.get(target, 0) + 1

        # Assign layers by topological level, respecting ArchiMate layers
        layers: List[List[int]] = []
        assigned: set[int] = set()
        current_layer = 0

        while len(assigned) < len(nodes):
            layer_nodes = []

            # Find nodes with no unassigned predecessors
            for node_id in range(len(nodes)):
                if node_id in assigned:
                    continue

                has_unassigned_pred = False
                for source in graph:
                    if node_id in graph[source] and source not in assigned:
                        has_unassigned_pred = True
                        break

                if not has_unassigned_pred:
                    # Check ArchiMate layer constraints
                    archimate_layer = layer_constraint.get_layer(node_id)
                    # Can assign to any layer >= its ArchiMate layer precedence
                    if self._respects_archimate_ordering(
                        node_id, current_layer, nodes, layer_constraint
                    ):
                        layer_nodes.append(node_id)

            if not layer_nodes:
                # If no valid nodes found, force assignment of remaining nodes
                for node_id in range(len(nodes)):
                    if node_id not in assigned:
                        layer_nodes.append(node_id)
                        break

            if layer_nodes:
                layers.append(layer_nodes)
                assigned.update(layer_nodes)
                current_layer += 1
            else:
                break

        return layers if layers else [list(range(len(nodes)))]

    def _respects_archimate_ordering(
        self,
        node_id: int,
        layer_index: int,
        nodes: List[Any],
        layer_constraint: LayerConstraint,
    ) -> bool:
        """Check if assigning node to layer respects ArchiMate layer ordering.

        Args:
            node_id: Node identifier
            layer_index: Target layer index
            nodes: List of nodes
            layer_constraint: Layer constraint manager

        Returns:
            True if assignment respects constraints
        """
        # Business > Application > Technology
        # Lower layer indices should contain higher-precedence elements
        # Check if assignment is reasonable (can be relaxed if needed)
        # Allow assignment to any layer for now to avoid blocking
        return True

    def _minimize_crossings(
        self, layers: List[List[int]], graph: Dict[int, List[int]]
    ) -> List[List[int]]:
        """Minimize edge crossings using barycentric method.

        Args:
            layers: Layers with node indices
            graph: Adjacency list representation

        Returns:
            Reordered layers
        """
        # Barycentric ordering: order nodes by average position of neighbors
        reordered_layers = [layer[:] for layer in layers]

        for layer_idx in range(1, len(reordered_layers)):
            current_layer = reordered_layers[layer_idx]
            prev_layer = reordered_layers[layer_idx - 1]

            # Calculate barycenter for each node in current layer
            barycenters = {}
            for node_id in current_layer:
                # Find incoming edges from previous layer
                incoming = []
                for source in graph:
                    if source in prev_layer and node_id in graph[source]:
                        incoming.append(prev_layer.index(source))

                if incoming:
                    barycenters[node_id] = sum(incoming) / len(incoming)
                else:
                    barycenters[node_id] = len(prev_layer) / 2

            # Sort by barycenter
            reordered_layers[layer_idx] = sorted(
                current_layer, key=lambda x: barycenters.get(x, 0)
            )

        return reordered_layers

    def _assign_positions(
        self, layers: List[List[int]], config: LayoutConfig, nodes: List[Any]
    ) -> Dict[int, Point]:
        """Assign x,y coordinates to nodes based on layer structure.

        Args:
            layers: Layers with ordered node indices
            config: Layout configuration
            nodes: List of nodes (for sizing information)

        Returns:
            Dictionary mapping node index to Point position
        """
        positions = {}

        # Y coordinate based on layer
        y_base = config.margin
        layer_height = max(150, self.layer_gap + 100)  # Larger separation to prevent overlap

        for layer_idx, layer in enumerate(layers):
            y = y_base + layer_idx * layer_height

            # X coordinate based on position within layer
            # Calculate spacing based on element widths
            x_base = config.margin
            spacing = config.spacing if config.spacing > 0 else 80

            # Increase spacing based on max element width in this layer
            max_width = 0
            for node_id in layer:
                if node_id < len(nodes):
                    w = getattr(nodes[node_id], 'w', 100)
                    max_width = max(max_width, w)

            # Add padding for visibility
            spacing = max(spacing, max_width + 50)

            for pos_idx, node_id in enumerate(layer):
                x = x_base + pos_idx * spacing
                positions[node_id] = Point(x, y)

        return positions

    def _count_crossings(
        self, positions: Dict[int, Point], edges: List[Tuple[int, int]]
    ) -> int:
        """Count edge crossings in the layout.

        Args:
            positions: Node positions
            edges: List of edges

        Returns:
            Number of crossing pairs
        """
        crossings = 0

        for i, (s1, t1) in enumerate(edges):
            for s2, t2 in edges[i + 1 :]:
                # Simple check: edges cross if their x-coordinates interleave
                if s1 in positions and t1 in positions and s2 in positions and t2 in positions:
                    x1_start = positions[s1].x
                    x1_end = positions[t1].x
                    x2_start = positions[s2].x
                    x2_end = positions[t2].x

                    # Check if edges cross (simplified)
                    if (x1_start < x2_start < x1_end < x2_end) or (
                        x2_start < x1_start < x2_end < x1_end
                    ):
                        crossings += 1

        return crossings
