"""Regression test: deleting a stereotype clears referencing elements' stereotype
assignment and therefore their stereotype-derived effective color, while leaving
any explicit element-level color untouched (spec.md Edge Cases)."""

from typing import cast

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import View


def test_deleting_stereotype_clears_derived_color_but_not_explicit_color():
    m = Model("Test")
    profile = m.add_profile(name="Risk", concept=ArchiType.Driver)
    profile.fill_color = "#F2A900"

    with_derived_color = m.add(ArchiType.Driver, "D1")
    with_derived_color.set_profile("Risk")

    with_explicit_color = m.add(ArchiType.Driver, "D2")
    with_explicit_color.set_profile("Risk")
    with_explicit_color.set_fill_color("#8B0000")

    v = cast(View, m.add(ArchiType.View, "V"))
    n1 = v.add(with_derived_color, x=0, y=0, w=120, h=55)
    n2 = v.add(with_explicit_color, x=200, y=0, w=120, h=55)

    assert n1.get_effective_fill_color() == "#f2a900"
    assert n2.get_effective_fill_color() == "#8b0000"

    profile.delete()

    assert with_derived_color.get_profile() is None
    assert n1.get_effective_fill_color() is None

    assert with_explicit_color.get_profile() is None
    assert n2.get_effective_fill_color() == "#8b0000"
