"""Element module - extracted from the legacy monolith."""

from typing import TYPE_CHECKING, Optional, cast

from .constants import ARCHI_CATEGORY
from .enums import ArchiType
from .exceptions import ArchimateConceptTypeError

if TYPE_CHECKING:
    from .model import Model


def _is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

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
    from uuid import UUID

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def set_id(uuid: Optional[str] = None) -> str:
    """
    Function to create an identifier if none exists

    :param uuid: a uuid
    :cat uuid: str
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
    :param profile: element profile identifier
    :type profile: str

    :raises ArchimateConceptTypeError: Exception raised on elem_type or parent tyme error

    :return: Element object
    :rtype: Element

    """

    def __init__(self, elem_type=None, name=None, uuid=None, desc=None, folder=None, parent=None, profile=None):

        # Check validity of arguments according to Archimate standard
        if elem_type is None or not hasattr(ArchiType, elem_type):
            raise ArchimateConceptTypeError(f"Invalid Element type '{elem_type}'")
        if ARCHI_CATEGORY[elem_type] == 'Relationship':
            raise ArchimateConceptTypeError(f"Element type '{elem_type}' cannot be a Relationship type")
        if parent is not None and not hasattr(parent, "elems_dict"):
            raise ValueError('Element class parent should be a class Model instance!')

        # Attribute and data structure initialization
        self._uuid: str = set_id(uuid)
        self.parent: "Model" = cast("Model", parent)
        self.model: "Model" = cast("Model", parent)
        self.name: Optional[str] = name
        self._type: Optional[str] = elem_type
        self.desc: Optional[str] = desc
        self.folder: Optional[str] = folder
        self._properties: dict[str, object] = {}
        self._profile: Optional[str] = profile
        self.junction_type: Optional[str] = None

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
    def uuid(self) -> str:
        """
        Get the identifier of this element

        :return:    Identifier str
        :rtype: str
        """
        return self._uuid

    @property
    def type(self) -> Optional[str]:
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
            if value not in ARCHI_CATEGORY or ARCHI_CATEGORY[value] == 'Relationship':
                raise ValueError('Invalid Archimate element type')
            self._type = value

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
        Sets the current profile for an instance. If the specified profile name already
        exists in the model, it sets the profile to the matching profile. Otherwise,
        a new profile is created, added to the model, and set as the current profile.

        Parameters:
            profile_name (str): The name of the profile to set. If it exists in the
            model, it will be used directly. If not, a new profile with this name
            will be created and used.

        Raises:
            No exceptions are explicitly raised in this method.
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

    def _merge_properties_and_desc(self, elem: "Element") -> None:
        for key, val in elem.props.items():
            if key not in self.props:
                self.prop(key, val)
        if elem.desc != self.desc:
            self.desc = (self.desc or '') + '\n----\n' + (elem.desc or '')

    def merge(self, elem: "Element", merge_props: bool = False) -> None:
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
            self._merge_properties_and_desc(elem)

        # Re-assign othe element related node references to this element (merge target)
        for n in [self.model.nodes_dict[x] for x in self.model.nodes_dict if self.model.nodes_dict[x].ref == elem.uuid]:
            n.ref = self.uuid

        # Re-assign other element inboud and outbound relationship references to this element
        for r in self.model.filter_relationships(lambda x: (x.target is not None and x.target.uuid == elem.uuid)):
            r.target = self

        for r in self.model.filter_relationships(lambda x: (x.source is not None and x.source.uuid == elem.uuid)):
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
            return self.model.filter_relationships(lambda x: (x.target is not None and x.target.uuid == self.uuid))
        else:
            return self.model.filter_relationships(lambda x: (
                    x.target is not None and x.target.uuid == self.uuid
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
            return self.model.filter_relationships(lambda x: (x.source is not None and x.source.uuid == self.uuid))
        else:
            return self.model.filter_relationships(lambda x: (
                    x.source is not None and x.source.uuid == self.uuid
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
                    (x.target is not None and x.target.uuid == self.uuid)
                    or
                    (x.source is not None and x.source.uuid == self.uuid))
                                                   )
        else:
            return self.model.filter_relationships(lambda x: (
                    ((x.target is not None and x.target.uuid == self.uuid) or (x.source is not None and x.source.uuid == self.uuid))
                    and
                    x.type == rel_type)
                                                   )

    def remove_folder(self):
        """
        Method to remove this element from the given folder path

        """
        self.folder = None


__all__ = ["Element"]
