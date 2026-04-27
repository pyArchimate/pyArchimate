"""Modern implementations of View, Node, Connection, Profile, Point, and Position.

All classes are self-contained and carry no dependency on the legacy module.
"""

import math
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from .constants import ARCHI_CATEGORY, DEFAULT_THEME
from .element import Element, set_id
from .enums import ArchiType
from .exceptions import ArchimateConceptTypeError
from .logger import log

if TYPE_CHECKING:
    from .model import Model

# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _sort_nodes(nodes: list[Any], sort: str) -> list[Any]:
    s = sort.lower()
    if 'asc' in s:
        return sorted(nodes, key=lambda x: x.w * x.h)
    if 'desc' in s:
        return sorted(nodes, key=lambda x: x.w * x.h, reverse=True)
    return nodes


def _apply_justify_right(nodes: list[Any], max_in_row: int, max_w: float, gap_x: float) -> None:
    remainder = len(nodes) % max_in_row
    right_start = len(nodes) - remainder
    for i in range(len(nodes), right_start, -1):
        _e = nodes[i - 1]
        _e.rx = max_w - _e.w - gap_x
        max_w = _e.rx
    if max_in_row == 1:
        for _e in nodes:
            _e.rx = max_w - _e.w - gap_x


def _next_row_x(justify: str, row: int, elem_w: float, gap_x: float) -> int:
    if justify == 'center':
        return 40 if row % 2 == 0 else 40 + int((elem_w + gap_x) / 2)
    return 40


def _classify_outer_quadrant(angle: float) -> str:
    if 135 <= angle < 225:
        return 'R'
    if 225 <= angle < 315:
        return 'B'
    if angle >= 315 or angle < 45:
        return 'L'
    return 'T'


# ---------------------------------------------------------------------------
# Colour helper
# ---------------------------------------------------------------------------

def default_color(elem_type: str, theme: Union[str, "dict[str, str]", None] = DEFAULT_THEME) -> str:
    """Return the default fill colour for a node, keyed by Archimate element type."""
    _archi_colors = {
        'strategy': '#F5DEAA', 'business': "#FFFFB5", 'application': "#B5FFFF",
        'technology': "#C9E7B7", 'physical': "#C9E7B7", 'migration': "#FFE0E0",
        'motivation': "#CCCCFF", 'relationship': "#DDDDDD", 'other': '#FFFFFF',
        'junction': '#000000',
    }
    _aris_colors = {
        'strategy': '#D38300', 'business': "#F5C800", 'application': "#00A0FF",
        'technology': "#6BA50E", 'physical': "#6BA50E", 'migration': "#FFE0E0",
        'motivation': "#F099FF", 'relationship': "#DDDDDD", 'other': '#FFFFFF',
        'junction': '#000000',
    }
    if elem_type in ARCHI_CATEGORY:
        cat = ARCHI_CATEGORY[elem_type].lower()
        if theme == 'archi' or theme is None:
            return _archi_colors.get(cat, '#FFFFFF')
        if theme == 'aris':
            return _aris_colors.get(cat, '#FFFFFF')
        try:
            theme_dict = cast("dict[str, str]", theme)
            return str(theme_dict[cat])
        except (KeyError, TypeError):
            return _archi_colors.get(cat, '#FFFFFF')
    return '#FFFFFF'


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

class Point:
    """A simple (x, y) coordinate pair where both values are non-negative integers."""

    def __init__(self, x: float = 0, y: float = 0):
        self._x = max(0, int(x))
        self._y = max(0, int(y))
        self.idx: int = 0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self._x = max(0, val)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._y = max(0, val)


class Position:
    """Positional relationship between two nodes (distance, angle, orientation)."""

    def __init__(self):
        self.dx: Optional[float] = None
        self.dy: Optional[float] = None
        self.gap_x: float = 0
        self.gap_y: float = 0
        self.angle: Optional[float] = None
        self.orientation: str = ""

    @property
    def dist(self):
        if self.dx is not None and self.dy is not None:
            return math.sqrt(self.dx ** 2 + self.dy ** 2)
        return None


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class Profile:
    """An Archimate stereotype / specialisation profile for elements or relationships."""

    def __init__(self, name=None, uuid=None, concept=None, model=None):
        if not name:
            raise ValueError('Name of Profile must be present.')
        if not concept:
            raise ValueError('concept of Profile must be specified as a class of type: Element')
        if not hasattr(ArchiType, concept):
            raise ArchimateConceptTypeError(
                "'concept' argument is not an instance of 'ArchiType' class."
            )
        if concept == 'View':
            raise ValueError("The concept type cannot be a View for a Profile")
        self.name = name
        self._uuid = set_id(uuid)
        self.concept = concept
        self.model: "Model" = cast("Model", model)

    def delete(self):
        """Remove this profile and clear all references to it from elements and relationships."""
        for x in [e for e in self.model.elements if e.profile_id == self.uuid]:
            x.reset_profile()
        for x in [r for r in self.model.relationships if r.profile_id == self.uuid]:
            x.reset_profile()
        if self.uuid in self.model._profiles_dict:
            del self.model._profiles_dict[self.uuid]

    @property
    def uuid(self) -> str:
        return self._uuid


# ---------------------------------------------------------------------------
# Node  (forward-references View in isinstance checks — defined below)
# ---------------------------------------------------------------------------

class Node:
    """A visual node in a View, representing an Element concept.

    :param ref:       Element identifier or Element object
    :param x:         top-left x coordinate
    :param y:         top-left y coordinate
    :param w:         width
    :param h:         height
    :param uuid:      node identifier
    :param node_type: one of 'Element', 'Label', 'Container'
    :param label:     label text (for Label/Container nodes)
    :param parent:    parent View or parent Node
    """

    @staticmethod
    def _resolve_ref(ref: object) -> "Optional[str]":
        if ref is None:
            return None
        if isinstance(ref, str):
            return ref
        if isinstance(ref, Element):
            return ref.uuid
        if hasattr(ref, 'uuid'):
            return str(ref.uuid)  # pyright: ignore[reportAttributeAccessIssue]
        raise ValueError("'ref' is not an instance of 'Element' class.")

    def _validate_ref(self, node_type: str, ref: "Optional[str]") -> None:
        if node_type == 'Element' and ref is not None and ref not in self.model.elems_dict:
            raise ValueError(f'Invalid element reference "{ref}"')
        if node_type == 'Label' and ref is not None and ref not in self.model.labels_dict:
            raise ValueError(f'Invalid element reference "{ref}"')

    def __init__(self, ref=None, x=0, y=0, w=120, h=55, uuid=None,
                 node_type='Element', label=None, parent=None):
        # parent type check is done after View is defined; accept duck-typed objects
        if parent is None or not (hasattr(parent, 'view') and hasattr(parent, 'model')):
            raise ValueError('Node class parent should be a class View or Node instance!')

        self.parent: "Union[View, Node]" = parent
        self._view: "View" = cast("View", parent.view)
        self._model: "Model" = cast("Model", parent.model)

        self._ref = self._resolve_ref(ref)
        self._validate_ref(node_type, self._ref)

        self._uuid = set_id(uuid)
        self._x = int(x)
        self._y = int(y)
        self._w = int(w)
        self._h = int(h)
        self._cx = self._x + self._w / 2
        self._cy = self._y + self._h / 2
        self._area = self._w * self._h
        self.flags = 0
        self.cat = node_type
        self.label = label
        self.nodes_dict: dict[str, "Node"] = {}
        self._fill_color: Optional[str] = None
        self.line_color: Optional[str] = None
        self.opacity: int | float = 100
        self.lc_opacity: int | float = 100
        self.font_color: Optional[str] = None
        self.font_name = 'Segoe UI'
        self.font_size: int | float = 9
        self.text_alignment: Optional[str] = None
        self.text_position = None
        self.label_expression: Optional[str] = None
        self.border_type: Optional[str] = None
        self.iconColor = None
        self.gradient = None

    # --- lifecycle ---

    def delete(self, recurse=True, delete_from_model=False):
        """Delete this node and its related connections."""
        for c in self.view.conns_dict.copy().values():
            if c._source == self._uuid or c._target == self._uuid:
                c.delete()
                del c
        for n in self.nodes_dict.copy().values():
            if recurse:
                n.delete()
            else:
                n.move(self.parent)
        if self._uuid in self.parent.nodes_dict:
            del self.parent.nodes_dict[self._uuid]
        del self.model.nodes_dict[self._uuid]
        if delete_from_model:
            e = self.concept
            related_nodes = [n for n in self.model.nodes if n.ref == e.uuid]
            for n in related_nodes:
                n.delete(recurse)
            e.delete()

    def add(self, ref=None, x=0, y=0, w=120, h=55, uuid=None,
            node_type='Element', label=None, nested_rel_type=None):
        """Create and return a child node embedded in this node."""
        n = Node(ref, x, y, w, h, uuid, node_type, label, parent=self)
        self.nodes_dict[n.uuid] = n
        self.model.nodes_dict[n.uuid] = n
        if nested_rel_type is not None:
            self.model.add_relationship(rel_type=nested_rel_type,
                                        source=self.concept, target=n.concept)
        return n

    # --- identity ---

    @property
    def uuid(self) -> str:
        return self._uuid

    # --- concept proxy ---

    @property
    def name(self) -> Optional[str]:
        if self.cat == 'Element':
            return self.concept.name
        return None

    @property
    def desc(self) -> Optional[str]:
        return self.concept.desc

    @property
    def type(self) -> Optional[str]:
        if self.cat == 'Element':
            return self.concept.type
        return None

    @property
    def concept(self) -> Element:
        try:
            return cast(Element, self.model.elems_dict[self._ref])
        except KeyError:
            raise ArchimateConceptTypeError(f'Invalid element reference "{self._ref}"') from None

    @property
    def ref(self) -> Optional[str]:
        return self._ref

    @ref.setter
    def ref(self, ref):
        if isinstance(ref, Element):
            new_ref = ref.uuid
        elif hasattr(ref, 'uuid'):
            new_ref = ref.uuid
        else:
            new_ref = ref
        if new_ref in self.model.elems_dict:
            self._ref = new_ref

    # --- position ---

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        if val < 0:
            val = 0
        for n in self.nodes:
            n.x += val - self._x
        self._x = int(val)
        self._cx = self._x + self.w / 2

    @property
    def cx(self):
        return float(self._cx)

    @cx.setter
    def cx(self, val):
        if val < 0:
            val = 0
        self.x = int(val - self._w / 2 + 0.5)
        self._cx = val

    @property
    def rx(self):
        if isinstance(self.parent, Node):
            return self._x - self.parent.x
        return self._x

    @rx.setter
    def rx(self, value):
        if value < 0:
            value = 0
        if isinstance(self.parent, Node):
            self.x = self.parent.x + value
        else:
            self.x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        if val < 0:
            val = 0
        for n in self.nodes:
            n.y += val - self._y
        self._y = int(val)
        self._cy = self._y + self.h / 2

    @property
    def cy(self):
        return float(self._cy)

    @cy.setter
    def cy(self, val: float) -> None:
        if val < 0:
            val = 0
        self.y = int(val - self._h / 2 + 0.5)
        self._cy = val

    @property
    def ry(self):
        if isinstance(self.parent, Node):
            return self._y - self.parent.y
        return self._y

    @ry.setter
    def ry(self, value):
        if value < 0:
            value = 0
        if isinstance(self.parent, Node):
            self.y = self.parent.y + int(value)
        else:
            self.y = value

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self, value):
        self._w = int(value)
        self._cx = self._x + self.w / 2

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, value):
        self._h = int(value)
        self._cy = self._y + self.h / 2

    # --- styling ---

    @property
    def fill_color(self):
        return self._fill_color

    @fill_color.setter
    def fill_color(self, color_str):
        if color_str is None:
            self._fill_color = default_color(self.type or '', self.model.theme)
        else:
            self._fill_color = color_str

    # --- navigation ---

    @property
    def view(self):
        return self._view

    @property
    def model(self):
        return self._model

    @property
    def nodes(self) -> list["Node"]:
        return list(self.nodes_dict.values())

    def getnodes(self, elem_type: Optional[str] = None) -> list["Node"]:
        if elem_type is None:
            return list(self.nodes_dict.values())
        return [x for x in self.nodes_dict.values() if x.type == elem_type]

    def get_or_create_node(self, elem=None, elem_type=None, x=0, y=0, w=120, h=55,
                           create_elem=False, create_node=False, nested_rel_type=None):
        """Return an existing child node or create one if requested."""
        _e = None
        if not isinstance(elem, Element):
            _e = self.model.find_elements(elem, elem_type)
            if len(_e) > 0:
                _e = _e[0]
            elif create_elem:
                _e = self.model.add(elem_type, name=elem)
            else:
                return None
        else:
            _e = elem
        n = [x for x in self.nodes if x.ref == _e.uuid]
        if len(n) > 0:
            return n[0]
        elif create_node:
            return self.add(ref=_e, x=x, y=y, w=w, h=h, nested_rel_type=nested_rel_type)
        return None

    def is_inside(self, x: float = 0, y: float = 0, point: Optional[Point] = None) -> bool:
        """Return True if the (x,y) point lies within this node's bounding box."""
        if point is not None:
            x = float(point.x)
            y = float(point.y)
        return bool(self.cx - self.w / 2 < x < self.cx + self.w / 2
                    and self.cy - self.h / 2 < y < self.cy + self.h / 2)

    def resize(self, max_in_row=3, keep_kids_size=True, w=120, h=55,
               gap_x=20, gap_y=20, justify='left', recurse=False, sort="asc"):
        """Resize this node to fit all embedded children."""
        max_w = w
        max_h = h
        ba_x = 40
        ba_y = 40
        max_row_h = h
        n = 1
        nodes = _sort_nodes(self.nodes, sort)
        for _e in nodes:
            if recurse:
                _e.resize(max_in_row=max_in_row, keep_kids_size=keep_kids_size,
                          w=w, h=h, gap_x=gap_x, gap_y=gap_y, justify=justify, sort=sort)
            min_w = _e.w if (w == -1 or keep_kids_size) else w
            min_h = _e.h if (h == -1 or keep_kids_size) else h
            _e.rx = ba_x
            _e.ry = ba_y
            _e.w = min_w
            _e.h = min_h
            max_row_h = max(max_row_h, _e.h)
            ba_x += _e.w + gap_x
            if n % max_in_row == 0:
                ba_x = _next_row_x(justify, n // max_in_row, _e.w, gap_x)
                ba_y += max_row_h + gap_y
                max_row_h = h
            n += 1
            max_w = max(max_w, _e.rx + _e.w + gap_x)
            max_h = max(max_h, _e.ry + _e.h + gap_y)
        self.w = max_w
        self.h = max_h
        if justify == 'right':
            _apply_justify_right(nodes, max_in_row, max_w, gap_x)

    def conns(self, rel_type=None):
        """Return connections to/from this node, optionally filtered by type."""
        if rel_type is None:
            return [c for c in self.view.conns_dict.values()
                    if c.source is not None and c.target is not None
                    and (c.source.uuid == self.uuid or c.target.uuid == self.uuid)]
        return [c for c in self.view.conns_dict.values()
                if c.source is not None and c.target is not None
                and c.type == rel_type and (c.source.uuid == self.uuid or c.target.uuid == self.uuid)]

    def in_conns(self, rel_type=None):
        if rel_type is None:
            return [c for c in self.view.conns_dict.values()
                    if c.target is not None and c.target.uuid == self.uuid]
        return [c for c in self.view.conns_dict.values()
                if c.target is not None and c.type == rel_type and c.target.uuid == self.uuid]

    def out_conns(self, rel_type=None):
        if rel_type is None:
            return [c for c in self.view.conns_dict.values()
                    if c.source is not None and c.source.uuid == self.uuid]
        return [c for c in self.view.conns_dict.values()
                if c.source is not None and c.type == rel_type and c.source.uuid == self.uuid]

    def _compute_gap_x(self, other_node: "Node") -> float:
        ocx, ow = float(other_node.cx), float(other_node.w)
        scx, sx, sw = float(self.cx), float(self.x), float(self.w)
        if ocx - ow / 2 > sx + sw / 2 and ocx + ow / 2 > scx + sw / 2:
            return ocx - ow / 2 - scx - sw / 2
        if ocx - ow / 2 < scx - sw / 2 and ocx + ow / 2 < scx - sw / 2:
            return ocx + ow / 2 - scx + sw / 2
        return 0.0

    def _compute_gap_y(self, other_node: "Node") -> float:
        ocy, oh = float(other_node.cy), float(other_node.h)
        scy, sh = float(self.cy), float(self.h)
        if ocy - oh / 2 > scy + sh / 2 and ocy + oh / 2 > scy + sh / 2:
            return ocy - oh / 2 - scy - sh / 2
        if ocy - oh / 2 < scy - sh / 2 and ocy + oh / 2 < scy - sh / 2:
            return ocy + oh / 2 - scy + sh / 2
        return 0.0

    @staticmethod
    def _refine_gap_orientation(position: Position) -> None:
        if position.gap_x == 0 and position.gap_y < 0:
            position.orientation = "T!"
        elif position.gap_x == 0 and position.gap_y > 0:
            position.orientation = "B!"
        elif position.gap_x < 0 and position.gap_y == 0:
            position.orientation = "L!"
        elif position.gap_x > 0 and position.gap_y == 0:
            position.orientation = "R!"

    def get_obj_pos(self, other_node: "Node") -> Position:
        """Return a Position describing this node's relationship to another."""
        dx = other_node.cx - self.cx
        dy = other_node.cy - self.cy
        position = Position()
        position.dx = dx
        position.dy = dy
        angle = math.atan2(float(dy), float(dx)) * 180 / math.pi
        if angle < 0:
            angle += 360
        angle = (360 - angle) % 360
        position.angle = angle
        if angle < 45 or angle > 315:
            position.orientation = 'R'
        elif 45 <= angle < 135:
            position.orientation = 'T'
        elif 135 <= angle < 225:
            position.orientation = 'L'
        else:
            position.orientation = 'B'
        position.gap_x = self._compute_gap_x(other_node)
        position.gap_y = self._compute_gap_y(other_node)
        self._refine_gap_orientation(position)
        return position

    def get_point_pos(self, point: Point) -> Position:
        position = Position()
        dx = float(point.x - self.cx)
        dy = float(point.y - self.cy)
        position.dx = dx
        position.dy = dy
        position.gap_x = (abs(dx) - self.w / 2) * (1 if dx > 0 else -1)
        position.gap_y = (abs(dy) - self.h / 2) * (1 if dy > 0 else -1)
        angle = math.atan2(dy, dx) * 180 / math.pi
        if angle < 0:
            angle += 360
        angle = (360 - angle) % 360
        position.angle = angle
        in_y_band = self.cy - self.h / 2 < point.y < self.cy + self.h / 2
        in_x_band = self.cx - self.w / 2 < point.x < self.cx + self.w / 2
        if not in_y_band and not in_x_band:
            pos = _classify_outer_quadrant(angle)
        elif (angle > 270 or angle < 90) and in_y_band:
            pos = 'L!'
        elif angle > 180 and in_x_band:
            pos = 'B!'
        elif angle < 180 and in_x_band:
            pos = 'T!'
        elif in_y_band:
            pos = 'R!'
        else:
            pos = '*'
        position.orientation = pos
        return position

    @staticmethod
    def _compute_midpoint(obj1: "Node", obj2: "Node", pos: Position) -> "tuple[float, float]":
        p = pos.orientation
        cx1, cy1 = float(obj1.cx), float(obj1.cy)
        cx2, cy2 = float(obj2.cx), float(obj2.cy)
        w1, h1 = float(obj1.w), float(obj1.h)
        if p == 'L!':
            return cx1 - w1 / 2 + pos.gap_x / 2, cy1
        if p == 'R!':
            return cx1 + w1 / 2 + pos.gap_x / 2, cy1
        if p == 'B!':
            return cx1, cy1 + h1 / 2 + pos.gap_y / 2
        if p == 'T!':
            return cx1, cy2 + float(obj2.h) / 2 - pos.gap_y / 2
        return (cx2 + cx1) / 2, (cy2 + cy1) / 2

    def _queue_connection_bp(self, r: "Connection", obj1: "Node", obj2: "Node",
                              top: "list[dict[str, Any]]", bottom: "list[dict[str, Any]]",
                              left: "list[dict[str, Any]]", right: "list[dict[str, Any]]") -> None:
        bps = r.get_all_bendpoints()
        pos = obj1.get_obj_pos(obj2)
        angle: float = pos.angle or 0.0
        if obj1.is_inside(obj2.cx, obj2.cy):
            return
        if len(bps) == 0:
            _x, _y = self._compute_midpoint(obj1, obj2, pos)
            r.add_bendpoint(Point(_x, _y))
            bps = r.get_all_bendpoints()
        if r.target is not None and r.target.uuid == self.uuid:
            bp = bps[len(bps) - 1]
            bp.idx = len(bps) - 1
        else:
            bp = bps[0]
            bp.idx = 0
        bp_pos = obj1.get_point_pos(bp)
        if 'R' in bp_pos.orientation:
            right.append({'order': angle, 'bp': bp, 'r': r})
        if 'L' in bp_pos.orientation:
            left.append({'order': -((angle + 180) % 360), 'bp': bp, 'r': r})
        if 'T' in bp_pos.orientation:
            top.append({'order': -angle, 'bp': bp, 'r': r})
        if 'B' in bp_pos.orientation:
            bottom.append({'order': angle, 'bp': bp, 'r': r})

    @staticmethod
    def _spread_connections_along_edge(obj1: "Node", items: "list[dict[str, Any]]", axis: str) -> None:
        n = len(items)
        for i, entry in enumerate(sorted(items, key=lambda d: d['order']), start=1):
            if axis == 'y':
                entry['bp'].y = obj1.cy - obj1.h * (0.5 - (i / (n + 1)))
            else:
                entry['bp'].x = obj1.cx - obj1.w * (0.5 - (i / (n + 1)))
            entry['r'].set_bendpoint(Point(entry['bp'].x, entry['bp'].y), entry['bp'].idx)

    def distribute_connections(self):
        """Redistribute all connections evenly along each edge of this node."""
        top: list[dict[str, Any]] = []
        bottom: list[dict[str, Any]] = []
        left: list[dict[str, Any]] = []
        right: list[dict[str, Any]] = []
        obj1 = None
        for r in self.conns():
            if r.target is not None and r.target.uuid == self.uuid:
                obj2, obj1 = r.source, r.target
            else:
                obj1, obj2 = r.source, r.target
            if obj1 is None or obj2 is None:
                continue
            self._queue_connection_bp(r, obj1, obj2, top, bottom, left, right)
        if obj1 is None:
            return
        self._spread_connections_along_edge(obj1, right, 'y')
        self._spread_connections_along_edge(obj1, left, 'y')
        self._spread_connections_along_edge(obj1, top, 'x')
        self._spread_connections_along_edge(obj1, bottom, 'x')

    def move(self, new_parent):
        """Reparent this node to a different Node or View within the same diagram."""
        if not (hasattr(new_parent, 'view') and hasattr(new_parent, 'model')):
            log.error("Invalid target to move the node to. Expecting a View or a Node")
            return
        if new_parent.view.uuid != self.view.uuid:
            log.error("Cannot move a node outside of its view")
            return
        del self.parent.nodes_dict[self.uuid]
        self.parent = new_parent
        new_parent.nodes_dict[self.uuid] = self


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

class Connection:
    """A visual connection between two Nodes, backed by a Relationship.

    :param ref:    Relationship identifier or Relationship-like object (duck-typed)
    :param source: source Node identifier or Node object
    :param target: target Node identifier or Node object
    :param uuid:   connection identifier
    :param parent: parent View
    """

    @staticmethod
    def _resolve_conn_ref(ref: object) -> str:
        if isinstance(ref, str):
            return ref
        if ref is not None and hasattr(ref, 'uuid'):
            return str(ref.uuid)  # pyright: ignore[reportAttributeAccessIssue]
        raise ArchimateConceptTypeError("'ref' is not an instance of 'Relationship' class.")

    @staticmethod
    def _resolve_node_uuid(node: object, label: str) -> str:
        if isinstance(node, Node):
            return node.uuid
        if isinstance(node, str):
            return node
        raise ArchimateConceptTypeError(f"'{label}' is not an instance of 'Node' class.")

    def __init__(self, ref=None, source=None, target=None, uuid=None, parent=None):
        if not isinstance(parent, View):
            raise ArchimateConceptTypeError(
                'Connection class parent should be a class View instance!'
            )
        self.parent: 'View' = parent
        self.view = self.parent
        self._uuid = set_id(uuid)
        self.model: "Model" = self.parent.parent

        self._ref = self._resolve_conn_ref(ref)
        if self._ref not in self.model.rels_dict:
            raise ValueError(f'Invalid relationship reference "{self._ref}"')

        self._source = self._resolve_node_uuid(source, 'source')
        if self._source not in self.model.nodes_dict and self._source not in self.model.conns_dict:
            raise ValueError(f'Invalid source reference "{self._source}"')

        self._target = self._resolve_node_uuid(target, 'target')
        if self._target not in self.model.nodes_dict and self._target not in self.model.conns_dict:
            raise ValueError(f'Invalid target reference "{self._target}"')

        self._uuid = set_id(uuid)
        self.bendpoints: list[Point] = []
        self.line_color = None
        self.font_color = None
        self.font_name = 'Segoe UI'
        self.font_size = 9
        self.line_width = 1
        self.text_position = "1"
        self.show_label = True

    def delete(self):
        del self.view.conns_dict[self.uuid]
        del self.model.conns_dict[self.uuid]

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def ref(self) -> str:
        return self._ref

    @ref.setter
    def ref(self, ref):
        if hasattr(ref, 'uuid'):
            new_ref = ref.uuid
        else:
            new_ref = ref
        if new_ref in self.model.rels_dict:
            self._ref = new_ref

    @property
    def concept(self):
        return self.model.rels_dict[self._ref]

    @property
    def type(self) -> str:
        return cast(str, self.model.rels_dict[self._ref].type)

    @property
    def name(self) -> Optional[str]:
        return cast(Optional[str], self.model.rels_dict[self._ref].name)

    @property
    def source(self) -> Optional[Node]:
        if self._source in self.model.nodes_dict:
            return cast(Node, self.model.nodes_dict[self._source])
        elif self._source in self.model.conns_dict:
            return cast(Node, self.model.rels_dict[self._source])
        return None

    @source.setter
    def source(self, elem):
        if isinstance(elem, Node):
            new_ref = elem.uuid
        elif hasattr(elem, 'uuid'):
            new_ref = elem.uuid
        else:
            new_ref = elem
        if new_ref in self.model.nodes_dict:
            self._source = new_ref

    @property
    def target(self) -> Optional[Node]:
        if self._target in self.model.nodes_dict:
            return cast(Node, self.model.nodes_dict[self._target])
        elif self._target in self.model.conns_dict:
            return cast(Node, self.model.rels_dict[self._target])
        return None

    @target.setter
    def target(self, elem):
        if isinstance(elem, Node):
            new_ref = elem.uuid
        elif hasattr(elem, 'uuid'):
            new_ref = elem.uuid
        else:
            new_ref = elem
        if new_ref in self.model.nodes_dict:
            self._target = new_ref

    @property
    def access_type(self):
        return self.concept.access_type

    @property
    def is_directed(self):
        return self.concept.is_directed

    @property
    def influence_strength(self):
        return self.concept.influence_strength

    def add_bendpoint(self, *bendpoints: Point) -> None:
        for bp in bendpoints:
            self.bendpoints.append(bp)

    def set_bendpoint(self, bp: Point, index: int) -> None:
        if index < len(self.bendpoints):
            self.bendpoints[index] = bp

    def get_bendpoint(self, index: int) -> Optional[Point]:
        return self.bendpoints[index] if index < len(self.bendpoints) else None

    def del_bendpoint(self, index: int) -> None:
        del self.bendpoints[index]

    def get_all_bendpoints(self) -> list[Point]:
        return self.bendpoints

    def remove_all_bendpoints(self):
        self.bendpoints = []

    def l_shape(self, direction=0, weight_x=0.5, weight_y=0.5):
        """Shape the connection as an L (one bendpoint)."""
        assert self.source is not None and self.target is not None
        self.remove_all_bendpoints()
        s_cx, s_cy = self.source.cx, self.source.cy
        t_cx, t_cy = self.target.cx, self.target.cy
        if direction == 0 and not self.source.is_inside(t_cx, s_cy) \
                and not self.target.is_inside(t_cx, s_cy):
            self.add_bendpoint(
                Point(t_cx + self.target.w * (0.5 - weight_x),
                      s_cy + self.source.h * (0.5 - weight_y))
            )
        elif direction == 1 and not self.source.is_inside(s_cx, t_cy) \
                and not self.target.is_inside(s_cx, t_cy):
            self.add_bendpoint(
                Point(s_cx - self.source.w * (0.5 - weight_x),
                      t_cy + self.target.h * (0.5 - weight_y))
            )

    def s_shape(self, direction=0, weight_x=0.5, weight_y=0.5, weight2=0.5):
        """Shape the connection as an S (two bendpoints)."""
        assert self.source is not None and self.target is not None
        self.remove_all_bendpoints()
        s_xy = Point(self.source.cx, self.source.cy)
        t_xy = Point(self.target.cx, self.target.cy)
        dx = t_xy.x - s_xy.x
        dy = t_xy.y - s_xy.y
        if direction == 0:
            bp1 = Point(s_xy.x + dx * weight_x, s_xy.y - self.source.h * (0.5 - weight_y))
            bp2 = Point(bp1.x, t_xy.y - self.target.h * (0.5 - weight2))
        else:
            bp1 = Point(s_xy.x - self.source.w * (0.5 - weight_x), s_xy.y + dy * weight_y)
            bp2 = Point(t_xy.x - self.target.w * (0.5 - weight2), bp1.y)
        if (not self.source.is_inside(point=bp1)
                and not self.target.is_inside(point=bp1)
                and not self.target.is_inside(point=bp2)):
            self.add_bendpoint(bp1)
            self.add_bendpoint(bp2)


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------

class View:
    """A diagram (view) in an Archimate model containing Nodes and Connections.

    :param name:   view name
    :param uuid:   view identifier
    :param desc:   description
    :param folder: folder path for organisation hierarchy
    :param parent: parent Model object (duck-typed: must have views_dict)
    """

    def __init__(self, name=None, uuid=None, desc=None, folder=None, parent=None):
        if not hasattr(parent, 'views_dict'):
            raise ArchimateConceptTypeError(
                'View class parent should be a class Model instance!'
            )
        self.parent: "Model" = cast("Model", parent)
        self.model: "Model" = cast("Model", parent)
        self.view = self  # root of the node tree
        self._uuid = set_id(uuid)
        self.name = name
        self.desc = desc
        self.unions: list[object] = []
        self.nodes_dict: dict[str, Node] = defaultdict(Node)
        self.conns_dict: dict[str, Connection] = defaultdict(Connection)
        self._properties: dict[str, object] = {}
        self.folder = folder

    def delete(self):
        _id = self.uuid
        for n in self.nodes_dict.copy().values():
            n.delete(recurse=True)
            del n
        for c in self.conns_dict.copy().values():
            c.delete()
            del c
        if _id in self.parent.views_dict:
            del self.parent.views_dict[_id]

    def add(self, ref: object = None, x: int = 0, y: int = 0, w: int = 120, h: int = 55,
            uuid: Optional[str] = None, node_type: str = 'Element',
            label: Optional[str] = None) -> Node:
        """Add and return a Node in this view."""
        n = Node(ref, x, y, w, h, uuid, node_type, label, self)
        self.nodes_dict[n.uuid] = n
        self.model.nodes_dict[n.uuid] = n
        return n

    def add_connection(self, ref: object = None, source: object = None,
                       target: object = None, uuid: Optional[str] = None) -> Connection:
        """Add and return a Connection between two Nodes."""
        c = Connection(ref, source, target, uuid, self)
        self.conns_dict[c.uuid] = c
        self.model.conns_dict[c.uuid] = c
        return c

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def type(self) -> str:
        return 'Diagram'

    @property
    def props(self) -> dict[str, object]:
        return self._properties

    def prop(self, key: str, value: object = None) -> object:
        if value is None:
            return self._properties.get(key)
        self._properties[key] = value
        return value

    def remove_prop(self, key):
        if key in self._properties:
            del self._properties[key]

    @property
    def nodes(self) -> list[Node]:
        return list(self.nodes_dict.values())

    @property
    def conns(self) -> list[Connection]:
        return list(self.conns_dict.values())

    def remove_folder(self):
        self.folder = None

    def get_or_create_node(self, elem: object = None, elem_type: Optional[str] = None,
                           x: int = 0, y: int = 0, w: int = 120, h: int = 55,
                           create_elem: bool = False, create_node: bool = False) -> Optional[Node]:
        """Return an existing node for the element, or create one if requested."""
        _e = None
        if not isinstance(elem, Element):
            _e = self.model.find_elements(elem, elem_type)
            if len(_e) > 0:
                _e = _e[0]
            elif create_elem:
                _e = self.model.add(elem_type, name=elem)
            else:
                return None
        else:
            _e = elem
        n = [x for x in self.nodes if x.ref == _e.uuid]
        if len(n) > 0:
            return n[0]
        elif create_node:
            return self.add(ref=_e, x=x, y=y, w=w, h=h)
        return None

    def _find_or_create_rel(self, source: "Node", target: "Node",
                             rel_type: Optional[str], name: Optional[str]) -> "Optional[Any]":
        src_uuid = source.concept.uuid
        tgt_uuid = target.concept.uuid
        if name is None:
            matches = self.model.filter_relationships(
                lambda x: (rel_type == x.type
                            and x.source is not None and x.target is not None
                            and src_uuid == x.source.uuid
                            and tgt_uuid == x.target.uuid)
            )
        else:
            matches = self.model.filter_relationships(
                lambda x: (rel_type == x.type
                            and x.source is not None and x.target is not None
                            and src_uuid == x.source.uuid
                            and tgt_uuid == x.target.uuid
                            and x.name == name)
            )
        if matches:
            return matches[0]
        if rel_type is None:
            return None
        return self.model.add_relationship(
            source=source.ref, target=target.ref, rel_type=rel_type, name=name
        )

    def get_or_create_connection(self, rel: object = None, source: Optional["Node"] = None,
                                 target: Optional["Node"] = None,
                                 rel_type: Optional[str] = None, name: Optional[str] = None,
                                 create_conn: bool = False) -> Optional["Connection"]:
        """Return an existing connection or create one if requested."""
        if rel is None:
            if source is None or target is None:
                return None
            r = self._find_or_create_rel(source, target, rel_type, name)
            if r is None:
                return None
        elif hasattr(rel, 'type'):  # duck-typed Relationship
            r = cast(Any, rel)
            rel_type = r.type
        else:
            return None
        c = [c for c in self.conns_dict.values() if c.ref == r.uuid and c.type == rel_type]
        if c:
            return c[0]
        if create_conn and target is not None and source is not None and target.parent.uuid != source.uuid:
            return self.add_connection(r, source, target)
        return None


__all__ = ["View", "Node", "Connection", "Profile", "Point", "Position", "default_color"]
