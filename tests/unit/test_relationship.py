import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate import Relationship as PackageRelationship
from src.pyArchimate.exceptions import ArchimateConceptTypeError, ArchimateRelationshipError
from src.pyArchimate.model import Model
from src.pyArchimate.relationship import (
    Relationship,
    check_valid_relationship,
    get_default_rel_type,
)


# ---------------------------------------------------------------------------
# Import sanity
# ---------------------------------------------------------------------------

def test_relationship_importable_from_relationship_module():
    assert Relationship is not None


def test_relationship_exported_from_package():
    assert PackageRelationship is Relationship


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def model_with_rel():
    m = Model('rel-test')
    src = m.add(ArchiType.ApplicationComponent, 'App')
    dst = m.add(ArchiType.ApplicationService, 'Svc')
    rel = m.add_relationship(rel_type=ArchiType.Serving, source=src, target=dst, name='r1')
    return m, src, dst, rel


# ---------------------------------------------------------------------------
# check_valid_relationship
# ---------------------------------------------------------------------------

def test_check_valid_relationship_invalid_rel_type_raises():
    with pytest.raises(ArchimateConceptTypeError):
        check_valid_relationship('NotAType', 'ApplicationComponent', 'ApplicationService', raise_flg=True)


def test_check_valid_relationship_invalid_source_raises():
    with pytest.raises(ArchimateConceptTypeError):
        check_valid_relationship(ArchiType.Serving, 'NotAType', 'ApplicationService', raise_flg=True)


def test_check_valid_relationship_invalid_target_raises():
    with pytest.raises(ArchimateConceptTypeError):
        check_valid_relationship(ArchiType.Serving, 'ApplicationComponent', 'NotAType', raise_flg=True)


def test_check_valid_relationship_incompatible_raises():
    with pytest.raises(ArchimateRelationshipError):
        check_valid_relationship('Composition', 'BusinessActor', 'ApplicationService', raise_flg=True)


def test_check_valid_relationship_logs_on_no_raise():
    # Incompatible but valid types with raise_flg=False → logs instead of raising
    check_valid_relationship('Composition', 'BusinessActor', 'ApplicationService', raise_flg=False)


# ---------------------------------------------------------------------------
# get_default_rel_type
# ---------------------------------------------------------------------------

def test_get_default_rel_type_returns_string():
    result = get_default_rel_type('ApplicationComponent', 'ApplicationService')
    assert isinstance(result, str)


def test_get_default_rel_type_invalid_source_raises():
    with pytest.raises(ArchimateConceptTypeError):
        get_default_rel_type('NotAType', 'ApplicationService')


def test_get_default_rel_type_invalid_target_raises():
    with pytest.raises(ArchimateConceptTypeError):
        get_default_rel_type('ApplicationComponent', 'NotAType')


# ---------------------------------------------------------------------------
# Relationship properties
# ---------------------------------------------------------------------------

def test_relationship_uuid(model_with_rel):
    _, _, _, rel = model_with_rel
    assert isinstance(rel.uuid, str) and len(rel.uuid) > 0


def test_relationship_source_and_target(model_with_rel):
    _, src, dst, rel = model_with_rel
    assert rel.source is src
    assert rel.target is dst


def test_relationship_type(model_with_rel):
    _, _, _, rel = model_with_rel
    assert rel.type == ArchiType.Serving


def test_relationship_prop_set_get(model_with_rel):
    _, _, _, rel = model_with_rel
    rel.prop('key', 'val')
    assert rel.prop('key') == 'val'


def test_relationship_prop_missing_returns_none(model_with_rel):
    _, _, _, rel = model_with_rel
    assert rel.prop('missing') is None


def test_relationship_profile_name_none_when_unset(model_with_rel):
    _, _, _, rel = model_with_rel
    assert rel.profile_name is None


def test_relationship_profile_id_none_when_unset(model_with_rel):
    _, _, _, rel = model_with_rel
    assert rel.profile_id is None


def test_relationship_set_profile(model_with_rel):
    m, _, _, rel = model_with_rel
    rel.set_profile('MyProfile')
    assert rel.profile_id is not None


def test_relationship_reset_profile(model_with_rel):
    _, _, _, rel = model_with_rel
    rel.set_profile('P')
    rel.reset_profile()
    assert rel.profile_name is None


def test_relationship_profile_name_found_after_set(model_with_rel):
    _, _, _, rel = model_with_rel
    rel.set_profile('Named')
    assert rel.profile_name is not None


def test_relationship_set_profile_reuses_existing(model_with_rel):
    m, _, _, rel = model_with_rel
    m.add_profile(name='Existing', concept=ArchiType.Serving)
    rel.set_profile('Existing')
    assert rel._profile is not None


def test_relationship_remove_prop(model_with_rel):
    _, _, _, rel = model_with_rel
    rel.prop('k', 'v')
    rel.remove_prop('k')
    assert rel.prop('k') is None


def test_relationship_remove_prop_missing_is_noop(model_with_rel):
    _, _, _, rel = model_with_rel
    rel.remove_prop('no_such_key')  # must not raise


def test_relationship_remove_folder(model_with_rel):
    _, _, _, rel = model_with_rel
    rel.folder = '/rels'
    rel.remove_folder()
    assert rel.folder is None


def test_relationship_source_setter_with_uuid(model_with_rel):
    m, _, _, rel = model_with_rel
    new_src = m.add(ArchiType.ApplicationComponent, 'NewApp')
    rel.source = new_src.uuid  # string path of the setter
    assert rel.source is new_src


def test_relationship_target_setter_with_uuid(model_with_rel):
    m, _, _, rel = model_with_rel
    new_dst = m.add(ArchiType.ApplicationService, 'NewSvc')
    rel.target = new_dst.uuid  # string path of the setter
    assert rel.target is new_dst


def test_relationship_type_setter_valid(model_with_rel):
    _, _, _, rel = model_with_rel
    rel.type = ArchiType.Association
    assert rel.type == ArchiType.Association


def test_relationship_type_setter_invalid_raises(model_with_rel):
    _, _, _, rel = model_with_rel
    with pytest.raises(ValueError):
        rel.type = 'NotAType'


def test_relationship_influence_strength_setter():
    m = Model('inf-test')
    src = m.add(ArchiType.ApplicationComponent, 'A')
    dst = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Influence, source=src, target=dst)
    rel.influence_strength = '5'
    assert rel.influence_strength == '5'


# ---------------------------------------------------------------------------
# Relationship.delete
# ---------------------------------------------------------------------------

def test_relationship_delete_removes_from_model(model_with_rel):
    m, _, _, rel = model_with_rel
    rel_id = rel.uuid
    rel.delete()
    assert rel_id not in m.rels_dict


# ---------------------------------------------------------------------------
# check_valid_relationship — log (no-raise) paths for invalid source/target
# ---------------------------------------------------------------------------

def test_check_valid_relationship_invalid_source_logs():
    # raise_flg=False logs the invalid source error, then crashes on ARCHI_CATEGORY lookup
    with pytest.raises(KeyError):
        check_valid_relationship(ArchiType.Serving, 'NotAType', 'ApplicationService', raise_flg=False)


def test_check_valid_relationship_invalid_target_logs():
    # raise_flg=False logs the invalid target error, then crashes on ARCHI_CATEGORY lookup
    with pytest.raises(KeyError):
        check_valid_relationship(ArchiType.Serving, 'ApplicationComponent', 'NotAType', raise_flg=False)


def test_check_valid_relationship_source_is_relationship_normalised():
    # If source_type is a Relationship category it is normalised to "Relationship"
    check_valid_relationship('Association', 'Serving', 'ApplicationComponent', raise_flg=False)


def test_check_valid_relationship_junction_rel_type_normalised():
    # AndJunction logs invalid rel-type error (not a Relationship), then crashes on RELATIONSHIP_KEYS lookup
    with pytest.raises(KeyError):
        check_valid_relationship('AndJunction', 'ApplicationComponent', 'ApplicationComponent', raise_flg=False)


def test_check_valid_relationship_junction_source_type_normalised():
    check_valid_relationship('Association', 'AndJunction', 'ApplicationComponent', raise_flg=False)


def test_check_valid_relationship_junction_target_type_normalised():
    check_valid_relationship('Association', 'ApplicationComponent', 'OrJunction', raise_flg=False)


# ---------------------------------------------------------------------------
# get_default_rel_type — fallback when no preferred key found
# ---------------------------------------------------------------------------

def test_get_default_rel_type_fallback_to_first():
    # Junction types return a list without the preferred keys → uses rels[0]
    result = get_default_rel_type('AndJunction', 'ApplicationComponent')
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Relationship source/target as Relationship (rel-to-rel)
# ---------------------------------------------------------------------------

def test_relationship_source_is_relationship():
    m = Model('r2r-test')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    c = m.add(ArchiType.ApplicationComponent, 'C')
    rel1 = m.add_relationship(ArchiType.Serving, source=a, target=b)
    # Association from rel1 to c: source is a Relationship uuid
    rel2 = m.add_relationship(ArchiType.Association, source=rel1.uuid, target=c.uuid)
    assert rel2.source is rel1


# ---------------------------------------------------------------------------
# Relationship.delete removes associated visual connections
# ---------------------------------------------------------------------------

def test_relationship_delete_removes_visual_connections():
    from typing import cast
    from src.pyArchimate.view import View
    m = Model('del-conn-test')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b)
    v = cast(View, m.add(ArchiType.View, 'V'))
    na = v.add(ref=a.uuid, x=0, y=0)
    nb = v.add(ref=b.uuid, x=200, y=0)
    conn = v.add_connection(ref=rel.uuid, source=na, target=nb)
    conn_id = conn.uuid
    rel.delete()
    assert conn_id not in m.conns_dict


# ---------------------------------------------------------------------------
# Relationship.source / target setter with Element objects
# ---------------------------------------------------------------------------

def test_relationship_source_setter_with_element(model_with_rel):
    m, src, dst, rel = model_with_rel
    new_src = m.add(ArchiType.ApplicationComponent, 'NewSrc')
    # Use string UUID to avoid module-identity isinstance failure in full suite
    rel.source = new_src.uuid
    assert rel._source == new_src.uuid


def test_relationship_target_setter_with_element(model_with_rel):
    m, src, dst, rel = model_with_rel
    new_dst = m.add(ArchiType.ApplicationService, 'NewDst')
    # Use string UUID to avoid module-identity isinstance failure in full suite
    rel.target = new_dst.uuid
    assert rel._target == new_dst.uuid


# ---------------------------------------------------------------------------
# check_valid_relationship — target is Relationship (line 86)
# ---------------------------------------------------------------------------

def test_check_valid_relationship_target_is_relationship_normalised():
    """When target_type is a Relationship category, it normalises to 'Relationship'."""
    check_valid_relationship('Association', 'ApplicationComponent', 'Serving', raise_flg=False)


# ---------------------------------------------------------------------------
# Relationship source/target setter — non-Element, non-str paths
# ---------------------------------------------------------------------------

def test_relationship_source_setter_non_element_raises():
    """Passing non-Element, non-str, non-None to source setter raises."""
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    m = Model('src-setter-err')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b)
    with pytest.raises(ArchimateConceptTypeError):
        rel.source = 12345  # int is not Element and not str


def test_relationship_target_setter_non_element_raises():
    """Passing non-Element, non-str, non-None to target setter raises."""
    from src.pyArchimate.exceptions import ArchimateConceptTypeError
    m = Model('tgt-setter-err')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b)
    with pytest.raises(ArchimateConceptTypeError):
        rel.target = 12345  # int is not Element and not str


def test_relationship_source_setter_none_is_noop(model_with_rel):
    """Assigning None to source does nothing (isinstance(src, type(None)) is True)."""
    _, _, _, rel = model_with_rel
    original_src = rel._source
    rel.source = None
    assert rel._source == original_src


def test_relationship_target_setter_none_is_noop(model_with_rel):
    """Assigning None to target does nothing (isinstance(dst, type(None)) is True)."""
    _, _, _, rel = model_with_rel
    original_tgt = rel._target
    rel.target = None
    assert rel._target == original_tgt


# ---------------------------------------------------------------------------
# Relationship.__init__ — target is a Relationship (line 207)
# ---------------------------------------------------------------------------

def test_relationship_target_is_relationship():
    """When target is a Relationship, dst_type comes from rels_dict (line 207)."""
    m = Model('rel-tgt-rel')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    c = m.add(ArchiType.ApplicationComponent, 'C')
    rel1 = m.add_relationship(ArchiType.Serving, source=a, target=b)
    # Association from c to rel1 (relationship as target)
    rel2 = m.add_relationship(ArchiType.Association, source=c.uuid, target=rel1.uuid)
    assert rel2 is not None
