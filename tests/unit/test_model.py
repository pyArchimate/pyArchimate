from typing import cast

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model, default_color
from src.pyArchimate.view import View
from tests._helpers import model_with_views


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_model():
    """A model with two elements and one relationship."""
    m = Model('test')
    src = m.add(ArchiType.ApplicationComponent, 'App')
    dst = m.add(ArchiType.ApplicationService, 'Svc')
    rel = m.add_relationship(rel_type=ArchiType.Serving, source=src, target=dst, name='serves')
    return m, src, dst, rel


# ---------------------------------------------------------------------------
# Existing test
# ---------------------------------------------------------------------------

def test_model_roundtrip_preserves_properties(tmp_path):
    model = Model('unit test')
    model.prop('custom', 'value')
    model.add(ArchiType.ApplicationComponent, 'UnitElement')
    destination = tmp_path / 'unit-model.archimate'
    model.write(str(destination))

    reloaded = Model('reload')
    reloaded.read(str(destination))
    assert reloaded.prop('custom') == 'value'
    assert any(elem.name == 'UnitElement' for elem in reloaded.elements)


# ---------------------------------------------------------------------------
# default_color
# ---------------------------------------------------------------------------

def test_default_color_archi_theme():
    assert default_color('ApplicationComponent', 'archi') == '#B5FFFF'


def test_default_color_aris_theme():
    assert default_color('ApplicationComponent', 'aris') == '#00A0FF'


def test_default_color_none_theme():
    result = default_color('BusinessActor', None)
    assert result.startswith('#')


def test_default_color_custom_theme_dict():
    custom = {'business': '#AABBCC'}
    assert default_color('BusinessActor', custom) == '#AABBCC'


def test_default_color_custom_theme_missing_key():
    # KeyError fallback → returns archi default
    result = default_color('BusinessActor', {})
    assert result.startswith('#')


def test_default_color_unknown_type():
    assert default_color('NotAType') == '#FFFFFF'


# ---------------------------------------------------------------------------
# Model.type property
# ---------------------------------------------------------------------------

def test_model_type_is_model():
    m = Model('x')
    assert m.type == 'Model'


# ---------------------------------------------------------------------------
# Model.prop / remove_prop
# ---------------------------------------------------------------------------

def test_model_remove_prop(simple_model):
    m, *_ = simple_model
    m.prop('tmp', '1')
    m.remove_prop('tmp')
    assert m.prop('tmp') is None


def test_model_remove_prop_missing_key_is_noop():
    m = Model('x')
    m.remove_prop('no_such_key')  # must not raise


# ---------------------------------------------------------------------------
# Model.add_profile / get_profile
# ---------------------------------------------------------------------------

def test_model_get_profile_found(simple_model):
    m, *_ = simple_model
    p = m.add_profile(name='MyProfile', concept='ApplicationComponent')
    assert m.get_profile('MyProfile') is p


def test_model_get_profile_not_found():
    m = Model('x')
    assert m.get_profile('ghost') is None


# ---------------------------------------------------------------------------
# Model.nodes / conns
# ---------------------------------------------------------------------------

def test_model_nodes_returns_list(simple_model):
    m, *_ = simple_model
    assert isinstance(m.nodes, list)


def test_model_conns_returns_list(simple_model):
    m, *_ = simple_model
    assert isinstance(m.conns, list)


# ---------------------------------------------------------------------------
# Model.filter_elements / find_elements
# ---------------------------------------------------------------------------

def test_filter_elements(simple_model):
    m, src, *_ = simple_model
    result = m.filter_elements(lambda e: e.type == ArchiType.ApplicationComponent)
    assert src in result


def test_find_elements_by_name(simple_model):
    m, src, *_ = simple_model
    assert m.find_elements(name='App') == [src]


def test_find_elements_by_type(simple_model):
    m, src, *_ = simple_model
    assert m.find_elements(elem_type=ArchiType.ApplicationComponent) == [src]


def test_find_elements_by_name_and_type(simple_model):
    m, src, *_ = simple_model
    assert m.find_elements(name='App', elem_type=ArchiType.ApplicationComponent) == [src]


def test_find_elements_no_criteria(simple_model):
    m, src, dst, *_ = simple_model
    result = m.find_elements()
    assert src in result and dst in result


# ---------------------------------------------------------------------------
# Model.find_relationships / filter_relationships
# ---------------------------------------------------------------------------

def test_find_relationships_with_type_both(simple_model):
    m, src, dst, rel = simple_model
    result = m.find_relationships(ArchiType.Serving, src, direction='both')
    assert rel in result


def test_find_relationships_out_only(simple_model):
    m, src, dst, rel = simple_model
    assert rel in m.find_relationships(ArchiType.Serving, src, direction='out')


def test_find_relationships_in_only(simple_model):
    m, src, dst, rel = simple_model
    assert rel in m.find_relationships(ArchiType.Serving, dst, direction='in')


def test_find_relationships_no_type(simple_model):
    m, src, dst, rel = simple_model
    result = m.find_relationships(None, src, direction='both')
    assert rel in result


def test_find_relationships_none_elem(simple_model):
    m, *_ = simple_model
    assert m.find_relationships(ArchiType.Serving, None) is None


def test_filter_relationships(simple_model):
    m, src, dst, rel = simple_model
    result = m.filter_relationships(lambda r: r.name == 'serves')
    assert rel in result


# ---------------------------------------------------------------------------
# Model.filter_views / find_views
# ---------------------------------------------------------------------------

def test_filter_views(simple_model):
    m, *_ = simple_model
    v = m.add(ArchiType.View, 'MyView')
    result = m.filter_views(lambda x: x.name == 'MyView')
    assert v in result


def test_find_views(simple_model):
    m, *_ = simple_model
    v = m.add(ArchiType.View, 'SearchView')
    assert m.find_views('SearchView') == [v]


# ---------------------------------------------------------------------------
# Model.merge
# ---------------------------------------------------------------------------

def test_model_merge_reads_data(tmp_path):
    m1 = Model('base')
    m1.add(ArchiType.ApplicationComponent, 'CompA')
    f = tmp_path / 'base.archimate'
    m1.write(str(f))

    m2 = Model('target')
    m2.add(ArchiType.ApplicationComponent, 'CompB')
    m2.merge(str(f))
    names = [e.name for e in m2.elements]
    assert 'CompA' in names
    assert 'CompB' in names


# ---------------------------------------------------------------------------
# Model.get_or_create_element
# ---------------------------------------------------------------------------

def test_get_or_create_element_empty_name(simple_model):
    m, *_ = simple_model
    assert m.get_or_create_element(ArchiType.ApplicationComponent, '') is None


def test_get_or_create_element_none_name(simple_model):
    m, *_ = simple_model
    assert m.get_or_create_element(ArchiType.ApplicationComponent, None) is None


def test_get_or_create_element_found(simple_model):
    m, src, *_ = simple_model
    result = m.get_or_create_element(ArchiType.ApplicationComponent, 'App')
    assert result is src


def test_get_or_create_element_create_true(simple_model):
    m, *_ = simple_model
    result = m.get_or_create_element(ArchiType.ApplicationComponent, 'Brand New', create_elem=True)
    assert result is not None
    assert result.name == 'Brand New'


def test_get_or_create_element_not_found_no_create(simple_model):
    m, *_ = simple_model
    assert m.get_or_create_element(ArchiType.ApplicationComponent, 'Ghost') is None


# ---------------------------------------------------------------------------
# Model.get_or_create_relationship
# ---------------------------------------------------------------------------

def test_get_or_create_relationship_none_source(simple_model):
    m, _, dst, *_ = simple_model
    assert m.get_or_create_relationship(ArchiType.Serving, None, None, dst) is None


def test_get_or_create_relationship_found_unnamed(simple_model):
    m, src, dst, rel = simple_model
    result = m.get_or_create_relationship(ArchiType.Serving, None, src, dst)
    assert result is rel


def test_get_or_create_relationship_found_named(simple_model):
    m, src, dst, rel = simple_model
    result = m.get_or_create_relationship(ArchiType.Serving, 'serves', src, dst)
    assert result is rel


def test_get_or_create_relationship_create(simple_model):
    m, src, dst, _ = simple_model
    result = m.get_or_create_relationship(
        ArchiType.Association, 'new-rel', src, dst, create_rel=True
    )
    assert result is not None
    assert result.name == 'new-rel'


def test_get_or_create_relationship_not_found_no_create(simple_model):
    m, src, dst, _ = simple_model
    result = m.get_or_create_relationship(ArchiType.Association, 'ghost', src, dst)
    assert result is None


# ---------------------------------------------------------------------------
# Model.get_or_create_view
# ---------------------------------------------------------------------------

def test_get_or_create_view_found(simple_model):
    m, *_ = simple_model
    v = m.add(ArchiType.View, 'MyView')
    assert m.get_or_create_view('MyView') is v


def test_get_or_create_view_not_found_create(simple_model):
    m, *_ = simple_model
    v = m.get_or_create_view('NewView', create_view=True)
    assert v is not None and v.name == 'NewView'


def test_get_or_create_view_not_found_no_create(simple_model):
    m, *_ = simple_model
    assert m.get_or_create_view('Ghost') is None


def test_get_or_create_view_object_passthrough(simple_model):
    m, *_ = simple_model
    v = m.add(ArchiType.View, 'ObjView')
    assert m.get_or_create_view(v) is v


# ---------------------------------------------------------------------------
# Model.check_invalid_conn / check_invalid_nodes
# ---------------------------------------------------------------------------

def test_check_invalid_conn_empty_model():
    assert Model('x').check_invalid_conn() == []


def test_check_invalid_nodes_empty_model():
    assert Model('x').check_invalid_nodes() == []


def test_check_invalid_conn_with_views():
    m = model_with_views()
    result = m.check_invalid_conn()
    assert isinstance(result, list)


def test_check_invalid_nodes_with_views():
    m = model_with_views()
    result = m.check_invalid_nodes()
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Model.default_theme
# ---------------------------------------------------------------------------

def test_model_default_theme_sets_theme():
    m = model_with_views()
    m.default_theme('archi')
    assert m.theme == 'archi'


def test_model_default_theme_colors_nodes():
    m = model_with_views()
    m.default_theme('aris')
    # All element nodes should now have a fill color set
    for n in m.nodes:
        if n.cat == 'Element':
            assert n.fill_color is not None


# ---------------------------------------------------------------------------
# Model.embed_props / expand_props
# ---------------------------------------------------------------------------

def test_model_embed_props_element():
    m = Model('ep-test')
    a = m.add(ArchiType.ApplicationComponent, 'App')
    a.prop('owner', 'team')
    m.embed_props()
    assert a.desc is not None and 'properties' in a.desc


def test_model_embed_props_view():
    m = Model('ep-view')
    v = cast(View, m.add(ArchiType.View, 'V'))
    v.prop('color', 'blue')
    m.embed_props()
    assert v.desc is not None and 'properties' in v.desc


def test_model_embed_props_model_level():
    m = Model('ep-model')
    m.prop('env', 'prod')
    m.embed_props()
    assert m.desc is not None and 'properties' in m.desc


def test_model_embed_props_relationship():
    m = Model('ep-rel')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b, name='serves')
    m.embed_props()
    assert rel.prop('Identifier') == 'serves'


def test_model_embed_props_remove_props():
    m = Model('ep-rm')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    a.prop('x', '1')
    m.embed_props(remove_props=True)
    assert a.prop('x') is None


def test_model_expand_props_restores_element():
    m = Model('ex-elem')
    a = m.add(ArchiType.ApplicationComponent, 'App')
    a.prop('k', 'v')
    m.embed_props()
    m.expand_props()
    assert a.prop('k') == 'v'


def test_model_expand_props_view():
    m = Model('ex-view')
    v = cast(View, m.add(ArchiType.View, 'V'))
    v.prop('key', 'val')
    m.embed_props()
    m.expand_props()
    assert v.prop('key') == 'val'


def test_model_expand_props_relationship():
    m = Model('ex-rel')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b, name='r1')
    m.embed_props()
    m.expand_props()
    assert rel.name is not None


# ---------------------------------------------------------------------------
# Model.add_relationship with Node sources/targets
# ---------------------------------------------------------------------------

def test_get_or_create_relationship_with_node_source_and_target():
    m = Model('node-rel')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    v = cast(View, m.add(ArchiType.View, 'V'))
    na = v.add(ref=a.uuid, x=10, y=10)
    nb = v.add(ref=b.uuid, x=200, y=10)
    # Passing Nodes directly — get_or_create_relationship converts them to concepts
    rel = m.get_or_create_relationship(
        ArchiType.Serving, None, na, nb, create_rel=True
    )
    assert rel is not None


# ---------------------------------------------------------------------------
# Model._prepare_reader — unknown XML format (lines 355, 363-364)
# ---------------------------------------------------------------------------

def test_model_read_unknown_xml_format_returns_none(tmp_path):
    """Reading an XML file with an unrecognised root tag returns silently (lines 355, 363-364)."""
    xml_file = tmp_path / 'unknown.xml'
    xml_file.write_text('<UnknownRoot><element/></UnknownRoot>', encoding='utf-8')
    m = Model('unknown-xml')
    # read() calls _prepare_reader which returns None for unknown root tag
    m.read(str(xml_file))  # should not raise; just logs and returns


def test_model_merge_unknown_xml_format_returns_none(tmp_path):
    """Merging an XML file with an unrecognised root tag returns silently (line 399)."""
    xml_file = tmp_path / 'unknown_merge.xml'
    xml_file.write_text('<Unrecognised><item/></Unrecognised>', encoding='utf-8')
    m = Model('merge-unknown')
    m.merge(str(xml_file))  # should not raise
