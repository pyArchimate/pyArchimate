# ruff: noqa: N999  # legacy module name preserved for API compatibility
"""
File reader for native Archimate Tool .archimate file format
"""

import os
import sys

try:
    from ..helpers.logging import log
    from ._archireader_helpers import get_folders_elem, get_folders_rel, get_folders_view
except ImportError:
    sys.path.insert(0, "..")
    from pyArchimate import log  # noqa: F401
    from pyArchimate.readers._archireader_helpers import (
        get_folders_elem,
        get_folders_rel,
        get_folders_view,
    )

__mod__ = __name__.split(".")[len(__name__.split(".")) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def _rebuild_hierarchy_from_parent_id(model, root):
    """Rebuild parent-child hierarchy from parentId attributes in XML.

    This is called after all elements have been loaded to establish
    the hierarchy relationships based on parentId attributes.

    :param model: pyArchimate Model object
    :param root: XML root element
    """
    xsi = "{http://www.w3.org/2001/XMLSchema-instance}"

    def _process_hierarchy(folder_elem):
        """Recursively process folders to find elements with parentId."""
        for elem in folder_elem.findall("element"):
            elem_id = elem.get("id")
            parent_id = elem.get("parentId")

            # Only process non-relationship, non-view elements
            type_attr = elem.get(xsi + "type", "")
            if "Relationship" in type_attr or "ArchimateDiagramModel" in type_attr:
                continue

            # If element has parentId and both parent and child exist, establish relationship
            if parent_id and elem_id in model.elems_dict and parent_id in model.elems_dict:
                try:
                    model.add_child(parent_id, elem_id)
                except (ValueError, KeyError) as e:
                    # Element might already have parent or relationship might be invalid
                    # This is acceptable during merge operations
                    log.debug(f"Failed to establish parent-child relationship: {e}")

        for folder in folder_elem.findall("folder"):
            _process_hierarchy(folder)

    for folder in root.findall("folder"):
        _process_hierarchy(folder)


def archi_reader(model, root, merge_flg=False):
    """
    Merge / initialize the model from XML Archimate OEF data

    Used by Model.read(filepath) or Model.merge(filepath) methods

    :param model: pyArchimate Model object
    :type model: Model
    :param root:    XML data to convert
    :type root:
    :param merge_flg: if True, merge data into the provided model, else clear the model and read data into it
    :type merge_flg: bool

    """
    if "archimate" not in root.tag:
        log.fatal(f"{__mod__}: Input file is not an Open Group Archimate file - Aborting")
        return None

    xsi = "{http://www.w3.org/2001/XMLSchema-instance}"

    model.name = root.get("name")
    model.desc = None if root.find("purpose") is None else root.find("purpose").text

    for p in root.findall("property"):
        model.prop(p.get("key"), p.get("value"))

    if root.find("profile") is not None:
        for p in root.findall("profile"):
            concept_type = p.get("conceptType")
            if "Relationship" in concept_type:
                concept_type = concept_type[: -len("Relationship")]
            model.add_profile(p.get("name"), p.get("id"), concept_type)

    for f in root.findall("folder"):
        get_folders_elem(f, model, xsi, merge_flg)
    for f in root.findall("folder"):
        get_folders_rel(f, model, xsi, merge_flg)
    for f in root.findall("folder"):
        get_folders_view(f, model, xsi)

    # Rebuild hierarchy from parentId attributes after all elements are loaded
    _rebuild_hierarchy_from_parent_id(model, root)
