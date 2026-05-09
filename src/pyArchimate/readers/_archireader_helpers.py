"""Private helpers extracted from archiReader to reduce cognitive complexity (S3776)."""
from typing import Any

try:
    from ..enums import AccessType, ArchiType
    from ..helpers.logging import log
    from ..helpers.parsing import parse_bool
    from ..view import Node, Point, View
except ImportError:
    import sys
    sys.path.insert(0, "..")
    from pyArchimate import (  # type: ignore[no-redef,attr-defined]
        AccessType,
        ArchiType,
        Node,
        Point,
        View,
        log,
        parse_bool,
    )


def _handle_diagram_object(parent: Any, child: Any) -> Any:
    node = parent.add(ref=child.get('archimateElement'), uuid=child.get('id'))
    if node is not None:
        try:
            if node.concept.prop('label') is not None:
                node.label_expression = str(node.concept.prop('label'))
        except Exception as e:
            log.debug(f"Failed to set label expression for node {getattr(node, 'uuid', None)}: {e}")
    return node


def _parse_node_type(parent: Any, child: Any, xsi: str) -> Any:
    type_n = child.get(xsi + 'type').split(':')[1]
    if type_n == 'DiagramObject':
        node = _handle_diagram_object(parent, child)
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


def _parse_node_style_attrs(node: Any, child: Any) -> None:
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
    if child.get('imagePath') is not None:
        node.image_path = child.get('imagePath')
    if child.get('imagePosition') is not None:
        node.image_position = int(child.get('imagePosition'))
    if child.get('type') is not None:
        node.image_type = int(child.get('type'))


def _parse_node_features(node: Any, child: Any) -> None:
    for ft in child.findall('feature'):
        ft_name = ft.get('name')
        if ft_name == 'lineAlpha':
            node.lc_opacity = 100 * int(ft.get('value')) / 255
        elif ft_name == 'labelExpression':
            node.label_expression = ft.get('value')
        elif ft_name == 'iconColor':
            node.icon_color = ft.get('value')
        elif ft_name == 'gradient':
            node.gradient = ft.get('value')
        elif ft_name == 'imageSource':
            node.image_source = parse_bool(ft.get('value'))


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
    _parse_node_style_attrs(node, child)
    _parse_node_features(node, child)
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
    # In Archi's format startX/startY are offsets from the SOURCE centre;
    # endX/endY are offsets from the TARGET centre.  Both encode the same
    # physical point for round-trip stability when nodes move.
    # When an attribute is absent the implied offset is 0, i.e. the bendpoint
    # sits at the node centre on that axis.
    # Priority: endX/endY take precedence over startX/startY when both present.
    has_start_x = bp.get('startX') is not None
    has_start_y = bp.get('startY') is not None
    has_end_x   = bp.get('endX') is not None
    has_end_y   = bp.get('endY') is not None

    if has_end_x:
        x = int(bp.get('endX')) + target_node.cx
    elif has_start_x:
        x = int(bp.get('startX')) + source_node.cx
    else:
        x = int(source_node.cx)  # offset = 0 → at source centre

    if has_end_y:
        y = int(bp.get('endY')) + target_node.cy
    elif has_start_y:
        y = int(bp.get('startY')) + source_node.cy
    else:
        y = int(source_node.cy)  # offset = 0 → at source centre
    return x, y


def _parse_connection(sc: Any, parent: View) -> None:
    ref = sc.get('archimateRelationship')
    if ref not in parent.model.rels_dict:
        log.debug(f'Unknown connection ref {ref}')
        return
    try:
        conn = parent.add_connection(ref=ref, source=sc.get('source'),
                                     target=sc.get('target'), uuid=sc.get('id'))
    except (ValueError, KeyError) as exc:
        log.warning(f'Skipping connection {sc.get("id")}: {exc}')
        return
    if sc.get('fontColor') is not None:
        conn.font_color = sc.get('fontColor')
    if sc.get('lineColor') is not None:
        conn.line_color = sc.get('lineColor')
    if sc.get('lineWidth') is not None:
        conn.line_width = int(sc.get('lineWidth'))
    conn.text_position = sc.get('textPosition')
    source_id = sc.get('source')
    target_id = sc.get('target')
    source_node = (parent.model.nodes_dict.get(source_id)
                   or parent.model.conns_dict.get(source_id))
    target_node = (parent.model.nodes_dict.get(target_id)
                   or parent.model.conns_dict.get(target_id))
    ft = sc.find('feature')
    if ft is not None and ft.get('name') == 'nameVisible':
        conn.show_label = parse_bool(ft.get('value'))
    if source_node and target_node:
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
        return None  # Will retry in next pass
    src = model.elems_dict[src_id] if src_id in model.elems_dict else model.rels_dict[src_id]
    dst = model.elems_dict[dst_id] if dst_id in model.elems_dict else model.rels_dict[dst_id]
    return src, dst


def _parse_rel_attributes(elem: Any, e: Any) -> None:
    at = e.get('accessType')
    if at is not None:
        if at == "1":
            elem.access_type = AccessType.Read
        elif at == "3":
            elem.access_type = AccessType.ReadWrite
        else:
            elem.access_type = AccessType.Access
    else:
        elem.access_type = AccessType.Write
    if e.get('directed') is not None:
        elem.is_directed = e.get('directed') == "true"
    if e.get('influenceStrength') is not None:
        elem.influence_strength = e.get("influenceStrength")
    elif e.get('modifier') is not None:
        elem.influence_strength = e.get("modifier")
    elif e.get('strength') is not None:
        elem.influence_strength = e.get("strength")
    doc = e.find('documentation')
    if doc is not None:
        elem.desc = doc.text
    for p in e.findall('property'):
        elem.prop(p.get('key'), p.get('value'))


def _process_viewpoint_property(elem: Any, slug: str) -> None:
    """Assign viewpoint to element if it exists in registry, log warning if not found."""
    from ..viewpoint_registry import (
        get_viewpoint,  # noqa: PLC0415  # deferred: avoids circular import at reader load time
    )
    if get_viewpoint(slug) is not None:
        elem.assign_viewpoint(slug)
    else:
        log.warning(f"Unknown viewpoint slug '{slug}' ignored during import")


def _process_property(elem: Any, prop: Any) -> None:
    """Process element property, handling viewpoint assignment or visual style restoration."""
    key = prop.get('key')
    if key == 'viewpoint':
        slug = (prop.get('value') or '').strip().lower()
        if slug:
            _process_viewpoint_property(elem, slug)
    elif key == 'junctionType':
        # Restore junction type from property (overrides any type extracted from xsi:type)
        value = prop.get('value')
        if value in ('and', 'or', 'xor'):
            elem.junction_type = value
    elif key in ('fillColor', 'lineColor', 'lineWidth', 'transparency'):
        # Restore visual style properties to the element's _visual_style dict
        value = prop.get('value')
        # Convert to appropriate type
        if key in ('lineWidth', 'transparency'):
            value = float(value)
        elem._visual_style[key] = value
    else:
        elem.prop(key, prop.get('value'))


def _get_or_create_element(e: Any, model: Any, merge_flg: bool, type_e: str) -> Any:
    """Get existing element if merge flag is set and element exists, otherwise create new element."""
    elem_id = e.get('id')
    if merge_flg and elem_id in model.elems_dict:
        return model.elems_dict[elem_id]
    return model.add(concept_type=type_e, name=e.get('name'), uuid=elem_id,
                     profile=e.get('profiles'))


def _set_documentation(elem: Any, e: Any) -> None:
    """Extract documentation text from XML element and assign to element description."""
    doc = e.find('documentation')
    if doc is not None:
        elem.desc = doc.text


def _set_junction_type(elem: Any, xsi_type: str) -> None:
    """Set junction type from xsi:type attribute for backward compatibility.

    Handles old format: xsi:type like 'AndJunction' -> 'and', 'OrJunction' -> 'or'
    For new format, the junctionType property will override this.
    Only sets junction type if xsi:type is not just 'Junction' (which means it was not set).
    """
    if xsi_type != 'Junction' and xsi_type.endswith('Junction'):
        junction_name = xsi_type[:-len('Junction')].lower()
        if junction_name in ('and', 'or', 'xor'):
            elem.junction_type = junction_name


def _process_folder_element(e: Any, model: Any, xsi: str, merge_flg: bool, folder: str) -> None:
    type_e = e.get(xsi + 'type').split(':')[1]
    if 'Relationship' in type_e or 'ArchimateDiagramModel' in type_e:
        return
    elem = _get_or_create_element(e, model, merge_flg, type_e)
    elem.folder = folder
    # Restore parent-child hierarchy from parentId attribute
    parent_id = e.get('parentId')
    if parent_id:
        elem._parent_uuid = parent_id
    # For backward compatibility: set default junction type from xsi:type or type attribute
    if 'Junction' in type_e:
        _set_junction_type(elem, type_e)
        # Also check for legacy type attribute (e.g., type="or")
        legacy_type = e.get('type')
        if legacy_type and legacy_type in ('and', 'or', 'xor'):
            elem.junction_type = legacy_type
    _set_documentation(elem, e)
    for p in e.findall('property'):
        _process_property(elem, p)


def get_folders_elem(tag: Any, model: Any, xsi: str, merge_flg: bool, folder_path: str = '') -> None:
    folder = folder_path + '/' + tag.get('name')
    for e in tag.findall('element'):
        _process_folder_element(e, model, xsi, merge_flg, folder)
    for f in tag.findall('folder'):
        get_folders_elem(f, model, xsi, merge_flg, folder)


def _add_resolved_rel(e: Any, type_e: str, folder: str, model: Any, merge_flg: bool, src: Any, dst: Any) -> None:
    if merge_flg and e.get('id') in model.rels_dict:
        elem = model.rels_dict[e.get('id')]
    else:
        elem = model.add_relationship(rel_type=type_e, name=e.get('name'), uuid=e.get('id'),
                                      source=src, target=dst, profile=e.get('profiles'))
    elem.folder = folder
    _parse_rel_attributes(elem, e)


def _retry_unresolved_rels(unresolved: list[Any], model: Any, merge_flg: bool) -> None:
    max_retries = len(unresolved) + 1
    still_unresolved: list[Any] = []
    for _retry_count in range(max_retries):
        still_unresolved = []
        for e, type_e, folder in unresolved:
            endpoints = _resolve_rel_endpoints(e, model)
            if endpoints is not None:
                src, dst = endpoints
                _add_resolved_rel(e, type_e, folder, model, merge_flg, src, dst)
            else:
                still_unresolved.append((e, type_e, folder))
        if not still_unresolved:
            break
        unresolved = still_unresolved
    for e, _type_e, _folder in still_unresolved:
        log.debug(f"Unable to resolve relationship {e.get('id')}: endpoints not found")


def get_folders_rel(tag: Any, model: Any, xsi: str, merge_flg: bool, folder_path: str = '', unresolved: list[Any] | None = None) -> None:
    if unresolved is None:
        unresolved = []
    folder = folder_path + '/' + tag.get('name')
    for e in tag.findall('element'):
        type_e = e.get(xsi + 'type').split(':')[1]
        if 'Relationship' not in type_e:
            continue
        type_e = type_e[:-len("Relationship")]
        endpoints = _resolve_rel_endpoints(e, model)
        if endpoints is None:
            unresolved.append((e, type_e, folder))
            continue
        src, dst = endpoints
        _add_resolved_rel(e, type_e, folder, model, merge_flg, src, dst)
    for f in tag.findall('folder'):
        get_folders_rel(f, model, xsi, merge_flg, folder, unresolved)
    if folder_path == '':
        _retry_unresolved_rels(unresolved, model, merge_flg)


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
            elem.desc = doc.text
        for p in e.findall('property'):
            elem.prop(p.get('key'), p.get('value'))
        # Read view-level primary viewpoint from 'viewpoint' XML attribute
        vp_attr = (e.get('viewpoint') or '').strip().lower()
        if vp_attr:
            from ..viewpoint_registry import (
                get_viewpoint,  # noqa: PLC0415  # deferred: avoids circular import at reader load time
            )
            if get_viewpoint(vp_attr) is not None:
                elem.set_primary_viewpoint(vp_attr)
            else:
                log.warning(f"Unknown viewpoint slug '{vp_attr}' on view ignored")
        get_node(e, elem, xsi)
        get_connection(e, elem)
    for f in tag.findall('folder'):
        get_folders_view(f, model, xsi, folder_path)
