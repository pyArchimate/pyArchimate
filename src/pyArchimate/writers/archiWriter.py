from .. import *

__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def archi_writer(model: Model, file_path: str):
    """
    The CSV writer generates three output files:
    - one for all elements
    - one for all relationships
    - one for all properties
    The file path is postfixed accordingly to the output file type
    :param model:
    :param file_path:
    """

    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:archimate="http://www.archimatetool.com/archimate" name="(new model)" id="id-2b0c639b388044d09709ceaaadbcf40f" version="4.9.0">
    </archimate:model>
    """

    tree = et.fromstring(xml)
    root = tree
    nsp_url = 'http://www.archimatetool.com/archimate'
    xsi_url = 'http://www.w3.org/2001/XMLSchema-instance'
    xsi = et.QName(xsi_url, 'type')
    ns = {'archimate': nsp_url, 'xsi': xsi}

    # Create basic folder structure
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

    folders = {
        "/Strategy": f_strategy,
        "/Business": f_business,
        "/Application": f_application,
        "/Technology": f_technology,
        "/Motivation": f_motivation,
        "/Implementation & Migration": f_implementation,
        "/Other": f_other,
        "/Physical": f_technology,
        "/Relations": f_relations,
        "/Views": f_views,
        "/Junction": f_other
    }

    def _get_folder(_folders, _folder_str):
        """
        Get or define the folder according to the folder path
        :param _folders: a dictionary of folders tag
        :param _folder_str: a folder path e.g. /Views/myview/...
        :return: a folder XML tag
        """
        paths = _folder_str.split('/')[1:]
        prev_f = _folders['/' + paths[0]]  # this one should already exist (e.g. 'Stragegy', 'Application'...
        cur_path = ''
        f = None
        for p in paths:
            cur_path += '/' + p
            f = _folders[cur_path] if cur_path in _folders else None
            if f is None:
                f = et.SubElement(prev_f, 'folder', name=p, id=set_id())
                _folders[cur_path] = f
            prev_f = f
        return f

    # Import elements
    for elem in model.elements:
        cat = archi_category[elem.type].split('-')[0]
        if cat == "Junction":
            cat = "Other"
        elif cat == "Physical":
            cat = 'Technology'
        if elem.folder is None:
            folder_path = '/' + cat
        elif '/' + cat == elem.folder[:len(cat) + 1]:
            folder_path = elem.folder
        else:
            folder_path = '/' + cat + elem.folder
        folder = _get_folder(folders, folder_path)
        if elem.type == 'Junction':
            elem.type = elem.junction_type.capitalize() + elem.type
        e = et.SubElement(folder, 'element', {
            xsi: 'archimate:' + elem.type,
            'name': elem.name,
            'id': elem.uuid
        })
        if elem.desc is not None:
            doc = et.SubElement(e, 'documentation')
            doc.text = elem.desc
        for k, v in elem.props.items():
            et.SubElement(e, 'property', key=k, value=v)


    # Import relationships
    for rel in model.relationships:
        cat = 'Relations'
        if rel.folder is None:
            folder_path = '/' + cat
        elif '/' + cat == rel.folder[:len(cat) + 1]:
            folder_path = rel.folder
        else:
            folder_path = '/' + cat + rel.folder
        folder = _get_folder(folders, folder_path)
        r = et.SubElement(folder, 'element', {
            xsi: 'archimate:' + rel.type + 'Relationship',
            'id': rel.uuid,
            'source': rel.source.uuid,
            'target': rel.target.uuid
        })

        if rel.name is not None:
            r.set('name', rel.name)

        if rel.access_type == "Read":
            r.set("accessType", "1")
        elif rel.access_type == "ReadWrite":
            r.set("accessType", "3")
        elif rel.access_type == "Access":
            r.set("accessType", "2")

        if rel.is_directed is not None:
            r.set("directed", str(rel.is_directed).lower())

        if rel.influence_strength is not None:
            r.set("strength", rel.influence_strength)

        if rel.desc is not None:
            doc = et.SubElement(r, 'documentation')
            doc.text = rel.desc
        for k, v in rel.props.items():
            et.SubElement(r, 'property', key=k, value=v)

    # Import views
    for view in model.views:
        cat = 'Views'
        if view.folder is None:
            folder_path = '/' + cat
        elif '/' + cat == view.folder[:len(cat) + 1]:
            folder_path = view.folder
        else:
            folder_path = '/' + cat + view.folder
        folder = _get_folder(folders, folder_path)

        e = et.SubElement(folder, 'element', {
            xsi: 'archimate:ArchimateDiagramModel',
            'name': view.name,
            'id': view.uuid
        })

        # Add nodes
        def _add_node(parent, parent_tag, node):

            child = et.SubElement(parent_tag, 'child', {
                xsi: 'archimate:DiagramObject',
                'id': node.uuid,
            })
            if node.font_name is not None and node.font_size is not None:
                size = str(int(node.font_size))
                child.set('font', f"1|{node.font_name}|{size}.0|0|WINDOWS|1|0|0|0|0|0|0|0|0|1|0|0|0|0|{node.font_name}")
            if node.font_color is not None:
                child.set('fontColor', node.font_color.lower())
            if node.line_color is not None:
                child.set('lineColor', node.line_color.lower())
            if node.fill_color is not None:
                child.set('fillColor', node.fill_color.lower())
            if str(node.opacity) != '100':
                child.set('alpha', str(int(255 * int(node.opacity)/100)))
            if str(node.lc_opacity) != '100':
                et.SubElement(child, 'feature', name='lineAlpha', value=str(int(255 * int(node.lc_opacity)/100)))
            if node.cat == 'Element':
                child.set('archimateElement', node.ref)
            elif node.cat == "Container":
                child.set(xsi, 'archimate:Group')
                child.set('name', node.label)
            else:
                child.set(xsi, 'archimate:Note')
                content = et.SubElement(child, 'content')
                content.text = node.label
            if node.text_aligment is not None:
                child.set('textAlignment', node.text_aligment)
            else:
                child.set('textAlignment', "1")

            if isinstance(parent, View):
                et.SubElement(child, 'bounds',
                              x=str(node.x),
                              y=str(node.y),
                              width=str(node.w),
                              height=str(node.h)
                              )
            else:
                et.SubElement(child, 'bounds',
                              x=str(node.x - parent.x),
                              y=str(node.y - parent.y),
                              width=str(node.w),
                              height=str(node.h)
                              )

            # Add related connections for which node is source
            for conn in node.out_conns():
                c = et.SubElement(child, 'sourceConnection', {
                    xsi: "archimate:Connection",
                    'id': conn.uuid,
                    'lineWidth': "1",
                    'source': conn.source.uuid,
                    'target': conn.target.uuid,
                    'archimateRelationship': conn.ref
                })
                if conn.line_width is not None:
                    c.set('lineWidth', str(conn.line_width))
                if conn.font_name is not None and conn.font_size is not None:
                    size = str(int(conn.font_size))
                    c.set('font', f"1|{conn.font_name}|{size}.0|0|WINDOWS|1|0|0|0|0|0|0|0|0|1|0|0|0|0|{conn.font_name}")
                if conn.font_color is not None:
                    c.set('fontColor', conn.font_color.lower())
                if conn.line_color is not None:
                    c.set('lineColor', conn.line_color.lower())
                if conn.text_position is not None:
                    c.set('textPosition', conn.text_position)
                for bp in conn.bendpoints:
                    et.SubElement(c, 'bendpoint',
                                  startX=str(int(bp.x - conn.source.cx)),
                                  startY=str(int(bp.y - conn.source.cy)),
                                  endX=str(int(bp.x - conn.target.cx)),
                                  endY=str(int(bp.y - conn.target.cy))
                                  )
            # Add the references for which the node is target
            targets = []
            for conn in node.in_conns():
                targets.append(conn.uuid)
            if len(targets) > 0:
                child.set('targetConnections', ' '.join(targets))

            for n in node.nodes:
                _add_node(node, child, n)

        for n in view.nodes:
            _add_node(view, e, n)

        if view.desc is not None:
            doc = et.SubElement(e, 'documentation')
            doc.text = view.desc
        for k, v in view.props.items():
            et.SubElement(e, 'property', key=k, value=v)

    # Add model name, documentation & properties
    root.set('name', model.name)
    if model.desc is not None:
        doc = et.SubElement(root, 'purpose')
        doc.text = model.desc
    for k, v in model.props.items():
        et.SubElement(root, 'property', key=k, value=v)

    # Convert the xml structure into XML string data
    xml_str = et.tostring(root, encoding='UTF-8', pretty_print=True)

    # Write  result to file
    if file_path is not None:
        if file_path is not None:
            try:
                with open(file_path, 'wb') as fd:
                    fd.write(xml_str)
            except IOError:
                log.error(f'{__mod__}.write: Cannot write to file "{file_path}')

    return xml_str.decode()
