# ruff: noqa: N999  # legacy module name preserved for API compatibility
"""Helper modules for diagram, property, logging, and parsing utilities."""

from .diagram import apply_profile_styles, get_or_create_connection, get_or_create_node
from .logging import log, log_set_level, log_to_file, log_to_stderr
from .parsing import compare_image_data, extract_images_from_archimate, parse_bool
from .properties import check_invalid_conn, check_invalid_nodes, embed_props, expand_props

__all__ = [
    "apply_profile_styles",
    "get_or_create_connection",
    "get_or_create_node",
    "check_invalid_conn",
    "check_invalid_nodes",
    "embed_props",
    "expand_props",
    "log",
    "log_set_level",
    "log_to_file",
    "log_to_stderr",
    "parse_bool",
    "extract_images_from_archimate",
    "compare_image_data",
]
