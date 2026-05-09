"""Graph analysis utilities for layout operations."""



class Graph:
    """Simple undirected graph representation."""

    def __init__(self) -> None:
        """Initialize empty graph."""
        self.nodes: set[str] = set()
        self.edges: dict[str, set[str]] = {}

    def add_node(self, node_id: str) -> None:
        """Add a node to the graph."""
        self.nodes.add(node_id)
        if node_id not in self.edges:
            self.edges[node_id] = set()

    def add_edge(self, node1: str, node2: str) -> None:
        """Add an edge between two nodes."""
        self.add_node(node1)
        self.add_node(node2)
        self.edges[node1].add(node2)
        self.edges[node2].add(node1)

    def get_neighbors(self, node_id: str) -> set[str]:
        """Get all neighbors of a node."""
        return self.edges.get(node_id, set())

    def _visit_node_for_cycle(self, node: str, parent: str, visited: set[str], rec_stack: set[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)
        for neighbor in self.edges.get(node, set()):
            if neighbor == parent:
                continue
            if neighbor not in visited:
                if self._visit_node_for_cycle(neighbor, node, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(node)
        return False

    def has_cycle(self) -> bool:
        """Check if graph contains a cycle."""
        visited: set[str] = set()
        rec_stack: set[str] = set()
        for node in self.nodes:
            if node not in visited and self._visit_node_for_cycle(node, "", visited, rec_stack):
                return True
        return False

    def get_connected_components(self) -> list[set[str]]:
        """Get all connected components in the graph."""
        visited: set[str] = set()
        components: list[set[str]] = []

        def _dfs(node: str, component: set[str]) -> None:
            visited.add(node)
            component.add(node)
            for neighbor in self.edges.get(node, set()):
                if neighbor not in visited:
                    _dfs(neighbor, component)

        for node in self.nodes:
            if node not in visited:
                component: set[str] = set()
                _dfs(node, component)
                components.append(component)

        return components


def detect_crossings(
    line1: tuple[tuple[float, float], tuple[float, float]],
    line2: tuple[tuple[float, float], tuple[float, float]],
) -> bool:
    """Detect if two line segments intersect.

    Args:
        line1: Tuple of ((x1, y1), (x2, y2))
        line2: Tuple of ((x3, y3), (x4, y4))

    Returns:
        True if lines intersect, False otherwise
    """
    def ccw(pt_a: tuple[float, float], pt_b: tuple[float, float], pt_c: tuple[float, float]) -> bool:
        return (pt_c[1] - pt_a[1]) * (pt_b[0] - pt_a[0]) > (pt_b[1] - pt_a[1]) * (pt_c[0] - pt_a[0])

    pt_a, pt_b = line1
    pt_c, pt_d = line2

    return ccw(pt_a, pt_c, pt_d) != ccw(pt_b, pt_c, pt_d) and ccw(pt_a, pt_b, pt_c) != ccw(pt_a, pt_b, pt_d)


def count_crossings(
    edges: list[tuple[tuple[float, float], tuple[float, float]]],
) -> int:
    """Count total number of edge crossings.

    Args:
        edges: List of line segments (edges)

    Returns:
        Total crossing count
    """
    crossing_count = 0
    for i, edge1 in enumerate(edges):
        for edge2 in edges[i + 1 :]:
            if detect_crossings(edge1, edge2):
                crossing_count += 1

    return crossing_count
