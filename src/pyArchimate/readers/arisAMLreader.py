"""
*   Conversion program from ARIS AML xml file to Archimate Open Exchange File format
*   Author: X. Mayeur
*   Date: October 2022
*   Version 0.9
*
*
"""
import ctypes
import platform
from .. import *


def get_text_size(text, points, font):
    """
    Get the size of a text, based on the font type & size
    :param text:    text
    :param points:  font size
    :param font:    font name

    """
    if platform.system() == 'Linux':
        from PIL import ImageFont
        font = ImageFont.truetype('DejaVuSans.ttf', points)
        size = font.getsize(text)
        return size[0], size[1]

    else:
        class SIZE(ctypes.Structure):
            """ """
            _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

        hdc = ctypes.windll.user32.GetDC(0)
        hfont = ctypes.windll.gdi32.CreateFontA(points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, font)
        hfont_old = ctypes.windll.gdi32.SelectObject(hdc, hfont)

        size = SIZE(0, 0)
        ctypes.windll.gdi32.GetTextExtentPoint32A(hdc, text, len(text), ctypes.byref(size))

        ctypes.windll.gdi32.SelectObject(hdc, hfont_old)
        ctypes.windll.gdi32.DeleteObject(hfont)

        return size.cx, size.cy


def _id_of(_id):
    """
    Return an Archimate Identifier
    :param _id: original identifier
    :returns: identifier starting with 'id-'
    """
    return 'id-' + _id.split('.')[1]



def aris_reader(model: Model, root, reader=None, scale_x=0.3, scale_y=0.3, no_view=False):
    """
    Class to perform the parsing of ARIS AML data and to generate an Archimate q

    :param model:       Model to read in
    :type model:        Model
    :param root:        XML data in Aris Markup Language
    :type root:         str
    :param scale_x:     X-Scaling factor in converting views
    :type scale_x:      float
    :param scale_y:     X-Scaling factor in converting views
    :type scale_y:      float
    :param no_view:     if true do not generate views
    """

    def _parse_elements(group=None, folder=''):
        """

        :param group:  (Default value = None)
        :param folder:  (Default value = '')

        """
        if group is None:
            group = root

        for g in group.findall('Group'):
            a = g.find('AttrDef')

            # Get group name and build organization folder
            old_folder = folder
            if a is not None:
                for n in a.iter('PlainText'):
                    folder += '/' + n.get('TextValue')
                    # print (folder)

            # Get Element (ObjDef)
            objs = g.findall('ObjDef')
            for o in objs:
                if 'SymbolNum' not in o.attrib:
                    continue
                o_type = ARIS_type_map[o.attrib['SymbolNum']]
                if o_type == '':
                    continue
                o_id = o.attrib['ObjDef.ID']
                # Extract GUID
                guid = o.find('GUID').text
                o_uuid = _id_of(guid)
                # Extract Element properties
                attrs = o.findall('AttrDef')
                props = {}
                o_name = None
                o_desc = None
                for attr in attrs:
                    key = attr.attrib['AttrDef.Type']
                    val = ''
                    for v in attr.iter('PlainText'):
                        val += v.get('TextValue') + '\n'
                    if key == 'AT_NAME':
                        o_name = val
                    elif key == 'AT_DESC':
                        o_desc = val
                    else:
                        props[key] = val
                props['GUID'] = guid
                elem = model.add(concept_type=o_type, name=o_name, desc=o_desc, uuid=o_uuid, folder=folder)
                for k,v in props.items():
                    elem.prop(k, v)

            _parse_elements(g, folder)
            folder = old_folder

    def _parse_relationships(groups=None):
        """

        :param groups:  (Default value = None)

        """
        if groups is None:
            groups = root

        # Relationships (CnxDef) are defined to relate ObjDef elements together
        # However, we needed to parse first all elements in order to detect relationships with
        # target to elements not defined in this Aris model. Those relationship will be skipped
        # We also do not classify relationships in folder. there is no real reason for that

        for g in groups.findall('Group'):
            # find again the objects
            objs = g.findall('ObjDef')
            for o in objs:
                # and their identifier
                o_id = o.attrib['ObjDef.ID']
                o_uuid = _id_of(o_id)
                # Get the relationships
                rels = o.findall('CxnDef')
                for rel in rels:
                    r_type = ARIS_type_map[rel.attrib['CxnDef.Type']]
                    r_id = _id_of(rel.attrib['CxnDef.ID'])
                    # Check if the target is a known element
                    r_target = _id_of(rel.attrib.get('ToObjDef.IdRef'))
                    if r_target in model.elems_dict:
                        # Extract relationship properties, that will be globally handled  at the end of the
                        # conversion process, before returning the model
                        attrs = rel.findall('AttrDef')
                        props = {}
                        for attr in attrs:
                            key = attr.attrib['AttrDef.Type']
                            val = ''
                            for v in attr.iter('PlainText'):
                                val += v.get('TextValue') + '\n'
                            props[key] = val

                        try:
                            r = model.add_relationship(
                                rel_type=r_type, source=o_uuid, target=r_target, uuid=r_id
                            )
                        except ArchimateRelationshipError as exc:
                            r_type = get_default_rel_type(model.elems_dict[o_uuid].type,
                                                          model.elems_dict[r_target].type)
                            log.warning(str(exc) + f' - Replacing by {r_type}')
                            r = model.add_relationship(
                                rel_type=r_type, source=o_uuid, target=r_target, uuid=r_id
                            )
                        if r is not None:
                            for key, value in props.items():
                                r.prop(key, value)

            _parse_relationships(g)

        return

    def _parse_nodes(grp=None, view=None):
        """

        :param grp:  (Default value = None)
        :param view:  (Default value = None)

        """
        if grp is None:
            return

        if view is None:
            return

        if not isinstance(view, View):
            raise ArchimateConceptTypeError("'view' is not an instance of class 'View'")

        for o in grp.findall('ObjOcc'):

            o_type = ARIS_type_map[o.attrib['SymbolNum']]
            o_id = _id_of(o.attrib['ObjOcc.ID'])
            o_elem_ref = model.elems_dict[_id_of(o.attrib['ObjDef.IdRef'])].uuid

            pos = o.find('Position')
            size = o.find('Size')
            n = view.add(
                ref=o_elem_ref,
                x=int(pos.get('Pos.X')) * scale_x,
                y=int(pos.get('Pos.Y')) * scale_y,
                w=int(size.get('Size.dX')) * scale_x,
                h=int(size.get('Size.dY')) * scale_y,
                uuid=o_id
            )

            if o_type == 'Grouping':
                n.fill_color = "#FFFFFF"
                n.opacity = 100
        _parse_nodes(grp)

    def _parse_connections(grp=None, view=None):
        """

        :param grp:  (Default value = None)
        :param view:  (Default value = None)

        """
        if grp is None:
            return

        if view is None:
            return

        if not isinstance(view, View):
            raise ValueError("'view' is not an instance of class 'View'")

        for o in grp.findall('ObjOcc'):
            o_id = _id_of(o.attrib['ObjOcc.ID'])
            for conn in o.findall('CxnOcc'):
                c_id = _id_of(conn.attrib['CxnOcc.ID'])
                c_rel_id = _id_of(conn.attrib['CxnDef.IdRef'])
                c_target = _id_of(conn.get('ToObjOcc.IdRef'))

                if 'Embedding' in conn.attrib and conn.attrib['Embedding'] == 'YES':
                    # Aris uses (sometime) reversed relationship when embedding objects,
                    # This gives validation errors when importing into archi...
                    # Swap therefore source and target if needed
                    try:
                        # rel = model.rels_dict[c_rel_id]
                        # x = rel.target
                        # check if the relationship target is the related data of the visual object and swap
                        nt = model.nodes_dict[c_target]
                        ns = model.nodes_dict[o_id]
                        # Embed the node
                        if not (
                                nt.x >= ns.x and nt.y >= ns.y
                                and nt.x + nt.w <= ns.x + ns.w and nt.y + nt.h <= ns.y + ns.h
                        ):
                            #     log.warning(f"Inverting embedded nodes relationship '{rel.type}' ")
                            #     #             f"between nodes '{rel.source.name}' and '{rel.target.name}'")
                            #     rel.target = rel.source
                            #     rel.source = x
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
                        log.error(f'Orphan Connection with unrelated relationship {c_rel_id} ')
                elif c_rel_id in model.rels_dict:
                    c = view.add_connection(ref=c_rel_id, source=o_id, target=c_target, uuid=c_id)
                    bps = conn.findall('Position')
                    for i in range(1, len(bps) - 1):
                        pos = bps[i]
                        bp_x = int(pos.get('Pos.X'))
                        bp_y = int(pos.get('Pos.Y'))
                        c.add_bendpoint(Point(bp_x * scale_x, bp_y * scale_y))

    def _parse_containers(grp=None, view=None):
        """

        :param grp:  (Default value = None)
        :param view:  (Default value = None)

        """
        if grp is None:
            return
        if view is None:
            return

        if not isinstance(view, View):
            raise ArchimateConceptTypeError("'view' is not an instance of class 'View'")

        for objs in grp.findall('GfxObj'):
            for o in objs.findall('RoundedRectangle'):
                pos = o.find('Position')
                size = o.find('Size')
                brush = o.find('Brush')
                if brush is not None:
                    color_str = brush.get('Color')
                else:
                    color_str = "#000000"
                if pos is not None and size is not None:
                    n = view.add(ref=None,
                                 x=scale_x * int(pos.get('Pos.X')),
                                 y=scale_y * int(pos.get('Pos.Y')),
                                 w=scale_x * int(size.get('Size.dX')),
                                 h=scale_y * int(size.get('Size.dY')),
                                 node_type='Container'
                                 )
                    n.line_color = f'#{int(color_str):0>6X}'
                    n.fill_color = "#FFFFFF"
                    n.opacity = 100

    def _parse_labels():
        """ """
        for o in root.findall('FFTextDef'):
            o_id = _id_of(o.attrib['FFTextDef.ID'])
            if o.attrib['IsModelAttr'] == 'TEXT':
                attrs = o.findall('AttrDef')
                o_name = None
                for attr in attrs:
                    key = attr.attrib['AttrDef.Type']
                    val = ''
                    for v in attr.iter('PlainText'):
                        val += v.get('TextValue') + '\n'
                    if key == 'AT_NAME':
                        o_name = val

                model.labels_dict[o_id] = o_name

    def _parse_labels_in_view(grp=None, view=None):
        """

        :param grp:  (Default value = None)
        :param view:  (Default value = None)

        """
        if grp is None:
            return
        if view is None:
            return
        if not isinstance(view, View):
            raise ArchimateConceptTypeError("'view' is not an instance of class 'View'")

        for objs in grp.findall('FFTextOcc'):
            lbl_ref = _id_of(objs.attrib['FFTextDef.IdRef'])
            if lbl_ref in model.labels_dict:
                # Extract Element properties
                o_name = model.labels_dict[lbl_ref]
                # calculate size in function of text
                o = objs.find('Position')
                if o is not None:
                    pos = o.attrib
                    # size = objs.find('Size').attrib
                    w, h = max([get_text_size(x, 9, "Segoe UI") for x in o_name.split('\n')])
                    try:
                        n = view.add(
                            ref=lbl_ref,
                            x=max(int(pos.get('Pos.X')) * scale_x, 0),
                            y=max(int(pos.get('Pos.Y')) * scale_y, 0),
                            w=w + 18,  # 13 * len(max(o_name.split('\n'))),
                            h=30 + (h * 1.5) * (o_name.count('\n') + 1),
                            node_type='Label', label=o_name
                        )
                        n.fill_color = "#FFFFFF"
                        n.opacity = 100
                        n.line_color = '#000000'
                        n.border_type = "2"
                        n.text_alignment = TextAlignment.Left
                    except ValueError:
                        log.warning(f'Node {o_name} has unknown element reference {lbl_ref}'
                                    f' - ignoring')
                        continue
        return

    def _parse_views(group=None, folder=''):
        """

        :param group:  (Default value = None)
        :param folder:  (Default value = '')

        """
        if group is None:
            group = root

        for g in group.findall('Group'):
            a = g.find('AttrDef')
            # Get group name and build organization folder
            old_folder = folder
            if a is not None:
                for n in a.iter('PlainText'):
                    folder += '/' + n.get('TextValue')
                    # print (folder)

            # In ARIS, a Model is actually a View
            objs = g.findall('Model')
            for o in objs:
                view_id = _id_of(o.attrib['Model.ID'])
                attrs = o.findall('AttrDef')
                props = {}
                o_name = None
                o_desc = None
                for attr in attrs:
                    key = attr.attrib['AttrDef.Type']
                    val = ''
                    for v in attr.iter('PlainText'):
                        val += v.get('TextValue') + '\n'
                    if key == 'AT_NAME':
                        o_name = val
                    elif key == 'AT_DESC':
                        o_desc = val
                    else:
                        props[key] = val

                # model.name = view_name
                view = model.add(concept_type=ArchiType.View,
                                 name=o_name, uuid=view_id, desc=o_desc)
                log.info('Parsing & adding nodes')
                view.folder = folder
                _parse_nodes(o, view)

                log.info('Parsing & adding conns')
                _parse_connections(o, view)
                log.info('Parsing and adding container groups')
                _parse_containers(o, view)
                log.info('Parsing and adding labels')
                _parse_labels_in_view(o, view)

            _parse_views(g, folder)
            folder = old_folder

    def _clean_nested_conns():
        """ """
        # Clean now all connections between a node and its embedding node parent
        nested_conns = [x for x in model.conns_dict.values()
                        if x.source.uuid == x.parent.uuid and isinstance(x.parent, Node)]
        for c in nested_conns:
            c.delete()
        nested_conns = [x for x in model.conns_dict.values() if
                        x.target.uuid == x.parent.uuid and isinstance(x.parent, Node)]
        for c in nested_conns:
            c.delete()

    def convert():
        """ """

        log.info('Parsing elements')
        _parse_elements()
        log.info('Parsing relationships')
        _parse_relationships()

        if not no_view:
            log.info('Parsing Labels')
            _parse_labels()
            log.info('Parsing Views')
            _parse_views()
            _clean_nested_conns()

        model.expand_props(clean_doc=True)
        log.info('Performing final model validation checks')
        inv_c = model.check_invalid_conn()
        inv_n = model.check_invalid_nodes()
        if len(inv_n) > 0 or len(inv_c) > 0:
            log.error("Errors found in the model")
            print(inv_n)
            print(inv_c)

        return model

    if root.tag != 'AML':
        log.fatal(' Input file is not an ARIS AML file - Aborting')
        sys.exit(1)

    scale_x = float(scale_x)
    scale_y = float(scale_y)
    no_view = no_view
    convert()
