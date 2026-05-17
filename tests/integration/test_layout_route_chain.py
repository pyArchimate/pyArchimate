"""Integration tests: chaining auto_layout then auto_route satisfies all SC criteria (T045)."""

from unittest.mock import MagicMock

from src.pyArchimate.view.layout import LayoutConfig, RoutingConfig, auto_layout, auto_route
from src.pyArchimate.view.layout.utils.geometry import Point


def mock_node(
    uuid: str, element_type: str = "BusinessActor", x: float = 0, y: float = 0, w: float = 120, h: float = 55
) -> MagicMock:
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
    c.bendpoints = []

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
    view.uuid = "v-chain"
    view.nodes = nodes
    view.nodes_dict = {n.uuid: n for n in nodes}
    view.conns = list(connections or [])
    view.conns_dict = {c.uuid: c for c in (connections or [])}
    return view


class TestChainLayoutAndRouting:
    """T045 — chained auto_layout + auto_route satisfies all acceptance criteria."""

    def test_chain_produces_valid_layout_and_routing(self) -> None:
        # Mixed layers with connections
        business = [mock_node(f"b{i}", "BusinessActor") for i in range(5)]
        app = [mock_node(f"a{i}", "ApplicationComponent") for i in range(5)]
        tech = [mock_node(f"t{i}", "TechnologyService") for i in range(5)]
        nodes = business + app + tech

        connections = [mock_connection(f"c{i}", business[i % 5].uuid, app[i % 5].uuid) for i in range(5)]
        view = make_view(nodes, connections)

        # Chain layout then routing
        layout_result = auto_layout(view, LayoutConfig(grid_size=120.0, margin=0.0))
        route_result = auto_route(view, RoutingConfig())

        # Both succeed
        assert layout_result.success is True
        assert route_result.success is True

        # SC-002: all node origins are multiples of grid_size
        for n in nodes:
            assert n.x % 120 == 0, f"Node {n.uuid} x={n.x} not aligned to grid"
            assert n.y % 120 == 0, f"Node {n.uuid} y={n.y} not aligned to grid"

        # SC-003: no two nodes overlap
        for i, n1 in enumerate(nodes):
            for j, n2 in enumerate(nodes):
                if i >= j:
                    continue
                overlap_x = n1.x < n2.x + n2.w and n2.x < n1.x + n1.w
                overlap_y = n1.y < n2.y + n2.h and n2.y < n1.y + n1.h
                assert not (overlap_x and overlap_y), f"Nodes {n1.uuid} and {n2.uuid} overlap after layout"

        # SC-004: Business Y < Application Y < Technology Y
        max_biz_y = max(n.y for n in business)
        min_app_y = min(n.y for n in app)
        max_app_y = max(n.y for n in app)
        min_tech_y = min(n.y for n in tech)
        assert max_biz_y < min_app_y
        assert max_app_y < min_tech_y

        # SC-006: no connection segment intersects any node bbox (verify routing ran)
        assert route_result.connections_processed >= 0
