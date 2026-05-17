"""Element module - extracted from the legacy monolith."""

import re
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID, uuid4

from .constants import ARCHI_CATEGORY, JUNCTION_TYPES, NAMED_COLORS
from .enums import ArchiType
from .exceptions import ArchimateConceptTypeError
from .viewpoint_registry import validate_viewpoint_slug

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
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def set_id(uuid: str | None = None) -> str:
    """
    Function to create an identifier if none exists

    :param uuid: a uuid
    :cat uuid: str
    :return: a formatted identifier
    :rtype: str

    """
    _id = str(uuid4()) if (uuid is None) else uuid
    if _is_valid_uuid(_id):
        _id = _id.replace("-", "")
        if not _id.startswith("id-"):
            _id = "id-" + _id
    return _id


def _normalize_color(color: str | None) -> str | None:
    """
    Normalize a color to lowercase hex format.

    :param color: Color as hex (#RRGGBB) or named color, or None
    :return: Normalized hex color (#rrggbb) or None
    :raises ValueError: If color format is invalid or color name unknown
    """
    if color is None:
        return None
    color = str(color).strip()
    if color.startswith("#"):
        if not re.match(r"^#[0-9a-fA-F]{6}$", color):
            raise ValueError(f"Invalid hex color: {color} (expected #RRGGBB)")
        return color.lower()
    named = NAMED_COLORS.get(color.lower())
    if named:
        return named
    raise ValueError(f"Unknown color: {color} (hex or named color expected)")


class Element:
    """
    Class to manage Element artifacts with visual styling and hierarchy support.

    Supports ArchiMate v3.x elements with optional parent-child relationships,
    custom visual styles (colors, transparency), and junction type semantics.

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

    **Visual Styling (P3)**:
    - Use set_fill_color(color), set_line_color(color) to customize appearance
    - Supports hex colors (#RRGGBB) and named colors (e.g., 'red', 'blue')
    - Use set_line_width(width) and set_transparency(alpha) for additional styling
    - All visual properties are preserved during XML export/import round-trips

    **Hierarchy (P3)**:
    - Elements can be organized into parent-child relationships via Model.add_child()
    - Use get_parent() to retrieve parent, get_siblings() for neighbors
    - Junction elements (AND/OR/XOR) use set_junction_type() for semantics

    **Junction Types (P3)**:
    - Junction elements support type validation: 'and', 'or', 'xor'
    - Use set_junction_type(type_str) to set junction semantics
    - Junction types are validated on set and preserved in round-trip exports

    :raises ArchimateConceptTypeError: Exception raised on elem_type or parent type error

    :return: Element object
    :rtype: Element

    Example::

        from pyArchimate import ArchiType
        from pyArchimate.model import Model
        m = Model('example')

        # Create elements
        process = m.add(ArchiType.BusinessProcess, 'Order Processing')
        func = m.add(ArchiType.BusinessFunction, 'Order Fulfillment')
        junction = m.add(ArchiType.Junction, 'Decision Point')

        # Build hierarchy
        m.add_child(process.uuid, func.uuid)

        # Style elements
        process.set_fill_color('#ffeb3b')
        process.set_transparency(0.9)

        # Set junction semantics
        junction.set_junction_type('and')

    """

    def __init__(self, elem_type=None, name=None, uuid=None, desc=None, folder=None, parent=None, profile=None):
        """Initialize an ArchiMate element with type, name, and parent model."""
        # Check validity of arguments according to Archimate standard
        if elem_type is None or not hasattr(ArchiType, elem_type):
            raise ArchimateConceptTypeError(f"Invalid Element type '{elem_type}'")
        if ARCHI_CATEGORY[elem_type] == "Relationship":
            raise ArchimateConceptTypeError(f"Element type '{elem_type}' cannot be a Relationship type")
        if parent is not None and not hasattr(parent, "elems_dict"):
            raise ValueError("Element class parent should be a class Model instance!")

        # Attribute and data structure initialization
        self._uuid: str = set_id(uuid)
        self.parent: Model = cast("Model", parent)
        self.model: Model = cast("Model", parent)
        self.name: str | None = name
        self._type: str | None = elem_type
        self.desc: str | None = desc
        self.folder: str | None = folder
        self._properties: dict[str, object] = {}
        self._profile: str | None = profile
        self.junction_type: str | None = None
        self._viewpoints: list[str] = []  # list of canonical viewpoint slugs
        self._parent_uuid: str | None = None
        self._visual_style: dict[str, Any] = {}

    def _delete_view_refs(self, _id: str) -> None:
        for n in self.parent.nodes_dict.copy().values():
            if n.ref == _id:
                n.delete()
                del n
        for r in self.parent.rels_dict.copy().values():
            if r.source.uuid == _id or r.target.uuid == _id:
                r.delete()
                del r

    def _orphan_children(self, _id: str) -> None:
        for child_uuid in self.parent._element_children.get(_id, set()).copy():
            child = self.parent.elems_dict.get(child_uuid)
            if child:
                child._parent_uuid = None
            if child_uuid in self.parent._element_hierarchy:
                del self.parent._element_hierarchy[child_uuid]
        if _id in self.parent._element_children:
            del self.parent._element_children[_id]

    def delete(self) -> None:
        """
        Delete the current element from the parent model
        Note: it does not delete the instance itself but it remove the data from the model

        It also deletes all relationships that have this element as source or target and
        it deletes all visual nodes referring to this element (and conns) from views

        Children are orphaned rather than cascaded (Phase 2 behavior).
        """
        _id = self.uuid
        self._delete_view_refs(_id)

        # P3 Phase 2: Clean up stale viewpoint references
        for vp_id in self._viewpoints:
            self.parent._viewpoint_elements.get(vp_id, set()).discard(_id)

        self._orphan_children(_id)

        # P3 Phase 2: Remove self from parent's children
        if self._parent_uuid is not None:
            self.parent._element_children.get(self._parent_uuid, set()).discard(_id)
            if _id in self.parent._element_hierarchy:
                del self.parent._element_hierarchy[_id]

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
    def type(self) -> str | None:  # noqa: A003  # 'type' is the canonical ArchiMate attribute name; renaming would break public API
        """
        Get the Archimate concept type of this element

        :return:    type str
        :rtype: str
        """
        return self._type

    @type.setter  # noqa: A003  # 'type' is the canonical ArchiMate attribute name; renaming would break public API
    def type(self, value):
        """
        Convert this element to a new Archimate concept type
        Note: this is potentially dangerous as existing relationships may become invalid
        No check if performed on the relationship validity afet conversion

        :param value:
        :type value: str

        """
        if value is not None:
            if value not in ARCHI_CATEGORY or ARCHI_CATEGORY[value] == "Relationship":
                raise ValueError("Invalid Archimate element type")
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

    def reset_profile(self) -> None:
        """Clear the profile assignment."""
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
            self.desc = (self.desc or "") + "\n----\n" + (elem.desc or "")

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
            raise ValueError("Merged element has not the same type as target")

        # merge elem into the current one
        if merge_props:
            self._merge_properties_and_desc(elem)

        # Re-assign othe element related node references to this element (merge target)
        for n in [self.model.nodes_dict[x] for x in self.model.nodes_dict if self.model.nodes_dict[x].ref == elem.uuid]:
            n.ref = self.uuid

        # Re-assign other element inboud and outbound relationship references to this element
        for r in self.model.filter_relationships(lambda x: x.target is not None and x.target.uuid == elem.uuid):
            r.target = self

        for r in self.model.filter_relationships(lambda x: x.source is not None and x.source.uuid == elem.uuid):
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
            return self.model.filter_relationships(lambda x: x.target is not None and x.target.uuid == self.uuid)
        else:
            return self.model.filter_relationships(
                lambda x: x.target is not None and x.target.uuid == self.uuid and x.type == rel_type
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
            return self.model.filter_relationships(lambda x: x.source is not None and x.source.uuid == self.uuid)
        else:
            return self.model.filter_relationships(
                lambda x: x.source is not None and x.source.uuid == self.uuid and x.type == rel_type
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
            return self.model.filter_relationships(
                lambda x: (
                    (x.target is not None and x.target.uuid == self.uuid)
                    or (x.source is not None and x.source.uuid == self.uuid)
                )
            )
        else:
            return self.model.filter_relationships(
                lambda x: (
                    (
                        (x.target is not None and x.target.uuid == self.uuid)
                        or (x.source is not None and x.source.uuid == self.uuid)
                    )
                    and x.type == rel_type
                )
            )

    def remove_folder(self):
        """
        Method to remove this element from the given folder path

        """
        self.folder = None

    @property
    def viewpoints(self) -> list[str]:
        """Return the list of assigned viewpoint slugs.

        :return: list of canonical viewpoint slug strings
        :rtype: list[str]
        """
        return list(self._viewpoints)

    def assign_viewpoint(self, viewpoint_id: str) -> None:
        """Assign a standard ArchiMate 3.x viewpoint slug to this element.

        :param viewpoint_id: canonical viewpoint slug (e.g. 'stakeholder')
        :type viewpoint_id: str
        :raises ValueError: if viewpoint_id is not a recognised slug
        """
        validate_viewpoint_slug(viewpoint_id)
        if viewpoint_id not in self._viewpoints:
            self._viewpoints.append(viewpoint_id)
            if self.parent is not None:
                vp_elems = self.parent._viewpoint_elements.setdefault(viewpoint_id, set())
                vp_elems.add(self._uuid)

    def remove_viewpoint(self, viewpoint_id: str) -> None:
        """Remove a viewpoint slug assignment; silently ignores unknown slugs.

        :param viewpoint_id: canonical viewpoint slug to remove
        :type viewpoint_id: str
        """
        if viewpoint_id in self._viewpoints:
            self._viewpoints.remove(viewpoint_id)
            if self.parent is not None:
                self.parent._viewpoint_elements.get(viewpoint_id, set()).discard(self._uuid)

    @property
    def parent_uuid(self) -> str | None:
        """Get the parent element UUID (for hierarchical grouping).

        :return: Parent element UUID or None if this is a root element
        :rtype: Optional[str]
        """
        return self._parent_uuid

    def set_fill_color(self, color: str | None) -> None:
        """Set the fill color of this element.

        :param color: Hex color (#RRGGBB), named color, or None to use default
        :type color: Optional[str]
        :raises ValueError: If color format is invalid
        """
        if color is None:
            self._visual_style.pop("fillColor", None)
        else:
            self._visual_style["fillColor"] = _normalize_color(color)

    def set_line_color(self, color: str | None) -> None:
        """Set the line/border color of this element.

        :param color: Hex color (#RRGGBB), named color, or None to use default
        :type color: Optional[str]
        :raises ValueError: If color format is invalid
        """
        if color is None:
            self._visual_style.pop("lineColor", None)
        else:
            self._visual_style["lineColor"] = _normalize_color(color)

    def set_line_width(self, width: float | None) -> None:
        """Set the line/border width of this element.

        :param width: Width in pixels (≥ 0), or None to use default
        :type width: Optional[float]
        :raises ValueError: If width is negative
        :raises TypeError: If width is not numeric
        """
        if width is None:
            self._visual_style.pop("lineWidth", None)
        else:
            if not isinstance(width, (int, float)):
                raise TypeError(f"Line width must be number, got {type(width).__name__}")
            if width < 0:
                raise ValueError(f"Line width must be non-negative number, got {width}")
            self._visual_style["lineWidth"] = float(width)

    def set_transparency(self, alpha: float | None) -> None:
        """Set the transparency/opacity of this element.

        :param alpha: Opacity 0.0 (transparent) to 1.0 (opaque), or None to use default
        :type alpha: Optional[float]
        :raises ValueError: If alpha is out of range
        :raises TypeError: If alpha is not numeric
        """
        if alpha is None:
            self._visual_style.pop("transparency", None)
        else:
            if not isinstance(alpha, (int, float)):
                raise TypeError(f"Transparency must be number, got {type(alpha).__name__}")
            if alpha < 0.0 or alpha > 1.0:
                raise ValueError(f"Transparency must be 0.0-1.0, got {alpha}")
            self._visual_style["transparency"] = float(alpha)

    def set_visual_style(
        self,
        fill_color: str | None = None,
        line_color: str | None = None,
        line_width: float | None = None,
        transparency: float | None = None,
    ) -> None:
        """Set multiple visual style properties at once.

        :param fill_color: Fill color (hex or named)
        :param line_color: Line color (hex or named)
        :param line_width: Line width in pixels (≥ 0)
        :param transparency: Opacity 0.0-1.0
        :raises ValueError: If any property is invalid
        """
        if fill_color is not None:
            self.set_fill_color(fill_color)
        if line_color is not None:
            self.set_line_color(line_color)
        if line_width is not None:
            self.set_line_width(line_width)
        if transparency is not None:
            self.set_transparency(transparency)

    def get_fill_color(self) -> str | None:
        """Get the fill color of this element.

        :return: Hex color (#rrggbb) or None if not set (use default)
        :rtype: Optional[str]
        """
        return self._visual_style.get("fillColor")

    def get_line_color(self) -> str | None:
        """Get the line/border color of this element.

        :return: Hex color (#rrggbb) or None if not set (use default)
        :rtype: Optional[str]
        """
        return self._visual_style.get("lineColor")

    def get_line_width(self) -> float | None:
        """Get the line/border width of this element.

        :return: Width in pixels or None if not set (use default)
        :rtype: Optional[float]
        """
        return self._visual_style.get("lineWidth")

    def get_transparency(self) -> float | None:
        """Get the transparency/opacity of this element.

        :return: Opacity 0.0-1.0 or None if not set (use default)
        :rtype: Optional[float]
        """
        return self._visual_style.get("transparency")

    def get_visual_style(self) -> dict[str, Any]:
        """Get all visual style properties as a dictionary.

        :return: Dictionary with fillColor, lineColor, lineWidth, transparency (only set values)
        :rtype: dict[str, Any]
        """
        return dict(self._visual_style)

    def reset_visual_style(self) -> None:
        """Reset all custom visual styles to defaults.

        :return: None
        """
        self._visual_style.clear()

    def set_junction_type(self, junction_type: str | None) -> None:
        """
        Set the junction type for a Junction element.

        :param junction_type: Junction type ('and', 'or', 'xor') or None
        :type junction_type: Optional[str]
        :raises ValueError: If junction_type is not valid
        """
        if junction_type is None:
            self.junction_type = None
            return
        junction_type_lower = str(junction_type).lower().strip()
        if junction_type_lower not in JUNCTION_TYPES:
            raise ValueError(f"Invalid junction type: {junction_type}. Must be one of {JUNCTION_TYPES}")
        self.junction_type = junction_type_lower

    def get_junction_type(self) -> str | None:
        """
        Get the junction type for a Junction element.

        :return: Junction type ('and', 'or', 'xor') or None if not set
        :rtype: Optional[str]
        """
        return self.junction_type


__all__ = ["Element"]
