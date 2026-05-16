"""pyArchimate: Python library for creating and manipulating ArchiMate diagrams.

Provides tools for reading/writing .archimate files, managing models and views,
and rendering diagrams to various formats. Supports ArchiMate 3.x specification.
"""
# ruff: noqa: N999  # legacy module name preserved for API compatibility
from .helpers.diagram import get_or_create_connection as get_or_create_connection  # noqa: E501
from .helpers.diagram import get_or_create_node as get_or_create_node
from .helpers.logging import log as log  # noqa: E501
from .helpers.logging import log_set_level as log_set_level
from .helpers.logging import log_to_file as log_to_file
from .helpers.logging import log_to_stderr as log_to_stderr
from .helpers.parsing import parse_bool as parse_bool  # noqa: E501
from .helpers.properties import check_invalid_conn as check_invalid_conn  # noqa: E501
from .helpers.properties import check_invalid_nodes as check_invalid_nodes
from .helpers.properties import embed_props as embed_props
from .helpers.properties import expand_props as expand_props
from .pyArchimate import *  # noqa: F401,F403
