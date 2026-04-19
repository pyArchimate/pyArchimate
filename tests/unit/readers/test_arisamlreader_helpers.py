"""Unit tests for _arisamlreader_helpers to ensure ≥80% coverage (T023)."""
import pytest
from lxml import etree

from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.readers._arisamlreader_helpers import (
    clean_nested_conns,
    id_of,
    parse_connections,
    parse_containers,
    parse_elements,
    parse_labels,
    parse_labels_in_view,
    parse_nodes,
    parse_relationships,
    parse_views,
)


def _make_aml_root():
    return etree.Element('AML')


def _make_group(name: str) -> etree._Element:
    g = etree.Element('Group')
    attr = etree.SubElement(g, 'AttrDef')
    pt = etree.SubElement(attr, 'PlainText')
    pt.set('TextValue', name)
    return g


def _make_objdef(obj_id: str, sym: str, name: str = 'E') -> etree._Element:
    o = etree.Element('ObjDef')
    o.set('ObjDef.ID', obj_id)
    o.set('SymbolNum', sym)
    guid = etree.SubElement(o, 'GUID')
    guid.text = 'abc-' + obj_id
    a = etree.SubElement(o, 'AttrDef')
    a.set('AttrDef.Type', 'AT_NAME')
    pt = etree.SubElement(a, 'PlainText')
    pt.set('TextValue', name)
    return o


def _make_model(name: str = 'test') -> Model:
    return Model(name)


# ── id_of ──────────────────────────────────────────────────────────────────


def test_id_of_with_dot():
    assert id_of('group.123') == 'id-123'


def test_id_of_without_dot():
    assert id_of('simple') == 'id-simple'


# ── parse_elements ─────────────────────────────────────────────────────────


def test_parse_elements_skips_obj_without_symbolnum():
    root = _make_aml_root()
    g = _make_group('folder')
    # ObjDef without SymbolNum → should be skipped (line 71)
    o = etree.SubElement(g, 'ObjDef')
    o.set('ObjDef.ID', 'obj.1')
    root.append(g)
    model = _make_model()
    parse_elements(None, root, model)
    assert len(model.elems_dict) == 0


def test_parse_elements_adds_element_with_props():
    root = _make_aml_root()
    g = _make_group('Application')
    obj = _make_objdef('obj.1', 'ST_ARCHIMATE_APPLICATION_COMPONENT', 'MyApp')
    # Add extra property (covers line 91: else props[key] = val)
    extra_attr = etree.SubElement(obj, 'AttrDef')
    extra_attr.set('AttrDef.Type', 'AT_CUSTOM')
    extra_pt = etree.SubElement(extra_attr, 'PlainText')
    extra_pt.set('TextValue', 'custom_value')
    # Add AT_DESC (covers line 89: elif key == 'AT_DESC')
    desc_attr = etree.SubElement(obj, 'AttrDef')
    desc_attr.set('AttrDef.Type', 'AT_DESC')
    desc_pt = etree.SubElement(desc_attr, 'PlainText')
    desc_pt.set('TextValue', 'My description')
    g.append(obj)
    root.append(g)
    model = _make_model()
    parse_elements(None, root, model)
    assert len(model.elems_dict) == 1


def test_parse_elements_with_explicit_group():
    # Wrap g inside parent so group.findall('Group') finds it
    parent = etree.Element('Container')
    g = _make_group('SubFolder')
    obj = _make_objdef('obj.2', 'ST_ARCHIMATE_APPLICATION_COMPONENT', 'SubApp')
    g.append(obj)
    parent.append(g)
    root = _make_aml_root()
    model = _make_model()
    parse_elements(parent, root, model)
    assert len(model.elems_dict) == 1


# ── parse_relationships ────────────────────────────────────────────────────


def test_parse_relationships_skips_unknown_target():
    root = _make_aml_root()
    g = _make_group('Rels')
    obj = _make_objdef('obj.1', 'ST_ARCHIMATE_APPLICATION_COMPONENT')
    rel = etree.SubElement(obj, 'CxnDef')
    rel.set('CxnDef.Type', 'CT_ARCHIMATE_ASSOCIATION')
    rel.set('CxnDef.ID', 'rel.1')
    rel.set('ToObjDef.IdRef', 'obj.999')  # unknown target
    g.append(obj)
    root.append(g)
    model = _make_model()
    parse_relationships(None, root, model)
    assert len(model.rels_dict) == 0


def test_parse_relationships_adds_relationship():
    root = _make_aml_root()
    g = _make_group('Group')
    src_obj = _make_objdef('src.1', 'ST_ARCHIMATE_APPLICATION_COMPONENT', 'Src')
    tgt_obj = _make_objdef('tgt.1', 'ST_ARCHIMATE_APPLICATION_COMPONENT', 'Tgt')
    rel = etree.SubElement(src_obj, 'CxnDef')
    rel.set('CxnDef.Type', 'CT_ARCHIMATE_ASSOCIATION')
    rel.set('CxnDef.ID', 'rel.1')
    rel.set('ToObjDef.IdRef', 'tgt.1')
    # Add rel property to cover lines 128-133
    rel_attr = etree.SubElement(rel, 'AttrDef')
    rel_attr.set('AttrDef.Type', 'AT_PROP')
    rel_pt = etree.SubElement(rel_attr, 'PlainText')
    rel_pt.set('TextValue', 'value')
    g.append(src_obj)
    g.append(tgt_obj)
    root.append(g)
    model = _make_model()
    parse_elements(None, root, model)
    parse_relationships(None, root, model)
    assert len(model.rels_dict) == 1


# ── parse_nodes ────────────────────────────────────────────────────────────


def _setup_model_with_element() -> tuple[Model, str]:
    model = _make_model()
    elem = model.add(concept_type='ApplicationComponent', name='App', uuid='id-elem1')
    return model, elem.uuid


def test_parse_nodes_returns_early_on_none_grp():
    model, _ = _setup_model_with_element()
    view = model.add(concept_type='View', name='V')
    parse_nodes(None, view, model, 1.0, 1.0)  # no-op


def test_parse_nodes_returns_early_on_none_view():
    grp = etree.Element('Group')
    model, _ = _setup_model_with_element()
    parse_nodes(grp, None, model, 1.0, 1.0)  # no-op


def test_parse_nodes_raises_on_wrong_view_type():
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    grp = etree.Element('Group')
    model = _make_model()
    with pytest.raises(ArchimateConceptTypeError):
        parse_nodes(grp, "not-a-view", model, 1.0, 1.0)  # type: ignore[arg-type]


def test_parse_nodes_adds_node():
    root = _make_aml_root()
    g = _make_group('Group')
    obj = _make_objdef('elem.1', 'ST_ARCHIMATE_APPLICATION_COMPONENT', 'App')
    g.append(obj)
    root.append(g)
    model = _make_model()
    parse_elements(None, root, model)

    occ = etree.Element('ObjOcc')
    occ.set('SymbolNum', 'ST_ARCHIMATE_APPLICATION_COMPONENT')
    occ.set('ObjOcc.ID', 'occ.1')
    occ.set('ObjDef.IdRef', 'elem.1')
    pos = etree.SubElement(occ, 'Position')
    pos.set('Pos.X', '100')
    pos.set('Pos.Y', '200')
    size = etree.SubElement(occ, 'Size')
    size.set('Size.dX', '120')
    size.set('Size.dY', '55')
    grp = etree.Element('View')
    grp.append(occ)

    view = model.add(concept_type='View', name='TestView')
    parse_nodes(grp, view, model, 1.0, 1.0)
    assert len(model.nodes_dict) == 1


def test_parse_nodes_grouping_node():
    root = _make_aml_root()
    g = _make_group('G')
    obj = _make_objdef('grp.1', 'ST_ARCHIMATE_GROUPING', 'Grp')
    g.append(obj)
    root.append(g)
    model = _make_model()
    parse_elements(None, root, model)

    occ = etree.Element('ObjOcc')
    occ.set('SymbolNum', 'ST_ARCHIMATE_GROUPING')
    occ.set('ObjOcc.ID', 'occ.g')
    occ.set('ObjDef.IdRef', 'grp.1')
    pos = etree.SubElement(occ, 'Position')
    pos.set('Pos.X', '0')
    pos.set('Pos.Y', '0')
    size = etree.SubElement(occ, 'Size')
    size.set('Size.dX', '300')
    size.set('Size.dY', '200')
    grp = etree.Element('View')
    grp.append(occ)
    view = model.add(concept_type='View', name='TV')
    parse_nodes(grp, view, model, 1.0, 1.0)
    node = list(model.nodes_dict.values())[0]
    assert node.fill_color == "#FFFFFF"


# ── parse_containers ───────────────────────────────────────────────────────


def test_parse_containers_returns_early_on_none():
    model = _make_model()
    view = model.add(concept_type='View', name='V')
    parse_containers(None, view, 1.0, 1.0)  # no-op
    parse_containers(etree.Element('G'), None, 1.0, 1.0)  # no-op


def test_parse_containers_adds_container():
    model = _make_model()
    view = model.add(concept_type='View', name='V')
    grp = etree.Element('Group')
    gfx = etree.SubElement(grp, 'GfxObj')
    rect = etree.SubElement(gfx, 'RoundedRectangle')
    pos = etree.SubElement(rect, 'Position')
    pos.set('Pos.X', '10')
    pos.set('Pos.Y', '20')
    sz = etree.SubElement(rect, 'Size')
    sz.set('Size.dX', '100')
    sz.set('Size.dY', '50')
    brush = etree.SubElement(rect, 'Brush')
    brush.set('Color', '16711680')
    parse_containers(grp, view, 1.0, 1.0)
    assert len(model.nodes_dict) == 1


def test_parse_containers_without_brush():
    model = _make_model()
    view = model.add(concept_type='View', name='V')
    grp = etree.Element('Group')
    gfx = etree.SubElement(grp, 'GfxObj')
    rect = etree.SubElement(gfx, 'RoundedRectangle')
    pos = etree.SubElement(rect, 'Position')
    pos.set('Pos.X', '0')
    pos.set('Pos.Y', '0')
    sz = etree.SubElement(rect, 'Size')
    sz.set('Size.dX', '50')
    sz.set('Size.dY', '25')
    parse_containers(grp, view, 1.0, 1.0)
    assert len(model.nodes_dict) == 1


# ── parse_labels ───────────────────────────────────────────────────────────


def test_parse_labels_adds_to_labels_dict():
    root = _make_aml_root()
    txt = etree.SubElement(root, 'FFTextDef')
    txt.set('FFTextDef.ID', 'lbl.1')
    txt.set('IsModelAttr', 'TEXT')
    attr = etree.SubElement(txt, 'AttrDef')
    attr.set('AttrDef.Type', 'AT_NAME')
    pt = etree.SubElement(attr, 'PlainText')
    pt.set('TextValue', 'My Label')
    model = _make_model()
    model.labels_dict = {}
    parse_labels(root, model)
    assert 'id-1' in model.labels_dict


# ── parse_connections ──────────────────────────────────────────────────────


def _build_two_node_model():
    root = _make_aml_root()
    g = _make_group('G')
    src = _make_objdef('src.1', 'ST_ARCHIMATE_APPLICATION_COMPONENT', 'Src')
    tgt = _make_objdef('tgt.1', 'ST_ARCHIMATE_APPLICATION_COMPONENT', 'Tgt')
    rel = etree.SubElement(src, 'CxnDef')
    rel.set('CxnDef.Type', 'CT_ARCHIMATE_ASSOCIATION')
    rel.set('CxnDef.ID', 'rel.1')
    rel.set('ToObjDef.IdRef', 'tgt.1')
    g.append(src)
    g.append(tgt)
    root.append(g)
    model = _make_model()
    parse_elements(None, root, model)
    parse_relationships(None, root, model)
    return model


def test_parse_connections_returns_early_on_none():
    model = _build_two_node_model()
    view = model.add(concept_type='View', name='V')
    parse_connections(None, view, model, 1.0, 1.0)  # no-op


def test_parse_connections_skips_unknown_rel():
    model = _build_two_node_model()
    view = model.add(concept_type='View', name='V')
    grp = etree.Element('Group')
    occ_src = etree.SubElement(grp, 'ObjOcc')
    occ_src.set('ObjOcc.ID', 'occ.src')
    conn = etree.SubElement(occ_src, 'CxnOcc')
    conn.set('CxnOcc.ID', 'cocc.1')
    conn.set('CxnDef.IdRef', 'unknown.rel')
    conn.set('ToObjOcc.IdRef', 'occ.tgt')
    parse_connections(grp, view, model, 1.0, 1.0)  # no-op on unknown rel


# ── clean_nested_conns ─────────────────────────────────────────────────────


def test_clean_nested_conns_no_error_on_empty_model():
    model = _make_model()
    clean_nested_conns(model)  # should not raise


# ── parse_labels_in_view ──────────────────────────────────────────────────


def test_parse_labels_in_view_returns_early_on_none():
    model = _make_model()
    model.labels_dict = {}
    view = model.add(concept_type='View', name='V')
    parse_labels_in_view(None, view, model, 1.0, 1.0)  # no-op
    parse_labels_in_view(etree.Element('G'), None, model, 1.0, 1.0)  # no-op


def test_parse_labels_in_view_raises_on_wrong_view_type():
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    model = _make_model()
    model.labels_dict = {}
    with pytest.raises(ArchimateConceptTypeError):
        parse_labels_in_view(etree.Element('G'), "not-view", model, 1.0, 1.0)  # type: ignore[arg-type]


def test_parse_labels_in_view_adds_label_node():
    model = _make_model()
    # id_of('lbl1') = 'id-lbl1' (no dot → uses whole string)
    model.labels_dict = {'id-lbl1': 'My Label Text'}
    view = model.add(concept_type='View', name='V')

    grp = etree.Element('Group')
    occ = etree.SubElement(grp, 'FFTextOcc')
    occ.set('FFTextDef.IdRef', 'lbl1')
    pos = etree.SubElement(occ, 'Position')
    pos.set('Pos.X', '10')
    pos.set('Pos.Y', '20')

    parse_labels_in_view(grp, view, model, 1.0, 1.0)
    assert len(model.nodes_dict) == 1


def test_parse_labels_in_view_skips_unknown_ref():
    model = _make_model()
    model.labels_dict = {}
    view = model.add(concept_type='View', name='V')

    grp = etree.Element('Group')
    occ = etree.SubElement(grp, 'FFTextOcc')
    occ.set('FFTextDef.IdRef', 'unknown.1')

    parse_labels_in_view(grp, view, model, 1.0, 1.0)
    assert len(model.nodes_dict) == 0


# ── parse_views ─────────────────────────────────────────────────────────────


def test_parse_views_empty_root():
    root = _make_aml_root()
    model = _make_model()
    parse_views(None, root, model, 1.0, 1.0)  # no views to parse, no error


def test_parse_views_adds_view():
    root = _make_aml_root()
    g = _make_group('Views')
    mdl_elem = etree.SubElement(g, 'Model')
    mdl_elem.set('Model.ID', 'view.1')
    # Add AT_NAME
    a = etree.SubElement(mdl_elem, 'AttrDef')
    a.set('AttrDef.Type', 'AT_NAME')
    pt = etree.SubElement(a, 'PlainText')
    pt.set('TextValue', 'MyView')
    # Add AT_DESC (covers line 301-302)
    ad = etree.SubElement(mdl_elem, 'AttrDef')
    ad.set('AttrDef.Type', 'AT_DESC')
    pd = etree.SubElement(ad, 'PlainText')
    pd.set('TextValue', 'View description')
    # Add extra prop (covers line 303-304)
    ap = etree.SubElement(mdl_elem, 'AttrDef')
    ap.set('AttrDef.Type', 'AT_CUSTOM')
    pp = etree.SubElement(ap, 'PlainText')
    pp.set('TextValue', 'prop_val')
    root.append(g)
    model = _make_model()
    parse_views(None, root, model, 1.0, 1.0)
    assert len(model.views) == 1
