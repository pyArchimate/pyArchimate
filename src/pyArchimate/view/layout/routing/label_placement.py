"""Label placement for connections without overlaps."""

from typing import List, Tuple

from ..utils.geometry import Point, Rectangle


def position_label_on_connection(
    connection_points: List[Point],
    _label_text: str,
    _label_width: float = 50,
    label_height: float = 20,
) -> Point:
    """Position a label near a connection with offset.

    Args:
        connection_points: Waypoints of the connection path
        label_text: Label text
        label_width: Estimated label width
        label_height: Estimated label height

    Returns:
        Position for the label
    """
    if not connection_points or len(connection_points) < 2:
        return Point(0, 0)

    # Find midpoint of the connection
    mid_idx = len(connection_points) // 2
    mid_point = connection_points[mid_idx]

    # Get direction vector of nearby segment
    p1 = connection_points[mid_idx - 1]
    p2 = connection_points[mid_idx]

    # Calculate perpendicular offset direction
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    # Perpendicular vector (rotate 90 degrees)
    if abs(dx) > 0.1 or abs(dy) > 0.1:
        length = (dx**2 + dy**2) ** 0.5
        perp_x = -dy / length
        perp_y = dx / length
    else:
        perp_x = 0
        perp_y = 1

    # Offset label position perpendicular to connection
    offset = label_height + 5  # Offset by label height plus margin
    label_x = mid_point.x + perp_x * offset
    label_y = mid_point.y + perp_y * offset

    return Point(label_x, label_y)


def detect_label_collision(
    label_bounds: Rectangle,
    connection_lines: List[Tuple[Point, Point]],
    other_labels: List[Rectangle],
) -> bool:
    """Detect if a label collides with connections or other labels.

    Args:
        label_bounds: Rectangle representing label bounds
        connection_lines: List of connection line segments
        other_labels: List of other label rectangles

    Returns:
        True if collision detected, False otherwise
    """
    # Check collision with connection lines
    for p_start, p_end in connection_lines:
        # Check if line passes through label bounds
        # Simple bounding box check
        if (
            min(p_start.x, p_end.x) <= label_bounds.x + label_bounds.width
            and max(p_start.x, p_end.x) >= label_bounds.x
            and min(p_start.y, p_end.y) <= label_bounds.y + label_bounds.height
            and max(p_start.y, p_end.y) >= label_bounds.y
        ):
            return True

    # Check collision with other labels
    for other_label in other_labels:
        if label_bounds.intersects(other_label):
            return True

    return False


def avoid_label_collision(
    original_position: Point,
    label_width: float,
    label_height: float,
    connection_lines: List[Tuple[Point, Point]],
    placed_labels: List[Rectangle],
    max_offsets: int = 8,
) -> Point:
    """Find a collision-free position for a label by trying different offsets.

    Args:
        original_position: Original label position
        label_width: Label width
        label_height: Label height
        connection_lines: Connection lines to avoid
        placed_labels: Already-placed labels
        max_offsets: Number of different offset positions to try

    Returns:
        Safe position for label, or original position if no safe position found
    """
    label_rect = Rectangle(
        original_position.x - label_width / 2,
        original_position.y - label_height / 2,
        label_width,
        label_height,
    )

    # Check original position
    if not detect_label_collision(label_rect, connection_lines, placed_labels):
        return original_position

    # Try different offsets around original position
    for i in range(1, max_offsets):
        angle = (i / max_offsets) * 360
        distance = label_height * (1 + i * 0.5)

        import math
        rad = math.radians(angle)
        new_x = original_position.x + distance * math.cos(rad)
        new_y = original_position.y + distance * math.sin(rad)
        new_pos = Point(new_x, new_y)

        new_rect = Rectangle(
            new_pos.x - label_width / 2,
            new_pos.y - label_height / 2,
            label_width,
            label_height,
        )

        if not detect_label_collision(new_rect, connection_lines, placed_labels):
            return new_pos

    # No collision-free position found, return original
    return original_position


def truncate_label(text: str, max_length: int = 20) -> str:
    """Truncate label text if too long.

    Args:
        text: Label text
        max_length: Maximum length before truncation

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


class LabelPlacement:
    """Manages label placement for connections."""

    def __init__(self) -> None:
        """Initialize label placement system."""
        self.placed_labels: List[Rectangle] = []

    def place_label(
        self,
        label_text: str,
        connection_points: List[Point],
        connection_lines: List[Tuple[Point, Point]],
        label_width: float = 50,
        label_height: float = 20,
    ) -> Tuple[Point, str]:
        """Place a label on a connection, avoiding collisions.

        Args:
            label_text: Label text
            connection_points: Connection waypoints
            connection_lines: Connection line segments
            label_width: Label width
            label_height: Label height

        Returns:
            Tuple of (label_position, label_text)
        """
        # Get initial position
        position = position_label_on_connection(
            connection_points,
            label_text,
            label_width,
            label_height,
        )

        # Avoid collisions
        safe_position = avoid_label_collision(
            position,
            label_width,
            label_height,
            connection_lines,
            self.placed_labels,
        )

        # Truncate if needed
        truncated_text = truncate_label(label_text)

        # Record placed label
        label_rect = Rectangle(
            safe_position.x - label_width / 2,
            safe_position.y - label_height / 2,
            label_width,
            label_height,
        )
        self.placed_labels.append(label_rect)

        return safe_position, truncated_text

    def reset(self) -> None:
        """Reset placed labels."""
        self.placed_labels = []
