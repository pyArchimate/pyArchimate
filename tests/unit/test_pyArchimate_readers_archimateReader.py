from lxml import etree

from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.readers.archimateReader import archimate_reader

OPEN_MODEL = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>archimate unit</name>
  <documentation>desc text</documentation>
  <elements/>
  <relationships/>
  <views>
    <diagrams/>
  </views>
</model>
"""


def test_archimate_reader_understands_opengroup():
    root = etree.fromstring(OPEN_MODEL)
    model = Model('open')
    archimate_reader(model, root)
    assert model.name == 'archimate unit'
    assert model.desc == 'desc text'
