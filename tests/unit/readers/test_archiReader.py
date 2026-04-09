from pathlib import Path

import pytest
from lxml import etree

from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.readers.archiReader import archi_reader

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


FULL_ARCHI_MODEL = """<?xml version='1.0'?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="folders">
  <property key="foo" value="bar"/>
  <profile name="Test Profile" id="prof-1" conceptType="BusinessInterfaceRelationship"/>
  <folder name="Business">
    <element xsi:type="archimate:BusinessActor" name="Actor One" id="elem-actor">
      <documentation>actor desc</documentation>
      <documentation>actor desc</documentation>
      <property key="foo" value="actor"/>
      <property key="foo" value="actor override"/>
    </element>
  </folder>
</archimate:model>
"""


def test_archi_reader_parses_sample_file():
    fixture_file = FIXTURES / "test.archimate"
    if not fixture_file.exists():
        pytest.skip("test.archimate fixture is not present")
    root = etree.parse(str(fixture_file)).getroot()
    model = Model("archi-sample")
    archi_reader(model, root)
    assert model.name == "test"
    assert len(model.elements) > 0


def test_archi_reader_returns_none_for_non_archimate_root():
    invalid_root = etree.Element("invalid-root")
    model = Model("invalid")
    assert archi_reader(model, invalid_root) is None


def test_archi_reader_handles_properties_and_profiles():
    root = etree.fromstring(FULL_ARCHI_MODEL)
    model = Model("profiles")
    archi_reader(model, root)

    assert model.prop("foo") == "bar"
    assert "elem-actor" in model.elems_dict
    elem = model.elems_dict["elem-actor"]
    assert elem.folder.endswith("/Business")
    assert elem.desc == "actor desc"
