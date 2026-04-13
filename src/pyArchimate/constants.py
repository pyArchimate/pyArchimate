"""
Constants and configuration values for the Archimate library.

This module contains module-level constants, magic numbers, configuration values,
and registry structures used throughout pyArchimate.

No external pyArchimate imports - this is a Layer 1 base module.
"""

import os
from dataclasses import dataclass
from typing import Any, Callable

import oyaml as yaml

# ===== Configuration Constants =====

# Default theme for diagram rendering
DEFAULT_THEME = 'archi'

# ===== Message Constants =====

OPERATION_ERROR_MESSAGES = {
    'read': 'Unsupported input format',
    'merge': 'Unsupported input format for merge operation',
}

# ===== Registry Dictionaries (initialized at module load) =====

# Dictionary of valid Archimate relationships
# This is populated dynamically by loading checker_rules.yml
ALLOWED_RELATIONSHIPS = {}

# Mapping of ARIS types to Archimate types
ARIS_TYPE_MAP = {}

# Mapping of relationship keys
RELATIONSHIP_KEYS = {}

# Mapping of Archimate element categories
ARCHI_CATEGORY = {}

# Influence strength values
INFLUENCE_STRENGTH = {
    '+': '+',
    '++': '++',
    '-': '-',
    '--': '--',
    '0': '0',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9',
    '10': '10'
}

# ===== Reader/Writer Configuration =====


@dataclass
class ReaderEntry:
    """
    Registry entry describing how to select and call a reader based on the root tag.
    """

    tag_key: str
    loader: Callable[[], Callable[..., Any]]
    supports_merge: bool = False
    forward_read_args: bool = False


def _load_archimate_reader():
    """Load the Archimate XML reader dynamically."""
    from .readers.archimateReader import archimate_reader
    return archimate_reader


def _load_archi_reader():
    """Load the Archi project reader dynamically."""
    from .readers.archiReader import archi_reader
    return archi_reader


def _load_aris_reader():
    """Load the ARIS AML reader dynamically."""
    from .readers.arisAMLreader import aris_reader
    return aris_reader


# Model reader registry - defines available readers and their loaders
MODEL_READER_REGISTRY = [
    ReaderEntry(
        tag_key='opengroup',
        loader=_load_archimate_reader,
        supports_merge=True
    ),
    ReaderEntry(
        tag_key='archimate',
        loader=_load_archi_reader,
        supports_merge=True
    ),
    ReaderEntry(
        tag_key='aml',
        loader=_load_aris_reader,
        forward_read_args=True
    ),
]

# Writer registry (populated at runtime by _ensure_default_writers)
WRITER_REGISTRY: dict[Any, Any] = {}
DEFAULT_WRITERS_INITIALIZED = False


# ===== Module Initialization =====
# Load checker_rules.yml to populate the metadata dictionaries

def _initialize_archimate_metadata():
    """Load Archimate metadata from checker_rules.yml."""
    try:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        checker_rules_path = os.path.join(__location__, "checker_rules.yml")

        with open(checker_rules_path, "r") as fd:
            data = yaml.load(fd, Loader=yaml.Loader)

        # Populate the global dictionaries
        if 'archimate_rels' in data:
            ALLOWED_RELATIONSHIPS.update(data['archimate_rels'])
        if 'ARIS_type_map' in data:
            ARIS_TYPE_MAP.update(data['ARIS_type_map'])
        if 'relationship_keys' in data:
            RELATIONSHIP_KEYS.update(data['relationship_keys'])
        if 'archi_category' in data:
            ARCHI_CATEGORY.update(data['archi_category'])
    except Exception as e:
        # Log but don't fail - this allows the module to load even if checker_rules.yml is missing
        print(f"Warning: Could not load Archimate metadata from checker_rules.yml: {e}")


# Initialize on module load
_initialize_archimate_metadata()


# ===== Color Utilities =====

class RGBA:
    """Manage RGB/hex color and alpha (opacity) channels.

    :param r: red channel 0-255
    :param g: green channel 0-255
    :param b: blue channel 0-255
    :param a: alpha channel 0-100
    """

    def __init__(self, r=0, g=0, b=0, a=100):
        self.r = max(0, min(255, int(r)))
        self.g = max(0, min(255, int(g)))
        self.b = max(0, min(255, int(b)))
        self.a = max(0, min(100, int(a)))

    @property
    def color(self):
        """Return #RRGGBB hex string."""
        return '#{0:02x}{1:02x}{2:02x}'.format(self.r, self.g, self.b).upper()

    @color.setter
    def color(self, color_string):
        """Set RGB from a #RRGGBB hex string."""
        if color_string is not None:
            self.r = int(color_string[1:3], 16)
            self.g = int(color_string[3:5], 16)
            self.b = int(color_string[5:], 16)

