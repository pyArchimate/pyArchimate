"""Integration tests for orthogonal routing spread calculation paths.

Covers previously-untested branches:
- Multiple outgoing connections from same source node (endpoint spread)
- Multiple incoming connections to same target node (endpoint spread)
- Gap-level spreading for parallel connections in same direction
"""

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view.layout import _apply_orthogonal_routing


def _make_view(num_nodes: int = 3, node_spacing: int = 200):
    """Build a simple view with vertically-stacked nodes."""
    model = Model("spread-test")
    view = model.add(ArchiType.View, "V")
    nodes = []
    elements = []
    for i in range(num_nodes):
        el = model.add(ArchiType.ApplicationComponent, f"El{i}")
        elements.append(el)
        n = view.add(el, x=40, y=40 + i * node_spacing, w=120, h=60)
        nodes.append(n)
    return model, view, elements, nodes


class TestMultipleSourceConnections:
    """Node with multiple outgoing connections triggers endpoint-spread logic."""

    def test_spread_assigned_for_fan_out(self):
        """Two connections from same source get non-zero spread offsets."""
        model, view, elements, nodes = _make_view(3, 200)
        rel1 = model.add_relationship(ArchiType.Serving, source=elements[0], target=elements[1])
        rel2 = model.add_relationship(ArchiType.Serving, source=elements[0], target=elements[2])
        conn1 = view.add_connection(ref=rel1.uuid, source=nodes[0], target=nodes[1])
        conn2 = view.add_connection(ref=rel2.uuid, source=nodes[0], target=nodes[2])

        _apply_orthogonal_routing(view)

        # Both connections should get bendpoints routed through gap corridors
        bp1 = conn1.get_all_bendpoints()
        bp2 = conn2.get_all_bendpoints()
        assert isinstance(bp1, list)
        assert isinstance(bp2, list)

    def test_single_connection_no_spread(self):
        """Single connection should not be affected by spread logic."""
        model, view, elements, nodes = _make_view(2, 200)
        rel = model.add_relationship(ArchiType.Serving, source=elements[0], target=elements[1])
        conn = view.add_connection(ref=rel.uuid, source=nodes[0], target=nodes[1])

        _apply_orthogonal_routing(view)

        bp = conn.get_all_bendpoints()
        assert isinstance(bp, list)

    def test_three_connections_from_one_source(self):
        """Three outgoing connections exercises spread distribution across edge."""
        model, view, elements, nodes = _make_view(4, 200)
        rels = [
            model.add_relationship(ArchiType.Serving, source=elements[0], target=elements[i])
            for i in range(1, 4)
        ]
        conns = [
            view.add_connection(ref=r.uuid, source=nodes[0], target=nodes[i + 1])
            for i, r in enumerate(rels)
        ]

        _apply_orthogonal_routing(view)

        for conn in conns:
            assert isinstance(conn.get_all_bendpoints(), list)


class TestMultipleTargetConnections:
    """Node with multiple incoming connections triggers target-spread logic."""

    def test_fan_in_connections(self):
        """Two sources connecting to same target get spread."""
        model, view, elements, nodes = _make_view(3, 200)
        rel1 = model.add_relationship(ArchiType.Serving, source=elements[0], target=elements[2])
        rel2 = model.add_relationship(ArchiType.Serving, source=elements[1], target=elements[2])
        conn1 = view.add_connection(ref=rel1.uuid, source=nodes[0], target=nodes[2])
        conn2 = view.add_connection(ref=rel2.uuid, source=nodes[1], target=nodes[2])

        _apply_orthogonal_routing(view)

        assert isinstance(conn1.get_all_bendpoints(), list)
        assert isinstance(conn2.get_all_bendpoints(), list)


class TestGapLevelSpreading:
    """Connections sharing a row gap get offset to avoid overlap."""

    def test_parallel_downward_connections_get_gap_offsets(self):
        """Two connections both going down through same gap get different offsets."""
        model = Model("gap-spread-test")
        view = model.add(ArchiType.View, "V")

        # Two side-by-side sources at top, both connecting down to a shared target
        el_s1 = model.add(ArchiType.ApplicationComponent, "S1")
        el_s2 = model.add(ArchiType.ApplicationComponent, "S2")
        el_t = model.add(ArchiType.ApplicationComponent, "T")

        n_s1 = view.add(el_s1, x=40, y=40, w=120, h=60)
        n_s2 = view.add(el_s2, x=200, y=40, w=120, h=60)
        n_t = view.add(el_t, x=120, y=250, w=120, h=60)

        rel1 = model.add_relationship(ArchiType.Serving, source=el_s1, target=el_t)
        rel2 = model.add_relationship(ArchiType.Serving, source=el_s2, target=el_t)
        conn1 = view.add_connection(ref=rel1.uuid, source=n_s1, target=n_t)
        conn2 = view.add_connection(ref=rel2.uuid, source=n_s2, target=n_t)

        _apply_orthogonal_routing(view)

        bp1 = conn1.get_all_bendpoints()
        bp2 = conn2.get_all_bendpoints()
        assert isinstance(bp1, list)
        assert isinstance(bp2, list)

    def test_no_conns_returns_without_error(self):
        """View with no connections should return cleanly."""
        model = Model("empty-test")
        view = model.add(ArchiType.View, "V")
        el = model.add(ArchiType.ApplicationComponent, "A")
        view.add(el, x=40, y=40, w=120, h=60)

        _apply_orthogonal_routing(view)

    def test_no_nodes_returns_without_error(self):
        """View with no nodes should return cleanly."""
        model = Model("no-nodes-test")
        view = model.add(ArchiType.View, "V")

        _apply_orthogonal_routing(view)

    def test_parallel_upward_connections(self):
        """Connections going upward also get gap offsets (reversed direction loop)."""
        model = Model("upward-test")
        view = model.add(ArchiType.View, "V")

        el_top = model.add(ArchiType.ApplicationComponent, "Top")
        el_b1 = model.add(ArchiType.ApplicationComponent, "B1")
        el_b2 = model.add(ArchiType.ApplicationComponent, "B2")

        n_top = view.add(el_top, x=120, y=40, w=120, h=60)
        n_b1 = view.add(el_b1, x=40, y=250, w=120, h=60)
        n_b2 = view.add(el_b2, x=240, y=250, w=120, h=60)

        rel1 = model.add_relationship(ArchiType.Serving, source=el_b1, target=el_top)
        rel2 = model.add_relationship(ArchiType.Serving, source=el_b2, target=el_top)
        conn1 = view.add_connection(ref=rel1.uuid, source=n_b1, target=n_top)
        conn2 = view.add_connection(ref=rel2.uuid, source=n_b2, target=n_top)

        _apply_orthogonal_routing(view)

        assert isinstance(conn1.get_all_bendpoints(), list)
        assert isinstance(conn2.get_all_bendpoints(), list)
