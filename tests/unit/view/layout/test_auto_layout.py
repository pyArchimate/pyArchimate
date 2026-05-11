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
