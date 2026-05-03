"""ArchiMate layer constraint handling for layout operations."""

from enum import Enum
from typing import Dict, Set


class ArchiMateLayer(Enum):
    """ArchiMate layers as defined in the specification."""

    BUSINESS = "business"
    APPLICATION = "application"
    TECHNOLOGY = "technology"
    OTHER = "other"

    @classmethod
    def from_archimate_type(cls, element_type: str) -> "ArchiMateLayer":
        """Determine ArchiMate layer from element type."""
        element_type_lower = element_type.lower()

        # Check for explicit layer indicators first
        if "business" in element_type_lower:
            return cls.BUSINESS
        if "application" in element_type_lower:
            return cls.APPLICATION
        if any(t in element_type_lower for t in ["technology", "infrastructure", "device"]):
            return cls.TECHNOLOGY

        # Business layer elements
        if any(t in element_type_lower for t in ["actor", "role", "interaction", "process", "function", "product", "event"]):
            return cls.BUSINESS

        # Application layer elements
        if any(t in element_type_lower for t in ["component", "interface", "data object"]):
            return cls.APPLICATION

        # Technology layer elements
        if any(t in element_type_lower for t in ["system software", "node", "network"]):
            return cls.TECHNOLOGY

        return cls.OTHER

    def layer_order(self) -> int:
        """Get layer ordering (higher = lower in diagram)."""
        order = {
            ArchiMateLayer.BUSINESS: 0,
            ArchiMateLayer.APPLICATION: 1,
            ArchiMateLayer.TECHNOLOGY: 2,
            ArchiMateLayer.OTHER: 3,
        }
        return order[self]


class LayerConstraint:
    """Manages ArchiMate layer constraints during layout."""

    def __init__(self) -> None:
        """Initialize layer constraint system."""
        self.element_layers: Dict[str, ArchiMateLayer] = {}

    def assign_layer(self, element_id: str, layer: ArchiMateLayer) -> None:
        """Assign an element to a layer."""
        self.element_layers[element_id] = layer

    def get_layer(self, element_id: str) -> ArchiMateLayer:
        """Get the layer of an element."""
        return self.element_layers.get(element_id, ArchiMateLayer.OTHER)

    def validate_layer_order(
        self, positions: Dict[str, tuple[float, float]], vertical: bool = True
    ) -> bool:
        """Validate that element positions respect layer ordering.

        Args:
            positions: Dict of element_id -> (x, y) position
            vertical: If True, check vertical ordering; else horizontal

        Returns:
            True if all constraints satisfied, False otherwise
        """
        for elem1_id, pos1 in positions.items():
            for elem2_id, pos2 in positions.items():
                if elem1_id >= elem2_id:
                    continue

                layer1 = self.get_layer(elem1_id)
                layer2 = self.get_layer(elem2_id)

                if layer1.layer_order() < layer2.layer_order():
                    # layer1 should be "above" or "left of" layer2
                    if vertical:
                        # Vertical: smaller y means higher position
                        if pos1[1] > pos2[1]:
                            return False
                    else:
                        # Horizontal: smaller x means more left
                        if pos1[0] > pos2[0]:
                            return False

        return True

    def enforce_layer_separation(
        self, positions: Dict[str, tuple[float, float]], spacing: float = 100
    ) -> Dict[str, tuple[float, float]]:
        """Enforce minimum separation between layers.

        Args:
            positions: Dict of element_id -> (x, y) position
            spacing: Minimum spacing between layers

        Returns:
            Updated positions dict with layer constraints enforced
        """
        # Group elements by layer
        layers: Dict[ArchiMateLayer, list[str]] = {}
        for elem_id, layer in self.element_layers.items():
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(elem_id)

        updated_positions = dict(positions)

        # Ensure proper vertical ordering (Business > Application > Technology)
        layer_y_ranges = {}
        current_y = 0
        for layer in [ArchiMateLayer.BUSINESS, ArchiMateLayer.APPLICATION, ArchiMateLayer.TECHNOLOGY]:
            if layer in layers:
                max_height = max(50, len(layers[layer]) * 30)
                layer_y_ranges[layer] = (current_y, current_y + max_height)
                current_y += max_height + spacing

        # Adjust positions to enforce layer boundaries
        for elem_id, pos in updated_positions.items():
            layer = self.get_layer(elem_id)
            if layer in layer_y_ranges:
                y_min, y_max = layer_y_ranges[layer]
                new_y = max(y_min, min(pos[1], y_max - 50))
                updated_positions[elem_id] = (pos[0], new_y)

        return updated_positions
