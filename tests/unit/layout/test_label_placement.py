"""Tests for label placement utilities."""

from src.pyArchimate.view.layout.routing.label_placement import (
    LabelPlacement,
    avoid_label_collision,
    detect_label_collision,
    position_label_on_connection,
    truncate_label,
)
from src.pyArchimate.view.layout.utils.geometry import Point, Rectangle


def test_position_label_on_connection_simple() -> None:
    """Test basic label positioning on connection."""
    connection_points = [Point(0, 0), Point(50, 50), Point(100, 100)]
    label_text = "Test"

    position = position_label_on_connection(connection_points, label_text)

    assert isinstance(position, Point)
    # Position should be near the middle of the connection
    assert position.x >= 0
    assert position.y >= 0


def test_position_label_on_connection_straight_line() -> None:
    """Test label positioning on straight connection."""
    connection_points = [Point(0, 0), Point(100, 100)]
    label_text = "Label"

    position = position_label_on_connection(connection_points, label_text)

    assert isinstance(position, Point)


def test_detect_label_collision_no_collision() -> None:
    """Test collision detection with no collision."""
    label_bounds = Rectangle(0, 0, 50, 20)
    connection_lines = [(Point(100, 100), Point(150, 150))]
    other_labels = []

    assert detect_label_collision(label_bounds, connection_lines, other_labels) is False


def test_detect_label_collision_with_connection() -> None:
    """Test collision detection with connection line."""
    label_bounds = Rectangle(25, 25, 50, 50)
    connection_lines = [(Point(0, 0), Point(100, 100))]
    other_labels = []

    assert detect_label_collision(label_bounds, connection_lines, other_labels) is True


def test_detect_label_collision_with_other_label() -> None:
    """Test collision detection with other labels."""
    label_bounds = Rectangle(0, 0, 50, 50)
    connection_lines = []
    other_labels = [Rectangle(25, 25, 50, 50)]

    assert detect_label_collision(label_bounds, connection_lines, other_labels) is True


def test_avoid_label_collision_safe_position() -> None:
    """Test collision avoidance when original position is safe."""
    original_pos = Point(0, 0)
    connection_lines: list = []
    placed_labels: list = []

    result = avoid_label_collision(original_pos, 50, 20, connection_lines, placed_labels)

    assert result == original_pos


def test_avoid_label_collision_unsafe() -> None:
    """Test collision avoidance with unsafe original position."""
    original_pos = Point(50, 50)
    connection_lines = [(Point(0, 0), Point(100, 100))]
    placed_labels: list = []

    result = avoid_label_collision(
        original_pos, 50, 20, connection_lines, placed_labels, max_offsets=4
    )

    # Result should be different from original (avoidance applied)
    # or the same if all positions collide
    assert isinstance(result, Point)


def test_truncate_label_short() -> None:
    """Test label truncation for short text."""
    text = "Short"
    truncated = truncate_label(text, max_length=20)
    assert truncated == "Short"


def test_truncate_label_long() -> None:
    """Test label truncation for long text."""
    text = "This is a very long label text that needs truncation"
    truncated = truncate_label(text, max_length=20)

    assert len(truncated) <= 20
    assert truncated.endswith("...")


def test_label_placement_manager() -> None:
    """Test LabelPlacement manager."""
    placement = LabelPlacement()
    assert len(placement.placed_labels) == 0

    connection_points = [Point(0, 0), Point(50, 50)]
    connection_lines: list = []

    pos, text = placement.place_label("Test", connection_points, connection_lines)

    assert isinstance(pos, Point)
    assert isinstance(text, str)
    assert len(placement.placed_labels) == 1


def test_label_placement_reset() -> None:
    """Test LabelPlacement reset."""
    placement = LabelPlacement()

    connection_points = [Point(0, 0), Point(50, 50)]
    connection_lines: list = []
    placement.place_label("Label1", connection_points, connection_lines)

    assert len(placement.placed_labels) == 1

    placement.reset()
    assert len(placement.placed_labels) == 0


def test_label_placement_multiple() -> None:
    """Test placing multiple labels."""
    placement = LabelPlacement()
    connection_points = [Point(0, 0), Point(50, 50)]
    connection_lines: list = []

    placement.place_label("Label1", connection_points, connection_lines)
    placement.place_label("Label2", connection_points, connection_lines)

    assert len(placement.placed_labels) == 2
