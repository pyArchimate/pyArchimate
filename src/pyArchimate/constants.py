"""
Constants and configuration values for the Archimate library.

This module contains module-level constants, magic numbers, configuration values,
and registry structures used throughout pyArchimate.

No external pyArchimate imports - this is a Layer 1 base module.
"""

import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import oyaml as yaml  # type: ignore[import-untyped]

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
ALLOWED_RELATIONSHIPS: dict[str, dict[str, list[str]]] = {}

# Mapping of ARIS types to Archimate types
ARIS_TYPE_MAP: dict[str, str] = {}

# Mapping of relationship keys
RELATIONSHIP_KEYS: dict[str, str] = {}

# Mapping of Archimate element categories
ARCHI_CATEGORY: dict[str, str] = {}

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

# Junction types (for Junction elements)
JUNCTION_TYPES = {'and', 'or', 'xor'}

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
    from .readers.archimateReader import (
        archimate_reader,  # noqa: PLC0415  # deferred: readers import from constants, must not be top-level
    )
    return archimate_reader


def _load_archi_reader():
    """Load the Archi project reader dynamically."""
    from .readers.archiReader import (
        archi_reader,  # noqa: PLC0415  # deferred: readers import from constants, must not be top-level
    )
    return archi_reader


def _load_aris_reader():
    """Load the ARIS AML reader dynamically."""
    from .readers.arisAMLreader import (
        aris_reader,  # noqa: PLC0415  # deferred: readers import from constants, must not be top-level
    )
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

        with open(checker_rules_path) as fd:
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
        return '#{:02x}{:02x}{:02x}'.format(self.r, self.g, self.b).upper()

    @color.setter
    def color(self, color_string):
        """Set RGB from a #RRGGBB hex string."""
        if color_string is not None:
            self.r = int(color_string[1:3], 16)
            self.g = int(color_string[3:5], 16)
            self.b = int(color_string[5:], 16)


# ===== P3 Element Grouping & Visual Style Constants =====

# Maximum nesting depth for element hierarchies
MAX_DEPTH = 5

# CSS/X11 named colors (140+)
NAMED_COLORS: dict[str, str] = {
    'aliceblue': '#f0f8ff', 'antiquewhite': '#faebd7', 'aqua': '#00ffff',
    'aquamarine': '#7fffd4', 'azure': '#f0ffff', 'beige': '#f5f5dc',
    'bisque': '#ffe4c4', 'black': '#000000', 'blanchedalmond': '#ffebcd',
    'blue': '#0000ff', 'blueviolet': '#8a2be2', 'brown': '#a52a2a',
    'burlywood': '#deb887', 'cadetblue': '#5f9ea0', 'chartreuse': '#7fff00',
    'chocolate': '#d2691e', 'coral': '#ff7f50', 'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc', 'crimson': '#dc143c', 'cyan': '#00ffff',
    'darkblue': '#00008b', 'darkcyan': '#008b8b', 'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9', 'darkgrey': '#a9a9a9', 'darkgreen': '#006400',
    'darkkhaki': '#bdb76b', 'darkmagenta': '#8b008b', 'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00', 'darkorchid': '#9932cc', 'darkred': '#8b0000',
    'darksalmon': '#e9967a', 'darkseagreen': '#8fbc8f', 'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f', 'darkslategrey': '#2f4f4f', 'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3', 'deeppink': '#ff1493', 'deepskyblue': '#00bfff',
    'dimgray': '#696969', 'dimgrey': '#696969', 'dodgerblue': '#1e90ff',
    'firebrick': '#b22222', 'floralwhite': '#fffaf0', 'forestgreen': '#228b22',
    'fuchsia': '#ff00ff', 'gainsboro': '#dcdcdc', 'ghostwhite': '#f8f8ff',
    'gold': '#ffd700', 'goldenrod': '#daa520', 'gray': '#808080',
    'grey': '#808080', 'green': '#008000', 'greenyellow': '#adff2f',
    'honeydew': '#f0fff0', 'hotpink': '#ff69b4', 'indianred': '#cd5c5c',
    'indigo': '#4b0082', 'ivory': '#fffff0', 'khaki': '#f0e68c',
    'lavender': '#e6e6fa', 'lavenderblush': '#fff0f5', 'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd', 'lightblue': '#add8e6', 'lightcoral': '#f08080',
    'lightcyan': '#e0ffff', 'lightgoldenrodyellow': '#fafad2', 'lightgray': '#d3d3d3',
    'lightgrey': '#d3d3d3', 'lightgreen': '#90ee90', 'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a', 'lightseagreen': '#20b2aa', 'lightskyblue': '#87cefa',
    'lightslategray': '#778899', 'lightslategrey': '#778899', 'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0', 'lime': '#00ff00', 'limegreen': '#32cd32',
    'linen': '#faf0e6', 'magenta': '#ff00ff', 'maroon': '#800000',
    'mediumaquamarine': '#66cdaa', 'mediumblue': '#0000cd', 'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370db', 'mediumseagreen': '#3cb371', 'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a', 'mediumturquoise': '#48d1cc', 'mediumvioletred': '#c71585',
    'midnightblue': '#191970', 'mintcream': '#f5fffa', 'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5', 'navajowhite': '#ffdead', 'navy': '#000080',
    'oldlace': '#fdf5e6', 'olive': '#808000', 'olivedrab': '#6b8e23',
    'orange': '#ffa500', 'orangered': '#ff4500', 'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa', 'palegreen': '#98fb98', 'paleturquoise': '#afeeee',
    'palevioletred': '#db7093', 'papayawhip': '#ffefd5', 'peachpuff': '#ffdab9',
    'peru': '#cd853f', 'pink': '#ffc0cb', 'plum': '#dda0dd',
    'powderblue': '#b0e0e6', 'purple': '#800080', 'red': '#ff0000',
    'rosybrown': '#bc8f8f', 'royalblue': '#4169e1', 'saddlebrown': '#8b4513',
    'salmon': '#fa8072', 'sandybrown': '#f4a460', 'seagreen': '#2e8b57',
    'seashell': '#fff5ee', 'sienna': '#a0522d', 'silver': '#c0c0c0',
    'skyblue': '#87ceeb', 'slateblue': '#6a5acd', 'slategray': '#708090',
    'slategrey': '#708090', 'snow': '#fffafa', 'springgreen': '#00ff7f',
    'steelblue': '#4682b4', 'tan': '#d2b48c', 'teal': '#008080',
    'thistle': '#d8bfd8', 'tomato': '#ff6347', 'turquoise': '#40e0d0',
    'violet': '#ee82ee', 'wheat': '#f5deb3', 'white': '#ffffff',
    'whitesmoke': '#f5f5f5', 'yellow': '#ffff00', 'yellowgreen': '#9acd32',
}

# Standard palette for element categories
STANDARD_PALETTE: dict[str, str] = {
    'strategy': '#f5deaa',
    'business': '#ffffb5',
    'application': '#b5ffff',
    'technology': '#c9e7b7',
    'physical': '#c9e7b7',
    'migration': '#ffe0e0',
    'motivation': '#ccccff',
    'implementation': '#ffe0e0',
    'relationship': '#dddddd',
    'junction': '#000000',
    'other': '#ffffff',
}

