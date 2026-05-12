"""Core layout classes: LayoutConfig, RoutingConfig, LayoutResult, and base algorithm interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LayoutConfig:
    """Configuration for auto_layout operations.

    - algorithm: Layout algorithm to use (force_directed or hierarchical)
    - spacing: Minimum space between nodes (pixels)
    - margin: Margin around canvas edges (pixels)
    - alignment: "free" (no snapping) or "grid" (snap to grid)
    - excluded_element_ids: List of element IDs to exclude from repositioning
    - node_size_constraints: Dict with min/max constraints for node sizing
    - routing_style: "orthogonal" (0°/90°) or "mixed_45" (allow ±45° angles)
    - layer_priority: "mandatory" (enforce layer constraints) or "soft"
    - grid_size: Grid cell size in pixels for coarse-grid snapping (default 240 = node width + gap)
    - layer_direction: "vertical" (Business top) or "horizontal" (Business left)
    - high_degree_threshold: Nodes with connection degree >= this value get isolated to their own
      sub-row (padded 1 cell on each side) to reduce routing bottlenecks (default 5)
    """

    algorithm: str = "force_directed"
    spacing: float = 50.0
    margin: float = 20.0
    alignment: str = "grid"
    excluded_element_ids: list[int] = field(default_factory=list)
    node_size_constraints: dict[str, Any] = field(default_factory=dict)
    routing_style: str = "orthogonal"
    layer_priority: str = "mandatory"
    grid_size: float = 240.0
    layer_direction: str = "vertical"
    high_degree_threshold: int = 5

    def _validate_spacing_and_margin(self) -> None:
        if self.spacing <= 0:
            raise ValueError("spacing must be positive (>0)")
        if self.spacing > 500:
            raise ValueError("spacing should not exceed 500 pixels")
        if self.margin < 0:
            raise ValueError("margin must be non-negative (>=0)")
        if self.margin > 500:
            raise ValueError("margin should not exceed 500 pixels")

    def _validate_alignment_and_grid(self) -> None:
        if self.alignment not in ("free", "grid"):
            raise ValueError(f"Invalid alignment: {self.alignment} (must be 'free' or 'grid')")
        if self.alignment == "grid" and self.grid_size <= 0:
            raise ValueError("grid_size must be positive when alignment='grid'")

    def _validate_node_size_constraints(self) -> None:
        if not self.node_size_constraints:
            return
        allowed_keys = {"min_width", "max_width", "min_height", "max_height"}
        invalid_keys = set(self.node_size_constraints.keys()) - allowed_keys
        if invalid_keys:
            raise ValueError(f"Invalid node_size_constraints keys: {invalid_keys}")
        min_w = self.node_size_constraints.get("min_width", 0)
        max_w = self.node_size_constraints.get("max_width", float('inf'))
        min_h = self.node_size_constraints.get("min_height", 0)
        max_h = self.node_size_constraints.get("max_height", float('inf'))
        if min_w < 0 or max_w < 0 or min_h < 0 or max_h < 0:
            raise ValueError("node_size_constraints values must be non-negative")
        if min_w > max_w or min_h > max_h:
            raise ValueError("node_size_constraints min cannot exceed max")

    def __post_init__(self) -> None:
        if self.algorithm not in ("force_directed", "hierarchical"):
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        self._validate_spacing_and_margin()
        self._validate_alignment_and_grid()
        if self.routing_style not in ("orthogonal", "mixed_45"):
            raise ValueError(f"Invalid routing_style: {self.routing_style} (must be 'orthogonal' or 'mixed_45')")
        if self.layer_priority not in ("mandatory", "soft"):
            raise ValueError(f"Invalid layer_priority: {self.layer_priority} (must be 'mandatory' or 'soft')")
        if self.layer_direction not in ("vertical", "horizontal"):
            raise ValueError(f"Invalid layer_direction: {self.layer_direction} (must be 'vertical' or 'horizontal')")
        self._validate_node_size_constraints()
        if not isinstance(self.excluded_element_ids, list):
            raise ValueError("excluded_element_ids must be a list")


@dataclass
class RoutingConfig:
    """Configuration for auto_route operations.

    - min_segment_gap: Minimum separation between collinear segments of different connections (px)
    - corner_clearance_pct: Fraction of edge length reserved at each corner (0 < pct <= 0.50)
    - corner_clearance_min: Absolute floor for corner clearance in px
    - crossing_penalty: Cost weight applied in BFS when crossing an already-routed segment
    """

    min_segment_gap: float = 10.0
    corner_clearance_pct: float = 0.10
    corner_clearance_min: float = 4.0
    crossing_penalty: float = 3.0

    def __post_init__(self) -> None:
        if self.min_segment_gap < 0:
            raise ValueError("min_segment_gap must be >= 0")
        if not (0 < self.corner_clearance_pct <= 0.50):
            raise ValueError("corner_clearance_pct must be in range (0, 0.50]")
        if self.corner_clearance_min < 0:
            raise ValueError("corner_clearance_min must be >= 0")
        if self.crossing_penalty < 0:
            raise ValueError("crossing_penalty must be >= 0")


@dataclass
class LayoutResult:
    """Result of a layout or routing operation."""

    success: bool
    view_id: str
    algorithm_used: str
    elements_processed: int
    connections_processed: int
    layout_time_ms: float
    quality_metrics: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)


class LayoutAlgorithm(ABC):
    """Base class for layout algorithms."""

    @abstractmethod
    def apply(self, view: Any, config: LayoutConfig) -> LayoutResult:
        """Apply layout algorithm to a view."""
        pass
