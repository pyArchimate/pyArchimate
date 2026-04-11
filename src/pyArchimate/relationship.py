"""Relationship module - extracted from the legacy monolith."""

from typing import TYPE_CHECKING, Union

from .constants import ARCHI_CATEGORY, ALLOWED_RELATIONSHIPS, RELATIONSHIP_KEYS
from .enums import ArchiType
from .exceptions import ArchimateConceptTypeError

if TYPE_CHECKING:
    from .model import Model
    from .element import Element


def _is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

    :param uuid_to_test: uuid string
    :param version: {1, 2, 3, 4}
    :return: True if uuid_to_test is a valid UUID, otherwise `False`.
    :rtype: bool
    """
    from uuid import UUID

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def set_id(uuid=None):
    """
    Function to create an identifier if none exists

    :param uuid: a uuid
    :return: a formatted identifier
    :rtype: str
    """
    from uuid import uuid4

    _id = str(uuid4()) if (uuid is None) else uuid
    if _is_valid_uuid(_id):
        _id = _id.replace('-', '')
        if _id[:3] != 'id-':
            _id = 'id-' + _id
    return _id


def check_valid_relationship(rel_type, source_type, target_type, raise_flg=False):
    """
    Check if a relationship is used according to Archimate language or raise an exception

    :param rel_type:        relationship type
    :type rel_type: str
    :param source_type:     source concept type
    :type source_type: str
    :param target_type:     target concept type
    :type target_type: str
    :param raise_flg: Throw an exception instead of logging an error
    """
    from .logger import log

    if not hasattr(ArchiType, rel_type) or ARCHI_CATEGORY[rel_type] != 'Relationship':
        msg = ArchimateConceptTypeError(f"Invalid Archimate Relationship Concept type '{rel_type}'")
        if raise_flg:
            raise msg
        else:
            log.error(ArchimateConceptTypeError(f"Invalid Archimate Relationship Concept type '{rel_type}'"))
    if not hasattr(ArchiType, source_type):
        msg = ArchimateConceptTypeError(f"Invalid Archimate Source Concept type '{source_type}'")
        if raise_flg:
            raise msg
        else:
            log.error(ArchimateConceptTypeError(f"Invalid Archimate Source Concept type '{source_type}'"))
    if not hasattr(ArchiType, target_type):
        msg = ArchimateConceptTypeError(f"Invalid Archimate Target Concept type '{target_type}'")
        if raise_flg:
            raise msg
        else:
            log.error(ArchimateConceptTypeError(f"Invalid Archimate Target Concept type '{target_type}'"))

    if ARCHI_CATEGORY[source_type] == 'Relationship':
        source_type = "Relationship"
    if ARCHI_CATEGORY[target_type] == 'Relationship':
        target_type = "Relationship"
    if 'Junction' in rel_type:
        rel_type = 'Junction'
    if 'Junction' in source_type:
        source_type = 'Junction'
    if 'Junction' in target_type:
        target_type = 'Junction'

    if RELATIONSHIP_KEYS[rel_type] not in ALLOWED_RELATIONSHIPS[source_type][target_type]:
        msg = ArchimateConceptTypeError(f"Invalid Relationship type '{rel_type}' from '{source_type}' and '{target_type}' ")
        if raise_flg:
            raise msg
        else:
            log.error(ArchimateConceptTypeError(f"Invalid Relationship type '{rel_type}' from '{source_type}' and '{target_type}' "))


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
    :param profile:          relationship profile identifier
    :type profile: str
    :param parent:           parent Model object
    :type parent: Model

    """

    def __init__(self, rel_type='', source=None, target=None, uuid=None, name=None,
                 access_type=None, influence_strength=None, desc=None, is_directed=None, profile=None, parent=None):

        if parent is not None:
            # Accept any model-like object exposing relationship storage to
            # remain compatible with legacy and modular Model instances.
            if not hasattr(parent, "rels_dict"):
                raise ValueError('Relationship class parent should be a class Model instance!')

        self.parent = parent
        self.model = parent
        # get source identifier as reference
        if isinstance(source, str):
            self._source = source
        elif source is not None:
            from .element import Element
            if not (
                isinstance(source, Element)
                or isinstance(source, Relationship)
                or hasattr(source, "uuid")
            ):
                raise ValueError("'source' argument is not an instance of 'Element or Relationship' class.")
            self._source = source.uuid
        if self._source not in self.parent.elems_dict and self._source not in self.parent.rels_dict:
            raise ValueError(f'Invalid source reference "{self._source}')
        # get target identifier
        if isinstance(target, str):
            self._target = target
        elif target is not None:
            from .element import Element
            if not (
                isinstance(target, Element)
                or isinstance(target, Relationship)
                or hasattr(target, "uuid")
            ):
                raise ValueError("'target' argument is not an instance of 'Element/Relationship' class.")
            self._target = target.uuid
        if self._target not in self.parent.elems_dict and self._target not in self.parent.rels_dict:
            raise ValueError(f'Invalid target reference "{target}')

        self._uuid = set_id(uuid)
        self._type = rel_type
        self.name = name
        self.desc = desc
        self._properties = {}
        self.folder = None
        self._profile = profile
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
        elif not isinstance(src, type(None)):
            from .element import Element
            if not isinstance(src, Element):
                raise ArchimateConceptTypeError("'source' argument is not an instance of 'Element' class.")
            else:
                self._source = src.uuid

    @property
    def target(self) -> "Element":
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
        elif not isinstance(dst, type(None)):
            from .element import Element
            if not isinstance(dst, Element):
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
        if new_type not in ARCHI_CATEGORY or ARCHI_CATEGORY[new_type] != 'Relationship':
            raise ValueError('Invalid Archimate relationship type')
        # Raise an exception is the new relationship type is not compatible with the source & target ones
        check_valid_relationship(new_type, self.source.type, self.target.type)
        self._type = new_type

    @property
    def profile_name(self):
        """

        Retrieve the name of the profile associated with the current object. This is done
        by checking if the profile attribute exists and matches a profile in the model's
        profiles. If no matching profile is found or the profile attribute is None, the
        method returns None.

        Returns:
            str or None: The name of the associated profile if it exists, otherwise None.
        """
        pn = [x.name for x in self.model.profiles if x.uuid == self._profile]
        if len(pn) == 1:
            return pn[0]
        else:
            return None

    @property
    def profile_id(self):
        """
        Gets the profile ID if the current profile is valid and exists in the associated
        model's profiles. Returns None if either there is no current profile or it does
        not exist in the model's profiles.

        Returns:
            int or None: The ID of the current profile if it exists, otherwise None.
        """
        pn = [x.uuid for x in self.model.profiles if x.uuid == self._profile]
        if len(pn) == 1:
            return pn[0]
        else:
            return None

    def set_profile(self, profile_name):
        """
        Sets or updates the profile for the current instance based on the provided
        profile name. If the profile name exists in the model's profile collection,
        it is set as the current profile. Otherwise, a new profile is created and
        added to the model, and its unique identifier is set for the current profile.

        Args:
            profile_name (str): The name of the profile to set. If it does not exist,
                a new profile is created with this name.

        Raises:
            ValueError: If the profile name is invalid or cannot be processed.
        """

        n = [x.name for x in self.model.profiles if x.name == profile_name]
        if len(n) == 1:
            self._profile = n[0]
        else:
            # add a new profile to the model
            p = self.model.add_profile(name=profile_name, concept=self.type)
            self._profile = p.uuid

    def reset_profile(self):
        self._profile = None


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


try:
    from . import _legacy as _legacy_module
except ImportError:
    _legacy_module = None

if _legacy_module and hasattr(_legacy_module, "register_relationship"):
    _legacy_module.register_relationship(Relationship)


__all__ = ["Relationship"]
