import os
import sys

try:
    from ..constants import RGBA
    from ..enums import ArchiType
    from ..helpers.logging import log
    from ..view import Point
except ImportError:
    sys.path.insert(0, "..")
    from pyArchimate import RGBA, ArchiType, Point, log  # type: ignore[no-redef,attr-defined]

__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def _read_pdefs(model, root, ns, merge_flg):
    pdef_merge_map: dict[str, str] = {}
    pdefs = root.find(ns + 'propertyDefinitions')
    if pdefs is None:
        return pdef_merge_map
    for p in pdefs.findall(ns + 'propertyDefinition'):
        _id = p.get('identifier')
        val = p.find(ns + 'name').text
        pdef_merge_map[_id] = _id
        if merge_flg and _id in model.pdefs and model.pdefs[_id] != val:
            pdef_merge_map[_id] = 'propid-' + str(len(model.pdefs) + 1)
            _id = pdef_merge_map[_id]
        model.pdefs[_id] = val
    return pdef_merge_map


def _read_props(obj, xml_elem, ns, pdef_merge_map, model):
    props = xml_elem.find(ns + 'properties')
    if props is None:
        return
    for p in props.findall(ns + 'property'):
        _id = pdef_merge_map[p.get('propertyDefinitionRef')]
        obj.prop(model.pdefs[_id], p.find(ns + 'value').text)


def _read_elements(model, root, ns, xsi, pdef_merge_map, merge_flg):
    elements_xml = root.find(ns + 'elements')
    if elements_xml is None:
        return
    for e in elements_xml.findall(ns + 'element'):
        _uuid = e.get('identifier')
        name = None if e.find(ns + 'name') is None else e.find(ns + 'name').text
        desc = None if e.find(ns + 'documentation') is None else e.find(ns + 'documentation').text
        if merge_flg and _uuid in model.elems_dict:
            elem = model.elems_dict[_uuid]
            elem.name = name
            elem.desc = desc
        else:
            elem = model.add(
                name=name,
                concept_type=e.get(xsi + 'type'),
                uuid=_uuid,
                desc=desc,
            )
        _read_props(elem, e, ns, pdef_merge_map, model)


def _read_relationships(model, root, ns, xsi, pdef_merge_map, merge_flg):
    rels_xml = root.find(ns + 'relationships')
    if rels_xml is None:
        return
    for r in rels_xml.findall(ns + 'relationship'):
        _uuid = r.get('identifier')
        name = None if r.find(ns + 'name') is None else r.find(ns + 'name').text
        desc = None if r.find(ns + 'documentation') is None else r.find(ns + 'documentation').text
        if merge_flg and _uuid in model.rels_dict:
            rel = model.rels_dict[_uuid]
            rel.name = name
            rel.desc = desc
        else:
            rel = model.add_relationship(
                source=r.get('source'),
                target=r.get('target'),
                rel_type=r.get(xsi + 'type'),
                uuid=r.get('identifier'),
                name=name,
                desc=desc,
                access_type=r.get('accessType'),
                influence_strength=r.get('modifier'),
            )
            if r.get('isDirected') == 'true':
                rel.is_directed = True
            _read_props(rel, r, ns, pdef_merge_map, model)


def _apply_node_style(node, style_xml, ns):
    if style_xml is None:
        return
    fc = style_xml.find(ns + 'fillColor')
    if fc is not None:
        node.fill_color = RGBA(fc.get('r'), fc.get('g'), fc.get('b')).color
        if fc.get('a') is not None:
            node.opacity = int(fc.get('a'))
    lc = style_xml.find(ns + 'lineColor')
    if lc is not None:
        node.line_color = RGBA(lc.get('r'), lc.get('g'), lc.get('b')).color
        if lc.get('a') is not None:
            node.lc_opacity = int(lc.get('a'))
    ft = style_xml.find(ns + 'font')
    if ft is not None:
        node.font_name = ft.get('name')
        node.font_size = ft.get('size')
        ftc = ft.find(ns + 'color')
        if ftc is not None:
            node.font_color = RGBA(ftc.get('r'), ftc.get('g'), ftc.get('b')).color


def _add_node(parent, node_xml, ns, xsi, model, merge_flg):
    _uuid = node_xml.get('identifier')
    if merge_flg and _uuid in model.nodes_dict:
        _uuid = None
    if node_xml.get(xsi + 'type') == 'Element':
        _n = parent.add(
            uuid=_uuid,
            ref=node_xml.get('elementRef'),
            x=node_xml.get('x'),
            y=node_xml.get('y'),
            w=node_xml.get('w'),
            h=node_xml.get('h'),
        )
    else:
        view_ref = node_xml.find(ns + 'viewRef')
        ref = view_ref.get('ref') if view_ref is not None else None
        cat = 'Model' if view_ref is not None else node_xml.get(xsi + 'type')
        label = node_xml.find(ns + 'label')
        _n = parent.add(
            uuid=_uuid,
            ref=ref,
            x=node_xml.get('x'),
            y=node_xml.get('y'),
            w=node_xml.get('w'),
            h=node_xml.get('h'),
            node_type=cat,
            label=None if label is None else label.text,
        )
    _apply_node_style(_n, node_xml.find(ns + 'style'), ns)
    for sub_xml in node_xml.findall(ns + 'node'):
        _sub = _add_node(_n, sub_xml, ns, xsi, model, merge_flg)
        _n.nodes_dict[_sub.uuid] = _sub
        _n.model.nodes_dict[_sub.uuid] = _sub
    return _n


def _apply_conn_style(conn, style_xml, ns):
    if style_xml is None:
        return
    lc = style_xml.find(ns + 'lineColor')
    if lc is not None:
        conn.line_color = RGBA(lc.get('r'), lc.get('g'), lc.get('b')).color
    ft = style_xml.find(ns + 'font')
    if ft is not None:
        conn.font_name = ft.get('name')
        conn.font_size = ft.get('size')
        ftc = ft.find(ns + 'color')
        conn.font_color = RGBA(ftc.get('r'), ftc.get('g'), ftc.get('b')).color
    conn.line_width = style_xml.get('lineWidth')


def _read_views(model, root, ns, xsi, pdef_merge_map, merge_flg):
    views_xml = root.find(ns + 'views')
    if views_xml is None:
        return
    for v in views_xml.find(ns + 'diagrams').findall(ns + 'view'):
        _uuid = v.get('identifier')
        if merge_flg and _uuid in model.views_dict:
            model.views_dict[_uuid].delete()
        _v = model.add(
            ArchiType.View,
            name=None if v.find(ns + 'name') is None else v.find(ns + 'name').text,
            uuid=_uuid,
            desc=None if v.find(ns + 'documentation') is None else v.find(ns + 'documentation').text,
        )
        _read_props(_v, v, ns, pdef_merge_map, model)
        for n in v.findall(ns + 'node'):
            _add_node(_v, n, ns, xsi, model, merge_flg)
        for c in v.findall(ns + 'connection'):
            _uuid_c = c.get('identifier')
            if merge_flg and _uuid_c is not None:
                _uuid_c = None
            _c = _v.add_connection(
                ref=c.get('relationshipRef'),
                source=c.get('source'),
                target=c.get('target'),
                uuid=_uuid_c,
            )
            _apply_conn_style(_c, c.find(ns + 'style'), ns)
            for bp in c.findall(ns + 'bendpoint'):
                _c.add_bendpoint(Point(bp.get('x'), bp.get('y')))


def _walk_orgs(item, ns, model, folder=''):
    items = item.findall(ns + 'item')
    label = item.find(ns + 'label')
    if label is not None:
        folder += '/' + label.text
    if item.find(ns + 'documentation') is not None:
        desc = item.find(ns + 'documentation').text
        ref_id = item.find(ns + 'item').get('identifierRef')
        _v = model.views_dict[ref_id]
        _v.desc = desc
        _v.folder = folder
    else:
        for sub_item in items:
            ref_id = sub_item.get('identifierRef')
            if ref_id is not None:
                if ref_id in model.views_dict:
                    model.views_dict[ref_id].folder = folder
                elif ref_id in model.elems_dict:
                    model.elems_dict[ref_id].folder = folder
                elif ref_id in model.rels_dict:
                    model.rels_dict[ref_id].folder = folder
            else:
                _walk_orgs(sub_item, ns, model, folder)


def _read_organizations(model, root, ns):
    orgs = root.find(ns + 'organizations')
    if orgs is None:
        return
    for item in orgs.findall(ns + 'item'):
        _walk_orgs(item, ns, model)


def archimate_reader(model, root, merge_flg=False):
    """
    Merge / initialize the model from XML Archi tool data

    Used by Model.read(filepath) or Model.merge(filepath) methods

    :param model: pyArchimate Model object
    :type model: Model
    :param root:    XML data to convert
    :type root:
    :param merge_flg: if True, merge data into the provided model, else clear the model and read data into it
    :type merge_flg: bool

    """
    if 'opengroup' not in root.tag:
        log.fatal(f'{__mod__}: Input file is not an Open Group Archimate file - Aborting')
        return None

    ns = root.tag.split('model')[0]
    xsi = '{http://www.w3.org/2001/XMLSchema-instance}'

    model.name = None if root.find(ns + 'name') is None else root.find(ns + 'name').text
    model.desc = None if root.find(ns + 'documentation') is None else root.find(ns + 'documentation').text

    pdef_merge_map = _read_pdefs(model, root, ns, merge_flg)
    _read_props(model, root, ns, pdef_merge_map, model)
    _read_elements(model, root, ns, xsi, pdef_merge_map, merge_flg)
    _read_relationships(model, root, ns, xsi, pdef_merge_map, merge_flg)
    _read_views(model, root, ns, xsi, pdef_merge_map, merge_flg)
    _read_organizations(model, root, ns)
