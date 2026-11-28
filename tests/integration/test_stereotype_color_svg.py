"""Integration test: SVG export renders elements using their effective fill color (FR-011, SC-002)."""

from typing import cast

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import View


def test_svg_export_uses_stereotype_color_for_unstyled_element():
    m = Model("Test")
    v = cast(View, m.add(ArchiType.View, "V"))
    profile = m.add_profile(name="Threat", concept=ArchiType.Driver)
    profile.fill_color = "#E8453C"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Threat")
    v.add(elem)

    svg = v.to_svg()

    assert "#e8453c" in svg.lower()


def test_svg_export_explicit_element_color_wins_over_stereotype():
    m = Model("Test")
    v = cast(View, m.add(ArchiType.View, "V"))
    profile = m.add_profile(name="Threat", concept=ArchiType.Driver)
    profile.fill_color = "#E8453C"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Threat")
    elem.set_fill_color("#8B0000")
    v.add(elem)

    svg = v.to_svg()

    assert "#8b0000" in svg.lower()
    assert "#e8453c" not in svg.lower()
