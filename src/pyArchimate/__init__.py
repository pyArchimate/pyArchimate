import os
import sys
import lxml.etree as et
from collections import defaultdict
# sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from .logger import log, log_set_level, log_to_stderr, log_to_file
from .pyArchimate import Model, View, Element, Node, Relationship, AccessType, archi_category, set_id, ARIS_type_map, \
    ArchimateRelationshipError, ArchimateConceptTypeError, get_default_rel_type, Point, RGBA, ArchiType, \
    check_valid_relationship, default_color, default_theme, TextPosition, TextAlignment, Position
