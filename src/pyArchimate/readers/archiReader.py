from .. import *

__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def archi_reader(model, root, merge_flg=False):
    """
    Merge / initialize the model from XML Archimate OEF data

    Used by Model.read(filepath) or Model.merge(filepath) methods
    :param model: pyArchimate Model object
    :type model: Model
    :param root:    XML data to convert
    :type root:
    :param merge_flg: if True, merge data into the provided model, else clear the model and read data into it
    :type merge_flg: bool

    """

    # Convert the xml structure into XML object
    # root = et.fromstring(data.encode())

    if 'archimate' not in root.tag:
        log.fatal(f'{__mod__}: Input file is not an Open Group Archimate file - Aborting')
        return None

    ns = root.tag.split('model')[0]
    xsi = '{http://www.w3.org/2001/XMLSchema-instance}'

    model.name = root.get('name')
    model.desc = None if root.find('purpose') is None else root.find('purpose').text

    # Get model properties
    if root.find('property') is not None:
        for p in root.findall('property'):
            model.prop(p.get('key'), p.get('value'))

    # Loop on folder (recursive) structure

    def _get_folders_elem(tag, folder_path=''):
        folder = folder_path + '/' + tag.get('name')
        # Get folders items that are not folder
        for e in tag.findall('element'):
            type_e = e.get(xsi + 'type').split(':')[1]
            if 'Relationship' not in type_e and 'ArchimateDiagramModel' not in type_e:
                elem = None
                if merge_flg:
                    elem = model.get_or_create_element(elem_type=type_e, elem=e.get('name'))
                if elem is None:
                    elem = model.add(concept_type=type_e, name=e.get('name'), uuid=e.get('id'))
                elem.folder = folder
                doc = e.find('documentation')
                if doc is not None:
                    elem.desc = e.text
                for p in e.findall('property'):
                    elem.prop(p.get('key'), p.get('value'))
                if type_e == 'Junction':
                    elem.junction_type = e.get('type') if e.get('type') is not None else 'and'

        for f in tag.findall('folder'):
            _get_folders_elem(f, folder)

    def _get_folders_rel(tag, folder_path=''):
        folder = folder_path + '/' + tag.get('name')
        # Get folders items that are not folder
        for e in tag.findall('element'):
            type_e = e.get(xsi + 'type').split(':')[1]
            if 'Relationship' in type_e:
                type_e = type_e[:-len("Relationship")]
                elem = None
                if merge_flg:
                    elem = model.get_or_create_relationship(rel_type=type_e, name=e.get('name'))
                if elem is None:
                    elem = model.add_relationship(rel_type=type_e, name=e.get('name'), uuid=e.get('id'),
                                                  source=e.get('source'), target=e.get('target'))
                elem.folder = folder
                at = e.get('accessType')
                if at is not None:
                    elem.access_type = access_type.Read if at == "1" else access_type.ReadWrite if at == "3" else access_type.Access
                if e.get('directed') is not None:
                    elem.is_directed = e.get('directed') == "true"
                if e.get('strength') is not None:
                    elem.influence_strength = e.get("strength")
                doc = e.find('documentation')
                if doc is not None:
                    elem.desc = e.text
                for p in e.findall('property'):
                    elem.prop(p.get('key'), p.get('value'))

        for f in tag.findall('folder'):
            _get_folders_rel(f, folder)

    def _get_node(tag, parent):
        """
        Get recursively children from parent tag (view or child)
        :param tag: XMLtag with children
        :param parent: archimate model View or Node parent
        :return:
        """
        for child in tag.findall('child'):
            # Get a child and its attributes
            node = None
            type = child.get(xsi + 'type').split(':')[1]
            if type == 'DiagramObject':
                node = parent.add(ref=child.get('archimateElement'), uuid=child.get('id'))
            elif type == 'Group':
                node = parent.add(ref=child.get('archimateElement'), uuid=child.get('id'), node_type='Container',
                                  label=child.get('name'))
            elif type == 'Note':
                node = parent.add(ref=child.get('archimateElement'), uuid=child.get('id'), node_type='Label')
                node.label = child.find('content').text if child.find('content') is not None else None

            bounds = child.find('bounds')
            if isinstance(parent, Node):
                x = parent.x
                y = parent.y
            else:
                x = 0
                y = 0

            node.x = int(bounds.get('x')) + x
            node.y = int(bounds.get('y')) + y
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
            ft = child.find('feature')
            if ft is not None:
                if ft.get('name') == 'lineAlpha':
                    node.lc_opacity = 100 * int(ft.get('value')) / 255
            node.text_alignment = child.get('textAlignment')
            node.text_position = child.get('textPosition')
            # recurse on child's children
            _get_node(child, node)

    def _get_connection(tag, parent: View):
        for child in tag.findall('child'):
            for sc in child.findall('sourceConnection'):
                conn = parent.add_connection(ref=sc.get('archimateRelationship'),
                                             source=sc.get('source'),
                                             target=sc.get('target'),
                                             uuid=sc.get('id')
                                             )
                if sc.get('fontColor') is not None:
                    conn.font_color = sc.get('fontColor')
                if sc.get('lineColor') is not None:
                    conn.line_color = sc.get('lineColor')
                if sc.get('lineWidth') is not None:
                    conn.line_width = int(sc.get('lineWidth'))
                conn.text_position = sc.get('textPosition')
                if sc.get('source') in parent.model.nodes_dict:
                    source_node = parent.model.nodes_dict[sc.get('source')]
                else:
                    source_node =  parent.model.conns_dict[sc.get('source')]
                if sc.get('target') in  parent.model.nodes_dict:
                    target_node = parent.model.nodes_dict[sc.get('target')]
                else:
                    target_node = parent.model.conns_dict[sc.get('target')]
                for bp in sc.findall('bendpoint'):
                    _x = 0
                    _y = 0
                    if bp.get('startX') is not None:
                        _x = int(bp.get('startX')) + source_node.cx
                    if bp.get('startY') is not None:
                        _y = int(bp.get('startY')) + source_node.cy
                    if bp.get('endX') is not None:
                        _x = int(bp.get('endX')) + target_node.cx
                    if bp.get('endY') is not None:
                        _y = int(bp.get('endY')) + target_node.cy
                    conn.add_bendpoint(Point(_x, _y))
            _get_connection(child, parent)

    def _get_folders_view(tag, folder_path=''):
        folder = folder_path + '/' + tag.get('name')
        # Get folders items that are not folder
        for e in tag.findall('element'):
            type_e = e.get(xsi + 'type').split(':')[1]
            if 'ArchimateDiagramModel' in type_e:
                elem = model.add(concept_type=archi_type.View, name=e.get('name'), uuid=e.get('id'))
                elem.folder = folder
                doc = e.find('documentation')
                if doc is not None:
                    elem.desc = e.text
                for p in e.findall('property'):
                    elem.prop(p.get('key'), p.get('value'))
                # Manage nodes
                _get_node(e, elem)
                # manage connections
                _get_connection(e, elem)
        for f in tag.findall('folder'):
            _get_folders_view(f, folder_path)

    for f in root.findall('folder'):
        _get_folders_elem(f, '')
    for f in root.findall('folder'):
        _get_folders_rel(f, '')
    for f in root.findall('folder'):
        _get_folders_view(f, '')
