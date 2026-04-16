from lxml import etree

from src.pyArchimate.writers.archiWriter import archi_writer
from tests._helpers import model_with_views, simple_archimate_model


def test_archi_writer_produces_archimate_document(tmp_path):
    model = simple_archimate_model()
    target = tmp_path / 'archi_output.archimate'
    archi_writer(model, str(target))
    assert target.exists()
    root = etree.parse(str(target)).getroot()
    assert root.find('folder') is not None
    assert root.findall('.//element')


def test_archi_writer_with_views(tmp_path):
    model = model_with_views()
    target = tmp_path / 'archi_views.archimate'
    archi_writer(model, str(target))
    assert target.exists()
    root = etree.parse(str(target)).getroot()
    # should have a Views folder with a diagram element
    all_elements = root.findall('.//element')
    types = [e.get('{http://www.w3.org/2001/XMLSchema-instance}type') for e in all_elements]
    assert any('Diagram' in (t or '') for t in types)
