"""Unit tests for Element visual style (P3 Phase 2)."""

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestFillColorSetter:
    """Test set_fill_color method."""

    def test_set_fill_color_hex_uppercase(self):
        """Test setting fill color with uppercase hex."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('#FF0000')

        assert elem.get_fill_color() == '#ff0000'

    def test_set_fill_color_hex_lowercase(self):
        """Test setting fill color with lowercase hex."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('#ff0000')

        assert elem.get_fill_color() == '#ff0000'

    def test_set_fill_color_named(self):
        """Test setting fill color with named color."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('red')

        assert elem.get_fill_color() == '#ff0000'

    def test_set_fill_color_named_case_insensitive(self):
        """Test named color is case-insensitive."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('RED')

        assert elem.get_fill_color() == '#ff0000'

    def test_set_fill_color_named_mixed_case(self):
        """Test named color with mixed case."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('DarkRed')

        assert elem.get_fill_color() == '#8b0000'

    def test_set_fill_color_invalid_hex_format(self):
        """Test error on invalid hex format."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        with pytest.raises(ValueError, match="Invalid hex color"):
            elem.set_fill_color('#GGGGGG')

    def test_set_fill_color_invalid_hex_short(self):
        """Test error on hex format too short."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        with pytest.raises(ValueError, match="Invalid hex color"):
            elem.set_fill_color('#FFF')

    def test_set_fill_color_unknown_name(self):
        """Test error on unknown color name."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        with pytest.raises(ValueError, match="Unknown color"):
            elem.set_fill_color('rainbow')

    def test_set_fill_color_none_clears(self):
        """Test that None clears the color."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('#ff0000')
        elem.set_fill_color(None)

        assert elem.get_fill_color() is None


class TestLineColorSetter:
    """Test set_line_color method."""

    def test_set_line_color_hex(self):
        """Test setting line color with hex."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_line_color('#0000FF')

        assert elem.get_line_color() == '#0000ff'

    def test_set_line_color_named(self):
        """Test setting line color with named color."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_line_color('blue')

        assert elem.get_line_color() == '#0000ff'

    def test_set_line_color_invalid(self):
        """Test error on invalid line color."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        with pytest.raises(ValueError):
            elem.set_line_color('notacolor')

    def test_set_line_color_none_clears(self):
        """Test that None clears the color."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_line_color('#0000ff')
        elem.set_line_color(None)

        assert elem.get_line_color() is None


class TestLineWidthSetter:
    """Test set_line_width method."""

    def test_set_line_width_float(self):
        """Test setting line width with float."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_line_width(2.5)

        assert elem.get_line_width() == pytest.approx(2.5)

    def test_set_line_width_int(self):
        """Test setting line width with int."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_line_width(2)

        assert elem.get_line_width() == pytest.approx(2.0)

    def test_set_line_width_zero(self):
        """Test setting line width to zero."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_line_width(0.0)

        assert elem.get_line_width() == pytest.approx(0.0)

    def test_set_line_width_negative_error(self):
        """Test error on negative line width."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        with pytest.raises(ValueError, match="must be non-negative"):
            elem.set_line_width(-1.0)

    def test_set_line_width_string_error(self):
        """Test error on string line width."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        with pytest.raises(TypeError, match="must be number"):
            elem.set_line_width("2.0")

    def test_set_line_width_none_clears(self):
        """Test that None clears the width."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_line_width(2.5)
        elem.set_line_width(None)

        assert elem.get_line_width() is None


class TestTransparencySetter:
    """Test set_transparency method."""

    def test_set_transparency_valid_values(self):
        """Test setting transparency with valid values."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        for value in [0.0, 0.5, 1.0]:
            elem.set_transparency(value)
            assert elem.get_transparency() == value

    def test_set_transparency_int(self):
        """Test setting transparency with int."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_transparency(1)

        assert elem.get_transparency() == pytest.approx(1.0)

    def test_set_transparency_too_high(self):
        """Test error on transparency > 1.0."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        with pytest.raises(ValueError, match="must be 0.0-1.0"):
            elem.set_transparency(1.5)

    def test_set_transparency_negative(self):
        """Test error on negative transparency."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        with pytest.raises(ValueError, match="must be 0.0-1.0"):
            elem.set_transparency(-0.1)

    def test_set_transparency_string_error(self):
        """Test error on string transparency."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        with pytest.raises(TypeError, match="must be number"):
            elem.set_transparency("0.8")

    def test_set_transparency_none_clears(self):
        """Test that None clears the transparency."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_transparency(0.5)
        elem.set_transparency(None)

        assert elem.get_transparency() is None


class TestSetVisualStyleBulk:
    """Test set_visual_style bulk setter."""

    def test_set_visual_style_all_properties(self):
        """Test setting all visual style properties at once."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_visual_style(
            fill_color='red',
            line_color='blue',
            line_width=2.0,
            transparency=0.8
        )

        assert elem.get_fill_color() == '#ff0000'
        assert elem.get_line_color() == '#0000ff'
        assert elem.get_line_width() == pytest.approx(2.0)
        assert elem.get_transparency() == pytest.approx(0.8)

    def test_set_visual_style_partial(self):
        """Test setting only some visual style properties."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_visual_style(fill_color='red', line_width=2.0)

        assert elem.get_fill_color() == '#ff0000'
        assert elem.get_line_color() is None
        assert elem.get_line_width() == pytest.approx(2.0)
        assert elem.get_transparency() is None

    def test_set_visual_style_invalid_property(self):
        """Test that invalid property in bulk set fails."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        with pytest.raises(ValueError):
            elem.set_visual_style(fill_color='notacolor')


class TestGetVisualStyle:
    """Test get_visual_style method."""

    def test_get_visual_style_empty(self):
        """Test getting empty visual style."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        style = elem.get_visual_style()

        assert style == {}

    def test_get_visual_style_partial(self):
        """Test getting partial visual style."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('red')
        elem.set_line_width(2.0)

        style = elem.get_visual_style()

        assert style == {'fillColor': '#ff0000', 'lineWidth': 2.0}

    def test_get_visual_style_all(self):
        """Test getting complete visual style."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('red')
        elem.set_line_color('blue')
        elem.set_line_width(2.0)
        elem.set_transparency(0.8)

        style = elem.get_visual_style()

        assert style == {
            'fillColor': '#ff0000',
            'lineColor': '#0000ff',
            'lineWidth': 2.0,
            'transparency': 0.8
        }

    def test_get_visual_style_returns_copy(self):
        """Test that get_visual_style returns a copy, not a reference."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('red')
        style = elem.get_visual_style()
        style['fillColor'] = '#0000ff'

        assert elem.get_fill_color() == '#ff0000'


class TestResetVisualStyle:
    """Test reset_visual_style method."""

    def test_reset_visual_style_clears_all(self):
        """Test that reset clears all custom styles."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_visual_style(
            fill_color='red',
            line_color='blue',
            line_width=2.0,
            transparency=0.8
        )

        elem.reset_visual_style()

        assert elem.get_fill_color() is None
        assert elem.get_line_color() is None
        assert elem.get_line_width() is None
        assert elem.get_transparency() is None

    def test_reset_visual_style_empty_dict(self):
        """Test that reset results in empty visual style dict."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('red')
        elem.reset_visual_style()

        assert elem.get_visual_style() == {}


class TestColorNormalization:
    """Test color normalization behavior."""

    def test_color_normalization_hex_case(self):
        """Test that hex colors are normalized to lowercase."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('#ABCDEF')

        assert elem.get_fill_color() == '#abcdef'

    def test_color_normalization_named_to_hex(self):
        """Test that named colors are converted to hex."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('darkred')

        assert elem.get_fill_color() == '#8b0000'

    def test_color_storage_always_hex(self):
        """Test that colors are always stored as hex."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('red')

        style = elem.get_visual_style()
        assert isinstance(style['fillColor'], str)
        assert style['fillColor'].startswith('#')
        assert len(style['fillColor']) == 7


class TestVisualStyleIndependence:
    """Test that visual style properties are independent."""

    def test_fill_and_line_independent(self):
        """Test that fill and line colors are independent."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('red')
        elem.set_line_color('blue')

        assert elem.get_fill_color() == '#ff0000'
        assert elem.get_line_color() == '#0000ff'

    def test_color_and_width_independent(self):
        """Test that colors and width are independent."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('red')
        elem.set_line_width(2.0)

        elem.set_fill_color(None)

        assert elem.get_fill_color() is None
        assert elem.get_line_width() == pytest.approx(2.0)

    def test_properties_accumulate(self):
        """Test that properties accumulate correctly."""
        model = Model('TestModel')
        elem = model.add(ArchiType.BusinessProcess, 'Elem')

        elem.set_fill_color('red')
        assert len(elem.get_visual_style()) == 1

        elem.set_line_color('blue')
        assert len(elem.get_visual_style()) == 2

        elem.set_line_width(2.0)
        assert len(elem.get_visual_style()) == 3

        elem.set_transparency(0.8)
        assert len(elem.get_visual_style()) == 4


class TestMultipleElements:
    """Test visual style on multiple elements."""

    def test_visual_style_per_element(self):
        """Test that visual style is per-element, not global."""
        model = Model('TestModel')
        elem1 = model.add(ArchiType.BusinessProcess, 'Elem1')
        elem2 = model.add(ArchiType.BusinessProcess, 'Elem2')

        elem1.set_fill_color('red')
        elem2.set_fill_color('blue')

        assert elem1.get_fill_color() == '#ff0000'
        assert elem2.get_fill_color() == '#0000ff'

    def test_visual_style_independence_across_elements(self):
        """Test that modifying one element's style doesn't affect others."""
        model = Model('TestModel')
        elem1 = model.add(ArchiType.BusinessProcess, 'Elem1')
        elem2 = model.add(ArchiType.BusinessProcess, 'Elem2')

        elem1.set_visual_style(fill_color='red', line_width=2.0)
        elem2.set_visual_style(fill_color='blue', line_width=1.0)

        elem1.reset_visual_style()

        assert elem1.get_fill_color() is None
        assert elem2.get_fill_color() == '#0000ff'
