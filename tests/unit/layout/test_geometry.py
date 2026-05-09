"""Tests for geometry utilities."""

from src.pyArchimate.view.layout.utils.geometry import Point, Rectangle, bounding_box, distance, midpoint


class TestPoint:
    """Tests for Point class."""

    def test_point_creation(self) -> None:
        """Test Point creation."""
        p = Point(3.0, 4.0)
        assert p.x == 3.0
        assert p.y == 4.0

    def test_distance_to(self) -> None:
        """Test distance calculation between points."""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        assert p1.distance_to(p2) == 5.0

    def test_distance_function(self) -> None:
        """Test module distance function."""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        assert distance(p1, p2) == 5.0

    def test_point_addition(self) -> None:
        """Test point addition."""
        p1 = Point(1, 2)
        p2 = Point(3, 4)
        result = p1 + p2
        assert result.x == 4
        assert result.y == 6

    def test_point_subtraction(self) -> None:
        """Test point subtraction."""
        p1 = Point(5, 7)
        p2 = Point(2, 3)
        result = p1 - p2
        assert result.x == 3
        assert result.y == 4

    def test_point_scalar_multiplication(self) -> None:
        """Test point scalar multiplication."""
        p = Point(2, 3)
        result = p * 2
        assert result.x == 4
        assert result.y == 6


class TestRectangle:
    """Tests for Rectangle class."""

    def test_rectangle_creation(self) -> None:
        """Test Rectangle creation."""
        r = Rectangle(10, 20, 30, 40)
        assert r.x == 10
        assert r.y == 20
        assert r.width == 30
        assert r.height == 40

    def test_rectangle_center(self) -> None:
        """Test rectangle center calculation."""
        r = Rectangle(0, 0, 10, 10)
        center = r.center
        assert center.x == 5
        assert center.y == 5

    def test_rectangle_corners(self) -> None:
        """Test rectangle corner points."""
        r = Rectangle(10, 20, 30, 40)
        assert r.top_left.x == 10
        assert r.top_left.y == 20
        assert r.top_right.x == 40
        assert r.top_right.y == 20
        assert r.bottom_left.x == 10
        assert r.bottom_left.y == 60
        assert r.bottom_right.x == 40
        assert r.bottom_right.y == 60

    def test_contains_point_inside(self) -> None:
        """Test point containment for point inside rectangle."""
        r = Rectangle(0, 0, 10, 10)
        assert r.contains_point(Point(5, 5)) is True

    def test_contains_point_outside(self) -> None:
        """Test point containment for point outside rectangle."""
        r = Rectangle(0, 0, 10, 10)
        assert r.contains_point(Point(15, 15)) is False

    def test_contains_point_boundary(self) -> None:
        """Test point containment on boundary."""
        r = Rectangle(0, 0, 10, 10)
        assert r.contains_point(Point(0, 0)) is True
        assert r.contains_point(Point(10, 10)) is True

    def test_intersects_true(self) -> None:
        """Test rectangle intersection detection (intersecting)."""
        r1 = Rectangle(0, 0, 10, 10)
        r2 = Rectangle(5, 5, 10, 10)
        assert r1.intersects(r2) is True

    def test_intersects_false(self) -> None:
        """Test rectangle intersection detection (non-intersecting)."""
        r1 = Rectangle(0, 0, 10, 10)
        r2 = Rectangle(20, 20, 10, 10)
        assert r1.intersects(r2) is False

    def test_distance_to_point_inside(self) -> None:
        """Test distance from rectangle to interior point."""
        r = Rectangle(0, 0, 10, 10)
        assert r.distance_to_point(Point(5, 5)) == 0.0

    def test_distance_to_point_outside(self) -> None:
        """Test distance from rectangle to exterior point."""
        r = Rectangle(0, 0, 10, 10)
        # Point at (15, 5) is 5 units to the right
        assert r.distance_to_point(Point(15, 5)) == 5.0


def test_midpoint() -> None:
    """Test midpoint calculation."""
    p1 = Point(0, 0)
    p2 = Point(10, 10)
    mid = midpoint(p1, p2)
    assert mid.x == 5
    assert mid.y == 5


def test_bounding_box_single_point() -> None:
    """Test bounding box for single point."""
    points = [Point(5, 5)]
    bbox = bounding_box(points)
    assert bbox.x == 5
    assert bbox.y == 5
    assert bbox.width == 0
    assert bbox.height == 0


def test_bounding_box_multiple_points() -> None:
    """Test bounding box for multiple points."""
    points = [Point(0, 0), Point(10, 10), Point(5, 5)]
    bbox = bounding_box(points)
    assert bbox.x == 0
    assert bbox.y == 0
    assert bbox.width == 10
    assert bbox.height == 10


def test_bounding_box_empty() -> None:
    """Test bounding box for empty list."""
    bbox = bounding_box([])
    assert bbox.x == 0
    assert bbox.y == 0
    assert bbox.width == 0
    assert bbox.height == 0
