"""Geometry utilities for layout operations."""

import math
from dataclasses import dataclass


@dataclass
class Point:
    """A point in 2D space."""

    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        """Calculate Euclidean distance to another point."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __add__(self, other: "Point") -> "Point":
        """Add two points."""
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        """Subtract two points."""
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Point":
        """Multiply point by scalar."""
        return Point(self.x * scalar, self.y * scalar)


@dataclass
class Rectangle:
    """An axis-aligned rectangle."""

    x: float
    y: float
    width: float
    height: float

    @property
    def center(self) -> Point:
        """Get rectangle center."""
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def top_left(self) -> Point:
        """Get top-left corner."""
        return Point(self.x, self.y)

    @property
    def top_right(self) -> Point:
        """Get top-right corner."""
        return Point(self.x + self.width, self.y)

    @property
    def bottom_left(self) -> Point:
        """Get bottom-left corner."""
        return Point(self.x, self.y + self.height)

    @property
    def bottom_right(self) -> Point:
        """Get bottom-right corner."""
        return Point(self.x + self.width, self.y + self.height)

    def contains_point(self, point: Point) -> bool:
        """Check if rectangle contains a point."""
        return (
            self.x <= point.x <= self.x + self.width
            and self.y <= point.y <= self.y + self.height
        )

    def intersects(self, other: "Rectangle") -> bool:
        """Check if this rectangle intersects with another."""
        return not (
            self.x + self.width < other.x
            or other.x + other.width < self.x
            or self.y + self.height < other.y
            or other.y + other.height < self.y
        )

    def distance_to_point(self, point: Point) -> float:
        """Calculate minimum distance from rectangle to a point."""
        if self.contains_point(point):
            return 0.0

        closest_x = max(self.x, min(point.x, self.x + self.width))
        closest_y = max(self.y, min(point.y, self.y + self.height))
        closest_point = Point(closest_x, closest_y)

        return point.distance_to(closest_point)


def distance(p1: Point, p2: Point) -> float:
    """Calculate Euclidean distance between two points."""
    return p1.distance_to(p2)


def midpoint(p1: Point, p2: Point) -> Point:
    """Calculate midpoint between two points."""
    return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)


def compute_corner_clearance(edge_length: float, pct: float = 0.10, min_px: float = 4.0) -> float:
    """Return corner clearance = max(edge_length * pct, min_px)."""
    return max(edge_length * pct, min_px)


def bounding_box(points: list[Point]) -> Rectangle:
    """Calculate bounding box for a list of points."""
    if not points:
        return Rectangle(0, 0, 0, 0)

    min_x = min(p.x for p in points)
    max_x = max(p.x for p in points)
    min_y = min(p.y for p in points)
    max_y = max(p.y for p in points)

    return Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)
