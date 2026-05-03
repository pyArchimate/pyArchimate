"""Element formatting service for standardizing view appearance.

This module provides formatting and standardization functionality for ArchiMate elements,
including size standardization, font consistency, and grid alignment.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Set, Tuple
from enum import Enum
import math


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

    def _initialize_standards(self) -> None:
        """Initialize standard format specifications for all element types."""
        # Business layer elements (larger, emphasizing role)
        self._register_spec(
            ArchiMateElementCategory.BUSINESS_ACTOR,
            ElementFormatSpec(
                ArchiMateElementCategory.BUSINESS_ACTOR,
                default_width=100,
                default_height=80,
                font_family="Arial",
                font_size=10,
                font_style="normal",
                font_weight="normal",
            ),
            ["BusinessActor"],
        )

        self._register_spec(
            ArchiMateElementCategory.BUSINESS_ROLE,
            ElementFormatSpec(
                ArchiMateElementCategory.BUSINESS_ROLE,
                default_width=100,
                default_height=70,
                font_family="Arial",
                font_size=10,
                font_style="normal",
                font_weight="normal",
            ),
            ["BusinessRole"],
        )

        self._register_spec(
            ArchiMateElementCategory.BUSINESS_PROCESS,
            ElementFormatSpec(
                ArchiMateElementCategory.BUSINESS_PROCESS,
                default_width=120,
                default_height=80,
                font_family="Arial",
                font_size=10,
                font_style="normal",
                font_weight="normal",
            ),
            ["BusinessProcess"],
        )

        self._register_spec(
            ArchiMateElementCategory.BUSINESS_FUNCTION,
            ElementFormatSpec(
                ArchiMateElementCategory.BUSINESS_FUNCTION,
                default_width=100,
                default_height=80,
                font_family="Arial",
                font_size=10,
                font_style="normal",
                font_weight="normal",
            ),
            ["BusinessFunction"],
        )

        self._register_spec(
            ArchiMateElementCategory.BUSINESS_SERVICE,
            ElementFormatSpec(
                ArchiMateElementCategory.BUSINESS_SERVICE,
                default_width=120,
                default_height=60,
                font_family="Arial",
                font_size=10,
                font_style="normal",
                font_weight="bold",
            ),
            ["BusinessService"],
        )

        self._register_spec(
            ArchiMateElementCategory.BUSINESS_OBJECT,
            ElementFormatSpec(
                ArchiMateElementCategory.BUSINESS_OBJECT,
                default_width=80,
                default_height=80,
                font_family="Arial",
                font_size=10,
                font_style="normal",
                font_weight="normal",
            ),
            ["BusinessObject"],
        )

        self._register_spec(
            ArchiMateElementCategory.BUSINESS_EVENT,
            ElementFormatSpec(
                ArchiMateElementCategory.BUSINESS_EVENT,
                default_width=80,
                default_height=60,
                font_family="Arial",
                font_size=9,
                font_style="normal",
                font_weight="normal",
            ),
            ["BusinessEvent"],
        )

        self._register_spec(
            ArchiMateElementCategory.BUSINESS_INTERFACE,
            ElementFormatSpec(
                ArchiMateElementCategory.BUSINESS_INTERFACE,
                default_width=80,
                default_height=60,
                font_family="Arial",
                font_size=9,
                font_style="normal",
                font_weight="normal",
            ),
            ["BusinessInterface"],
        )

        # Application layer elements (medium size)
        self._register_spec(
            ArchiMateElementCategory.APPLICATION_COMPONENT,
            ElementFormatSpec(
                ArchiMateElementCategory.APPLICATION_COMPONENT,
                default_width=100,
                default_height=80,
                font_family="Arial",
                font_size=10,
                font_style="normal",
                font_weight="normal",
            ),
            ["ApplicationComponent"],
        )

        self._register_spec(
            ArchiMateElementCategory.APPLICATION_SERVICE,
            ElementFormatSpec(
                ArchiMateElementCategory.APPLICATION_SERVICE,
                default_width=120,
                default_height=60,
                font_family="Arial",
                font_size=10,
                font_style="normal",
                font_weight="bold",
            ),
            ["ApplicationService"],
        )

        self._register_spec(
            ArchiMateElementCategory.APPLICATION_INTERFACE,
            ElementFormatSpec(
                ArchiMateElementCategory.APPLICATION_INTERFACE,
                default_width=80,
                default_height=60,
                font_family="Arial",
                font_size=9,
                font_style="normal",
                font_weight="normal",
            ),
            ["ApplicationInterface"],
        )

        self._register_spec(
            ArchiMateElementCategory.APPLICATION_FUNCTION,
            ElementFormatSpec(
                ArchiMateElementCategory.APPLICATION_FUNCTION,
                default_width=100,
                default_height=70,
                font_family="Arial",
                font_size=10,
                font_style="normal",
                font_weight="normal",
            ),
            ["ApplicationFunction"],
        )

        self._register_spec(
            ArchiMateElementCategory.DATA_OBJECT,
            ElementFormatSpec(
                ArchiMateElementCategory.DATA_OBJECT,
                default_width=80,
                default_height=80,
                font_family="Arial",
                font_size=10,
                font_style="normal",
                font_weight="normal",
            ),
            ["DataObject"],
        )

        # Technology layer elements (smaller, technical detail)
        self._register_spec(
            ArchiMateElementCategory.TECHNOLOGY_NODE,
            ElementFormatSpec(
                ArchiMateElementCategory.TECHNOLOGY_NODE,
                default_width=100,
                default_height=80,
                font_family="Arial",
                font_size=9,
                font_style="normal",
                font_weight="normal",
            ),
            ["TechnologyNode"],
        )

        self._register_spec(
            ArchiMateElementCategory.TECHNOLOGY_ARTIFACT,
            ElementFormatSpec(
                ArchiMateElementCategory.TECHNOLOGY_ARTIFACT,
                default_width=80,
                default_height=80,
                font_family="Arial",
                font_size=9,
                font_style="normal",
                font_weight="normal",
            ),
            ["TechnologyArtifact"],
        )

        self._register_spec(
            ArchiMateElementCategory.TECHNOLOGY_SERVICE,
            ElementFormatSpec(
                ArchiMateElementCategory.TECHNOLOGY_SERVICE,
                default_width=120,
                default_height=60,
                font_family="Arial",
                font_size=9,
                font_style="normal",
                font_weight="bold",
            ),
            ["TechnologyService"],
        )

        self._register_spec(
            ArchiMateElementCategory.TECHNOLOGY_DEVICE,
            ElementFormatSpec(
                ArchiMateElementCategory.TECHNOLOGY_DEVICE,
                default_width=100,
                default_height=80,
                font_family="Arial",
                font_size=9,
                font_style="normal",
                font_weight="normal",
            ),
            ["TechnologyDevice"],
        )

        self._register_spec(
            ArchiMateElementCategory.TECHNOLOGY_INTERFACE,
            ElementFormatSpec(
                ArchiMateElementCategory.TECHNOLOGY_INTERFACE,
                default_width=80,
                default_height=60,
                font_family="Arial",
                font_size=8,
                font_style="normal",
                font_weight="normal",
            ),
            ["TechnologyInterface"],
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
            default_width=100,
            default_height=80,
            font_family="Arial",
            font_size=10,
            font_style="normal",
            font_weight="normal",
        )


class FormatService:
    """Service for standardizing and formatting ArchiMate view elements."""

    def __init__(self) -> None:
        """Initialize format service."""
        self.registry = ElementFormatRegistry()

    def format_element(
        self,
        element: Any,
        user_size_override: Optional[Tuple[float, float]] = None,
        user_font_override: Optional[Dict[str, str]] = None,
        alignment: str = "free",
        grid_size: float = 10.0,
    ) -> None:
        """Format an individual element.

        Args:
            element: Element to format
            user_size_override: Custom size (width, height) from user, if any
            user_font_override: Custom font properties from user, if any
            alignment: "free" or "grid" for position alignment
            grid_size: Grid cell size if alignment="grid"
        """
        element_type = getattr(element, "type", "unknown")
        spec = self.registry.get_spec(element_type)

        # Apply size standardization (respect user overrides)
        if user_size_override is None:
            element.width = spec.default_width
            element.height = spec.default_height
        else:
            element.width, element.height = user_size_override

        # Apply font standardization (respect user overrides)
        if user_font_override is None:
            element.font_family = spec.font_family
            element.font_size = spec.font_size
            element.font_style = spec.font_style
            element.font_weight = spec.font_weight
        else:
            if "font_family" in user_font_override:
                element.font_family = user_font_override["font_family"]
            else:
                element.font_family = spec.font_family

            if "font_size" in user_font_override:
                element.font_size = int(user_font_override["font_size"])
            else:
                element.font_size = spec.font_size

            if "font_style" in user_font_override:
                element.font_style = user_font_override["font_style"]
            else:
                element.font_style = spec.font_style

            if "font_weight" in user_font_override:
                element.font_weight = user_font_override["font_weight"]
            else:
                element.font_weight = spec.font_weight

        # Apply grid alignment if requested
        if alignment == "grid":
            self._snap_to_grid(element, grid_size)

    def _snap_to_grid(self, element: Any, grid_size: float) -> None:
        """Snap element position to grid.

        Args:
            element: Element to snap
            grid_size: Grid cell size
        """
        x = getattr(element, "x", 0)
        y = getattr(element, "y", 0)

        element.x = round(x / grid_size) * grid_size
        element.y = round(y / grid_size) * grid_size

    def format_view(
        self,
        view: Any,
        alignment: str = "free",
        grid_size: float = 10.0,
        excluded_element_ids: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """Format all elements in a view.

        Args:
            view: View to format
            alignment: "free" or "grid" for position alignment
            grid_size: Grid cell size if alignment="grid"
            excluded_element_ids: Element IDs to skip formatting

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

            if element_id in excluded_element_ids:
                skipped_count += 1
                continue

            try:
                self.format_element(element, alignment=alignment, grid_size=grid_size)
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

        widths = [getattr(e, "width", 100) for e in elements]
        heights = [getattr(e, "height", 80) for e in elements]
        areas = [w * h for w, h in zip(widths, heights)]

        mean_area = sum(areas) / len(areas)
        variance = sum((a - mean_area) ** 2 for a in areas) / len(areas)
        std_dev = math.sqrt(variance)

        return {
            "mean": mean_area,
            "std_dev": std_dev,
            "min": min(areas),
            "max": max(areas),
        }
