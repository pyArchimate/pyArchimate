"""
*   Conversion program from ARIS AML xml file to Archimate Open Exchange File format
*   Author: X. Mayeur
*   Date: October 2022
*   Version 0.9
*
*
"""
import sys
from typing import Any

try:
    from ..helpers.logging import log
    from ..model import Model
    from ._arisamlreader_helpers import (
        clean_nested_conns,
        get_text_size,
        id_of,
        parse_elements,
        parse_labels,
        parse_relationships,
        parse_views,
    )
except ImportError:
    sys.path.insert(0, "..")
    from pyArchimate import Model, log  # type: ignore[no-redef,attr-defined]
    from pyArchimate.readers._arisamlreader_helpers import (
        clean_nested_conns,
        get_text_size,
        id_of,
        parse_elements,
        parse_labels,
        parse_relationships,
        parse_views,
    )

# Re-export for backward compatibility
_id_of = id_of
__all__ = ['aris_reader', 'get_text_size', '_id_of', 'id_of']


def aris_reader(model: Model, root: Any,
                scale_x: float = 0.3, scale_y: float = 0.3, no_view: bool = False) -> None:
    """
    Class to perform the parsing of ARIS AML data and to generate an Archimate model

    :param model:       Model to read in
    :type model:        Model
    :param root:        XML data in Aris Markup Language
    :param scale_x:     X-Scaling factor in converting views
    :type scale_x:      float
    :param scale_y:     Y-Scaling factor in converting views
    :type scale_y:      float
    :param no_view:     if true do not generate views
    """
    if root.tag != 'AML':
        log.fatal(' Input file is not an ARIS AML file - Aborting')
        sys.exit(1)

    scale_x = float(scale_x)
    scale_y = float(scale_y)

    log.info('Parsing elements')
    parse_elements(None, root, model)
    log.info('Parsing relationships')
    parse_relationships(None, root, model)

    if not no_view:
        log.info('Parsing Labels')
        parse_labels(root, model)
        log.info('Parsing Views')
        parse_views(None, root, model, scale_x, scale_y)
        clean_nested_conns(model)

    model.expand_props(clean_doc=True)
    log.info('Performing final model validation checks')
    inv_c = model.check_invalid_conn()
    inv_n = model.check_invalid_nodes()
    if len(inv_n) > 0 or len(inv_c) > 0:
        log.error("Errors found in the model")
        print(inv_n)
        print(inv_c)
