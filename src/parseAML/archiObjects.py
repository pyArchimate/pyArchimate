"""
* A library to create Archimate Open Exchange File documents.
*
* Author: Xavier Mayeur
* Date: December 2021
* Version 0.1
*
* TODO verify if Elements or Relationships Type are compliant
* TODO Add enumeration for Archimate types
*
"""
from uuid import uuid4, UUID

import xmltodict

from allowedPatterns import simplified_patterns
from logger import log

# Dictionary with all artefact identifier keys & objects
elems_list = {}
rels_list = {}
nodes_list = {}
conns_list = {}
views_list = {}
labels_list = {}


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def set_id(uuid=None):
    """
    Function to create an identifier if none exists
    """
    _id = str(uuid4()) if (uuid is None) else uuid
    if is_valid_uuid(_id):
        _id = _id.replace('-', '')
        if _id[:3] != 'id-':
            _id = 'id-' + _id
    return _id


class OpenExchange:
    """
    OpenExchange class define the methods and properties to create an Open Exchange document

    Properties:
    OEF : OrderedDict
        An OrderedDict dictionary as a model, compliant with the OEF format

    name : str
        the name of the Archimate model
    uuid: str
        the identifier of the Archimate model

    Methods:
    generate_xml: xml
        convert the OEF dictionary into xml

    add_elements : None
        add a collection of Elements to the model

    add_relationships : None
        add a collection of Relationships to the model

    add_view : None
        add a collection of Views to the model

    add_property_def : None
        add a list of property definitions to the model

    add_properties: None
        add a collection of properties to an Element, a Relationship or a View


    """

    def __init__(self, name, uuid=None):
        self._name = name
        self.uuid = set_id(uuid)
        self.elements = []
        self.relationships = []
        self.views = []
        self.organizations = []
        self.properties = {}
        self.OEF = {'model': {
            '@xmlns': 'http://www.opengroup.org/xsd/archimate/3.0/',
            '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            '@xsi:schemaLocation': 'http://www.opengroup.org/xsd/archimate/3.0/ '
                                   'http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd',
            '@identifier': self.uuid,  # UUID
            'name': {
                '@xml:lang': 'en',
                '#text': self._name,  # MODEL NAME
            },
            'properties': {'property': []},
            'elements': {'element': []},  # list of elements
            'relationships': {'relationship': []},  # list of relationships
            'organizations': {'item': []},
            'propertyDefinitions': {'propertyDefinition': []},
            # 'views': {'diagrams': {'view': []}}  # list of diagrams
        }
        }

    def generate_xml(self):
        # Add Model properties
        pdefs = PropertyDefinitions()
        self.add_property_def(pdefs)
        if len(self.properties) == 0:
            del self.OEF['model']['properties']
        else:
            if 'properties' not in self.OEF['model']:
                self.OEF['model']['properties'] = {'property': []}
            for key, value in self.properties.items():
                p = Property(key, value, pdefs)
                if isinstance(p, Property):
                    p = p.property
                self.OEF['model']['properties']['property'].append(p)

        # Add elements
        if 'elements' not in self.OEF['model']:
            self.OEF['model']['elements'] = {'element': []}
        for e in self.elements:
            for key, value in e.properties.items():
                e.add_property(Property(key, value, pdefs))
            self.OEF['model']['elements']['element'].append(e.element)

        # Add relationships
        if len(self.relationships) == 0:
            del self.OEF['model']['relationships']
        else:
            if 'relationships' not in self.OEF['model']:
                self.OEF['model']['relationships'] = {'relationship': []}
            for r in self.relationships:
                self.OEF['model']['relationships']['relationship'].append(r.relationship)

        # Add Views
        if 'views' not in self.OEF['model']:
            self.OEF['model']['views'] = {'diagrams': {'view': []}}
        for v in self.views:
            self.OEF['model']['views']['diagrams']['view'].append(v.view)

        return xmltodict.unparse(self.OEF, pretty=True)

    def add_elements(self, *elements):
        for e in elements:
            self.elements.append(e)

    def find_element(self, name=None, type=None):
        if name and not type:
            return [e for e in self.elements if e.name == name]
        elif type and not name:
            return [e for e in self.elements if e.type == type]
        else:
            return [e for e in self.elements if e.name == name and e.type == type]

    def add_relationships(self, *relationships):
        for r in relationships:
            self.relationships.append(r)

    def replace_relationships(self, id, new_rel):
        self.relationships = [new_rel if (x.id == id) else x for x in self.relationships]
        # rels = self.OEF['model']['relationships']['relationship']
        # self.OEF['model']['relationships']['relationship'] = [elem if (x['@identifier'] == id) else x for x in rels]

    def add_views(self, *views):
        for v in views:
            self.views.append(v)

    def add_property_def(self, propdef):
        self.OEF['model']['propertyDefinitions'] = {'propertyDefinition': propdef.propertyDefinitions}

    def add_organizations(self, org_list=None, item_refs=None):
        refs = item_refs
        orgs = self.OEF['model']['organizations']['item']
        if not isinstance(org_list, list):
            org_list = [org_list]
        p = []
        item = None
        for o in reversed(org_list):
            item = OrgItem(label=o, items=p, item_refs=refs).item
            refs = None
            p = [item]
        if item is not None:
            orgs.append(item)

    def set_name(self, s):
        self._name = s
        self.OEF['model']['name'] = {
            '@xml:lang': 'en',
            '#text': s,  # MODEL NAME
        }

    def get_name(self):
        return self._name

    name = property(get_name, set_name)


class OrgItem:
    def __init__(self, label=None, items=None, item_refs=None):
        self.label = label
        self.item = {}
        if label is not None:
            self.item['label'] = {
                '@xml:lang': 'en',
                '#text': self.label,  # Label NAME
            }
        if item_refs is not None and len(item_refs) > 0:
            if not isinstance(item_refs, list):
                item_refs = [item_refs]
            if 'item' not in self.item:
                self.item['item'] = []
            for i in item_refs:
                self.item['item'].append({
                    "@identifierRef": i
                })
        if items is not None:
            if not isinstance(items, list):
                items = [items]
            if 'item' not in self.item:
                self.item['item'] = []
            for i in items:
                self.item['item'].append(i)


class Element:
    """
    Define an Element artifact

    Properties:
    name : str
        Name of the Element
    uuid : str
        identifier of the Element - can be a UUID4 string, or any unique identifier string
    element: dict
        the element object that will be added to the model

    """

    def __init__(self, name=None, type=None, uuid=None, desc=None, orgs=None, guid=None):
        self._name = name
        self._type = type
        self.uuid = set_id(uuid)
        self._desc = desc
        self.orgs = orgs
        self.guid = guid
        self.properties = {}
        self.element = {
            '@identifier': self.uuid,  # UUID
            '@xsi:type': self._type,  # ELEMENT TYPE
            'name': {
                '@xml:lang': 'en',
                '#text': self._name,  # ELEMENT NAME
            },
            # 'properties': []  # LIST OF ELEMENT PROPERTIES
        }
        if desc:
            self.element['documentation'] = {
                '@xml:lang': 'en',
                '#text': self._desc
            }

    def add_property(self, *properties):

        if 'properties' not in self.element:
            self.element['properties'] = {'property': []}
        for p in properties:
            if isinstance(p, Property):
                p = p.property
            self.element['properties']['property'].append(p)

    def set_name(self, s):
        self._name = s
        self.element['name'] = {
            '@xml:lang': 'en',
            '#text': s,  # MODEL NAME
        }

    def get_name(self):
        return self._name

    name = property(get_name, set_name)

    def set_type(self, t):
        self._type = t
        self.element['@xsi:type'] = self._type

    def get_type(self):
        return self._type

    type = property(get_type, set_type)

    def set_desc(self, s):
        self._desc = s
        self.element['documentation'] = {
            '@xml:lang': 'en',
            '#text': s,  # MODEL NAME
        }

    def get_desc(self):
        return self._desc

    desc = property(get_desc, set_desc)


class Property:
    """
    Define a Property

    Parameters:
    key : str
        the Property key
    value : str
        the Property value
    propdef : PropertyDefinition
        a PropertyDefinition object

    Properties:
    property : dict
        the property object to be added to a model artefact

    """

    def __init__(self, key: str, value: str, propdef):
        self.key = key
        self.value = value
        if not isinstance(propdef, PropertyDefinitions):
            raise ValueError('"propdef" is not a PropertyDefinitions class.')
        ref = [x['@identifier'] for x in propdef.propertyDefinitions if x['name'] == key]
        if len(ref) == 0:
            _id = propdef.add(key)
        else:
            _id = ref[0]

        self.property = {
            '@propertyDefinitionRef': _id,  # PROPERTY ID
            'value': {
                '@xml:lang': 'en',
                '#text': self.value  # PROPERTY VALUE
            }
        }


class PropertyDefinitions:
    """
    Define an PropertyDefinition object

    Properties:
    propertyDefinition : list
        a list of property key objects

    Methods:
    add : str
        add a new key to the list
        :param:  str key
        :return: str key identifier
    """

    def __init__(self):
        self.propertyDefinitions = []

    def add(self, key):
        _p = {
            '@identifier': 'propid_' + str(len(self.propertyDefinitions) + 1),
            '@type': 'string',
            'name': key
        }
        self.propertyDefinitions.append(_p)
        return _p['@identifier']


class Relationship:

    def __init__(self, source, target, type='', uuid=None, name='', access_type=None, influence_strength=None,
                 desc=None):
        self.uuid = set_id(uuid)

        if isinstance(source, Element):
            self._source = source.uuid
        elif isinstance(source, str):
            self._source = source
        else:
            raise ValueError("'source' argument is not an instance of 'Element' class.")

        if isinstance(target, Element):
            self._target = target.uuid
        elif isinstance(target, str):
            self._target = target
        else:
            raise ValueError("'target' argument is not an instance of 'Element' class.")
        self.type = type
        self.name = name
        self.desc = desc
        self.relationship = {
            '@identifier': self.uuid,  # RELATIONSHIP UUID
            '@source': self._source,  # SOURCE UUID
            '@target': self._target,  # TARGET UUID
            '@xsi:type': self.type,  # RELATIONSHIP TYPE
            'name': {
                '@xml:lang': 'en',
                '#text': self.name,  # ELEMENT NAME
            },
            # 'properties': {'property':[]}
        }
        self.access_type = access_type
        self.influence_strength = influence_strength
        if desc:
            self.relationship['documentation'] = {
                '@xml:lang': 'en',
                '#text': self.desc
            }

        if access_type is not None:
            self.relationship['@accessType'] = access_type
        if influence_strength is not None:
            self.relationship['@modifier'] = influence_strength

    def set_source(self, src):
        if isinstance(src, Element):
            self._source = src.uuid
        elif isinstance(src, str):
            self._source = src
        else:
            raise ValueError("'source' argument is not an instance of 'Element' class.")
        self.relationship['@source'] = self._source

    def get_source(self):
        return self._source

    def set_target(self, dst):
        if isinstance(dst, Element):
            self._target = dst.uuid
        elif isinstance(dst, str):
            self._target = dst
        else:
            raise ValueError("'target' argument is not an instance of 'Element' class.")
        self.relationship['@target'] = self._target

    def get_target(self):
        return self._target

    def add_property(self, *properties):
        if 'properties' not in self.relationship:
            self.relationship['properties'] = {'property': []}
        for p in properties:
            if isinstance(p, Property):
                p = p.property
            self.relationship['properties']['property'].append(p)

    def is_simplified_pattern(self) -> bool:
        src: Element = elems_list[self._source]
        dst: Element = elems_list[self._target]
        check_key = src.type + "-" + dst.type
        if check_key in simplified_patterns:
            return True
        else:
            log.warning(f'Relationship "{self.type}" between "{src.name}" and "{dst.name}" '
                        f'does not match simplified patterns list.')
            return False

    source = property(get_source, set_source)
    target = property(get_target, set_target)


class View:

    def __init__(self, name='', uuid=None, desc=None):
        self.uuid = set_id(uuid)
        self.name = name
        self.desc = desc
        self.unions = []
        self.nodes = []
        self.connections = []
        self.properties = {}
        self.view = {
            '@identifier': self.uuid,  # VIEW UUID
            '@xsi:type': 'Diagram',  # VIEW TYPE
            'name': {
                '@xml:lang': 'en',
                '#text': self.name,  # ELEMENT NAME
            },
            'documentation': {
                '@xml:lang': 'en',
                '#text': '' if (self.desc is None) else self.desc
            },
            'node': [],  # LIST OF NODES
            'connection': [],  # LIST OF CONNECTIONS
        }

    def add_node(self, *nodes):
        if 'node' not in self.view:
            self.view['node'] = []
        for n in nodes:
            self.nodes.append(n)
            self.view['node'].append(n.node)
            # check whether nodes refers to a known element
            # if not n.ref in elems_list:
            #     log.warning(f"In 'View.add_node', node '{n.uuid}' refers to undefined element reference '{n.ref}'")

    def sort_node(self):
        self.view['node'].sort(key=lambda x: int(x['@x']) * int(x['@y']))

    def add_container(self, container, label):
        if 'node' not in self.view:
            self.view['node'] = []

        container.node['@xsi:type'] = 'Container'
        container.node['label'] = {
            '@xml:lang': 'en',
            '#text': label,  # label NAME
        }
        del container.node['@elementRef']
        self.view['node'].append(container.node)
        self.nodes.append(container)

    def add_label(self, label_node, label):
        if 'node' not in self.view:
            self.view['node'] = []

        label_node.node['@xsi:type'] = 'Label'
        label_node.node['label'] = {
            '@xml:lang': 'en',
            '#text': label,  # label NAME
        }
        del label_node.node['@elementRef']
        self.view['node'].append(label_node.node)
        self.nodes.append(label_node)
        labels_list[label_node.uuid] = label

    def add_connection(self, *connections):
        if 'connection' not in self.view:
            self.view['connection'] = []
        for c in connections:
            if c.ref in rels_list:
                self.view['connection'].append(c.connection)
                self.connections.append(c)
            else:
                _ns: Node = nodes_list[c.source]
                _nt: Node = nodes_list[c.target]
                _es: Element = elems_list[_ns.ref]
                _et: Element = elems_list[_nt.ref]
                log.warning(f"In 'View.add_connection', node '{c.uuid}' refers "
                            f"to undefined relationship reference '{c.ref}' between nodes "
                            f"'{_es.name}' and '{_et.name}' ")

    def add_property(self, *properties):
        if 'properties' not in self.view:
            self.view['properties'] = {'property': []}
        for p in properties:
            if isinstance(p, Property):
                self.properties[p.key] = p.value
                p = p.property
                self.view['properties']['property'].append(p)


class Node:

    def __init__(self, ref, x=0, y=0, w=120, h=55, style=None, node=None, uuid=None):
        self.uuid = set_id(uuid)
        if isinstance(ref, Element):
            self.ref = ref.uuid
        elif isinstance(ref, str):
            self.ref = ref
        elif ref is not None:
            raise ValueError("'ref' is not an instance of 'Element' class.")
        else:
            self.ref = None
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
        self.area = w * h
        self.style = style
        self.node = node
        self.flags = 0
        self.nodes = []
        self.connections = []
        if self.node:
            self.nodes.append(self.node)
        self.node = {
            '@identifier': self.uuid,  # NODE UUID
            '@elementRef': self.ref,  # ELEMENT UUID
            '@xsi:type': 'Element',
            '@x': str(self.x),  # X CENTER POSITION
            '@y': str(self.y),  # Y CENTER POSITION
            '@w': str(self.w),  # ELEMENT WIDTH
            '@h': str(self.h),  # ELEMENT HEIGHT
            # 'style': self.style,  # STYLE
            # 'node': self.node,  # EMBEDDED NODES
        }

        if isinstance(style, Style) and style is not None:
            self.node['style'] = style.style

    def add_node(self, *nodes):
        if 'node' not in self.node:
            self.node['node'] = []
        for n in nodes:
            self.node['node'].append(n.node)
            self.nodes.append(n)

    def add_connection(self, *connections):
        if 'connection' not in self.node:
            self.node['connection'] = []
        for c in connections:
            self.node['connection'].append(c.connection)
            self.connections.append(c)

    def add_style(self, style):
        if isinstance(style, Style):
            self.node['style'] = style.style

    def get_related_element(self) -> Element:
        return elems_list[self.ref]


class Connection:
    def __init__(self, ref, source, target, style=None, bendpoint=None, uuid=None):
        self.uuid = set_id(uuid)

        if isinstance(ref, Relationship):
            self.ref = ref.uuid
        elif isinstance(ref, str):
            self.ref = ref
        else:
            raise ValueError("'ref' is not an instance of 'Relationship' class.")

        if isinstance(source, Node):
            self.source = source.uuid
        elif isinstance(source, str):
            self.source = source
        else:
            raise ValueError("'source' is not an instance of 'Node' class.")

        if isinstance(target, Node):
            self.target = target.uuid
        elif isinstance(target, str):
            self.target = target
        else:
            raise ValueError("'target' is not an instance of 'Node' class.")

        self.style = style
        self.bendpoints = [bendpoint]
        self.bendpoint = bendpoint

        self.connection = {
            '@identifier': self.uuid,  # CONNECTION UUID
            '@relationshipRef': self.ref,  # RELATIONSHIP UUID
            '@xsi:type': 'Relationship',
            '@source': self.source,  # SOURCE UUID
            '@target': self.target,  # TARGET UUID
            # 'style': self.style,  # STYLE
            # 'bendpoint': self.bendpoint  # BENDPOINTS ABSOLUTE X,Y
        }

        if isinstance(style, Style) and style is not None:
            self.connection['style'] = style.style

    def add_bendpoint(self, *bendpoints):
        if 'bendpoint' not in self.connection:
            self.connection['bendpoint'] = []
        for bp in bendpoints:
            self.bendpoints.append(bp)
            self.connection['bendpoint'].append({
                '@x': str(int(bp[0])),
                '@y': str(int(bp[1]))
            })

    def set_bendpoint(self, bp, index):
        n = len(self.bendpoints)
        if index < n:
            self.bendpoints[index] = bp
            self.connection['bendpoint'][index] = {
                '@x': str(int(bp[0])),
                '@y': str(int(bp[1]))
            }

    def get_bendpoint(self, index):
        n = len(self.bendpoints)
        if index < n:
            return self.bendpoints[index]
        else:
            return None

    def get_all_benpoints(self):
        return self.bendpoints

    def add_style(self, style):
        if isinstance(style, Style):
            self.connection['style'] = style.style


class RGBA:

    def __init__(self, r: int, g: int, b: int, a: int = 100):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
        self.a = max(0, min(100, a))


class Font:

    def __init__(self, name: str = 'Segoe UI', size: int = 9, color: RGBA = (0, 0, 0, 100)):
        self.name = name
        self.size = size
        self.color = color


class Style:

    def __init__(self, fill_color=None, line_color=None, font=None):
        self.fc = fill_color
        self.lc = line_color
        self.f = font
        self.style = {}

        if fill_color is not None and isinstance(fill_color, RGBA):
            self.style['fillColor'] = {
                '@r': str(self.fc.r),  # RED 0-255
                '@g': str(self.fc.g),  # GREEN
                '@b': str(self.fc.b),  # BLUE
                '@a': str(self.fc.a)  # OPACITY 0-100
            }
        if line_color is not None and isinstance(line_color, RGBA):
            self.style['lineColor'] = {
                '@r': str(self.lc.r),  # RED 0-255
                '@g': str(self.lc.g),  # GREEN
                '@b': str(self.lc.b),  # BLUE
                '@a': str(self.lc.a)  # OPACITY 0-100
            }
        if font is not None and isinstance(font, Font):
            self.style['font'] = {
                '@name': self.f.name,
                '@size': self.f.size,
                'color': {
                    '@r': str(self.f.color.r),
                    '@g': str(self.f.color.g),
                    '@b': str(self.f.color.b)
                }
            }
