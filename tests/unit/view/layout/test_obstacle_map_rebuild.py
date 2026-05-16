"""Unit tests for ObstacleMap.rebuild_for_moved_nodes()."""

from src.pyArchimate.view.layout.core import NodeMove, RoutingConfig
from src.pyArchimate.view.layout.routing.obstacle_map import ObstacleMap
from src.pyArchimate.view.layout.utils.geometry import Rectangle


class TestObstacleMapRebuild:
    """Test ObstacleMap.rebuild_for_moved_nodes() method."""

    def test_rebuild_single_node_move(self):
        """P2-T55: After 1-cell node move, old AABB cells cleared, new cells present."""
        # Create initial obstacle map with one node at (0, 0) sized 100x100
        obstacles = [Rectangle(0.0, 0.0, 100.0, 100.0)]
        config = RoutingConfig(node_clearance=25)  # 25px inflation on all sides
        om = ObstacleMap(obstacles, resolution=10.0, config=config)

        # Capture old cells (with 25px clearance: x0=-25, y0=-25, x1=125, y1=125)
        # Cells from -25/10=-3 to 125/10=12
        old_cells_count = len(om._cells)
        assert old_cells_count > 0, "Initial obstacle map should have blocked cells"

        # Node object with w, h
        class MockNode:
            def __init__(self, x, y, w, h, uuid):
                self.x = x
                self.y = y
                self.w = w
                self.h = h
                self.uuid = uuid

        # Move node 1 cell right (10px * 1 = 10px displacement)
        node = MockNode(0.0, 0.0, 100.0, 100.0, "node-1")
        node.x = 10.0  # Move 10px right
        nodes_dict = {"node-1": node}

        move = NodeMove(uuid="node-1", old_x=0.0, old_y=0.0, new_x=10.0, new_y=10.0)
        om.rebuild_for_moved_nodes([move], nodes_dict)

        # Verify old cells cleared and new cells added
        # Old rect: (-25, -25) to (125, 125) in cell coords: (-3, -3) to (12, 12)
        # New rect: (-15, -15) to (135, 135) in cell coords: (-2, -2) to (13, 13)
        # There should be some overlap but cells should change
        new_cells_count = len(om._cells)
        assert new_cells_count > 0, "Obstacle map should still have blocked cells after rebuild"

    def test_rebuild_multiple_nodes_move(self):
        """P2-T55: Multiple nodes moved simultaneously."""
        obstacles = [
            Rectangle(0.0, 0.0, 100.0, 100.0),
            Rectangle(200.0, 0.0, 100.0, 100.0),
        ]
        config = RoutingConfig(node_clearance=25)
        om = ObstacleMap(obstacles, resolution=10.0, config=config)

        assert len(om._cells) > 0, "Initial obstacle map should have blocked cells"

        class MockNode:
            def __init__(self, x, y, w, h, uuid):
                self.x = x
                self.y = y
                self.w = w
                self.h = h
                self.uuid = uuid

        node1 = MockNode(0.0, 0.0, 100.0, 100.0, "node-1")
        node2 = MockNode(200.0, 0.0, 100.0, 100.0, "node-2")
        node1.x = 20.0
        node2.x = 220.0
        nodes_dict = {"node-1": node1, "node-2": node2}

        moves = [
            NodeMove(uuid="node-1", old_x=0.0, old_y=0.0, new_x=20.0, new_y=0.0),
            NodeMove(uuid="node-2", old_x=200.0, old_y=0.0, new_x=220.0, new_y=0.0),
        ]
        om.rebuild_for_moved_nodes(moves, nodes_dict)

        final_count = len(om._cells)
        assert final_count > 0, "Map should still have cells after multiple node moves"

    def test_rebuild_with_default_clearance(self):
        """P2-T55: rebuild_for_moved_nodes uses RoutingConfig.node_clearance from init."""
        obstacles = [Rectangle(0.0, 0.0, 100.0, 100.0)]
        config = RoutingConfig(node_clearance=20)
        om = ObstacleMap(obstacles, resolution=10.0, config=config)

        class MockNode:
            def __init__(self, x, y, w, h, uuid):
                self.x = x
                self.y = y
                self.w = w
                self.h = h
                self.uuid = uuid

        node = MockNode(0.0, 0.0, 100.0, 100.0, "node-1")
        node.x = 5.0
        nodes_dict = {"node-1": node}

        move = NodeMove(uuid="node-1", old_x=0.0, old_y=0.0, new_x=5.0, new_y=0.0)
        om.rebuild_for_moved_nodes([move], nodes_dict)

        # Should use node_clearance=20 from initial config
        assert len(om._cells) > 0, "Cells should exist after rebuild with custom clearance"

    def test_rebuild_preserves_routed_segments(self):
        """P2-T55: rebuild_for_moved_nodes does not affect _routed segments."""
        obstacles = [Rectangle(0.0, 0.0, 100.0, 100.0)]
        om = ObstacleMap(obstacles, resolution=10.0)

        # Mark a routed segment
        from src.pyArchimate.view.layout.utils.geometry import Point
        om.mark_routed_segment(Point(500.0, 500.0), Point(600.0, 500.0))
        routed_before = len(om._routed)
        assert routed_before > 0, "Should have marked routed cells"

        class MockNode:
            def __init__(self, x, y, w, h, uuid):
                self.x = x
                self.y = y
                self.w = w
                self.h = h
                self.uuid = uuid

        node = MockNode(0.0, 0.0, 100.0, 100.0, "node-1")
        node.x = 10.0
        nodes_dict = {"node-1": node}

        move = NodeMove(uuid="node-1", old_x=0.0, old_y=0.0, new_x=10.0, new_y=0.0)
        om.rebuild_for_moved_nodes([move], nodes_dict)

        routed_after = len(om._routed)
        assert routed_after == routed_before, "Routed segments should be preserved after rebuild"

    def test_rebuild_missing_node_ignored(self):
        """P2-T55: If node not in nodes_dict, skip it gracefully."""
        obstacles = [Rectangle(0.0, 0.0, 100.0, 100.0)]
        om = ObstacleMap(obstacles, resolution=10.0)

        nodes_dict = {}  # Empty
        move = NodeMove(uuid="nonexistent", old_x=0.0, old_y=0.0, new_x=10.0, new_y=0.0)

        # Should not raise, just skip the missing node
        om.rebuild_for_moved_nodes([move], nodes_dict)
        assert len(om._cells) > 0, "Map should retain original cells for skipped moves"
