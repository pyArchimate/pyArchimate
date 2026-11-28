"""Regression test (FR-013): Element.set_line_color()/set_line_width()/transparency
behavior and persistence are unchanged by the stereotype-color feature."""

import tempfile

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


def test_line_color_width_transparency_setters_unaffected():
    m = Model("VisualStyleTest")
    elem = m.add(ArchiType.BusinessActor, "A1")
    elem.set_line_color("#0066cc")
    elem.set_line_width(2.5)
    elem.set_transparency(0.5)

    assert elem.get_line_color() == "#0066cc"
    assert elem.get_line_width() == 2.5
    assert elem.get_transparency() == 0.5


def test_line_color_width_transparency_unaffected_by_stereotype_assignment():
    m = Model("VisualStyleTest")
    profile = m.add_profile(name="Risk", concept=ArchiType.BusinessActor)
    profile.fill_color = "#F2A900"
    elem = m.add(ArchiType.BusinessActor, "A1")
    elem.set_profile("Risk")
    elem.set_line_color("#0066cc")
    elem.set_line_width(2.5)
    elem.set_transparency(0.5)

    assert elem.get_line_color() == "#0066cc"
    assert elem.get_line_width() == 2.5
    assert elem.get_transparency() == 0.5


def test_visual_style_persists_unchanged_through_archi_native_roundtrip():
    m1 = Model("VisualStyleTest")
    elem = m1.add(ArchiType.BusinessActor, "A1")
    elem.set_line_color("#0066cc")
    elem.set_line_width(2.5)
    elem.set_transparency(0.5)

    with tempfile.NamedTemporaryFile(suffix=".archimate", delete=False) as f:
        path = f.name
    m1.write(path)

    m2 = Model("VisualStyleTest-reload")
    m2.read(path)
    elem2 = m2.elems_dict[elem.uuid]
    assert elem2.get_line_color() == "#0066cc"
    assert elem2.get_line_width() == 2.5
    assert elem2.get_transparency() == 0.5


def test_visual_style_round_trips_through_exchange_xml_as_generic_props_unchanged():
    """Pre-existing behavior (not introduced or altered by this feature): element-level
    line/width/transparency survive the Exchange XML round trip as generic `props`
    entries, not via `get_line_color()` etc. This asserts that pre-existing shape
    is unaffected by the stereotype-color reader/writer additions (FR-013).
    """
    m1 = Model("VisualStyleTest")
    elem = m1.add(ArchiType.BusinessActor, "A1")
    elem.set_line_color("#0066cc")
    elem.set_line_width(2.5)
    elem.set_transparency(0.5)

    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        path = f.name
    m1.write(path)

    m2 = Model("VisualStyleTest-reload")
    m2.read(path)
    elem2 = m2.elems_dict[elem.uuid]
    assert elem2.props.get("lineColor") == "#0066cc"
    assert elem2.props.get("lineWidth") == "2.5"
    assert elem2.props.get("transparency") == "0.5"
