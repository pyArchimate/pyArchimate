from .. import *


__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def archimate_writer(model, file_path=None) -> str:
    """
    Method to generate an Archimate XML Open Exchange File format structure as a string object

    Used by Model.write(filepath) method

    """
    # Basic model structure
    # Attribute starting with '@' are XML attributes, other are tags
    # Note that the order of the tags may be important, so those ones are defined by default
    # and removed afterward if empty (e.g. documentation or property tags)
    xml = b"""<?xml version="1.0" encoding="utf-8"?>
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd" identifier="id-a84d2455d48c44a2847b3407e270599f">
    </model>
    """

    tree = et.fromstring(xml)
    root = tree
    nsp_url = 'http://www.opengroup.org/xsd/archimate/3.0/'
    xsi_url = 'http://www.w3.org/2001/XMLSchema-instance'
    xsi = et.QName(xsi_url, 'type')
    ns = {'ns': nsp_url, 'xsi': xsi}

    name = et.SubElement(root, 'name')
    name.text = model.name if model.name is not None else 'Archimate Model'

    def _get_prop_def_id(k):
        """
        Get the property definition id for the provided key, or create a new one
        :param k: key to map
        :type k: str
        :return: propertydek id
        """
        id = [x for x, y in model.pdefs.items() if y == k]
        if len(id) == 0:
            id = 'propid-' + str(len(model.pdefs) + 1)
            model.pdefs[id] = k
        else:
            id = id[0]
        return id

    # Get Model documentation
    if model.desc is not None:
        doc = et.SubElement(root, 'documentation')
        doc.text = model.desc
    # get model properties
    if model.props != {}:
        view_props = et.SubElement(root, 'properties')
        for k, v in model.props.items():
            id = _get_prop_def_id(k)
            p = et.SubElement(view_props, 'property', propertyDefinitionRef=id)
            pv = et.SubElement(p, 'value')
            pv.text = v

    # Add all Elements
    elems = et.SubElement(root, 'elements')
    for e in model.elements:
        elem = et.SubElement(elems, 'element', {'identifier': e.uuid, xsi: e.type})
        if e.name is None:
            e.name = e.type
        if e.name is not None:
            e_name = et.SubElement(elem, 'name')
            e_name.text = e.name
        if e.desc is not None and e.desc != '':
            e_desc = et.SubElement(elem, 'documentation')
            e_desc.text = e.desc
        if e.props != {}:
            pp = et.SubElement(elem, 'properties')
            for k, v in e.props.items():
                id = _get_prop_def_id(k)
                p = et.SubElement(pp, 'property', propertyDefinitionRef=id)
                pv = et.SubElement(p, 'value')
                pv.text = v

    # Add all relationships
    elems = et.SubElement(root, 'relationships')
    for e in model.relationships:
        elem = et.SubElement(elems, 'relationship', {
            'identifier': e.uuid,
            'source': e.source.uuid,
            'target': e.target.uuid,
            xsi: e.type
        })
        e: Relationship = e
        if e.access_type is not None:
            elem.set('accessType', e.access_type)
        if e.is_directed is not None:
            elem.set('isDirected', "true")
        if e.influence_strength is not None:
            elem.set('influenceStrength', e.influence_strength)
        if e.name is not None:
            e_name = et.SubElement(elem, 'name')
            e_name.text = e.name
        if e.desc is not None:
            e_desc = et.SubElement(elem, 'documentation')
            e_desc.text = e.desc
        if e.props != {}:
            pp = et.SubElement(elem, 'properties')
            for k, v in e.props.items():
                id = _get_prop_def_id(k)
                if len(id) == 0:
                    id = 'propid-' + str(len(model.pdefs) + 1)
                    model.pdefs[id] = k

                p = et.SubElement(pp, 'property', propertyDefinitionRef=id)
                pv = et.SubElement(p, 'value')
                pv.text = v

    # get model organization
    orgs_dict = defaultdict(list)
    for e in model.elements:
        if e.folder is not None:
            orgs_dict[e.folder].append(e.uuid)
    for r in model.relationships:
        if r.folder is not None:
            orgs_dict[r.folder].append(r.uuid)
    for v in model.views:
        if v.folder is not None:
            orgs_dict[v.folder].append(v.uuid)
    if orgs_dict is not None:
        keys = sorted(orgs_dict.keys())
        orgs = et.SubElement(root, 'organizations')
        for k in keys:
            labels = k.split('/')
            item = orgs
            for label in labels[1:-1]:
                if item.find('ns:item', ns) is None:
                    item = et.SubElement(item, 'item')
                else:
                    item = item.find('ns:item', ns)
                lbl = et.SubElement(item, 'label')
                lbl.text = label
            if item.find('ns:item', ns) is None:
                item = et.SubElement(item, 'item')
            else:
                item = item.find('ns:item', ns)
            label = labels[-1:][0]
            lbl = et.SubElement(item, 'label')
            lbl.text = label
            for i in orgs_dict[k]:
                ref_item = et.SubElement(item, 'item', identifierRef=i)

    # Set Propertydefs
    pd = et.SubElement(root, 'propertyDefinitions')
    for k, v in model.pdefs.items():
        p = et.SubElement(pd, 'propertyDefinition', identifier=k, type='string')
        p_name = et.SubElement(p, 'name')
        p_name.text = v

    # Add all views
    #
    if len(model.views) > 0:
        views = et.SubElement(root, 'views')
        diag = et.SubElement(views, 'diagrams')

        # Add each view
        for _v in model.views:

            view = et.SubElement(diag, 'view', attrib={
                'identifier': _v.uuid,
                xsi: 'Diagram'
            })

            if _v.name is not None:
                v_name = et.SubElement(view, 'name')
                v_name.text = _v.name

            # Get Model documentation
            if _v.desc is not None:
                doc = et.SubElement(view, 'documentation')
                doc.text = _v.desc

            # get view properties
            if _v.props != {}:
                pp = et.SubElement(view, 'properties')
                for k, v in _v.props.items():
                    id = _get_prop_def_id(k)
                    p = et.SubElement(pp, 'property', propertyDefinitionRef=id)
                    pv = et.SubElement(p, 'value')
                    pv.text = v

            # Add all nodes
            # TODO remove the 4 next lines
            _n_data = None
            _v_data = None
            _data = None
            root_xml = None

            def _add_node(parent, n: Node):
                """
                Local function to add nodes in xml view structure

                :param n: Node object
                :return: xml data structure
                """
                if n.cat == 'Element':
                    n_elem = et.SubElement(parent, 'node', attrib={
                        'identifier': n.uuid,
                        'elementRef': n.ref,
                        xsi: n.cat,
                        'x': str(n.x),
                        'y': str(n.y),
                        'w': str(n.w),
                        'h': str(n.h)
                    })
                else:
                    n_elem = et.SubElement(parent, 'node', attrib={
                        'identifier': n.uuid,
                        xsi: n.cat,
                        'x': str(n.x),
                        'y': str(n.y),
                        'w': str(n.w),
                        'h': str(n.h)
                    })
                    lbl = et.SubElement(n_elem, 'label')
                    lbl.text = n.label

                style = et.SubElement(n_elem, 'style')
                if n.line_color is not None:
                    lc = et.SubElement(style, 'lineColor')
                    rgb = RGBA()
                    rgb.color = n.line_color
                    lc.set('r', str(rgb.r))
                    lc.set('g', str(rgb.g))
                    lc.set('b', str(rgb.b))
                    lc.set('a', '100' if n.opacity is None else str(int(n.lc_opacity)))
                if n.fill_color is not None:
                    fc = et.SubElement(style, 'fillColor')
                    rgb = RGBA()
                    rgb.color = n.fill_color
                    fc.set('r', str(rgb.r))
                    fc.set('g', str(rgb.g))
                    fc.set('b', str(rgb.b))
                    fc.set('a', '100' if n.opacity is None else str(int(n.opacity)))
                if n.font_name is not None:
                    ft = et.SubElement(style, 'font', attrib={
                        'name': n.font_name,
                        'size': str(n.font_size)
                    })
                    rgb = RGBA()
                    ftc = et.SubElement(ft, 'color')
                    rgb.color = n.font_color
                    ftc.set('r', str(rgb.r))
                    ftc.set('g', str(rgb.g))
                    ftc.set('b', str(rgb.b))
                # recurse in embedded nodes if any
                for sub_n in n.nodes:
                    _add_node(n_elem, sub_n)

            # Add nodes in view xml structure
            for _n in _v.nodes:
                _add_node(view, _n)

            # Add Connections
            for c in _v.conns:
                c_elem = et.SubElement(view, 'connection', attrib={
                    'identifier': c.uuid,
                    'relationshipRef': c.ref,
                    xsi: 'Relationship',
                    'source': c.source.uuid,
                    'target': c.target.uuid
                })

                style = et.SubElement(c_elem, 'style')
                style.set('lineWidth', str(c.line_width))
                if c.line_color is not None:
                    lc = et.SubElement(style, 'lineColor')
                    rgb = RGBA()
                    rgb.color = c.line_color
                    lc.set('r', str(rgb.r))
                    lc.set('g', str(rgb.g))
                    lc.set('b', str(rgb.b))
                if c.font_name is not None:
                    ft = et.SubElement(style, 'font', attrib={
                        'name': c.font_name,
                        'size': str(c.font_size)
                    })
                    rgb = RGBA()
                    ftc = et.SubElement(ft, 'color')
                    rgb.color = c.font_color
                    ftc.set('r', str(rgb.r))
                    ftc.set('g', str(rgb.g))
                    ftc.set('b', str(rgb.b))
                # Add bendpoints
                for bp in c.get_all_bendpoints():
                    et.SubElement(c_elem, 'bendpoint', x=str(bp.x), y=str(bp.y))

    # Convert the xml structure into XML string data
    xml_str = et.tostring(root, encoding='UTF-8', pretty_print=True)

    if file_path is not None:
        if file_path is not None:
            try:
                with open(file_path, 'wb') as fd:
                    fd.write(xml_str)
            except IOError:
                log.error(f'{__mod__}.write: Cannot write to file "{file_path}')

    return xml_str.decode()

