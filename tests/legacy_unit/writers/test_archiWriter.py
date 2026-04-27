from lxml import etree

from src.pyArchimate.writers.archiWriter import archi_writer
from tests._helpers import simple_archimate_model


def test_archi_writer_produces_archimate_document(tmp_path):
    model = simple_archimate_model()
    target = tmp_path / 'archi_output.archimate'
    archi_writer(model, str(target))
    assert target.exists()
    root = etree.parse(str(target)).getroot()
    assert root.find('folder') is not None  # NOSONAR — lxml find() returns None at runtime; stubs omit Optional
    assert root.findall('.//element')
