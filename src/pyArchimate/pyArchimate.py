"""Compatibility shim that re-exports legacy and modular APIs."""

try:
    from ._legacy import *  # noqa: F401,F403
    from .element import Element
    from .helpers.diagram import get_or_create_connection, get_or_create_node
    from .helpers.logging import log, log_set_level, log_to_file, log_to_stderr
    from .helpers.properties import check_invalid_conn, check_invalid_nodes, embed_props, expand_props
    from .model import Model
    from .relationship import Relationship
except ImportError:
    from _legacy import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
