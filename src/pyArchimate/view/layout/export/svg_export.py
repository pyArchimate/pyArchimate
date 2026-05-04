"""SVG export service for rendering pyArchimate views as SVG diagrams.

This module provides functionality to export views as self-contained SVG files
for visual inspection, automated testing, and sharing without requiring the
Archi desktop tool.
"""

import math
from typing import Any, Optional, Tuple
from xml.etree import ElementTree as ET

from .symbols.archimate_symbols import ARCHIMATE_SYMBOLS
from .symbols.color_palette import get_element_color
from .symbols.archimate_relationships import (
    get_relationship_style,
    RelationshipStyleService,
)


class SVGExportService:
    """Service for exporting pyArchimate views as SVG diagrams."""

    # SVG render defaults
    SVG_MARGIN = 20  # pixels around the entire view
    TEXT_PADDING = 4  # pixels inside element rectangles
    ARROWHEAD_SIZE = 8  # size of arrowhead marker
    LABEL_PADDING = 2  # padding inside label background

    def __init__(self) -> None:
        """Initialize SVG export service."""
        pass

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
        svg_width = bounds['max_x'] + self.SVG_MARGIN
        svg_height = bounds['max_y'] + self.SVG_MARGIN

        svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'width': str(int(svg_width)),
            'height': str(int(svg_height)),
            'viewBox': f'0 0 {int(svg_width)} {int(svg_height)}',
        })

        # Add defs block with arrowhead marker
        self._add_defs(svg)

        # Add white background rectangle
        self._add_background(svg, svg_width, svg_height)

        # Render connections/relationships first (so they appear behind nodes)
        # Try new rendering with relationship styles, fall back to basic rendering if needed
        relationship_service = RelationshipStyleService()
        for conn in view.conns:
            self._render_relationship(svg, conn, view.nodes_dict, relationship_service)

        # Render nodes on top
        for node in view.nodes:
            self._render_node(svg, node)

        # Convert to string
        svg_string = ET.tostring(svg, encoding='unicode')

        # Write to file if filepath provided
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
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
            'min_x': float('inf'),
            'min_y': float('inf'),
            'max_x': 0.0,
            'max_y': 0.0,
        }

        nodes = getattr(view, 'nodes', [])
        if not nodes:
            return bounds

        for node in nodes:
            x = float(getattr(node, 'x', 0))
            y = float(getattr(node, 'y', 0))
            w = float(getattr(node, 'w', 120))
            h = float(getattr(node, 'h', 55))

            bounds['min_x'] = min(bounds['min_x'], x)
            bounds['min_y'] = min(bounds['min_y'], y)
            bounds['max_x'] = max(bounds['max_x'], x + w)
            bounds['max_y'] = max(bounds['max_y'], y + h)

        # Handle empty view
        if bounds['min_x'] == float('inf'):
            bounds['min_x'] = 0
            bounds['min_y'] = 0
            bounds['max_x'] = 100
            bounds['max_y'] = 100

        return bounds

    def _add_defs(self, svg: ET.Element) -> None:
        """Add SVG definitions (markers, patterns, etc.).

        Args:
            svg: SVG root element
        """
        defs = ET.SubElement(svg, 'defs')

        # Add ArchiMate symbol definitions
        for symbol_def in ARCHIMATE_SYMBOLS.values():
            symbol = ET.SubElement(defs, 'symbol', {
                'id': f'archimate_{symbol_def.element_type}',
                'viewBox': symbol_def.viewBox,
            })
            ET.SubElement(symbol, 'path', {
                'd': symbol_def.svg_path,
                'fill': symbol_def.default_color,
                'stroke': 'black',
                'stroke-width': '1',
            })

        # Arrowhead marker (filled triangle) - for connections
        marker = ET.SubElement(defs, 'marker', {
            'id': 'arrowhead',
            'markerWidth': str(self.ARROWHEAD_SIZE),
            'markerHeight': str(self.ARROWHEAD_SIZE),
            'refX': str(self.ARROWHEAD_SIZE - 2),
            'refY': str(self.ARROWHEAD_SIZE // 2),
            'orient': 'auto',
        })

        # Triangle polygon for arrowhead
        ET.SubElement(marker, 'polygon', {
            'points': f'0 0, {self.ARROWHEAD_SIZE} {self.ARROWHEAD_SIZE // 2}, 0 {self.ARROWHEAD_SIZE}',
            'fill': 'black',
        })

        # Relationship markers
        # Filled arrow (for serving, access, etc.)
        marker_filled = ET.SubElement(defs, 'marker', {
            'id': 'arrow-filled',
            'markerWidth': '8',
            'markerHeight': '8',
            'refX': '6',
            'refY': '4',
            'orient': 'auto',
        })
        ET.SubElement(marker_filled, 'polygon', {
            'points': '0 0, 8 4, 0 8',
            'fill': 'black',
        })

        # Hollow arrow (for realization, etc.)
        marker_hollow = ET.SubElement(defs, 'marker', {
            'id': 'arrow-hollow',
            'markerWidth': '8',
            'markerHeight': '8',
            'refX': '6',
            'refY': '4',
            'orient': 'auto',
        })
        ET.SubElement(marker_hollow, 'polygon', {
            'points': '0 0, 8 4, 0 8',
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': '1',
        })

        # Diamond filled (for composition)
        marker_diamond_filled = ET.SubElement(defs, 'marker', {
            'id': 'diamond-filled',
            'markerWidth': '8',
            'markerHeight': '8',
            'refX': '4',
            'refY': '4',
            'orient': 'auto',
        })
        ET.SubElement(marker_diamond_filled, 'polygon', {
            'points': '4 0, 8 4, 4 8, 0 4',
            'fill': 'black',
        })

        # Diamond hollow (for aggregation)
        marker_diamond_hollow = ET.SubElement(defs, 'marker', {
            'id': 'diamond-hollow',
            'markerWidth': '8',
            'markerHeight': '8',
            'refX': '4',
            'refY': '4',
            'orient': 'auto',
        })
        ET.SubElement(marker_diamond_hollow, 'polygon', {
            'points': '4 0, 8 4, 4 8, 0 4',
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': '1',
        })

    def _add_background(self, svg: ET.Element, width: float, height: float) -> None:
        """Add white background rectangle to SVG canvas.

        Args:
            svg: SVG root element
            width: SVG canvas width
            height: SVG canvas height
        """
        ET.SubElement(svg, 'rect', {
            'x': '0',
            'y': '0',
            'width': str(int(width)),
            'height': str(int(height)),
            'fill': 'white',
            'stroke': 'none',
        })

    def _render_node(self, svg: ET.Element, node: Any) -> None:
        """Render a single node as an ArchiMate symbol with text.

        Args:
            svg: SVG root element
            node: Node to render
        """
        x = float(getattr(node, 'x', 0))
        y = float(getattr(node, 'y', 0))
        w = float(getattr(node, 'w', 120))
        h = float(getattr(node, 'h', 55))
        element_type = getattr(node, 'type', 'BusinessActor')
        element_id = getattr(node, 'uuid', None)

        # Group for node
        g = ET.SubElement(svg, 'g', {'class': 'node'})

        # Get symbol definition
        symbol_def = ARCHIMATE_SYMBOLS.get(element_type)
        if not symbol_def:
            # Fallback to BusinessActor if type not found
            symbol_def = ARCHIMATE_SYMBOLS['BusinessActor']

        # Get color (check for per-element override via fill_color property)
        color = getattr(node, 'fill_color', None) or get_element_color(element_type, element_id)

        # Render symbol via <use> element
        ET.SubElement(g, 'use', {
            'href': f'#archimate_{symbol_def.element_type}',
            'x': str(int(x)),
            'y': str(int(y)),
            'width': str(int(w)),
            'height': str(int(h)),
            'fill': color,
            'stroke': 'black',
            'stroke-width': '1',
        })

        # Text with element name (positioned below/beside symbol)
        element_name = getattr(node, 'name', getattr(node, 'label', ''))
        if element_name:
            self._render_wrapped_text(
                g,
                element_name,
                x + w / 2,  # center x
                y + h + 15,  # below symbol
                w - 2 * self.TEXT_PADDING,  # available width
            )

    def _render_wrapped_text(
        self,
        parent: ET.Element,
        text: str,
        center_x: float,
        center_y: float,
        max_width: float,
    ) -> None:
        """Render text with automatic word wrapping.

        Args:
            parent: Parent SVG element
            text: Text to render
            center_x: X coordinate of center point
            center_y: Y coordinate of center point
            max_width: Maximum width for text
        """
        # Word wrap the text
        lines = self._word_wrap_text(text, max_width)

        # Calculate vertical positioning
        line_height = 12  # pixels
        total_height = len(lines) * line_height
        start_y = center_y - total_height / 2

        # Create text element
        text_elem = ET.SubElement(parent, 'text', {
            'x': str(int(center_x)),
            'y': str(int(start_y + line_height / 2)),
            'text-anchor': 'middle',
            'font-family': 'Arial, sans-serif',
            'font-size': '10',
            'fill': 'black',
        })

        # Add lines as tspan elements
        for i, line in enumerate(lines):
            if i == 0:
                text_elem.text = line
            else:
                tspan = ET.SubElement(text_elem, 'tspan', {
                    'x': str(int(center_x)),
                    'dy': str(line_height),
                })
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
        lines = []
        current_line = []

        for word in words:
            # Check if adding this word would exceed the limit
            test_line = ' '.join(current_line + [word])
            if len(test_line) <= chars_per_line:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

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
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 0.1:
            return

        dx /= dist
        dy /= dist

        if position == 'end':
            # Arrow pointing in direction of line
            dx = -dx
            dy = -dy

        # Create arrow pointing marker (larger size for visibility)
        marker_size = 12
        if marker_type in ('filled', 'hollow'):
            # Triangle arrow: base perpendicular to direction, point along direction
            perp_x = -dy
            perp_y = dx

            # Triangle vertices (pointing along dx, dy direction)
            p1 = (ex + dx * marker_size, ey + dy * marker_size)  # Point
            p2 = (ex - perp_x * marker_size/2 - dx * marker_size/3, ey - perp_y * marker_size/2 - dy * marker_size/3)  # Base corners
            p3 = (ex + perp_x * marker_size/2 - dx * marker_size/3, ey + perp_y * marker_size/2 - dy * marker_size/3)

            points_str = f'{p1[0]},{p1[1]} {p2[0]},{p2[1]} {p3[0]},{p3[1]}'

            fill = color if marker_type == 'filled' else 'none'
            stroke = 'none' if marker_type == 'filled' else color
            stroke_width = '1' if marker_type == 'filled' else '1.5'

            ET.SubElement(svg, 'polygon', {
                'points': points_str,
                'fill': fill,
                'stroke': stroke,
                'stroke-width': stroke_width,
                'stroke-linejoin': 'miter',
            })

        elif marker_type == 'diamond':
            # Diamond marker (larger for visibility)
            size = 8
            p1 = (ex + dx * size, ey + dy * size)
            p2 = (ex - dy * size, ey + dx * size)
            p3 = (ex - dx * size, ey - dy * size)
            p4 = (ex + dy * size, ey - dx * size)

            points_str = f'{p1[0]},{p1[1]} {p2[0]},{p2[1]} {p3[0]},{p3[1]} {p4[0]},{p4[1]}'

            fill = color if marker_type == 'diamond' else 'none'
            stroke = 'none' if marker_type == 'diamond' else color
            stroke_width = '1' if marker_type == 'diamond' else '1.5'

            ET.SubElement(svg, 'polygon', {
                'points': points_str,
                'fill': fill,
                'stroke': stroke,
                'stroke-width': stroke_width,
                'stroke-linejoin': 'miter',
            })

    def _render_relationship(
        self,
        svg: ET.Element,
        conn: Any,
        nodes_dict: dict[str, Any],
        relationship_service: RelationshipStyleService,
    ) -> None:
        """Render a single relationship with ArchiMate styling.

        Args:
            svg: SVG root element
            conn: Connection/relationship to render
            nodes_dict: Dictionary of nodes by uuid
            relationship_service: Service for relationship styles
        """
        source_uuid = getattr(conn, '_source', None)
        target_uuid = getattr(conn, '_target', None)

        if not source_uuid or not target_uuid:
            return

        source_node = nodes_dict.get(source_uuid)
        target_node = nodes_dict.get(target_uuid)

        if not source_node or not target_node:
            return

        # Get bendpoints
        bendpoints = getattr(conn, 'bendpoints', [])

        # Build polyline points
        points = self._get_clipped_polyline_points(
            source_node,
            target_node,
            bendpoints,
        )

        if len(points) < 2:
            return

        # Get relationship type and style
        rel_type = getattr(conn, 'type', 'Association')
        relationship_style = relationship_service.get_style(rel_type)

        # If no style found, try without "Relationship" suffix
        if not relationship_style and 'Relationship' in rel_type:
            relationship_style = relationship_service.get_style(rel_type.replace('Relationship', ''))

        # Fall back to basic connection rendering if no style found
        if not relationship_style:
            self._render_connection(svg, conn, nodes_dict)
            return

        # Apply per-relationship overrides if available
        stroke_color = getattr(conn, 'stroke_color', None) or relationship_style.stroke_color
        stroke_width = getattr(conn, 'stroke_width', None) or relationship_style.stroke_width
        stroke_dasharray = getattr(conn, 'stroke_style', None) or relationship_style.stroke_dasharray

        # Render polyline with relationship style
        points_str = ' '.join(f'{int(p[0])},{int(p[1])}' for p in points)
        polyline_attrs = {
            'points': points_str,
            'fill': 'none',
            'stroke': stroke_color,
            'stroke-width': str(stroke_width),
            'opacity': '0.8',
        }

        # Add dash pattern if specified
        if stroke_dasharray:
            polyline_attrs['stroke-dasharray'] = stroke_dasharray

        # Add markers if specified
        if relationship_style.marker_start:
            polyline_attrs['marker-start'] = relationship_style.marker_start
        if relationship_style.marker_end:
            polyline_attrs['marker-end'] = relationship_style.marker_end

        ET.SubElement(svg, 'polyline', polyline_attrs)

        # Render custom arrow/diamond markers as explicit path elements
        if len(points) >= 2:
            # End marker
            if relationship_style.marker_end:
                self._render_marker_shape(
                    svg,
                    points[-1],
                    points[-2],
                    relationship_style.arrow_type,
                    stroke_color,
                    'end',
                )
            # Start marker
            if relationship_style.marker_start:
                self._render_marker_shape(
                    svg,
                    points[0],
                    points[1],
                    relationship_style.arrow_type,
                    stroke_color,
                    'start',
                )

        # Render relationship label
        label_text = self._get_short_type_name(rel_type)
        if label_text and len(points) >= 2:
            self._render_connection_label(svg, points, label_text)

    def _render_connection(
        self,
        svg: ET.Element,
        conn: Any,
        nodes_dict: dict[str, Any],
    ) -> None:
        """Render a single connection as a polyline with optional label.

        Args:
            svg: SVG root element
            conn: Connection to render
            nodes_dict: Dictionary of nodes by uuid
        """
        source_uuid = getattr(conn, '_source', None)
        target_uuid = getattr(conn, '_target', None)

        if not source_uuid or not target_uuid:
            return

        source_node = nodes_dict.get(source_uuid)
        target_node = nodes_dict.get(target_uuid)

        if not source_node or not target_node:
            return

        # Get bendpoints
        bendpoints = getattr(conn, 'bendpoints', [])

        # Build polyline points
        points = self._get_clipped_polyline_points(
            source_node,
            target_node,
            bendpoints,
        )

        if len(points) < 2:
            return

        # Render polyline
        points_str = ' '.join(f'{int(p[0])},{int(p[1])}' for p in points)
        ET.SubElement(svg, 'polyline', {
            'points': points_str,
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': '1',
            'marker-end': 'url(#arrowhead)',
        })

        # Render connection label
        rel_type = getattr(conn, 'type', 'Relationship')
        label_text = self._get_short_type_name(rel_type)

        if label_text and len(points) >= 2:
            self._render_connection_label(svg, points, label_text)

    def _get_clipped_polyline_points(
        self,
        source_node: Any,
        target_node: Any,
        bendpoints: list[Any],
    ) -> list[Tuple[float, float]]:
        """Get polyline points clipped at node boundary edges.

        Args:
            source_node: Source node
            target_node: Target node
            bendpoints: List of intermediate bendpoints (if any)

        Returns:
            List of (x, y) tuples representing polyline points
        """
        # Get source and target centers
        sx = float(getattr(source_node, 'x', 0)) + float(getattr(source_node, 'w', 120)) / 2
        sy = float(getattr(source_node, 'y', 0)) + float(getattr(source_node, 'h', 55)) / 2
        tx = float(getattr(target_node, 'x', 0)) + float(getattr(target_node, 'w', 120)) / 2
        ty = float(getattr(target_node, 'y', 0)) + float(getattr(target_node, 'h', 55)) / 2

        # Get node bounds
        source_bounds = self._get_node_bounds(source_node)
        target_bounds = self._get_node_bounds(target_node)

        # Build full polyline (source center → bendpoints → target center)
        full_points = [(sx, sy)]

        # Add bendpoints
        for bp in bendpoints:
            bx = float(getattr(bp, 'x', 0))
            by = float(getattr(bp, 'y', 0))
            full_points.append((bx, by))

        full_points.append((tx, ty))

        # Clip first segment at source boundary
        if len(full_points) >= 2:
            start_point = self._clip_line_at_rectangle(
                full_points[0],
                full_points[1],
                source_bounds,
                exit_from=True,
            )
            full_points[0] = start_point

        # Clip last segment at target boundary
        if len(full_points) >= 2:
            end_point = self._clip_line_at_rectangle(
                full_points[-2],
                full_points[-1],
                target_bounds,
                exit_from=False,
            )

            # Extend endpoint by ~8 pixels in the direction away from the previous point
            # This ensures SVG markers (arrows, diamonds) are fully visible outside the symbol
            prev_point = full_points[-2]
            dx = end_point[0] - prev_point[0]
            dy = end_point[1] - prev_point[1]
            dist = (dx*dx + dy*dy) ** 0.5

            if dist > 0:
                # Extend by 8 pixels to ensure markers are fully visible
                extension = 8.0
                end_point = (
                    end_point[0] + (dx / dist) * extension,
                    end_point[1] + (dy / dist) * extension
                )

            full_points[-1] = end_point

        # Extend start point similarly for marker_start visibility
        if len(full_points) >= 2:
            start_point = full_points[0]
            next_point = full_points[1]
            dx = next_point[0] - start_point[0]
            dy = next_point[1] - start_point[1]
            dist = (dx*dx + dy*dy) ** 0.5

            if dist > 0:
                # Extend backward by 8 pixels to ensure start markers are visible
                extension = 8.0
                start_point = (
                    start_point[0] - (dx / dist) * extension,
                    start_point[1] - (dy / dist) * extension
                )
                full_points[0] = start_point

        return full_points

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
        x = float(getattr(node, 'x', 0))
        y = float(getattr(node, 'y', 0))
        w = float(getattr(node, 'w', 120))
        h = float(getattr(node, 'h', 55))
        element_type = getattr(node, 'type', 'BusinessActor')

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

    def _clip_line_at_rectangle(
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
                    if best_t is None or (exit_from and t > best_t) or (not exit_from and t < best_t):
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
        g = ET.SubElement(svg, 'g', {'class': 'connection-label'})

        # Background rectangle
        text_width = len(label_text) * 6  # estimate
        text_height = 12
        bg_x = mid_x - text_width / 2
        bg_y = mid_y - text_height / 2

        ET.SubElement(g, 'rect', {
            'x': str(int(bg_x)),
            'y': str(int(bg_y)),
            'width': str(int(text_width)),
            'height': str(int(text_height)),
            'fill': 'white',
            'stroke': 'none',
        })

        # Label text
        text_elem = ET.SubElement(g, 'text', {
            'x': str(int(mid_x)),
            'y': str(int(mid_y + text_height / 3)),
            'text-anchor': 'middle',
            'font-family': 'Arial, sans-serif',
            'font-size': '9',
            'fill': 'black',
        })
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

        max_length = 0
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
        if rel_type.endswith('Relationship'):
            return rel_type[:-len('Relationship')]
        return rel_type
