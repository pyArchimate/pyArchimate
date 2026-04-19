"""Private helpers extracted from arisAMLreader to reduce cognitive complexity (S3776)."""
import ctypes
import platform
import sys
from typing import Any, Optional, cast

try:
    from ..constants import ARIS_TYPE_MAP as ARIS_type_map
    from ..enums import ArchiType, TextAlignment
    from ..exceptions import ArchimateConceptTypeError, ArchimateRelationshipError
    from ..helpers.logging import log
    from ..model import Model
    from ..relationship import get_default_rel_type
    from ..view import Node, Point, View
except ImportError:
    sys.path.insert(0, "..")
    from pyArchimate import (  # type: ignore[no-redef,attr-defined]  # noqa: E401
        ArchimateConceptTypeError,
        ArchimateRelationshipError,
        ArchiType,
        ARIS_type_map,
        Model,
        Node,
        Point,
        TextAlignment,
        View,
        get_default_rel_type,
        log,
    )


_ATTRDEF_TYPE = 'AttrDef.Type'
_POS_X = 'Pos.X'
_POS_Y = 'Pos.Y'


def get_text_size(text: str, points: int, font: str) -> tuple[float, float]:
    if platform.system() == 'Linux':
        from PIL import ImageFont
        fnt = ImageFont.truetype('DejaVuSans.ttf', points)
        bbox = fnt.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:
        class SIZE(ctypes.Structure):
            _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

        hdc = ctypes.windll.user32.GetDC(0)  # type: ignore[attr-defined]
        hfont = ctypes.windll.gdi32.CreateFontA(  # type: ignore[attr-defined]
            points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, font)
        hfont_old = ctypes.windll.gdi32.SelectObject(hdc, hfont)  # type: ignore[attr-defined]
        size = SIZE(0, 0)
        ctypes.windll.gdi32.GetTextExtentPoint32A(  # type: ignore[attr-defined]
            hdc, text, len(text), ctypes.byref(size))
        ctypes.windll.gdi32.SelectObject(hdc, hfont_old)  # type: ignore[attr-defined]
        ctypes.windll.gdi32.DeleteObject(hfont)  # type: ignore[attr-defined]
        return size.cx, size.cy


def id_of(_id: str) -> str:
    if '.' in _id:
        return 'id-' + _id.split('.')[1]
    return 'id-' + _id


def _parse_aris_attrs(elem: Any) -> tuple[Optional[str], Optional[str], dict[str, str]]:
    name: Optional[str] = None
    desc: Optional[str] = None
    props: dict[str, str] = {}
    for attr in elem.findall('AttrDef'):
        key = attr.attrib[_ATTRDEF_TYPE]
        val = ''.join(v.get('TextValue') + '\n' for v in attr.iter('PlainText'))
        if key == 'AT_NAME':
            name = val
        elif key == 'AT_DESC':
            desc = val
        else:
            props[key] = val
    return name, desc, props


def _parse_objdef(o: Any, model: Model, folder: str) -> None:
    if 'SymbolNum' not in o.attrib:
        return
    o_type = ARIS_type_map[o.attrib['SymbolNum']]
    if o_type == '':
        return
    guid = o.find('GUID').text
    o_uuid = id_of(o.attrib['ObjDef.ID'])
    o_name, o_desc, props = _parse_aris_attrs(o)
    props['GUID'] = guid
    elem = model.add(concept_type=o_type, name=o_name, desc=o_desc, uuid=o_uuid, folder=folder)
    for k, v in props.items():
        elem.prop(k, v)


def parse_elements(group: Any, root: Any, model: Model, folder: str = '') -> None:
    if group is None:
        group = root
    for g in group.findall('Group'):
        a = g.find('AttrDef')
        old_folder = folder
        if a is not None:
            for n in a.iter('PlainText'):
                folder += '/' + n.get('TextValue')
        for o in g.findall('ObjDef'):
            _parse_objdef(o, model, folder)
        parse_elements(g, root, model, folder)
        folder = old_folder


def _add_rel_with_fallback(model: Model, r_type: str, o_uuid: str,
                           r_target: str, r_id: str, props: dict[str, str]) -> None:
    try:
        r = model.add_relationship(rel_type=r_type, source=o_uuid, target=r_target, uuid=r_id)
    except ArchimateRelationshipError as exc:
        fallback_type = get_default_rel_type(model.elems_dict[o_uuid].type, model.elems_dict[r_target].type)
        log.warning(str(exc) + f' - Replacing by {fallback_type}')
        if fallback_type is None:
            return
        r = model.add_relationship(rel_type=fallback_type, source=o_uuid, target=r_target, uuid=r_id)
    if r is not None:
        for key, value in props.items():
            r.prop(key, value)


def _collect_cxn_props(rel: Any) -> dict[str, str]:
    props: dict[str, str] = {}
    for attr in rel.findall('AttrDef'):
        key = attr.attrib[_ATTRDEF_TYPE]
        val = ''.join(v.get('TextValue') + '\n' for v in attr.iter('PlainText'))
        props[key] = val
    return props


def _process_objdef_rels(o: Any, model: Model) -> None:
    o_uuid = id_of(o.attrib['ObjDef.ID'])
    for rel in o.findall('CxnDef'):
        r_type = ARIS_type_map[rel.attrib['CxnDef.Type']]
        r_id = id_of(rel.attrib['CxnDef.ID'])
        r_target = id_of(rel.attrib.get('ToObjDef.IdRef'))
        if r_target not in model.elems_dict:
            continue
        _add_rel_with_fallback(model, r_type, o_uuid, r_target, r_id, _collect_cxn_props(rel))


def parse_relationships(groups: Any, root: Any, model: Model) -> None:
    if groups is None:
        groups = root
    for g in groups.findall('Group'):
        for o in g.findall('ObjDef'):
            _process_objdef_rels(o, model)
        parse_relationships(g, root, model)


def parse_nodes(grp: Any, view: Optional[View], model: Model,
                scale_x: float, scale_y: float) -> None:
    if grp is None or view is None:
        return
    if not isinstance(view, View):
        raise ArchimateConceptTypeError("'view' is not an instance of class 'View'")
    for o in grp.findall('ObjOcc'):
        o_type = ARIS_type_map[o.attrib['SymbolNum']]
        o_id = id_of(o.attrib['ObjOcc.ID'])
        o_elem_ref = model.elems_dict[id_of(o.attrib['ObjDef.IdRef'])].uuid
        pos = o.find('Position')
        size = o.find('Size')
        n = view.add(ref=o_elem_ref,
                     x=int(int(pos.get(_POS_X)) * scale_x),
                     y=int(int(pos.get(_POS_Y)) * scale_y),
                     w=int(int(size.get('Size.dX')) * scale_x),
                     h=int(int(size.get('Size.dY')) * scale_y),
                     uuid=o_id)
        if o_type == 'Grouping':
            n.fill_color = "#FFFFFF"
            n.opacity = 100


def _handle_embedding(conn: Any, o_id: str, model: Model) -> None:
    c_target = id_of(conn.get('ToObjOcc.IdRef'))
    try:
        nt = model.nodes_dict[c_target]
        ns = model.nodes_dict[o_id]
        if not (nt.x >= ns.x and nt.y >= ns.y
                and nt.x + nt.w <= ns.x + ns.w and nt.y + nt.h <= ns.y + ns.h):
            ns.move(nt)
        else:
            nt.move(ns)
    except ArchimateConceptTypeError as exc:
        log.warning(exc)
    except ArchimateRelationshipError as exc:
        log.warning(exc)
    except ValueError as exc:
        log.warning(exc)
    except KeyError:
        log.error(f'Orphan Connection with unrelated relationship {id_of(conn.attrib["CxnDef.IdRef"])} ')


def _handle_regular_conn(conn: Any, o_id: str, view: View, model: Model,
                         scale_x: float, scale_y: float) -> None:
    c_id = id_of(conn.attrib['CxnOcc.ID'])
    c_rel_id = id_of(conn.attrib['CxnDef.IdRef'])
    c_target = id_of(conn.get('ToObjOcc.IdRef'))
    if c_rel_id not in model.rels_dict:
        return
    c = view.add_connection(ref=c_rel_id, source=o_id, target=c_target, uuid=c_id)
    for i, pos in enumerate(conn.findall('Position')):
        if 0 < i < len(conn.findall('Position')) - 1:
            c.add_bendpoint(Point(int(pos.get(_POS_X)) * scale_x,
                                  int(pos.get(_POS_Y)) * scale_y))


def parse_connections(grp: Any, view: Optional[View], model: Model,
                      scale_x: float, scale_y: float) -> None:
    if grp is None or view is None:
        return
    if not isinstance(view, View):
        raise ValueError("'view' is not an instance of class 'View'")
    for o in grp.findall('ObjOcc'):
        o_id = id_of(o.attrib['ObjOcc.ID'])
        for conn in o.findall('CxnOcc'):
            if 'Embedding' in conn.attrib and conn.attrib['Embedding'] == 'YES':
                _handle_embedding(conn, o_id, model)
            else:
                _handle_regular_conn(conn, o_id, view, model, scale_x, scale_y)


def parse_containers(grp: Any, view: Optional[View], scale_x: float, scale_y: float) -> None:
    if grp is None or view is None:
        return
    if not isinstance(view, View):
        raise ArchimateConceptTypeError("'view' is not an instance of class 'View'")
    for objs in grp.findall('GfxObj'):
        for o in objs.findall('RoundedRectangle'):
            pos = o.find('Position')
            size = o.find('Size')
            brush = o.find('Brush')
            if pos is not None and size is not None:
                n = view.add(ref=None,
                             x=int(int(pos.get(_POS_X)) * scale_x),
                             y=int(int(pos.get(_POS_Y)) * scale_y),
                             w=int(int(size.get('Size.dX')) * scale_x),
                             h=int(int(size.get('Size.dY')) * scale_y),
                             node_type='Container')
                n.line_color = f'#{int(brush.get("Color")):0>6X}' if brush is not None else "#000000"
                n.fill_color = "#FFFFFF"
                n.opacity = 100


def parse_labels(root: Any, model: Model) -> None:
    for o in root.findall('FFTextDef'):
        o_id = id_of(o.attrib['FFTextDef.ID'])
        if o.attrib['IsModelAttr'] == 'TEXT':
            o_name = None
            for attr in o.findall('AttrDef'):
                key = attr.attrib[_ATTRDEF_TYPE]
                val = ''
                for v in attr.iter('PlainText'):
                    val += v.get('TextValue') + '\n'
                if key == 'AT_NAME':
                    o_name = val
            model.labels_dict[o_id] = o_name


def parse_labels_in_view(grp: Any, view: Optional[View], model: Model,
                         scale_x: float, scale_y: float) -> None:
    if grp is None or view is None:
        return
    if not isinstance(view, View):
        raise ArchimateConceptTypeError("'view' is not an instance of class 'View'")
    for objs in grp.findall('FFTextOcc'):
        lbl_ref = id_of(objs.attrib['FFTextDef.IdRef'])
        if lbl_ref not in model.labels_dict:
            continue
        o_name = model.labels_dict[lbl_ref]
        o = objs.find('Position')
        if o is None:
            continue
        pos = o.attrib
        w, h = max([get_text_size(x, 9, "Segoe UI") for x in o_name.split('\n')])
        try:
            n = view.add(ref=lbl_ref,
                         x=max(int(float(pos.get(_POS_X, '0')) * scale_x), 0),
                         y=max(int(float(pos.get(_POS_Y, '0')) * scale_y), 0),
                         w=int(w) + 18,
                         h=30 + (h * 1.5) * (o_name.count('\n') + 1),
                         node_type='Label', label=o_name)
            n.fill_color = "#FFFFFF"
            n.opacity = 100
            n.line_color = '#000000'
            n.border_type = "2"
            n.text_alignment = TextAlignment.Left
        except ValueError:
            log.warning(f'Node {o_name} has unknown element reference {lbl_ref} - ignoring')


def _build_view(o: Any, model: Model, folder: str, scale_x: float, scale_y: float) -> None:
    view_id = id_of(o.attrib['Model.ID'])
    o_name, o_desc, _ = _parse_aris_attrs(o)
    view = cast(View, model.add(concept_type=ArchiType.View, name=o_name, uuid=view_id, desc=o_desc))
    view.folder = folder
    log.info('Parsing & adding nodes')
    parse_nodes(o, view, model, scale_x, scale_y)
    log.info('Parsing & adding conns')
    parse_connections(o, view, model, scale_x, scale_y)
    log.info('Parsing and adding container groups')
    parse_containers(o, view, scale_x, scale_y)
    log.info('Parsing and adding labels')
    parse_labels_in_view(o, view, model, scale_x, scale_y)


def parse_views(group: Any, root: Any, model: Model, scale_x: float, scale_y: float,
                folder: str = '') -> None:
    if group is None:
        group = root
    for g in group.findall('Group'):
        a = g.find('AttrDef')
        old_folder = folder
        if a is not None:
            for n in a.iter('PlainText'):
                folder += '/' + n.get('TextValue')
        for o in g.findall('Model'):
            _build_view(o, model, folder, scale_x, scale_y)
        parse_views(g, root, model, scale_x, scale_y, folder)
        folder = old_folder


def clean_nested_conns(model: Model) -> None:
    for c in [x for x in model.conns_dict.values()
              if x.source.uuid == x.parent.uuid and isinstance(x.parent, Node)]:
        c.delete()
    for c in [x for x in model.conns_dict.values()
              if x.target.uuid == x.parent.uuid and isinstance(x.parent, Node)]:
        c.delete()
