"""Tests for ArchiMate layer constraint module."""

from src.pyArchimate.view.layout.routing.layer_constraints import (
    ArchiMateLayer,
    LayerConstraint,
)


class TestArchiMateLayer:
    """Tests for ArchiMateLayer enum."""

    def test_layer_from_business_type(self) -> None:
        """Test layer detection for business elements."""
        assert ArchiMateLayer.from_archimate_type("BusinessActor") == ArchiMateLayer.BUSINESS
        assert ArchiMateLayer.from_archimate_type("BusinessProcess") == ArchiMateLayer.BUSINESS
        assert ArchiMateLayer.from_archimate_type("BusinessRole") == ArchiMateLayer.BUSINESS

    def test_layer_from_application_type(self) -> None:
        """Test layer detection for application elements."""
        assert ArchiMateLayer.from_archimate_type("ApplicationComponent") == ArchiMateLayer.APPLICATION
        assert ArchiMateLayer.from_archimate_type("ApplicationService") == ArchiMateLayer.APPLICATION

    def test_layer_from_technology_type(self) -> None:
        """Test layer detection for technology elements."""
        assert ArchiMateLayer.from_archimate_type("Technology") == ArchiMateLayer.TECHNOLOGY
        assert ArchiMateLayer.from_archimate_type("InfrastructureService") == ArchiMateLayer.TECHNOLOGY

    def test_layer_order(self) -> None:
        """Test layer ordering."""
        assert ArchiMateLayer.BUSINESS.layer_order() == 0
        assert ArchiMateLayer.APPLICATION.layer_order() == 1
        assert ArchiMateLayer.TECHNOLOGY.layer_order() == 2
        assert ArchiMateLayer.OTHER.layer_order() == 3


class TestLayerConstraint:
    """Tests for LayerConstraint class."""

    def test_assign_and_get_layer(self) -> None:
        """Test assigning and retrieving element layers."""
        lc = LayerConstraint()
        lc.assign_layer("elem1", ArchiMateLayer.BUSINESS)
        assert lc.get_layer("elem1") == ArchiMateLayer.BUSINESS

    def test_get_layer_default(self) -> None:
        """Test getting layer for unassigned element."""
        lc = LayerConstraint()
        assert lc.get_layer("unknown") == ArchiMateLayer.OTHER

    def test_validate_layer_order_vertical_valid(self) -> None:
        """Test vertical layer order validation (valid)."""
        lc = LayerConstraint()
        lc.assign_layer("elem1", ArchiMateLayer.BUSINESS)
        lc.assign_layer("elem2", ArchiMateLayer.APPLICATION)

        positions = {
            "elem1": (100, 50),  # Business higher (lower y)
            "elem2": (100, 150),  # Application lower (higher y)
        }

        assert lc.validate_layer_order(positions, vertical=True) is True

    def test_validate_layer_order_vertical_invalid(self) -> None:
        """Test vertical layer order validation (invalid)."""
        lc = LayerConstraint()
        lc.assign_layer("elem1", ArchiMateLayer.BUSINESS)
        lc.assign_layer("elem2", ArchiMateLayer.APPLICATION)

        positions = {
            "elem1": (100, 150),  # Business lower (higher y) - WRONG
            "elem2": (100, 50),  # Application higher (lower y) - WRONG
        }

        assert lc.validate_layer_order(positions, vertical=True) is False

    def test_validate_layer_order_horizontal_valid(self) -> None:
        """Test horizontal layer order validation (valid)."""
        lc = LayerConstraint()
        lc.assign_layer("elem1", ArchiMateLayer.BUSINESS)
        lc.assign_layer("elem2", ArchiMateLayer.APPLICATION)

        positions = {
            "elem1": (50, 100),  # Business left (lower x)
            "elem2": (150, 100),  # Application right (higher x)
        }

        assert lc.validate_layer_order(positions, vertical=False) is True

    def test_enforce_layer_separation(self) -> None:
        """Test layer separation enforcement."""
        lc = LayerConstraint()
        lc.assign_layer("elem1", ArchiMateLayer.BUSINESS)
        lc.assign_layer("elem2", ArchiMateLayer.APPLICATION)
        lc.assign_layer("elem3", ArchiMateLayer.TECHNOLOGY)

        positions = {
            "elem1": (100, 200),
            "elem2": (100, 300),
            "elem3": (100, 400),
        }

        updated = lc.enforce_layer_separation(positions, spacing=50)

        # Check that positions were adjusted
        assert updated is not None
        assert "elem1" in updated
        assert "elem2" in updated
        assert "elem3" in updated
