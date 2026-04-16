import pytest

from src.pyArchimate import ArchiType, Element as PackageElement
from src.pyArchimate.element import Element
from src.pyArchimate.exceptions import ArchimateConceptTypeError
from src.pyArchimate.model import Model


# ---------------------------------------------------------------------------
# Import sanity
# ---------------------------------------------------------------------------

def test_element_importable_from_element_module():
    assert Element is not None


def test_element_exported_from_package():
    assert PackageElement is Element


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def model_with_elem():
    m = Model('elem-test')
    e = m.add(ArchiType.ApplicationComponent, 'App', desc='desc')
    return m, e


# ---------------------------------------------------------------------------
# Element.__init__ error branches
# ---------------------------------------------------------------------------

def test_element_invalid_type_raises():
    with pytest.raises(ArchimateConceptTypeError):
        Element(elem_type='NotAType', name='x')


def test_element_relationship_type_raises():
    with pytest.raises(ArchimateConceptTypeError):
        Element(elem_type=ArchiType.Serving, name='x')


def test_element_invalid_parent_raises():
    with pytest.raises(ValueError):
        Element(elem_type=ArchiType.ApplicationComponent, name='x', parent=object())


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
        e.type = 'NotAType'


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
    e.prop('color', 'blue')
    assert e.prop('color') == 'blue'


def test_element_prop_missing_returns_none(model_with_elem):
    _, e = model_with_elem
    assert e.prop('nope') is None


def test_element_remove_prop(model_with_elem):
    _, e = model_with_elem
    e.prop('x', '1')
    e.remove_prop('x')
    assert e.prop('x') is None


def test_element_remove_prop_missing_is_noop(model_with_elem):
    _, e = model_with_elem
    e.remove_prop('ghost')  # must not raise


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
    m, e = model_with_elem
    e.set_profile('MyProfile')
    assert e.profile_id is not None


def test_element_set_profile_reuses_existing(model_with_elem):
    m, e = model_with_elem
    m.add_profile(name='Existing', concept=ArchiType.ApplicationComponent)
    e.set_profile('Existing')
    # profile_name returns model profile name looked up by uuid — uuid stored is the profile name here
    assert e._profile is not None


def test_element_reset_profile(model_with_elem):
    _, e = model_with_elem
    e.set_profile('P')
    e.reset_profile()
    assert e.profile_name is None


def test_element_profile_name_found_after_set(model_with_elem):
    _, e = model_with_elem
    e.set_profile('Named')
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
    dst = m.add(ArchiType.ApplicationService, 'Svc')
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(dst.in_rels()) == 1


def test_element_in_rels_filtered(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, 'Svc')
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(dst.in_rels(ArchiType.Serving)) == 1


def test_element_out_rels(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, 'Svc')
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(e.out_rels()) == 1


def test_element_out_rels_filtered(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, 'Svc')
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(e.out_rels(ArchiType.Serving)) == 1


def test_element_rels(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, 'Svc')
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(e.rels()) == 1


def test_element_rels_filtered(model_with_elem):
    m, e = model_with_elem
    dst = m.add(ArchiType.ApplicationService, 'Svc')
    m.add_relationship(ArchiType.Serving, source=e, target=dst)
    assert len(e.rels(ArchiType.Serving)) == 1


def test_element_remove_folder(model_with_elem):
    _, e = model_with_elem
    e.folder = '/app'
    e.remove_folder()
    assert e.folder is None


def test_element_merge_same_type(model_with_elem):
    m, e = model_with_elem
    other = m.add(ArchiType.ApplicationComponent, 'Other', desc='other desc')
    e.prop('color', 'red')
    e.merge(other, merge_props=True)
    # other should be deleted after merge
    assert other.uuid not in m.elems_dict


def test_element_merge_wrong_type_raises(model_with_elem):
    m, e = model_with_elem
    other = m.add(ArchiType.ApplicationService, 'Svc')
    with pytest.raises(ValueError):
        e.merge(other)


def test_element_merge_without_props(model_with_elem):
    m, e = model_with_elem
    other = m.add(ArchiType.ApplicationComponent, 'Other2')
    e.merge(other, merge_props=False)
    assert other.uuid not in m.elems_dict


def test_element_delete_removes_related_relationships():
    m = Model('del-test')
    src = m.add(ArchiType.ApplicationComponent, 'A')
    dst = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Serving, source=src, target=dst)
    rel_id = rel.uuid
    dst.delete()
    assert rel_id not in m.rels_dict
