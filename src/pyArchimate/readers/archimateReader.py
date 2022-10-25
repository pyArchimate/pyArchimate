from .. import *

__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


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

    # Convert the xml structure into XML object
    # root = et.fromstring(data.encode())

    if 'opengroup' not in root.tag:
        log.fatal(f'{__mod__}: Input file is not an Open Group Archimate file - Aborting')
        return None

    ns = root.tag.split('model')[0]
    xsi = '{http://www.w3.org/2001/XMLSchema-instance}'

    model.name = None if root.find(ns + 'name') is None else root.find(ns + 'name').text
    model.desc = None if root.find(ns + 'documentation') is None else root.find(ns + 'documentation').text

    # Get the property definitions dictionary
    pdefs = root.find(ns + 'propertyDefinitions')
    pdef_merge_map = {}
    for p in pdefs.findall(ns + 'propertyDefinition'):
        _id = p.get('identifier')
        val = p.find(ns + 'name').text
        pdef_merge_map[_id] = _id
        if merge_flg:
            if _id in model.pdefs and model.pdefs[_id] != val:
                pdef_merge_map[_id] = 'propid-' + str(len(model.pdefs) + 1)
                _id = pdef_merge_map[_id]
        model.pdefs[_id] = val
    # Get model properties
    if root.find(ns + 'properties') is not None:
        for p in root.find(ns + 'properties').findall(ns + 'property'):
            _id = pdef_merge_map[p.get('propertyDefinitionRef')]
            val = p.find(ns + 'value').text
            model.prop(model.pdefs[_id], val)

    if root.find(ns + 'elements') is not None:
        for e in root.find(ns + 'elements').findall(ns + 'element'):

            # check whether to create or merge element
            _uuid = e.get('identifier')

            if merge_flg and _uuid in model.elems_dict:
                elem = model.elems_dict[_uuid]
                elem.name = None if e.find(ns + 'name') is None else e.find(ns + 'name').text
                elem.desc = None if e.find(ns + 'documentation') is None else e.find(ns + 'documentation').text
                # merge completed, loop on next element
            else:
                # else create a new element
                elem = model.add(
                    name=None if e.find(ns + 'name') is None else e.find(ns + 'name').text,
                    concept_type=e.get(xsi + 'type'),
                    uuid=_uuid,
                    desc=None if e.find(ns + 'documentation') is None else e.find(ns + 'documentation').text
                )
            # Get element properties
            if e.find(ns + 'properties') is not None:
                for p in e.find(ns + 'properties').findall(ns + 'property'):
                    _id = pdef_merge_map[p.get('propertyDefinitionRef')]
                    val = p.find(ns + 'value').text
                    elem.prop(model.pdefs[_id], val)
            # Add the element in the dictionary
            # model.elems_dict[elem.uuid] = elem

    # get relationships
    if root.find(ns + 'relationships') is not None:
        for r in root.find(ns + 'relationships').findall(ns + 'relationship'):
            # check whether to create or merge element
            _uuid = r.get('identifier')
            if merge_flg and _uuid in model.rels_dict:
                rel = model.rels_dict[_uuid]
                rel.name = None if r.find(ns + 'name') is None else r.find(ns + 'name').text
                rel.desc = None if r.find(ns + 'documentation') is None else r.find(ns + 'documentation').text

            else:
                # else create a new element
                rel = model.add_relationship(
                    source=r.get('source'),
                    target=r.get('target'),
                    rel_type=r.get(xsi + 'type'),
                    uuid=r.get('identifier'),
                    name=None if r.find(ns + 'name') is None else r.find(ns + 'name').text,
                    desc=None if r.find(ns + 'documentation') is None else r.find(ns + 'documentation').text,
                    access_type=r.get('accessType'),
                    influence_strength=r.get('modifier'),
                )
                if r.get('isDirected') == "true":
                    rel.is_directed = True
                # model.rels_dict[rel.uuid] = rel
                # Get element properties
                if r.find(ns + 'properties') is not None:
                    for p in r.find(ns + 'properties').findall(ns + 'property'):
                        _id = pdef_merge_map[p.get('propertyDefinitionRef')]
                        val = p.find(ns + 'value').text
                        rel.prop(model.pdefs[_id], val)

    # Get views
    if root.find(ns + 'views') is not None:
        for v in root.find(ns + 'views').find(ns + 'diagrams').findall(ns + 'view'):
            _uuid = v.get('identifier')
            if merge_flg:
                if _uuid in model.views_dict:
                    # Merged view replaces the original one
                    _view = model.views_dict[_uuid]
                    _view.delete()

            _v = model.add(ArchiType.View,
                           name=None if v.find(ns + 'name') is None else v.find(ns + 'name').text,
                           uuid=_uuid,
                           desc=None if v.find(ns + 'documentation') is None else v.find(ns + 'documentation').text
                           )

            # Get element properties
            if v.find(ns + 'properties') is not None:
                for p in v.find(ns + 'properties').findall(ns + 'property'):
                    _id = pdef_merge_map[p.get('propertyDefinitionRef')]
                    val = p.find(ns + 'value').text
                    _v.prop(model.pdefs[_id], val)

            # Get recursively nodes
            def _add_node(o, node):
                """
                Local recursive function to add a node into a view or another node from the XML data

                :param o:           target object in the model (View or Node)
                :param node:   xml data about node and embded nodes
                :return: Node

                """

                _uuid = node.get('identifier')
                if merge_flg and _uuid in model.nodes_dict:
                    _uuid = None
                if node.get(xsi + 'type') == 'Element':
                    _n = o.add(
                        uuid=_uuid,
                        ref=node.get('elementRef'),
                        x=node.get('x'),
                        y=node.get('y'),
                        w=node.get('w'),
                        h=node.get('h'),
                    )
                else:
                    _n = o.add(
                        uuid=_uuid,
                        ref=None,
                        x=node.get('x'),
                        y=node.get('y'),
                        w=node.get('w'),
                        h=node.get('h'),
                        node_type=node.get(xsi + 'type'),
                        label=None if node.find(ns + 'label') is None else node.find(ns + 'label').text
                    )

                # add style
                style = node.find(ns + 'style')
                if style is not None:
                    fc = style.find(ns + 'fillColor')
                    if fc is not None:
                        _n.fill_color = RGBA(fc.get('r'), fc.get('g'), fc.get('b')).color
                        _n.opacity = int(fc.get('a'))
                    lc = style.find(ns + 'lineColor')
                    if lc is not None:
                        _n.line_color = RGBA(lc.get('r'), lc.get('g'), lc.get('b')).color
                        _n.lc_opacity = int(lc.get('a'))
                    ft = style.find(ns + 'font')
                    if ft is not None:
                        _n.font_name = ft.get('name')
                        _n.font_size = ft.get('size')
                        ftc = ft.find(ns + 'color')
                        _n.font_color = RGBA(ftc.get('r'), ftc.get('g'), ftc.get('b')).color

                # Recurse on embedded nodes
                if node.find(ns + 'node') is not None:
                    for sub_node in node.findall(ns + 'node'):
                        _sub_node = _add_node(_n, sub_node)
                        _n.nodes_dict[_sub_node.uuid] = _sub_node
                        _n.model.nodes_dict[_sub_node.uuid] = _sub_node

                # o.model.nodes_dict[node.get('identifier')] = _n
                # o.nodes_dict[node.get('identifier')] = _n
                return _n

            # Get Nodes in view
            if v.find(ns + 'node') is not None:
                for n in v.findall(ns + 'node'):
                    _add_node(_v, n)

            # Get Connections
            if v.find(ns + 'connection') is not None:
                for c in v.findall(ns + 'connection'):
                    _uuid = c.get('identifier')
                    if merge_flg and _uuid is not None:
                        _uuid = None
                    _c = _v.add_connection(
                        ref=c.get('relationshipRef'),
                        source=c.get('source'),
                        target=c.get('target'),
                        uuid=_uuid
                    )
                    # add style
                    style = c.find(ns + 'style')
                    if style is not None:
                        lc = style.find(ns + 'lineColor')
                        if lc is not None:
                            _c.line_color = RGBA(lc.get('r'), lc.get('g'), lc.get('b')).color
                        ft = style.find(ns + 'font')
                        if ft is not None:
                            _c.font_name = ft.get('name')
                            _c.font_size = ft.get('size')
                            ftc = ft.find(ns + 'color')
                            _c.font_color = RGBA(ftc.get('r'), ftc.get('g'), ftc.get('b')).color
                        _c.line_width = style.get('lineWidth')
                    # Add Bendpoints
                    for bp in c.findall(ns + 'bendpoint'):
                        _c.add_bendpoint(Point(bp.get('x'), bp.get('y')))
                    # and update the dictionary
                    # model.conns_dict[c['@identifier']] = _c

            # Add view in the model
            # model.views_dict[_v.uuid] = _v

    # # Get organizations
    orgs = root.find(ns + 'organizations')
    if orgs is not None:
        def _walk_orgs(item, folder=''):
            """
            Local recursive function to walk through the xml organization structure
            and assign folder path to referred View/Element/Relationship objects

            :param item:
            :param folder:

            """
            items = item.findall(ns + 'item')
            label = item.find(ns + 'label')
            if label is not None:
                folder += '/' + label.text
            if item.find(ns + 'documentation') is not None:
                # We reach the lowest level for a view, where we also find the documentation of the view
                desc = item.find(ns + 'documentation').text
                id = item.find(ns + 'item').get('identifierRef')
                _v = model.views_dict[id]
                _v.desc = desc
                _v.folder = folder
            else:
                # Either we find references
                for sub_item in items:
                    id = sub_item.get('identifierRef')
                    if id is not None:
                        if id in model.views_dict:
                            model.views_dict[id].folder = folder
                        elif id in model.elems_dict:
                            model.elems_dict[id].folder = folder
                        elif id in model.rels_dict:
                            model.rels_dict[id].folder = folder
                    else:
                        # Or we drill down
                        _walk_orgs(sub_item, folder)

        # Extract organization structure from the model
        items = orgs.findall(ns + 'item')
        for item in items:
            _walk_orgs(item)
