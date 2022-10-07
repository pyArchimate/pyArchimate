"""
*   Conversion program from ARIS AML xml file to Archimate Open Exchange File format
*   Author: X. Mayeur
*   Date: December 2021
*   Version 0.1
*
*
"""

import ctypes
import platform
from xml.sax.saxutils import escape
from jsonpath_ng import parse
from logger import log
from src.pyArchimate.pyArchimate import *


used_elems_id = []
# Dictionary with all artefact identifier keys & objects
elems_list = defaultdict(Element)
rels_list = defaultdict(Relationship)
nodes_list = defaultdict(Node)
conns_list = defaultdict(Connection)
views_list = defaultdict(View)
labels_list = defaultdict(Node)


def get_text_size(text, points, font):
    if platform.system() == 'Linux':
        from PIL import ImageFont
        font = ImageFont.truetype('DejaVuSans.ttf', points)
        size = font.getsize('Hello world')
        return size[0], size[1]

    else:
        class SIZE(ctypes.Structure):
            _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

        hdc = ctypes.windll.user32.GetDC(0)
        hfont = ctypes.windll.gdi32.CreateFontA(points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, font)
        hfont_old = ctypes.windll.gdi32.SelectObject(hdc, hfont)

        size = SIZE(0, 0)
        ctypes.windll.gdi32.GetTextExtentPoint32A(hdc, text, len(text), ctypes.byref(size))

        ctypes.windll.gdi32.SelectObject(hdc, hfont_old)
        ctypes.windll.gdi32.DeleteObject(hfont)

        return size.cx, size.cy


def str2xml_escape(txt):
    return escape(txt, entities={"'": "&apos;", '"': "&quot;", '\r': "&#13;"})


def xml_escape2str(txt):
    txt = txt.replace("&lt;", "<")
    txt = txt.replace("&gt;", ">")
    txt = txt.replace("&amp;", "&")
    txt = txt.replace("&apos;", "'")
    txt = txt.replace("&quot;", '"')
    txt = txt.replace("&#13;", "\r")
    return txt


def _id_of(_id):
    return 'id-' + _id.split('.')[1]


class AML:
    """
    Class to perform the parsing of ARIS AML data and to generate an Archimate model
    """

    def __init__(self, aml_data: str, name='aris_export', scale_x=0.3, scale_y=0.3,
                 skip_bendpoint=True, include_organization=False, incl_unions=True,
                 optimize=True, no_view=False, check_pattern=True):
        """
        Parameters:
             aml_data : str
                file path  to ARIS AML
            name : str
                name of the model
            scale_x : float
                scale factor to enlarge or reduce the diagrams (X-axis)
            scale_x : float
                scale factor to enlarge or reduce the diagrams (Y-axis)
            skip_bendpoint : bool
                flag to indicate whether bendpoints of conns should not be managed

        properties:
            data : orderedDict
                ARIS AML data converted to an ordered dictionary object
            eof_data : XML
                Result of the conversion in XML format
            model : orderedDict
                Result of the conversion as an orderedDict

        methods:

            convert : None
                Convert AML object to OEF one by calling the parsers
            _parse_elements : None
                Extract all elements 'ObjDef' from ARIS data
            _parse_relationships : None
                Extract all relationships 'CxnDef' between elements from Aris data
                Note that some relationships are not processed as they relate to object in the central Aris database
                not shown in the view. A warning is generated in such case
            parse_view : None
                Extract all views and invokes _parse_nodes and _parse_connections
            _parse_nodes : None
                Extract all nodes 'ObjOcc' and check whether the related target data exists
            _parse_connections : None
                Extract all conns between node and check whether the related target node exist
            _parse_containers: None
                Extract all rectangle graphical objects and convert them in containers.
                It is a specialization of _parse_nodes
            _parse_labels : None
                Extract all text label
            _parse_labels_in_view : None
                Extract labels metadata (position, style) and convert them as labels.
                It is a specialization of _parse_nodes


        """
        # self.data = xmltodict.parse(open(aml_file, 'r').read())
        self.data = xmltodict.parse(aml_data)
        if 'AML' not in self.data:
            log.fatal(' Input file is not an ARIS AML file - Aborting')
            sys.exit(1)
        self.organizations = []
        self.name = name
        self.model = Model(self.name)
        self.elements = []
        self.relationships = []
        self.scaleX = float(scale_x)
        self.scaleY = float(scale_y)
        self.skip_bendpoint = skip_bendpoint
        self.incl_org = include_organization
        self.optimize = optimize
        self.no_view = no_view
        self.check_pattern = check_pattern
        self.incl_union = incl_unions

    def convert(self):

        log.info('Parsing elements')
        self._parse_elements()
        log.info('Parsing relationships')
        self._parse_relationships()

        if not self.no_view:
            log.info('Parsing Labels')
            self._parse_labels()
            log.info('Parsing Views')
            self._parse_views()
            # Clean nested connections
            self._clean_nested_conns()
        # log.info('Adding elements')
        # self._add_elements()
        # log.info('Adding relationships')
        # self.add_relationships()
        self.model.expand_props(clean_doc=True)
        log.info('Performing final model validation checks')
        inv_c = self.model.check_invalid_conn()
        inv_n = self.model.check_invalid_nodes()
        if len(inv_n) > 0 or len(inv_c) > 0:
            log.error("Errors found in the model")
            print(inv_n)
            print(inv_c)

        return self.model

    def _get_attributes(self, o: dict, sep=' ') -> dict:
        """
        Extract attributes from the aml data
        :param o:       aml data dictionary
        :type o: object
        :param sep: word separator
        :type sep= str
        :returns: a tuple with the name, the description and properties found in the aml object
        :rtype: (str, str, dict)
        """
        o_name = ''
        props = dict()
        o_desc = None

        def _find_text(arg):
            expr = parse('$[*]..@TextValue')
            return expr.find(arg)

        if 'AttrDef' not in o:
            return None, {}, None
        else:
            attribs = o['AttrDef']

        if not isinstance(attribs, list):
            attribs = [attribs]

        for attr in attribs:
            attr = attr

            if not isinstance(attr, list):
                attr = [attr]
            for ad in attr:
                if ad['@AttrDef.Type'] == 'AT_NAME':
                    o_name += sep.join([x.value for x in _find_text(ad)])
                    o_name = o_name.encode('ascii', 'replace').decode()
                else:
                    attr_type = ad['@AttrDef.Type']
                    prop_key = attr_type
                    prop_val = sep.join([x.value for x in _find_text(ad)])
                    prop_val = xml_escape2str(prop_val).encode('ascii', 'replace').decode()
                    props[prop_key] = prop_val
                    if attr_type == 'AT_DESC':
                        o_desc = prop_val

        return o_name, props, o_desc

    def _parse_elements(self, groups=None, orgs=None):
        if groups is None:
            groups = self.data['AML']
        if orgs is None:
            orgs = []
        if 'Group' not in groups:
            return

        groups = groups['Group']
        if not isinstance(groups, list):
            groups = [groups]

        for grp in groups:
            # List organizations
            oo = orgs.copy()
            if not isinstance(oo, list):
                oo = [oo]
            if '@TypeNum' in grp and 'AttrDef' in grp:
                name, props, desc = self._get_attributes(grp)
                oo.append(name)

            if 'ObjDef' in grp:
                objects = grp['ObjDef']

                if not isinstance(objects, list):
                    objects = [objects]

                for o in objects:
                    o_type = ARIS_type_map[o['@SymbolNum']]
                    if o_type == "":
                        o_type = 'label'
                        log.warning("In 'parse_element', empty type found")
                    o_id = o['@ObjDef.ID']
                    o_uuid = 'id-' + o['GUID']
                    o_name, props, o_desc = self._get_attributes(o)
                    if log.getEffectiveLevel() == logging.DEBUG:
                        print('\r' + ' ' * 10 + '\rElement # ' + str(len(elems_list)), end='', flush=True)
                    elem = self.model.add(concept_type=o_type, name=o_name, uuid=o_uuid, desc=o_desc)

                    for k, v in props.items():
                        elem.prop(k, v)
                    if self.incl_org:
                        elem.folder = '/' + '/'.join(oo)
                    elems_list[o_id] = elem
                    elems_list[o_uuid] = elem

            self._parse_elements(grp, oo)
        return

    def _parse_relationships(self, groups=None):
        if groups is None:
            groups = self.data['AML']
        if 'Group' not in groups:
            return

        groups = groups['Group']
        if not isinstance(groups, list):
            groups = [groups]

        for grp in groups:
            if 'ObjDef' in grp:

                objects = grp['ObjDef']

                if not isinstance(objects, list):
                    objects = [objects]

                for o in objects:
                    o_id = o['@ObjDef.ID']
                    o_uuid = "id-" + o['GUID']
                    if 'CxnDef' in o:
                        rels = o['CxnDef']

                        if not isinstance(rels, list):
                            rels = [rels]

                        for rel in rels:
                            r_type = ARIS_type_map[rel['@CxnDef.Type']]
                            r_id = rel['@CxnDef.ID']
                            r_target = elems_list[rel['@ToObjDef.IdRef']].uuid
                            # Extract relationship properties, that will be globally handled  at the end of the
                            # conversion process, before returning the model
                            _, props, _ = self._get_attributes(rel)
                            if r_target is not None:
                                try:
                                    r = self.model.add_relationship(
                                        rel_type=r_type, source=o_uuid, target=r_target, uuid=r_id
                                    )
                                except ArchimateRelationshipError as exc:
                                    r_type = get_default_rel_type(elems_list[o_uuid].type,
                                                                  elems_list[r_target].type)
                                    log.warning(str(exc) + f' - Replacing by {r_type}')
                                    r = self.model.add_relationship(
                                        rel_type=r_type, source=o_uuid, target=r_target, uuid=r_id
                                    )
                                if r is not None:
                                    for k, v in props.items():
                                        r.prop(k, v)
                                    rels_list[r_id] = r

            self._parse_relationships(grp)

        return

    def _parse_unions(self, uu):
        if not self.incl_union:
            return []
        uu = uu
        ns = []
        if not isinstance(uu, list):
            uu = [uu]
        for u in uu:
            if '@ObjOccs.IdRefs' not in u:
                continue
            refs = u['@ObjOccs.IdRefs'].strip().split(' ')
            refs = list(map(_id_of, refs))
            # Need to look which of the data in the refs list is the parent embedding node
            # meaning has connection references to the others

            for np in refs:
                pp = [rels_list[y].source.uuid for y in rels_list
                      if rels_list[y].source.uuid == elems_list[nodes_list[np].ref].uuid]
                if elems_list[nodes_list[np].ref].uuid in pp and len(pp) == len(refs):
                    n: Node = nodes_list[np]
                    ns.append(n)

                    for x in list(set(refs) - {np}):
                        nn: Node = nodes_list[x]
                        # Move the node out of the view and add it into the embedding node
                        # nn.move(n)

                    if 'Union' in u:
                        ns = self._parse_unions(u['Union'])
                        for nn in ns:
                            # nn.move(n)
                            pass
                    break

        return ns

    def _parse_nodes(self, grp=None, view=None):
        if grp is None:
            return

        if 'ObjOcc' not in grp:
            return

        if view is None:
            return

        if not isinstance(view, View):
            raise ArchimateConceptTypeError("'view' is not an instance of class 'View'")

        if 'ObjOcc' in grp:
            objects = grp['ObjOcc']
            if not isinstance(objects, list):
                objects = [objects]
            for o in objects:
                o_type = ARIS_type_map[o['@SymbolNum']]
                o_id = _id_of(o['@ObjOcc.ID'])
                o_elem_ref = elems_list[o['@ObjDef.IdRef']].uuid
                pos = o['Position']
                size = o['Size']
                n = view.add(
                    ref=o_elem_ref,
                    x=int(pos['@Pos.X']) * self.scaleX,
                    y=int(pos['@Pos.Y']) * self.scaleY,
                    w=int(size['@Size.dX']) * self.scaleX,
                    h=int(size['@Size.dY']) * self.scaleY,
                    uuid=o_id
                )
                nodes_list[o_id] = n

                if o_type == 'Grouping':
                    n.fill_color = "#000000"
                    n.opacity = 0
            self._parse_nodes(grp)

        return

    def _parse_connections(self, grp=None, view=None):
        if grp is None:
            return

        if 'ObjOcc' not in grp:
            return

        if view is None:
            return

        if not isinstance(view, View):
            raise ValueError("'view' is not an instance of class 'View'")

        if 'ObjOcc' in grp:
            objects = grp['ObjOcc']
            if not isinstance(objects, list):
                objects = [objects]
            for o in objects:
                o_id = _id_of(o['@ObjOcc.ID'])
                if 'CxnOcc' in o:
                    conns = o['CxnOcc']

                    if not isinstance(conns, list):
                        conns = [conns]
                    for conn in conns:
                        c_id = _id_of(conn['@CxnOcc.ID'])
                        c_rel_id = conn['@CxnDef.IdRef']
                        c_target = _id_of(conn['@ToObjOcc.IdRef'])
                        if '@Embedding' in conn and conn['@Embedding'] == 'YES' and self.incl_union is True:
                            # Aris uses (sometime) reversed relationship when embedding objects,
                            # This gives validation errors when importing into archi...
                            # Swap therefore source and target if needed
                            try:
                                rel = rels_list[c_rel_id]
                                x = rel.target
                                # check if the relationship target is the related data of the visual object and swap
                                nt = nodes_list[c_target]
                                ns = nodes_list[o_id]
                                # Embed the node
                                if ns.x > nt.x and ns.y > nt.y:
                                    log.warning(f"Inverting embedded nodes relationship '{rel.type}' ")
                                    #             f"between nodes '{rel.source.name}' and '{rel.target.name}'")
                                    rel.target = rel.source
                                    rel.source = x
                                    ns.move(nt)
                                else:
                                    nt.move(ns)
                                    # self.model.replace_relationships(c_rel_id, rel.relationship)
                            except ArchimateConceptTypeError as exc:
                                log.warning(exc)
                            except ArchimateRelationshipError as exc:
                                log.warning(exc)
                            except ValueError as exc:
                                log.warning(exc)
                            except KeyError:
                                log.error(f'Orphan Connection with unrelated relationship {c_rel_id} ')
                        else:
                            c = view.add_connection(ref=c_rel_id, source=o_id, target=c_target, uuid=c_id)
                            conns_list[c_id] = c
                            if 'Position' in conn and not self.skip_bendpoint:
                                bps = conn['Position']
                                for i in range(1, len(bps) - 1):
                                    bp_x = int(bps[i]['@Pos.X'])
                                    bp_y = int(bps[i]['@Pos.Y'])
                                    c.add_bendpoint( Point(bp_x * self.scaleX, bp_y * self.scaleY))

            return

    def _parse_containers(self, grp=None, view=None):
        if grp is None:
            return

        if 'GfxObj' not in grp:
            return

        if view is None:
            return

        if not isinstance(view, View):
            raise ArchimateConceptTypeError("'view' is not an instance of class 'View'")

        if 'GfxObj' in grp:
            objects = grp['GfxObj']

            if not isinstance(objects, list):
                objects = [objects]

            for o in objects:
                if 'RoundedRectangle' not in o:
                    continue
                pos = o['Position']
                size = o['Size']
                color_str = o['Brush']['@Color']

                n = view.add(
                    ref=None,
                    x=int(pos['@Pos.X']) * self.scaleX,
                    y=int(pos['@Pos.Y']) * self.scaleY,
                    w=int(size['@Size.dX']) * self.scaleX,
                    h=int(size['@Size.dY']) * self.scaleY,
                    node_type='Container'
                )
                n.line_color = f'#{int(color_str):0>6X}'
                n.fill_color = "#FFFFFF"
                n.opacity = 0
            return

    def _parse_labels(self, groups=None):
        if groups is None:
            groups = self.data['AML']

        if 'FFTextDef' in groups:
            objects = groups['FFTextDef']
            if not isinstance(objects, list):
                objects = [objects]
            for o in objects:
                o_id = _id_of(o['@FFTextDef.ID'])
                labels_list[o_id] = o
            return

    def _parse_labels_in_view(self, grp=None, view=None):
        if grp is None:
            return
        if 'FFTextOcc' not in grp:
            return
        if view is None:
            return
        if not isinstance(view, View):
            raise ArchimateConceptTypeError("'view' is not an instance of class 'View'")

        if 'FFTextOcc' in grp:
            objects = grp['FFTextOcc']
            if not isinstance(objects, list):
                objects = [objects]

            for o in objects:
                lbl_ref = _id_of(o['@FFTextDef.IdRef'])
                if lbl_ref in labels_list:
                    lbl = labels_list[lbl_ref]
                    # calculate size in function of text
                    o_name, _, _ = self._get_attributes(lbl, '\n')
                    pos = o['Position']
                    w, h = max([get_text_size(x, 9, "Segoe UI") for x in o_name.split('\n')])
                    try:
                        n = view.add(
                            ref=_id_of(o['@FFTextDef.IdRef']),
                            x=max(int(pos['@Pos.X']) * self.scaleX, 0),
                            y=max(int(pos['@Pos.Y']) * self.scaleY, 0),
                            w=w,  # 13 * len(max(o_name.split('\n'))),
                            h=30 + (h * 1.5) * (o_name.count('\n') + 1),
                            node_type='Label', label=o_name
                        )
                        n.fill_color = "#FFFFFF"
                        n.opacity = 0
                        n.line_color = '#000000'
                    except ValueError:
                        log.warning(f'Node {o_name} has unknown element reference {_id_of(o["@FFTextDef.IdRef"])}'
                                    f' - ignoring')
                        continue
            return

        self._parse_labels_in_view(grp)
        return

    def _parse_views(self, groups=None, orgs=None):
        if groups is None:
            groups = self.data['AML']
        if orgs is None:
            orgs = []

        if 'Group' not in groups:
            return

        groups = groups['Group']

        if not isinstance(groups, list):
            groups = [groups]

        # Recurse through groups
        for grp in groups:
            # List organizations
            oo = orgs.copy()

            if not isinstance(oo, list):
                oo = [oo]

            if '@TypeNum' in grp and 'AttrDef' in grp:
                name, props, desc = self._get_attributes(grp)
                oo.append(name)

            # Parse models (views)
            if 'Model' in grp:
                refs = []
                models = grp['Model']

                if not isinstance(models, list):
                    models = [models]
                for m in models:
                    view_id = _id_of(m['@Model.ID'])
                    views_list[view_id] = m
                    view_name, model_props, desc = self._get_attributes(m)
                    # self.model.name = view_name
                    view = self.model.add(concept_type=archi_type.View,
                                          name=view_name, uuid=view_id, desc=desc)
                    log.info('Parsing & adding nodes')
                    if self.incl_org:
                        view.folder = '/' + '/'.join(oo)
                    self._parse_nodes(m, view)

                    log.info('Parsing & adding conns')
                    self._parse_connections(m, view)
                    log.info('Parsing and adding container groups')
                    self._parse_containers(m, view)
                    log.info('Parsing and adding labels')
                    self._parse_labels_in_view(m, view)
                    # view.sort_node()
                    refs.append(view_id)

                    lst = []
                    # Parse Unions (node embeddings definitions)
                    if 'Union' in m:
                        unions = m['Union']
                        if not isinstance(unions, list):
                            unions = [unions]
                        for u in unions:
                            self._parse_unions(u)

            self._parse_views(grp, oo)

        return

    def _clean_nested_conns(self):
        # Clean now all connections between a node and its embedding node parent
        nested_conns = [x for x in conns_list.values() if x.source.uuid == x.parent.uuid and isinstance(x.parent, Node)]
        for c in nested_conns:
            c.delete()
        nested_conns = [x for x in conns_list.values() if x.target.uuid == x.parent.uuid and isinstance(x.parent, Node)]
        for c in nested_conns:
            c.delete()

    def _add_elements(self, groups=None, orgs=None):
        if groups is None:
            groups = self.data['AML']
        if orgs is None:
            orgs = []

        if 'Group' not in groups:
            return

        groups = groups['Group']

        if not isinstance(groups, list):
            groups = [groups]

        # Recurse through groups
        for grp in groups:
            # List organizations
            oo = orgs.copy()
            if not isinstance(oo, list):
                oo = [oo]
            if '@TypeNum' in grp and 'AttrDef' in grp:
                name, props, desc = self._get_attributes(grp)
                oo.append(name)

            if 'ObjDef' in grp:
                refs = []
                objects = grp['ObjDef']

                if not isinstance(objects, list):
                    objects = [objects]

                for o in objects:
                    o_id = o['@ObjDef.ID']
                    elem = elems_list[o_id]
                    o_uuid = 'id-' + o['GUID']
                    if self.no_view:
                        # self.model.add_elements(elems_list[o_id])
                        refs.append(o_uuid)
                        used_elems_id.append(o_uuid)
                    else:
                        # check if data has one or more nodes in views or is already defined
                        nn = [x for x in nodes_list if nodes_list[x].ref == o_uuid]
                        if (not self.optimize or len(nn) > 0) and o_id in elems_list:
                            # self.model.add_elements(elems_list[o_id])
                            refs.append(o_uuid)
                            used_elems_id.append(o_uuid)
                    if self.incl_org:
                        elem.folder = '/' + '/'.join(oo)
            self._add_elements(grp, oo)
        return

    def add_relationships(self, groups=None, orgs=None):
        if groups is None:
            groups = self.data['AML']
        if orgs is None:
            orgs = []
        if 'Group' not in groups:
            return
        groups = groups['Group']
        if not isinstance(groups, list):
            groups = [groups]

        # Recurse through groups
        for grp in groups:
            # List organizations
            oo = orgs.copy()
            if not isinstance(oo, list):
                oo = [oo]
            if '@TypeNum' in grp and 'AttrDef' in grp:
                name, props, desc = self._get_attributes(grp)
                oo.append(name)

            if 'ObjDef' in grp:
                refs = []
                objects = grp['ObjDef']

                if not isinstance(objects, list):
                    objects = [objects]

                for o in objects:
                    o_id = o['@ObjDef.ID']
                    o_uuid = 'id-' + o['GUID']
                    if 'CxnDef' in o:
                        rels = o['CxnDef']

                        if not isinstance(rels, list):
                            rels = [rels]

                        for rel in rels:
                            r_id = rel['@CxnDef.ID']
                            # r_id = _id_of(rel['@CxnDef.ID'])
                            r: Relationship = rels_list[r_id]
                            r_target = r.target

                            # Check if source & target are known
                            if r_target in used_elems_id and r_id in rels_list and o_uuid in used_elems_id:
                                # TODO check how to manage access & influence relation metadata
                                self.model.add_relationship(r)
                                refs.append(r_id)
                            # else:
                            #     e: Element = elems_list[o_id]
                            #     log.info(f"In 'add_relationships', Skipping relationship between target {r_target} "
                            #              f"and source '{e.name}' - {o_id}")
                # if self.incl_org:
                #     self.model.add_organizations(oo, refs)

            self.add_relationships(grp)
        return

    # def convert_elem_id(self):
    #     elems = self.model.OEF["model"]['elements']['data']
    #     for e in elems:
    #         id = e['@identifier']
    #         guid = e['properties']['property'][0]['value']['#text']
    #         e['@identifier'] = "id-" + guid
    #         e['properties']['property'][0]['value']['#text'] = id+'|'+guid
    #
    # def convert_other_id(self, data):
    #     # find t and replace ObjDef references
    #     pat = re.compile(r'identifier="(ObjDef\..*?)"')
    #     for id in re.findall(pat, data):
    #         new_id = elems_list[id].guid
    #         data = re.sub(id, new_id, data)
    #
    #     return data


def _is_embedded(node1: Node, node2: Node) -> bool:
    return node1.x > node2.x and node1.y > node2.y
