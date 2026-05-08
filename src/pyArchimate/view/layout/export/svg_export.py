"""SVG export service for rendering pyArchimate views as SVG diagrams.

This module provides functionality to export views as self-contained SVG files
for visual inspection, automated testing, and sharing without requiring the
Archi desktop tool.
"""

import math
from typing import Any, Optional, Tuple
from xml.etree import ElementTree as ET

from .symbols.archimate_relationships import (
    RelationshipStyleService,
)
from .symbols.archimate_symbols import ARCHIMATE_SYMBOLS
from .symbols.color_palette import get_element_color


class SVGExportService:
    """Service for exporting pyArchimate views as SVG diagrams."""

    # SVG render defaults
    SVG_MARGIN = 20  # pixels around the entire view
    TEXT_PADDING = 4  # pixels inside element rectangles
    ARROWHEAD_SIZE = 8  # size of arrowhead marker
    LABEL_PADDING = 2  # padding inside label background
    ENDPOINT_SPREAD_STEP = 12.0  # pixels between parallel connection anchors
    EDGE_CORNER_MARGIN = 12.0  # keep endpoint spread away from corners

    def __init__(self) -> None:
        """Initialize SVG export service."""
        pass

    def _sort_nodes_by_hierarchy(self, view: Any) -> list[Any]:
        """Sort nodes so that containing elements render before contained elements.

        This ensures proper z-order in SVG output where parent containers appear
        behind their child nodes. Uses depth-first traversal to visit parents
        before children.

        Args:
            view: View object containing nodes to sort

        Returns:
            List of nodes in proper rendering order (parents before children)
        """
        sorted_nodes: list[Any] = []
        visited: set[str] = set()

        def visit(node: Any) -> None:
            """Depth-first visit: render parent before children."""
            if node.uuid in visited:
                return
            visited.add(node.uuid)
            sorted_nodes.append(node)
            # Visit children in the order they appear in nodes_dict
            for child in node.nodes:
                visit(child)

        # Start from root nodes (those with View as parent)
        for root_node in view.nodes:
            visit(root_node)

        return sorted_nodes

    def _build_complete_nodes_dict(self, view: Any) -> dict[str, Any]:
        """Build a dictionary of all nodes including nested ones.

        This creates a flat dictionary mapping node UUIDs to node objects,
        including both root-level nodes and nodes nested within containers.
        This is needed for connection rendering to work with nested nodes.

        Args:
            view: View object to scan for nodes

        Returns:
            Dictionary mapping node UUID to node object
        """
        nodes_dict = dict(view.nodes_dict)  # Start with root-level nodes

        def add_nested_nodes(parent_node: Any) -> None:
            """Recursively add nested nodes from containers."""
            for child in parent_node.nodes:
                nodes_dict[child.uuid] = child
                # Recursively add grandchildren
                add_nested_nodes(child)

        # Add all nested nodes from root-level containers
        for root_node in view.nodes:
            add_nested_nodes(root_node)

        return nodes_dict

    def _is_containment_relationship(self, conn: Any, complete_nodes_dict: dict[str, Any]) -> bool:
        """Check if a connection represents a containment relationship.

        Containment relationships (Composition/Aggregation from container to child)
        are redundant with the visual containment shown by container boundaries
        and should be hidden from the SVG output.

        Args:
            conn: Connection to check
            complete_nodes_dict: Dictionary of all nodes

        Returns:
            True if this is a containment relationship, False otherwise
        """
        source_uuid = getattr(conn, "_source", None)
        target_uuid = getattr(conn, "_target", None)
        rel_type = getattr(conn, "type", "")

        if not source_uuid or not target_uuid:
            return False

        # Only Composition and Aggregation can represent containment
        if rel_type not in ("CompositionRelationship", "Composition", "AggregationRelationship", "Aggregation"):
            return False

        # Check if target is a child of source
        source_node = complete_nodes_dict.get(source_uuid)
        target_node = complete_nodes_dict.get(target_uuid)

        if not source_node or not target_node:
            return False

        # If target is in source's children, it's a containment relationship
        return target_node in getattr(source_node, "nodes", [])
    def to_svg(self, view: Any, filepath: Optional[str] = None) -> str:
        """Export view to SVG string and optionally write to file.

        Args:
            view: View object to export
            filepath: Optional path to write SVG file to

        Returns:
            SVG string (valid XML with <svg> root)
        """
        # Calculate view bounds
        bounds = self._calculate_bounds(view)

        # Create SVG root element
        svg_width = bounds["max_x"] + self.SVG_MARGIN
        svg_height = bounds["max_y"] + self.SVG_MARGIN

        svg = ET.Element(
            "svg",
            {
                "xmlns": "http://www.w3.org/2000/svg",
                "xmlns:xlink": "http://www.w3.org/1999/xlink",
                "width": str(int(svg_width)),
                "height": str(int(svg_height)),
                "viewBox": f"0 0 {int(svg_width)} {int(svg_height)}",
            },
        )

        # Add defs block with arrowhead marker
        self._add_defs(svg)

        # Add white background rectangle
        self._add_background(svg, svg_width, svg_height)

        # Compute temporary endpoint spreads so repeated connections do not stack
        endpoint_spreads = self._compute_endpoint_spreads(view)

        # Build complete nodes dictionary including nested nodes (for connection rendering)
        complete_nodes_dict = self._build_complete_nodes_dict(view)

        # Render nodes on top, respecting containment hierarchy (parents before children)
        sorted_nodes = self._sort_nodes_by_hierarchy(view)

        # Build a mapping of node UUID to SVG parent element
        # This ensures nested nodes are rendered inside their container groups
        svg_parents: dict[str, ET.Element] = {}
        svg_parents["root"] = svg

        for node in sorted_nodes:
            # Determine parent element for this node
            # If node is in another node's children, render it inside that node's group
            parent_elem = svg
            for potential_parent in sorted_nodes:
                if node != potential_parent and node in getattr(potential_parent, "nodes", []):
                    # Find the SVG group for the parent node
                    parent_uuid = getattr(potential_parent, "uuid", None)
                    if parent_uuid in svg_parents:
                        parent_elem = svg_parents[parent_uuid]
                    break

            # Render node into the appropriate parent element
            node_group = self._render_node_into(parent_elem, node)
            node_uuid = getattr(node, "uuid", None)
            if node_uuid:
                svg_parents[node_uuid] = node_group

        # Render connections/relationships last (so they appear on top of nodes)
        # Try new rendering with relationship styles, fall back to basic rendering if needed
        relationship_service = RelationshipStyleService()
        for conn in view.conns:
            # Skip containment relationships (they're already shown visually by container boundaries)
            if self._is_containment_relationship(conn, complete_nodes_dict):
                continue
            self._render_relationship(svg, conn, complete_nodes_dict, relationship_service, endpoint_spreads)

        # Convert to string
        svg_string = ET.tostring(svg, encoding="unicode")

        # Write to file if filepath provided
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(svg_string)

        return svg_string

    def _calculate_bounds(self, view: Any) -> dict[str, float]:
        """Calculate the bounding box of all elements in the view.

        Args:
            view: View object

        Returns:
            Dictionary with min_x, min_y, max_x, max_y
        """
        bounds = {
            "min_x": float("inf"),
            "min_y": float("inf"),
            "max_x": 0.0,
            "max_y": 0.0,
        }

        nodes = getattr(view, "nodes", [])
        if not nodes:
            return bounds

        for node in nodes:
            x = float(getattr(node, "x", 0))
            y = float(getattr(node, "y", 0))
            w = float(getattr(node, "w", 120))
            h = float(getattr(node, "h", 55))

            bounds["min_x"] = min(bounds["min_x"], x)
            bounds["min_y"] = min(bounds["min_y"], y)
            bounds["max_x"] = max(bounds["max_x"], x + w)
            bounds["max_y"] = max(bounds["max_y"], y + h)

        # Handle empty view
        if bounds["min_x"] == float("inf"):
            bounds["min_x"] = 0
            bounds["min_y"] = 0
            bounds["max_x"] = 100
            bounds["max_y"] = 100

        return bounds

    def _add_defs(self, svg: ET.Element) -> None:
        """Add SVG definitions (markers only - no symbol definitions).

        Args:
            svg: SVG root element
        """
        defs = ET.SubElement(svg, "defs")

        # Arrowhead marker (filled triangle) - for connections
        marker = ET.SubElement(
            defs,
            "marker",
            {
                "id": "arrowhead",
                "markerWidth": str(self.ARROWHEAD_SIZE),
                "markerHeight": str(self.ARROWHEAD_SIZE),
                "refX": str(self.ARROWHEAD_SIZE - 2),
                "refY": str(self.ARROWHEAD_SIZE // 2),
                "orient": "auto",
            },
        )

        # Triangle polygon for arrowhead
        ET.SubElement(
            marker,
            "polygon",
            {
                "points": f"0 0, {self.ARROWHEAD_SIZE} {self.ARROWHEAD_SIZE // 2}, 0 {self.ARROWHEAD_SIZE}",
                "fill": "black",
            },
        )

        # Relationship markers
        # Filled arrow (for serving, access, etc.)
        marker_filled = ET.SubElement(
            defs,
            "marker",
            {
                "id": "arrow-filled",
                "markerWidth": "8",
                "markerHeight": "8",
                "refX": "6",
                "refY": "4",
                "orient": "auto",
            },
        )
        ET.SubElement(
            marker_filled,
            "polygon",
            {
                "points": "0 0, 8 4, 0 8",
                "fill": "black",
            },
        )

        # Hollow arrow (for realization, etc.)
        marker_hollow = ET.SubElement(
            defs,
            "marker",
            {
                "id": "arrow-hollow",
                "markerWidth": "8",
                "markerHeight": "8",
                "refX": "6",
                "refY": "4",
                "orient": "auto",
            },
        )
        ET.SubElement(
            marker_hollow,
            "polygon",
            {
                "points": "0 0, 8 4, 0 8",
                "fill": "none",
                "stroke": "black",
                "stroke-width": "1",
            },
        )

        # Diamond filled (for composition)
        marker_diamond_filled = ET.SubElement(
            defs,
            "marker",
            {
                "id": "diamond-filled",
                "markerWidth": "8",
                "markerHeight": "8",
                "refX": "4",
                "refY": "4",
                "orient": "auto",
            },
        )
        ET.SubElement(
            marker_diamond_filled,
            "polygon",
            {
                "points": "4 0, 8 4, 4 8, 0 4",
                "fill": "black",
            },
        )

        # Diamond hollow (for aggregation)
        marker_diamond_hollow = ET.SubElement(
            defs,
            "marker",
            {
                "id": "diamond-hollow",
                "markerWidth": "8",
                "markerHeight": "8",
                "refX": "4",
                "refY": "4",
                "orient": "auto",
            },
        )
        ET.SubElement(
            marker_diamond_hollow,
            "polygon",
            {
                "points": "4 0, 8 4, 4 8, 0 4",
                "fill": "none",
                "stroke": "black",
                "stroke-width": "1",
            },
        )

    def _add_background(self, svg: ET.Element, width: float, height: float) -> None:
        """Add white background rectangle to SVG canvas.

        Args:
            svg: SVG root element
            width: SVG canvas width
            height: SVG canvas height
        """
        ET.SubElement(
            svg,
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": str(int(width)),
                "height": str(int(height)),
                "fill": "white",
                "stroke": "none",
            },
        )

    def _scale_path(self, svg_path: str, x: float, y: float, w: float, h: float) -> str:
        """Scale SVG path from 150×75 reference frame to element bounds.

        Transforms path coordinates from the 150×75 reference space to (x, y, w, h):
        - x_new = x + x_ref * (w / 150.0)
        - y_new = y + y_ref * (h / 75.0)

        Args:
            svg_path: SVG path data
            x, y: Element position
            w, h: Element dimensions

        Returns:
            Scaled SVG path
        """
        return self._apply_path_transform(svg_path, x, y, w / 150.0, h / 75.0)

    def _translate_icon(
        self, icon_path: str, icon_viewbox: str, icon_ox: float, icon_oy: float
    ) -> str:
        """Translate icon path from reference origin to canvas position.

        Args:
            icon_path: SVG path data
            icon_viewbox: Icon viewBox (e.g., "128 5 22 15")
            icon_ox, icon_oy: Canvas position for icon

        Returns:
            Translated SVG path
        """
        # Parse viewBox to get origin offset
        parts = icon_viewbox.split()
        min_x = float(parts[0])
        min_y = float(parts[1])
        # Calculate translation to move from reference origin to canvas position
        tx = icon_ox - min_x
        ty = icon_oy - min_y
        return self._apply_path_transform(icon_path, tx, ty, 1.0, 1.0)

    def _apply_path_transform(
        self, svg_path: str, tx: float, ty: float, sx: float, sy: float
    ) -> str:
        """Apply transformation (translate + scale) to SVG path.

        Args:
            svg_path: SVG path data
            tx, ty: Translation offset
            sx, sy: Scale factors

        Returns:
            Transformed path
        """
        import re

        def transform_number(match: Any) -> str:
            """Transform a single coordinate."""
            x_str = match.group(1)
            y_str = match.group(2)
            x = float(x_str)
            y = float(y_str)
            x_new = tx + x * sx
            y_new = ty + y * sy
            # Format with minimal decimal places
            x_fmt = f"{x_new:.1f}".rstrip('0').rstrip('.')
            y_fmt = f"{y_new:.1f}".rstrip('0').rstrip('.')
            return f"{x_fmt} {y_fmt}"

        # Match coordinate pairs: "x y" (with optional decimal points)
        result = re.sub(r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', transform_number, svg_path)
        return result

    def _render_node(self, svg: ET.Element, node: Any) -> None:
        """Render a single node as an ArchiMate symbol with text.

        Args:
            svg: SVG root element
            node: Node to render
        """
        self._render_node_into(svg, node)

    def _render_node_into(self, parent: ET.Element, node: Any) -> ET.Element:
        """Render a single node as flat inline SVG with stacked layers.

        Renders each element as:
        1. Filled shape (rect or path)
        2. Stroked border
        3. Icon (fixed-size line-art) if available
        4. Text label

        Args:
            parent: Parent SVG element to render into
            node: Node to render

        Returns:
            The SVG group element for this node (for nested children)
        """
        x = float(getattr(node, "x", 0))
        y = float(getattr(node, "y", 0))
        w = float(getattr(node, "w", 120))
        h = float(getattr(node, "h", 55))
        element_type = getattr(node, "type", "BusinessActor")
        element_id = getattr(node, "uuid", None)

        # Group for node
        g = ET.SubElement(parent, "g", {"class": "node"})

        # Check if this is a container (has child nodes)
        has_children = len(getattr(node, "nodes", [])) > 0

        # ── Container nodes: dashed, transparent border ────────────
        if has_children and element_type != "Group":
            ET.SubElement(
                g,
                "rect",
                {
                    "x": str(int(x)),
                    "y": str(int(y)),
                    "width": str(int(w)),
                    "height": str(int(h)),
                    "fill": "none",
                    "stroke": "black",
                    "stroke-width": "1",
                    "stroke-dasharray": "5,5",
                },
            )
            self._render_topleft_text(g, node, x, y, w)
            return g

        # ── Group: solid grey, no icon, label top-left ───────────────
        if element_type == "Group":
            color = getattr(node, "fill_color", None) or "#d9d9d9"
            ET.SubElement(
                g,
                "rect",
                {
                    "x": str(int(x)),
                    "y": str(int(y)),
                    "width": str(int(w)),
                    "height": str(int(h)),
                    "fill": color,
                    "stroke": "black",
                    "stroke-width": "1",
                },
            )
            self._render_topleft_text(g, node, x, y, w)
            return g

        # ── Regular element ──────────────────────────────────────────
        symbol_def = ARCHIMATE_SYMBOLS.get(element_type)
        if not symbol_def:
            symbol_def = ARCHIMATE_SYMBOLS["BusinessActor"]

        color = getattr(node, "fill_color", None) or get_element_color(element_type, element_id)
        body_type = symbol_def.body_type

        if body_type == "rect":
            # 1. Filled body
            ET.SubElement(
                g,
                "rect",
                {
                    "x": str(int(x)),
                    "y": str(int(y)),
                    "width": str(int(w)),
                    "height": str(int(h)),
                    "fill": color,
                    "stroke": "none",
                },
            )
            # 2. Border
            ET.SubElement(
                g,
                "rect",
                {
                    "x": str(int(x)),
                    "y": str(int(y)),
                    "width": str(int(w)),
                    "height": str(int(h)),
                    "fill": "none",
                    "stroke": "black",
                    "stroke-width": "1",
                },
            )

        elif body_type == "rect_header":
            # Header stripe at 20% from top (y=15 in 75-unit reference frame)
            header_y = y + h * (15.0 / 75.0)
            # 1. Filled body
            ET.SubElement(
                g,
                "rect",
                {
                    "x": str(int(x)),
                    "y": str(int(y)),
                    "width": str(int(w)),
                    "height": str(int(h)),
                    "fill": color,
                    "stroke": "none",
                },
            )
            # 2. Border
            ET.SubElement(
                g,
                "rect",
                {
                    "x": str(int(x)),
                    "y": str(int(y)),
                    "width": str(int(w)),
                    "height": str(int(h)),
                    "fill": "none",
                    "stroke": "black",
                    "stroke-width": "1",
                },
            )
            # 3. Header line
            ET.SubElement(
                g,
                "line",
                {
                    "x1": str(int(x)),
                    "y1": f"{header_y:.1f}",
                    "x2": str(int(x + w)),
                    "y2": f"{header_y:.1f}",
                    "stroke": "black",
                    "stroke-width": "1",
                },
            )

        else:  # "path"
            scaled_body = self._scale_path(symbol_def.svg_path, x, y, w, h)
            # 1. Filled shape
            ET.SubElement(g, "path", {"d": scaled_body, "fill": color, "stroke": "none"})
            # 2. Stroked border
            ET.SubElement(
                g,
                "path",
                {"d": scaled_body, "fill": "none", "stroke": "black", "stroke-width": "1"},
            )

        # 3. Icon (top-right, fixed size, translated line-art)
        if symbol_def.icon_path and symbol_def.icon_viewbox:
            ICON_MARGIN = 4  # noqa: C901, N806
            icon_ox = x + w - 20 - ICON_MARGIN  # 4px from right edge, 20px wide
            icon_oy = y + ICON_MARGIN  # 4px from top
            translated = self._translate_icon(symbol_def.icon_path, symbol_def.icon_viewbox, icon_ox, icon_oy)
            ET.SubElement(
                g,
                "path",
                {"d": translated, "fill": "none", "stroke": "black", "stroke-width": "1"},
            )

        # 4. Text
        has_children = len(getattr(node, "nodes", [])) > 0
        element_name = getattr(node, "name", getattr(node, "label", ""))
        if element_name:
            if has_children:
                self._render_topleft_text(g, node, x, y, w)
            else:
                self._render_wrapped_text(
                    g, element_name, x + w / 2, y + h / 2, w - 8, is_centered=True
                )

        return g

    def _render_topleft_text(self, parent: ET.Element, node: Any, x: float, y: float, w: float) -> None:
        """Render text label at top-left for Grouping/Group elements.

        Args:
            parent: Parent SVG element
            node: Node with name/label
            x, y: Element position
            w: Element width
        """
        name = getattr(node, "name", getattr(node, "label", ""))
        if name:
            self._render_wrapped_text(parent, name, x + 5, y + 14, w - 10, is_centered=False)

    def _render_wrapped_text(
        self,
        parent: ET.Element,
        text: str,
        text_x: float,
        text_y: float,
        max_width: float,
        is_centered: bool = True,
    ) -> None:
        """Render text with automatic word wrapping.

        Args:
            parent: Parent SVG element
            text: Text to render
            text_x: X coordinate of text position
            text_y: Y coordinate of text position
            max_width: Maximum width for text
            is_centered: If True, text is centered at (text_x, text_y); if False, positioned at top-left
        """
        # Word wrap the text
        lines = self._word_wrap_text(text, max_width)

        # Calculate vertical positioning
        line_height = 11  # pixels
        if is_centered:
            total_height = len(lines) * line_height
            start_y = text_y - total_height / 2
            anchor = "middle"
            x_pos = text_x
            y_pos = start_y + line_height / 2
        else:
            # For top-left aligned text
            start_y = text_y
            anchor = "start"
            x_pos = text_x
            y_pos = start_y + line_height / 2

        # Create text element
        text_elem = ET.SubElement(
            parent,
            "text",
            {
                "x": str(int(x_pos)),
                "y": str(int(y_pos)),
                "text-anchor": anchor,
                "font-family": "Arial, sans-serif",
                "font-size": "10",
                "fill": "black",
            },
        )

        # Add lines as tspan elements
        for i, line in enumerate(lines):
            if i == 0:
                text_elem.text = line
            else:
                tspan = ET.SubElement(
                    text_elem,
                    "tspan",
                    {
                        "x": str(int(x_pos)),
                        "dy": str(line_height),
                    },
                )
                tspan.text = line

    def _word_wrap_text(self, text: str, max_width: float) -> list[str]:
        """Word wrap text to fit within max_width.

        Args:
            text: Text to wrap
            max_width: Maximum width in pixels

        Returns:
            List of text lines
        """
        # Estimate characters per line (rough: ~6 pixels per character)
        chars_per_line = max(1, int(max_width / 6))

        words = text.split()
        lines: list[str] = []
        current_line: list[str] = []

        for word in words:
            # Check if adding this word would exceed the limit
            test_line = " ".join(current_line + [word])
            if len(test_line) <= chars_per_line:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines if lines else [text]

    def _render_marker_shape(
        self,
        svg: ET.Element,
        endpoint: tuple[float, float],
        direction_from: tuple[float, float],
        marker_type: str,
        color: str,
        position: str,
    ) -> None:
        """Render a marker shape (arrow or diamond) at a polyline endpoint.

        Args:
            svg: SVG root element
            endpoint: (x, y) position of the marker
            direction_from: (x, y) of the point before endpoint (for direction)
            marker_type: Type of marker ('filled', 'hollow', 'diamond')
            color: Color of the marker
            position: 'start' or 'end' (affects direction)
        """
        import math

        ex, ey = endpoint
        dx = direction_from[0] - ex
        dy = direction_from[1] - ey

        # Normalize direction
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.1:
            return

        dx /= dist
        dy /= dist

        if position == "end":
            # Arrow pointing in direction of line
            dx = -dx
            dy = -dy

        # Create arrow pointing marker (larger size for visibility)
        marker_size = 12
        if marker_type in ("filled", "hollow"):
            # Triangle arrow: base perpendicular to direction, point along direction
            perp_x = -dy
            perp_y = dx

            # Triangle vertices (pointing along dx, dy direction)
            p1 = (ex + dx * marker_size, ey + dy * marker_size)  # Point
            p2 = (
                ex - perp_x * marker_size / 2 - dx * marker_size / 3,
                ey - perp_y * marker_size / 2 - dy * marker_size / 3,
            )  # Base corners
            p3 = (
                ex + perp_x * marker_size / 2 - dx * marker_size / 3,
                ey + perp_y * marker_size / 2 - dy * marker_size / 3,
            )

            points_str = f"{p1[0]},{p1[1]} {p2[0]},{p2[1]} {p3[0]},{p3[1]}"

            fill = color if marker_type == "filled" else "none"
            stroke = "none" if marker_type == "filled" else color
            stroke_width = "1" if marker_type == "filled" else "1.5"

            ET.SubElement(
                svg,
                "polygon",
                {
                    "points": points_str,
                    "fill": fill,
                    "stroke": stroke,
                    "stroke-width": stroke_width,
                    "stroke-linejoin": "miter",
                },
            )

        elif marker_type == "diamond":
            # Diamond marker (larger for visibility)
            size = 8
            p1 = (ex + dx * size, ey + dy * size)
            p2 = (ex - dy * size, ey + dx * size)
            p3 = (ex - dx * size, ey - dy * size)
            p4 = (ex + dy * size, ey - dx * size)

            points_str = f"{p1[0]},{p1[1]} {p2[0]},{p2[1]} {p3[0]},{p3[1]} {p4[0]},{p4[1]}"

            fill = color if marker_type == "diamond" else "none"
            stroke = "none" if marker_type == "diamond" else color
            stroke_width = "1" if marker_type == "diamond" else "1.5"

            ET.SubElement(
                svg,
                "polygon",
                {
                    "points": points_str,
                    "fill": fill,
                    "stroke": stroke,
                    "stroke-width": stroke_width,
                    "stroke-linejoin": "miter",
                },
            )

    def _render_relationship(
        self,
        svg: ET.Element,
        conn: Any,
        nodes_dict: dict[str, Any],
        relationship_service: RelationshipStyleService,
        endpoint_spreads: dict[tuple[str, str, int], tuple[float, float]],
    ) -> None:
        """Render a single relationship with ArchiMate styling.

        Args:
            svg: SVG root element
            conn: Connection/relationship to render
            nodes_dict: Dictionary of nodes by uuid
            relationship_service: Service for relationship styles
        """
        source_uuid = getattr(conn, "_source", None)
        target_uuid = getattr(conn, "_target", None)

        if not source_uuid or not target_uuid:
            return

        source_node = nodes_dict.get(source_uuid)
        target_node = nodes_dict.get(target_uuid)

        if not source_node or not target_node:
            return

        # Get bendpoints
        bendpoints = getattr(conn, "bendpoints", [])

        # Build polyline points
        points = self._get_clipped_polyline_points(
            source_node,
            target_node,
            bendpoints,
            endpoint_spreads.get((source_uuid, "src", id(conn)), (0.0, 0.0)),
            endpoint_spreads.get((target_uuid, "tgt", id(conn)), (0.0, 0.0)),
        )

        if len(points) < 2:
            return

        # Get relationship type and style
        rel_type = getattr(conn, "type", "Association")
        relationship_style = relationship_service.get_style(rel_type)

        # If no style found, try without "Relationship" suffix
        if not relationship_style and "Relationship" in rel_type:
            relationship_style = relationship_service.get_style(rel_type.replace("Relationship", ""))

        # Fall back to basic connection rendering if no style found
        if not relationship_style:
            self._render_connection(svg, conn, nodes_dict, endpoint_spreads)
            return

        # Apply per-relationship overrides if available
        stroke_color = getattr(conn, "stroke_color", None) or relationship_style.stroke_color
        stroke_width = getattr(conn, "stroke_width", None) or relationship_style.stroke_width
        stroke_dasharray = getattr(conn, "stroke_style", None) or relationship_style.stroke_dasharray

        # Render polyline with relationship style
        points_str = " ".join(f"{int(p[0])},{int(p[1])}" for p in points)
        polyline_attrs = {
            "points": points_str,
            "fill": "none",
            "stroke": stroke_color,
            "stroke-width": str(stroke_width),
            "opacity": "0.8",
        }

        # Add dash pattern if specified
        if stroke_dasharray:
            polyline_attrs["stroke-dasharray"] = stroke_dasharray

        # Add markers if specified
        # Composition and Aggregation show start marker (diamond) only
        if relationship_style.marker_start:
            polyline_attrs["marker-start"] = relationship_style.marker_start
        if relationship_style.marker_end and rel_type not in (
            "CompositionRelationship",
            "Composition",
            "AggregationRelationship",
            "Aggregation",
        ):
            polyline_attrs["marker-end"] = relationship_style.marker_end

        ET.SubElement(svg, "polyline", polyline_attrs)

        # Render relationship label
        label_text = self._get_short_type_name(rel_type)
        if label_text and len(points) >= 2:
            self._render_connection_label(svg, points, label_text)

    def _render_connection(
        self,
        svg: ET.Element,
        conn: Any,
        nodes_dict: dict[str, Any],
        endpoint_spreads: dict[tuple[str, str, int], tuple[float, float]],
    ) -> None:
        """Render a single connection as a polyline with optional label.

        Args:
            svg: SVG root element
            conn: Connection to render
            nodes_dict: Dictionary of nodes by uuid
        """
        source_uuid = getattr(conn, "_source", None)
        target_uuid = getattr(conn, "_target", None)

        if not source_uuid or not target_uuid:
            return

        source_node = nodes_dict.get(source_uuid)
        target_node = nodes_dict.get(target_uuid)

        if not source_node or not target_node:
            return

        # Get bendpoints
        bendpoints = getattr(conn, "bendpoints", [])

        # Build polyline points
        points = self._get_clipped_polyline_points(
            source_node,
            target_node,
            bendpoints,
            endpoint_spreads.get((source_uuid, "src", id(conn)), (0.0, 0.0)),
            endpoint_spreads.get((target_uuid, "tgt", id(conn)), (0.0, 0.0)),
        )

        if len(points) < 2:
            return

        # Render polyline
        points_str = " ".join(f"{int(p[0])},{int(p[1])}" for p in points)
        ET.SubElement(
            svg,
            "polyline",
            {
                "points": points_str,
                "fill": "none",
                "stroke": "black",
                "stroke-width": "1",
                "marker-end": "url(#arrowhead)",
            },
        )

        # Render connection label
        rel_type = getattr(conn, "type", "Relationship")
        label_text = self._get_short_type_name(rel_type)

        if label_text and len(points) >= 2:
            self._render_connection_label(svg, points, label_text)

    def _get_clipped_polyline_points(
        self,
        source_node: Any,
        target_node: Any,
        bendpoints: list[Any],
        source_spread: tuple[float, float] = (0.0, 0.0),
        target_spread: tuple[float, float] = (0.0, 0.0),
    ) -> list[Tuple[float, float]]:
        """Get polyline points clipped at node boundary edges.

        SVG export renders views as stored in the model without routing:
        - If bendpoints exist: Use them with routing logic (for auto-layout results)
        - If no bendpoints: Render simple direct path (model as-is)

        Args:
            source_node: Source node
            target_node: Target node
            bendpoints: List of intermediate bendpoints (if any)

        Returns:
            List of (x, y) tuples representing polyline points
        """
        # Get source and target centers
        sx = float(getattr(source_node, "x", 0)) + float(getattr(source_node, "w", 120)) / 2
        sy = float(getattr(source_node, "y", 0)) + float(getattr(source_node, "h", 55)) / 2
        tx = float(getattr(target_node, "x", 0)) + float(getattr(target_node, "w", 120)) / 2
        ty = float(getattr(target_node, "y", 0)) + float(getattr(target_node, "h", 55)) / 2

        sx += source_spread[0]
        sy += source_spread[1]
        tx += target_spread[0]
        ty += target_spread[1]

        # Get node bounds
        source_bounds = self._get_node_bounds(source_node)
        target_bounds = self._get_node_bounds(target_node)

        # If no bendpoints: Render simple direct line clipped at boundaries
        if not bendpoints:
            start_point = self._clip_point_to_boundary(source_bounds, (sx, sy), (tx, ty))
            end_point = self._clip_point_to_boundary(target_bounds, (tx, ty), (sx, sy))
            return [start_point, end_point]

        # With bendpoints: Apply routing logic for proper orthogonal paths
        # Use first bendpoint (not final target) to determine source exit side
        first_bendpoint = (bendpoints[0].x, bendpoints[0].y) if bendpoints else (tx, ty)
        source_side = self._preferred_boundary_side(source_bounds, first_bendpoint, exit_from=True)

        # Use last bendpoint (not source) to determine target entry side
        last_bendpoint = (bendpoints[-1].x, bendpoints[-1].y) if bendpoints else (sx, sy)
        target_side = self._preferred_boundary_side(target_bounds, last_bendpoint, exit_from=True)

        start_point = self._boundary_anchor(source_bounds, source_side, source_spread)
        end_point = self._boundary_anchor(target_bounds, target_side, target_spread)

        # Build full polyline (source anchor → bendpoints → target anchor)
        full_points = [start_point]

        # Add bendpoints
        for bp in bendpoints:
            bx = float(getattr(bp, "x", 0))
            by = float(getattr(bp, "y", 0))
            full_points.append((bx, by))

        full_points.append(end_point)

        # Insert source boundary stub so the first segment exits orthogonally.
        if len(full_points) >= 2:
            full_points.insert(1, self._boundary_stub(full_points[0], source_side))

        # Preserve the chosen target side for the final segment and marker orientation.
        target_orientation = "horizontal" if target_side in ("left", "right") else "vertical"
        if len(full_points) >= 2:
            full_points[-1] = end_point

        source_orientation = "horizontal" if source_side in ("top", "bottom") else "vertical"

        full_points = self._orthogonalize_polyline_points(
            full_points,
            target_orientation=target_orientation,
            source_orientation=source_orientation,
        )

        return full_points

    def _orthogonalize_polyline_points(
        self,
        points: list[Tuple[float, float]],
        target_orientation: str = "vertical",
        source_orientation: str = "vertical",
    ) -> list[Tuple[float, float]]:
        """Insert corners so each segment is axis-aligned.

        The SVG export should use only horizontal and vertical segments.
        Existing bendpoints are preserved, but diagonal segments are split
        into L-shaped turns.
        """
        if len(points) < 2:
            return points

        orthogonal: list[Tuple[float, float]] = [points[0]]
        for idx, (prev, cur) in enumerate(zip(points, points[1:], strict=False)):
            if prev[0] == cur[0] or prev[1] == cur[1]:
                orthogonal.append(cur)
                continue

            if idx == len(points) - 2:
                corner = (prev[0], cur[1]) if target_orientation == "horizontal" else (cur[0], prev[1])
            elif idx == 0:
                corner = (prev[0], cur[1]) if source_orientation == "horizontal" else (cur[0], prev[1])
            elif abs(cur[0] - prev[0]) >= abs(cur[1] - prev[1]):
                corner = (cur[0], prev[1])
            else:
                corner = (prev[0], cur[1])

            if orthogonal[-1] != corner:
                orthogonal.append(corner)
            orthogonal.append(cur)

        return orthogonal

    @staticmethod
    def _boundary_side(
        bounds: Tuple[float, float, float, float],
        point: Tuple[float, float],
    ) -> str | None:
        """Return which rectangle edge a point lies on."""
        x1, y1, x2, y2 = bounds
        px, py = point
        if abs(py - y1) < 0.01:
            return "top"
        if abs(py - y2) < 0.01:
            return "bottom"
        if abs(px - x1) < 0.01:
            return "left"
        if abs(px - x2) < 0.01:
            return "right"
        return None

    @staticmethod
    def _boundary_stub(
        point: Tuple[float, float],
        side: str,
        length: float = 8.0,
    ) -> Tuple[float, float]:
        """Create a short orthogonal stub away from a boundary edge."""
        x, y = point
        if side == "top":
            return x, y - length
        if side == "bottom":
            return x, y + length
        if side == "left":
            return x - length, y
        if side == "right":
            return x + length, y
        return point

    def _boundary_anchor(
        self,
        bounds: Tuple[float, float, float, float],
        side: str,
        spread: tuple[float, float],
    ) -> Tuple[float, float]:
        """Place an anchor on the requested edge, clamped away from corners."""
        x1, y1, x2, y2 = bounds
        margin = self.EDGE_CORNER_MARGIN
        if side in ("left", "right"):
            axis_value = (y1 + y2) / 2.0 + spread[1]
            y = max(y1 + margin, min(y2 - margin, axis_value))
            x = x1 if side == "left" else x2
            return x, y

        axis_value = (x1 + x2) / 2.0 + spread[0]
        x = max(x1 + margin, min(x2 - margin, axis_value))
        y = y1 if side == "top" else y2
        return x, y

    @staticmethod
    def _preferred_boundary_side(
        bounds: Tuple[float, float, float, float],
        other_point: Tuple[float, float],
        exit_from: bool = True,
    ) -> str:
        """Pick the edge side that best matches the connection direction."""
        x1, y1, x2, y2 = bounds
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        ox, oy = other_point
        dx = ox - cx
        dy = oy - cy

        if abs(dx) >= abs(dy):
            if dx >= 0:
                return "right" if exit_from else "left"
            return "left" if exit_from else "right"

        if dy >= 0:
            return "bottom" if exit_from else "top"
        return "top" if exit_from else "bottom"

    @staticmethod
    def _infer_boundary_orientation(
        bounds: Tuple[float, float, float, float],
        point: Tuple[float, float],
        exit_from: bool = False,
    ) -> str:
        """Infer whether a boundary point lies on a horizontal or vertical edge."""
        x1, y1, x2, y2 = bounds
        px, py = point
        if abs(px - x1) < 0.01 or abs(px - x2) < 0.01:
            return "horizontal"
        if abs(py - y1) < 0.01 or abs(py - y2) < 0.01:
            return "vertical"
        return "vertical" if exit_from else "horizontal"

    @staticmethod
    def _clip_point_to_boundary(  # noqa: C901
        bounds: Tuple[float, float, float, float],
        from_point: Tuple[float, float],
        to_point: Tuple[float, float],
    ) -> Tuple[float, float]:
        """Find the boundary intersection point of a line segment with a rectangle.

        Returns the point where the line from from_point toward to_point exits the rectangle.
        Uses simple intersection tests with all four edges.
        """
        x1, y1, x2, y2 = bounds
        fx, fy = from_point
        tx, ty = to_point

        dx = tx - fx
        dy = ty - fy

        # If from_point is already on or outside boundary, return it
        if abs(dx) < 0.01 and abs(dy) < 0.01:
            return from_point

        # Find closest intersection with rectangle edges
        min_t = 1.0
        result = to_point

        # Right edge (x = x2)
        if abs(dx) > 0.01:
            t = (x2 - fx) / dx
            if 0 < t < min_t:
                y = fy + t * dy
                if y1 <= y <= y2:
                    min_t = t
                    result = (x2, y)

        # Left edge (x = x1)
        if abs(dx) > 0.01:
            t = (x1 - fx) / dx
            if 0 < t < min_t:
                y = fy + t * dy
                if y1 <= y <= y2:
                    min_t = t
                    result = (x1, y)

        # Bottom edge (y = y2)
        if abs(dy) > 0.01:
            t = (y2 - fy) / dy
            if 0 < t < min_t:
                x = fx + t * dx
                if x1 <= x <= x2:
                    min_t = t
                    result = (x, y2)

        # Top edge (y = y1)
        if abs(dy) > 0.01:
            t = (y1 - fy) / dy
            if 0 < t < min_t:
                x = fx + t * dx
                if x1 <= x <= x2:
                    min_t = t
                    result = (x, y1)

        return result

    def _compute_endpoint_spreads(  # noqa: C901
        self,
        view: Any,
    ) -> dict[tuple[str, str, int], tuple[float, float]]:
        """Compute temporary source/target offsets for repeated connections.

        The calculation mirrors the layout layer's spreading logic, but it is
        kept local to SVG export so the model itself is not mutated.
        """
        endpoint_spreads: dict[tuple[str, str, int], tuple[float, float]] = {}
        def _collect_all_nodes(node_dict: dict[str, Any]) -> dict[str, Any]:
            result = {}
            for uuid, node in node_dict.items():
                result[uuid] = node
                child_dict = getattr(node, "nodes_dict", {})
                if child_dict:
                    result.update(_collect_all_nodes(child_dict))
            return result

        nodes_dict: dict[Any, Any] = _collect_all_nodes(getattr(view, "nodes_dict", {}))
        conns = getattr(view, "conns", [])

        for node_uuid, node in nodes_dict.items():
            src_conns = [c for c in conns if getattr(c, "_source", None) == node_uuid]
            if len(src_conns) > 1:
                src_conns_sorted = sorted(
                    src_conns,
                    key=lambda c: float(
                        getattr(nodes_dict.get(getattr(c, "_target", None)), "cx", getattr(node, "cx", 0))
                    ),
                )
                for i, conn in enumerate(src_conns_sorted):
                    target_node = nodes_dict.get(getattr(conn, "_target", None))
                    if not target_node:
                        continue
                    dy = float(getattr(target_node, "cy", 0)) - float(getattr(node, "cy", 0))
                    dx = float(getattr(target_node, "cx", 0)) - float(getattr(node, "cx", 0))
                    spread_val = self._distributed_spread(
                        i,
                        len(src_conns_sorted),
                        float(getattr(node, "w", 120)) if abs(dy) > abs(dx) else float(getattr(node, "h", 55)),
                    )
                    if abs(dy) > abs(dx):
                        spread_x, spread_y = spread_val, 0.0
                    else:
                        spread_x, spread_y = 0.0, spread_val
                    endpoint_spreads[(node_uuid, "src", id(conn))] = (spread_x, spread_y)

            tgt_conns = [c for c in conns if getattr(c, "_target", None) == node_uuid]
            if len(tgt_conns) > 1:
                tgt_conns_sorted = sorted(
                    tgt_conns,
                    key=lambda c: float(
                        getattr(nodes_dict.get(getattr(c, "_source", None)), "cx", getattr(node, "cx", 0))
                    ),
                )
                for i, conn in enumerate(tgt_conns_sorted):
                    source_node = nodes_dict.get(getattr(conn, "_source", None))
                    if not source_node:
                        continue
                    dy = float(getattr(node, "cy", 0)) - float(getattr(source_node, "cy", 0))
                    dx = float(getattr(node, "cx", 0)) - float(getattr(source_node, "cx", 0))
                    spread_val = self._distributed_spread(
                        i,
                        len(tgt_conns_sorted),
                        float(getattr(node, "w", 120)) if abs(dy) > abs(dx) else float(getattr(node, "h", 55)),
                    )
                    if abs(dy) > abs(dx):
                        spread_x, spread_y = spread_val, 0.0
                    else:
                        spread_x, spread_y = 0.0, spread_val
                    endpoint_spreads[(node_uuid, "tgt", id(conn))] = (spread_x, spread_y)

        return endpoint_spreads

    def _distributed_spread(self, index: int, count: int, edge_span: float) -> float:
        """Return a centered spread value constrained to the middle of an edge."""
        if count <= 1:
            return 0.0

        usable_span = max(0.0, edge_span - 2 * self.EDGE_CORNER_MARGIN)
        if usable_span <= 0.0:
            return 0.0

        step = min(self.ENDPOINT_SPREAD_STEP, usable_span / max(1, count - 1))
        total_span = step * (count - 1)
        return -total_span / 2.0 + index * step

    def _get_node_bounds(self, node: Any) -> Tuple[float, float, float, float]:
        """Get node bounds using symbol bounding box when available.

        For symbol-based rendering, this uses the symbol's bounding box coordinates
        scaled to the node's width and height. For compatibility, falls back to
        simple rectangle bounds if symbol not found.

        Args:
            node: Node object

        Returns:
            Tuple of (x, y, x+w, y+h) representing the symbol's boundary
        """
        x = float(getattr(node, "x", 0))
        y = float(getattr(node, "y", 0))
        w = float(getattr(node, "w", 120))
        h = float(getattr(node, "h", 55))
        element_type = getattr(node, "type", "BusinessActor")

        # Get symbol definition to use its bounding box
        symbol_def = ARCHIMATE_SYMBOLS.get(element_type)
        if not symbol_def:
            # Fallback: use rectangle bounds
            return (x, y, x + w, y + h)

        # Scale symbol bounding box to node dimensions
        sym_x, sym_y, sym_w, sym_h = symbol_def.bounding_box
        # ViewBox is typically 0 0 100 100
        vb_parts = symbol_def.viewBox.split()
        vb_w = float(vb_parts[2]) if len(vb_parts) > 2 else 100.0
        vb_h = float(vb_parts[3]) if len(vb_parts) > 3 else 100.0

        # Scale from viewBox coordinates to node coordinates
        scale_x = w / vb_w if vb_w > 0 else 1.0
        scale_y = h / vb_h if vb_h > 0 else 1.0

        # Transform symbol bounds to node coordinate space
        bounds_x1 = x + sym_x * scale_x
        bounds_y1 = y + sym_y * scale_y
        bounds_x2 = x + (sym_x + sym_w) * scale_x
        bounds_y2 = y + (sym_y + sym_h) * scale_y

        return (bounds_x1, bounds_y1, bounds_x2, bounds_y2)

    def _clip_line_at_rectangle(  # noqa: C901
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        bounds: Tuple[float, float, float, float],
        exit_from: bool = True,
    ) -> Tuple[float, float]:
        """Clip a line segment at rectangle edge.

        Args:
            p1: Start point
            p2: End point
            bounds: Rectangle bounds (x1, y1, x2, y2)
            exit_from: If True, clip where exiting; if False, clip where entering

        Returns:
            Clipped point on rectangle edge
        """
        x1, y1, x2, y2 = bounds
        px1, py1 = p1
        px2, py2 = p2

        # If both points are outside or inside, return appropriate point
        if px1 == px2 and py1 == py2:
            return (px1, py1)

        # Find intersection with rectangle edges
        # Check each edge: top, bottom, left, right

        best_t = None
        best_point = (px1, py1) if exit_from else (px2, py2)

        # Direction vector
        dx = px2 - px1
        dy = py2 - py1

        # Check intersection with each edge
        # Top edge (y = y1)
        if dy != 0:
            t = (y1 - py1) / dy
            if 0 <= t <= 1:
                ix = px1 + t * dx
                if x1 <= ix <= x2:
                    if best_t is None or (exit_from and t > best_t) or (not exit_from and t < best_t):  # type: ignore[unreachable]
                        best_t = t
                        best_point = (ix, y1)

        # Bottom edge (y = y2)
        if dy != 0:
            t = (y2 - py1) / dy
            if 0 <= t <= 1:
                ix = px1 + t * dx
                if x1 <= ix <= x2:
                    if best_t is None or (exit_from and t > best_t) or (not exit_from and t < best_t):
                        best_t = t
                        best_point = (ix, y2)

        # Left edge (x = x1)
        if dx != 0:
            t = (x1 - px1) / dx
            if 0 <= t <= 1:
                iy = py1 + t * dy
                if y1 <= iy <= y2:
                    if best_t is None or (exit_from and t > best_t) or (not exit_from and t < best_t):
                        best_t = t
                        best_point = (x1, iy)

        # Right edge (x = x2)
        if dx != 0:
            t = (x2 - px1) / dx
            if 0 <= t <= 1:
                iy = py1 + t * dy
                if y1 <= iy <= y2:
                    if best_t is None or (exit_from and t > best_t) or (not exit_from and t < best_t):
                        best_t = t
                        best_point = (x2, iy)

        return best_point

    def _render_connection_label(
        self,
        svg: ET.Element,
        points: list[Tuple[float, float]],
        label_text: str,
    ) -> None:
        """Render a connection label on the longest segment.

        Args:
            svg: SVG root element
            points: Polyline points
            label_text: Label text to render
        """
        # Find longest segment
        longest_segment_idx = self._find_longest_segment(points)
        if longest_segment_idx is None:
            return

        # Get segment midpoint
        p1 = points[longest_segment_idx]
        p2 = points[longest_segment_idx + 1]
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2

        # Create group for label
        g = ET.SubElement(svg, "g", {"class": "connection-label"})

        # Background rectangle
        text_width = len(label_text) * 6  # estimate
        text_height = 12
        bg_x = mid_x - text_width / 2
        bg_y = mid_y - text_height / 2

        ET.SubElement(
            g,
            "rect",
            {
                "x": str(int(bg_x)),
                "y": str(int(bg_y)),
                "width": str(int(text_width)),
                "height": str(int(text_height)),
                "fill": "white",
                "stroke": "none",
            },
        )

        # Label text
        text_elem = ET.SubElement(
            g,
            "text",
            {
                "x": str(int(mid_x)),
                "y": str(int(mid_y + text_height / 3)),
                "text-anchor": "middle",
                "font-family": "Arial, sans-serif",
                "font-size": "9",
                "fill": "black",
            },
        )
        text_elem.text = label_text

    def _find_longest_segment(self, points: list[Tuple[float, float]]) -> Optional[int]:
        """Find the index of the longest segment in a polyline.

        Args:
            points: List of (x, y) points

        Returns:
            Index of the first point of the longest segment
        """
        if len(points) < 2:
            return None

        max_length: float = 0.0
        max_idx = 0

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.sqrt(dx * dx + dy * dy)

            if length > max_length:
                max_length = length
                max_idx = i

        return max_idx if max_length > 0 else 0

    def _get_short_type_name(self, rel_type: str) -> str:
        """Get short relationship type name (strip trailing "Relationship").

        Args:
            rel_type: Full relationship type name

        Returns:
            Short type name
        """
        if rel_type.endswith("Relationship"):
            return rel_type[: -len("Relationship")]
        return rel_type
