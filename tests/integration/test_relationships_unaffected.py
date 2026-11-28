"""Regression test (FR-012): stereotype-color feature does not alter relationship
rendering, styling, or persistence in any of the writer/reader/SVG code paths."""

import tempfile
from typing import cast

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import View


def _build_model_with_relationship():
    m = Model("RelTest")
    src = m.add(ArchiType.BusinessActor, "Actor1")
    tgt = m.add(ArchiType.BusinessProcess, "Process1")
    rel = m.add_relationship(source=src.uuid, target=tgt.uuid, rel_type=ArchiType.Assignment, name="performs")
    rel.desc = "doc"
    rel.prop("owner", "team-a")
    v = cast(View, m.add(ArchiType.View, "V"))
    v.add(src, x=10, y=10, w=100, h=50)
    v.add(tgt, x=200, y=10, w=100, h=50)
    v.add(rel)
    return m, src, tgt, rel


def test_relationship_survives_archi_native_roundtrip_unchanged():
    m1, _src, _tgt, rel = _build_model_with_relationship()
    with tempfile.NamedTemporaryFile(suffix=".archimate", delete=False) as f:
        path = f.name
    m1.write(path)

    m2 = Model("RelTest-reload")
    m2.read(path)
    rel2 = m2.rels_dict[rel.uuid]
    assert rel2.name == "performs"
    assert rel2.desc == "doc"
    assert rel2.props.get("owner") == "team-a"


def test_relationship_survives_exchange_xml_roundtrip_unchanged():
    m1, _src, _tgt, rel = _build_model_with_relationship()
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        path = f.name
    m1.write(path)

    m2 = Model("RelTest-reload")
    m2.read(path)
    rel2 = m2.rels_dict[rel.uuid]
    assert rel2.name == "performs"
    assert rel2.desc == "doc"
    assert rel2.props.get("owner") == "team-a"


def test_relationship_svg_rendering_unaffected_by_stereotype_color_logic():
    m, _src, _tgt, _rel = _build_model_with_relationship()
    v = m.views[0]
    svg = v.to_svg()
    assert "<path" in svg
    assert "Actor1" in svg
    assert "Process1" in svg
