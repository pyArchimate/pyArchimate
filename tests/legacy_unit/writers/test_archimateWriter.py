from lxml import etree

from src.pyArchimate.writers.archimateWriter import archimate_writer
from tests.legacy_unit._helpers import simple_archimate_model


def test_archimate_writer_produces_valid_xml():
    model = simple_archimate_model()
    xml_content = archimate_writer(model)
    root = etree.fromstring(xml_content.encode('utf-8'))
    ns = {'ns': 'http://www.opengroup.org/xsd/archimate/3.0/'}
    assert root.find('ns:elements', namespaces=ns) is not None
