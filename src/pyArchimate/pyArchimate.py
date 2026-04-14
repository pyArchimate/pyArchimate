"""Compatibility shim that re-exports legacy and modular APIs."""

import math  # noqa: F401 - re-exported for legacy callers that do `from pyArchimate import *`

try:
    from ._legacy import *  # type: ignore[import-not-found]  # noqa: F401,F403
except ImportError:
    # Fallback when legacy module is absent; rely on new modules only.
    pass

# All imports below are intentional re-exports — this file is a public API shim.
from .constants import ARCHI_CATEGORY as archi_category  # noqa: F401
from .constants import ARIS_TYPE_MAP as ARIS_type_map  # noqa: F401
from .constants import DEFAULT_THEME as default_theme  # noqa: F401
from .constants import RGBA as RGBA  # noqa: F401
from .element import Element as Element  # noqa: F401
from .element import set_id as set_id
from .enums import AccessType as AccessType  # noqa: F401,E501
from .enums import ArchiType as ArchiType
from .enums import Readers as Readers
from .enums import TextAlignment as TextAlignment
from .enums import TextPosition as TextPosition
from .enums import Writers as Writers
from .exceptions import ArchimateConceptTypeError as ArchimateConceptTypeError  # noqa: F401,E501
from .exceptions import ArchimateRelationshipError as ArchimateRelationshipError
from .helpers.diagram import get_or_create_connection as get_or_create_connection  # noqa: F401,E501
from .helpers.diagram import get_or_create_node as get_or_create_node
from .helpers.logging import log as log  # noqa: F401,E501
from .helpers.logging import log_set_level as log_set_level
from .helpers.logging import log_to_file as log_to_file
from .helpers.logging import log_to_stderr as log_to_stderr
from .helpers.properties import check_invalid_conn as check_invalid_conn  # noqa: F401,E501
from .helpers.properties import check_invalid_nodes as check_invalid_nodes
from .helpers.properties import embed_props as embed_props
from .helpers.properties import expand_props as expand_props
from .model import Model as Model  # noqa: F401
from .model import default_color as default_color
from .relationship import Relationship as Relationship  # noqa: F401,E501
from .relationship import check_valid_relationship as check_valid_relationship
from .relationship import get_default_rel_type as get_default_rel_type
from .view import Connection as Connection  # noqa: F401,E501
from .view import Node as Node
from .view import Point as Point
from .view import Position as Position
from .view import Profile as Profile
from .view import View as View
from .writers import register_writer as register_writer  # noqa: F401

__all__ = [name for name in globals() if not name.startswith("_")]  # pyright: ignore[reportUnsupportedDunderAll]
