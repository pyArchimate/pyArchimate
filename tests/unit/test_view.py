"""Tests for View/Node/Connection/Profile implementations."""
from typing import cast

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import (
    Connection,
    Node,
    Point,
    Position,
    Profile,
    View,
    default_color,
)


# ---------------------------------------------------------------------------
# Basic import tests
# ---------------------------------------------------------------------------

def test_view_importable():
    """View, Node, Connection, Profile are importable from src.pyArchimate.view."""
    assert View is not None
    assert Node is not None
    assert Connection is not None
    assert Profile is not None


# ---------------------------------------------------------------------------
# default_color (view module version)
# ---------------------------------------------------------------------------

def test_view_default_color_archi_theme():
    assert default_color('ApplicationComponent', 'archi') == '#B5FFFF'


def test_view_default_color_none_theme():
    result = default_color('ApplicationComponent', None)
    assert result.startswith('#')


def test_view_default_color_aris_theme():
    assert default_color('ApplicationComponent', 'aris') == '#00A0FF'


def test_view_default_color_custom_dict():
    assert default_color('ApplicationComponent', {'application': '#AABB00'}) == '#AABB00'


def test_view_default_color_custom_dict_missing_key():
    result = default_color('ApplicationComponent', {})
    assert result.startswith('#')


def test_view_default_color_unknown_type():
    assert default_color('NotAType') == '#FFFFFF'


# ---------------------------------------------------------------------------
# Point
# ---------------------------------------------------------------------------

def test_point_x_setter():
    p = Point(10, 20)
    p.x = 50
    assert p.x == 50


def test_point_y_setter():
    p = Point(10, 20)
    p.y = 99
    assert p.y == 99


def test_point_negative_clamped():
    p = Point(10, 10)
    p.x = -5
    assert p.x == 0
    p.y = -3
    assert p.y == 0


# ---------------------------------------------------------------------------
# Position
# ---------------------------------------------------------------------------

def test_position_init():
    pos = Position()
    assert pos.dx is None
    assert pos.dy is None
    assert pos.gap_x == 0
    assert pos.gap_y == 0
    assert pos.angle is None
    assert pos.orientation == ""


def test_position_dist_none_when_unset():
    pos = Position()
    assert pos.dist is None


def test_position_dist_computed():
    pos = Position()
    pos.dx = 3.0
    pos.dy = 4.0
    assert abs(pos.dist - 5.0) < 1e-9


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

def test_profile_missing_name_raises():
    with pytest.raises(ValueError):
        Profile(name=None, concept='ApplicationComponent')


def test_profile_missing_concept_raises():
    with pytest.raises(ValueError):
        Profile(name='P', concept=None)


def test_profile_invalid_concept_raises():
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    with pytest.raises(ArchimateConceptTypeError):
        Profile(name='P', concept='NotAType')


def test_profile_view_concept_raises():
    with pytest.raises(ValueError):
        Profile(name='P', concept='View')


def test_profile_delete_clears_references():
    m = Model('prof-test')
    e = m.add(ArchiType.ApplicationComponent, 'App')
    e.set_profile('ToDelete')
    profile = m.get_profile('ToDelete')
    assert profile is not None
    profile_id = profile.uuid
    profile.delete()
    assert profile_id not in m._profiles_dict
    assert e.profile_name is None


# ---------------------------------------------------------------------------
# Fixtures for View/Node/Connection tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_view():
    """A model with two elements and a view containing two connected nodes."""
    m = Model('view-test')
    a = m.add(ArchiType.ApplicationComponent, 'CompA')
    b = m.add(ArchiType.ApplicationService, 'SvcB')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b)
    v = cast(View, m.add(ArchiType.View, 'TestView'))
    na = v.add(ref=a.uuid, x=10, y=10, w=120, h=55)
    nb = v.add(ref=b.uuid, x=200, y=10, w=120, h=55)
    conn = v.add_connection(ref=rel.uuid, source=na, target=nb)
    return m, v, a, b, rel, na, nb, conn


# ---------------------------------------------------------------------------
# View operations
# ---------------------------------------------------------------------------

def test_view_type_is_diagram(simple_view):
    _, v, *_ = simple_view
    assert v.type == 'Diagram'


def test_view_prop_set_get(simple_view):
    _, v, *_ = simple_view
    v.prop('color', 'blue')
    assert v.prop('color') == 'blue'


def test_view_prop_missing_returns_none(simple_view):
    _, v, *_ = simple_view
    assert v.prop('ghost') is None


def test_view_remove_prop(simple_view):
    _, v, *_ = simple_view
    v.prop('tmp', '1')
    v.remove_prop('tmp')
    assert v.prop('tmp') is None


def test_view_remove_folder(simple_view):
    _, v, *_ = simple_view
    v.folder = '/Views'
    v.remove_folder()
    assert v.folder is None


def test_view_props_returns_dict(simple_view):
    _, v, *_ = simple_view
    assert isinstance(v.props, dict)


def test_view_delete_removes_from_model(simple_view):
    m, v, *_ = simple_view
    view_id = v.uuid
    v.delete()
    assert view_id not in m.views_dict


def test_view_get_or_create_node_found(simple_view):
    _, v, a, *_ = simple_view
    node = v.get_or_create_node(elem=a)
    assert node is not None
    assert node.ref == a.uuid


def test_view_get_or_create_node_not_found_no_create(simple_view):
    m, v, *_ = simple_view
    result = v.get_or_create_node(elem='Ghost', elem_type=ArchiType.ApplicationComponent)
    assert result is None


def test_view_get_or_create_node_create_elem_and_node(simple_view):
    m, v, *_ = simple_view
    node = v.get_or_create_node(
        elem='NewComp',
        elem_type=ArchiType.ApplicationComponent,
        create_elem=True,
        create_node=True,
    )
    assert node is not None


def test_view_get_or_create_node_create_node_only(simple_view):
    m, v, a, *_ = simple_view
    # Remove existing node first
    existing = v.get_or_create_node(elem=a)
    existing.delete()
    node = v.get_or_create_node(elem=a, create_node=True)
    assert node is not None


def test_view_get_or_create_connection_found(simple_view):
    _, v, a, b, rel, na, nb, conn = simple_view
    found = v.get_or_create_connection(rel=rel, source=na, target=nb)
    assert found is conn


def test_view_get_or_create_connection_none_rel_none_source():
    m = Model('gc-test')
    v = cast(View, m.add(ArchiType.View, 'V'))
    result = v.get_or_create_connection(rel=None, source=None, target=None)
    assert result is None


def test_view_get_or_create_connection_create(simple_view):
    m, v, a, b, rel, na, nb, conn = simple_view
    c2 = m.add(ArchiType.ApplicationFunction, 'FuncC')
    rel2 = m.add_relationship(ArchiType.Serving, source=a, target=c2)
    nc = v.add(ref=c2.uuid, x=400, y=10, w=120, h=55)
    result = v.get_or_create_connection(rel=None, source=na, target=nc,
                                        rel_type=ArchiType.Serving, create_conn=True)
    assert result is not None


def test_view_get_or_create_connection_no_rel_type_returns_none(simple_view):
    _, v, a, b, rel, na, nb, _ = simple_view
    result = v.get_or_create_connection(rel=None, source=na, target=nb, rel_type=None)
    assert result is None


# ---------------------------------------------------------------------------
# Node operations
# ---------------------------------------------------------------------------

def test_node_name_for_element(simple_view):
    _, _, a, _, _, na, *_ = simple_view
    assert na.name == a.name


def test_node_name_for_container(simple_view):
    _, v, *_ = simple_view
    container = v.add(ref=None, node_type='Container', label='MyGroup')
    assert container.name is None


def test_node_type_for_element(simple_view):
    _, _, a, _, _, na, *_ = simple_view
    assert na.type == a.type


def test_node_type_for_container(simple_view):
    _, v, *_ = simple_view
    container = v.add(ref=None, node_type='Container', label='C')
    assert container.type is None


def test_node_desc(simple_view):
    _, _, a, _, _, na, *_ = simple_view
    a.desc = 'test desc'
    assert na.desc == 'test desc'


def test_node_ref_setter_with_element(simple_view):
    m, v, a, b, *_ = simple_view
    c = m.add(ArchiType.ApplicationComponent, 'Another')
    na = v.add(ref=a.uuid, x=0, y=0)
    na.ref = c
    assert na.ref == c.uuid


def test_node_ref_setter_with_uuid_string(simple_view):
    m, v, a, b, *_ = simple_view
    c = m.add(ArchiType.ApplicationComponent, 'Another2')
    na = v.add(ref=a.uuid, x=0, y=0)
    na.ref = c.uuid
    assert na.ref == c.uuid


def test_node_getnodes_no_filter(simple_view):
    _, v, a, *_ = simple_view
    na = v.nodes[0]
    result = na.getnodes()
    assert isinstance(result, list)


def test_node_getnodes_with_type(simple_view):
    _, v, a, *_ = simple_view
    na = v.nodes[0]
    result = na.getnodes(elem_type=ArchiType.ApplicationComponent)
    assert isinstance(result, list)


def test_node_is_inside_true(simple_view):
    _, _, _, _, _, na, *_ = simple_view
    # na is at x=10, y=10, w=120, h=55 → cx=70, cy=37.5
    assert na.is_inside(70, 37) is True


def test_node_is_inside_false(simple_view):
    _, _, _, _, _, na, *_ = simple_view
    assert na.is_inside(500, 500) is False


def test_node_is_inside_with_point(simple_view):
    _, _, _, _, _, na, *_ = simple_view
    p = Point(70, 37)
    assert na.is_inside(point=p) is True


def test_node_conns_unfiltered(simple_view):
    _, _, _, _, _, na, nb, conn = simple_view
    result = na.conns()
    assert conn in result


def test_node_conns_filtered_by_type(simple_view):
    _, _, _, _, _, na, nb, conn = simple_view
    result = na.conns(rel_type=ArchiType.Serving)
    assert conn in result


def test_node_in_conns(simple_view):
    _, _, _, _, _, na, nb, conn = simple_view
    result = nb.in_conns()
    assert conn in result


def test_node_in_conns_filtered(simple_view):
    _, _, _, _, _, na, nb, conn = simple_view
    result = nb.in_conns(rel_type=ArchiType.Serving)
    assert conn in result


def test_node_out_conns(simple_view):
    _, _, _, _, _, na, nb, conn = simple_view
    result = na.out_conns()
    assert conn in result


def test_node_out_conns_filtered(simple_view):
    _, _, _, _, _, na, nb, conn = simple_view
    result = na.out_conns(rel_type=ArchiType.Serving)
    assert conn in result


def test_node_delete_removes_connection(simple_view):
    m, v, a, b, rel, na, nb, conn = simple_view
    conn_id = conn.uuid
    na.delete()
    assert conn_id not in v.conns_dict


# ---------------------------------------------------------------------------
# Connection operations
# ---------------------------------------------------------------------------

def test_connection_name(simple_view):
    _, _, _, _, rel, _, _, conn = simple_view
    assert conn.name == rel.name


def test_connection_type(simple_view):
    _, _, _, _, rel, _, _, conn = simple_view
    assert conn.type == rel.type


def test_connection_access_type(simple_view):
    m, v, a, b, rel, na, nb, _ = simple_view
    data = m.add(ArchiType.DataObject, 'D')
    access_rel = m.add_relationship(ArchiType.Access, source=a, target=data)
    nd = v.add(ref=data.uuid, x=350, y=10, w=120, h=55)
    c = v.add_connection(ref=access_rel.uuid, source=na, target=nd)
    access_rel.access_type = 'Read'
    assert c.access_type == 'Read'


def test_connection_is_directed(simple_view):
    m, v, a, b, rel, na, nb, _ = simple_view
    c2 = m.add(ArchiType.ApplicationFunction, 'F')
    assoc = m.add_relationship(ArchiType.Association, source=a, target=c2)
    nf = v.add(ref=c2.uuid, x=350, y=10, w=120, h=55)
    conn = v.add_connection(ref=assoc.uuid, source=na, target=nf)
    assoc.is_directed = True
    assert conn.is_directed is not None


def test_connection_influence_strength(simple_view):
    m, v, a, b, rel, na, nb, _ = simple_view
    c3 = m.add(ArchiType.ApplicationFunction, 'G')
    inf_rel = m.add_relationship(ArchiType.Influence, source=b, target=c3)
    ng = v.add(ref=c3.uuid, x=350, y=10, w=120, h=55)
    conn = v.add_connection(ref=inf_rel.uuid, source=nb, target=ng)
    inf_rel.influence_strength = '7'
    assert conn.influence_strength == '7'


def test_connection_ref_setter(simple_view):
    m, v, a, b, rel, na, nb, conn = simple_view
    c = m.add(ArchiType.ApplicationFunction, 'H')
    rel2 = m.add_relationship(ArchiType.Serving, source=a, target=c)
    conn.ref = rel2.uuid
    assert conn.ref == rel2.uuid


def test_connection_source_setter_with_node(simple_view):
    m, v, a, b, rel, na, nb, conn = simple_view
    c = m.add(ArchiType.ApplicationComponent, 'Cx')
    nc = v.add(ref=c.uuid, x=0, y=100, w=120, h=55)
    conn.source = nc
    assert conn._source == nc.uuid


def test_connection_target_setter_with_node(simple_view):
    m, v, a, b, rel, na, nb, conn = simple_view
    c = m.add(ArchiType.ApplicationService, 'Cy')
    nc = v.add(ref=c.uuid, x=0, y=200, w=120, h=55)
    conn.target = nc
    assert conn._target == nc.uuid


def test_connection_set_bendpoint(simple_view):
    _, _, _, _, _, _, _, conn = simple_view
    conn.add_bendpoint(Point(50, 50))
    conn.set_bendpoint(Point(99, 99), 0)
    assert conn.bendpoints[0].x == 99


def test_connection_get_bendpoint(simple_view):
    _, _, _, _, _, _, _, conn = simple_view
    conn.add_bendpoint(Point(10, 20))
    bp = conn.get_bendpoint(0)
    assert bp is not None
    assert bp.x == 10


def test_connection_get_bendpoint_out_of_range(simple_view):
    _, _, _, _, _, _, _, conn = simple_view
    assert conn.get_bendpoint(99) is None


def test_connection_del_bendpoint(simple_view):
    _, _, _, _, _, _, _, conn = simple_view
    conn.add_bendpoint(Point(1, 2))
    conn.del_bendpoint(0)
    assert len(conn.bendpoints) == 0


def test_connection_get_all_bendpoints(simple_view):
    _, _, _, _, _, _, _, conn = simple_view
    conn.add_bendpoint(Point(1, 2))
    conn.add_bendpoint(Point(3, 4))
    bps = conn.get_all_bendpoints()
    assert len(bps) == 2


def test_connection_remove_all_bendpoints(simple_view):
    _, _, _, _, _, _, _, conn = simple_view
    conn.add_bendpoint(Point(1, 2))
    conn.remove_all_bendpoints()
    assert conn.bendpoints == []


def test_connection_delete(simple_view):
    m, v, a, b, rel, na, nb, conn = simple_view
    conn_id = conn.uuid
    conn.delete()
    assert conn_id not in v.conns_dict
    assert conn_id not in m.conns_dict


# ---------------------------------------------------------------------------
# Node geometry setters — negative clamping and child propagation
# ---------------------------------------------------------------------------

def test_node_x_setter_negative_clamped(simple_view):
    _, _, _, _, _, na, *_ = simple_view
    na.x = -10
    assert na.x == 0


def test_node_y_setter_negative_clamped(simple_view):
    _, _, _, _, _, na, *_ = simple_view
    na.y = -5
    assert na.y == 0


def test_node_cx_setter(simple_view):
    _, _, _, _, _, na, *_ = simple_view
    na.cx = 200.0
    assert abs(na.cx - 200.0) < 1.0


def test_node_cx_setter_negative(simple_view):
    _, _, _, _, _, na, *_ = simple_view
    na.cx = -50.0
    assert na.x == 0


def test_node_cy_setter(simple_view):
    _, _, _, _, _, na, *_ = simple_view
    na.cy = 100.0
    assert abs(na.cy - 100.0) < 1.0


def test_node_cy_setter_negative(simple_view):
    _, _, _, _, _, na, *_ = simple_view
    na.cy = -50.0
    assert na.y == 0


def test_node_fill_color_none_uses_default(simple_view):
    _, _, _, _, _, na, *_ = simple_view
    na.fill_color = None
    # Should set a default color string
    assert na.fill_color is not None and na.fill_color.startswith('#')


# ---------------------------------------------------------------------------
# Nested nodes — rx, ry, x/y child propagation
# ---------------------------------------------------------------------------

@pytest.fixture()
def view_with_nested_node():
    """A view containing a parent node with one embedded child."""
    m = Model('nested-test')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationComponent, 'Child')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_node = v.add(ref=a.uuid, x=100, y=100, w=300, h=200)
    child_node = parent_node.add(ref=b.uuid, x=120, y=120, w=100, h=55)
    return m, v, a, b, parent_node, child_node


def test_nested_node_rx_returns_relative(view_with_nested_node):
    _, _, _, _, parent_node, child_node = view_with_nested_node
    assert child_node.rx == child_node.x - parent_node.x


def test_nested_node_ry_returns_relative(view_with_nested_node):
    _, _, _, _, parent_node, child_node = view_with_nested_node
    assert child_node.ry == child_node.y - parent_node.y


def test_nested_node_rx_setter(view_with_nested_node):
    _, _, _, _, parent_node, child_node = view_with_nested_node
    child_node.rx = 20
    assert child_node.x == parent_node.x + 20


def test_nested_node_ry_setter(view_with_nested_node):
    _, _, _, _, parent_node, child_node = view_with_nested_node
    child_node.ry = 30
    assert child_node.y == parent_node.y + 30


def test_nested_node_rx_setter_negative(view_with_nested_node):
    _, _, _, _, parent_node, child_node = view_with_nested_node
    child_node.rx = -5
    assert child_node.rx == 0


def test_nested_node_ry_setter_negative(view_with_nested_node):
    _, _, _, _, parent_node, child_node = view_with_nested_node
    child_node.ry = -5
    assert child_node.ry == 0


def test_parent_node_x_setter_propagates_to_child(view_with_nested_node):
    _, _, _, _, parent_node, child_node = view_with_nested_node
    old_child_x = child_node.x
    parent_node.x = parent_node.x + 50
    assert child_node.x == old_child_x + 50


def test_parent_node_y_setter_propagates_to_child(view_with_nested_node):
    _, _, _, _, parent_node, child_node = view_with_nested_node
    old_child_y = child_node.y
    parent_node.y = parent_node.y + 50
    assert child_node.y == old_child_y + 50


def test_node_add_with_nested_rel_type(view_with_nested_node):
    m, v, a, b, parent_node, _ = view_with_nested_node
    c = m.add(ArchiType.ApplicationComponent, 'Another')
    child2 = parent_node.add(ref=c.uuid, x=10, y=10, nested_rel_type=ArchiType.Composition)
    assert child2 is not None
    # A composition relationship should have been created
    assert any(r.type == ArchiType.Composition for r in m.relationships)


def test_node_delete_with_children(view_with_nested_node):
    m, v, a, b, parent_node, child_node = view_with_nested_node
    child_id = child_node.uuid
    parent_node.delete(recurse=True)
    assert child_id not in m.nodes_dict


# ---------------------------------------------------------------------------
# Connection shape methods
# ---------------------------------------------------------------------------

def test_connection_l_shape(simple_view):
    _, _, _, _, _, na, nb, conn = simple_view
    conn.l_shape(direction=0)
    # If nodes don't overlap at those coords, a bendpoint is added
    assert isinstance(conn.bendpoints, list)


def test_connection_l_shape_direction1(simple_view):
    _, _, _, _, _, na, nb, conn = simple_view
    conn.l_shape(direction=1)
    assert isinstance(conn.bendpoints, list)


def test_connection_s_shape(simple_view):
    _, _, _, _, _, na, nb, conn = simple_view
    conn.s_shape(direction=0)
    assert isinstance(conn.bendpoints, list)


def test_connection_s_shape_direction1(simple_view):
    _, _, _, _, _, na, nb, conn = simple_view
    conn.s_shape(direction=1)
    assert isinstance(conn.bendpoints, list)


# ---------------------------------------------------------------------------
# Connection ref/source/target setter — object (hasattr) paths
# ---------------------------------------------------------------------------

def test_connection_ref_setter_with_relationship_object(simple_view):
    m, v, a, b, rel, na, nb, conn = simple_view
    c = m.add(ArchiType.ApplicationFunction, 'F')
    rel2 = m.add_relationship(ArchiType.Serving, source=a, target=c)
    conn.ref = rel2  # pass Relationship object (has .uuid)
    assert conn.ref == rel2.uuid


def test_connection_source_setter_with_string(simple_view):
    m, v, a, b, rel, na, nb, conn = simple_view
    c = m.add(ArchiType.ApplicationComponent, 'Cx')
    nc = v.add(ref=c.uuid, x=0, y=100, w=120, h=55)
    conn.source = nc.uuid  # plain string — falls through to else
    assert conn._source == nc.uuid


def test_connection_target_setter_with_string(simple_view):
    m, v, a, b, rel, na, nb, conn = simple_view
    c = m.add(ArchiType.ApplicationService, 'Cy')
    nc = v.add(ref=c.uuid, x=0, y=200, w=120, h=55)
    conn.target = nc.uuid  # plain string — falls through to else
    assert conn._target == nc.uuid


def test_connection_source_setter_with_uuid_object(simple_view):
    """Covers the hasattr(elem, 'uuid') branch in Connection.source setter."""
    m, v, a, b, rel, na, nb, conn = simple_view

    class FakeNode:
        def __init__(self, uuid):
            self.uuid = uuid

    c = m.add(ArchiType.ApplicationComponent, 'Cz')
    nc = v.add(ref=c.uuid, x=0, y=300, w=120, h=55)
    conn.source = FakeNode(nc.uuid)
    assert conn._source == nc.uuid


def test_connection_target_setter_with_uuid_object(simple_view):
    """Covers the hasattr(elem, 'uuid') branch in Connection.target setter."""
    m, v, a, b, rel, na, nb, conn = simple_view

    class FakeNode:
        def __init__(self, uuid):
            self.uuid = uuid

    c = m.add(ArchiType.ApplicationService, 'Cw')
    nc = v.add(ref=c.uuid, x=0, y=400, w=120, h=55)
    conn.target = FakeNode(nc.uuid)
    assert conn._target == nc.uuid


# ---------------------------------------------------------------------------
# Profile.delete — covers relationship-profile loop (line 126)
# ---------------------------------------------------------------------------

def test_profile_delete_clears_relationship_profile():
    """Covers the relationship-loop body in Profile.delete (line 126)."""
    m = Model('prof-rel-test')
    a = m.add(ArchiType.ApplicationComponent, 'App')
    b = m.add(ArchiType.ApplicationService, 'Svc')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b)
    rel.set_profile('ByeProfile')
    profile = m.get_profile('ByeProfile')
    assert profile is not None
    profile.delete()
    assert rel.profile_name is None


# ---------------------------------------------------------------------------
# Node.__init__ error paths
# ---------------------------------------------------------------------------

def test_node_invalid_parent_raises():
    """Node requires a View/Node parent; plain string raises ValueError."""
    with pytest.raises(ValueError):
        Node(ref=None, parent="not_a_view")


def test_node_init_with_hasattr_ref():
    """Covers the hasattr(ref, 'uuid') branch in Node.__init__ (lines 169-170)."""
    m = Model('fake-ref-test')
    a = m.add(ArchiType.ApplicationComponent, 'App')
    v = cast(View, m.add(ArchiType.View, 'V'))

    class FakeRef:
        uuid = a.uuid

    n = v.add(ref=FakeRef(), x=0, y=0)
    assert n.ref == a.uuid


def test_node_init_with_invalid_ref_type_raises():
    """Covers the else: raise branch (line 172) when ref is not str/Element/has-uuid."""
    m = Model('bad-ref-test')
    v = cast(View, m.add(ArchiType.View, 'V'))
    with pytest.raises(ValueError):
        v.add(ref=42, x=0, y=0)  # int has no .uuid attribute


def test_node_init_elem_ref_not_in_model_raises():
    """Covers line 176: node_type='Element' but ref uuid not registered in model."""
    m = Model('bad-elem-ref')
    v = cast(View, m.add(ArchiType.View, 'V'))
    with pytest.raises(ValueError):
        v.add(ref='nonexistent-uuid', x=0, y=0)


# ---------------------------------------------------------------------------
# Node.delete(delete_from_model=True) — lines 219, 224-228
# ---------------------------------------------------------------------------

def test_node_delete_from_model_removes_element():
    """delete_from_model=True also removes the underlying Element (lines 219, 224-228)."""
    m = Model('del-model-test')
    a = m.add(ArchiType.ApplicationComponent, 'App')
    v = cast(View, m.add(ArchiType.View, 'V'))
    n = v.add(ref=a.uuid, x=0, y=0)
    a_uuid = a.uuid
    n_uuid = n.uuid
    n.delete(delete_from_model=True)
    assert n_uuid not in m.nodes_dict
    assert a_uuid not in m.elems_dict


# ---------------------------------------------------------------------------
# Node.concept property — KeyError path (lines 269-270)
# ---------------------------------------------------------------------------

def test_node_concept_invalid_ref_raises():
    """Covers ArchimateConceptTypeError raised when _ref is no longer in elems_dict."""
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    m = Model('bad-concept-test')
    a = m.add(ArchiType.ApplicationComponent, 'App')
    v = cast(View, m.add(ArchiType.View, 'V'))
    n = v.add(ref=a.uuid, x=0, y=0)
    n._ref = 'dangling-uuid'  # corrupt the reference
    with pytest.raises(ArchimateConceptTypeError):
        _ = n.concept


# ---------------------------------------------------------------------------
# Node.ref setter — hasattr(ref, 'uuid') branch (line 281)
# ---------------------------------------------------------------------------

def test_node_ref_setter_with_hasattr_obj():
    """Covers the hasattr(ref, 'uuid') branch in Node.ref setter (line 281)."""
    m = Model('ref-setter-test')
    a = m.add(ArchiType.ApplicationComponent, 'App')
    b = m.add(ArchiType.ApplicationComponent, 'App2')
    v = cast(View, m.add(ArchiType.View, 'V'))
    n = v.add(ref=a.uuid, x=0, y=0)

    class FakeElem:
        uuid = b.uuid

    n.ref = FakeElem()
    assert n.ref == b.uuid


# ---------------------------------------------------------------------------
# Node.rx / Node.ry — View parent (non-Node parent) paths
# ---------------------------------------------------------------------------

def test_node_rx_view_parent_returns_x():
    """Covers line 317: rx returns _x when parent is a View (not Node)."""
    m = Model('rx-view-test')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    v = cast(View, m.add(ArchiType.View, 'V'))
    n = v.add(ref=a.uuid, x=50, y=10)
    assert n.rx == 50  # parent is View → rx == x


def test_node_rx_setter_view_parent():
    """Covers line 326: rx setter sets x directly when parent is a View."""
    m = Model('rx-set-view-test')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    v = cast(View, m.add(ArchiType.View, 'V'))
    n = v.add(ref=a.uuid, x=50, y=10)
    n.rx = 100
    assert n.x == 100


def test_node_ry_view_parent_returns_y():
    """Covers line 356: ry returns _y when parent is a View (not Node)."""
    m = Model('ry-view-test')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    v = cast(View, m.add(ArchiType.View, 'V'))
    n = v.add(ref=a.uuid, x=10, y=70)
    assert n.ry == 70


def test_node_ry_setter_view_parent():
    """Covers line 365: ry setter sets y directly when parent is a View."""
    m = Model('ry-set-view-test')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    v = cast(View, m.add(ArchiType.View, 'V'))
    n = v.add(ref=a.uuid, x=10, y=70)
    n.ry = 200
    assert n.y == 200


# ---------------------------------------------------------------------------
# Node.get_or_create_node (Node method) — lines 420-436
# ---------------------------------------------------------------------------

def test_node_get_or_create_node_by_name_found():
    """String elem found → covers lines 422-424."""
    m = Model('gocn-found')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationComponent, 'Child')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=300, h=200)
    child_n = parent_n.add(ref=b.uuid, x=10, y=10)
    result = parent_n.get_or_create_node(
        elem='Child', elem_type=ArchiType.ApplicationComponent
    )
    assert result is child_n


def test_node_get_or_create_node_not_found_no_create():
    """String elem not found, create_elem=False → returns None (line 428)."""
    m = Model('gocn-none')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=300, h=200)
    result = parent_n.get_or_create_node(elem='Ghost', elem_type=ArchiType.ApplicationComponent)
    assert result is None


def test_node_get_or_create_node_create_elem_and_node():
    """create_elem=True creates element and child node (lines 425-426, 434-435)."""
    m = Model('gocn-create')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=300, h=200)
    result = parent_n.get_or_create_node(
        elem='NewChild',
        elem_type=ArchiType.ApplicationComponent,
        create_elem=True,
        create_node=True,
    )
    assert result is not None


def test_node_get_or_create_node_existing_child():
    """Elem object passed directly, node exists → returns it (lines 430, 432-433)."""
    m = Model('gocn-existing')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationComponent, 'Child')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=300, h=200)
    child_n = parent_n.add(ref=b.uuid, x=10, y=10)
    result = parent_n.get_or_create_node(elem=b)
    assert result is child_n


def test_node_get_or_create_node_create_node_only():
    """Elem object passed, no existing child node, create_node=True (line 434-435)."""
    m = Model('gocn-create-node')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationComponent, 'Child')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=300, h=200)
    result = parent_n.get_or_create_node(elem=b, create_node=True)
    assert result is not None


# ---------------------------------------------------------------------------
# Node.resize — lines 449-493
# ---------------------------------------------------------------------------

def test_node_resize_default():
    """resize() with default args (justify='left', sort='asc') — lines 449-485."""
    m = Model('resize-default')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationService, 'Child1')
    c = m.add(ArchiType.ApplicationComponent, 'Child2')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=400, h=300)
    parent_n.add(ref=b.uuid, x=10, y=10)
    parent_n.add(ref=c.uuid, x=150, y=10)
    parent_n.resize(max_in_row=2)
    assert parent_n.w > 0 and parent_n.h > 0


def test_node_resize_desc_sort():
    """resize() with sort='desc' — covers the 'desc' branch (line 458)."""
    m = Model('resize-desc')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationService, 'Child1')
    c = m.add(ArchiType.ApplicationComponent, 'Child2')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=400, h=300)
    parent_n.add(ref=b.uuid, x=10, y=10)
    parent_n.add(ref=c.uuid, x=150, y=10)
    parent_n.resize(sort='desc')
    assert parent_n.w > 0


def test_node_resize_no_sort():
    """resize() with unrecognised sort value — covers the else branch (line 460)."""
    m = Model('resize-none')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationService, 'Child1')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=400, h=300)
    parent_n.add(ref=b.uuid, x=10, y=10)
    parent_n.resize(sort='none')
    assert parent_n.w > 0


def test_node_resize_justify_center():
    """resize() with justify='center' — covers lines 475-476."""
    m = Model('resize-center')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationService, 'C1')
    c = m.add(ArchiType.ApplicationComponent, 'C2')
    d = m.add(ArchiType.ApplicationComponent, 'C3')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=500, h=300)
    parent_n.add(ref=b.uuid, x=10, y=10)
    parent_n.add(ref=c.uuid, x=150, y=10)
    parent_n.add(ref=d.uuid, x=290, y=10)
    parent_n.resize(max_in_row=2, justify='center')
    assert parent_n.w > 0


def test_node_resize_justify_right():
    """resize() with justify='right' — covers lines 486-493."""
    m = Model('resize-right')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationService, 'C1')
    c = m.add(ArchiType.ApplicationComponent, 'C2')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=400, h=300)
    parent_n.add(ref=b.uuid, x=10, y=10)
    parent_n.add(ref=c.uuid, x=150, y=10)
    parent_n.resize(max_in_row=2, justify='right')
    assert parent_n.w > 0


def test_node_resize_with_recurse():
    """resize(recurse=True) — covers the recurse branch (line 463)."""
    m = Model('resize-recurse')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationService, 'Child')
    c = m.add(ArchiType.ApplicationComponent, 'GrandChild')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=400, h=300)
    child_n = parent_n.add(ref=b.uuid, x=10, y=10, w=200, h=150)
    child_n.add(ref=c.uuid, x=20, y=20)
    parent_n.resize(recurse=True)
    assert parent_n.w > 0


# ---------------------------------------------------------------------------
# Node.get_obj_pos — lines 521-560
# ---------------------------------------------------------------------------

@pytest.fixture()
def two_spaced_nodes():
    """Two nodes far apart to exercise get_obj_pos orientations."""
    m = Model('obj-pos-test')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    v = cast(View, m.add(ArchiType.View, 'V'))
    # A to the left, B to the right, vertically aligned
    na = v.add(ref=a.uuid, x=0, y=200, w=120, h=55)
    nb = v.add(ref=b.uuid, x=300, y=200, w=120, h=55)
    return m, v, na, nb


def test_get_obj_pos_right(two_spaced_nodes):
    """B is to the right of A → orientation 'R'."""
    _, _, na, nb = two_spaced_nodes
    pos = na.get_obj_pos(nb)
    assert 'R' in pos.orientation or pos.orientation in ('R', 'R!')


def test_get_obj_pos_left(two_spaced_nodes):
    """A is to the left of B → orientation 'L' from B's perspective."""
    _, _, na, nb = two_spaced_nodes
    pos = nb.get_obj_pos(na)
    assert 'L' in pos.orientation


def test_get_obj_pos_below():
    """B is directly below A → orientation 'B'."""
    m = Model('obj-pos-below')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    v = cast(View, m.add(ArchiType.View, 'V'))
    na = v.add(ref=a.uuid, x=200, y=0, w=120, h=55)
    nb = v.add(ref=b.uuid, x=200, y=300, w=120, h=55)
    pos = na.get_obj_pos(nb)
    assert 'B' in pos.orientation


def test_get_obj_pos_above():
    """B is directly above A → orientation 'T'."""
    m = Model('obj-pos-above')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    v = cast(View, m.add(ArchiType.View, 'V'))
    na = v.add(ref=a.uuid, x=200, y=300, w=120, h=55)
    nb = v.add(ref=b.uuid, x=200, y=0, w=120, h=55)
    pos = na.get_obj_pos(nb)
    assert 'T' in pos.orientation


def test_get_obj_pos_gap_x():
    """Nodes with horizontal gap → pos.gap_x is set."""
    m = Model('obj-pos-gapx')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    v = cast(View, m.add(ArchiType.View, 'V'))
    na = v.add(ref=a.uuid, x=0, y=0, w=100, h=50)
    nb = v.add(ref=b.uuid, x=250, y=0, w=100, h=50)
    pos = na.get_obj_pos(nb)
    assert pos.gap_x > 0


def test_get_obj_pos_gap_y():
    """Nodes with vertical gap → pos.gap_y is set."""
    m = Model('obj-pos-gapy')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    v = cast(View, m.add(ArchiType.View, 'V'))
    na = v.add(ref=a.uuid, x=0, y=0, w=100, h=50)
    nb = v.add(ref=b.uuid, x=0, y=200, w=100, h=50)
    pos = na.get_obj_pos(nb)
    assert pos.gap_y > 0


# ---------------------------------------------------------------------------
# Node.move — lines 674-682
# ---------------------------------------------------------------------------

def test_node_move_between_parents():
    """Move a child node from one parent to another (lines 674-682)."""
    m = Model('move-test')
    a = m.add(ArchiType.ApplicationComponent, 'ParentA')
    b = m.add(ArchiType.ApplicationComponent, 'ParentB')
    c = m.add(ArchiType.ApplicationComponent, 'Child')
    v = cast(View, m.add(ArchiType.View, 'V'))
    p1 = v.add(ref=a.uuid, x=0, y=0, w=300, h=200)
    p2 = v.add(ref=b.uuid, x=400, y=0, w=300, h=200)
    child_n = p1.add(ref=c.uuid, x=10, y=10)
    child_n.move(p2)
    assert child_n.uuid in p2.nodes_dict
    assert child_n.uuid not in p1.nodes_dict


def test_node_move_invalid_target_logs(caplog):
    """Moving to an invalid target logs an error and returns early."""
    import logging
    m = Model('move-invalid')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationComponent, 'B')
    v = cast(View, m.add(ArchiType.View, 'V'))
    p1 = v.add(ref=a.uuid, x=0, y=0, w=300, h=200)
    child_n = p1.add(ref=b.uuid, x=10, y=10)
    with caplog.at_level(logging.ERROR):
        child_n.move("not_a_valid_parent")
    # Node should remain in original parent
    assert child_n.uuid in p1.nodes_dict


# ---------------------------------------------------------------------------
# Connection.__init__ error paths — lines 701, 715, 725, 735
# ---------------------------------------------------------------------------

def test_connection_invalid_parent_raises():
    """Connection requires a View parent; string raises ArchimateConceptTypeError."""
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    with pytest.raises(ArchimateConceptTypeError):
        Connection(ref='any', source='s', target='t', parent="not_a_view")


def test_connection_invalid_ref_raises():
    """ref that is not str and has no .uuid raises ArchimateConceptTypeError."""
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    m = Model('conn-bad-ref')
    v = cast(View, m.add(ArchiType.View, 'V'))
    with pytest.raises(ArchimateConceptTypeError):
        Connection(ref=None, source='s', target='t', parent=v)


def test_connection_invalid_source_raises():
    """source that is not a Node or str raises ArchimateConceptTypeError."""
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    m = Model('conn-bad-src')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b)
    v = cast(View, m.add(ArchiType.View, 'V'))
    with pytest.raises(ArchimateConceptTypeError):
        Connection(ref=rel.uuid, source=None, target='t', parent=v)


def test_connection_invalid_target_raises():
    """target that is not a Node or str raises ArchimateConceptTypeError."""
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    m = Model('conn-bad-tgt')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b)
    v = cast(View, m.add(ArchiType.View, 'V'))
    na = v.add(ref=a.uuid, x=0, y=0)
    with pytest.raises(ArchimateConceptTypeError):
        Connection(ref=rel.uuid, source=na, target=None, parent=v)


# ---------------------------------------------------------------------------
# View.__init__ invalid parent (line 908)
# ---------------------------------------------------------------------------

def test_view_invalid_parent_raises():
    """View requires a parent with views_dict; string raises ArchimateConceptTypeError."""
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    with pytest.raises(ArchimateConceptTypeError):
        View(name='V', parent="not_a_model")


# ---------------------------------------------------------------------------
# l_shape / s_shape — adds bendpoints with vertically separated nodes
# ---------------------------------------------------------------------------

@pytest.fixture()
def vertical_view():
    """A view with source/target nodes far apart vertically (enables l/s shape)."""
    m = Model('vertical-test')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b)
    v = cast(View, m.add(ArchiType.View, 'V'))
    na = v.add(ref=a.uuid, x=0, y=0, w=120, h=55)
    nb = v.add(ref=b.uuid, x=200, y=500, w=120, h=55)
    conn = v.add_connection(ref=rel.uuid, source=na, target=nb)
    return m, v, a, b, rel, na, nb, conn


def test_connection_l_shape_adds_bendpoint(vertical_view):
    """l_shape(direction=0) adds a bendpoint when nodes are vertically separated."""
    _, _, _, _, _, na, nb, conn = vertical_view
    conn.l_shape(direction=0)
    assert len(conn.bendpoints) > 0


def test_connection_l_shape_direction1_adds_bendpoint(vertical_view):
    """l_shape(direction=1) adds a bendpoint when nodes are vertically separated."""
    _, _, _, _, _, na, nb, conn = vertical_view
    conn.l_shape(direction=1)
    assert len(conn.bendpoints) > 0


def test_connection_s_shape_direction0_adds_bendpoints(vertical_view):
    """s_shape(direction=0) adds 2 bendpoints when nodes don't overlap."""
    _, _, _, _, _, na, nb, conn = vertical_view
    conn.s_shape(direction=0)
    assert len(conn.bendpoints) == 2


def test_connection_s_shape_direction1_adds_bendpoints(vertical_view):
    """s_shape(direction=1) adds 2 bendpoints when nodes don't overlap."""
    _, _, _, _, _, na, nb, conn = vertical_view
    conn.s_shape(direction=1)
    assert len(conn.bendpoints) == 2


# ---------------------------------------------------------------------------
# Additional Node.__init__ and Node.delete paths
# ---------------------------------------------------------------------------

def test_node_init_label_ref_not_in_model_raises():
    """Covers line 179: Label node with ref not in labels_dict raises."""
    m = Model('label-bad-ref')
    v = cast(View, m.add(ArchiType.View, 'V'))
    with pytest.raises(ValueError):
        v.add(ref='nonexistent-label-uuid', node_type='Label', x=0, y=0)


def test_node_delete_recurse_false_moves_children():
    """Node.delete(recurse=False) moves children to parent (line 219: n.move)."""
    m = Model('delete-no-recurse')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationComponent, 'Child')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=300, h=200)
    child_n = parent_n.add(ref=b.uuid, x=10, y=10)
    parent_n.delete(recurse=False)
    # Child should have been re-parented to view, not deleted
    assert child_n.uuid in v.nodes_dict


def test_node_delete_from_model_with_related_nodes():
    """delete_from_model=True with another node referencing the same elem (line 227)."""
    m = Model('del-related')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    m.add_relationship(ArchiType.Serving, source=a, target=b)
    v1 = cast(View, m.add(ArchiType.View, 'V1'))
    v2 = cast(View, m.add(ArchiType.View, 'V2'))
    n1 = v1.add(ref=a.uuid, x=0, y=0)
    n2 = v2.add(ref=a.uuid, x=100, y=100)  # same element in another view
    # delete n1 with delete_from_model=True; n2 (related_node) is also deleted
    n1.delete(delete_from_model=True)
    assert a.uuid not in m.elems_dict
    assert n2.uuid not in m.nodes_dict


# ---------------------------------------------------------------------------
# Node.get_or_create_node — Element obj, no child, create_node=False → None
# ---------------------------------------------------------------------------

def test_node_get_or_create_node_no_child_no_create():
    """Element passed directly, no existing child, create_node=False → None (line 436)."""
    m = Model('gocn-no-create')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationComponent, 'Child')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=300, h=200)
    # b has no node inside parent_n, create_node=False
    result = parent_n.get_or_create_node(elem=b, create_node=False)
    assert result is None


# ---------------------------------------------------------------------------
# Node.resize — fix justify='right' to cover lines 488-490, 492-493
# ---------------------------------------------------------------------------

def test_node_resize_justify_right_odd_children():
    """justify='right' with 3 nodes and max_in_row=2 → covers lines 488-490."""
    m = Model('resize-right-odd')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationService, 'C1')
    c = m.add(ArchiType.ApplicationComponent, 'C2')
    d = m.add(ArchiType.ApplicationComponent, 'C3')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=500, h=300)
    parent_n.add(ref=b.uuid, x=10, y=10)
    parent_n.add(ref=c.uuid, x=150, y=10)
    parent_n.add(ref=d.uuid, x=290, y=10)
    parent_n.resize(max_in_row=2, justify='right')
    assert parent_n.w > 0


def test_node_resize_justify_right_max_in_row_1():
    """justify='right' with max_in_row=1 — covers lines 491-493."""
    m = Model('resize-right-1')
    a = m.add(ArchiType.ApplicationComponent, 'Parent')
    b = m.add(ArchiType.ApplicationService, 'C1')
    c = m.add(ArchiType.ApplicationComponent, 'C2')
    v = cast(View, m.add(ArchiType.View, 'V'))
    parent_n = v.add(ref=a.uuid, x=0, y=0, w=400, h=300)
    parent_n.add(ref=b.uuid, x=10, y=10)
    parent_n.add(ref=c.uuid, x=150, y=100)
    parent_n.resize(max_in_row=1, justify='right')
    assert parent_n.w > 0


# ---------------------------------------------------------------------------
# Node.move — wrong view (lines 678-679)
# ---------------------------------------------------------------------------

def test_node_move_wrong_view_logs(caplog):
    """Moving to a node in a different view logs an error (lines 678-679)."""
    import logging
    m = Model('move-wrong-view')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationComponent, 'B')
    c = m.add(ArchiType.ApplicationComponent, 'C')
    v1 = cast(View, m.add(ArchiType.View, 'V1'))
    v2 = cast(View, m.add(ArchiType.View, 'V2'))
    p1 = v1.add(ref=a.uuid, x=0, y=0, w=300, h=200)
    p2 = v2.add(ref=b.uuid, x=0, y=0, w=300, h=200)
    child_n = p1.add(ref=c.uuid, x=10, y=10)
    with caplog.at_level(logging.ERROR):
        child_n.move(p2)  # p2 is in a different view
    # Child should remain in original parent
    assert child_n.uuid in p1.nodes_dict


# ---------------------------------------------------------------------------
# Connection.__init__ — valid ref/source/target not found in model (717, 727, 737)
# ---------------------------------------------------------------------------

def test_connection_valid_ref_not_in_rels_dict_raises(simple_view):
    """Covers line 717: ref is a valid string but not in rels_dict."""
    m, v, *_ = simple_view
    a = m.add(ArchiType.ApplicationComponent, 'X1')
    b = m.add(ArchiType.ApplicationService, 'X2')
    na = v.add(ref=a.uuid, x=0, y=600)
    nb = v.add(ref=b.uuid, x=200, y=600)
    with pytest.raises(ValueError):
        Connection(ref='nonexistent-rel-uuid', source=na, target=nb, parent=v)


def test_connection_valid_source_not_in_nodes_dict_raises(simple_view):
    """Covers line 727: source is a valid string but not in nodes_dict."""
    m, v, a, b, rel, na, nb, conn = simple_view
    with pytest.raises(ValueError):
        Connection(ref=rel.uuid, source='nonexistent-node-uuid', target=nb, parent=v)


def test_connection_valid_target_not_in_nodes_dict_raises(simple_view):
    """Covers line 737: target is a valid string but not in nodes_dict."""
    m, v, a, b, rel, na, nb, conn = simple_view
    with pytest.raises(ValueError):
        Connection(ref=rel.uuid, source=na, target='nonexistent-node-uuid', parent=v)


# ---------------------------------------------------------------------------
# View.get_or_create_node — string elem paths (lines 992, 1004)
# ---------------------------------------------------------------------------

def test_view_get_or_create_node_string_found():
    """String elem that exists in model → covers line 992 (_e = _e[0])."""
    m = Model('gocn-str-found')
    a = m.add(ArchiType.ApplicationComponent, 'CompA')
    v = cast(View, m.add(ArchiType.View, 'V'))
    n = v.add(ref=a.uuid, x=0, y=0)
    result = v.get_or_create_node(elem='CompA', elem_type=ArchiType.ApplicationComponent)
    assert result is n


def test_view_get_or_create_node_string_create_node():
    """String elem found, no existing node, create_node=True → covers line 1003."""
    m = Model('gocn-str-create')
    a = m.add(ArchiType.ApplicationComponent, 'CompB')
    v = cast(View, m.add(ArchiType.View, 'V'))
    # No node added yet for CompB
    result = v.get_or_create_node(
        elem='CompB', elem_type=ArchiType.ApplicationComponent, create_node=True
    )
    assert result is not None


def test_view_get_or_create_node_no_node_no_create():
    """String elem found, no existing node, create_node=False → covers line 1004 (return None)."""
    m = Model('gocn-no-create-view')
    a = m.add(ArchiType.ApplicationComponent, 'CompC')
    v = cast(View, m.add(ArchiType.View, 'V'))
    # Element exists but no node in this view; create_node defaults to False
    result = v.get_or_create_node(elem='CompC', elem_type=ArchiType.ApplicationComponent)
    assert result is None


# ---------------------------------------------------------------------------
# View.get_or_create_connection — lines 1023, 1035, 1043, 1050
# ---------------------------------------------------------------------------

def test_view_get_or_create_connection_with_name_creates_rel(simple_view):
    """Named lookup finds no match, creates new rel → covers lines 1023, 1035."""
    m, v, a, b, rel, na, nb, conn = simple_view
    new_svc = m.add(ArchiType.ApplicationService, 'NewS')
    nn = v.add(ref=new_svc.uuid, x=400, y=10)
    result = v.get_or_create_connection(
        rel=None, source=na, target=nn,
        rel_type=ArchiType.Serving, name='new-conn',
        create_conn=True
    )
    assert result is not None


def test_view_get_or_create_connection_duck_type_no_type_returns_none(simple_view):
    """rel has no .type attribute → covers line 1043 (return None)."""
    _, v, _, _, _, na, nb, _ = simple_view

    class NoTypeDuck:
        pass

    result = v.get_or_create_connection(rel=NoTypeDuck(), source=na, target=nb)
    assert result is None


def test_view_get_or_create_connection_no_conn_create_false(simple_view):
    """Existing rel but no connection, create_conn=False → covers line 1050."""
    m, v, a, b, rel, na, nb, conn = simple_view
    conn.delete()
    result = v.get_or_create_connection(rel=rel, source=na, target=nb)
    assert result is None
