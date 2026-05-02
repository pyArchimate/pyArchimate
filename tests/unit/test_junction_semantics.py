"""Unit tests for junction type semantics and validation.

Tests cover junction type validation, setter/getter methods, and edge cases.
"""

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


class TestJunctionTypeValidation:
    """T040-T042: Junction type validation and API."""

    def test_junction_type_default_none(self):
        """Test that junction_type defaults to None on element creation."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'Test Junction')
        assert elem.junction_type is None
        assert elem.get_junction_type() is None

    def test_set_junction_type_and(self):
        """Test setting junction type to 'and'."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'AND Junction')
        elem.set_junction_type('and')
        assert elem.get_junction_type() == 'and'

    def test_set_junction_type_or(self):
        """Test setting junction type to 'or'."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'OR Junction')
        elem.set_junction_type('or')
        assert elem.get_junction_type() == 'or'

    def test_set_junction_type_xor(self):
        """Test setting junction type to 'xor'."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'XOR Junction')
        elem.set_junction_type('xor')
        assert elem.get_junction_type() == 'xor'

    def test_set_junction_type_case_insensitive(self):
        """Test that junction type setting is case-insensitive."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'Test Junction')
        elem.set_junction_type('AND')
        assert elem.get_junction_type() == 'and'
        elem.set_junction_type('Or')
        assert elem.get_junction_type() == 'or'
        elem.set_junction_type('XoR')
        assert elem.get_junction_type() == 'xor'

    def test_set_junction_type_strips_whitespace(self):
        """Test that junction type setting strips whitespace."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'Test Junction')
        elem.set_junction_type('  and  ')
        assert elem.get_junction_type() == 'and'

    def test_set_junction_type_none_clears(self):
        """Test that setting junction type to None clears it."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'Test Junction')
        elem.set_junction_type('and')
        assert elem.get_junction_type() == 'and'
        elem.set_junction_type(None)
        assert elem.get_junction_type() is None

    def test_set_junction_type_invalid_raises(self):
        """Test that invalid junction types raise ValueError."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'Test Junction')
        with pytest.raises(ValueError, match="Invalid junction type"):
            elem.set_junction_type('invalid')
        with pytest.raises(ValueError, match="Invalid junction type"):
            elem.set_junction_type('nand')
        with pytest.raises(ValueError, match="Invalid junction type"):
            elem.set_junction_type('nor')

    def test_junction_type_on_non_junction_element(self):
        """Test that junction type can be set on non-Junction elements (no validation)."""
        m = Model('test-model')
        elem = m.add(ArchiType.BusinessProcess, 'Process')
        elem.set_junction_type('and')
        assert elem.get_junction_type() == 'and'

    def test_multiple_junction_types_different_elements(self):
        """Test that different junction elements can have different types."""
        m = Model('test-model')
        and_junction = m.add(ArchiType.Junction, 'AND Junction')
        or_junction = m.add(ArchiType.Junction, 'OR Junction')
        xor_junction = m.add(ArchiType.Junction, 'XOR Junction')

        and_junction.set_junction_type('and')
        or_junction.set_junction_type('or')
        xor_junction.set_junction_type('xor')

        assert and_junction.get_junction_type() == 'and'
        assert or_junction.get_junction_type() == 'or'
        assert xor_junction.get_junction_type() == 'xor'

    def test_junction_type_persistence_after_property_change(self):
        """Test that junction type persists when other properties change."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'Test Junction')
        elem.set_junction_type('and')
        elem.name = 'Updated Name'
        elem.desc = 'Updated Description'
        elem.prop('key', 'value')
        assert elem.get_junction_type() == 'and'

    def test_empty_string_junction_type_raises(self):
        """Test that empty string junction type raises ValueError."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'Test Junction')
        with pytest.raises(ValueError, match="Invalid junction type"):
            elem.set_junction_type('')

    def test_whitespace_only_junction_type_raises(self):
        """Test that whitespace-only junction type raises ValueError."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'Test Junction')
        with pytest.raises(ValueError, match="Invalid junction type"):
            elem.set_junction_type('   ')

    def test_junction_type_numeric_string_raises(self):
        """Test that numeric strings raise ValueError."""
        m = Model('test-model')
        elem = m.add(ArchiType.Junction, 'Test Junction')
        with pytest.raises(ValueError, match="Invalid junction type"):
            elem.set_junction_type('1')
        with pytest.raises(ValueError, match="Invalid junction type"):
            elem.set_junction_type('0')
