"""Model module - extracted from the legacy monolith."""

import json
import os
import re
import sys
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Optional

import lxml.etree as et

from .constants import (
    ARCHI_CATEGORY,
    DEFAULT_THEME,
    MODEL_READER_REGISTRY,
    OPERATION_ERROR_MESSAGES,
)
from .element import Element, set_id
from .enums import ArchiType, Writers
from .exceptions import ArchimateConceptTypeError
from .logger import log
from .view import Node, Profile, View

if TYPE_CHECKING:
    from .relationship import Relationship

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
__mod__ = __name__.split('.')[-1]

ARCHIMATE_EXCEPTION_GROUP = (ArchimateConceptTypeError,)


def _matches_rel(r: Any, rel_type: Optional[str], elem_uuid: str, wants_in: bool, wants_out: bool) -> bool:
    if wants_in and r.target.uuid == elem_uuid:
        return rel_type is None or r.type == rel_type
    if wants_out and r.source.uuid == elem_uuid:
        return rel_type is None or r.type == rel_type
    return False


def _embed_object(o: Any, remove_props: bool) -> None:
    from .relationship import Relationship
    if isinstance(o, Relationship):
        if o.name is not None:
            o.prop('Identifier', o.name)
    elif o.props != {}:
        pat = r'[#]*properties\s*=\s*(\{[\s\S]*\})[;]*'
        desc = '' if o.desc is None else re.sub(pat, '', o.desc, flags=re.DOTALL)
        desc += desc.strip(' \n') + '\n\nproperties = ' + json.dumps(o.props, indent=2) + '\n'
        o.desc = desc
        if remove_props:
            for x in o.props.copy():
                o.remove_prop(x)


def _expand_object(o: Any, clean_doc: bool) -> None:
    from .relationship import Relationship
    pat = r'[#]*properties\s*=\s*(\{[\s\S]*\})[;]*'
    if isinstance(o, Relationship):
        if o.prop('Identifier') is not None:
            p = o.prop('Identifier')
            match = re.findall(pat, str(p), re.M)
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
            o.desc = None if o.desc is None else re.sub(pat, '', o.desc, flags=re.DOTALL)
    elif isinstance(o, (View, Element)):
        if o.desc is not None:
            match = re.findall(pat, o.desc, re.M)
            if len(match) == 1:
                props = json.loads(match[0])
                o.desc = re.sub(pat, '', o.desc, flags=re.DOTALL).strip(' \n')
                for key, val in props.items():
                    o.prop(key, val)
                if clean_doc:
                    o.desc = None if o.desc is None else re.sub(pat, '', o.desc, flags=re.DOTALL)



def default_color(elem_type: str, theme: Any = DEFAULT_THEME) -> str:
    """
    Get the default color of a Node, according to its type

    :param elem_type:       archimate element type
    :type elem_type: str
    :param theme:  'archi' or 'aris' color theme - default = 'archi'
    :type theme: str
    :return: #Hex color str
    """
    default_colors = {'strategy': '#F5DEAA', 'business': "#FFFFB5", 'application': "#B5FFFF", 'technology': "#C9E7B7",
                      'physical': "#C9E7B7", 'migration': "#FFE0E0", 'motivation': "#CCCCFF",
                      'relationship': "#DDDDDD", 'other': '#FFFFFF', 'junction': '#000000'}
    aris_colors = {'strategy': '#D38300', 'business': "#F5C800", 'application': "#00A0FF", 'technology': "#6BA50E",
                   'physical': "#6BA50E", 'migration': "#FFE0E0", 'motivation': "#F099FF",
                   'relationship': "#DDDDDD", 'other': '#FFFFFF', 'junction': '#000000'}
    if elem_type in ARCHI_CATEGORY:
        cat = ARCHI_CATEGORY[elem_type].lower()

        if theme == 'archi' or theme is None:
            return default_colors[cat]
        if theme == 'aris':
            return aris_colors[cat]
        else:
            try:
                return str(theme[cat])
            except KeyError:
                return default_colors[cat]
    return default_colors['other']


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
        self._profiles_dict = {}
        self.elems_dict = {}
        self.rels_dict = {}
        self.nodes_dict = {}
        self.conns_dict = {}
        self.views_dict = {}
        self.labels_dict = {}
        self.orgs = defaultdict(list)
        self.theme = 'archi'

        # with open(os.path.join(__location__, 'archimate3_Diagram.xsd'), 'r') as _f:
        #     self.schemaD = _f.read()
        # with open(os.path.join(__location__, 'archimate3_Model.xsd'), 'r') as _f:
        #     self.schemaM = _f.read()
        # with open(os.path.join(__location__, 'archimate3_View.xsd'), 'r') as _f:
        #     self.schemaV = _f.read()

    def add(self, concept_type=None, name=None, uuid=None, desc=None, folder=None, profile=None):
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
        :param profile: str     Archimate Element profile name
        :type folder: str
        :return:                Element or View class object
        :rtype: Element|View
        """
        if concept_type == ArchiType.View:
            v = View(name, uuid, desc, folder, parent=self)
            self.views_dict[v.uuid] = v
            return v
        else:
            _e = Element(concept_type, name, uuid, desc, folder, parent=self, profile=profile)
            self.elems_dict[_e.uuid] = _e
            return _e

    def add_relationship(self, rel_type: str = '', source: Any = None, target: Any = None, uuid: Optional[str] = None, name: Optional[str] = None, access_type: Optional[str] = None,  # noqa: E501
                         influence_strength: Optional[str] = None, desc: Optional[str] = None, is_directed: Optional[bool] = None, profile: Optional[str] = None) -> "Relationship":
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
        from .relationship import Relationship
        r = Relationship(rel_type, source, target, uuid, name, access_type, influence_strength, desc,
                         is_directed, profile,
                         parent=self)
        self.rels_dict[r.uuid] = r
        return r

    @property
    def uuid(self):
        """
        Get the Model Identifier

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
    def profiles(self):
        """
        Property to access the profiles.

        This property provides access to the `_profiles` attribute of the class
        instance. It allows getting the internal profiles data which is encapsulated
        within the class.

        Returns:
            The value of the `_profiles` attribute.
        """
        return list(self._profiles_dict.values())

    def add_profile(self, name=None, uuid=None, concept=None):
        """
        Adds a new profile to the profiles dictionary and associates it with this model.

        This method creates an instance of the Profile class using the provided arguments
        and stores it in the internal dictionary, keyed by its unique identifier (UUID).
        If no UUID or name is provided, the default values will be used. This method also
        returns the newly created Profile instance.

        Args:
            name (str, optional): The name of the profile being added.
            uuid (str, optional): The unique identifier for the profile.
            concept (Any, optional): A concept object associated with the profile.

        Returns:
            Profile: The newly created Profile object.
        """
        p = Profile(name=name, uuid=uuid, concept=concept, model=self)
        self._profiles_dict[p.uuid] = p
        return p

    def get_profile(self, name):
        for p in self.profiles:
            if p.name == name:
                return p
        return None

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
        :param writer: writer selection (enum value, registry key, or callable) used to format the output.
        :type writer: Writers|str|callable
        :return:  data structure
        :rtype: str
        """
        from .writers import _resolve_writer
        writer_callable = _resolve_writer(writer)
        return writer_callable(self, file_path)

    def _load_file_contents(self, file_path, operation):
        try:
            with open(file_path, 'r', encoding='utf-8') as fd:
                return fd.read()
        except IOError:
            log.error(f"{__mod__} {self.__class__.__name__}.{operation}: Cannot open or read file '{file_path}'")
            sys.exit(1)

    @staticmethod
    def _match_reader_entry(root_tag):
        lower_tag = root_tag.lower()
        for entry in MODEL_READER_REGISTRY:
            if entry.tag_key in lower_tag:
                return entry
        return None

    def _prepare_reader(self, file_path, operation):
        data = self._load_file_contents(file_path, operation)
        parser = et.XMLParser(recover=True)
        root = et.fromstring(data.encode(), parser=parser)
        entry = self._match_reader_entry(root.tag)
        if entry is None:
            log.error(OPERATION_ERROR_MESSAGES.get(operation, OPERATION_ERROR_MESSAGES['read']))
            return None, None, None
        reader = entry.loader()
        return reader, root, entry

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
        reader, root, entry = self._prepare_reader(file_path, 'read')
        if reader is None or entry is None:
            return
        call_args = args if entry.forward_read_args else ()
        call_kwargs = kwargs if entry.forward_read_args else {}
        reader(self, root, *call_args, **call_kwargs)

    def merge(self, file_path):
        """
        Method to merge an Archimate file into this model

        :param file_path:
        :type file_path: str

        """

        reader, root, entry = self._prepare_reader(file_path, 'merge')
        if reader is None or entry is None:
            return
        if not entry.supports_merge:
            log.error(OPERATION_ERROR_MESSAGES['merge'])
            return
        reader(self, root, merge_flg=True)

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
        direction = direction.lower()
        wants_in = 'in' in direction or 'both' in direction
        wants_out = 'out' in direction or 'both' in direction
        return [r for r in self.rels_dict.values()
                if _matches_rel(r, rel_type, elem.uuid, wants_in, wants_out)]

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

    def get_or_create_element(self, elem_type: str, elem: str, create_elem: bool = False) -> Optional[Any]:
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

    def get_or_create_relationship(self, rel_type: str, name: Optional[str], source: Any, target: Any, create_rel: bool = False,  # noqa: E501
                                   access_type: Optional[str] = None,
                                   influence_strength: Optional[str] = None, desc: Optional[str] = None, is_directed: Optional[bool] = None) -> Optional[Any]:
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
        _embed_object(self, remove_props)
        for v in self.views_dict.values():
            _embed_object(v, remove_props)
        for e in self.elems_dict.values():
            _embed_object(e, remove_props)
        for r in self.rels_dict.values():
            _embed_object(r, remove_props)

    def expand_props(self, clean_doc=True):
        """
        Method to expand model's concepts desc attribute properties tag into concept's properties

        """
        _expand_object(self, clean_doc)
        for v in self.views_dict.values():
            _expand_object(v, clean_doc)
        for e in self.elems_dict.values():
            _expand_object(e, clean_doc)
        for r in self.rels_dict.values():
            _expand_object(r, clean_doc)

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
        if c.source is not None and not isinstance(c.source, View):
            if c.source._ref != c.concept._source:
                log.error(f'Connection {c.uuid} has a reference to its source Element which is not '
                          'the reference of the relationship source Element')
            _ok = False
        if c.target is not None and not isinstance(c.target, View):
            if c.target._ref != c.concept._target:
                log.error(f'Connection {c.uuid} has a reference to its target Element which is not '
                          'the reference of the relationship target Element')
            _ok = False

        return _ok

    def check_invalid_nodes(self):
        """
        Check and get the list of nodes that are orphans (without known related Element)
        :return: list of orphan nodes
        :rtype: list(Node)
        """
        invalids = []
        for id, n in self.nodes_dict.items():
            if n.ref not in self.elems_dict and n.cat == 'Element':
                invalids.append(id)
                try:
                    log.error(f'Orphan node "{n.name}" with id {n.uuid} refers to unknown {n.ref}')
                except ARCHIMATE_EXCEPTION_GROUP:
                    log.error(f'Orphan node with id {id}')
        return invalids

    def default_theme(self, theme=DEFAULT_THEME):
        """
        Set the default color theme for the model
        :param theme: default theme reference
        :return: nothing
        """
        for e in self.nodes:
            e.fill_color = default_color(e.type, theme)
        for r in self.conns:
            r.line_color = default_color('Relationship', theme)
        self.theme = theme


__all__ = ["Model"]
