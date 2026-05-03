"""Core layout classes: LayoutConfig, LayoutResult, and base algorithm interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LayoutConfig:
    """Configuration for layout operations."""

    algorithm: str = "force_directed"
    spacing: float = 50.0
    margin: float = 20.0
    alignment: str = "free"
    excluded_element_ids: list = field(default_factory=list)
    node_size_constraints: dict = field(default_factory=dict)
    routing_style: str = "orthogonal"
    layer_priority: str = "mandatory"

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.spacing <= 0:
            raise ValueError("spacing must be positive")
        if self.margin < 0:
            raise ValueError("margin must be non-negative")
        if self.algorithm not in ("force_directed", "hierarchical"):
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        if self.alignment not in ("free", "grid"):
            raise ValueError(f"Invalid alignment: {self.alignment}")
        if self.routing_style not in ("orthogonal", "mixed_45"):
            raise ValueError(f"Invalid routing_style: {self.routing_style}")


@dataclass
class LayoutResult:
    """Result of a layout operation."""

    success: bool
    view_id: str
    algorithm_used: str
    elements_processed: int
    connections_processed: int
    layout_time_ms: float
    quality_metrics: dict = field(default_factory=dict)
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
