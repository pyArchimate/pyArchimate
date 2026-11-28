"""Unit tests for Profile.fill_color validation (FR-001-FR-003)."""

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


@pytest.fixture
def profile():
    m = Model("Test")
    return m.add_profile(name="Threat", concept=ArchiType.Driver)


def test_fill_color_defaults_to_none(profile):
    assert profile.fill_color is None


def test_fill_color_accepts_hex(profile):
    profile.fill_color = "#E8453C"
    assert profile.fill_color == "#e8453c"


def test_fill_color_accepts_named_color_case_insensitive(profile):
    profile.fill_color = "DarkOrange"
    assert profile.fill_color is not None
    assert profile.fill_color.startswith("#")


def test_fill_color_rejects_invalid_value(profile):
    with pytest.raises(ValueError):
        profile.fill_color = "not-a-color"


def test_fill_color_can_be_cleared(profile):
    profile.fill_color = "#E8453C"
    profile.fill_color = None
    assert profile.fill_color is None


def test_fill_color_invalid_value_leaves_prior_state_unchanged(profile):
    profile.fill_color = "#E8453C"
    with pytest.raises(ValueError):
        profile.fill_color = "not-a-color"
    assert profile.fill_color == "#e8453c"


def test_get_profile_returns_none_for_dangling_profile_reference():
    """Element.get_profile() must not raise if _profile points to a uuid that
    is no longer present in model.profiles (defensive guard; not reachable via
    the public API, which always clears _profile before a profile disappears)."""
    m = Model("Test")
    elem = m.add(ArchiType.Driver, "D1")
    elem._profile = "00000000-0000-4000-8000-000000000000"
    assert elem.get_profile() is None
