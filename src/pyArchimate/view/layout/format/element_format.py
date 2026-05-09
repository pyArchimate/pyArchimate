"""Element formatting service for standardizing view appearance.

This module provides formatting and standardization functionality for ArchiMate elements,
including size standardization, font consistency, and grid alignment.
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Set, Tuple


class ArchiMateElementCategory(Enum):
    """ArchiMate element categories for standardized sizing."""

    BUSINESS_ACTOR = "business_actor"
    BUSINESS_ROLE = "business_role"
    BUSINESS_COLLABORATION = "business_collaboration"
    BUSINESS_INTERFACE = "business_interface"
    BUSINESS_PROCESS = "business_process"
    BUSINESS_FUNCTION = "business_function"
    BUSINESS_INTERACTION = "business_interaction"
    BUSINESS_EVENT = "business_event"
    BUSINESS_OBJECT = "business_object"
    BUSINESS_SERVICE = "business_service"
    BUSINESS_CONTRACT = "business_contract"

    APPLICATION_COMPONENT = "application_component"
    APPLICATION_COLLABORATION = "application_collaboration"
    APPLICATION_INTERFACE = "application_interface"
    APPLICATION_FUNCTION = "application_function"
    APPLICATION_INTERACTION = "application_interaction"
    APPLICATION_SERVICE = "application_service"
    DATA_OBJECT = "data_object"

    TECHNOLOGY_NODE = "technology_node"
    TECHNOLOGY_DEVICE = "technology_device"
    TECHNOLOGY_ARTIFACT = "technology_artifact"
    TECHNOLOGY_INFRASTRUCTURE = "technology_infrastructure"
    TECHNOLOGY_INTERFACE = "technology_interface"
    TECHNOLOGY_SERVICE = "technology_service"
    TECHNOLOGY_COLLABORATION = "technology_collaboration"

    STRATEGY_ELEMENT = "strategy_element"
    PHYSICAL_ELEMENT = "physical_element"
    IMPLEMENTATION_ELEMENT = "implementation_element"
    MOTIVATION_ELEMENT = "motivation_element"

    UNKNOWN = "unknown"


@dataclass
class ElementFormatSpec:
    """Standardized format specification for an element type."""

    category: ArchiMateElementCategory
    default_width: float
    default_height: float
    font_family: str
    font_size: int
    font_style: str  # "normal", "italic"
    font_weight: str  # "normal", "bold"


class ElementFormatRegistry:
    """Registry of standard element format specifications."""

    def __init__(self) -> None:
        """Initialize format registry with ArchiMate element standards."""
        self._specs: Dict[str, ElementFormatSpec] = {}
        self._type_to_category: Dict[str, ArchiMateElementCategory] = {}
        self._initialize_standards()

    # Archi default element size — all element types use the same dimensions
    ARCHI_DEFAULT_WIDTH: int = 120
    ARCHI_DEFAULT_HEIGHT: int = 55

    def _initialize_standards(self) -> None:
        """Initialize standard format specifications for all element types."""
        w, h = self.ARCHI_DEFAULT_WIDTH, self.ARCHI_DEFAULT_HEIGHT

        type_map: dict[ArchiMateElementCategory, list[str]] = {
            ArchiMateElementCategory.BUSINESS_ACTOR: ["BusinessActor"],
            ArchiMateElementCategory.BUSINESS_ROLE: ["BusinessRole"],
            ArchiMateElementCategory.BUSINESS_PROCESS: ["BusinessProcess"],
            ArchiMateElementCategory.BUSINESS_FUNCTION: ["BusinessFunction"],
            ArchiMateElementCategory.BUSINESS_SERVICE: ["BusinessService"],
            ArchiMateElementCategory.BUSINESS_OBJECT: ["BusinessObject"],
            ArchiMateElementCategory.BUSINESS_EVENT: ["BusinessEvent"],
            ArchiMateElementCategory.BUSINESS_INTERFACE: ["BusinessInterface"],
            ArchiMateElementCategory.APPLICATION_COMPONENT: ["ApplicationComponent"],
            ArchiMateElementCategory.APPLICATION_SERVICE: ["ApplicationService"],
            ArchiMateElementCategory.APPLICATION_INTERFACE: ["ApplicationInterface"],
            ArchiMateElementCategory.APPLICATION_FUNCTION: ["ApplicationFunction"],
            ArchiMateElementCategory.DATA_OBJECT: ["DataObject"],
            ArchiMateElementCategory.TECHNOLOGY_NODE: ["TechnologyNode"],
            ArchiMateElementCategory.TECHNOLOGY_ARTIFACT: ["TechnologyArtifact"],
            ArchiMateElementCategory.TECHNOLOGY_SERVICE: ["TechnologyService"],
            ArchiMateElementCategory.TECHNOLOGY_DEVICE: ["TechnologyDevice"],
            ArchiMateElementCategory.TECHNOLOGY_INTERFACE: ["TechnologyInterface"],
        }

        for category, archimate_types in type_map.items():
            self._register_spec(
                category,
                ElementFormatSpec(
                    category,
                    default_width=w,
                    default_height=h,
                    font_family="Segoe UI",
                    font_size=9,
                    font_style="normal",
                    font_weight="normal",
                ),
                archimate_types,
            )

    def _register_spec(
        self,
        category: ArchiMateElementCategory,
        spec: ElementFormatSpec,
        archimate_types: list[str],
    ) -> None:
        """Register a format specification for a category and its ArchiMate types.

        Args:
            category: Element category
            spec: Format specification
            archimate_types: List of ArchiMate type names
        """
        self._specs[category.value] = spec
        for archimate_type in archimate_types:
            self._type_to_category[archimate_type] = category

    def get_spec(self, element_type: str) -> ElementFormatSpec:
        """Get format specification for an element type.

        Args:
            element_type: ArchiMate element type name

        Returns:
            ElementFormatSpec for the type, or default spec if unknown
        """
        category = self._type_to_category.get(
            element_type, ArchiMateElementCategory.UNKNOWN
        )
        if category.value in self._specs:
            return self._specs[category.value]

        # Return default spec for unknown types
        return ElementFormatSpec(
            ArchiMateElementCategory.UNKNOWN,
            default_width=ElementFormatRegistry.ARCHI_DEFAULT_WIDTH,
            default_height=ElementFormatRegistry.ARCHI_DEFAULT_HEIGHT,
            font_family="Segoe UI",
            font_size=9,
            font_style="normal",
            font_weight="normal",
        )


class FormatService:
    """Service for standardizing and formatting ArchiMate view elements."""

    def __init__(self) -> None:
        """Initialize format service."""
        self.registry = ElementFormatRegistry()

    def _apply_font(self, element: Any, spec: Any, user_font_override: dict[str, Any] | None) -> None:
        if user_font_override is None:
            self._apply_default_font(element, spec)
        else:
            self._apply_override_font(element, spec, user_font_override)

    def _apply_default_font(self, element: Any, spec: Any) -> None:
        if hasattr(element, 'font_name'):
            element.font_name = spec.font_family
            element.font_size = spec.font_size
        else:
            element.font_family = spec.font_family
            element.font_size = spec.font_size
            element.font_style = spec.font_style
            element.font_weight = spec.font_weight

    def _apply_override_font(self, element: Any, spec: Any, override: dict[str, Any]) -> None:
        if hasattr(element, 'font_name'):
            font_name = override.get("font_family") or override.get("font_name") or spec.font_family
            element.font_name = font_name
            element.font_size = int(override.get("font_size", spec.font_size))
        else:
            element.font_family = override.get("font_family", spec.font_family)
            element.font_size = int(override.get("font_size", spec.font_size))
            element.font_style = override.get("font_style", spec.font_style)
            element.font_weight = override.get("font_weight", spec.font_weight)

    def format_element(
        self,
        element: Any,
        user_size_override: Optional[Tuple[float, float]] = None,
        user_font_override: Optional[Dict[str, str]] = None,
        alignment: str = "free",
        grid_size: float = 10.0,
        size_constraints: Optional[Dict[str, float]] = None,
    ) -> None:
        """Format an individual element.

        Args:
            element: Element to format
            user_size_override: Custom size (width, height) from user, if any
            user_font_override: Custom font properties from user, if any
            alignment: "free" or "grid" for position alignment
            grid_size: Grid cell size if alignment="grid"
            size_constraints: Dict with optional constraints: {"min_width": float, "max_width": float, "min_height": float, "max_height": float}
        """
        element_type = getattr(element, "type", "unknown")
        spec = self.registry.get_spec(element_type)

        # Apply size standardization (respect user overrides and constraints)
        # Support both 'w'/'h' and 'width'/'height' attribute names
        if user_size_override is None:
            width = spec.default_width
            height = spec.default_height
        else:
            width, height = user_size_override

        # Apply size constraints if provided
        if size_constraints:
            width = self._apply_size_constraint(width, size_constraints, "width")
            height = self._apply_size_constraint(height, size_constraints, "height")

        if hasattr(element, 'w'):
            element.w = width
            element.h = height
        else:
            element.width = width
            element.height = height

        self._apply_font(element, spec, user_font_override)

        # Apply grid alignment if requested
        if alignment == "grid":
            self._snap_to_grid(element, grid_size)

    def _apply_size_constraint(self, size: float, constraints: Dict[str, float], dimension: str) -> float:
        """Apply min/max constraints to a dimension.

        Args:
            size: Current dimension value
            constraints: Dict with min/max keys
            dimension: "width" or "height"

        Returns:
            Constrained size value
        """
        min_key = f"min_{dimension}"
        max_key = f"max_{dimension}"

        if min_key in constraints:
            size = max(size, constraints[min_key])
        if max_key in constraints:
            size = min(size, constraints[max_key])

        return size

    def _snap_to_grid(self, element: Any, grid_size: float) -> None:
        """Snap element position to grid.

        Args:
            element: Element to snap
            grid_size: Grid cell size
        """
        x = getattr(element, "x", 0)
        y = getattr(element, "y", 0)

        # Convert to integers for Archi XML compatibility
        element.x = int(round(x / grid_size) * grid_size)
        element.y = int(round(y / grid_size) * grid_size)

    def format_view(
        self,
        view: Any,
        alignment: str = "free",
        grid_size: float = 10.0,
        excluded_element_ids: Optional[Set[str]] = None,
        size_constraints: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Format all elements in a view.

        Args:
            view: View to format
            alignment: "free" or "grid" for position alignment
            grid_size: Grid cell size if alignment="grid"
            excluded_element_ids: Element IDs to skip formatting
            size_constraints: Dict with optional constraints: {"min_width": float, "max_width": float, "min_height": float, "max_height": float}

        Returns:
            Dictionary with formatting statistics
        """
        if excluded_element_ids is None:
            excluded_element_ids = set()

        elements = getattr(view, "nodes", [])
        formatted_count = 0
        skipped_count = 0
        errors = []

        for element in elements:
            element_id = getattr(element, "id", None)

            if element_id is not None and (str(element_id) in excluded_element_ids or element_id in excluded_element_ids):
                skipped_count += 1
                continue

            try:
                self.format_element(
                    element,
                    alignment=alignment,
                    grid_size=grid_size,
                    size_constraints=size_constraints,
                )
                formatted_count += 1
            except Exception as e:
                skipped_count += 1
                errors.append(f"Error formatting element {element_id}: {str(e)}")

        return {
            "formatted": formatted_count,
            "skipped": skipped_count,
            "total": len(elements),
            "errors": errors,
        }

    def calculate_size_variance(self, view: Any) -> Dict[str, float]:
        """Calculate size variance statistics for a view.

        Args:
            view: View to analyze

        Returns:
            Dictionary with variance statistics (mean, std_dev, min, max)
        """
        elements = getattr(view, "nodes", [])

        if not elements:
            return {"mean": 0, "std_dev": 0, "min": 0, "max": 0}

        widths = [getattr(e, "w", getattr(e, "width", 100)) for e in elements]
        heights = [getattr(e, "h", getattr(e, "height", 80)) for e in elements]
        areas = [w * h for w, h in zip(widths, heights, strict=False)]

        mean_area = sum(areas) / len(areas)
        variance = sum((a - mean_area) ** 2 for a in areas) / len(areas)
        std_dev = math.sqrt(variance)

        return {
            "mean": mean_area,
            "std_dev": std_dev,
            "min": min(areas),
            "max": max(areas),
        }
