"""Unit tests validating the explicit-override precedence (US2, FR-004, FR-008)."""

from typing import cast

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import View


@pytest.fixture
def model_with_view():
    m = Model("Test")
    v = cast(View, m.add(ArchiType.View, "V"))
    return m, v


def test_explicit_element_color_wins_over_different_stereotype_color(model_with_view):
    m, v = model_with_view
    profile = m.add_profile(name="Risk", concept=ArchiType.Driver)
    profile.fill_color = "#F2A900"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Risk")
    elem.set_fill_color("#8B0000")
    node = v.add(elem)
    assert node.get_effective_fill_color() == "#8b0000"


def test_falls_back_to_stereotype_color_once_explicit_color_cleared(model_with_view):
    m, v = model_with_view
    profile = m.add_profile(name="Risk", concept=ArchiType.Driver)
    profile.fill_color = "#F2A900"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Risk")
    elem.set_fill_color("#8B0000")
    node = v.add(elem)
    elem.set_fill_color(None)
    assert node.get_effective_fill_color() == "#f2a900"


def test_reassigning_stereotype_updates_resolved_color(model_with_view):
    m, v = model_with_view
    profile_a = m.add_profile(name="Threat", concept=ArchiType.Driver)
    profile_a.fill_color = "#E8453C"
    profile_b = m.add_profile(name="Risk", concept=ArchiType.Driver)
    profile_b.fill_color = "#F2A900"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Threat")
    node = v.add(elem)
    assert node.get_effective_fill_color() == "#e8453c"

    elem.set_profile("Risk")
    assert node.get_effective_fill_color() == "#f2a900"
