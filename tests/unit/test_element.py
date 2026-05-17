import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate import Element as PackageElement
from src.pyArchimate.element import Element
from src.pyArchimate.exceptions import ArchimateConceptTypeError
from src.pyArchimate.model import Model

# ---------------------------------------------------------------------------
# Import sanity
# ---------------------------------------------------------------------------


def test_element_importable_from_element_module():
    assert Element


def test_element_exported_from_package():
    assert PackageElement is Element


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def model_with_elem():
    m = Model("elem-test")
    e = m.add(ArchiType.ApplicationComponent, "App", desc="desc")
    return m, e


# ---------------------------------------------------------------------------
# Element.__init__ error branches
# ---------------------------------------------------------------------------


def test_element_invalid_type_raises():
    with pytest.raises(ArchimateConceptTypeError):
        Element(elem_type="NotAType", name="x")


def test_element_relationship_type_raises():
    with pytest.raises(ArchimateConceptTypeError):
        Element(elem_type=ArchiType.Serving, name="x")


def test_element_invalid_parent_raises():
    with pytest.raises(ValueError):
        Element(elem_type=ArchiType.ApplicationComponent, name="x", parent=object())


# ---------------------------------------------------------------------------
# Element.type setter
# ---------------------------------------------------------------------------


def test_element_type_setter_valid(model_with_elem):
    _, e = model_with_elem
    e.type = ArchiType.ApplicationService
    assert e.type == ArchiType.ApplicationService


def test_element_type_setter_invalid_raises(model_with_elem):
    _, e = model_with_elem
    with pytest.raises(ValueError):
        e.type = "NotAType"


def test_element_type_setter_none_is_noop(model_with_elem):
    _, e = model_with_elem
    original = e.type
    e.type = None
    assert e.type == original


# ---------------------------------------------------------------------------
# Element.prop / remove_prop
# ---------------------------------------------------------------------------


def test_element_prop_set_and_get(model_with_elem):
    _, e = model_with_elem
    e.prop("color", "blue")
    assert e.prop("color") == "blue"


def test_element_prop_missing_returns_none(model_with_elem):
    _, e = model_with_elem
    assert e.prop("nope") is None


def test_element_remove_prop(model_with_elem):
    _, e = model_with_elem
    e.prop("x", "1")
    e.remove_prop("x")
    assert e.prop("x") is None


def test_element_remove_prop_missing_is_noop(model_with_elem):
    _, e = model_with_elem
    e.remove_prop("ghost")  # must not raise


# ---------------------------------------------------------------------------
# Element.profile_name / profile_id / set_profile / reset_profile
# ---------------------------------------------------------------------------


def test_element_profile_name_none_when_unset(model_with_elem):
    _, e = model_with_elem
    assert e.profile_name is None


def test_element_profile_id_none_when_unset(model_with_elem):
    _, e = model_with_elem
    assert e.profile_id is None


def test_element_set_profile_creates_profile(model_with_elem):
    _, e = model_with_elem
    e.set_profile("MyProfile")
    assert e.profile_id is not None


def test_element_set_profile_reuses_existing(model_with_elem):
    m, e = model_with_elem
    m.add_profile(name="Existing", concept=ArchiType.ApplicationComponent)
    e.set_profile("Existing")
    # profile_name returns model profile name looked up by uuid — uuid stored is the profile name here
    assert e._profile is not None


def test_element_reset_profile(model_with_elem):
    _, e = model_with_elem
    e.set_profile("P")
    e.reset_profile()
    assert e.profile_name is None


def test_element_profile_name_found_after_set(model_with_elem):
    _, e = model_with_elem
    e.set_profile("Named")
    assert e.profile_name is not None


# ---------------------------------------------------------------------------
# Element.delete
# ---------------------------------------------------------------------------


def test_element_delete_removes_from_model(model_with_elem):
    m, e = model_with_elem
    elem_id = e.uuid
    e.delete()
    assert elem_id not in m.elems_dict


def test_element_in_rels(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, "Svc")
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(dst.in_rels()) == 1


def test_element_in_rels_filtered(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, "Svc")
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(dst.in_rels(ArchiType.Serving)) == 1


def test_element_out_rels(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, "Svc")
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(e.out_rels()) == 1


def test_element_out_rels_filtered(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, "Svc")
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(e.out_rels(ArchiType.Serving)) == 1


def test_element_rels(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, "Svc")
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(e.rels()) == 1


def test_element_rels_filtered(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, "Svc")
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(e.rels(ArchiType.Serving)) == 1


def test_element_remove_folder(model_with_elem):
    _, e = model_with_elem
    e.folder = "/app"
    e.remove_folder()
    assert e.folder is None


def test_element_merge_same_type(model_with_elem):
    m, e = model_with_elem
    other = m.add(ArchiType.ApplicationComponent, "Other", desc="other desc")
    e.prop("color", "red")
    e.merge(other, merge_props=True)
    # other should be deleted after merge
    assert other.uuid not in m.elems_dict


def test_element_merge_wrong_type_raises(model_with_elem):
    m, e = model_with_elem
    other = m.add(ArchiType.ApplicationService, "Svc")
    with pytest.raises(ValueError):
        e.merge(other)


def test_element_merge_without_props(model_with_elem):
    m, e = model_with_elem
    other = m.add(ArchiType.ApplicationComponent, "Other2")
    e.merge(other, merge_props=False)
    assert other.uuid not in m.elems_dict


@pytest.fixture()
def sample_model():
    return Model("sample")


def test_element_delete_removes_related_relationships():
    m = Model("del-test")
    src = m.add(ArchiType.ApplicationComponent, "A")
    dst = m.add(ArchiType.ApplicationService, "B")
    rel = m.add_relationship(ArchiType.Serving, source=src, target=dst)
    rel_id = rel.uuid
    dst.delete()
    assert rel_id not in m.rels_dict


# ---------------------------------------------------------------------------
# ArchiMate 3.x Compliance: BusinessInteraction
# ---------------------------------------------------------------------------


def test_create_business_interaction():
    """Test that BusinessInteraction element can be created without validation errors."""
    m = Model("bi-test")
    bi = m.add(ArchiType.BusinessInteraction, "Customer Service Interaction", desc="Interaction element")
    assert bi is not None
    assert bi.name == "Customer Service Interaction"
    assert bi.type == ArchiType.BusinessInteraction
    assert bi.uuid in m.elems_dict


def test_business_interaction_has_properties():
    """Test that BusinessInteraction element can store properties."""
    m = Model("bi-props-test")
    bi = m.add(ArchiType.BusinessInteraction, "Test BI")
    bi.prop("owner", "business-team")
    assert bi.props["owner"] == "business-team"


def test_business_interaction_can_relate_to_other_elements():
    """Test that BusinessInteraction can participate in relationships."""
    m = Model("bi-rel-test")
    bi = m.add(ArchiType.BusinessInteraction, "Interaction")
    actor = m.add(ArchiType.BusinessActor, "Actor")
    rel = m.add_relationship(ArchiType.Association, source=bi, target=actor)
    assert rel is not None
    assert rel.source.uuid == bi.uuid
    assert rel.target.uuid == actor.uuid


# ---------------------------------------------------------------------------
# ArchiMate 3.x Compliance: Viewpoint Assignment
# ---------------------------------------------------------------------------


def test_element_viewpoint_assignment(sample_model):
    elem = sample_model.add(ArchiType.BusinessActor, "Test Actor")
    elem.assign_viewpoint("stakeholder")
    assert "stakeholder" in elem.viewpoints


def test_element_viewpoint_removal(sample_model):
    elem = sample_model.add(ArchiType.BusinessActor, "Test Actor")
    elem.assign_viewpoint("stakeholder")
    elem.remove_viewpoint("stakeholder")
    assert "stakeholder" not in elem.viewpoints


def test_multi_viewpoint_assignment(sample_model):
    elem = sample_model.add(ArchiType.BusinessActor, "Test Actor")
    elem.assign_viewpoint("stakeholder")
    elem.assign_viewpoint("capability")
    assert "stakeholder" in elem.viewpoints
    assert "capability" in elem.viewpoints


def test_invalid_viewpoint_raises(sample_model):
    elem = sample_model.add(ArchiType.BusinessActor, "Test Actor")
    with pytest.raises(ValueError):
        elem.assign_viewpoint("not_a_real_viewpoint")


def test_element_viewpoint_no_duplicate(sample_model):
    """Assigning the same viewpoint twice does not create a duplicate."""
    elem = sample_model.add(ArchiType.BusinessActor, "Test Actor")
    elem.assign_viewpoint("stakeholder")
    elem.assign_viewpoint("stakeholder")
    assert elem.viewpoints.count("stakeholder") == 1


def test_element_remove_viewpoint_silent_on_unknown(sample_model):
    """Removing a viewpoint not assigned silently ignores the call."""
    elem = sample_model.add(ArchiType.BusinessActor, "Test Actor")
    elem.remove_viewpoint("stakeholder")  # should not raise


# ---------------------------------------------------------------------------
# _normalize_color None path (line 69 in element.py)
# ---------------------------------------------------------------------------


def test_normalize_color_none_returns_none():
    """_normalize_color(None) returns None (line 69)."""
    from src.pyArchimate.element import _normalize_color

    assert _normalize_color(None) is None


# ---------------------------------------------------------------------------
# element.delete with nodes in views (lines 187-188)
# ---------------------------------------------------------------------------


def test_element_delete_removes_nodes_from_views():
    """delete() removes diagram nodes that reference this element (lines 187-188)."""
    m = Model("del-nodes")
    elem = m.add(ArchiType.ApplicationComponent, "App")
    view = m.add(ArchiType.View, "V")
    node = view.add(ref=elem.uuid, x=0, y=0, w=100, h=50)
    node_id = node.uuid
    elem.delete()
    assert node_id not in m.nodes_dict


# ---------------------------------------------------------------------------
# element.delete viewpoint cleanup (line 198)
# ---------------------------------------------------------------------------


def test_element_delete_cleans_up_viewpoints():
    """delete() removes the element UUID from viewpoint tracking sets (line 198)."""
    m = Model("del-vp")
    elem = m.add(ArchiType.BusinessActor, "Actor")
    elem.assign_viewpoint("stakeholder")
    elem_id = elem.uuid
    elem.delete()
    # The element's uuid should no longer be in the viewpoint tracking set
    assert elem_id not in m._viewpoint_elements.get("stakeholder", set())


# ---------------------------------------------------------------------------
# element.merge when other is SOURCE of a relationship (line 386)
# ---------------------------------------------------------------------------


def test_element_merge_reassigns_source_relationship():
    """merge() reassigns relationships where other is the source (line 386)."""
    m = Model("merge-src")
    target = m.add(ArchiType.ApplicationComponent, "Target")
    other = m.add(ArchiType.ApplicationComponent, "Other")
    svc = m.add(ArchiType.ApplicationService, "Svc")
    # other is SOURCE of this relationship
    rel = m.add_relationship(ArchiType.Serving, source=other, target=svc)
    rel_id = rel.uuid
    # Merge other into target — the relationship source should now be target
    target.merge(other)
    assert m.rels_dict[rel_id].source.uuid == target.uuid


# ---------------------------------------------------------------------------
# Extra coverage tests
# ---------------------------------------------------------------------------


def test_is_valid_uuid_invalid_string():
    """Line 35-36: Catch ValueError in _is_valid_uuid."""
    from src.pyArchimate.element import _is_valid_uuid

    assert _is_valid_uuid("not-a-uuid") is False


def test_normalize_color_variants():
    """Lines 70-78: _normalize_color logic coverage."""
    from src.pyArchimate.element import _normalize_color

    # Strip whitespace
    assert _normalize_color(" #ff0000 ") == "#ff0000"
    # Invalid hex
    with pytest.raises(ValueError, match="Invalid hex color"):
        _normalize_color("#GGGGGG")
    # Named color
    assert _normalize_color("red") == "#ff0000"
    # Unknown color
    with pytest.raises(ValueError, match="Unknown color"):
        _normalize_color("banana")


def test_element_delete_orphans_children():
    """Lines 202-206, 208: verify orphaning logic in delete()."""
    m = Model("m")
    p = m.add(ArchiType.ApplicationComponent, "Parent")
    c = m.add(ArchiType.ApplicationComponent, "Child")
    m.add_child(p.uuid, c.uuid)

    parent = m.get_parent(c.uuid)
    assert parent is not None
    assert parent.uuid == p.uuid

    p.delete()

    assert c.uuid in m.elems_dict
    assert m.get_parent(c.uuid) is None
    assert p.uuid not in m._element_children


def test_element_delete_removes_from_parent():
    """Lines 212-214: verify removal from parent's children in delete()."""
    m = Model("m")
    p = m.add(ArchiType.ApplicationComponent, "Parent")
    c = m.add(ArchiType.ApplicationComponent, "Child")
    m.add_child(p.uuid, c.uuid)

    c.delete()
    assert c.uuid not in m._element_children.get(p.uuid, set())


def test_element_merge_updates_nodes_and_rels_extended():
    """Lines 379, 383, 354-355: merge coverage."""
    m = Model("m")
    e1 = m.add(ArchiType.ApplicationComponent, "E1")
    e2 = m.add(ArchiType.ApplicationComponent, "E2")
    e1.prop("p1", "v1")
    e2.prop("p2", "v2")

    # Add a view with a node referring to e2
    v = m.add(ArchiType.View, "V")
    n = v.add(ref=e2.uuid, x=0, y=0, w=100, h=50)

    # add_relationship(rel_type, source, target)
    rel = m.add_relationship(ArchiType.Association, e1.uuid, e2.uuid)

    e1.merge(e2, merge_props=True)

    assert e1.prop("p2") == "v2"
    assert n.ref == e1.uuid
    assert rel.target.uuid == e1.uuid


def test_parent_uuid_property():
    """Line 501: parent_uuid coverage."""
    m = Model("m")
    p = m.add(ArchiType.ApplicationComponent, "Parent")
    c = m.add(ArchiType.ApplicationComponent, "Child")
    m.add_child(p.uuid, c.uuid)
    assert c.parent_uuid == p.uuid


def test_visual_style_setters():
    """Lines 510-559, 571-578: visual style setters coverage."""
    e = Element(ArchiType.ApplicationComponent, "E")

    # Fill color
    e.set_fill_color(None)
    assert e.get_fill_color() is None
    e.set_fill_color("red")
    assert e.get_fill_color() == "#ff0000"

    # Line color
    e.set_line_color(None)
    assert e.get_line_color() is None
    e.set_line_color("blue")
    assert e.get_line_color() == "#0000ff"

    # Line width
    e.set_line_width(None)
    assert e.get_line_width() is None
    e.set_line_width(5.0)
    assert e.get_line_width() == pytest.approx(5.0)
    with pytest.raises(TypeError):
        e.set_line_width("string")
    with pytest.raises(ValueError):
        e.set_line_width(-1)

    # Transparency
    e.set_transparency(None)
    assert e.get_transparency() is None
    e.set_transparency(0.5)
    assert e.get_transparency() == pytest.approx(0.5)
    with pytest.raises(TypeError):
        e.set_transparency("string")
    with pytest.raises(ValueError):
        e.set_transparency(1.5)

    # Multi setter
    e.set_visual_style(fill_color="green", line_width=10.0)
    assert e.get_fill_color() == "#008000"
    assert e.get_line_width() == pytest.approx(10.0)


def test_visual_style_getters_and_reset():
    """Lines 586-625: visual style getters and reset coverage."""
    e = Element(ArchiType.ApplicationComponent, "E")
    e.set_visual_style(fill_color="red", line_color="blue", line_width=2.0, transparency=0.8)

    assert e.get_fill_color() == "#ff0000"
    assert e.get_line_color() == "#0000ff"
    assert e.get_line_width() == pytest.approx(2.0)
    assert e.get_transparency() == pytest.approx(0.8)

    style = e.get_visual_style()
    assert style["fillColor"] == "#ff0000"

    e.reset_visual_style()
    assert e.get_fill_color() is None
    assert len(e.get_visual_style()) == 0


def test_junction_type_methods():
    """Lines 635-651: junction type coverage."""
    e = Element(ArchiType.Junction, "J")

    e.set_junction_type(None)
    assert e.get_junction_type() is None

    e.set_junction_type(" AND ")
    assert e.get_junction_type() == "and"

    with pytest.raises(ValueError, match="Invalid junction type"):
        e.set_junction_type("invalid")
