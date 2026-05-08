# ruff: noqa: N999  # legacy module name preserved for API compatibility
import os
import re
import sys
from typing import Any, Optional

try:
    from ..constants import NAMED_COLORS, RGBA
    from ..enums import ArchiType
    from ..helpers.logging import log
    from ..view import Point
except ImportError:
    sys.path.insert(0, "..")
    from constants import NAMED_COLORS  # type: ignore[import-not-found,no-redef]

    from pyArchimate import RGBA, ArchiType, Point, log  # type: ignore[attr-defined,no-redef]

__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def _normalize_color_on_import(color_str: Optional[str]) -> Optional[str]:
    """
    Normalize color from import to hex format.
    Accepts hex (#RRGGBB) or named colors.
    Returns lowercase hex or None on error.
    """
    if not color_str or not isinstance(color_str, str):
        return None
    color_str = color_str.strip().lower()
    if not color_str:
        return None
    if color_str.startswith('#'):
        if re.match(r'^#[0-9a-f]{6}$', color_str):
            return color_str
        log.warning(f"Invalid hex color format on import: {color_str}")
        return None
    if color_str in NAMED_COLORS:
        return NAMED_COLORS[color_str].lower()
    log.warning(f"Unknown color on import: {color_str}")
    return None


def _parse_style_property_value(key: str, val: str) -> Any:
    """Parse a single visual style property value; returns parsed value or None on failure."""
    try:
        if key in ('fillColor', 'lineColor'):
            return _normalize_color_on_import(val) or None
        if key == 'lineWidth':
            width_val = float(val)
            if width_val >= 0:
                return width_val
            log.warning(f"Invalid lineWidth on import (negative): {val}")
        elif key == 'transparency':
            alpha_val = float(val)
            if 0.0 <= alpha_val <= 1.0:
                return alpha_val
            log.warning(f"Invalid transparency on import (out of range): {val}")
    except (ValueError, TypeError) as e:
        log.warning(f"Failed to parse visual style property {key}={val}: {e}")
    return None


def _extract_visual_style_properties(elem_xml: Any, ns: str) -> dict[str, Any]:
    """Extract visual style properties (fillColor, lineColor, lineWidth, transparency) from element."""
    style: dict[str, Any] = {}
    props_xml = elem_xml.find(ns + 'properties')
    if props_xml is None:
        return style
    for p in props_xml.findall(ns + 'property'):
        key = p.get('key')
        val_elem = p.find(ns + 'value')
        if val_elem is None:
            continue
        val = (val_elem.text or '').strip()
        if not val:
            continue
        parsed = _parse_style_property_value(key, val)
        if parsed is not None:
            style[key] = parsed
    return style


def _build_hierarchy_from_parents(model: Any, parent_map: dict[str, Optional[str]]) -> None:
    """
    Build parent-child hierarchy after all elements are loaded.
    parent_map: dict of {child_uuid: parent_uuid}
    Validates hierarchy with cycle detection and depth limits.
    On error: Log warning, skip relationship, continue (lenient).
    """
    if not parent_map:
        return
    for child_uuid, parent_uuid in parent_map.items():
        if parent_uuid is None or child_uuid not in model.elems_dict:
            continue
        if parent_uuid not in model.elems_dict:
            log.warning(f"Parent element {parent_uuid} not found during import, skipping hierarchy")
            continue
        try:
            model.add_child(parent_uuid, child_uuid)
        except (KeyError, ValueError) as e:
            log.warning(f"Failed to add hierarchy during import: {e}, skipping relationship")


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


def _read_props(obj: Any, xml_elem: Any, ns: str, pdef_merge_map: dict[str, str], model: Any) -> None:
    props = xml_elem.find(ns + 'properties')
    if props is None:
        return
    for p in props.findall(ns + 'property'):
        # Skip visual style properties (fillColor, lineColor, lineWidth, transparency)
        # which have 'key' but not 'propertyDefinitionRef'
        if p.get('propertyDefinitionRef') is None:
            if p.get('key') in ('fillColor', 'lineColor', 'lineWidth', 'transparency'):
                continue
            # Unknown property format, skip it
            continue
        _id = pdef_merge_map[p.get('propertyDefinitionRef')]
        obj.prop(model.pdefs[_id], p.find(ns + 'value').text)


def _assign_viewpoint(obj: Any, slug: str, method: str = 'assign_viewpoint') -> None:
    from ..viewpoint_registry import (
        get_viewpoint,  # noqa: PLC0415  # deferred: avoids circular import at reader load time
    )
    if not slug:
        return
    if get_viewpoint(slug) is not None:
        getattr(obj, method)(slug)
    else:
        log.warning(f"Unknown viewpoint slug '{slug}' ignored during import")


def _apply_viewpoint_props(elem: Any, props_xml: Any, ns: str, pdef_merge_map: dict[str, str], model: Any) -> None:
    if props_xml is None:
        return
    for p in props_xml.findall(ns + 'property'):
        prop_id = p.get('propertyDefinitionRef')
        if prop_id not in pdef_merge_map:
            continue
        if model.pdefs.get(pdef_merge_map[prop_id]) != 'viewpoint':
            continue
        val_xml = p.find(ns + 'value')
        slug = (val_xml.text or '').strip().lower() if val_xml is not None else ''
        _assign_viewpoint(elem, slug)


def _apply_junction_type_props(elem: Any, props_xml: Any, ns: str) -> None:
    if props_xml is None:
        return
    for p in props_xml.findall(ns + 'property'):
        if p.get('key') == 'junctionType':
            val_elem = p.find(ns + 'value')
            if val_elem is not None:
                junction_type = (val_elem.text or '').strip().lower()
                if junction_type:
                    try:
                        elem.set_junction_type(junction_type)
                    except ValueError as e:
                        log.warning(f"Invalid junctionType on import: {e}")


def _read_elements(model, root, ns, xsi, pdef_merge_map, merge_flg):
    elements_xml = root.find(ns + 'elements')
    if elements_xml is None:
        return {}, {}
    parent_map = {}
    visual_style_map = {}
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
        parent_id = e.get('parentId')
        if parent_id:
            parent_map[_uuid] = parent_id
        visual_style = _extract_visual_style_properties(e, ns)
        if visual_style:
            visual_style_map[_uuid] = visual_style

        props_xml = e.find(ns + 'properties')
        _apply_viewpoint_props(elem, props_xml, ns, pdef_merge_map, model)
        _apply_junction_type_props(elem, props_xml, ns)

    return parent_map, visual_style_map


def _process_one_relationship(model, r, ns, xsi, pdef_merge_map, merge_flg):
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
            influence_strength=r.get('influenceStrength') or r.get('modifier'),
        )
        if r.get('isDirected') == 'true':
            rel.is_directed = True
        _read_props(rel, r, ns, pdef_merge_map, model)


def _read_relationships(model, root, ns, xsi, pdef_merge_map, merge_flg):
    rels_xml = root.find(ns + 'relationships')
    if rels_xml is None:
        return
    # Multi-pass to handle forward references (relationship targeting another relationship
    # defined later in the XML — valid ArchiMate but breaks single-pass ordering).
    remaining = list(rels_xml.findall(ns + 'relationship'))
    while remaining:
        deferred = []
        for r in remaining:
            try:
                _process_one_relationship(model, r, ns, xsi, pdef_merge_map, merge_flg)
            except ValueError:
                deferred.append(r)
        if len(deferred) == len(remaining):
            # No progress — genuine unresolvable references; surface the first error.
            _process_one_relationship(model, deferred[0], ns, xsi, pdef_merge_map, merge_flg)
        remaining = deferred


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


def _get_xml_text(elem, tag, ns):
    found = elem.find(ns + tag)
    return None if found is None else found.text


def _read_view_connection(view, c, ns, merge_flg):
    # Skip view-only lines (xsi:type="Line") — no backing model relationship.
    if c.get('relationshipRef') is None:
        return
    _uuid_c = None if merge_flg else c.get('identifier')
    _c = view.add_connection(
        ref=c.get('relationshipRef'),
        source=c.get('source'),
        target=c.get('target'),
        uuid=_uuid_c,
    )
    _apply_conn_style(_c, c.find(ns + 'style'), ns)
    for bp in c.findall(ns + 'bendpoint'):
        _c.add_bendpoint(Point(bp.get('x'), bp.get('y')))


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
            name=_get_xml_text(v, 'name', ns),
            uuid=_uuid,
            desc=_get_xml_text(v, 'documentation', ns),
        )
        _read_props(_v, v, ns, pdef_merge_map, model)
        _assign_viewpoint(_v, (v.get('viewpoint') or '').strip().lower(), 'set_primary_viewpoint')
        for n in v.findall(ns + 'node'):
            _add_node(_v, n, ns, xsi, model, merge_flg)
        for c in v.findall(ns + 'connection'):
            _read_view_connection(_v, c, ns, merge_flg)


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


def _apply_visual_styles(model: Any, visual_style_map: dict[str, Any]) -> None:
    _setters = {
        'fillColor': 'set_fill_color',
        'lineColor': 'set_line_color',
        'lineWidth': 'set_line_width',
        'transparency': 'set_transparency',
    }
    for elem_uuid, style in visual_style_map.items():
        if elem_uuid not in model.elems_dict:
            continue
        elem = model.elems_dict[elem_uuid]
        for key, setter_name in _setters.items():
            if key in style:
                try:
                    getattr(elem, setter_name)(style[key])
                except (ValueError, TypeError) as e:
                    log.warning(f"Failed to apply {key} to {elem_uuid}: {e}")


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
    parent_map, visual_style_map = _read_elements(model, root, ns, xsi, pdef_merge_map, merge_flg)
    _read_relationships(model, root, ns, xsi, pdef_merge_map, merge_flg)
    _read_views(model, root, ns, xsi, pdef_merge_map, merge_flg)
    _read_organizations(model, root, ns)
    _build_hierarchy_from_parents(model, parent_map)
    _apply_visual_styles(model, visual_style_map)
