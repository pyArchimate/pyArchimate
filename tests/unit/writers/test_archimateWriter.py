from lxml import etree

from src.pyArchimate import ArchiType
from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.writers.archimateWriter import archimate_writer
from tests._helpers import model_with_views, simple_archimate_model


def test_archimate_writer_produces_valid_xml():
    model = simple_archimate_model()
    xml_content = archimate_writer(model)
    root = etree.fromstring(xml_content.encode("utf-8"))
    ns = {"ns": "http://www.opengroup.org/xsd/archimate/3.0/"}  # NOSONAR — XML namespace URI, not a network request
    assert (
        root.find("ns:elements", namespaces=ns) is not None
    )  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime


def test_archimate_writer_with_views_produces_view_xml():
    model = model_with_views()
    xml_content = archimate_writer(model)
    root = etree.fromstring(xml_content.encode("utf-8"))
    ns = {"ns": "http://www.opengroup.org/xsd/archimate/3.0/"}  # NOSONAR — XML namespace URI, not a network request
    # views element must be present and contain a diagram
    views = root.find("ns:views", namespaces=ns)
    assert views is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    diagrams = views.find("ns:diagrams", namespaces=ns)
    assert diagrams is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    view_el = diagrams.find("ns:view", namespaces=ns)
    assert view_el is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    # nodes must be serialised
    assert (
        view_el.find("ns:node", namespaces=ns) is not None
    )  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime


def test_archimate_writer_with_views_to_file(tmp_path):
    model = model_with_views()
    out = tmp_path / "out.xml"
    archimate_writer(model, str(out))
    assert out.exists()
    assert out.stat().st_size > 0


def test_write_elem_viewpoints_creates_properties_element():
    """_write_elem_viewpoints writes viewpoint slugs as <property> children (lines 70-76).

    Exercises the 'pp is None' branch: element has no existing <properties>, so the
    function must create one before appending the viewpoint property.
    """
    model = Model("vp-no-props")
    elem = model.add(ArchiType.ApplicationComponent, "App")
    elem.assign_viewpoint("business")
    xml_content = archimate_writer(model)
    root = etree.fromstring(xml_content.encode("utf-8"))
    ns = {"ns": "http://www.opengroup.org/xsd/archimate/3.0/"}  # NOSONAR — XML namespace URI, not a network request
    elements_el = root.find("ns:elements", namespaces=ns)
    assert elements_el is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    app_el = elements_el.find("ns:element", namespaces=ns)
    assert app_el is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    props_el = app_el.find("ns:properties", namespaces=ns)
    assert props_el is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    values = [p.findtext("ns:value", namespaces=ns) for p in props_el.findall("ns:property", namespaces=ns)]
    assert "business" in values


def test_write_elem_viewpoints_reuses_existing_properties_element():
    """_write_elem_viewpoints appends to the existing <properties> element (lines 70-76).

    Exercises the 'pp is not None' branch: element already has a <properties> child
    from its own props, so the viewpoint property must be appended to that element.
    """
    model = Model("vp-with-props")
    elem = model.add(ArchiType.ApplicationComponent, "App")
    elem.prop("owner", "team-a")
    elem.assign_viewpoint("stakeholder")
    xml_content = archimate_writer(model)
    root = etree.fromstring(xml_content.encode("utf-8"))
    ns = {"ns": "http://www.opengroup.org/xsd/archimate/3.0/"}  # NOSONAR — XML namespace URI, not a network request
    elements_el = root.find("ns:elements", namespaces=ns)
    assert elements_el is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    app_el = elements_el.find("ns:element", namespaces=ns)
    assert app_el is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    props_els = app_el.findall("ns:properties", namespaces=ns)
    assert len(props_els) == 1, "must reuse the single <properties> element, not create a duplicate"
    values = [p.findtext("ns:value", namespaces=ns) for p in props_els[0].findall("ns:property", namespaces=ns)]
    assert "stakeholder" in values


def test_archimate_writer_exports_business_interaction():
    """Test that BusinessInteraction elements are exported correctly to OpenGroup format."""
    from src.pyArchimate import ArchiType

    model = simple_archimate_model("bi-opengroup-export")
    model.add(ArchiType.BusinessInteraction, "Service Interaction", desc="Service interactions")
    xml_content = archimate_writer(model)
    root = etree.fromstring(xml_content.encode("utf-8"))
    ns = {"ns": "http://www.opengroup.org/xsd/archimate/3.0/"}  # NOSONAR — XML namespace URI, not a network request
    # Find BusinessInteraction element
    elements = root.find("ns:elements", namespaces=ns)
    bi_elements = [
        e
        for e in elements.findall(
            "ns:element", namespaces=ns
        )  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
        if e.get("{http://www.w3.org/2001/XMLSchema-instance}type") == "BusinessInteraction"
    ]  # NOSONAR — XML namespace URI, not a network request
    assert len(bi_elements) > 0
    bi_elem = bi_elements[0]
    name = bi_elem.find("ns:name", namespaces=ns)
    assert name is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    assert name.text == "Service Interaction"
    doc = bi_elem.find("ns:documentation", namespaces=ns)
    assert doc is not None  # NOSONAR — lxml stubs omit Optional; find() returns None at runtime
    assert doc.text == "Service interactions"
