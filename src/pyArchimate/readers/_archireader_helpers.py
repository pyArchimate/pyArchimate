"""Private helpers extracted from archiReader to reduce cognitive complexity (S3776)."""
from typing import Any

try:
    from ..enums import AccessType, ArchiType
    from ..helpers.logging import log
    from ..view import Node, Point, View
except ImportError:
    import sys
    sys.path.insert(0, "..")
    from pyArchimate import AccessType, ArchiType, Node, Point, View, log  # type: ignore[no-redef,attr-defined]


def _parse_node_type(parent: Any, child: Any, xsi: str) -> Any:
    type_n = child.get(xsi + 'type').split(':')[1]
    if type_n == 'DiagramObject':
        node = parent.add(ref=child.get('archimateElement'), uuid=child.get('id'))
        if node is not None and node.concept.prop('label') is not None:
            node.label_expression = str(node.concept.prop('label'))
    elif type_n == 'Group':
        node = parent.add(ref=child.get('archimateElement'), uuid=child.get('id'),
                          node_type='Container', label=child.get('name'))
        if child.get('borderType'):
            node.border_type = child.get('borderType')
    elif type_n == 'Note':
        node = parent.add(ref=child.get('archimateElement'), uuid=child.get('id'), node_type='Label')
        node.label = child.find('content').text if child.find('content') is not None else None
    elif type_n == 'DiagramModelReference':
        node = parent.add(ref=child.get('model'), uuid=child.get('id'), node_type="Model")
    else:
        node = None
    return node, type_n


def _parse_node_attributes(node: Any, child: Any, parent: Any) -> None:
    bounds = child.find('bounds')
    parent_x = parent.x if isinstance(parent, Node) else 0
    parent_y = parent.y if isinstance(parent, Node) else 0
    nx = 0 if bounds.get('x') is None else bounds.get('x')
    ny = 0 if bounds.get('y') is None else bounds.get('y')
    node.x = int(nx) + parent_x
    node.y = int(ny) + parent_y
    node.w = int(bounds.get('width'))
    node.h = int(bounds.get('height'))
    if child.get('font') is not None:
        font_param = child.get('font').split('|')
        node.font_name = font_param[1]
        node.font_size = float(font_param[2])
    if child.get('fontColor') is not None:
        node.font_color = child.get('fontColor')
    if child.get('lineColor') is not None:
        node.line_color = child.get('lineColor')
    if child.get('fillColor') is not None:
        node.fill_color = child.get('fillColor')
    if child.get('alpha') is not None:
        node.opacity = 100 * int(child.get('alpha')) / 255
    for ft in child.findall('feature'):
        ft_name = ft.get('name')
        if ft_name == 'lineAlpha':
            node.lc_opacity = 100 * int(ft.get('value')) / 255
        elif ft_name == 'labelExpression':
            node.label_expression = ft.get('value')
        elif ft_name == 'iconColor':
            node.iconColor = ft.get('value')
        elif ft_name == 'gradient':
            node.gradient = ft.get('value')
    node.text_alignment = child.get('textAlignment')
    node.text_position = child.get('textPosition')


def get_node(tag: Any, parent: Any, xsi: str) -> None:
    for child in tag.findall('child'):
        node, type_n = _parse_node_type(parent, child, xsi)
        if node is None:
            log.warning(f"Invalid node {child.get('id')} with type {type_n}")
            continue
        _parse_node_attributes(node, child, parent)
        get_node(child, node, xsi)


def _resolve_bp_coords(bp: Any, source_node: Any, target_node: Any) -> tuple[int, int]:
    x, y = 0, 0
    if bp.get('startX') is not None:
        x = int(bp.get('startX')) + source_node.cx
    if bp.get('startY') is not None:
        y = int(bp.get('startY')) + source_node.cy
    if bp.get('endX') is not None:
        x = int(bp.get('endX')) + target_node.cx
    if bp.get('endY') is not None:
        y = int(bp.get('endY')) + target_node.cy
    return x, y


def _parse_connection(sc: Any, parent: View) -> None:
    ref = sc.get('archimateRelationship')
    if ref not in parent.model.rels_dict:
        log.warning(f'Unknown connection ref {ref}')
        return
    conn = parent.add_connection(ref=ref, source=sc.get('source'),
                                 target=sc.get('target'), uuid=sc.get('id'))
    if sc.get('fontColor') is not None:
        conn.font_color = sc.get('fontColor')
    if sc.get('lineColor') is not None:
        conn.line_color = sc.get('lineColor')
    if sc.get('lineWidth') is not None:
        conn.line_width = int(sc.get('lineWidth'))
    conn.text_position = sc.get('textPosition')
    source_node = (parent.model.nodes_dict[sc.get('source')]
                   if sc.get('source') in parent.model.nodes_dict
                   else parent.model.conns_dict[sc.get('source')])
    target_node = (parent.model.nodes_dict[sc.get('target')]
                   if sc.get('target') in parent.model.nodes_dict
                   else parent.model.conns_dict[sc.get('target')])
    ft = sc.find('feature')
    if ft is not None and ft.get('name') == 'nameVisible':
        conn.show_label = bool(ft.get('value'))
    for bp in sc.findall('bendpoint'):
        _x, _y = _resolve_bp_coords(bp, source_node, target_node)
        conn.add_bendpoint(Point(_x, _y))


def get_connection(tag: Any, parent: View) -> None:
    for child in tag.findall('child'):
        for sc in child.findall('sourceConnection'):
            _parse_connection(sc, parent)
        get_connection(child, parent)


def _resolve_rel_endpoints(e: Any, model: Any) -> tuple[Any, Any] | None:
    src_id, dst_id = e.get('source'), e.get('target')
    if (src_id not in model.elems_dict and src_id not in model.rels_dict) \
            or (dst_id not in model.elems_dict and dst_id not in model.rels_dict):
        log.warning(f"Invalid {src_id} or {dst_id}")
        return None
    src = model.elems_dict[src_id] if src_id in model.elems_dict else model.rels_dict[src_id]
    dst = model.elems_dict[dst_id] if dst_id in model.elems_dict else model.rels_dict[dst_id]
    return src, dst


def _parse_rel_attributes(elem: Any, e: Any) -> None:
    at = e.get('accessType')
    if at is not None:
        elem.access_type = (AccessType.Read if at == "1"
                            else AccessType.ReadWrite if at == "3"
                            else AccessType.Access)
    else:
        elem.access_type = AccessType.Write
    if e.get('directed') is not None:
        elem.is_directed = e.get('directed') == "true"
    if e.get('strength') is not None:
        elem.influence_strength = e.get("strength")
    doc = e.find('documentation')
    if doc is not None:
        elem.desc = e.text
    for p in e.findall('property'):
        elem.prop(p.get('key'), p.get('value'))


def _process_folder_element(e: Any, model: Any, xsi: str, merge_flg: bool, folder: str) -> None:
    type_e = e.get(xsi + 'type').split(':')[1]
    if 'Relationship' in type_e or 'ArchimateDiagramModel' in type_e:
        return
    if merge_flg and e.get('id') in model.elems_dict:
        elem = model.elems_dict[e.get('id')]
    else:
        elem = model.add(concept_type=type_e, name=e.get('name'), uuid=e.get('id'),
                         profile=e.get('profiles'))
    elem.folder = folder
    doc = e.find('documentation')
    if doc is not None:
        elem.desc = doc.text
    for p in e.findall('property'):
        elem.prop(p.get('key'), p.get('value'))
    if type_e == 'Junction':
        elem.junction_type = e.get('type') if e.get('type') is not None else 'and'


def get_folders_elem(tag: Any, model: Any, xsi: str, merge_flg: bool, folder_path: str = '') -> None:
    folder = folder_path + '/' + tag.get('name')
    for e in tag.findall('element'):
        _process_folder_element(e, model, xsi, merge_flg, folder)
    for f in tag.findall('folder'):
        get_folders_elem(f, model, xsi, merge_flg, folder)


def get_folders_rel(tag: Any, model: Any, xsi: str, merge_flg: bool, folder_path: str = '') -> None:
    folder = folder_path + '/' + tag.get('name')
    for e in tag.findall('element'):
        type_e = e.get(xsi + 'type').split(':')[1]
        if 'Relationship' not in type_e:
            continue
        type_e = type_e[:-len("Relationship")]
        endpoints = _resolve_rel_endpoints(e, model)
        if endpoints is None:
            continue
        src, dst = endpoints
        if merge_flg and e.get('id') in model.rels_dict:
            elem = model.rels_dict(e.get('id'))
        else:
            elem = model.add_relationship(rel_type=type_e, name=e.get('name'), uuid=e.get('id'),
                                          source=src, target=dst, profile=e.get('profiles'))
        if elem is None:
            log.warning(f'Invalid {src.uuid} or {dst.uuid}')
            continue
        elem.folder = folder
        _parse_rel_attributes(elem, e)
    for f in tag.findall('folder'):
        get_folders_rel(f, model, xsi, merge_flg, folder)


def get_folders_view(tag: Any, model: Any, xsi: str, folder_path: str = '') -> None:
    folder = folder_path + '/' + tag.get('name')
    for e in tag.findall('element'):
        type_e = e.get(xsi + 'type').split(':')[1]
        if 'ArchimateDiagramModel' not in type_e:
            continue
        elem = model.add(concept_type=ArchiType.View, name=e.get('name'), uuid=e.get('id'))
        elem.folder = folder
        doc = e.find('documentation')
        if doc is not None:
            elem.desc = e.text
        for p in e.findall('property'):
            elem.prop(p.get('key'), p.get('value'))
        get_node(e, elem, xsi)
        get_connection(e, elem)
    for f in tag.findall('folder'):
        get_folders_view(f, model, xsi, folder_path)
