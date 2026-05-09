"""Core layout classes: LayoutConfig, LayoutResult, and base algorithm interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LayoutConfig:
    """Configuration for layout operations.

    Advanced configuration options for customizing layout behavior:
    - algorithm: Layout algorithm to use (force_directed or hierarchical)
    - spacing: Minimum space between elements (pixels)
    - margin: Margin around canvas edges (pixels)
    - alignment: "free" (no snapping) or "grid" (snap to grid)
    - excluded_element_ids: List of element IDs to exclude from repositioning
    - node_size_constraints: Dict with min/max constraints: {"min_width": float, "max_width": float, "min_height": float, "max_height": float}
    - routing_style: "orthogonal" (0°/90°) or "mixed_45" (allow ±45° angles)
    - layer_priority: "mandatory" (enforce layer constraints) or "soft" (prefer but allow violations)
    - grid_size: Grid spacing for alignment mode (pixels)
    """

    algorithm: str = "force_directed"
    spacing: float = 50.0
    margin: float = 20.0
    alignment: str = "free"
    excluded_element_ids: list[int] = field(default_factory=list)
    node_size_constraints: dict[str, Any] = field(default_factory=dict)
    routing_style: str = "orthogonal"
    layer_priority: str = "mandatory"
    grid_size: float = 10.0

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
        if self.alignment == "grid":
            if self.grid_size <= 0:
                raise ValueError("grid_size must be positive when alignment='grid'")
            if self.grid_size > 100:
                raise ValueError("grid_size should not exceed 100 pixels")

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
        """Validate configuration parameters."""
        if self.algorithm not in ("force_directed", "hierarchical"):
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        self._validate_spacing_and_margin()
        self._validate_alignment_and_grid()
        if self.routing_style not in ("orthogonal", "mixed_45"):
            raise ValueError(f"Invalid routing_style: {self.routing_style} (must be 'orthogonal' or 'mixed_45')")
        if self.layer_priority not in ("mandatory", "soft"):
            raise ValueError(f"Invalid layer_priority: {self.layer_priority} (must be 'mandatory' or 'soft')")
        self._validate_node_size_constraints()
        if not isinstance(self.excluded_element_ids, list):
            raise ValueError("excluded_element_ids must be a list")


@dataclass
class LayoutResult:
    """Result of a layout operation."""

    success: bool
    view_id: str
    algorithm_used: str
    elements_processed: int
    connections_processed: int
    layout_time_ms: float
    quality_metrics: dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class LayoutAlgorithm(ABC):
    """Base class for layout algorithms."""

    @abstractmethod
    def apply(self, view: Any, config: LayoutConfig) -> LayoutResult:
        """Apply layout algorithm to a view.

        Args:
            view: View object to layout
            config: Layout configuration

        Returns:
            LayoutResult with layout metrics
        """
        pass
