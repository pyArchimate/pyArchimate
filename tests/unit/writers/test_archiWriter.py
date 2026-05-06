import zipfile
from typing import cast

from lxml import etree

from src.pyArchimate import ArchiType, Point
from src.pyArchimate.model import Model
from src.pyArchimate.view import View
from src.pyArchimate.writers.archiWriter import archi_writer
from tests._helpers import model_with_views, simple_archimate_model


def test_archi_writer_produces_archimate_document(tmp_path):
    model = simple_archimate_model()
    target = tmp_path / 'archi_output.archimate'
    archi_writer(model, str(target))
    assert target.exists()
    # Extract model.xml from .archimate ZIP archive
    with zipfile.ZipFile(str(target), 'r') as zf:
        xml_data = zf.read('model.xml')
    root = etree.fromstring(xml_data)
    assert root.find('folder') is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    assert root.findall('.//element')


def test_archi_writer_with_views(tmp_path):
    model = model_with_views()
    target = tmp_path / 'archi_views.archimate'
    archi_writer(model, str(target))
    assert target.exists()
    # Extract model.xml from .archimate ZIP archive
    with zipfile.ZipFile(str(target), 'r') as zf:
        xml_data = zf.read('model.xml')
    root = etree.fromstring(xml_data)
    # should have a Views folder with a diagram element
    all_elements = root.findall('.//element')
    types = [e.get('{http://www.w3.org/2001/XMLSchema-instance}type') for e in all_elements]
    assert any('Diagram' in (t or '') for t in types)


def test_archi_writer_exports_business_interaction(tmp_path):
    """Test that BusinessInteraction elements are exported correctly to .archimate format."""
    model = simple_archimate_model('bi-export-test')
    bi = model.add(ArchiType.BusinessInteraction, 'Customer Interaction', desc='Handles customers')
    bi.prop('category', 'external')
    target = tmp_path / 'archi_bi_export.archimate'
    archi_writer(model, str(target))
    assert target.exists()
    # Extract model.xml from .archimate ZIP archive
    with zipfile.ZipFile(str(target), 'r') as zf:
        xml_data = zf.read('model.xml')
    root = etree.fromstring(xml_data)
    # Find BusinessInteraction element
    bi_elements = root.findall(".//element[@xsi:type='archimate:BusinessInteraction']",
                               namespaces={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})  # NOSONAR — XML namespace URI, not a network request
    assert len(bi_elements) > 0
    bi_elem = bi_elements[0]
    assert bi_elem.get('name') == 'Customer Interaction'
    doc = bi_elem.find('documentation')
    assert doc is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    assert doc.text == 'Handles customers'


# ---------------------------------------------------------------------------
# archiWriter coverage gap tests
# ---------------------------------------------------------------------------

def test_archi_writer_element_with_parent_id(tmp_path):
    """Element with _parent_uuid set writes parentId attribute (line 87)."""
    model = Model('parent-id-test')
    parent = model.add(ArchiType.ApplicationComponent, 'Parent')
    child = model.add(ArchiType.ApplicationComponent, 'Child')
    model.add_child(parent.uuid, child.uuid)
    target = tmp_path / 'parent_id.archimate'
    xml_str = archi_writer(model, str(target))
    assert 'parentId' in xml_str


def test_archi_writer_element_with_visual_style(tmp_path):
    """Element with _visual_style populated writes visual properties (line 100)."""
    model = simple_archimate_model('vs-test')
    elem = model.elements[0]
    elem.set_fill_color('#ff0000')
    target = tmp_path / 'vs.archimate'
    xml_str = archi_writer(model, str(target))
    assert 'fillColor' in xml_str


def test_archi_writer_element_with_viewpoint(tmp_path):
    """Element with viewpoints writes viewpoint property (line 102)."""
    model = simple_archimate_model('vp-test')
    elem = model.elements[0]
    elem.assign_viewpoint('business')
    target = tmp_path / 'vp.archimate'
    xml_str = archi_writer(model, str(target))
    assert 'viewpoint' in xml_str


def test_archi_writer_connection_font_color(tmp_path):
    """Connection with font_color writes fontColor attribute (line 172)."""
    model = Model('conn-font')
    a = model.add(ArchiType.ApplicationComponent, 'A')
    b = model.add(ArchiType.ApplicationService, 'B')
    rel = model.add_relationship(ArchiType.Serving, source=a, target=b)
    view = cast(View, model.add(ArchiType.View, 'V'))
    na = view.add(ref=a.uuid, x=0, y=0, w=100, h=50)
    nb = view.add(ref=b.uuid, x=200, y=0, w=100, h=50)
    conn = view.add_connection(ref=rel.uuid, source=na, target=nb)
    conn.font_color = '#ff0000'
    conn.font_name = 'Arial'
    conn.font_size = 12
    target = tmp_path / 'conn_font.archimate'
    xml_str = archi_writer(model, str(target))
    assert 'fontColor' in xml_str


def test_archi_writer_connection_bendpoint_offsets_use_node_origin(tmp_path):
    """Bendpoint offsets are written relative to the node top-left for Archi import."""
    model = Model('conn-bp-origin')
    a = model.add(ArchiType.ApplicationComponent, 'A')
    b = model.add(ArchiType.ApplicationService, 'B')
    rel = model.add_relationship(ArchiType.Serving, source=a, target=b)
    view = cast(View, model.add(ArchiType.View, 'V'))
    na = view.add(ref=a.uuid, x=10, y=10, w=100, h=50)
    nb = view.add(ref=b.uuid, x=210, y=10, w=100, h=50)
    conn = view.add_connection(ref=rel.uuid, source=na, target=nb)
    conn.add_bendpoint(Point(110, 50))
    target = tmp_path / 'conn_bp_origin.archimate'
    xml_str = archi_writer(model, str(target))
    assert 'startX="100"' in xml_str
    assert 'startY="40"' in xml_str
    assert 'endX="-100"' in xml_str
    assert 'endY="40"' in xml_str


def test_archi_writer_node_icon_color_and_gradient(tmp_path):
    """Node with icon_color and gradient writes feature elements (lines 216, 219)."""
    model = Model('icon-grad')
    a = model.add(ArchiType.ApplicationComponent, 'A')
    view = cast(View, model.add(ArchiType.View, 'V'))
    node = view.add(ref=a.uuid, x=0, y=0, w=100, h=50)
    node.icon_color = '#0000ff'
    node.gradient = 'top'
    target = tmp_path / 'icon_grad.archimate'
    xml_str = archi_writer(model, str(target))
    assert 'iconColor' in xml_str
    assert 'gradient' in xml_str


def test_archi_writer_node_border_type(tmp_path):
    """Node with border_type writes borderType attribute (line 246)."""
    model = Model('border-type')
    a = model.add(ArchiType.ApplicationComponent, 'A')
    view = cast(View, model.add(ArchiType.View, 'V'))
    node = view.add(ref=a.uuid, x=0, y=0, w=100, h=50)
    node.border_type = '1'
    target = tmp_path / 'border.archimate'
    xml_str = archi_writer(model, str(target))
    assert 'borderType' in xml_str


def test_archi_writer_view_with_primary_viewpoint(tmp_path):
    """View with primary_viewpoint writes viewpoint attribute (line 289)."""
    model = Model('vp-view')
    view = cast(View, model.add(ArchiType.View, 'V'))
    view.set_primary_viewpoint('business')
    target = tmp_path / 'vp_view.archimate'
    xml_str = archi_writer(model, str(target))
    assert 'viewpoint' in xml_str


def test_archi_writer_preserves_technology_and_physical_folder(tmp_path):
    """Folder names like 'Technology & Physical' should not be treated as a Technology prefix."""
    model = Model('tech-folder')
    elem = model.add(ArchiType.Equipment, 'Rack')
    elem.folder = '/Technology & Physical'
    target = tmp_path / 'tech_folder.archimate'
    xml_str = archi_writer(model, str(target))
    assert target.exists()
    assert 'Rack' in xml_str


def test_archi_writer_propagates_target_connections_to_group_ancestors(tmp_path):
    """Connections into nested nodes should be listed on enclosing groups as well."""
    model = Model('group-target-connections')
    src_elem = model.add(ArchiType.ApplicationComponent, 'Source')
    tgt_elem = model.add(ArchiType.ApplicationService, 'Target')
    rel = model.add_relationship(ArchiType.Serving, source=src_elem, target=tgt_elem)

    view = cast(View, model.add(ArchiType.View, 'V'))
    src = view.add(ref=src_elem.uuid, x=0, y=0, w=100, h=50)
    group = view.add(ref=None, node_type='Container', label='Group', x=200, y=0, w=220, h=140)
    tgt = group.add(ref=tgt_elem.uuid, x=20, y=20, w=100, h=50)
    conn = view.add_connection(ref=rel.uuid, source=src, target=tgt)

    target = tmp_path / 'group_target_connections.archimate'
    xml_str = archi_writer(model, str(target))
    assert target.exists()

    root = etree.fromstring(xml_str.encode('utf-8'))
    group_node = root.find(".//child[@name='Group']")
    assert group_node is not None
    tgt_node = root.find(f".//child[@id='{tgt.uuid}']")
    assert tgt_node is not None

    assert conn.uuid in (group_node.get('targetConnections') or '')
    assert conn.uuid in (tgt_node.get('targetConnections') or '')
