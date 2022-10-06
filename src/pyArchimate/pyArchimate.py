"""
A library to create and manage Archimate models.

Author: Xavier Mayeur
Date: Aug 2022
Version 0.1

"""
import json
import math
import re
import sys
from collections import defaultdict
from enum import Enum
from uuid import uuid4, UUID
import logging
import xmltodict
import os
import oyaml as yaml

__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
log = logging.getLogger()


def _is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

    Parameters
    ----------
    :param uuid_to_test: uuid string
    :param version: {1, 2, 3, 4}
    :return: True if uuid_to_test is a valid UUID, otherwise `False`.
    :rtype: bool

     Examples
    --------
    is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    is_valid_uuid('c9bf9e58')
    False

    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def _set_id(uuid=None):
    """
    Function to create an identifier if none exists

    Parameters
    ----------   
    :param uuid: a uuid
    :cat uuid: str
    :return: a formatted identifier
    :rtype: str

    """
    _id = str(uuid4()) if (uuid is None) else uuid
    if _is_valid_uuid(_id):
        _id = _id.replace('-', '')
        if _id[:3] != 'id-':
            _id = 'id-' + _id
    return _id


def _add_prop(o, key: str, value=None):
    """
    Add to- or return a property from- an object
    if the value argument is omitted or is None, the property value is returned
    else the property is updated with the new value

    :param o:       an Element, Relationship, View, Model class object
    :type o: Element
    :param key:     property key
    :type key: str
    :param value:   property value
    :type value: str
    :return:        value of the property associated with the key or None if the key does not exist
    :rtype: str

    """
    m = o if isinstance(o, Model) else o.model
    if key not in o.props and value is not None:
        # create prop
        o.props[key] = value
    else:
        # retrieve the identifier and the record in the properties list
        _id = m.property_def.get_id(key)
        if _id is not None and key in o.props:
            if 'properties' not in o.data:
                o.data['properties'] = dict(property=[])
            for p in o.data['properties']['property']:
                if p['@propertyDefinitionRef'] == _id:
                    if value is not None:
                        # update the record
                        p['value'] = value
                        o.props[key] = value
                        return value
                    else:
                        return o.props[key]
        else:
            return None


def _remove_prop(o, key: str):
    """
    Remove a property from an object

    :param o:       an Element, Relationship, View, Model class object
    :param key:     the key of the property to remove
    :return:        None

    """
    if key in o._properties:
        _id = o.property_def.get_id(key) if isinstance(o, Model) else o.model.property_def.get_id(key)
        if _id is not None:
            for idx, p in enumerate(o.data['properties']['property']):
                if p['@propertyDefinitionRef'] == _id:
                    del o._properties[key]
                    del o.data['properties']['property'][idx]
                    break


class DictMergeError(Exception):
    """
    An empty class used to return specific class of error in dictionary merge
    """
    pass


def _data_merge(a: dict, b: dict) -> dict:
    """
    Deep (recursive)  merge of b into a and return merged result
    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen

    :param a: the dictionary object to merge into
    :param b:  the dictionary object to merge into a
    :raises DictMergeError: Merge error
    :return: an object

    """
    key = None

    try:
        if a is None or isinstance(a, str) or isinstance(a, int) or isinstance(a, float):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                a.extend(b)
            else:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = _data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise DictMergeError('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise DictMergeError('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError as _err:
        raise DictMergeError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (_err, key, b, a))
    return a


def _get_str_attrib(key, d: dict) -> str:
    """
    Function to read a string attribute, skipping the language definition if any

    Used in converting from xml data structure by the model reader

    :param key: the name of the attribute
    :param d:   the object containing the attribute
    :return:    text tag

    """
    if d is not None and key in d:
        if '#text' in d[key]:
            return d[key]['#text']
        elif '@xml:lang' not in d[key]:
            return d[key]
        else:
            return ''


def _default_color(elem_type) -> str:
    """
    Get the default color of a Node, according to its type

    :param elem_type:
    :return: #Hex color str
    """
    default_colors = {'strategy': '#F5DEAA', 'business': "#FFFFB5", 'application': "#B5FFFF", 'technology': "#C9E7B7",
                      'physical': "#C9E7B7", 'migration': "#FFE0E0", 'motivation': "#CCCCFF",
                      'relationship': "#0000FF", 'other': '#FFFFFF'}
    if elem_type in archi_category:
        cat = archi_category[elem_type].lower()
        return default_colors[cat]


class Reader(Enum):
    """
    Enum class for Model.read(file, reader) reader options
    """
    ARCHIMATE = 0
    AML = 1


class Point:
    """
    A simple class to manage x, y coordinates of a point
    x: x-coordinate
    y: y-coordinate

    """

    def __init__(self, x=0, y=0):
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        self._x = x
        self._y = y
        
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, val):
        if val < 0:
            val = 0
        self._x = val

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        if val < 0:
            val = 0
        self._y = val

class Position:
    """
    A class to manage positional parameters of a node wrt to another one
        dx: horizontal distance between the two nodes centres
        dy: vertical distance between the two node centres
        gap_x: horizontal distance between the adjacent vertical edges of the two nodes
        gap_y: vertical distance between the adjacent horizontal edges of the two nodes
        angle the angle of the imaginary line connecting the two node's centers
        orientation: one of the letter L(eft), R(ight), T(op), B(ottom) giving the position of the other node
        with respect to this node. An exclamation character '!' means that the adjacent edges
        are overlapping

    """

    def __init__(self):
        self.dx = None
        self.dy = None
        self.gap_x = 0
        self.gap_y = 0
        self.angle = None
        self.orientation = ""

    @property
    def dist(self):
        if self.dx is not None and self.dy is not None:
            return math.sqrt(self.dx ** 2 + self.dy ** 2)
        else:
            return None


# Dictionary with all artefact identifier keys & objects
class PropertyDefinitions:
    """
    Define an PropertyDefinition object

    """

    def __init__(self):
        self.propertyDefinitions = {}
        self.propertyDefinitionsData = []

    def add(self, key):
        """
        Add a new key in the dictionary

        :param key: key to add
        :return: the new key definition
        """
        _id = {
            '@identifier': 'propid-1' + str(len(self.propertyDefinitions) + 1),
            '@type': 'string',
            'name': key
        }
        if _id['@identifier'] not in self.propertyDefinitions:
            self.propertyDefinitions[_id['@identifier']] = key
            self.propertyDefinitionsData.append(_id)
        return _id['@identifier']

    def get_id(self, key):
        keys = [x for x in self.propertyDefinitions if self.propertyDefinitions[x] == key]
        if len(keys) > 0:
            return keys[0]


class Property:
    """
    Define a Property
    Property are key/value pair, where the key is also stored in a PropertyDefinition dictionnart
    and referred by a 'propid' identifier

    :param key: the property key
    :param value: the value associated to the mkey
    :raises ValueError: Exception raised if prodef is not a PropertyDefinition object
    :param propdef: a property definition object

    """

    def __init__(self, key: str, value: str, propdef=None):
        self.key = key
        self.value = value
        self.property = None
        if not isinstance(propdef, PropertyDefinitions):
            raise ValueError('"propdef" is not a PropertyDefinitions class.')
        if key is not None and key != '' and value is not None:
            ref = [k for k, v in propdef.propertyDefinitions.items() if v == key]
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


class OrgItem:
    """
    An Organization items is a  folder in a folder hierarchy (or also called a group)
    and may contain a list of reference to Concepts (Element, View or Relationship) objects
    or a list of other sub-folders

    :param label: the name of the folder
    :param items: a list of other organization items
    :param item_refs: a list of references to other concepts
    """

    def __init__(self, label=None, items=None, item_refs=None):
        self.label = label
        self.item = {}
        # label attribute structure
        if label is not None:
            self.item['label'] = {
                '@xml:lang': 'en',
                '#text': self.label,  # Label NAME
            }
        # item list of references
        if item_refs is not None and len(item_refs) > 0:
            if not isinstance(item_refs, list):
                item_refs = [item_refs]
            if 'item' not in self.item:
                self.item['item'] = []
            for i in item_refs:
                self.item['item'].append({
                    "@identifierRef": i
                })
        # and/or list of sub-folders items
        if items is not None:
            if not isinstance(items, list):
                items = [items]
            if 'item' not in self.item:
                self.item['item'] = []
            for i in items:
                self.item['item'].append(i)


class RGBA:
    """
    Class to manage RGB/hex color and alpha (opacity) channels

    :param r: red channel color intensity 0-255
    :param g: green channel color intensity 0-255
    :param b: blue channel color intensity 0-255
    :param a: alpha channel color intensity 0-100
    """

    def __init__(self, r=255, g=255, b=255, a=100):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
        self.a = max(0, min(100, a))

    @property
    def color(self):
        """
        Get #RGB hex string

        :return: str
        """
        _color = '#' + str(hex(self.r))[2:] + str(hex(self.g))[2:] + str(hex(self.b))[2:]
        return '#{0:02x}{1:02x}{2:02x}'.format(self.r, self.g, self.b).upper()

    @color.setter
    def color(self, color_string):
        """
        Set RGB color from #HEX string

        :param color_string:

        """
        if color_string is not None:
            self.r = int(color_string[1:3], 16)
            self.g = int(color_string[3:5], 16)
            self.b = int(color_string[5:], 16)


class Font:
    """
    Class to manage font attributes

    :param name: Font name
    :param size: Font size
    :param color: RGBA-class font color
    """

    def __init__(self, name: str = 'Segoe UI', size: int = 9, color=RGBA(0, 0, 0, 100)):
        self.name = name
        self.size = size
        self.rgb = color

    @property
    def color(self):
        """
        Get #Hex font color

        :return:  #Hex color string
        """
        return self.rgb.color

    @color.setter
    def color(self, color_string: str):
        """
        Set #Hex color

        :param color_string:

        """
        if color_string is not None:
            self.rgb = RGBA(
                int(color_string[1:3], 16),
                int(color_string[3:5], 16),
                int(color_string[5:], 16)
            )


class Style:
    """
    Class to manage Node or Connection style

    :param fill_color: RGBA color for node background fill
    :param line_color: RGBA color for connection line color
    :param font:       Font class of node & connection font
    :param line_width: Connection line width (normal=1-heavy=3)
    """

    def __init__(self, fill_color=None, line_color=None, font: Font = None, line_width=None):

        if line_color is None:
            self._lc = RGBA(0, 0, 0, 100)
        elif isinstance(line_color, str):
            self._lc = RGBA()
            self._lc.color = line_color
        else:
            self._lc = line_color

        if fill_color is None:
            self._fc = RGBA(0, 0, 0, 100)
        elif isinstance(fill_color, str):
            self._fc = RGBA()
            self._fc.color = fill_color
        else:
            self._fc = fill_color

        self._f = font
        self.data = {}

        if line_width is not None:
            self.data['@lineWidth'] = str(line_width)

        if fill_color is not None and isinstance(fill_color, RGBA):
            self.data['fillColor'] = {
                '@r': str(self._fc.r),  # RED 0-255
                '@g': str(self._fc.g),  # GREEN
                '@b': str(self._fc.b),  # BLUE
                '@a': str(self._fc.a)  # OPACITY 0-100
            }
        if line_color is not None and isinstance(line_color, RGBA):
            self.data['lineColor'] = {
                '@r': str(self._lc.r),  # RED 0-255
                '@g': str(self._lc.g),  # GREEN
                '@b': str(self._lc.b),  # BLUE
                '@a': str(self._lc.a)  # OPACITY 0-100
            }
        if font is not None and isinstance(font, Font):
            self.data['font'] = {
                '@name': self._f.name,
                '@size': str(self._f.size),
                'color': {
                    '@r': str(self._f.rgb.r),
                    '@g': str(self._f.rgb.g),
                    '@b': str(self._f.rgb.b)
                }
            }

    @property
    def fill_color(self):
        """
        Get #Hex fill color code

        :return:   #Hex color string
        """
        if self._fc is not None:
            return self._fc.color

    @fill_color.setter
    def fill_color(self, color_string: str):
        """
        Set #Hex fill color

        :param color_string:

        """
        if self._fc is None:
            self._fc = RGBA(0, 0, 0)
        self._fc.color = color_string
        if 'fillColor' not in self.data:
            self.data['fillColor'] = dict()
        self.data['fillColor']['@r'] = str(self._fc.r)
        self.data['fillColor']['@g'] = str(self._fc.g)
        self.data['fillColor']['@b'] = str(self._fc.b)
        self.data['fillColor']['@a'] = str(self._fc.a)

    @property
    def opacity(self):
        """
        Get node  fill color opacity

        :return: Opacity value 0-100
        """
        if self._fc is not None:
            return self._fc.a

    @opacity.setter
    def opacity(self, val):
        """
        Set node fill color opacity

        :param val: Opacity value 0-100
        """
        if self._fc is None:
            self._fc = RGBA(0, 0, 0)
        self._fc.a = val if (0 <= val <= 100) else 0 if val <= 0 else 100
        self.data['fillColor']['@a'] = self._fc.a

    @property
    def line_color(self):
        """
        Get line color Hex code

        :return: #Hex color string
        """
        if self._lc is not None:
            return self._lc.color

    @line_color.setter
    def line_color(self, color_string: str):
        """
        Set line color to #Hex value

        :param color_string:

        """
        if self._lc is None:
            self._lc = RGBA(0, 0, 0)
        self._lc.color = color_string
        if 'lineColor' not in self.data:
            self.data['lineColor'] = dict()
        self.data['lineColor']['@r'] = str(self._lc.r)
        self.data['lineColor']['@g'] = str(self._lc.g)
        self.data['lineColor']['@b'] = str(self._lc.b)
        self.data['lineColor']['@a'] = str(self._lc.a)

    @property
    def font(self):
        """
        Get a font object

        :return: Font object
        """
        return self._f

    @font.setter
    def font(self, font: Font):
        """
        Set font style

        :param font:

        """
        if self._f is None:
            self._f = Font()
        self._f = font
        if 'font' not in self.data:
            self.data['font'] = dict(color={})
            self.data['font']['color']['@r'] = '0'
            self.data['font']['color']['@g'] = '0'
            self.data['font']['color']['@b'] = '0'
            self.data['font']['@name'] = 'Segoe UI'
            self.data['font']['@size'] = '9'

        self.data['font']['color']['@r'] = str(self._f.rgb.r)
        self.data['font']['color']['@g'] = str(self._f.rgb.g)
        self.data['font']['color']['@b'] = str(self._f.rgb.b)
        self.data['font']['@name'] = self._f.name
        self.data['font']['@size'] = str(self._f.size)

    @property
    def font_color(self):
        """
        Get font color #Hex code

        :return:    #Hex color str
        """
        return self._f.color

    @font_color.setter
    def font_color(self, color_string):
        """
        Set font color to #Hex code value

        :param color_string:

        """
        if self._f is None:
            self._f = Font()
        self._f.color = color_string
        if 'font' not in self.data:
            self.data['font'] = dict(color=dict())
        self.data['font']['color']['@r'] = str(self._f.rgb.r)
        self.data['font']['color']['@g'] = str(self._f.rgb.g)
        self.data['font']['color']['@b'] = str(self._f.rgb.b)

    @property
    def font_name(self) -> str:
        """
        Get font name

        :return: str font name
        """
        return self._f.name

    @font_name.setter
    def font_name(self, name):
        """
        Set font name

        :param name:

        """
        if self._f is None:
            self._f = Font()
        self._f.name = name
        self.data['font']['@name'] = name

    @property
    def font_size(self) -> int:
        """
        Get font size
        :return:    font size
        """
        return int(self._f.size)

    @font_size.setter
    def font_size(self, size):
        """
        Set font size

        :param size:

        """
        if self._f is None:
            self._f = Font()
        self._f.size = size
        self.data['font']['@size'] = str(size)

    @property
    def line_width(self):
        """
        Get line width

        :return: Line width 1-3
        """
        return int(self.data['@lineWidth'])

    @line_width.setter
    def line_width(self, line_width: int):
        """
        Set line width

        :param line_width:

        """
        self.data['@lineWidth'] = str(line_width) if (1 < line_width < 4) else 1


class Element:
    """
    Class to manage Element artifacts
    
    :param name: Name of the element
    :type name: str
    :param elem_type: Archimate concept type of element
    :type elem_type: str
    :param uuid: element identifier
    :type uuid: str
    :param desc: description of the element
    :type desc: str
    :param folder: folder path in which element should be referred to (e.g. /Application/BE)
    :type folder: str
    :param parent: reference to the parent Model object
    :type parent: Model

    :raises ArchimateConceptTypeError: Exception raised on elem_type or parent tyme error
    
    :return: Element object
    :rtype: Element

    """

    def __init__(self, elem_type=None, name=None, uuid=None, desc=None, folder=None, parent=None):

        # Check validity of arguments according to Archimate standard
        if elem_type is None or not hasattr(archi_type, elem_type):
            raise ArchimateConceptTypeError(f"Invalid Element type '{elem_type}'")
        if archi_category[elem_type] == 'Relationship':
            raise ArchimateConceptTypeError(f"Element type '{elem_type}' cannot be a Relationship type")
        if not isinstance(parent, Model):
            raise ValueError('Element class parent should be a class Model instance!')

        # Attribute and data structure initialization
        self._uuid = _set_id(uuid)
        self.parent = parent
        self.model: Model = parent
        self.name = name
        self._type = elem_type
        self.desc = desc
        self.folder = folder
        self._properties = {}

    def delete(self) -> None:
        """
        Delete the current element from the parent model
        Note: it does not delete the instance itself but it remove the data from the model

        It also deletes all relationships that have this element as source or target and
        it deletes all visual nodes referring to this element (and conns) from views

        """
        _id = self.uuid

        # remove nodes used in views referring to this element
        for n in self.parent.nodes_dict.copy().values():
            n_id = n.uuid
            if n.ref == _id:
                n.delete()
                del n

        # remove relationships from ot to this element
        for r in self.parent.rels_dict.copy().values():
            if r.source.uuid == _id or r.target.uuid == _id:
                r.delete()
                del r

        # remove this element's id from parent's dictionaries
        if _id in self.parent.elems_dict:
            del self.parent.elems_dict[_id]

    @property
    def uuid(self):
        """
        Get the identifier of this element
        
        :return:    Identifier str
        :rtype: str
        """
        return self._uuid

    @property
    def type(self):
        """
        Get the Archimate concept type of this element
        
        :return:    type str
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, value):
        """
        Convert this element to a new Archimate concept type
        Note: this is potentially dangerous as existing relationships may become invalid
        No check if performed on the relationship validity afet conversion
        
        :param value:
        :type value: str

        """
        if value is not None:
            if value not in archi_category or archi_category[value] == 'Relationship':
                raise ValueError('Invalid Archimate element type')
            self._type = value

    @property
    def props(self):
        """
        Get all element properties as a  dictionary
        
        :return: properties
        :rtype: dict
        """
        return self._properties

    def prop(self, key, value=None):
        """
        Method to get or set an element's property

        :param key:     Property key
        :type key: str
        :param value:   Property value
        :type value: str
        :return: an existing element property value str if 'value' argument is None
        :rtype: str
        """
        if value is None:
            return self._properties[key] if key in self._properties else None
        else:
            self._properties[key] = value
            return value

    def remove_prop(self, key):
        """
        Method to remove an element property
        
        :param key:
        :type key: str

        """
        if key in self._properties:
            del self._properties[key]

    def merge(self, elem=None, merge_props=False):
        """
        Method to merge another element of the same type with this element
        
        :param elem:        the element to merge
        :type elem: Element
        :param merge_props: flag to merge or not the properties
        :type merge_props: bool

        """
        # check if merged elem is of the same type or raise an exception
        if elem.type != self.type:
            raise ValueError('Merged element has not the same type as target')

        # merge elem into the current one
        if merge_props:
            for key, val in elem.props.items():
                if key not in self.props:
                    self.prop(key, val)

            # merge (concatenate) element description
            if elem.desc != self.desc:
                self.desc += '\n----\n' + elem.desc

        # Re-assign othe element related node references to the this element (merge target)
        for n in [self.model.nodes_dict[x] for x in self.model.nodes_dict if self.model.nodes_dict[x].ref == elem.uuid]:
            n.ref = self.uuid

        # Re-assign other element inboud and outbound relationship references to this element
        for r in self.model.filter_relationships(lambda x: (x.target.uuid == elem.uuid)):
            r.target = self

        for r in self.model.filter_relationships(lambda x: (x.source.uuid == elem.uuid)):
            r.source = self

        # finally delete the merged element
        elem.delete()

    def in_rels(self, rel_type=None):
        """
        Method to get a list of the inbound relationships
        
        :param rel_type: relationship type to filter
        :type rel_type: str
        :return:         [Relationship]
        :rtype: list
        
        """
        if rel_type is None:
            return self.model.filter_relationships(lambda x: (x.target.uuid == self.uuid))
        else:
            return self.model.filter_relationships(lambda x: (
                    x.target.uuid == self.uuid
                    and
                    x.type == rel_type)
                                                   )

    def out_rels(self, rel_type=None):
        """
        Method to get a list of the outbound relationships
        
        :param rel_type: relationship type to filter
        :type rel_type: str
        :return:         [Relationship]
        :rtype: list

        """
        if rel_type is None:
            return self.model.filter_relationships(lambda x: (x.source.uuid == self.uuid))
        else:
            return self.model.filter_relationships(lambda x: (
                    x.source.uuid == self.uuid
                    and
                    x.type == rel_type)
                                                   )

    def rels(self, rel_type=None):
        """
        Method to get a list of the inbound and outbound relationships
        
        :param rel_type: relationship type to filter
        :type rel_type: str
        
        :return:         [Relationship]
        :rtype: list
        """
        if rel_type is None:
            return self.model.filter_relationships(lambda x: (
                    x.target.uuid == self.uuid
                    or
                    x.source.uuid == self.uuid)
                                                   )
        else:
            return self.model.filter_relationships(lambda x: (
                    (x.target.uuid == self.uuid or x.source.uuid == self.uuid)
                    and
                    x.type == rel_type)
                                                   )

    def remove_folder(self):
        """
        Method to remove this element from the given folder path

        """
        self.folder = None


class Relationship:
    """
    Class to manage the relationship between two elements of the model
    
    :param rel_type:        Archimate relationship type
    :type rel_type: str
    :param source:          element source either an element identifier, or an element object
    :type source: [str|Element]
    :param target:          element target either an element identifier, or an element object
    :type target: [str|Element]
    :param uuid:            identifier of the relationship
    :type uuid: str
    :param name:            optional name of the relationship
    :type name: str
    :param access_type:     optional parameter for access relationship ('Read', 'ReadWrite', 'Write', 'Access')
    :type access_type: str
    :param influence_strength: optional influence strength (1-10, '+', '-')parameter for influence relationship
    :type influence_strength: str
    :param desc:             description of the relationship
    :type desc: str
    :param is_directed:      boolean flag for association relationship
    :type is_directed: bool
    :param parent:           parent Model object
    :type parent: Model
    
    """

    def __init__(self, rel_type='', source=None, target=None, uuid=None, name='',
                 access_type=None, influence_strength=None, desc=None, is_directed=None, parent=None):

        if not isinstance(parent, Model):
            raise ValueError('Relationship class parent should be a class Model instance!')
        self.parent = parent
        self.model = parent
        # get source identifier as reference
        if isinstance(source, str):
            self._source = source
        elif not isinstance(source, Element):
            raise ValueError("'source' argument is not an instance of 'Element' class.")
        else:
            self._source = source.uuid
        if self._source not in self.parent.elems_dict:
            raise ValueError(f'Invalid source reference "{self._source}')
        # get target identifier
        if isinstance(target, str):
            self._target = target
        elif not isinstance(target, Element):
            raise ValueError("'target' argument is not an instance of 'Element' class.")
        else:
            self._target = target.uuid
        if self._target not in self.parent.elems_dict:
            raise ValueError(f'Invalid target reference "{target}')

        self._uuid = _set_id(uuid)
        self._type = rel_type
        self.name = name
        self.desc = desc
        self._properties = {}
        self.folder = None

        self._access_type = access_type
        self._influence_strength = influence_strength
        self._is_directed = is_directed

        # check relationship validity (it also tests concept type validity) or raise exception
        check_valid_relationship(self.type, self.source.type, self.target.type)

        # Add the new relationship object in model's dictionaries
        self.parent.rels_dict[self.uuid] = self

    def delete(self):
        """
        Method to delete this relationship from the model structure
        Also take care to remove visual conns from the views
        
        """
        _id = self._uuid
        # remove related conns
        for c in self.parent.conns_dict.copy().values():
            if c.ref == _id:
                c.delete()
                del c
        # remove from parent dictionaries
        if _id in self.parent.rels_dict:
            del self.parent.rels_dict[_id]

    @property
    def uuid(self):
        """
        Get this relationship identifier
        
        :return: Identifier
        :rtype: str
        
        """
        return self._uuid

    @property
    def source(self):
        """
        Get the source object
        
        :return: Source object
        :rtype: [Element | None]
        
        """
        _id = self._source
        return self.parent.elems_dict[_id] if _id in self.parent.elems_dict else None

    @source.setter
    def source(self, src):
        """
        Set the reference to a new source object
        
        :param src: an Element identifier or an Element object
        :type src: [str | Element]
        :raises ArchimateConceptTypeError: wrong type exception
        
        """
        if isinstance(src, str):
            self._source = src
        elif not isinstance(src, Element):
            raise ArchimateConceptTypeError("'source' argument is not an instance of 'Element' class.")
        else:
            self._source = src.uuid

    @property
    def target(self) -> Element:
        """
        Get the target object
        
        :return: Element object
        :rtype: Element
        """
        _id = self._target
        return self.parent.elems_dict[_id] if _id in self.parent.elems_dict else None

    @target.setter
    def target(self, dst):
        """
        Set the reference to a new target object
        
        :param dst: an Element identifier or an Element object
        :type dst: [str | Element]
        :raises ArchimateConceptTypeError: wrong type exception
        
        """
        if isinstance(dst, str):
            self._target = dst
        elif not isinstance(dst, Element):
            raise ArchimateConceptTypeError("'target' argument is not an instance of 'Element' class.")
        else:
            self._target = dst.uuid

    @property
    def type(self):
        """
        Get the Archimate type of the relationship

        :return: Archimate type
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, new_type):
        """
        Set a new type for the relationship

        :param new_type:
        :type new_type: str

        """
        if new_type not in archi_category or archi_category[new_type] != 'Relationship':
            raise ValueError('Invalid Archimate relationship type')
        # Raise an exception is the new relationship type is not compatible with the source & target ones
        check_valid_relationship(new_type, self.source.type, self.target.type)
        self._type = new_type

    @property
    def props(self):
        """
        Return the properties of this relationship

        :return: properties
        :rtype: dict
        """
        return self._properties

    def prop(self, key, value=None):
        """
        Method to set a property given by its key if a value is provided
        or to return of value of a property if the value is None

        :param key:
        :type key: str
        :param value:
        :type value: str
        :return:   value of the property defined by the key or None
        :rtype: str
        """
        if value is None:
            return self._properties[key] if key in self._properties else None
        else:
            self._properties[key] = value
            return value

    def remove_prop(self, key):
        """
        Methode to remove a property by key

        :param key:
        :type key: str

        """
        if key in self._properties:
            del self._properties[key]

    @property
    def access_type(self):
        """
        Get the access type of an Access relationship

        :return: type
        :rtype: str
        """
        return self._access_type

    @access_type.setter
    def access_type(self, val):
        """
        Set the access type of an Access relationship

        :param val:
        :type val: str

        """
        self._access_type = val
        if val is not None and self.type == archi_type.Access:
            self._access_type = val

    @property
    def is_directed(self):
        """
        Get the direction of an Association relationship

        :return: direction flag
        :rtype: boolean
        """
        return self._is_directed

    @is_directed.setter
    def is_directed(self, val: bool):
        """
        Set the direction of an Association relationship

        :param val:
        :type val: bool

        """
        if val is not None and self.type == archi_type.Association:
            self._is_directed = "true" if val else "false"

    @property
    def influence_strength(self):
        """
        Get the influence strength of an Influence relationship

        :return: influence strength
        :rtype: str
        """
        return self._influence_strength

    @influence_strength.setter
    def influence_strength(self, strength):
        """
        Set the influence strength of an Influence relationship
        [0-10 | '+' | '++' | '-' | '--']

        :param strength: strength value
        :type strength: str

        """
        if strength is not None and self.type == archi_type.Influence:
            self._influence_strength = str(strength)

    def remove_folder(self):
        """
        Method to remove this element from the given folder path

        """
        self.folder = None


class Node:
    """
    Class to manage Nodes
    A Node is a visual object representing an Element concept in a View
    
    :param ref:     Identifier of the related Element or an Element object
    :type ref: [str | Element]
    :param x:       top-left absolute x coordinate of the node in the view
    :type x: int
    :param y:       top-left absolute y coordinate of the node in the view
    :type y: int
    :param w:       width of the node
    :type w: int
    :param h:       height of the node
    :type h: int
    :param uuid:    Node identifier
    :type uuid: str
    :param node_type: Node type ['Element' | 'Label' | 'Container']
    :type node_type: str
    :param label:   Label text if node type is not 'Element'
    :type label: str
    :param parent:  Parent object, a View or an embedding Node object
    :type parent: [View | Node]
    
    """

    def __init__(self, ref=None, x=0, y=0, w=120, h=55, uuid=None, node_type='Element',
                 label=None, parent=None):

        if not isinstance(parent, View) and not isinstance(parent, Node):
            raise ValueError('Node class parent should be a class View or Node instance!')

        if isinstance(parent, View):
            self.parent: View = parent
        else:
            self.parent: Node = parent

        self._view = parent.view
        self._model = parent.model

        self._ref = None
        if ref is not None:
            if isinstance(ref, str):
                self._ref = ref
            elif not isinstance(ref, Element):
                raise ValueError("'ref' is not an instance of 'Element' class.")
            else:
                self._ref = ref.uuid

        if self._ref is not None and self._ref not in self.model.elems_dict:
            raise ValueError(f'Invalid element reference "{self._ref}')

        self._uuid = _set_id(uuid)

        self._x = int(x)
        self._y = int(y)
        self._w = int(w)
        self._h = int(h)
        self._cx = self._x + self.w / 2
        self._cy = self._y + self.h / 2
        self._area = self._w * self._h
        self.flags = 0
        self.cat = node_type
        self.label = label
        self.nodes_dict = defaultdict(Node)
        self._fill_color = _default_color(self.type)
        self.line_color = '#000000'
        self.opacity = 100
        self.font_color = None
        self.font_name = 'Segoe UI'
        self.font_size = 9

    def delete(self, recurse=True, delete_from_model=False):
        """
        Delete node and related connections

        :param recurse:  Recurse into embedded nodes & delete them as well
        :type recurse: bool
        :param delete_from_model: Also delete the related Element (always non-recursive)
        :type delete_from_model: bool

        """

        # remove conns from or to this node in parent view connection dictionary
        for c in self.view.conns_dict.copy().values():
            if c._source == self._uuid or c._target == self._uuid:
                c.delete()
                del c

        for n in self.nodes_dict.copy().values():
            if recurse:
                # delete embedded nodes
                n.delete()
            else:
                # re-assign nodes ref to this node's parent
                n.parent = self.parent
                self.parent.nodes_dict[n._ref] = n

        if self._uuid in self.parent.nodes_dict:
            del self.parent.nodes_dict[self._uuid]
        del self.model.nodes_dict[self._uuid]

        if delete_from_model:
            e = self.concept
            e.delete()

    def add(self, ref=None, x=0, y=0, w=120, h=55, style=None, uuid=None, node_type='Element',
            label=None, nested_rel_type=None):
        """
        Method to create a node embedded in this node

        :param ref:     Identifier of the related Element or an Element object
        :type ref: [str | Element]
        :param x:       top-left absolute x coordinate of the node in the view
        :type x: int
        :param y:       top-left absolute y coordinate of the node in the view
        :type y: int
        :param w:       width of the node
        :type w: int
        :param h:       height of the node
        :type h: int
        :param style:   Style object with fill_color and font attributes
        :type style: Style
        :param uuid:    Node identifier
        :type uuid: str
        :param node_type: Node type ['Element' | 'Label' | 'Container']
        :type node_type: str
        :param label:   Label text if node type is not 'Element'
        :type label: str
        :param nested_rel_type: type of nested relationship between the new node and its parent embedding one
        :type nested_rel_type: str

        :returns: Node object
        :rtype: Node

        """
        n = Node(ref, x, y, w, h, uuid, node_type, label, parent=self)
        self.nodes_dict[n.uuid] = n
        self.model.nodes_dict[n.uuid] = n

        # An Embedded node should have a relationship between its parent concept
        # and the parent concept of the embedding node

        # TODO Check the logic to derive the nesting relationship
        #         # check if a relation already exist between the embedding and embedded elements
        #         rels = [r for r in self.model.rels_dict.values() if (r.source.uuid == self._uuid and r.target.uuid == n._uuid)
        #                 or (r.target.uuid == self._uuid and r.source.uuid == n._uuid)]
        #         if len(rels) == 0:
        #             # same types => Specialization
        #             if embed_rel_type == self.type:
        #                 self.model.add_relationship(embed_rel_type=archi_type.Specialization, source=n.concept, target=self.concept)
        #             elif embed_rel_type is None:
        #                 # take the default one
        #                 embed_rel_type = get_default_rel_type(n.type, self.type)
        #                 try:
        #                     embed_rel_type = get_default_rel_type(self.type, n.type)
        #                     self.model.add_relationship(embed_rel_type=embed_rel_type, source=self.concept, target=n.concept)
        #                 except ArchimateRelationshipError:
        #                     # Sometime, there is no allowed type
        #                     log.warning(f'{n.name} ({n.type}) should not be embedded into {self.name} ({self.type})')
        #             else:
        #                 self.model.add_relationship(embed_rel_type=embed_rel_type, source=self.concept, target=n.concept)

        if nested_rel_type is not None:
            self.model.add_relationship(rel_type=nested_rel_type, source=self.concept, target=n.concept)
        return n

    @property
    def uuid(self) -> str:
        """
        Get the identifier of the node.

        :return: Identifier string
        :rtype: str

        """
        return self._uuid

    @property
    def name(self) -> str:
        """
        Get the name of the node's Element concept

        :return: str : parent Element name
        :rtype: str

        """
        if self.cat == 'Element':
            return self.concept.name

    @property
    def desc(self) -> str:
        """
        Get the Node description from the parent Element
        :return: description
        :rtype: str
        """
        return self.concept.desc

    @property
    def type(self):
        """
        Get the type of the node's parent Element concept

        :return: type
        :rtype: str

        """
        if self.cat == 'Element':
            return self.concept.type

    @property
    def concept(self) -> Element:
        """
        Get the referred Element concept object

        :return: Element
        """
        return self.model.elems_dict[self._ref]

    @property
    def ref(self) -> str:
        """
        Get the identifier of the parent Element concept

        :return: Identifier str
        """
        return self._ref

    @ref.setter
    def ref(self, ref):
        """
        Change the reference of the parent Element concept
        This method is used when merging two Elements (of the same type) or migrating the node to another parent Element
        It should be used with care as referring to an Element of another type may lead
        to invalid Archimate relationships

        :param ref: the identifier of the new parent Element
        :type ref: [str | Element]

        """
        if isinstance(ref, Element):
            new_ref = ref.uuid
        else:
            new_ref = ref
        if new_ref in self.model.elems_dict:
            self._ref = new_ref

    @property
    def x(self):
        """
        get the x-coordinate (top-left corner) of the node

        :return: int x
        :rtype: int
        """
        return self._x

    @x.setter
    def x(self, val):
        """
        Set the  top-left x-coordinate of a node

        This also move accordingly all embedded nodes and their children to a new relative position

        :param val:
        :type val: int

        """
        if val < 0:
            val = 0
        for n in self.nodes():
            n.x += val - self._x
        self._x = int(val)
        self._cx = self._x + self.w / 2

    @property
    def cx(self):
        """
        Get the node centroid x coordinate

        :return: float cx

        """
        return float(self._cx)

    @cx.setter
    def cx(self, val):
        """
        Set the value of the centroid x coordinate

        :param val: 
        :type val: float

        """
        if val < 0:
            val = 0

        self.x = int(val - self._w / 2 + 0.5)
        self._cx = val

    @property
    def rx(self):
        """
        Get the relative  x coordinate wrt to embedding node

        :return:   rx
        
        :rtype: int
        """
        if isinstance(self.parent, Node):
            return self._x - self.parent.x
        else:
            return self._x

    @rx.setter
    def rx(self, value):
        """
        Set the x-coordinate relatively to the parent embedding node position

        :param value:
        :type value: int

        """
        if value < 0:
            value = 0
        if isinstance(self.parent, Node):
            self.x = self.parent.x + value
        else:
            self.x = value

    @property
    def y(self):
        """
        Get the top-left node y coordinate

        :return: y
        :rtype: int

        """
        return self._y

    @y.setter
    def y(self, val):
        """
        Set the top-left y-coordinate of the node and move all embedded children position

        :param val:
        :type val: int

        """
        if val < 0:
            val = 0
        for n in self.nodes():
            n.y += val - self._y
        self._y = int(val)
        self._cy = self._y + self.h / 2

    @property
    def cy(self):
        """
        Get the node centroid y coordinate

        :return: cy
        :rtype: float

        """
        return float(self._cy)

    @cy.setter
    def cy(self, val: float):
        """
        Set the centroid y-coordinate

        :param val: centroid y
        :type val: float

        """
        if val < 0:
            val = 0
        self.y = int(val - self._h / 2 + 0.5)
        self._cy = val

    @property
    def ry(self):
        """
        Get the node relative y coordinate wrt to embedding Node

        :return: y
        :rtype: int

        """
        if isinstance(self.parent, Node):
            return self._y - self.parent.y
        else:
            return self._y

    @ry.setter
    def ry(self, value):
        """
        Set the relative y coordinate of this node wrt to embedding node

        :param value:
        :type value: int

        """
        if value < 0:
            value = 0
        if isinstance(self.parent, Node):
            self.y = self.parent.y + int(value)
        else:
            self.y = value

    @property
    def w(self):
        """
        Get the node width

        :return: w
        :rtype: int
        """
        return self._w

    @w.setter
    def w(self, value):
        """
        Set node width

        :param value:
        :type value: int

        """
        self._w = int(value)
        self._cx = self._x + self.w / 2

    @property
    def h(self):
        """
        Get node height

        :return: h
        :rtype: int

        """
        return self._h

    @h.setter
    def h(self, value):
        """
        Set node height

        :param value:
        :type value: int

        """
        self._h = int(value)
        self._cy = self._y + self.h / 2

    @property
    def fill_color(self):
        """
        Get the fill color

        :return: #Hex color
        :rtype: str

        """
        return self._fill_color

    @fill_color.setter
    def fill_color(self, color_str):
        """
        Set the fill color of the Node.

        If color is None, reset to default value

        :param color_str: #Hex color string
        :type color_str: str

        """
        if color_str is None:
            self._fill_color = _default_color(self.type)
        else:
            self._fill_color = color_str

    @property
    def view(self):
        """
        Get parent View object

        :return: View object
        :rtype: View

        """
        return self._view

    @property
    def model(self):
        """
        Get root Model
        :return: Model object
        :rtype: Model
        """
        return self._model

    def nodes(self, elem_type=None):
        """
        Get the list of children nodes

        :return: [Node]
        :rtype: list

        """
        if elem_type is None:
            return self.nodes_dict.values()
        else:
            return [x for x in self.nodes_dict.values() if x.type == elem_type]

    def get_or_create_node(self, elem=None, elem_type=None, x=0, y=0, w=120, h=55,
                           create_elem=False, create_node=False, nested_rel_type=None):
        """
        Method to get an existing node or to create a new one in this node

        :param elem:            Element object or name of the related Element concept
        :type elem: [str | Element]
        :param elem_type:       Archimate Element concept type if create_elem flag is set
        :type elem_type: str
        :param x:               top-left x position of the node
        :type x: int
        :param y:               top-left y position of the node
        :type y: int
        :param w:               node's width
        :type w: int
        :param h:               node's height
        :type h: int
        :param create_elem:     flag to create a new element with name & type if not found
        :type create_elem: bool
        :param create_node:     flag to create a new node if not found
        :type create_node: bool

        :return:                Node object or None
        :rtype: [Node | None]

        """
        # get the element objects
        _e = None
        if not isinstance(elem, Element):
            _e = self.model.find_elements(elem, elem_type)
            if len(_e) > 0:
                _e = _e[0]
            elif create_elem:
                _e = self.model.add(elem_type, name=elem)
            else:
                return None
        else:
            _e = elem

        # get the related node object
        n = [x for x in self.nodes() if x.ref == _e.uuid]
        if len(n) > 0:
            return n[0]
        elif create_node:
            n = self.add(ref=_e, x=x, y=y, w=w, h=h, nested_rel_type=nested_rel_type)
            return n
        else:
            return None

    def is_inside(self, x: int = 0, y: int = 0, point: Point = None) -> bool:
        """
        Check whether the point given by the x,y coordinate is inside this node boundary

        :param x: 
        :type x: int
        :param y:
        :type y: int
        :param point: a point object, overwriting x, y parameters if given
        :type point: Point
        :return: True of the point is inside the node boundary
        :rtype: bool

        """
        if point is not None:
            x = float(point.x)
            y = float(point.y)

        return (self.cx - self.w / 2 < x < self.cx + self.w / 2
                and self.cy - self.h / 2 < y < self.cy + self.h / 2)

    def resize(self, max_in_row=3, keep_kids_size=True, w=120, h=55, gap_x=20, gap_y=20, justify='left', recurse=True):
        """
        Resize the node, to fit all embedded nodes, recursively

        :param max_in_row:          Maximum number of embedded nodes per row
        :type max_in_row: int
        :param keep_kids_size:      Keep embedded node original size or set to default passed w,h parameters
        :type keep_kids_size: bool
        :param w:                   Default node width
        :type w: int
        :param h:                   Default node height
        :type h: int
        :param gap_x:               Horizontal gap between two nodes
        :type gap_x: int
        :param gap_y:               Vertical gap size between two nodes
        :type gap_y: int
        :param justify:             justify node to 'left', 'right', or 'center'
        :type justify: str
        :param recurse:             recurse  & resize embedded nodes
        :type recurse: bool

        """
        max_w = w
        max_h = h

        ba_x = 40
        ba_y = 40
        max_row_h = h

        n = 1
        row = 0
        for _e in self.nodes():
            if recurse:
                _e.resize(max_in_row=3, keep_kids_size=True, w=120, h=55, gap_x=20, gap_y=20)
            min_w = _e.w if (w == -1 or keep_kids_size) else w
            min_h = _e.h if (h == -1 or keep_kids_size) else h

            if justify == 'left':
                _e.rx = ba_x
            elif justify == 'center':
                _e.rx = ba_x
            else:
                _e.rx = max(ba_x, max_w - min_w - gap_x)

            _e.ry = ba_y
            _e.w = min_w
            _e.h = min_h

            max_row_h = max(max_row_h, _e.h)
            ba_x += _e.w + gap_x
            if n % max_in_row == 0:
                row += 1
                if justify == 'center':
                    ba_x = 40 if row % 2 == 0 else 40 + int((_e.w + gap_x) / 2)
                else:
                    ba_x = 40
                ba_y += max_row_h + gap_y
                max_row_h = h

            n += 1
            max_w = max(max_w, _e.rx + _e.w + gap_x)
            max_h = max(max_h, _e.ry + _e.h + gap_y)

        self.w = max_w
        self.h = max_h

    def conns(self, rel_type=None):
        """
        List all connections of the given type connected to the node

        :param rel_type: an Archimate relationship type
        :type rel_type: str

        :return: [Connection]
        :rtype: list
        """
        if rel_type is None:
            return [c for c in self.view.conns_dict.values() if
                    (c.source.uuid == self.uuid or c.target.uuid == self.uuid)]
        else:
            return [c for c in self.view.conns_dict.values() if
                    c.type == rel_type and (c.source.uuid == self.uuid or c.target.uuid == self.uuid)]

    def in_conns(self, rel_type=None):
        """
        List all connections of the given type where the node is target to (inbound conns)

        :param rel_type: an Archimate relationships type
        :type rel_type: str

        :return: [Connection]
        :rtype: list

        """
        if rel_type is None:
            return [c for c in self.view.conns_dict.values() if c.target.uuid == self.uuid]
        else:
            return [c for c in self.view.conns_dict.values() if c.type == rel_type and c.target.uuid == self.uuid]

    def out_conns(self, rel_type=None):
        """
        List all connections of the given type where the node is source to (outbound conns)

        :param rel_type: an Archimate relationships type
        :type rel_type: str

        :return: [Connection]
        :rtype: list
        """
        if rel_type is None:
            return [c for c in self.view.conns_dict.values() if c.source.uuid == self.uuid]
        else:
            return [c for c in self.view.conns_dict.values() if c.type == rel_type and c.source.uuid == self.uuid]

    def get_obj_pos(self, other_node) -> Position:
        """
        Get positional parameter of this node with respect to another one using centroid coordinates

        :param other_node: a Node object
        :type other_node: Node

        :return: a Position object:
        :rtype: Position

        """
        dx = other_node.cx - self.cx
        dy = other_node.cy - self.cy
        position = Position()
        position.dx = dx
        position.dy = dy

        angle = math.atan2(float(dy), float(dx)) * 180 / math.pi
        # normalize angle wrt obj1
        if angle < 0:
            angle += 360
        angle = (360 - angle) % 360
        position.angle = angle

        # Set the orientation
        if angle < 45 or angle > 315:
            pos = 'R'
        elif 45 <= angle < 135:
            pos = 'T'
        elif 135 <= angle < 225:
            pos = 'L'
        else:
            pos = 'B'
        position.orientation = pos

        # Calculate the gaps between objects
        if other_node.cx - other_node.w / 2 > self.x + self.w / 2 \
                and other_node.cx + other_node.w / 2 > self.cx + self.w / 2:
            position.gap_x = other_node.cx - other_node.w / 2 - self.cx - self.w / 2

        elif other_node.cx - other_node.w / 2 < self.cx - self.w / 2 \
                and other_node.cx + other_node.w / 2 < self.cx - self.w / 2:
            position.gap_x = other_node.cx + other_node.w / 2 - self.cx + self.w / 2

        if other_node.cy - other_node.h / 2 > self.cy + self.h / 2 \
                and other_node.cy + other_node.h / 2 > self.cy + self.h / 2:
            position.gap_y = other_node.cy - other_node.h / 2 - self.cy - self.h / 2

        elif other_node.cy - other_node.h / 2 < self.cy - self.h / 2 \
                and other_node.cy + other_node.h / 2 < self.cy - self.h / 2:
            position.gap_y = other_node.cy + other_node.h / 2 - self.cy + self.h / 2

        # Adjust the orientation for adjacent overlapping edges
        if position.gap_x == 0 and position.gap_y < 0:
            position.orientation = "T!"
        elif position.gap_x == 0 and position.gap_y > 0:
            position.orientation = "B!"
        elif position.gap_x < 0 and position.gap_y == 0:
            position.orientation = "L!"
        elif position.gap_x > 0 and position.gap_y == 0:
            position.orientation = "R!"

        return position

    def get_point_pos(self, point: Point) -> Position:
        """
        Get positional parameter of this node center (x,y) points with respect to a point

        :param point: centroid (x, y) coordinate of a Node
        :type point: Point
        :return: Position object
        :rtype: Point

        """
        position = Position()
        position.dx = point.x - self.cx
        position.dy = point.y - self.cy
        position.gap_x = (abs(position.dx) - self.w / 2) * (1 if position.dx > 0 else -1)
        position.gap_y = (abs(position.dy) - self.h / 2) * (1 if position.dy > 0 else -1)

        pos = '*'

        angle = math.atan2(float(position.dy), float(position.dx)) * 180 / math.pi
        if angle < 0:
            angle += 360
        angle = (360 - angle) % 360
        position.angle = angle

        if not (self.cy - self.h / 2 < point.y < self.cy + self.h / 2) and not (
                self.cx - self.w / 2 < point.x < self.cx + self.w / 2):
            if 135 <= angle < 225:
                pos = 'R'
            elif 225 <= angle < 315:
                pos = 'B'
            elif angle >= 315 or angle < 45:
                pos = 'L'
            else:
                pos = 'T'

        if (angle > 270 or angle < 90) and (self.cy - self.h / 2 < point.y < self.cy + self.h / 2):
            pos = 'L!'
        elif angle > 180 and (self.cx - self.w / 2 < point.x < self.cx + self.w / 2):
            pos = 'B!'
        elif angle < 180 and (self.cx - self.w / 2 < point.x < self.cx + self.w / 2):
            pos = 'T!'
        elif self.cy - self.h / 2 < point.y < self.cy + self.h / 2:
            pos = 'R!'

        position.orientation = pos
        return position

    def distribute_connections(self):
        """
        Method to arrange and distribute equally all visual conns along each edge of this node

        """
        top = []
        bottom = []
        left = []
        right = []
        obj1 = None

        # For all conns from/to this node
        for r in self.conns():
            # Get the actual bendpoints
            bps = r.get_all_bendpoints()
            # Set the source and destination objects
            if r.target.uuid == self.uuid:
                obj2 = r.source
                obj1 = r.target
            else:
                obj1 = r.source
                obj2 = r.target

            # Evaluate the position of the other object
            pos = obj1.get_obj_pos(obj2)
            angle = pos.angle
            p = pos.orientation

            # only manage conns that are related to non-embedded objects
            if not obj1.is_inside(obj2.cx, obj2.cy):
                # if a connection does not have any bendpoint, add one in the middle of connection,
                # so we can also reposition it
                if len(bps) == 0:
                    # Calculate the position of this new bendpoint
                    if p == 'L!':
                        _x = obj1.cx - obj1.w / 2 + pos.gap_x / 2
                        _y = obj1.cy
                    elif p == 'R!':
                        _x = obj1.cx + obj1.w / 2 + pos.gap_x / 2
                        _y = obj1.cy
                    elif p == 'B!':
                        _y = obj1.cy + obj1.h / 2 + pos.gap_y / 2
                        _x = obj1.cx
                    elif p == 'T!':
                        _y = obj2.cy + obj2.h / 2 - pos.gap_y / 2
                        _x = obj1.cx
                    else:
                        _x = (obj2.cx + obj1.cx) / 2
                        _y = (obj2.cy + obj1.cy) / 2
                    # Add it to the connection & refresh the list
                    r.add_bendpoint(Point(_x, _y))
                    bps = r.get_all_bendpoints()

                # Select the bendpoint which is closer to this node
                # This is the bendpoint to reposition in this process
                if r.target.uuid == self.uuid:
                    bp = bps[len(bps) - 1]
                    bp.idx = len(bps) - 1
                else:
                    bp = bps[0]
                    bp.idx = 0

                # Get position information about this bendpoint wrt to this node
                bp_pos = obj1.get_point_pos(bp)

                # Sort bendpoint by edge
                if 'R' in bp_pos.orientation:
                    # Add all bendpoints on the right edge of this node in the 'right' list
                    # angle = (angle + 180) % 360
                    right.append({'order': angle, 'bp': bp, 'r': r})
                # and do the same for the other edges
                if 'L' in bp_pos.orientation:
                    angle = (angle + 180) % 360
                    left.append({'order': -angle, 'bp': bp, 'r': r})

                if 'T' in bp_pos.orientation:
                    top.append({'order': -angle, 'bp': bp, 'r': r})

                if 'B' in bp_pos.orientation:
                    # angle = (angle + 180) % 360
                    bottom.append({'order': angle, 'bp': bp, 'r': r})

        # When all relationships and bendpoints are sorted by edge, reposition them
        # Sort the bendpoint in function of the position of the other node to this node
        # so that the connection does not cross whith others
        # and calculate the position of the bendpoint to distribute them over the edge
        i = 1
        for r in sorted(right, key=lambda d: d['order']):
            r['bp'].y = obj1.cy - obj1.h * (0.5 - (i / (len(right) + 1)))
            i += 1
            # r['bp'].x = r['bp'].x + 5*i * ((r.order > 180)? 1:-1)
            r['r'].set_bendpoint(Point(r['bp'].x, r['bp'].y), r['bp'].idx)

        i = 1
        for r in sorted(left, key=lambda d: d['order']):
            r['bp'].y = obj1.cy - obj1.h * (0.5 - (i / (len(left) + 1)))
            i += 1
            # r['bp'].x = r['bp'].x + 5*i * ((r.order > 180)? 1:-1)
            r['r'].set_bendpoint(Point(r['bp'].x, r['bp'].y), r['bp'].idx)

        i = 1
        for r in sorted(bottom, key=lambda d: d['order']):
            r['bp'].x = obj1.cx - obj1.w * (0.5 - (i / (len(top) + 1)))
            i += 1
            r['r'].set_bendpoint(Point(r['bp'].x, r['bp'].y), r['bp'].idx)

        i = 1
        for r in sorted(top, key=lambda d: d['order']):
            r['bp'].x = obj1.cx - obj1.w * (0.5 - (i / (len(bottom) + 1)))
            i += 1
            r['r'].set_bendpoint(Point(r['bp'].x, r['bp'].y), r['bp'].idx)


class Connection:
    """
    Class to manage visual connections between Nodes


    :param ref:         Reference to the parent Relationship concept
    :type ref: [str | Relationship]
    :param source:      Source Node or node uuid of the connection
    :type source: [str | Node]
    :param target:      Target Node or node uuid of the connection
    :type target: [ | Node
    :param uuid:        uuid of the connection (read-only excepted when reading an XML file to set the identifier)
    :type uuid: str
    :param parent:      Parent's view
    :type parent: View
    
    :raises ArchimateConceptTypeError: Exception raised if invalid Archimate object type given
    :raises ValueError:  Exception raise if a reference is not found in the model object dictionaries

    :returns: Connection object
    :rtype: Conenction
   """

    def __init__(self, ref=None, source=None, target=None, uuid=None, parent=None):

        if not isinstance(parent, View):
            raise ArchimateConceptTypeError('Connection class parent should be a class View instance!')
        self.parent: View = parent
        self.view = self.parent
        self._uuid = _set_id(uuid)
        self.model: Model = self.parent.parent

        if isinstance(ref, Relationship):
            self._ref = ref.uuid
        elif isinstance(ref, str):
            self._ref = ref
        else:
            raise ArchimateConceptTypeError("'ref' is not an instance of 'Relationship' class.")
        if self._ref not in self.model.rels_dict:
            raise ValueError(f'Invalid relationship reference "{self._ref}')

        if isinstance(source, Node):
            self._source = source.uuid
        elif isinstance(source, str):
            self._source = source
        else:
            raise ArchimateConceptTypeError("'source' is not an instance of 'Node' class.")
        if self._source not in self.model.nodes_dict:
            raise ValueError(f'Invalid source reference "{self._source}')

        if isinstance(target, Node):
            self._target = target.uuid
        elif isinstance(target, str):
            self._target = target
        else:
            raise ArchimateConceptTypeError("'target' is not an instance of 'Node' class.")
        if self._target not in self.model.nodes_dict:
            raise ValueError(f'Invalid source reference "{self._target}')

        self._uuid = _set_id(uuid)

        self.bendpoints = list()

        # set default style
        self.line_color = "#000000"
        self.font_color = None
        self.font_name = 'Segoe UI'
        self.font_size = 9

    def delete(self):
        """
        Method to delete this Connection

        """
        del self.view.conns_dict[self.uuid]
        del self.model.conns_dict[self.uuid]

    @property
    def uuid(self):
        """
        Get Connection identifier

        :return: Identifier 
        :rtype: str
        """
        return self._uuid

    @property
    def ref(self):
        """
        Get the parent Relationship reference

        :return: Identifier 
        :rtype: str
        """
        return self._ref

    @ref.setter
    def ref(self, ref):
        """
        Set a new Relationship reference to this connection

        :param ref: Reference to a Relationship 
        :type ref: [str | Relationship]

        """
        if isinstance(ref, Relationship):
            new_ref = ref.uuid
        else:
            new_ref = ref
        if new_ref in self.model.rels_dict:
            self._ref = new_ref

    @property
    def concept(self):
        """
        Get the Relationship object referred by ref

        :return: Relationship object
        :rtype: Relationship
        """
        return self.model.rels_dict[self._ref]

    @property
    def type(self):
        """
        Get the type of the parent relationship

        :return: type 
        :rtype: str
        """
        return self.model.rels_dict[self._ref].type

    @property
    def name(self):
        """
        Get the name of the parent Relationship

        :return: name 
        :rtype: str
        """
        return self.model.rels_dict[self._ref].name

    @property
    def source(self):
        """
        Get the Node object at the source of the relationship

        :return: Node object
        :rtype: Node
        """
        if self._source in self.model.nodes_dict:
            return self.model.nodes_dict[self._source]

    @source.setter
    def source(self, elem):
        """
        Set a new source Node object to this

        :param elem:
        :type elem: [str|Node]

        """
        if isinstance(elem, Node):
            new_ref = elem.uuid
        else:
            new_ref = elem
        if new_ref in self.model.nodes_dict:
            self._source = new_ref

    @property
    def target(self):
        """
        Get the target Node object

        :return: Node object
        :rtype: Node
        """
        if self._target in self.model.nodes_dict:
            return self.model.nodes_dict[self._target]

    @target.setter
    def target(self, elem):
        """
        Set a new target Node to this relationship

        :param elem:
        :type elem: [str|Node]

        """
        if isinstance(elem, Node):
            new_ref = elem.uuid
        else:
            new_ref = elem
        if new_ref in self.model.nodes_dict:
            self._target = new_ref

    def add_bendpoint(self, *bendpoints: Point):
        """
        Method to add one or multiple bendpoints x-y Point to shape the connection

        :param bendpoints:
        :type bendpoints: Point, Point, ...

        """
        for bp in bendpoints:
            self.bendpoints.append(bp)

    def set_bendpoint(self, bp: Point, index):
        """
        Method to set an existing bendpoint to another xy-Point

        :param bp:
        :type bp: Point
        :param index:
        :type index: int

        """
        n = len(self.bendpoints)
        if index < n:
            self.bendpoints[index] = bp

    def get_bendpoint(self, index):
        """
        Get the benpoint at the given index position (O is the first bendpoint at the source object)

        :param index:
        :type index: int
        :return: Point object
        :rtype: Point|None
        """
        n = len(self.bendpoints)
        if index < n:
            return self.bendpoints[index]
        else:
            return None

    def del_bendpoint(self, index):
        """
        Method to delete an endpoint by index position

        :param index:
        :type index: int

        """
        del self.bendpoints[index]

    def get_all_bendpoints(self):
        """
        Get the list of all bendpoints

        :return: [Point]
        """
        return self.bendpoints

    def remove_all_bendpoints(self):
        """
        Remove all bendpoint of the Connection

        """
        self.bendpoints = []

    def l_shape(self, direction=0, weight_x=0.5, weight_y=0.5):
        """
        Format the connection using a L-shape (one bendpoint, orthogonal shape)

        :param direction: 0 start with a horizontal segment, or 1 for a vertical one
        :type direction: int
        :param weight_x:  0...1 position of the bendpoint on the x-axis
        :type weight_x: float
        :param weight_y:  0...1 position of the bendpoint on the y-axis
        :type weight_y: float

        """
        self.remove_all_bendpoints()
        s_cx = self.source.cx
        s_cy = self.source.cy
        t_cx = self.target.cx
        t_cy = self.target.cy

        if direction == 0 and not self.source.is_inside(t_cx, s_cy) \
                and not self.target.is_inside(t_cx, s_cy):
            self.add_bendpoint(
                Point(t_cx + self.target.w * (0.5 - weight_x), s_cy + self.source.h * (0.5 - weight_y))
            )

        elif direction == 1 and not self.source.is_inside(s_cx, t_cy) \
                and not self.target.is_inside(s_cx, t_cy):
            self.add_bendpoint(
                Point(s_cx - self.source.w * (0.5 - weight_x),
                      t_cy + self.target.h * (0.5 - weight_y))
            )

    def s_shape(self, direction=0, weight_x=0.5, weight_y=0.5, weight2=0.5):
        """
        Format the connection using a S-shape (two bendpoints, orthogonal shape)

        :param direction: 0 starts with a horizontal segment, or 1 for a vertical one
        :type direction: int
        :param weight_x:  0...1 position of the first bendpoint on the x-axis
        :type weight_x: float
        :param weight_y:  0...1 position of the first bendpoint on the y-axis
        :type weight_y: float
        :param weight2:   0...1 position of the second bendpoint
        :type weight2: float

        """
        self.remove_all_bendpoints()
        s_xy = Point(self.source.cx, self.source.cy)
        t_xy = Point(self.target.cx, self.target.cy)

        dx = t_xy.x - s_xy.x
        dy = t_xy.y - s_xy.y

        if direction == 0:
            bp1 = Point(s_xy.x + dx * weight_x, s_xy.y - self.source.h * (0.5 - weight_y))
            bp2 = Point(bp1.x, t_xy.y - self.target.h * (0.5 - weight2))
        else:
            bp1 = Point(s_xy.x - self.source.w * (0.5 - weight_x),
                        s_xy.y + dy / 2 - self.source.h * (0.5 - weight_y) / 2)
            bp2 = Point(t_xy.x - self.target.w * (0.5 - weight2), bp1.y)

        if not self.source.is_inside(point=bp1) \
                and not self.target.is_inside(point=bp1) \
                and not self.source.is_inside(point=bp1) \
                and not self.target.is_inside(point=bp2):
            self.add_bendpoint(bp1)
            self.add_bendpoint(bp2)


class View:
    """
    Class to manage the views (diagrams) in an Archimate model

    :param name:    Name of the view
    :type name: str
    :param uuid:    Identifier of the view
    :type uuid: str
    :param desc:    Description of the view content
    :type desc: str
    :param folder:  folder path (organization) to structure view hierarchy
    :type folder: str
    :param parent:  parent Model object reference
    :type parent: Model
    :raises ArchimateConceptTypeError: Exception raised if an invalid parent object type is given
    
    :returns: View object
    :rtype: View

    """

    def __init__(self, name=None, uuid=None, desc=None, folder=None, parent=None):
        if not isinstance(parent, Model):
            raise ArchimateConceptTypeError('View class parent should be a class Model instance!')
        self.parent = parent
        self.model = parent
        self.view = self  # the view points to itself - it is the root of the nodes in the diagram
        self._uuid = _set_id(uuid)
        self.name = name
        self.desc = desc
        self.unions = []
        self.nodes_dict = defaultdict(Node)
        self.conns_dict = defaultdict(Connection)
        self._properties = {}
        self.folder = folder

    def delete(self):
        """
        Method to delete this view from its model

        """
        # Delete all nodes from the view
        _id = self.uuid
        for n in self.nodes_dict.copy().values():
            n.delete(recurse=True)
            del n
        # delete all connections from the view
        for c in self.conns_dict.copy().values():
            c.delete()
            del c
        # remove this view from the parent's dictionaries
        if _id in self.parent.views_dict:
            del self.parent.views_dict[_id]

    def add(self, ref=None, x=0, y=0, w=120, h=55, style=None, uuid=None, node_type='Element',
            label=None) -> Node:
        """
        Method to add a node in this view

        :param ref:             Identifier of the node's Element concept
        :type ref: [str|Element]
        :param x:               top-left x position of the node in the view
        :type x: int
        :param y:               top-left y position
        :type y: int
        :param w:               node's width
        :type w: int
        :param h:               node's height
        :type h: int
        :param style:           node's style (fill color, line color, font attributes) 
        :type style: Style
        :param uuid:            node's Identifier
        :type uuid: str
        :param node_type:       node's category (Element, Label or Container) 
        :type node_type: str
        :param label:           Label of a Label or Container type node
        :type label: str
        
        :return:                Node object
        :rtype: Node
        """
        n = Node(ref, x, y, w, h, uuid, node_type, label, self)
        self.nodes_dict[n.uuid] = n
        self.model.nodes_dict[n.uuid] = n
        return n

    def add_connection(self, ref=None, source=None, target=None, style=None, uuid=None):
        """
        Method to add a connection between two nodes in this view

        :param ref:             Identifier of the connnection's Relationship
        :type ref: [str|Relationship]
        :param source:          Source node of the connection (its Identifier or the node object itself)
        :type source: [str|Node]
        :param target:          Target node of the connection
        :type target: [str|Node]
        :param style:           connection's style (line width, line color, font)
        :type style: Style
        :param uuid:            Identifier of the connection
        :type uuid: str
        :return:                Connection object
        :rtype: Connection
        """
        c = Connection(ref, source, target, uuid, self)
        self.conns_dict[c.uuid] = c
        self.model.conns_dict[c.uuid] = c
        return c

    @property
    def uuid(self):
        """
        Get the identifier of the connection

        :return: Identifier
        :rtype: str
        """
        return self._uuid

    @property
    def type(self):
        """
        Get the type of the view

        :return: type 
        :rtype: str
        """
        return 'Diagram'

    @property
    def props(self):
        """
        Get the dictionary of view properties (Read-only)

        :return: Properties dictionary
        :rtype: dict
        """
        return self._properties

    def prop(self, key, value=None):
        """
        Method to get or set a view's property

        :param key:     Property key
        :type key: str
        :param value:   Property value
        :type value: str

        :return: an existing element property value if 'value' argument is None
        :rtype: str

        """
        if value is None:
            return self._properties[key] if key in self._properties else None
        else:
            self._properties[key] = value
            return value

    def remove_prop(self, key):
        """
        Method to remove a view property

        :param key:
        :type key: str

        """
        if key in self._properties:
            del self._properties[key]

    def nodes(self, elem_type=None):
        """
        Get the dictionary of nodes in the view (do not recurse for nodes in nodes)

        :param      elem_type: Archimate Element's type to filter nodes by type
        :type      elem_type: str
        :return:    [Nodes]
        :rtype: list
        """
        if elem_type is None:
            return self.nodes_dict.values()
        else:
            return [x for x in self.nodes_dict.values() if x.type == elem_type]

    def remove_folder(self):
        """
        Remove this view from the organization hierarchy

        """
        self.folder = None

    def get_or_create_node(self, elem=None, elem_type=None, x=0, y=0, w=120, h=55,
                           create_elem=False, create_node=False):
        """
        Method to get an existing node or to create a new one in this view

        :param elem:            Element object or name of the related Element concept
        :type elem: [str|Element]
        :param elem_type:       Archimate Element concept type if create_elem flag is set
        :type elem_type: str
        :param x:               top-left x position of the node
        :type x: int
        :param y:               top-left y position of the node
        :type y: int
        :param w:               node's width
        :type w: int
        :param h:               node's height
        :type h: int
        :param create_elem:     flag to create a new element with name & type if not found
        :type create_elem: bool
        :param create_node:     flag to create a new node if not found
        :type create_node: bool
        :return:                Node object or None
        :rtype: Node|None
        """
        # get the element objects
        _e = None
        if not isinstance(elem, Element):
            _e = self.model.find_elements(elem, elem_type)
            if len(_e) > 0:
                _e = _e[0]
            elif create_elem:
                _e = self.model.add(elem_type, name=elem)
            else:
                return None
        else:
            _e = elem

        # get the related node object
        n = [x for x in self.nodes() if x.ref == _e.uuid]
        if len(n) > 0:
            return n[0]
        elif create_node:
            n = self.add(ref=_e, x=x, y=y, w=w, h=h)
            return n
        else:
            return None

    def get_or_create_connection(self, rel=None, source=None, target=None, rel_type=None, name=None,
                                 create_conn=False) -> Connection:
        """
        Method to get or create a connection between two nodes in this view

        If no Parent Relationship is given, a search is performed on existing relationships with same attributes
        (type, source, target and name if given)

        :param rel:         Parent Relationship object referred by the connection or None if a new relationship is to be created
        :type rel: [str|Relationship]
        :param source:      Source node of the connection
        :type source: [str|Node]
        :param target:      Target node of the connection
        :type target: [str|Node]
        :param rel_type:    Archimate relationship type to search the parent Relationship or
        :type rel_type: str
                            used when a new relationship is to be created
        :param name:        Name of the new relationship
        :type name: str
        :param create_conn: flag to create a new connection if not found
        :type create_conn: bool
        :return:            Connection object
        :rtype: Connection
        """
        v = self
        # get the relationships
        if rel is None:
            # Search relationship having tha same type
            # and the same source, target than the source/target node's concepts
            if name is None:
                r = self.model.filter_relationships(lambda x:
                                                    rel_type == x.type and source.concept.uuid == x.source.uuid
                                                    and target.concept.uuid == x.target.uuid
                                                    )
                # r = self.find_relationships(embed_rel_type=embed_rel_type, elem=source.concept, direction='out')
            else:
                # And if provided with the same relationship name
                r = self.model.filter_relationships(lambda x:
                                                    (rel_type == x.type and source.concept.uuid == x.source.uuid
                                                     and target.concept.uuid == x.target.uuid
                                                     and x.name == name)
                                                    )
            if len(r) > 0:
                # Return the fist in the list
                r = r[0]
            else:
                # Or create a new Relationship between the source and target Element concepts
                r = self.model.add_relationship(source=source.ref, target=target.ref, rel_type=rel_type, name=name)
        elif isinstance(rel, Relationship):
            r = rel
        else:
            return None

        # Get the connection
        c = [c for c in self.conns_dict.values() if c.ref == r.uuid and c.type == rel_type]
        if len(c) > 0:
            return c[0]
        elif create_conn:
            # Don't create connection if target node is embedded into source node
            if target.parent.uuid != source.uuid:
                c = v.add_connection(r, source, target)
            return c
        else:
            return None


class Model:
    """
    Class to create a Archimate compliant models

    Note: Perspectives are not handled in the current version of this library
    
    This class define the methods and properties to create Elements, Relationships, Diagrams (Views) with Nodes and
    Connections with visual layout

    It also reads, writes or merges XML files using the Archimate Open Exchange File format

    :param name:    Model name
    :type name: str
    :param uuid:    Model Identifier
    :type uuid: str
    :param desc:    Model documentation
    :type desc: str
    
    :returns: Model object
    :rtype: Model

    """

    def __init__(self, name=None, uuid=None, desc=None):

        self._uuid = _set_id()
        self.name = name
        self.desc = desc
        self._properties = {}
        self.property_def = PropertyDefinitions()
        self.elems_dict = defaultdict(Element)
        self.rels_dict = defaultdict(Relationship)
        self.nodes_dict = defaultdict(Node)
        self.conns_dict = defaultdict(Connection)
        self.views_dict = defaultdict(View)
        self.labels_dict = defaultdict(Node)
        self.orgs = defaultdict(list)

        # with open(os.path.join(__location__, 'archimate3_Diagram.xsd'), 'r') as _f:
        #     self.schemaD = _f.read()
        # with open(os.path.join(__location__, 'archimate3_Model.xsd'), 'r') as _f:
        #     self.schemaM = _f.read()
        # with open(os.path.join(__location__, 'archimate3_View.xsd'), 'r') as _f:
        #     self.schemaV = _f.read()

    def add(self, concept_type=None, name=None, uuid=None, desc=None, folder=None):
        """
        Method to add a new Element in this model

        :param concept_type:    Archimate Element type
        :type concept_type: str
        :param name:            Element's name
        :type name: str
        :param uuid:            Element's Identifier
        :type uuid: str
        :param desc:            Element's documentation
        :type desc: str
        :param folder:          Element's organization path
        :type folder: str
        :return:                Element or View class object
        :rtype: Element|View
        """
        if concept_type == archi_type.View:
            v = View(name, uuid, desc, folder, parent=self)
            self.views_dict[v.uuid] = v
            return v
        else:
            _e = Element(concept_type, name, uuid, desc, folder, parent=self)
            self.elems_dict[_e.uuid] = _e
            return _e

    def add_relationship(self, rel_type='', source=None, target=None, uuid=None, name='', access_type=None,
                         influence_strength=None, desc=None, is_directed=None) -> Relationship:
        """
        Method to add a new Relationship between two Element objects

        :param rel_type:                Archimate relationship type
        :type rel_type: str
        :param source:                  Source Element by Identifier or by object
        :type source: [str|Element]
        :param target:                  Target Element by Identifier or by object
        :type target: [str|Element]
        :param uuid:                    Relationship Identifier
        :type uuid: str
        :param name:                    Relationship name
        :type name: str
        :param access_type:             if type is Access, type of Access (Read, Write...)
        :type access_type: str
        :param influence_strength:      if type is Influence, strength of the influence (1, 10, +,++...)
        :type influence_strength: str
        :param desc:                    Relationship documentation
        :type desc: str
        :param is_directed:             if type is Association, flag to indicated if the relationhsip is directed
        :type is_directed: bool
        :return:                        Relationship class object
        :rtype: Relationship
        """
        r = Relationship(rel_type, source, target, uuid, name, access_type, influence_strength, desc,
                         is_directed,
                         parent=self)
        self.rels_dict[r.uuid] = r
        return r

    @property
    def uuid(self):
        """
        Ge the Model Identifier

        :return: Identifer 
        :rtype: str
        """
        return self._uuid

    @property
    def type(self):
        """
        Get the type of Model
        :return: type 
        :rtype: str
        """
        return 'Model'

    @property
    def props(self):
        """
        Dictionary of model properties (read only)

        :return: properties dictionary
        :rtype: dict
        """
        return self._properties

    def prop(self, key, value=None):
        """
        Method to get or set an element's property

        :param key:     Property key
        :type key: str
        :param value:   Property value
        :type value: str
        :return: an existing element property value if 'value' argument is None
        :rtype: str
        """
        if value is None:
            return self._properties[key] if key in self._properties else None
        else:
            self._properties[key] = value
            return value

    def remove_prop(self, key):
        """
        Method to remove an element property

        :param key:
        :type key: str

        """
        if key in self._properties:
            del self._properties[key]

    @property
    def archimate(self):
        """
        Method to generate an Archimate XML Open Exchange File format structure as a string object

        Used by Model.write(filepath) method

        """
        # Basic model structure
        # Attribute starting with '@' are XML attributes, other are tags
        # Note that the order of the tags may be important, so those ones are defined by default
        # and removed afterward if empty (e.g. documentation or property tags)
        model = {
            'model': {
                '@xmlns': 'http://www.opengroup.org/xsd/archimate/3.0/',
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                '@xsi:schemaLocation': 'http://www.opengroup.org/xsd/archimate/3.0/ '
                                       'http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd',
                '@identifier': _set_id(self.uuid),  # UUID
                'name': {
                    '@xml:lang': 'en',
                    '#text': self.name,  # MODEL NAME
                },
                'documentation': {
                    '@xml:lang': 'en',
                    '#text': self.desc,  # MODEL NAME
                },
                'properties': {'property': []},
                'elements': {'element': []},  # list of elements
                'relationships': {'relationship': []},  # list of relationships
                'organizations': {'item': []},
                'propertyDefinitions': {'propertyDefinition': []},
                # 'views': {'diagrams': {'view': []}}  # list of diagrams
            }
        }
        _data = model['model']

        if self.desc is None:
            del _data['documentation']

        # Get model properties
        _property_def = dict()

        def _get_props(o, pdef):
            """
            Return the XML structure of the properties of an object

            :param o:       object with properties
            :type o: object
            :param pdef:    Property definition structure
            :type pdef: PropertyDefinitions
            :return:        dict
            :rtype: dict
            """
            p = []
            for _key, _value in o.props.items():
                if _key not in pdef:
                    pdef[_key] = 'propid-1' + str(len(pdef) + 1)
                _id = pdef[_key]
                p.append({
                    '@propertyDefinitionRef': _id,  # PROPERTY ID
                    'value': {
                        '@xml:lang': 'en',
                        '#text': _value  # PROPERTY VALUE
                    }
                })
            return p

        def _add_organization_item(path=None, ref=None):
            """
            Method to add the referred object Identifier in the XML Organization structure

            :param path:    Organization path (e.g. /View/folder1/folder2 or ['/', 'folder1', 'folder2']
            :type path: str
            :param ref:     Reference to  an Element/Relationship/View object
            :type ref: Element|View|Relationship

            """
            refs = ref
            orgs = _data['organizations']['item']

            # org_list is a path e.g. /Business/MyOrg
            if isinstance(path, str) and path[0] == "/":
                path = path[1:].split('/')
            # or is a list e.g. ["Business", "MyOrg"]
            elif not isinstance(path, list):
                path = [path]

            def find(_o, _p):
                """
                Find the location of the path in the organization structure

                :param _o:  organization structure
                :param _p:  path to match
                :return:    tuple (organization level where the path match, unmatch part of the path)
                            or (None, None) if no match
                """
                if len(_o) == 0:
                    return _o, _p
                for x in _o:
                    if 'label' not in x:
                        continue
                    if _p[0] != x['label']['#text']:
                        continue
                    # get next match
                    if len(_p) <= 1:
                        return [x], _p
                    _p.pop(0)
                    if not isinstance(x['item'], list):
                        x['item'] = [x['item']]
                    res, _ = find([x['item']], _p)
                    if res is None:
                        return x, _p
                return None, None

            org, nxt_path = find(orgs, path)

            # if no match, add to the orgs root
            if org is None and nxt_path is None:
                item = OrgItem(label=path[0], items=[], item_refs=refs).item
                if 'item' not in orgs:
                    orgs.append(item)
                else:
                    orgs['item'].append(item)
                return

            p = []
            item = None

            # Else create the item object that correspond to the remaining path to cover
            for o in reversed(nxt_path):
                item = OrgItem(label=o, items=p, item_refs=refs).item
                refs = None
                p = [item]
            # And add to the organization tree
            if item is not None:
                if 'item' not in org:
                    org.append(item)
                else:
                    o = org['item'] if isinstance(org['item'], list) else [org['item']]
                    for i in o:
                        if 'label' in i and i['label']['#text'] == nxt_path[0]:
                            i['item'] += item['item']
                            return
                    o.append(item)

        # check if model has properties
        if len(self.props) > 0:
            _data['properties'] = dict(property=[])
            _data['properties']['property'] = _get_props(self, _property_def)

        # Add all Elements
        for _e in self.elems_dict.values():
            _e_data = {
                '@identifier': _set_id(_e.uuid),  # UUID
                '@xsi:type': _e.type,  # ELEMENT TYPE
                'name': {
                    '@xml:lang': 'en',
                    '#text': _e.name,  # ELEMENT NAME
                },
                'documentation': {
                    '@xml:lang': 'en',
                    '#text': _e.desc
                }
            }
            if _e.desc is None:
                del _e_data['documentation']

            if _e.folder is not None:
                _add_organization_item(_e.folder, _e.uuid)
            if len(_e.props) > 0:
                _e_data['properties'] = dict(property=[])
                _e_data['properties']['property'] = _get_props(_e, _property_def)

            _data['elements']['element'].append(_e_data)

        # Add all Relationships
        for _r in self.rels_dict.values():
            _r_data = {
                '@identifier': _set_id(_r.uuid),  # RELATIONSHIP UUID
                '@source': _r.source.uuid,  # SOURCE UUID
                '@target': _r.target.uuid,  # TARGET UUID
                '@xsi:type': _r.type,  # RELATIONSHIP TYPE
                'name': {
                    '@xml:lang': 'en',
                    '#text': _r.name,  # ELEMENT NAME
                },
                'documentation': {
                    '@xml:lang': 'en',
                    '#text': _r.desc
                }
            }

            if _r.desc is None:
                del _r_data['documentation']

            # Add special relationship type attributes
            if _r.access_type is not None:
                _r_data['@accessType'] = _r.access_type

            if _r.is_directed is not None:
                _r_data['@isDirected'] = str(_r.is_directed).lower()

            if _r.influence_strength is not None:
                _r_data['@influenceStrenght'] = str(_r.influence_strength)

            if _r.folder is not None:
                _add_organization_item(_r.folder, _r.uuid)

            # Add properties
            if len(_r.props) > 0:
                _r_data['properties'] = dict(property=[])
                _r_data['properties']['property'] = _get_props(_r, _property_def)
            _data['relationships']['relationship'].append(_r_data)

        # Add all views
        # create root xml structure
        if len(self.views_dict) > 0:
            _data['views'] = dict(diagrams=dict())
            _data['views']['diagrams'] = dict(view=list())

        # Add each view
        for _v in self.views_dict.values():
            _v_data = {
                '@identifier': _v.uuid,
                '@xsi:type': 'Diagram',
                'name': {
                    '@xml:lang': 'en',
                    '#text': _v.name,
                },
                'documentation': {
                    '@xml:lang': 'en',
                    '#text': _v.desc
                },
                'properties': {'property': []},
                'node': [],  # LIST OF NODES
                'connection': [],  # LIST OF CONNECTIONS
            }
            if _v.desc is None:
                del _v_data['documentation']

            # Add all nodes
            def _add_node(n: Node):
                """
                Local function to add nodes in xml view structure

                :param n: Node object
                :return: xml data structure
                """
                _n_data = {
                    '@identifier': n.uuid,  # NODE UUID
                    '@elementRef': n.ref,  # ELEMENT UUID
                    '@xsi:type': n.cat,
                    '@x': str(n.x),  # X CENTER POSITION
                    '@y': str(n.y),  # Y CENTER POSITION
                    '@w': str(n.w),  # ELEMENT WIDTH
                    '@h': str(n.h),  # ELEMENT HEIGHT
                    # 'style': None,  # STYLE
                    # 'node': self.node,  # EMBEDDED NODES
                }

                # Special setting for Labels & Containers that should not have element reference attributes
                if n.cat != 'Element':
                    del _n_data['@elementRef']
                    _n_data['label'] = {'@xml:lang': 'en', '#text': n.label}

                # set style
                _s = Style()
                _s.fill_color = n.fill_color
                _s.line_color = n.line_color
                _s.opacity = n.opacity
                _s.font_color = n.font_color
                _s.font_size = n.font_size
                _s.font_name = n.font_name
                _n_data['style'] = _s.data

                # Recurse for all sub-nodes
                if len(n.nodes()) > 0:
                    _n_data['node'] = list()
                    for sub_node in n.nodes():
                        _n_data['node'].append(_add_node(sub_node))

                # finally, return a node structure
                return _n_data

            # Add nodes in view xml structure
            for _n in _v.nodes():
                _v_data['node'].append(_add_node(_n))

            # Add all connections
            for _c in _v.conns_dict.values():
                _c_data = {
                    '@identifier': _c.uuid,  # CONNECTION UUID
                    '@relationshipRef': _c.ref,  # RELATIONSHIP UUID
                    '@xsi:type': 'Relationship',
                    '@source': _c.source.uuid,  # SOURCE UUID
                    '@target': _c.target.uuid,  # TARGET UUID
                    'style': None
                    # 'bendpoint': None  # BENDPOINTS ABSOLUTE X,Y
                }

                # Add endpoints
                bps = _c.get_all_bendpoints()
                if len(bps) > 0:
                    _c_data['bendpoint'] = list()
                    for bp in bps:
                        _c_data['bendpoint'].append(
                            {
                                '@x': str(int(bp.x)),
                                '@y': str(int(bp.y))
                            }
                        )

                # set style
                s = Style()
                s.line_color = _c.line_color
                s.font_color = _c.font_color
                s.font_size = _c.font_size
                s.font_name = _c.font_name
                _c_data['style'] = s.data

                _v_data['connection'].append(_c_data)

            # Add into organization structure
            if _v.folder is not None:
                _add_organization_item(_v.folder, _v.uuid)
            # add properties
            if len(_v.props) > 0:
                _v_data['properties'] = dict(property=[])
            _v_data['properties']['property'] = _get_props(self, _property_def)
            # Add view in model structure
            _data['views']['diagrams']['view'].append(_v_data)

        # Finalize model structure
        # Add property definitions to the model
        for k, v in _property_def.items():
            _data['propertyDefinitions']['propertyDefinition'].append({
                '@identifier': v,
                '@type': 'string',
                'name': k
            })

        # Remove all empty tags
        if len(_data['properties']['property']) == 0:
            del _data['properties']

        if len(_data['elements']['element']) == 0 and "relationships" in _data:
            del _data['elements']

        if len(_data['relationships']['relationship']) == 0 and "relationships" in _data:
            del _data['relationships']

        if 'organizations' in _data and len(_data['organizations']['item']) == 0:
            del _data['organizations']
            #
        if 'views' in _data and \
                ('view' not in _data['views']['diagrams'] or len(_data['views']['diagrams']['view']) == 0):
            del _data['views']

        if 'views' in _data and 'view' in _data['views']['diagrams']:
            for v in _data['views']['diagrams']['view']:
                if 'properties' in v and len(v['properties']['property']) == 0:
                    del v['properties']

        if len(_data['propertyDefinitions']['propertyDefinition']) == 0:
            del _data['propertyDefinitions']

        if 'organizations' in _data and len(_data['organizations']['item']) == 0:
            del _data['organizations']

        # Convert the xml structure into XML string data
        try:
            xml_str = xmltodict.unparse(model, pretty=True)
        except Exception as _err:
            log.error(_err)
            # yaml.dump(self.xml, open('xml_error.yaml', 'w'), Dumper=yaml.Dumper)
            return None

        return xml_str

    @archimate.setter
    def archimate(self, xml_data):
        """
        Merge / initialize the model from XML Archimate OEF data

        Used by Model.read(filepath) or Model.merge(filepath) methods

        :param xml_data:
        :type xml_data: str

        """

        def _get_properties(model, o, obj):
            """
            Local function to extract properties from XML data

            :param model:   model object
            :param o:       xml properties tag with key/values pairs
            :param obj:     target Element/Relationship/View/Model object in the model

            """
            if 'properties' in o and o['properties'] is not None:
                props = o['properties']
                if isinstance(props, dict):
                    props = [props]
                for p in props:
                    if isinstance(p['property'], dict):
                        p['property'] = [p['property']]
                    for q in p['property']:
                        if q['value'] is not None:
                            key = model.property_def.propertyDefinitions[q['@propertyDefinitionRef']]
                            value = _get_str_attrib('value', q)
                            obj.prop(key, value)

        def _update_keys(old_key, new_key, d):
            """
            local function to update a key in a complex dict of dict

            :param old_key:
            :param new_key:
            :param d:

            """
            if isinstance(d, dict):
                if old_key in d:
                    d[new_key] = d[old_key]
                    del d[old_key]
                for key in d:
                    _update_keys(old_key, new_key, d[key])

        # Get merge option
        merge_flg = ('@merge' in xml_data)
        # Initialize the model
        m = xml_data["model"]

        # Extract name (skipping language attributes from the tag)
        self.name = _get_str_attrib('name', m)

        # Get property definitions (property keys translation)
        if 'propertyDefinitions' in m:
            pd = m['propertyDefinitions']['propertyDefinition']
            if not isinstance(pd, list):
                pd = [pd]
            for k in pd:
                if merge_flg and k['@identifier'] in self.property_def.propertyDefinitions \
                        and k['name'] != self.property_def.propertyDefinitions[k['@identifier']]:
                    # When merging, key definitions can conflit and need resolution
                    new_key = self.property_def.add(k['@identifier'])
                    _update_keys(k['@identifier'], new_key, xml_data)
                    k['@identifier'] = new_key

                if k['@identifier'] not in self.property_def.propertyDefinitions:
                    self.property_def.propertyDefinitions[k['@identifier']] = k['name']
                    self.property_def.propertyDefinitionsData.append(k)

        # Get Model properties
        _get_properties(self, m, self)

        # get elements in the model
        if 'elements' in m and m['elements'] is not None:
            elems = m['elements']['element'] if isinstance(m['elements']['element'], list) else [
                m['elements']['element']]
            for e in elems:
                # check whether to create or merge element
                _uuid = e['@identifier']
                if merge_flg and _uuid in self.elems_dict:
                    elem = self.elems_dict[_uuid]
                    elem.name = e['name']['#text']
                    elem.desc = e['documentation']['#text'] if ('documentation' in e
                                                                and '#text' in e['documentation']) else None
                    _get_properties(self, e, elem)
                    # merge completed, loop on next element
                else:
                    # else create a new element
                    elem = self.add(
                        name=_get_str_attrib('name', e),
                        concept_type=e['@xsi:type'],
                        uuid=e['@identifier'],
                        desc=_get_str_attrib('documentation', e)
                    )

                # Get element properties
                _get_properties(self, e, elem)

                # Add the element in the dictionary
                self.elems_dict[elem.uuid] = elem

        # get relationships
        if 'relationships' in m:
            rels = m['relationships']['relationship']
            if not isinstance(rels, list):
                rels = [rels]
            for r in rels:
                # check whether to create or merge element
                _uuid = r['@identifier']
                if merge_flg and _uuid in self.rels_dict:
                    rel = self.rels_dict[_uuid]
                    rel.name = _get_str_attrib('name', r)
                    rel.desc = _get_str_attrib('documentation', r)
                    _get_properties(self, r, rel)
                    # merge completed, loop on next element
                else:
                    # else create a new element
                    rel = self.add_relationship(
                        source=r['@source'],
                        target=r['@target'],
                        rel_type=r['@xsi:type'],
                        uuid=r['@identifier'],
                        name=_get_str_attrib('name', r),
                        access_type=['@accessType'] if ('accessType' in r) else None,
                        influence_strength=['@modifier'] if ('modifier' in r) else None,
                        desc=_get_str_attrib('documentation', r),
                        is_directed=['@isDirected'] if ('isDirected' in r) else None,
                    )
                    _get_properties(self, r, rel)
                    self.rels_dict[rel.uuid] = rel

        # Get views
        if 'views' in m:
            views = m['views']['diagrams']['view']
            if not isinstance(views, list):
                views = [views]
            for v in views:
                _uuid = v['@identifier']
                if merge_flg:
                    if _uuid in self.views_dict:
                        # Merged view replaces the original one
                        _view = self.views_dict[_uuid]
                        _view.delete()

                _v = self.add(archi_type.View,
                              name=_get_str_attrib('name', v),
                              uuid=_uuid,
                              desc=_get_str_attrib('documentation', v)
                              )

                _get_properties(self, v, _v)

                # Get recursively nodes
                def _add_node(o, data_node):
                    """
                    Local recursive function to add a node into a view or another node from the XML data

                    :param o:           target object in the model (View or Node)
                    :param data_node:   xml data about node and embded nodes
                    :return: Node

                    """
                    data_node = [data_node] if isinstance(data_node, dict) else data_node
                    for n_data in data_node:
                        _uuid = n_data['@identifier']
                        if merge_flg and _uuid in self.nodes_dict:
                            _uuid = None
                        if '@elementRef' in n_data:
                            _n = o.add(
                                uuid=_uuid,
                                ref=n_data['@elementRef'],
                                x=n_data['@x'],
                                y=n_data['@y'],
                                w=n_data['@w'],
                                h=n_data['@h'],
                                style=n_data['style'] if 'style' in n_data else None
                            )
                        else:
                            _n = o.add(
                                uuid=_uuid,
                                ref=None,
                                x=n_data['@x'],
                                y=n_data['@y'],
                                w=n_data['@w'],
                                h=n_data['@h'],
                                style=n_data['style'] if 'style' in n_data else None,
                                node_type=n_data['@xsi:type'],
                                label=_get_str_attrib('label', n_data)
                            )

                        if 'node' in n_data:
                            nodes = n_data['node']
                            nodes = [nodes] if isinstance(nodes, dict) else nodes
                            for sub_node in nodes:
                                _sub_node = _add_node(_n, sub_node)
                                _n.nodes_dict[_sub_node.uuid] = _sub_node
                                o.model.nodes_dict[_sub_node.uuid] = _sub_node

                        o.model.nodes_dict[n_data['@identifier']] = _n
                        o.nodes_dict[n_data['@identifier']] = _n
                        return _n

                # Get Nodes in view
                if 'node' in v:
                    nodes = v['node']
                    if isinstance(nodes, dict):
                        nodes = [nodes]
                    for n in nodes:
                        _add_node(_v, n)

                # Get Connections
                if 'connection' in v:
                    conns = v['connection'] if isinstance(v['connection'], list) else [v['connection']]
                    for c in conns:
                        _uuid = c['@identifier']
                        if merge_flg and _uuid in c['@identifier']:
                            _uuid = None
                        _c = _v.add_connection(
                            ref=c['@relationshipRef'],
                            source=c['@source'],
                            target=c["@target"],
                            style=c["style"] if 'style' in c else None,
                            uuid=_uuid
                        )

                        if 'bendpoint' in c:
                            bps = c['bendpoint'] if isinstance(c['bendpoint'], list) else [c['bendpoint']]
                            for bp in bps:
                                _c.add_bendpoint(Point(bp['@x'], bp['@y']))
                            self.conns_dict[c['@identifier']] = _c

                # Add view in the model
                self.views_dict[_v.uuid] = _v

        # # Get organizations
        if 'organizations' in m:
            _orgs = m['organizations']['item']
            if isinstance(_orgs, dict):
                _orgs = [_orgs]

            def _walk_orgs(_orgs, path=None):
                """
                Local recursive function to walk through the xml organization structure
                and assign folder path to referred View/Element/Relationship objects

                :param _orgs:
                :param path:

                """
                if path is None:
                    path = []
                if isinstance(_orgs, dict):
                    _orgs = [_orgs]
                prev_path = path.copy()
                for o in _orgs:
                    path = prev_path.copy()
                    if 'label' in o:
                        label = _get_str_attrib('label', o)
                        path.append(label)
                    if 'item' in o:
                        _item = o['item']
                        if isinstance(_item, dict):
                            _item = [_item]
                        for i in _item:
                            if '@identifierRef' in i:
                                uuid = i['@identifierRef']
                                folder = '/' + '/'.join(path)
                                if uuid in self.views_dict:
                                    self.views_dict[uuid].folder = folder
                                elif uuid in self.elems_dict:
                                    self.elems_dict[uuid].folder = folder
                                elif uuid in self.rels_dict:
                                    self.rels_dict[uuid].folder = folder
                                self.orgs[folder].append(uuid)
                            else:
                                # prev_path = path.copy()
                                # path = walk_orgs(i, path)
                                _walk_orgs(i, path)

                return path

            # Extract organization structure from the model
            _walk_orgs(_orgs, None)

    @property
    def aml(self):
        """
        Unused future Property - is write-only

        """
        return None

    @aml.setter
    def aml(self, data):
        """
        Get an ARIS AML data structure in this model

        :param data:
        :type data: str

        """
        # To be implemented from AMLparse refactoring
        pass

    @property
    def views(self):
        """
        Get the list of views in this model

        :return: [View]
        :rtype: list
        """
        return self.views_dict.values()

    @property
    def elements(self):
        """
        Get the list of Elements in this model

        :return: [Element]
        :rtype: list
        """
        return self.elems_dict.values()

    @property
    def relationships(self):
        """
        Get the list of Relationships in this Model

        :return: [Relationship]
        :rtype: list
         """
        return self.rels_dict.values()

    def write(self, file_path=None):
        """
        Method to write the file_path to an Archimate file

        :param file_path:
        :type file_path: str
        :return: xml data structure
        :rtype: str
        """

        if file_path is not None:
            try:
                with open(file_path, 'w', encoding='utf-8') as fd:
                    if self.archimate is not None:
                        fd.write(self.archimate)
                    else:
                        log.error('Empty content due to error - No file written')
            except IOError:
                log.error(f'{__mod__} {self.__class__.__name__}.write: Cannot write to file "{file_path}')
        return self.archimate

    def read(self, file_path, reader=Reader.ARCHIMATE):
        """
        Method to read an Archimate file

        :param file_path:
        :type file_path: str
        :param reader: Reader option (default = ARCHIMATE OEF format, or ARIS)
        :type reader: Reader

        """
        try:
            with open(file_path, 'r', encoding='utf-8') as fd:
                _data = xmltodict.parse(fd.read())
        except IOError:
            log.error(f"{__mod__} {self.__class__.__name__}.read: Cannot open or read file '{file_path}'")
            sys.exit(1)
        if "model" not in _data:
            log.error(
                f"{__mod__} {self.__class__.__name__}.read: File '{file_path}' is not a valid Archimate OEF file")
            sys.exit(1)
        if reader == Reader.ARCHIMATE:
            self.archimate = _data
        elif reader == Reader.AML:
            self.aml = _data

    def merge(self, file_path):
        """
        Method to merge an Archimate file into this model

        :param file_path:
        :type file_path: str

        """
        try:
            with open(file_path, 'r', encoding='utf-8') as fd:
                _data = xmltodict.parse(fd.read())
        except IOError:
            log.error(f"{__mod__} {self.__class__.__name__}.merge: Cannot open or read file '{file_path}'")
            sys.exit(1)
        if "model" not in _data:
            log.error(
                f"{__mod__} {self.__class__.__name__}.merge: File '{file_path}' is not a valid Archimate OEF file")
            sys.exit(1)

        _data['@merge'] = 'true'
        self.archimate = _data

    def filter_elements(self, fct):
        """
        Method to filter Elements

        :param fct: callback (lambda) function with filtering criteria
        :type fct: function
        :return: list of Elements
        :rtype: list
        """
        return [x for x in self.elems_dict.values() if fct(x)]

    def find_elements(self, name=None, elem_type=None):
        """
        Method to find elements by name or type or both

        :param name:        name criteria
        :type name: str
        :param elem_type:   elem_type criteria
        :type elem_type: str
        :return: list(Element)
        :rtype: list
        """
        if name and not elem_type:
            return [e for e in self.elems_dict.values() if e.name == name]
        elif elem_type and not name:
            return [e for e in self.elems_dict.values() if e.type == elem_type]
        elif elem_type and name:
            return [e for e in self.elems_dict.values() if e.name == name and e.type == elem_type]
        else:
            return self.elems_dict.values()

    def find_relationships(self, rel_type, elem, direction='both'):
        """
        Find all relationships of a list of elements

        :param rel_type: type of relationship tp search for
        :type rel_type: str
        :param elem: an element with relationships
        :type elem: Element
        :param direction: data direction ['in_rels', 'out_rels', 'both' | None]
        :type direction: str
        :return: [Relationship]
        :rtype: list


        """
        if elem is None:
            return None
        result = []
        direction = direction.lower()
        if rel_type is not None:
            if 'in' in direction or 'both' in direction:
                result += [r for r in self.rels_dict.values() if r.target.uuid == elem.uuid and rel_type == r.type]
            if 'out' in direction or 'both' in direction:
                result += [r for r in self.rels_dict.values() if r.source.uuid == elem.uuid and rel_type == r.type]
            return result
        else:
            if 'in' in direction or 'both' in direction:
                result += [r for r in self.rels_dict.values() if r.target.uuid == elem.uuid]
            if 'out' in direction or 'both' in direction:
                result += [r for r in self.rels_dict.values() if r.source.uuid == elem.uuid]
            return result

    def filter_relationships(self, fct):
        """
        Method to find relationhips by providing a callback function with criteria

        :param fct: callback function
        :type fct: function
        :return: list(Relationships)
        :rtype: list
        """
        return [r for r in self.rels_dict.values() if fct(r)]

    def filter_views(self, fct):
        """
        Method to find views by providing a callback function with criteria

        :param fct: callback function
        :type fct: function
        :return: list(Views)
        :rtype: list
        """
        return [v for v in self.views_dict.values() if fct(v)]

    def find_views(self, name):
        """
        Method to find views by name

        :param name:
        :type name: str
        :return: list(View)
        :rtype: list
        """
        return [x for x in self.views_dict.values() if x.name == name]

    def get_or_create_element(self, elem_type: str, elem: str, create_elem=False):
        """
        Method to get an Element by name or create one if not existing

        :param elem_type:   Archimate type of the element
        :type elem_type: str
        :param elem:        name of the Element
        :type elem: str
        :param create_elem: if True,  create a new Element if not found
        :type create_elem: bool
        :return: Element object
        :rtype: Element
        """
        if elem == '' or elem is None:
            return None
        e = self.find_elements(elem, elem_type)
        if len(e) > 0:
            return e[0]
        elif create_elem:
            return self.add(name=elem, concept_type=elem_type)
        else:
            return None

    def get_or_create_relationship(self, rel_type: str, name: str, source, target, create_rel=False,
                                   access_type=None,
                                   influence_strength=None, desc=None, is_directed=None):
        """
        Method to get a Relationship by source/target/type and/or by name or create one if not found

        :param rel_type:                Archimate type of the relationship
        :type rel_type: str
        :param name:                    name of the relationships
        :type name: str
        :param source:                  Source Element or Identifier of the Element
        :type source: [str|Element]
        :param target:                  Target Element or Identifier of the Element
        :type target: [str|Element]
        :param create_rel:              if True, create a new relationship if not found
        :type create_rel: bool
        :param access_type:             if type is Access, and creat_rel is true, set the access type
        :type access_type: str
        :param influence_strength:      if type is Influence, and creat_rel is true, set the strenght
        :type influence_strength: str
        :param desc:                    relationship description        
        :type desc: str
        :param is_directed:             if type is Association, and creat_rel is true, set the direction flag
        :type is_directed: bool
        :return:                        Relationship object
        :rtype: Relationship
        """
        if source is None or target is None:
            return None

        # Relations are created between Elements, not Nodes
        if isinstance(source, Node):
            source = source.concept
        if isinstance(target, Node):
            target = target.concept

        r = self.filter_relationships(lambda x: (x.type == rel_type
                                                 and x.source.uuid == source.uuid
                                                 and x.target.uuid == target.uuid))
        if len(r) > 0:
            return r[0]
        if create_rel:
            return self.add_relationship(source=source.uuid, target=target.uuid, rel_type=rel_type, name=name,
                                         access_type=access_type, influence_strength=influence_strength, desc=desc,
                                         is_directed=is_directed)
        else:
            return None

    def get_or_create_view(self, view, create_view=False):
        """
        Method to get or create a view by name

        :param view:        View name   
        :type view: str
        :param create_view: if True, create a view if not found
        :type create_view: bool
        :return:            View object
        :rtype: View
        """
        if isinstance(view, str):
            v = self.find_views(view)
            if len(v) > 0:
                v = v[0]
            elif create_view:
                v = self.add(archi_type.View, view)
            else:
                return None
        else:
            v = view

    def embed_props(self, remove_props=False):
        """
        Method to embed properties of each view, element, relationship into their description attribute
        as a stringified json tag

        Some tools like Aris are not configured to managed concept's properties,
        so we embed the properties before exporting the model there

        """

        def _embed(o):
            """
            Local function to embed the properties of an object

            :param o:   Method/View/Element/Relationship object

            """
            if isinstance(o, Relationship):
                # For relationship we embed all properties in a single one called 'Identifier'
                # to cope with ARIS limitation
                p = {'name': o.name, 'documentation': o.desc}
                if o.type == archi_type.Association:
                    p['isDirected'] = o.is_directed
                elif o.type == archi_type.Access:
                    p['access'] = o.access_type
                elif o.type == archi_type.Influence:
                    p['influence_strength'] = o.influence_strength
                for key, val in o.props.items():
                    p[key] = val
                for x in o.props.copy():
                    o.remove_prop(x)
                o.prop('Identifier', '#properties = ' + json.dumps(p, indent=2) + '\n')

            elif o.props != {} and (isinstance(o, View) or isinstance(o, Element) or isinstance(o, Model)):
                # Else we embed properties art the end of the description field
                pat = r'#properties\s*=\s*(\{[\s\S]*\})'
                # Get the concept description and remove any existing embedded properties tag
                desc = '' if o.desc is None else re.sub(pat, '', o.desc, re.DOTALL)
                # add the properties tag in the concept desc
                desc += desc.strip(' \n') + '\n\n#properties = ' + json.dumps(o.props, indent=2) + '\n'
                o.desc = desc
                if remove_props:
                    for x in o.props.copy():
                        o.remove_prop(x)

        _embed(self)
        for v in self.views_dict.values():
            _embed(v)
        for e in self.elems_dict.values():
            _embed(e)
        for r in self.rels_dict.values():
            _embed(r)

    def expand_props(self, clean_doc=True):
        """
        Method to expand model's concepts desc attribute properties tag into concept's properties

        """

        def _expand(o):
            if isinstance(o, Relationship):
                if o.prop('Identifier') is not None:
                    pat = r'#properties\s*=\s*(\{[\s\S]*\})'
                    p = o.prop('Identifier')
                    match = re.findall(pat, p, re.M)
                    p = json.loads(match[0])
                    o.remove_prop('Identifier')
                    if p is not None:
                        o.name = p['name'] if 'name' in p else None
                        o.desc = p['documentation'] if 'documentation' in p else None
                        if 'isDirected' in p and o.type == archi_type.Association:
                            o.is_directed = True if p['isDirected'].lower() == 'true' else False
                        if 'access' in p and o.type == archi_type.Access:
                            o.access_type = p['access']
                        if 'influence_strength' in p and o.type == archi_type.Influence:
                            o.influence_strength = p['influence_strength']
                        for key, val in p.items():
                            o.prop(key, val)

            elif isinstance(o, View) or isinstance(o, Element) or isinstance(o, Model):
                # Get the concept description and remove any existing embedded properties tag
                if o.desc is not None:
                    pat = r'#properties\s*=\s*(\{[\s\S]*\})'
                    match = re.findall(pat, o.desc, re.M)
                    if len(match) == 1:
                        # get the properties
                        props = json.loads(match[0])
                        # and clean up the desc attribute
                        o.desc = re.sub(pat, '', o.desc, re.DOTALL).strip(' \n')
                        for key, val in props.items():
                            o.prop(key, val)
                        if clean_doc:
                            o.desc = None if o.desc is None else re.sub(pat, '', o.desc, re.DOTALL)

        _expand(self)
        for v in self.views_dict.values():
            _expand(v)
        for e in self.elems_dict.values():
            _expand(e)
        for r in self.rels_dict.values():
            _expand(r)

    def check_invalid_conn(self):
        """
        Method to check the validity of a list of connections

        """
        for c in self.conns_dict.values():
            self.check_connection(c)

    def check_connection(self, c):
        """
        Method to check the validity of a single connection

        :param c:   Connection object
        :type c:    Connection
        :return:    True if the connection is valid
        :rtype:     boolean
        """

        _ok = True
        # check connections with unknown references
        if c._ref not in self.rels_dict:
            log.error(f'Orphan connection {c.uuid} to unknown relationship {c.ref}')
            _ok = False
        # check existence of the source & target nodes
        if c._source not in self.nodes_dict:
            log.error(f'Connection {c.uuid} has orphan source node {c._source}')
            _ok = False
        if c._target not in self.nodes_dict:
            log.error(f'Connection {c.uuid} has orphan target node {c._target}')
            _ok = False
        # Check source / target are nodes, not views
        if isinstance(c.target, View):
            log.error(f'Connection {c.uuid} has a view {c.target.name} as source node')
            _ok = False
        if isinstance(c.source, View):
            log.error(f'Connection {c.uuid} has a view {c.source.name} as source node')
            _ok = False
        if c.source is not None:
            if c.source._ref != c.concept._source:
                log.error(f'Connection {c.uuid} has a reference to its source Element which is not '
                          'the reference of the relationship source Element')
            _ok = False
        if c.target is not None:
            if c.target._ref != c.concept._target:
                log.error(f'Connection {c.uuid} has a reference to its target Element which is not '
                          'the reference of the relationship target Element')
            _ok = False

        return _ok


# Dictionary of valid Archimate relationships
allowed_relationships = {}
ARIS_type_map = {}
relationship_keys = {}
archi_category = {}


class AccessType:
    """
    Enumeration of Access Relationship types
    """

    def __init__(self):
        self.Access = 'Access'
        self.Read = 'Read'
        self.Write = 'Write'
        self.ReadWrite = 'ReadWrite'


access_type = AccessType()

influenceStrength = {'+': '+', '++': '++', '-': '-', '--': '--', '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
                     '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': '10'},


class ArchiTypes:
    """
    Enumeration of Archimate Element & Relationships types
    """

    def __init__(self):
        # Business Layer
        self.BusinessActor = "BusinessActor"
        self.BusinessRole = "BusinessRole"
        self.BusinessCollaboration = "BusinessCollaboration"
        self.BusinessInterface = "BusinessInterface"
        self.BusinessProcess = "BusinessProcess"
        self.BusinessFunction = "BusinessFunction"
        self.BusinessInteraction = "BusinessInteraction"
        self.BusinessEvent = "BusinessEvent"
        self.BusinessService = "BusinessService"
        self.BusinessObject = "BusinessObject"
        self.Contract = "Contract"
        self.Representation = "Representation"
        self.Product = "Product"

        # Application Layer

        self.ApplicationComponent = "ApplicationComponent"
        self.ApplicationInterface = "ApplicationInterface"
        self.ApplicationCollaboration = "ApplicationCollaboration"
        self.ApplicationFunction = "ApplicationFunction"
        self.ApplicationProcess = "ApplicationProcess"
        self.ApplicationEvent = "ApplicationEvent"
        self.ApplicationService = "ApplicationService"
        self.DataObject = "DataObject"

        # Technology layer

        self.Node = "Node"
        self.Device = "Device"
        self.Path = "Path"
        self.CommunicationNetwork = "CommunicationNetwork"
        self.SystemSoftware = "SystemSoftware"
        self.TechnologyCollaboration = "TechnologyCollaboration"
        self.TechnologyInterface = "TechnologyInterface"
        self.TechnologyFunction = "TechnologyFunction"
        self.TechnologyProcess = "TechnologyProcess"
        self.TechnologyInteraction = "TechnologyInteraction"
        self.TechnologyEvent = "TechnologyEvent"
        self.TechnologyService = "TechnologyService"
        self.Artifact = "Artifact"

        # Physical elements

        self.Equipment = "Equipment"
        self.Facility = "Facility"
        self.DistributionNetwork = "DistributionNetwork"
        self.Material = "Material"

        #  Motivation

        self.Stakeholder = "Stakeholder"
        self.Driver = "Driver"
        self.Assessment = "Assessment"
        self.Goal = "Goal"
        self.Outcome = "Outcome"
        self.Principle = "Principle"
        self.Requirement = "Requirement"
        self.Constraint = "Constraint"
        self.Meaning = "Meaning"
        self.Value = "Value"

        # Strategy

        self.Resource = "Resource"
        self.Capability = "Capability"
        self.CourseOfAction = "CourseOfAction"

        # Implementation & Migration

        self.WorkPackage = "WorkPackage"
        self.Deliverable = "Deliverable"
        self.ImplementationEvent = "ImplementationEvent"
        self.Plateau = "Plateau"
        self.Gap = "Gap"

        # Other

        self.Grouping = "Grouping"
        self.Location = "Location"

        # Junction

        self.Junction = "Junction"
        self.OrJunction = "OrJunction"
        self.AndJunction = "AndJunction"

        # Relationships

        self.Association = "Association"
        self.Assignment = "Assignment"
        self.Realization = "Realization"
        self.Serving = "Serving"
        self.Composition = "Composition"
        self.Aggregation = "Aggregation"
        self.Access = "Access"
        self.Influence = "Influence"
        self.Triggering = "Triggering"
        self.Flow = "Flow"
        self.Specialization = "Specialization"

        # Special
        self.View = "View"


archi_type = ArchiTypes()


class ArchimateRelationshipError(Exception):
    pass


class ArchimateConceptTypeError(Exception):
    pass


def check_valid_relationship(rel_type, source_type, target_type):
    """
    Check if a relationship is used according to Archimate language or raise an exception

    :param rel_type:        relationship type
    :type rel_type: str
    :param source_type:     source concept type
    :type source_type: str
    :param target_type:     target concept type
    :type target_type: str

    :raises ArchimateConceptTypeError: Exception raised on invalid object Archimate type
    :raises ArchimateRelationshipError: Exception raised on invalid relationship between the source and target parent elements

    """
    if not hasattr(archi_type, rel_type) or archi_category[rel_type] != 'Relationship':
        raise ArchimateConceptTypeError(f"Invalid Archimate Relationship Concept type '{rel_type}'")
    if not hasattr(archi_type, source_type) or archi_category[source_type] == 'Relationship':
        raise ArchimateConceptTypeError(f"Invalid Archimate Source Concept type '{source_type}'")
    if not hasattr(archi_type, target_type) or archi_category[target_type] == 'Relationship':
        raise ArchimateConceptTypeError(f"Invalid Archimate Target Concept type '{target_type}'")

    if not relationship_keys[rel_type] in allowed_relationships[source_type][target_type]:
        raise ArchimateRelationshipError(
            f"Invalid Relationship type '{rel_type}' from '{source_type}' and '{target_type}' ")


def get_default_rel_type(source_type, target_type):
    """
    Return the default valid relationship between two element types

    :param source_type:
    :type source_type: str
    :param target_type:
    :type target_type: str
    :return: default relationship type
    :rtype: str
    """
    if not hasattr(archi_type, source_type) or archi_category[source_type] == 'Relationship':
        raise ArchimateConceptTypeError(f"Invalid Archimate Source Concept type '{source_type}'")
    if not hasattr(archi_type, target_type) or archi_category[target_type] == 'Relationship':
        raise ArchimateConceptTypeError(f"Invalid Archimate Target Concept type '{target_type}'")
    rels = allowed_relationships[source_type][target_type]
    if len(rels) > 0:
        # TODO Define default rel type for embedding - next statement does not work
        return [k for k, v in relationship_keys.items() if v == rels[0]][0]


# Fetch model parameters during initialization of the module
if allowed_relationships == {}:
    data = None
    try:
        data = yaml.load(open(os.path.join(os.path.sep, __location__, "checker_rules.yml"), "r"), Loader=yaml.Loader)
        metamodel_valid_rels = data['metamodel']['relationships']
        metamodel_valid_elems = data['metamodel']['elements']
        allowed_relationships = data['archimate_rels']
        ARIS_type_map = data['ARIS_type_map']
        relationship_keys = data['relationship_keys']
        archi_category = data['archi_category']
    except IOError as e:
        log.error(f'{__mod__}: Cannot open metamodel parameters - checks are disabled!\n{e}')
        raise IOError(e)
    except KeyError as e:
        log.error(f'{__mod__}: Invalid metamodel parameters - checks are disabled!')
        raise KeyError(e)