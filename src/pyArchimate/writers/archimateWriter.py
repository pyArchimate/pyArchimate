import os
import sys
from collections import defaultdict
from typing import Callable, Optional
from typing import cast as _cast

from lxml import etree as et
from lxml.etree import _Element

try:
    from ..constants import ARCHI_CATEGORY as archi_category
    from ..constants import DEFAULT_THEME as default_theme
    from ..constants import RGBA
    from ..enums import ArchiType
    from ..helpers.logging import log
    from ..model import Model, default_color
    from ..view import Node
except ImportError:
    sys.path.insert(0, "..")
    from pyArchimate import (  # type: ignore[no-redef,attr-defined]  # noqa: E401
        RGBA,
        ArchiType,
        Model,
        Node,
        archi_category,
        default_color,
        default_theme,
        log,
    )

__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

_NS_ITEM = 'ns:item'

_GetPropId = Callable[[str], str]


def _get_prop_def_id(model: Model, k: str) -> str:
    id_list = [x for x, y in model.pdefs.items() if y == k]
    if len(id_list) == 0:
        prop_id: str = 'propid-' + str(len(model.pdefs) + 1)
        model.pdefs[prop_id] = k
        return prop_id
    return str(id_list[0])


def _write_properties(parent: _Element, props: dict[str, object], model: Model) -> None:
    pp = et.SubElement(parent, 'properties')
    for k, v in props.items():
        prop_id = _get_prop_def_id(model, k)
        p = et.SubElement(pp, 'property', propertyDefinitionRef=prop_id)
        pv = et.SubElement(p, 'value')
        pv.text = str(v)


def _write_elements(root: _Element, model: Model, xsi: et.QName) -> None:
    elems = et.SubElement(root, 'elements')
    for e in model.elements:
        cat = archi_category[e.type].split('-')[0]
        if cat == "Junction":
            cat = "Other"
        elif cat == "Physical":
            cat = 'Technology'
        if e.folder is None:
            e.folder = '/' + cat
        elem = et.SubElement(elems, 'element', {'identifier': e.uuid, str(xsi): e.type})
        if e.name is None:
            e.name = e.type
        if e.name is not None:
            e_name = et.SubElement(elem, 'name')
            e_name.text = e.name
        if e.desc is not None and e.desc != '':
            e_desc = et.SubElement(elem, 'documentation')
            e_desc.text = e.desc
        if e.props:
            _write_properties(elem, e.props, model)


def _write_relationships(root: _Element, model: Model, xsi: et.QName) -> None:
    rels = et.SubElement(root, 'relationships')
    for e in model.relationships:
        assert e.source is not None and e.target is not None
        elem = et.SubElement(rels, 'relationship', {
            'identifier': e.uuid,
            'source': e.source.uuid,
            'target': e.target.uuid,
            str(xsi): e.type
        })
        if e.access_type is not None and e.type == ArchiType.Access:
            elem.set('accessType', e.access_type)
        if e.is_directed is not None and e.type == ArchiType.Association:
            elem.set('isDirected', "true")
        if e.influence_strength is not None and e.type == ArchiType.Influence:
            elem.set('influenceStrength', e.influence_strength)
        if e.name is not None:
            e_name = et.SubElement(elem, 'name')
            e_name.text = e.name
        if e.desc is not None:
            e_desc = et.SubElement(elem, 'documentation')
            e_desc.text = e.desc
        if e.props:
            _write_properties(elem, e.props, model)


def _write_organizations(root: _Element, model: Model, ns_find: dict[str, str]) -> None:
    orgs_dict: dict[str, list[str]] = defaultdict(list)
    for e in model.elements:
        if e.folder is not None:
            orgs_dict[e.folder].append(e.uuid)
    for r in model.relationships:
        if r.folder is not None:
            orgs_dict[r.folder].append(r.uuid)
    for v in model.views:
        if v.folder is not None:
            orgs_dict[v.folder].append(v.uuid)
    keys = sorted(orgs_dict.keys())
    orgs = et.SubElement(root, 'organizations')
    for k in keys:
        labels = k.split('/')
        item = orgs
        for label in labels[1:-1]:
            if item.find(_NS_ITEM, ns_find) is None:
                item = et.SubElement(item, 'item')
            else:
                item = _cast(_Element, item.find(_NS_ITEM, ns_find))
            lbl = et.SubElement(item, 'label')
            lbl.text = label
        if item.find(_NS_ITEM, ns_find) is None:
            item = et.SubElement(item, 'item')
        else:
            item = _cast(_Element, item.find(_NS_ITEM, ns_find))
        label_text = labels[-1:][0]
        lbl = et.SubElement(item, 'label')
        lbl.text = label_text
        for i in orgs_dict[k]:
            et.SubElement(item, 'item', identifierRef=i)


def _write_node_style(n_elem: _Element, n: Node) -> None:
    style = et.SubElement(n_elem, 'style')
    if n.line_color is not None:
        lc = et.SubElement(style, 'lineColor')
        rgb = RGBA()
        rgb.color = n.line_color
        lc.set('r', str(rgb.r))
        lc.set('g', str(rgb.g))
        lc.set('b', str(rgb.b))
        lc.set('a', '100' if n.opacity is None else str(n.lc_opacity))
    if n.fill_color is not None:
        if n.fill_color != default_color(n.type or '', default_theme):
            fc = et.SubElement(style, 'fillColor')
            rgb = RGBA()
            rgb.color = n.fill_color
            fc.set('r', str(rgb.r))
            fc.set('g', str(rgb.g))
            fc.set('b', str(rgb.b))
            fc.set('a', '100' if n.opacity is None else str(n.opacity))
    if n.font_name is not None:
        ft = et.SubElement(style, 'font', attrib={
            'name': n.font_name,
            'size': str(n.font_size)
        })
        rgb = RGBA()
        ftc = et.SubElement(ft, 'color')
        rgb.color = n.font_color
        ftc.set('r', str(rgb.r))
        ftc.set('g', str(rgb.g))
        ftc.set('b', str(rgb.b))


def _add_node(parent: _Element, n: Node, xsi: et.QName) -> None:
    if n.cat == 'Element':
        n_elem = et.SubElement(parent, 'node', attrib={
            'identifier': n.uuid,
            'elementRef': n.ref or '',
            str(xsi): n.cat,
            'x': str(n.x),
            'y': str(n.y),
            'w': str(n.w),
            'h': str(n.h)
        })
    else:
        n_elem = et.SubElement(parent, 'node', attrib={
            'identifier': n.uuid,
            str(xsi): n.cat,
            'x': str(n.x),
            'y': str(n.y),
            'w': str(n.w),
            'h': str(n.h)
        })
        lbl = et.SubElement(n_elem, 'label')
        lbl.text = n.label
    _write_node_style(n_elem, n)
    if n.cat == 'Model':
        et.SubElement(n_elem, 'viewRef', ref=n.ref or '')
        n_elem.set(str(xsi), 'Label')
    for sub_n in n.nodes:
        _add_node(n_elem, sub_n, xsi)


def _write_connections(view_elem: _Element, _v: object, xsi: et.QName) -> None:
    for c in _v.conns:  # type: ignore[attr-defined]
        assert c.source is not None and c.target is not None

        def _is_embedded(n1: Node, n2: Node) -> bool:
            return bool((n1.x < n2.x < n1.x + n1.w) and (n1.y < n2.y < n1.y + n1.h))

        if _is_embedded(c.source, c.target) or _is_embedded(c.target, c.source):
            continue
        c_elem = et.SubElement(view_elem, 'connection', attrib={
            'identifier': c.uuid,
            'relationshipRef': c.ref,
            str(xsi): 'Relationship',
            'source': c.source.uuid,
            'target': c.target.uuid
        })
        style = et.SubElement(c_elem, 'style')
        if c.line_width is not None:
            style.set('lineWidth', str(c.line_width))
        if c.line_color is not None:
            if c.line_color != default_color(c.type, default_theme):
                lc = et.SubElement(style, 'lineColor')
                rgb = RGBA()
                rgb.color = c.line_color
                lc.set('r', str(rgb.r))
                lc.set('g', str(rgb.g))
                lc.set('b', str(rgb.b))
        if c.font_name is not None:
            ft = et.SubElement(style, 'font', attrib={
                'name': c.font_name,
                'size': str(c.font_size)
            })
            rgb = RGBA()
            ftc = et.SubElement(ft, 'color')
            rgb.color = c.font_color
            ftc.set('r', str(rgb.r))
            ftc.set('g', str(rgb.g))
            ftc.set('b', str(rgb.b))
        for bp in c.get_all_bendpoints():
            et.SubElement(c_elem, 'bendpoint', x=str(bp.x), y=str(bp.y))


def _write_views(root: _Element, model: Model, xsi: et.QName, ns_find: dict[str, str]) -> None:
    if not model.views:
        return
    views = et.SubElement(root, 'views')
    diag = et.SubElement(views, 'diagrams')
    for _v in model.views:
        view_elem = et.SubElement(diag, 'view', attrib={
            'identifier': _v.uuid,
            str(xsi): 'Diagram'
        })
        if _v.name is not None:
            v_name = et.SubElement(view_elem, 'name')
            v_name.text = _v.name
        if _v.desc is not None:
            doc = et.SubElement(view_elem, 'documentation')
            doc.text = _v.desc
        if _v.props:
            _write_properties(view_elem, _v.props, model)
        for _n in _v.nodes:
            _add_node(view_elem, _n, xsi)
        _write_connections(view_elem, _v, xsi)


def archimate_writer(model: Model, file_path: Optional[str] = None) -> str:
    """
    Method to generate an Archimate XML Open Exchange File format structure as a string object

    Used by Model.write(filepath) method

    """
    xml = b"""<?xml version="1.0" encoding="utf-8"?>
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd" identifier="id-a84d2455d48c44a2847b3407e270599f">
    </model>
    """

    root = et.fromstring(xml)
    nsp_url = 'http://www.opengroup.org/xsd/archimate/3.0/'
    xsi_url = 'http://www.w3.org/2001/XMLSchema-instance'
    xsi = et.QName(xsi_url, 'type')
    ns_find: dict[str, str] = {'ns': nsp_url}

    name = et.SubElement(root, 'name')
    name.text = model.name if model.name is not None else 'Archimate Model'

    if model.desc is not None:
        doc = et.SubElement(root, 'documentation')
        doc.text = model.desc

    if model.props:
        _write_properties(root, model.props, model)

    _write_elements(root, model, xsi)
    _write_relationships(root, model, xsi)
    _write_organizations(root, model, ns_find)

    pd = et.SubElement(root, 'propertyDefinitions')
    for k, v in model.pdefs.items():
        p = et.SubElement(pd, 'propertyDefinition', identifier=k, type='string')
        p_name = et.SubElement(p, 'name')
        p_name.text = str(v)

    _write_views(root, model, xsi, ns_find)

    pd_check = root.find('propertyDefinitions')
    if pd_check is not None and pd_check.find('propertyDefinition') is None:
        root.remove(pd_check)

    xml_str = et.tostring(root, encoding='UTF-8', pretty_print=True)

    if file_path is not None:
        try:
            with open(file_path, 'wb') as fd:
                fd.write(xml_str)
        except IOError:
            log.error(f'{__mod__}.write: Cannot write to file "{file_path}')

    return xml_str.decode()
