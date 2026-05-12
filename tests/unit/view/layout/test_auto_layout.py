"""Tests for auto_layout function (T021-T032)."""

import time
from unittest.mock import MagicMock

from src.pyArchimate.view.layout import LayoutConfig, auto_layout

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def mock_node(uuid: str, element_type: str, x: float = 0, y: float = 0,
              w: float = 120, h: float = 55) -> MagicMock:
    n = MagicMock()
    n.uuid = uuid
    n.type = element_type
    n.x = x
    n.y = y
    n.w = w
    n.h = h
    n.cx = x + w / 2
    n.cy = y + h / 2
    return n


def mock_connection(uuid: str, source_uuid: str, target_uuid: str,
                    bendpoints: list | None = None) -> MagicMock:
    c = MagicMock()
    c.uuid = uuid
    c._source = source_uuid
    c._target = target_uuid
    c.bendpoints = list(bendpoints or [])
    return c


def make_view(nodes: list, connections: list | None = None) -> MagicMock:
    view = MagicMock()
    view.uuid = "view-1"
    view.nodes = nodes
    view.nodes_dict = {n.uuid: n for n in nodes}
    view.conns = list(connections or [])
    view.conns_dict = {c.uuid: c for c in (connections or [])}
    return view


# ---------------------------------------------------------------------------
# T021 — Grid snapping
# ---------------------------------------------------------------------------

class TestGridSnapping:
    def test_all_nodes_snap_to_grid(self) -> None:
        """Node origins must be margin + multiple of grid_size after auto_layout."""
        nodes = [
            mock_node("n1", "BusinessActor", x=37, y=23),
            mock_node("n2", "ApplicationComponent", x=155, y=88),
            mock_node("n3", "TechnologyService", x=301, y=211),
        ]
        view = make_view(nodes)
        config = LayoutConfig(grid_size=120.0, margin=0.0)
        auto_layout(view, config)
        for n in nodes:
            assert n.x % 120 == 0, f"Node {n.uuid} x={n.x} not multiple of 120"
            assert n.y % 120 == 0, f"Node {n.uuid} y={n.y} not multiple of 120"

    def test_custom_grid_size(self) -> None:
        """Node origins snap to custom grid_size=80."""
        nodes = [mock_node("n1", "BusinessActor", x=50, y=50)]
        view = make_view(nodes)
        auto_layout(view, LayoutConfig(grid_size=80.0, margin=0.0))
        assert nodes[0].x % 80 == 0
        assert nodes[0].y % 80 == 0


# ---------------------------------------------------------------------------
# T022 — Vertical layer ordering
# ---------------------------------------------------------------------------

class TestVerticalLayerOrdering:
    def test_business_above_application_above_technology(self) -> None:
        business = [mock_node(f"b{i}", "BusinessActor") for i in range(3)]
        app = [mock_node(f"a{i}", "ApplicationComponent") for i in range(3)]
        tech = [mock_node(f"t{i}", "TechnologyService") for i in range(3)]
        view = make_view(business + app + tech)
        auto_layout(view, LayoutConfig(layer_direction="vertical"))
        max_biz_y = max(n.y for n in business)
        min_app_y = min(n.y for n in app)
        max_app_y = max(n.y for n in app)
        min_tech_y = min(n.y for n in tech)
        assert max_biz_y < min_app_y, "Business nodes must be above Application nodes"
        assert max_app_y < min_tech_y, "Application nodes must be above Technology nodes"


# ---------------------------------------------------------------------------
# T023 — Horizontal layer ordering
# ---------------------------------------------------------------------------

class TestHorizontalLayerOrdering:
    def test_business_left_of_application_left_of_technology(self) -> None:
        business = [mock_node(f"b{i}", "BusinessActor") for i in range(2)]
        app = [mock_node(f"a{i}", "ApplicationComponent") for i in range(2)]
        tech = [mock_node(f"t{i}", "TechnologyService") for i in range(2)]
        view = make_view(business + app + tech)
        auto_layout(view, LayoutConfig(layer_direction="horizontal"))
        max_biz_x = max(n.x for n in business)
        min_app_x = min(n.x for n in app)
        max_app_x = max(n.x for n in app)
        min_tech_x = min(n.x for n in tech)
        assert max_biz_x < min_app_x, "Business nodes must be left of Application nodes"
        assert max_app_x < min_tech_x, "Application nodes must be left of Technology nodes"


# ---------------------------------------------------------------------------
# T024 — No overlapping nodes
# ---------------------------------------------------------------------------

class TestNoNodeOverlap:
    def test_no_two_nodes_overlap(self) -> None:
        """After auto_layout, no two node bounding boxes intersect."""
        nodes = [mock_node(f"n{i}", "BusinessActor") for i in range(8)]
        view = make_view(nodes)
        auto_layout(view, LayoutConfig(grid_size=120.0))
        for i, n1 in enumerate(nodes):
            for j, n2 in enumerate(nodes):
                if i >= j:
                    continue
                # Check bounding box non-intersection
                overlap_x = n1.x < n2.x + n2.w and n2.x < n1.x + n1.w
                overlap_y = n1.y < n2.y + n2.h and n2.y < n1.y + n1.h
                assert not (overlap_x and overlap_y), (
                    f"Nodes {n1.uuid} and {n2.uuid} overlap: "
                    f"({n1.x},{n1.y},{n1.w},{n1.h}) vs ({n2.x},{n2.y},{n2.w},{n2.h})"
                )


# ---------------------------------------------------------------------------
# T025 — Waypoints unchanged (SC-010)
# ---------------------------------------------------------------------------

class TestWaypointsUnchanged:
    def test_auto_layout_does_not_modify_connection_bendpoints(self) -> None:
        """auto_layout must not touch any connection waypoints."""
        from src.pyArchimate.view.__init__ import Point as ViewPoint
        nodes = [
            mock_node("n1", "BusinessActor"),
            mock_node("n2", "ApplicationComponent"),
        ]
        bp = ViewPoint(100, 200)
        conn = mock_connection("c1", "n1", "n2", bendpoints=[bp])
        original_bendpoints = list(conn.bendpoints)
        view = make_view(nodes, [conn])
        auto_layout(view)
        assert conn.bendpoints == original_bendpoints, \
            "auto_layout must not modify connection bendpoints"


# ---------------------------------------------------------------------------
# T030 — Idempotency
# ---------------------------------------------------------------------------

class TestIdempotency:
    def test_calling_twice_produces_same_positions(self) -> None:
        nodes = [mock_node(f"n{i}", "BusinessActor") for i in range(4)]
        view = make_view(nodes)
        auto_layout(view)
        positions_after_first = {n.uuid: (n.x, n.y) for n in nodes}
        auto_layout(view)
        positions_after_second = {n.uuid: (n.x, n.y) for n in nodes}
        assert positions_after_first == positions_after_second


# ---------------------------------------------------------------------------
# T031 — Empty view
# ---------------------------------------------------------------------------

class TestEmptyView:
    def test_empty_view_returns_success(self) -> None:
        view = make_view([])
        result = auto_layout(view)
        assert result.success is True
        assert result.elements_processed == 0
        assert result.error_message is None


# ---------------------------------------------------------------------------
# T032 — Performance smoke test (SC-001: < 2s for 500 nodes)
# ---------------------------------------------------------------------------

class TestPerformance:
    def test_500_nodes_completes_under_2s(self) -> None:
        nodes = [mock_node(f"n{i}", "BusinessActor") for i in range(500)]
        view = make_view(nodes)
        start = time.time()
        result = auto_layout(view)
        elapsed = time.time() - start
        assert result.success is True
        assert elapsed < 2.0, f"auto_layout took {elapsed:.2f}s for 500 nodes (limit 2s)"


# ---------------------------------------------------------------------------
# P2-T10 — Default grid_size=240 snapping
# ---------------------------------------------------------------------------

class TestDefaultGridSize:
    def test_default_grid_size_is_240(self) -> None:
        """P2-T10: Default LayoutConfig.grid_size is 240px."""
        assert LayoutConfig().grid_size == 240.0

    def test_nodes_snap_to_240px_grid(self) -> None:
        """P2-T10: auto_layout with default config snaps all node origins to 240px multiples."""
        nodes = [
            mock_node("b1", "BusinessActor"),
            mock_node("b2", "BusinessActor"),
            mock_node("a1", "ApplicationComponent"),
        ]
        view = make_view(nodes)
        config = LayoutConfig(margin=0.0)  # default grid_size=240
        auto_layout(view, config)
        for node in nodes:
            assert node.x % 240 == 0, f"node.x={node.x} not multiple of 240"
            assert node.y % 240 == 0, f"node.y={node.y} not multiple of 240"


# ---------------------------------------------------------------------------
# P2-T11 — High-degree node row isolation
# ---------------------------------------------------------------------------

class TestHighDegreeIsolation:
    def test_high_degree_node_gets_isolation_gap(self) -> None:
        """P2-T11: high-degree node (degree >= 5) has at least 1 grid-cell gap to neighbors."""
        from src.pyArchimate.view.layout.layout_engine import assign_grid_cells

        # 1 high-degree node + 2 normal nodes in same layer
        nodes = [
            mock_node("hub", "ApplicationComponent"),
            mock_node("n1",  "ApplicationComponent"),
            mock_node("n2",  "ApplicationComponent"),
        ]
        # hub has degree 5 (high), others have degree 1
        degrees = {"hub": 5, "n1": 1, "n2": 1}
        assignments = assign_grid_cells(
            nodes,
            grid_size=240.0,
            layer_direction="vertical",
            node_degrees=degrees,
            high_degree_threshold=5,
        )
        hub_col = assignments["hub"][0]
        n1_col  = assignments["n1"][0]
        n2_col  = assignments["n2"][0]
        # hub must have at least 1 empty cell between it and any neighbor in same row
        for neighbor_col in (n1_col, n2_col):
            if assignments["hub"][1] == assignments[list({"n1","n2"} - {list({"n1","n2"})[0]})[0]][1]:
                # same row: check gap
                assert abs(hub_col - neighbor_col) >= 2, (
                    f"hub col={hub_col} too close to neighbor col={neighbor_col} (gap < 2 cells)"
                )

    def test_high_degree_threshold_default_is_5(self) -> None:
        """P2-T11: LayoutConfig.high_degree_threshold defaults to 5."""
        assert LayoutConfig().high_degree_threshold == 5

    def test_no_isolation_below_threshold(self) -> None:
        """P2-T11: nodes below threshold packed normally (no isolation gap)."""
        from src.pyArchimate.view.layout.layout_engine import assign_grid_cells

        nodes = [mock_node(f"n{i}", "ApplicationComponent") for i in range(4)]
        degrees = {f"n{i}": 2 for i in range(4)}  # all below threshold=5
        assignments = assign_grid_cells(
            nodes,
            grid_size=240.0,
            layer_direction="vertical",
            node_degrees=degrees,
            high_degree_threshold=5,
        )
        # All 4 nodes should fit in columns 0–3 (packed, no isolation gaps)
        cols = sorted(assignments[f"n{i}"][0] for i in range(4))
        assert cols == [0, 1, 2, 3], f"Expected packed cols [0,1,2,3] but got {cols}"

    def test_high_degree_node_not_adjacent_to_neighbor_in_same_row(self) -> None:
        """P2-T11: high-degree node has at least 1 cell gap; its col+1 is blocked."""
        from src.pyArchimate.view.layout.layout_engine import assign_grid_cells

        nodes = [
            mock_node("hub", "ApplicationComponent"),
            mock_node("after", "ApplicationComponent"),
        ]
        degrees = {"hub": 6, "after": 1}
        assignments = assign_grid_cells(
            nodes,
            grid_size=240.0,
            layer_direction="vertical",
            node_degrees=degrees,
            high_degree_threshold=5,
        )
        hub_col = assignments["hub"][0]
        after_col = assignments["after"][0]
        # after must not be immediately adjacent (col+1) to hub
        assert after_col >= hub_col + 2, (
            f"after_col={after_col} adjacent to hub_col={hub_col}; expected gap of ≥2"
        )
