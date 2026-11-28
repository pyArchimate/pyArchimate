"""Compatibility test: apply_profile_styles() composes correctly with the automatic
stereotype-color resolution chain, since it sets Node.fill_color directly (tier 1
of research.md Decision 1)."""

from typing import cast

from src.pyArchimate import ArchiType
from src.pyArchimate.helpers.diagram import apply_profile_styles
from src.pyArchimate.model import Model
from src.pyArchimate.view import View


def test_apply_profile_styles_wins_over_automatic_stereotype_color():
    m = Model("Test")
    profile = m.add_profile(name="Risk", concept=ArchiType.Driver)
    profile.fill_color = "#F2A900"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Risk")
    v = cast(View, m.add(ArchiType.View, "V"))
    node = v.add(elem, x=0, y=0, w=120, h=55)

    assert node.get_effective_fill_color() == "#f2a900"

    apply_profile_styles(v, {"Risk": "#123456"})

    assert node.get_effective_fill_color() == "#123456"


def test_apply_profile_styles_with_no_matching_profile_leaves_stereotype_color_in_effect():
    m = Model("Test")
    profile = m.add_profile(name="Risk", concept=ArchiType.Driver)
    profile.fill_color = "#F2A900"
    elem = m.add(ArchiType.Driver, "D1")
    elem.set_profile("Risk")
    v = cast(View, m.add(ArchiType.View, "V"))
    node = v.add(elem, x=0, y=0, w=120, h=55)

    apply_profile_styles(v, {"SomeOtherProfile": "#123456"})

    assert node.get_effective_fill_color() == "#f2a900"
