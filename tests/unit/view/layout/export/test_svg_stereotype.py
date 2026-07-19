"""Unit tests for SVG stereotype rendering."""

from typing import cast

import pytest
from defusedxml import ElementTree as ET

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import View
from src.pyArchimate.view.layout.export import SVGExportService


@pytest.fixture()
def view_with_profiled_node():
    m = Model("Test")
    v = cast(View, m.add(ArchiType.View, "V"))
    elem = m.add(ArchiType.ApplicationComponent, "MyApp")
    elem.set_profile("Threat")
    node = v.add(elem, x=10, y=10, w=120, h=55)
    return v, node


@pytest.fixture()
def view_with_unprofiled_node():
    m = Model("Test")
    v = cast(View, m.add(ArchiType.View, "V"))
    elem = m.add(ArchiType.ApplicationComponent, "Plain")
    node = v.add(elem, x=10, y=10, w=120, h=55)
    return v, node


def _svg_texts(svg_string: str) -> list[str]:
    """Return all text content strings from <text> elements in the SVG."""
    root = ET.fromstring(svg_string)
    ns = "http://www.w3.org/2000/svg"
    return [el.text or "" for el in root.iter(f"{{{ns}}}text")]


def _svg_text_elements(svg_string: str):
    """Return all <text> ET elements from the SVG."""
    root = ET.fromstring(svg_string)
    ns = "http://www.w3.org/2000/svg"
    return list(root.iter(f"{{{ns}}}text"))


# ---------------------------------------------------------------------------
# Increment 1 — SVGExportService accepts show_stereotypes flag
# ---------------------------------------------------------------------------


def test_svg_export_service_accepts_show_stereotypes_flag():
    svc = SVGExportService(show_stereotypes=True)
    assert svc.show_stereotypes is True


def test_svg_export_service_show_stereotypes_defaults_false():
    svc = SVGExportService()
    assert svc.show_stereotypes is False


# ---------------------------------------------------------------------------
# Increment 2 — no guillemet text when show_stereotypes is False
# ---------------------------------------------------------------------------


def test_no_stereotype_text_when_flag_false(view_with_profiled_node):
    v, _ = view_with_profiled_node
    svc = SVGExportService(show_stereotypes=False)
    svg = svc.to_svg(v)
    assert not any("«" in t for t in _svg_texts(svg))


# ---------------------------------------------------------------------------
# Increment 3 — stereotype <text> appears when show_stereotypes is True
# ---------------------------------------------------------------------------


def test_stereotype_text_present_when_flag_true(view_with_profiled_node):
    v, _ = view_with_profiled_node
    svc = SVGExportService(show_stereotypes=True)
    svg = svc.to_svg(v)
    assert any("«Threat»" in t for t in _svg_texts(svg))


# ---------------------------------------------------------------------------
# Increment 4 — stereotype text is smaller and italic
# ---------------------------------------------------------------------------


def _stereotype_text_element(svg_string: str):
    """Return the <text> element containing «…» or None."""
    for el in _svg_text_elements(svg_string):
        if el.text and "«" in el.text:
            return el
    return None


def test_stereotype_text_is_italic(view_with_profiled_node):
    v, _ = view_with_profiled_node
    svc = SVGExportService(show_stereotypes=True)
    el = _stereotype_text_element(svc.to_svg(v))
    assert el is not None
    assert el.get("font-style") == "italic"


def test_stereotype_text_is_smaller_than_default(view_with_profiled_node):
    v, _ = view_with_profiled_node
    svc = SVGExportService(show_stereotypes=True)
    el = _stereotype_text_element(svc.to_svg(v))
    assert el is not None
    font_size = float(el.get("font-size", "12"))
    assert font_size < 12


# ---------------------------------------------------------------------------
# Increment 5 — no stereotype for nodes with no profile
# ---------------------------------------------------------------------------


def test_no_stereotype_for_unprofiled_node(view_with_unprofiled_node):
    v, _ = view_with_unprofiled_node
    svc = SVGExportService(show_stereotypes=True)
    svg = svc.to_svg(v)
    assert not any("«" in t for t in _svg_texts(svg))


# ---------------------------------------------------------------------------
# Increment 6 — View.to_svg passes show_stereotypes through
# ---------------------------------------------------------------------------


def test_view_to_svg_show_stereotypes_true(view_with_profiled_node):
    v, _ = view_with_profiled_node
    svg = v.to_svg(show_stereotypes=True)
    assert any("«Threat»" in t for t in _svg_texts(svg))


def test_view_to_svg_show_stereotypes_false_by_default(view_with_profiled_node):
    v, _ = view_with_profiled_node
    svg = v.to_svg()
    assert not any("«" in t for t in _svg_texts(svg))
