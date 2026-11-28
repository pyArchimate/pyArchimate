"""Unit tests for Node.get_effective_fill_color() resolution precedence (research.md Decision 1)."""

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


# ---------------------------------------------------------------------------
# Branch 3/4 — stereotype fallback and none (US1 Acceptance Scenarios 1-3)
# ---------------------------------------------------------------------------


def test_resolves_to_stereotype_color_when_unset_elsewhere(model_with_view):
    m, v = model_with_view
    profile = m.add_profile(name="Threat", concept=ArchiType.Driver)
    profile.fill_color = "#E8453C"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Threat")
    node = v.add(elem)
    assert node.get_effective_fill_color() == "#e8453c"


def test_stereotype_color_applies_to_multiple_elements(model_with_view):
    m, v = model_with_view
    profile = m.add_profile(name="Threat", concept=ArchiType.Driver)
    profile.fill_color = "#E8453C"
    elem_a = m.add(ArchiType.Driver, "A")
    elem_a.set_profile("Threat")
    elem_b = m.add(ArchiType.Driver, "B")
    elem_b.set_profile("Threat")
    node_a = v.add(elem_a)
    node_b = v.add(elem_b)
    assert node_a.get_effective_fill_color() == "#e8453c"
    assert node_b.get_effective_fill_color() == "#e8453c"


def test_changed_stereotype_color_reflected_without_touching_elements(model_with_view):
    m, v = model_with_view
    profile = m.add_profile(name="Threat", concept=ArchiType.Driver)
    profile.fill_color = "#E8453C"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Threat")
    node = v.add(elem)
    assert node.get_effective_fill_color() == "#e8453c"
    profile.fill_color = "#F2A900"
    assert node.get_effective_fill_color() == "#f2a900"


def test_reverts_to_none_once_stereotype_color_cleared(model_with_view):
    m, v = model_with_view
    profile = m.add_profile(name="Threat", concept=ArchiType.Driver)
    profile.fill_color = "#E8453C"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Threat")
    node = v.add(elem)
    profile.fill_color = None
    assert node.get_effective_fill_color() is None


def test_no_stereotype_and_no_explicit_color_resolves_to_none(model_with_view):
    m, v = model_with_view
    elem = m.add(ArchiType.Driver, "D1")
    node = v.add(elem)
    assert node.get_effective_fill_color() is None


# ---------------------------------------------------------------------------
# Branch 1/2 — Node.fill_color and Element.get_fill_color() precedence (FR-004)
# ---------------------------------------------------------------------------


def test_node_fill_color_wins_over_element_and_stereotype_color(model_with_view):
    m, v = model_with_view
    profile = m.add_profile(name="Threat", concept=ArchiType.Driver)
    profile.fill_color = "#E8453C"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Threat")
    elem.set_fill_color("#8B0000")
    node = v.add(elem)
    node.fill_color = "#123456"
    assert node.get_effective_fill_color() == "#123456"


def test_element_fill_color_wins_over_stereotype_color_when_node_unset(model_with_view):
    m, v = model_with_view
    profile = m.add_profile(name="Threat", concept=ArchiType.Driver)
    profile.fill_color = "#E8453C"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Threat")
    elem.set_fill_color("#8B0000")
    node = v.add(elem)
    assert node.get_effective_fill_color() == "#8b0000"
