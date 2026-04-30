from lxml import etree

from src.pyArchimate.writers.archiWriter import archi_writer
from tests._helpers import model_with_views, simple_archimate_model


def test_archi_writer_produces_archimate_document(tmp_path):
    model = simple_archimate_model()
    target = tmp_path / 'archi_output.archimate'
    archi_writer(model, str(target))
    assert target.exists()
    root = etree.parse(str(target)).getroot()
    assert root.find('folder') is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
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


def test_archi_writer_exports_business_interaction(tmp_path):
    """Test that BusinessInteraction elements are exported correctly to .archimate format."""
    from src.pyArchimate import ArchiType
    model = simple_archimate_model('bi-export-test')
    bi = model.add(ArchiType.BusinessInteraction, 'Customer Interaction', desc='Handles customers')
    bi.prop('category', 'external')
    target = tmp_path / 'archi_bi_export.archimate'
    archi_writer(model, str(target))
    assert target.exists()
    root = etree.parse(str(target)).getroot()
    # Find BusinessInteraction element
    bi_elements = root.findall(".//element[@xsi:type='archimate:BusinessInteraction']",
                               namespaces={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
    assert len(bi_elements) > 0
    bi_elem = bi_elements[0]
    assert bi_elem.get('name') == 'Customer Interaction'
    doc = bi_elem.find('documentation')
    assert doc is not None
    assert doc.text == 'Handles customers'
