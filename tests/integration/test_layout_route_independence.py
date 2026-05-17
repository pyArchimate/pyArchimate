"""Integration tests: auto_layout and auto_route do not touch each other's domain (SC-010)."""

from unittest.mock import MagicMock

from src.pyArchimate.view.layout import auto_layout, auto_route
from src.pyArchimate.view.layout.utils.geometry import Point


def mock_node(uuid: str, element_type: str = "BusinessActor",
              x: float = 0, y: float = 0, w: float = 120, h: float = 55) -> MagicMock:
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


def mock_connection(uuid: str, src: str, tgt: str) -> MagicMock:
    c = MagicMock()
    c.uuid = uuid
    c._source = src
    c._target = tgt
    c.bendpoints = [Point(50, 50), Point(150, 50)]

    def _add(*pts: Point) -> None:
        for p in pts:
            c.bendpoints.append(p)

    def _remove_all() -> None:
        c.bendpoints.clear()

    c.add_bendpoint.side_effect = _add
    c.remove_all_bendpoints.side_effect = _remove_all
    return c


def make_view(nodes: list, connections: list | None = None) -> MagicMock:
    view = MagicMock()
    view.uuid = "v-independence"
    view.nodes = nodes
    view.nodes_dict = {n.uuid: n for n in nodes}
    view.conns = list(connections or [])
    view.conns_dict = {c.uuid: c for c in (connections or [])}
    return view


class TestLayoutDoesNotTouchWaypoints:
    """T046 — auto_layout must not modify any connection bendpoints."""

    def test_waypoints_unchanged_after_auto_layout(self) -> None:  # [P]
        nodes = [
            mock_node("n1", "BusinessActor", x=100, y=200),
            mock_node("n2", "ApplicationComponent", x=300, y=400),
        ]
        conn = mock_connection("c1", "n1", "n2")
        original_bps = [(p.x, p.y) for p in conn.bendpoints]
        view = make_view(nodes, [conn])

        auto_layout(view)

        after_bps = [(p.x, p.y) for p in conn.bendpoints]
        assert after_bps == original_bps, \
            "auto_layout must not modify connection bendpoints"


class TestRoutingDoesNotTouchNodePositions:
    """T046 — auto_route must not modify any node (x, y)."""

    def test_node_positions_unchanged_after_auto_route(self) -> None:  # [P]
        nodes = [
            mock_node("n1", "BusinessActor", x=0, y=0),
            mock_node("n2", "ApplicationComponent", x=400, y=400),
        ]
        original_positions = {n.uuid: (n.x, n.y) for n in nodes}
        conn = mock_connection("c1", "n1", "n2")
        view = make_view(nodes, [conn])

        auto_route(view)

        for n in nodes:
            assert (n.x, n.y) == original_positions[n.uuid], \
                f"auto_route changed position of node {n.uuid}"


class TestIdempotentLayout:
    """T047 — calling auto_layout twice gives identical node positions."""

    def test_auto_layout_is_idempotent(self) -> None:  # [P]
        nodes = [
            mock_node(f"n{i}", "BusinessActor") for i in range(10)
        ]
        view = make_view(nodes)
        auto_layout(view)
        positions_first = {n.uuid: (n.x, n.y) for n in nodes}
        auto_layout(view)
        positions_second = {n.uuid: (n.x, n.y) for n in nodes}
        assert positions_first == positions_second, \
            "auto_layout is not idempotent — positions differ on second call"
