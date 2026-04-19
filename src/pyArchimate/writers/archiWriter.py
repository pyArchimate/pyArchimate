import os
import sys
from typing import cast as _cast

from lxml import etree as et
from lxml.etree import _Element

try:
    from ..constants import ARCHI_CATEGORY as archi_category
    from ..element import set_id
    from ..enums import ArchiType
    from ..helpers.logging import log
    from ..model import Model
    from ..view import View
except ImportError:
    sys.path.insert(0, "..")
    from pyArchimate import ArchiType, Model, View, archi_category, log, set_id  # type: ignore[no-redef,attr-defined]

__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def _create_folders(root: _Element) -> dict[str, _Element]:
    f_strategy = et.SubElement(root, 'folder', name="Strategy", id=set_id(), type="strategy")
    f_business = et.SubElement(root, 'folder', name="Business", id=set_id(), type="business")
    f_application = et.SubElement(root, 'folder', name="Application", id=set_id(), type="application")
    f_technology = et.SubElement(root, 'folder', name="Technology", id=set_id(), type="technology")
    f_motivation = et.SubElement(root, 'folder', name="Motivation", id=set_id(), type="motivation")
    f_implementation = et.SubElement(root, 'folder', name="Implementation", id=set_id(),
                                     type="implementation_migration")
    f_other = et.SubElement(root, 'folder', name="Other", id=set_id(), type="other")
    f_relations = et.SubElement(root, 'folder', name="Relations", id=set_id(), type="relations")
    f_views = et.SubElement(root, 'folder', name="Views", id=set_id(), type="diagrams")
    return {
        "/Strategy": f_strategy, "/Business": f_business, "/Application": f_application,
        "/Technology": f_technology, "/Motivation": f_motivation,
        "/Implementation & Migration": f_implementation, "/Other": f_other,
        "/Physical": f_technology, "/Relations": f_relations, "/Views": f_views,
        "/Junction": f_other
    }


def _get_folder(folders: dict[str, _Element], folder_str: str) -> _Element:
    paths = folder_str.split('/')[1:]
    prev_f = folders['/' + paths[0]]
    cur_path = ''
    f = None
    for p in paths:
        cur_path += '/' + p
        f = folders[cur_path] if cur_path in folders else None
        if f is None:
            f = et.SubElement(prev_f, 'folder', name=p, id=set_id())
            folders[cur_path] = f
        prev_f = f
    return _cast(_Element, f)


def _resolve_folder_path(obj_folder: str | None, cat: str) -> str:
    if obj_folder is None:
        return '/' + cat
    if obj_folder.startswith('/' + cat):
        return obj_folder
    return '/' + cat + obj_folder


def _write_element(folders: dict[str, _Element], elem: object, xsi: et.QName) -> None:
    elem_type = getattr(elem, 'type', '')
    cat = archi_category[elem_type].split('-')[0]
    if cat == "Junction":
        cat = "Other"
    elif cat == "Physical":
        cat = 'Technology'
    folder_path = _resolve_folder_path(getattr(elem, 'folder', None), cat)
    folder = _get_folder(folders, folder_path)
    if elem_type == 'Junction':
        junction_type = getattr(elem, 'junction_type', 'and')
        setattr(elem, 'type', junction_type.capitalize() + elem_type)  # noqa: B010
        elem_type = getattr(elem, 'type', '')
    e = et.SubElement(folder, 'element', {
        str(xsi): 'archimate:' + elem_type,
        'id': getattr(elem, 'uuid', '')
    })
    name = getattr(elem, 'name', None)
    if name is not None:
        e.set('name', name)
    desc = getattr(elem, 'desc', None)
    if desc is not None:
        doc = et.SubElement(e, 'documentation')
        doc.text = desc
    for k, v in getattr(elem, 'props', {}).items():
        et.SubElement(e, 'property', key=k, value=str(v))
    profile_id = getattr(elem, 'profile_id', None)
    if profile_id is not None:
        e.set('profiles', profile_id)


def _write_relationship(folders: dict[str, _Element], rel: object, xsi: et.QName) -> None:
    rel_folder = _resolve_folder_path(getattr(rel, 'folder', None), 'Relations')
    folder = _get_folder(folders, rel_folder)
    source = getattr(rel, 'source', None)
    target = getattr(rel, 'target', None)
    assert source is not None and target is not None
    rel_type = getattr(rel, 'type', '')
    r = et.SubElement(folder, 'element', {
        str(xsi): 'archimate:' + rel_type + 'Relationship',
        'id': getattr(rel, 'uuid', ''),
        'source': source.uuid,
        'target': target.uuid
    })
    name = getattr(rel, 'name', None)
    if name is not None:
        r.set('name', name)
    access_type = getattr(rel, 'access_type', None)
    if access_type == "Read":
        r.set("accessType", "1")
    elif access_type == "ReadWrite":
        r.set("accessType", "3")
    elif access_type == "Access":
        r.set("accessType", "2")
    is_directed = getattr(rel, 'is_directed', None)
    if is_directed is not None:
        r.set("directed", str(is_directed).lower())
    influence_strength = getattr(rel, 'influence_strength', None)
    if influence_strength is not None:
        r.set("strength", influence_strength)
    desc = getattr(rel, 'desc', None)
    if desc is not None:
        doc = et.SubElement(r, 'documentation')
        doc.text = desc
    for k, v in getattr(rel, 'props', {}).items():
        et.SubElement(r, 'property', key=k, value=str(v))
    profile_id = getattr(rel, 'profile_id', None)
    if profile_id is not None:
        r.set('profiles', profile_id)


def _write_connection(child: _Element, conn: object, xsi: et.QName) -> None:
    conn_source = getattr(conn, 'source', None)
    conn_target = getattr(conn, 'target', None)
    assert conn_source is not None and conn_target is not None
    c = et.SubElement(child, 'sourceConnection', {
        str(xsi): "archimate:Connection",
        'id': getattr(conn, 'uuid', ''),
        'lineWidth': "1",
        'source': conn_source.uuid,
        'target': conn_target.uuid,
        'archimateRelationship': getattr(conn, 'ref', '')
    })
    if not getattr(conn, 'show_label', True):
        et.SubElement(c, 'feature', name='nameVisible',
                      value=str(getattr(conn, 'show_label', True)).lower())
    line_width = getattr(conn, 'line_width', None)
    if line_width is not None:
        c.set('lineWidth', str(line_width))
    font_name = getattr(conn, 'font_name', None)
    font_size = getattr(conn, 'font_size', None)
    if font_name is not None and font_size is not None:
        c.set('font', f"1|{font_name}|{int(font_size)}|0|WINDOWS|1|0|0|0|0|0|0|0|0|1|0|0|0|0|{font_name}")
    font_color = getattr(conn, 'font_color', None)
    if font_color is not None:
        c.set('fontColor', font_color.lower())
    line_color = getattr(conn, 'line_color', None)
    if line_color is not None:
        c.set('lineColor', line_color.lower())
    text_position = getattr(conn, 'text_position', None)
    if text_position is not None:
        c.set('textPosition', text_position)
    for bp in getattr(conn, 'bendpoints', []):
        et.SubElement(c, 'bendpoint',
                      startX=str(int(bp.x - conn_source.cx)),
                      startY=str(int(bp.y - conn_source.cy)),
                      endX=str(int(bp.x - conn_target.cx)),
                      endY=str(int(bp.y - conn_target.cy)))


def _set_node_visual_attrs(child: _Element, node: object) -> None:
    font_name = getattr(node, 'font_name', None)
    font_size = getattr(node, 'font_size', None)
    if font_name is not None and font_size is not None:
        size = str(float(font_size))
        child.set('font', f"1|{font_name}|{size}|0|WINDOWS|1|0|0|0|0|0|0|0|0|1|0|0|0|0|{font_name}")
    font_color = getattr(node, 'font_color', None)
    if font_color is not None:
        child.set('fontColor', font_color.lower())
    line_color = getattr(node, 'line_color', None)
    if line_color is not None:
        child.set('lineColor', line_color.lower())
    fill_color = getattr(node, 'fill_color', None)
    if fill_color is not None:
        child.set('fillColor', fill_color.lower())
    opacity = getattr(node, 'opacity', 100)
    if str(opacity) != '100':
        child.set('alpha', str(int(255 * int(opacity) / 100)))
    lc_opacity = getattr(node, 'lc_opacity', 100)
    if str(lc_opacity) != '100':
        et.SubElement(child, 'feature', name='lineAlpha', value=str(int(255 * int(lc_opacity) / 100)))


def _set_node_features(child: _Element, node: object) -> None:
    label_expression = getattr(node, 'label_expression', None)
    if label_expression is not None:
        et.SubElement(child, 'feature', name='labelExpression', value=label_expression)
    icon_color = getattr(node, 'iconColor', None)
    if icon_color is not None:
        et.SubElement(child, 'feature', name='iconColor', value=icon_color)
    gradient = getattr(node, 'gradient', None)
    if gradient is not None:
        et.SubElement(child, 'feature', name='gradient', value=gradient)


def _set_node_cat_content(child: _Element, node: object, xsi: et.QName) -> None:
    cat = getattr(node, 'cat', 'Element')
    node_ref = getattr(node, 'ref', None)
    node_label = getattr(node, 'label', None)
    if cat == 'Element':
        child.set('archimateElement', node_ref or '')
    elif cat == "Container":
        child.set(str(xsi), 'archimate:Group')
        child.set('name', node_label or '')
    elif cat == "Label":
        child.set(str(xsi), 'archimate:Note')
        content = et.SubElement(child, 'content')
        content.text = node_label
    elif cat == "Model":
        child.set(str(xsi), 'archimate:DiagramModelReference')
        child.set('model', node_ref or '')
    text_alignment = getattr(node, 'text_alignment', None)
    if text_alignment is not None:
        child.set('textAlignment', text_alignment)
    text_position = getattr(node, 'text_position', None)
    if text_position is not None:
        child.set('textPosition', text_position)
    border_type = getattr(node, 'border_type', None)
    if border_type is not None:
        child.set('borderType', border_type)


def _add_node(parent: object, parent_tag: _Element, node: object, xsi: et.QName) -> None:
    child = et.SubElement(parent_tag, 'child', {
        str(xsi): 'archimate:DiagramObject',
        'id': getattr(node, 'uuid', ''),
    })
    _set_node_visual_attrs(child, node)
    _set_node_features(child, node)
    _set_node_cat_content(child, node, xsi)
    node_type = getattr(node, 'type', None)
    fill_color = getattr(node, 'fill_color', None)
    if node_type == ArchiType.Grouping and fill_color is None:
        setattr(node, 'opacity', 0)  # noqa: B010
    node_x = getattr(node, 'x', 0)
    node_y = getattr(node, 'y', 0)
    if isinstance(parent, View):
        et.SubElement(child, 'bounds', x=str(node_x), y=str(node_y),
                      width=str(getattr(node, 'w', 120)), height=str(getattr(node, 'h', 55)))
    else:
        parent_x = getattr(parent, 'x', 0)
        parent_y = getattr(parent, 'y', 0)
        et.SubElement(child, 'bounds', x=str(node_x - parent_x), y=str(node_y - parent_y),
                      width=str(getattr(node, 'w', 120)), height=str(getattr(node, 'h', 55)))
    for conn in getattr(node, 'out_conns', lambda: [])():
        _write_connection(child, conn, xsi)
    targets = [conn.uuid for conn in getattr(node, 'in_conns', lambda: [])()]
    if targets:
        child.set('targetConnections', ' '.join(targets))
    for sub_n in getattr(node, 'nodes', []):
        _add_node(node, child, sub_n, xsi)


def archi_writer(model: Model, file_path: str) -> str:
    """
    Write a Model to Archi (.archimate) XML format.

    :param model: the model to write
    :param file_path: output file path
    """
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:archimate="http://www.archimatetool.com/archimate" name="(new model)" id="id-2b0c639b388044d09709ceaaadbcf40f" version="4.9.0">
    </archimate:model>
    """

    root = et.fromstring(xml)
    xsi_url = 'http://www.w3.org/2001/XMLSchema-instance'
    xsi = et.QName(xsi_url, 'type')
    folders = _create_folders(root)

    for elem in model.elements:
        _write_element(folders, elem, xsi)

    for rel in model.relationships:
        _write_relationship(folders, rel, xsi)

    for view in model.views:
        view_folder_path = _resolve_folder_path(view.folder, 'Views')
        view_folder = _get_folder(folders, view_folder_path)
        e = et.SubElement(view_folder, 'element', {
            str(xsi): 'archimate:ArchimateDiagramModel',
            'name': view.name,
            'id': view.uuid
        })
        for n in view.nodes:
            _add_node(view, e, n, xsi)
        if view.desc is not None:
            doc = et.SubElement(e, 'documentation')
            doc.text = view.desc
        for k, v in view.props.items():
            et.SubElement(e, 'property', key=k, value=str(v))

    root.set('name', model.name or '')
    if model.desc is not None:
        doc = et.SubElement(root, 'purpose')
        doc.text = model.desc
    for k, v in model.props.items():
        et.SubElement(root, 'property', key=k, value=str(v))

    for p in model.profiles:
        et.SubElement(root, 'profile', name=p.name, id=p.uuid, conceptType=p.concept)

    xml_str = et.tostring(root, encoding='UTF-8', pretty_print=True)

    if file_path is not None:
        try:
            with open(file_path, 'wb') as fd:
                fd.write(xml_str)
        except IOError:
            log.error(f'{__mod__}.write: Cannot write to file "{file_path}')

    return xml_str.decode()
