"""Integration tests: view.to_svg() automatic non-standard stereotype labeling (US4, SC-006)."""

from typing import cast

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import View


def test_to_svg_default_labels_non_standard_and_omits_standard_and_unstereotyped():
    m = Model("Test")
    v = cast(View, m.add(ArchiType.View, "V"))

    non_standard = m.add(ArchiType.ApplicationComponent, "App1")
    non_standard.set_profile("Risk")
    v.add(non_standard, x=10, y=10, w=120, h=55)

    standard = m.add(ArchiType.ApplicationComponent, "App2")
    standard.set_profile("ApplicationComponent")
    v.add(standard, x=150, y=10, w=120, h=55)

    unstereotyped = m.add(ArchiType.ApplicationComponent, "App3")
    v.add(unstereotyped, x=290, y=10, w=120, h=55)

    svg = v.to_svg()

    assert "«Risk»" in svg
    assert "«ApplicationComponent»" not in svg
    occurrences = svg.count("«")
    assert occurrences == 1


def test_to_svg_show_stereotypes_true_force_renders_every_assigned_label():
    m = Model("Test")
    v = cast(View, m.add(ArchiType.View, "V"))

    non_standard = m.add(ArchiType.ApplicationComponent, "App1")
    non_standard.set_profile("Risk")
    v.add(non_standard, x=10, y=10, w=120, h=55)

    standard = m.add(ArchiType.ApplicationComponent, "App2")
    standard.set_profile("ApplicationComponent")
    v.add(standard, x=150, y=10, w=120, h=55)

    unstereotyped = m.add(ArchiType.ApplicationComponent, "App3")
    v.add(unstereotyped, x=290, y=10, w=120, h=55)

    svg = v.to_svg(show_stereotypes=True)

    assert "«Risk»" in svg
    assert "«ApplicationComponent»" in svg
    assert svg.count("«") == 2
