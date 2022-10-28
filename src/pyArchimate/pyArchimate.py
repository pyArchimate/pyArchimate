"""
A library to create and manage Archimate models.

Author: Xavier Mayeur
Date: Aug 2022
Version 0.1

"""
import lxml.etree as et
from enum import Enum
import sys
import os
import json
import math
import re
from collections import defaultdict
from uuid import uuid4, UUID
import oyaml as yaml
from enum import Enum
from os import path
from .logger import log, log_set_level, log_to_stderr, log_to_file


__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Dictionary of valid Archimate relationships
allowed_relationships = {}
ARIS_type_map = {}
relationship_keys = {}
archi_category = {}
default_theme = 'archi'


class Writers(Enum):
    archi = 0
    csv = 1
    archimate = 2


class Readers(Enum):
    archi = 0
    aris = 1
    archimate = 2


class AccessType:
    """
    Enumeration of Access Relationship types
    """

    Access = 'Access'
    Read = 'Read'
    Write = 'Write'
    ReadWrite = 'ReadWrite'


class TextPosition:
    Top = "0"
    Middle = "1"
    Bottom = "2"


class TextAlignment:
    Left = "0"
    Center = "1"
    Right = "2"


class BorderType:
    DogEar = "0"
    Rectangle = "1"
    NoBorder = "2"


influenceStrength = {'+': '+', '++': '++', '-': '-', '--': '--', '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
                     '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': '10'},


class ArchiType:
    """
    Enumeration of Archimate Element & Relationships types
    """
    # Business Layer
    BusinessActor = "BusinessActor"
    BusinessRole = "BusinessRole"
    BusinessCollaboration = "BusinessCollaboration"
    BusinessInterface = "BusinessInterface"
    BusinessProcess = "BusinessProcess"
    BusinessFunction = "BusinessFunction"
    BusinessInteraction = "BusinessInteraction"
    BusinessEvent = "BusinessEvent"
    BusinessService = "BusinessService"
    BusinessObject = "BusinessObject"
    Contract = "Contract"
    Representation = "Representation"
    Product = "Product"

    # Application Layer

    ApplicationComponent = "ApplicationComponent"
    ApplicationInterface = "ApplicationInterface"
    ApplicationCollaboration = "ApplicationCollaboration"
    ApplicationFunction = "ApplicationFunction"
    ApplicationProcess = "ApplicationProcess"
    ApplicationEvent = "ApplicationEvent"
    ApplicationService = "ApplicationService"
    DataObject = "DataObject"

    # Technology layer

    Node = "Node"
    Device = "Device"
    Path = "Path"
    CommunicationNetwork = "CommunicationNetwork"
    SystemSoftware = "SystemSoftware"
    TechnologyCollaboration = "TechnologyCollaboration"
    TechnologyInterface = "TechnologyInterface"
    TechnologyFunction = "TechnologyFunction"
    TechnologyProcess = "TechnologyProcess"
    TechnologyInteraction = "TechnologyInteraction"
    TechnologyEvent = "TechnologyEvent"
    TechnologyService = "TechnologyService"
    Artifact = "Artifact"

    # Physical elements

    Equipment = "Equipment"
    Facility = "Facility"
    DistributionNetwork = "DistributionNetwork"
    Material = "Material"

    #  Motivation

    Stakeholder = "Stakeholder"
    Driver = "Driver"
    Assessment = "Assessment"
    Goal = "Goal"
    Outcome = "Outcome"
    Principle = "Principle"
    Requirement = "Requirement"
    Constraint = "Constraint"
    Meaning = "Meaning"
    Value = "Value"

    # Strategy

    Resource = "Resource"
    Capability = "Capability"
    CourseOfAction = "CourseOfAction"

    # Implementation & Migration

    WorkPackage = "WorkPackage"
    Deliverable = "Deliverable"
    ImplementationEvent = "ImplementationEvent"
    Plateau = "Plateau"
    Gap = "Gap"

    # Other

    Grouping = "Grouping"
    Location = "Location"

    # Junction

    Junction = "Junction"
    OrJunction = "OrJunction"
    AndJunction = "AndJunction"

    # Relationships

    Association = "Association"
    Assignment = "Assignment"
    Realization = "Realization"
    Serving = "Serving"
    Composition = "Composition"
    Aggregation = "Aggregation"
    Access = "Access"
    Influence = "Influence"
    Triggering = "Triggering"
    Flow = "Flow"
    Specialization = "Specialization"

    # Special
    View = "View"


class ArchimateRelationshipError(Exception):
    pass


class ArchimateConceptTypeError(Exception):
    pass


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


def set_id(uuid=None):
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


def default_color(elem_type, theme=default_theme) -> str:
    """
    Get the default color of a Node, according to its type

    :param elem_type:       archimate element type
    :type elem_type: str
    :param theme:  'archi' or 'aris' color theme - default = 'archi'
    :type theme: dict
    :return: #Hex color str
    """
    default_colors = {'strategy': '#F5DEAA', 'business': "#FFFFB5", 'application': "#B5FFFF", 'technology': "#C9E7B7",
                      'physical': "#C9E7B7", 'migration': "#FFE0E0", 'motivation': "#CCCCFF",
                      'relationship': "#DDDDDD", 'other': '#FFFFFF', 'junction': '#000000'}
    aris_colors = {'strategy': '#D38300', 'business': "#F5C800", 'application': "#00A0FF", 'technology': "#6BA50E",
                   'physical': "#6BA50E", 'migration': "#FFE0E0", 'motivation': "#F099FF",
                   'relationship': "#DDDDDD", 'other': '#FFFFFF', 'junction': '#000000'}
    if elem_type in archi_category:
        cat = archi_category[elem_type].lower()

        if theme == 'archi' or theme is None:
            return default_colors[cat]
        if theme == 'aris':
            return aris_colors[cat]
        else:
            try:
                return theme[cat]
            except KeyError:
                return default_colors[cat]


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
    if not hasattr(ArchiType, rel_type) or archi_category[rel_type] != 'Relationship':
        raise ArchimateConceptTypeError(f"Invalid Archimate Relationship Concept type '{rel_type}'")
    if not hasattr(ArchiType, source_type):  # or archi_category[source_type] == 'Relationship':
        raise ArchimateConceptTypeError(f"Invalid Archimate Source Concept type '{source_type}'")
    if not hasattr(ArchiType, target_type):  # or archi_category[target_type] == 'Relationship':
        raise ArchimateConceptTypeError(f"Invalid Archimate Target Concept type '{target_type}'")
    if archi_category[source_type] == 'Relationship':
        source_type = "Relationship"
    if archi_category[target_type] == 'Relationship':
        target_type = "Relationship"
    if 'Junction' in rel_type:
        rel_type = 'Junction'
    if 'Junction' in source_type:
        source_type = 'Junction'
    if 'Junction' in target_type:
        target_type = 'Junction'
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
    if not hasattr(ArchiType, source_type) or archi_category[source_type] == 'Relationship':
        raise ArchimateConceptTypeError(f"Invalid Archimate Source Concept type '{source_type}'")
    if not hasattr(ArchiType, target_type) or archi_category[target_type] == 'Relationship':
        raise ArchimateConceptTypeError(f"Invalid Archimate Target Concept type '{target_type}'")
    rels = allowed_relationships[source_type][target_type]
    if len(rels) > 0:
        if 'g' in rels:
            t = 'g'
        elif 'r' in rels:
            t = 'r'
        elif 's' in rels:
            t = 's'
        elif 'a' in rels:
            t = 'a'
        elif 'c' in rels:
            t = 'c'
        elif 'o' in rels:
            t = 'o'
        elif 'v' in rels:
            t = 'v'
        else:
            t = rels[0]

        return [k for k, v in relationship_keys.items() if v == t][0]


class Point:
    """
    A simple class to manage x, y coordinates of a point
    x: x-coordinate
    y: y-coordinate

    """

    def __init__(self, x=0, y=0):
        x = int(x)
        y = int(y)
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


class RGBA:
    """
    Class to manage RGB/hex color and alpha (opacity) channels

    :param r: red channel color intensity 0-255
    :param g: green channel color intensity 0-255
    :param b: blue channel color intensity 0-255
    :param a: alpha channel color intensity 0-100
    """

    def __init__(self, r=0, g=0, b=0, a=100):
        self.r = max(0, min(255, int(r)))
        self.g = max(0, min(255, int(g)))
        self.b = max(0, min(255, int(b)))
        self.a = max(0, min(100, int(a)))

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
        if elem_type is None or not hasattr(ArchiType, elem_type):
            raise ArchimateConceptTypeError(f"Invalid Element type '{elem_type}'")
        if archi_category[elem_type] == 'Relationship':
            raise ArchimateConceptTypeError(f"Element type '{elem_type}' cannot be a Relationship type")
        if not isinstance(parent, Model):
            raise ValueError('Element class parent should be a class Model instance!')

        # Attribute and data structure initialization
        self._uuid = set_id(uuid)
        self.parent = parent
        self.model: Model = parent
        self.name = name
        self._type = elem_type
        self.desc = desc
        self.folder = folder
        self._properties = {}
        self.junction_type = None

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

        # Re-assign othe element related node references to this element (merge target)
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

    def __init__(self, rel_type='', source=None, target=None, uuid=None, name=None,
                 access_type=None, influence_strength=None, desc=None, is_directed=None, parent=None):

        if not isinstance(parent, Model):
            raise ValueError('Relationship class parent should be a class Model instance!')
        self.parent = parent
        self.model = parent
        # get source identifier as reference
        if isinstance(source, str):
            self._source = source
        elif not isinstance(source, Element) and not isinstance(source, Relationship):
            raise ValueError("'source' argument is not an instance of 'Element or Relationship' class.")
        else:
            self._source = source.uuid
        if self._source not in self.parent.elems_dict and self._source not in self.parent.rels_dict:
            raise ValueError(f'Invalid source reference "{self._source}')
        # get target identifier
        if isinstance(target, str):
            self._target = target
        elif not isinstance(target, Element) and not isinstance(target, Relationship):
            raise ValueError("'target' argument is not an instance of 'Element/Relationship' class.")
        else:
            self._target = target.uuid
        if self._target not in self.parent.elems_dict and self._target not in self.parent.rels_dict:
            raise ValueError(f'Invalid target reference "{target}')

        self._uuid = set_id(uuid)
        self._type = rel_type
        self.name = name
        self.desc = desc
        self._properties = {}
        self.folder = None

        self._access_type = access_type
        self._influence_strength = influence_strength
        self._is_directed = is_directed

        # check relationship validity (it also tests concept type validity) or raise exception
        if self._source in self.model.elems_dict:
            src_type = self.model.elems_dict[self._source].type
        else:
            src_type = self.model.rels_dict[self._source].type
        if self._target in self.model.elems_dict:
            dst_type = self.model.elems_dict[self._target].type
        else:
            dst_type = self.model.rels_dict[self._target].type

        check_valid_relationship(self.type, src_type, dst_type)

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
        return self.parent.elems_dict[_id] if _id in self.parent.elems_dict else self.parent.rels_dict[
            _id] if _id in self.parent.rels_dict else None

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
        return self.parent.elems_dict[_id] if _id in self.parent.elems_dict \
            else self.parent.rels_dict[_id] if _id in self.parent.rels_dict else None

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
        if val is not None and self.type == ArchiType.Access:
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
        if val is not None and self.type == ArchiType.Association:
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
        if strength is not None and self.type == ArchiType.Influence:
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

        if node_type == 'Element':
            if self._ref is not None and self._ref not in self.model.elems_dict:
                raise ValueError(f'Invalid element reference "{self._ref}')
        elif node_type == "Label":
            if self._ref is not None and self._ref not in self.model.labels_dict:
                raise ValueError(f'Invalid element reference "{self._ref}')

        self._uuid = set_id(uuid)

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
        self._fill_color = None
        self.line_color = None
        self.opacity = 100
        self.lc_opacity = 100
        self.font_color = None
        self.font_name = 'Segoe UI'
        self.font_size = 9
        self.text_alignment = None
        self.text_position = None
        self.label_expression = None
        self.border_type = None

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
                n.move(self.parent)

        if self._uuid in self.parent.nodes_dict:
            del self.parent.nodes_dict[self._uuid]
        del self.model.nodes_dict[self._uuid]

        if delete_from_model:
            # find if nodes in other views are referring to this element
            e = self.concept
            related_nodes = [n for n in self.model.nodes if n.ref == e.uuid]
            for n in related_nodes:
                n.delete(recurse)
            e.delete()

    def add(self, ref=None, x=0, y=0, w=120, h=55, uuid=None, node_type='Element',
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
        #                 self.model.add_relationship(embed_rel_type=ArchiTypes.Specialization, source=n.concept, target=self.concept)
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
        for n in self.nodes:
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
        for n in self.nodes:
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
            self._fill_color = default_color(self.type, self.model.theme)
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

    @property
    def nodes(self):
        return list(self.nodes_dict.values())

    def getnodes(self, elem_type=None):
        """
        Get the list of children nodes

        :return: [Node]
        :rtype: list

        """
        if elem_type is None:
            return list(self.nodes_dict.values())
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
        :param nested_rel_type: relationship to use for nested node, else use a default value
        :type nested_rel_type:  Relationship
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
        n = [x for x in self.nodes if x.ref == _e.uuid]
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

    def resize(self, max_in_row=3, keep_kids_size=True, w=120, h=55, gap_x=20, gap_y=20, justify='left',
               recurse=True, sort="asc"):
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
        :param sort:                one of 'asc' | 'desc' | 'none'
        :type sort: str

        """
        max_w = w
        max_h = h

        ba_x = 40
        ba_y = 40
        max_row_h = h

        n = 1
        row = 0
        if 'asc' in sort.lower():
            nodes = sorted(self.nodes, key=lambda x: x.w * x.h, reverse=False)
        elif 'desc' in sort.lower():
            nodes = sorted(self.nodes, key=lambda x: x.w * x.h, reverse=True)
        else:
            nodes = self.nodes

        for _e in nodes:
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

    def move(self, new_parent):
        """
        Move a Node to another Node on the same view or to its root view
        :param new_parent: new parent object
        :rtype new_parent: Node | View
        """
        if not isinstance(new_parent, View) and not isinstance(new_parent, Node):
            log.error(f"Invalid target to move the node to. Expecting a View or a Node")
            return

        if new_parent.view.uuid != self.view.uuid:
            log.error(f"Cannot move a node outside of its view")
            return

        del self.parent.nodes_dict[self.uuid]
        self.parent = new_parent
        new_parent.nodes_dict[self.uuid] = self


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
        self._uuid = set_id(uuid)
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
        if self._source not in self.model.nodes_dict and self._source not in self.model.conns_dict:
            raise ValueError(f'Invalid source reference "{self._source}')

        if isinstance(target, Node):
            self._target = target.uuid
        elif isinstance(target, str):
            self._target = target
        else:
            raise ArchimateConceptTypeError("'target' is not an instance of 'Node' class.")
        if self._target not in self.model.nodes_dict and self._target not in self.model.conns_dict:
            raise ValueError(f'Invalid source reference "{self._target}')

        self._uuid = set_id(uuid)

        self.bendpoints = list()

        # set default style
        self.line_color = None
        self.font_color = None
        self.font_name = 'Segoe UI'
        self.font_size = 9
        self.line_width = 1
        self.text_position = "1"
        self.show_label = True

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
        elif self._source in self.model.conns_dict:
            return self.model.rels_dict[self._source]

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
        elif self._target in self.model.conns_dict:
            return self.model.rels_dict[self._target]

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

    @property
    def access_type(self):
        return self.concept.access_type

    @property
    def is_directed(self):
        return self.concept.is_directed

    @property
    def influence_strength(self):
        return self.concept.influence_strength

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

        dx = s_cx - t_cx
        dy = s_cy - t_cy

        if direction == 0 and not self.source.is_inside(t_cx, s_cy) \
                and not self.target.is_inside(t_cx, s_cy):
            self.add_bendpoint(
                Point(t_cx + dx * weight_x, s_cy + self.source.h * (0.5 - weight_y))
            )

        elif direction == 1 and not self.source.is_inside(s_cx, t_cy) \
                and not self.target.is_inside(s_cx, t_cy):
            self.add_bendpoint(
                Point(s_cx - self.source.w * (0.5 - weight_x),
                      t_cy + dy *weight_y)
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
                        s_xy.y + dy * weight_y)
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
        self._uuid = set_id(uuid)
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

    def add(self, ref=None, x=0, y=0, w=120, h=55, uuid=None, node_type='Element',
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

    def add_connection(self, ref=None, source=None, target=None, uuid=None):
        """
        Method to add a connection between two nodes in this view

        :param ref:             Identifier of the connnection's Relationship
        :type ref: [str|Relationship]
        :param source:          Source node of the connection (its Identifier or the node object itself)
        :type source: [str|Node]
        :param target:          Target node of the connection
        :type target: [str|Node]
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

    @property
    def nodes(self):
        return list(self.nodes_dict.values())

    @property
    def conns(self):
        return list(self.conns_dict.values())

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
        n = [x for x in self.nodes if x.ref == _e.uuid]
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

        :param rel: Parent Relationship object referred by the connection or None if a new relationship is to be created
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
            rel_type = r.type
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

        self._uuid = set_id(uuid)
        self.name = name
        self.desc = desc
        self._properties = {}
        self.pdefs = {}
        self.elems_dict = defaultdict(Element)
        self.rels_dict = defaultdict(Relationship)
        self.nodes_dict = defaultdict(Node)
        self.conns_dict = defaultdict(Connection)
        self.views_dict = defaultdict(View)
        self.labels_dict = defaultdict(Node)
        self.orgs = defaultdict(list)
        self.theme = 'archi'

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
        if concept_type == ArchiType.View:
            v = View(name, uuid, desc, folder, parent=self)
            self.views_dict[v.uuid] = v
            return v
        else:
            _e = Element(concept_type, name, uuid, desc, folder, parent=self)
            self.elems_dict[_e.uuid] = _e
            return _e

    def add_relationship(self, rel_type='', source=None, target=None, uuid=None, name=None, access_type=None,
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
    def views(self):
        """
        Get the list of views in this model

        :return: [View]
        :rtype: list
        """
        return list(self.views_dict.values())

    @property
    def elements(self):
        """
        Get the list of Elements in this model

        :return: [Element]
        :rtype: list
        """
        return list(self.elems_dict.values())

    @property
    def relationships(self):
        """
        Get the list of Relationships in this Model

        :return: [Relationship]
        :rtype: list
         """
        return list(self.rels_dict.values())

    @property
    def nodes(self):
        """
        Get the list of all nodes from the model
        :return: Nodes
        :rtype: list(Node)
        """
        return list(self.nodes_dict.values())

    @property
    def conns(self):
        """
        Get the list of all connections from the model
        :return: Connections
        :rtype: list(Connection)
        """
        return list(self.conns_dict.values())

    def write(self, file_path=None, writer=Writers.archimate):
        """
        Method to write the file_path to an Archimate file

        :param file_path:
        :type file_path: str
        :param writer: a writer function converting the model into the desired output format, default: Archimate OEF XML
        :type writer: function
        :return:  data structure
        :rtype: str
        """
        from .writers.archimateWriter import archimate_writer
        from .writers.csvWriter import csv_writer
        from .writers.archiWriter import archi_writer
        if writer == Writers.archimate:
            return archimate_writer(self, file_path)
        elif writer == Writers.csv:
            return csv_writer(self, file_path)
        else:
            return archi_writer(self, file_path)

    def read(self, file_path, *args, **kwargs):
        """
        Method to read an Archimate file
        The method detects automagically and read the following formats:
        - ARIS AML
        - Open Group Open Exchange File
        - Archi Tool

        :param file_path:
        :type file_path: str


        """
        try:
            with open(file_path, 'r', encoding='utf-8') as fd:
                _data = fd.read()
        except IOError:
            log.error(f"{__mod__} {self.__class__.__name__}.read: Cannot open or read file '{file_path}'")
            sys.exit(1)
        root = et.fromstring(_data.encode())
        from .readers.archimateReader import archimate_reader
        from .readers.archiReader import archi_reader
        from .readers.arisAMLreader import aris_reader
        if 'opengroup' in root.tag:
            archimate_reader(self, root)
        elif 'archimate' in root.tag:
            archi_reader(self, root)
        elif 'AML' in root.tag:
            aris_reader(self, root, *args, **kwargs)
        else:
            log.error('Unsupported input format')

    def merge(self, file_path):
        """
        Method to merge an Archimate file into this model

        :param file_path:
        :type file_path: str

        """

        try:
            with open(file_path, 'r', encoding='utf-8') as fd:
                _data = fd.read()
        except IOError:
            log.error(f"{__mod__} {self.__class__.__name__}.read: Cannot open or read file '{file_path}'")
            sys.exit(1)
        root = et.fromstring(_data.encode())
        from .readers.archimateReader import archimate_reader
        from .readers.archiReader import archi_reader
        # self from .readers.arisAMLreader import aris_reader
        if 'opengroup' in root.tag:
            archimate_reader(self, root, merge_flg=True)
        elif 'archimate' in root.tag:
            archi_reader(self, root, merge_flg=True)
        else:
            log.error('Unsupported input format for merge operation')

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
            return list(self.elems_dict.values())

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
        if name is None:
            r = self.filter_relationships(lambda x: (x.type == rel_type
                                                     and x.source.uuid == source.uuid
                                                     and x.target.uuid == target.uuid
                                                     and x.access_type == access_type
                                                     and x.is_directed == is_directed))
        else:
            r = self.filter_relationships(lambda x: (x.type == rel_type and x.name == name
                                                     and x.source.uuid == source.uuid
                                                     and x.target.uuid == target.uuid
                                                     and x.access_type == access_type
                                                     and x.is_directed == is_directed))
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
                v = self.add(ArchiType.View, view)
            else:
                v = None
        else:
            v = view
        return v

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
                # For relationship, we embed all properties in a single one called 'Identifier'
                # to cope with ARIS limitation
                p = {}
                if o.name is not None:
                    p['name'] = o.name
                if o.desc is not None:
                    p['documentation'] = o.desc
                if o.type == ArchiType.Association:
                    p['isDirected'] = o.is_directed
                elif o.type == ArchiType.Access:
                    p['access'] = o.access_type
                elif o.type == ArchiType.Influence:
                    p['influence_strength'] = o.influence_strength
                for key, val in o.props.items():
                    p[key] = val
                for x in o.props.copy():
                    o.remove_prop(x)
                o.prop('Identifier', 'properties = ' + json.dumps(p))

            elif o.props != {} and (isinstance(o, View) or isinstance(o, Element) or isinstance(o, Model)):
                # Else we embed properties art the end of the description field
                pat = r'[#]*properties\s*=\s*(\{[\s\S]*\})[;]*'
                # Get the concept description and remove any existing embedded properties tag
                desc = '' if o.desc is None else re.sub(pat, '', o.desc, re.DOTALL)
                # add the properties tag in the concept desc
                desc += desc.strip(' \n') + '\n\nproperties = ' + json.dumps(o.props, indent=2) + '\n'
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

        def _expand(o, clean_doc):
            pat = r'[#]*properties\s*=\s*(\{[\s\S]*\})[;]*'
            if isinstance(o, Relationship):
                if o.prop('Identifier') is not None:
                    p = o.prop('Identifier')
                    match = re.findall(pat, p, re.M)
                    if len(match) > 0:
                        p = json.loads(match[0])
                        o.remove_prop('Identifier')
                        if p is not None:
                            o.name = p['name'] if 'name' in p else None
                            o.desc = p['documentation'] if 'documentation' in p else None
                            if 'isDirected' in p and o.type == ArchiType.Association:
                                o.is_directed = True if str(p['isDirected']).lower() == 'true' else False
                            if 'access' in p and o.type == ArchiType.Access:
                                o.access_type = p['access']
                            if 'influence_strength' in p and o.type == ArchiType.Influence:
                                o.influence_strength = p['influence_strength']
                            for key, val in p.items():
                                o.prop(key, val)
                if clean_doc:
                    o.desc = None if o.desc is None else re.sub(pat, '', o.desc, re.DOTALL)

            elif isinstance(o, View) or isinstance(o, Element) or isinstance(o, Model):
                # Get the concept description and remove any existing embedded properties tag
                if o.desc is not None:
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

        _expand(self, clean_doc)
        for v in self.views_dict.values():
            _expand(v, clean_doc)
        for e in self.elems_dict.values():
            _expand(e, clean_doc)
        for r in self.rels_dict.values():
            _expand(r, clean_doc)

    def check_invalid_conn(self):
        """
        Method to check the validity of a list of connections
        """
        invalids = []

        for id, c in self.conns_dict.items():
            if self.check_connection(c):
                invalids.append(id)
        return invalids

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
        if c.concept._source not in self.elems_dict:
            log.error(f'Connection {c.uuid} has orphan source node concept {c.concept._source}')
            _ok = False
        if c._target not in self.nodes_dict:
            log.error(f'Connection {c.uuid} has orphan target node {c._target}')
            _ok = False
        if c.concept._target not in self.elems_dict:
            log.error(f'Connection {c.uuid} has orphan target node concept {c.concept._target}')
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

    def check_invalid_nodes(self):
        invalids = []
        for id, n in self.nodes_dict.items():
            if n.ref not in self.elems_dict and n.cat == 'Element':
                invalids.append(id)
                try:
                    log.error(f'Orphan node "{n.name}" with id {n.uuid} refers to unknown {n.ref}')
                except ArchimateConceptTypeError:
                    log.error(f'Orphan node with id {id}')
        return invalids

    def default_theme(self, theme=default_theme):
        for e in self.nodes:
            e.fill_color = default_color(e.type, theme)
        for r in self.conns:
            r.line_color = default_color('Relationship', self.default_theme)
        self.theme = theme


# Fetch model parameters during initialization of the module
if allowed_relationships == {}:
    data = None
    try:
        with open(os.path.join(os.path.sep, __location__, "checker_rules.yml"), "r") as fd:
            data = yaml.load(fd, Loader=yaml.Loader)
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
