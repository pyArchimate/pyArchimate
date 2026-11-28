"""Unit tests for automatic non-standard stereotype labeling (US4, FR-015-FR-018)."""

from typing import cast

import pytest
from defusedxml import ElementTree as ET

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import View
from src.pyArchimate.view.layout.export import SVGExportService


def _svg_texts(svg_string: str) -> list[str]:
    root = ET.fromstring(svg_string)
    ns = "http://www.w3.org/2000/svg"
    return [el.text or "" for el in root.iter(f"{{{ns}}}text")]


@pytest.fixture
def model_and_view():
    m = Model("Test")
    v = cast(View, m.add(ArchiType.View, "V"))
    return m, v


def test_non_standard_stereotype_shown_without_display_option(model_and_view):
    m, v = model_and_view
    elem = m.add(ArchiType.ApplicationComponent, "App1")
    elem.set_profile("Risk")
    v.add(elem, x=10, y=10, w=120, h=55)
    svc = SVGExportService()
    svg = svc.to_svg(v)
    assert any("«Risk»" in t for t in _svg_texts(svg))


def test_standard_named_stereotype_not_shown_by_default(model_and_view):
    """A stereotype whose name matches the element's own ArchiType (e.g. a
    profile literally named "ApplicationComponent") is not redundantly labeled.
    """
    m, v = model_and_view
    elem = m.add(ArchiType.ApplicationComponent, "App1")
    elem.set_profile("ApplicationComponent")
    v.add(elem, x=10, y=10, w=120, h=55)
    svc = SVGExportService()
    svg = svc.to_svg(v)
    assert not any("«" in t for t in _svg_texts(svg))


def test_element_with_no_stereotype_not_shown(model_and_view):
    m, v = model_and_view
    elem = m.add(ArchiType.ApplicationComponent, "App1")
    v.add(elem, x=10, y=10, w=120, h=55)
    svc = SVGExportService()
    svg = svc.to_svg(v)
    assert not any("«" in t for t in _svg_texts(svg))


def test_standard_named_stereotype_comparison_is_case_insensitive(model_and_view):
    """ "applicationcomponent" (lowercase) must still be classified as standard-named
    against the "ApplicationComponent" ArchiType value.
    """
    m, v = model_and_view
    elem = m.add(ArchiType.ApplicationComponent, "App1")
    elem.set_profile("applicationcomponent")
    v.add(elem, x=10, y=10, w=120, h=55)
    svc = SVGExportService()
    svg = svc.to_svg(v)
    assert not any("«" in t for t in _svg_texts(svg))


def test_show_stereotypes_flag_still_forces_standard_named_label(model_and_view):
    """FR-018: show_stereotypes=True still force-shows even a standard-named stereotype."""
    m, v = model_and_view
    elem = m.add(ArchiType.ApplicationComponent, "App1")
    elem.set_profile("ApplicationComponent")
    v.add(elem, x=10, y=10, w=120, h=55)
    svc = SVGExportService(show_stereotypes=True)
    svg = svc.to_svg(v)
    assert any("«ApplicationComponent»" in t for t in _svg_texts(svg))
