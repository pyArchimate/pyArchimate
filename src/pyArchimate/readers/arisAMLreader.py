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
import xml.etree.ElementTree as ElemTree

from src.pyArchimate.logger import *
from src.pyArchimate.pyArchimate import *

log_to_stderr()
log.name = 'aml'


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


class ArisAmlWriter:
    """Class to perform the parsing of ARIS AML data and to generate an Archimate model"""

    def __init__(self, model: Model, aml_data: str, name='aris_export', scale_x=0.3, scale_y=0.3, no_view=False):
        """

        :param model:       Model to read in
        :type model:        Model
        :param aml_data:    XML data in Aris Markup Language
        :type aml_data:     str
        :param name:        Model name
        :type name:         str
        :param scale_x:     X-Scaling factor in converting views
        :type scale_x:      float
        :param scale_y:     X-Scaling factor in converting views
        :type scale_y:      float
        :param no_view:     if true do not generate views
        """
        # self.data = xmltodict.parse(open(aml_file, 'r').read())
        self.root = ElemTree.fromstring(aml_data)

        if self.root.tag != 'AML':
            log.fatal(' Input file is not an ARIS AML file - Aborting')
            sys.exit(1)
        self.organizations = []
        self.name = name
        self.model = model
        self.elements = []
        self.relationships = []
        self.scaleX = float(scale_x)
        self.scaleY = float(scale_y)
        self.no_view = no_view
        self.convert()

    def convert(self):
        """ """

        log.info('Parsing elements')
        self._parse_elements()
        log.info('Parsing relationships')
        self._parse_relationships()

        if not self.no_view:
            log.info('Parsing Labels')
            self._parse_labels()
            log.info('Parsing Views')
            self._parse_views()
            self._clean_nested_conns()

        self.model.expand_props(clean_doc=True)
        log.info('Performing final model validation checks')
        inv_c = self.model.check_invalid_conn()
        inv_n = self.model.check_invalid_nodes()
        if len(inv_n) > 0 or len(inv_c) > 0:
            log.error("Errors found in the model")
            print(inv_n)
            print(inv_c)

        return self.model

    def _parse_elements(self, group=None, folder=''):
        """

        :param group:  (Default value = None)
        :param folder:  (Default value = '')

        """
        if group is None:
            group = self.root

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
                o_type = ARIS_type_map[o.attrib['SymbolNum']]
                if o_type == '':
                    continue
                o_id = o.attrib['ObjDef.ID']
                o_uuid = _id_of(o_id)

                # Extract Element properties
                attrs = o.findall('AttrDef')
                props = {}
                o_name = None
                o_desc = None
                for attr in attrs:
                    key = attr.attrib['AttrDef.Type']
                    val = ''
                    for v in attr.iter('PlainText'):
                        val += v.get('TextValue')
                    if key == 'AT_NAME':
                        o_name = val
                    elif key == 'AT_DESC':
                        o_desc = val
                    else:
                        props[key] = val

                self.model.add(concept_type=o_type, name=o_name, desc=o_desc, uuid=o_uuid, folder=folder)

            self._parse_elements(g, folder)
            folder = old_folder

    def _parse_relationships(self, groups=None):
        """

        :param groups:  (Default value = None)

        """
        if groups is None:
            groups = self.root

        # Relationships (CnxDef) are defined with each elements ObjDef
        # However, we needed to parse first all elements in order to detect relationships with
        # target to elements not provided in this Aris model. Those relationship will be skipped
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
                    if r_target in self.model.elems_dict:
                        # Extract relationship properties, that will be globally handled  at the end of the
                        # conversion process, before returning the model
                        attrs = rel.findall('AttrDef')
                        props = {}
                        for attr in attrs:
                            key = attr.attrib['AttrDef.Type']
                            val = ''
                            for v in attr.iter('PlainText'):
                                val += v.get('TextValue')
                            props[key] = val

                        try:
                            r = self.model.add_relationship(
                                rel_type=r_type, source=o_uuid, target=r_target, uuid=r_id
                            )
                        except ArchimateRelationshipError as exc:
                            r_type = get_default_rel_type(self.model.elems_dict[o_uuid].type,
                                                          self.model.elems_dict[r_target].type)
                            log.warning(str(exc) + f' - Replacing by {r_type}')
                            r = self.model.add_relationship(
                                rel_type=r_type, source=o_uuid, target=r_target, uuid=r_id
                            )
                        if r is not None:
                            for key, value in props.items():
                                r.prop(key, value)

            self._parse_relationships(g)

        return

    def _parse_nodes(self, grp=None, view=None):
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
            o_elem_ref = self.model.elems_dict[_id_of(o.attrib['ObjDef.IdRef'])].uuid

            pos = o.find('Position')
            size = o.find('Size')
            n = view.add(
                ref=o_elem_ref,
                x=int(pos.get('Pos.X')) * self.scaleX,
                y=int(pos.get('Pos.Y')) * self.scaleY,
                w=int(size.get('Size.dX')) * self.scaleX,
                h=int(size.get('Size.dY')) * self.scaleY,
                uuid=o_id
            )

            if o_type == 'Grouping':
                n.fill_color = "#000000"
                n.opacity = 0
        self._parse_nodes(grp)

    def _parse_connections(self, grp=None, view=None):
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
                        # rel = self.model.rels_dict[c_rel_id]
                        # x = rel.target
                        # check if the relationship target is the related data of the visual object and swap
                        nt = self.model.nodes_dict[c_target]
                        ns = self.model.nodes_dict[o_id]
                        # Embed the node
                        if not (
                                nt.x >= ns.x and nt.y >= ns.x
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
                elif c_rel_id in self.model.rels_dict:
                    c = view.add_connection(ref=c_rel_id, source=o_id, target=c_target, uuid=c_id)
                    bps = conn.findall('Position')
                    for i in range(1, len(bps) - 1):
                        pos = bps[i]
                        bp_x = int(pos.get('Pos.X'))
                        bp_y = int(pos.get('Pos.Y'))
                        c.add_bendpoint(Point(bp_x * self.scaleX, bp_y * self.scaleY))

    def _parse_containers(self, grp=None, view=None):
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
            for o in objs.find('RoundedRectangle'):
                pos = o.find('Position')
                size = o.find('Size')
                brush = o.find('Brush')
                if brush is not None:
                    color_str = brush.get('Color')
                else:
                    color_str = "#000000"
                if pos is not None and size is not None:
                    n = view.add(ref=None,
                                 x=self.scaleX * int(pos.get('Pos.X')),
                                 y=self.scaleY * int(pos.get('Pos.Y')),
                                 w=self.scaleX * int(size.get('Size.dX')),
                                 h=self.scaleY * int(size.get('Size.dY')),
                                 node_type='Container'
                                 )
                    n.line_color = f'#{int(color_str):0>6X}'
                    n.fill_color = "#FFFFFF"
                    n.opacity = 0

    def _parse_labels(self):
        """ """
        for o in self.root.findall('FFTextDef'):
            o_id = _id_of(o.attrib['FFTextDef.ID'])
            if o.attrib['IsModelAttr'] == 'TEXT':
                attrs = o.findall('AttrDef')
                o_name = None
                for attr in attrs:
                    key = attr.attrib['AttrDef.Type']
                    val = ''
                    for v in attr.iter('PlainText'):
                        val += v.get('TextValue')
                    if key == 'AT_NAME':
                        o_name = val

                self.model.labels_dict[o_id] = o_name

    def _parse_labels_in_view(self, grp=None, view=None):
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
            if lbl_ref in self.model.labels_dict:
                # Extract Element properties
                o_name = self.model.labels_dict[lbl_ref]
                # calculate size in function of text
                o = objs.find('Position')
                if o is not None:
                    pos = o.attrib
                    # size = objs.find('Size').attrib
                    w, h = max([get_text_size(x, 9, "Segoe UI") for x in o_name.split('\n')])
                    try:
                        n = view.add(
                            ref=lbl_ref,
                            x=max(int(pos.get('Pos.X')) * self.scaleX, 0),
                            y=max(int(pos.get('Pos.Y')) * self.scaleY, 0),
                            w=w + 18,  # 13 * len(max(o_name.split('\n'))),
                            h=30 + (h * 1.5) * (o_name.count('\n') + 1),
                            node_type='Label', label=o_name
                        )
                        n.fill_color = "#FFFFFF"
                        n.opacity = 0
                        n.line_color = '#000000'
                    except ValueError:
                        log.warning(f'Node {o_name} has unknown element reference {lbl_ref}'
                                    f' - ignoring')
                        continue
        return

    def _parse_views(self, group=None, folder=''):
        """

        :param group:  (Default value = None)
        :param folder:  (Default value = '')

        """
        if group is None:
            group = self.root

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
                        val += v.get('TextValue')
                    if key == 'AT_NAME':
                        o_name = val
                    elif key == 'AT_DESC':
                        o_desc = val
                    else:
                        props[key] = val

                # self.model.name = view_name
                view = self.model.add(concept_type=archi_type.View,
                                      name=o_name, uuid=view_id, desc=o_desc)
                log.info('Parsing & adding nodes')
                view.folder = folder
                self._parse_nodes(o, view)

                log.info('Parsing & adding conns')
                self._parse_connections(o, view)
                log.info('Parsing and adding container groups')
                self._parse_containers(o, view)
                log.info('Parsing and adding labels')
                self._parse_labels_in_view(o, view)

            self._parse_views(g, folder)
            folder = old_folder

    def _clean_nested_conns(self):
        """ """
        # Clean now all connections between a node and its embedding node parent
        nested_conns = [x for x in self.model.conns_dict.values()
                        if x.source.uuid == x.parent.uuid and isinstance(x.parent, Node)]
        for c in nested_conns:
            c.delete()
        nested_conns = [x for x in self.model.conns_dict.values() if
                        x.target.uuid == x.parent.uuid and isinstance(x.parent, Node)]
        for c in nested_conns:
            c.delete()
