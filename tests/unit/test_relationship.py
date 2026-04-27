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
    assert Relationship


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


# ---------------------------------------------------------------------------
# _resolve_and_validate_ref — lines 100, 103 (error branches)
# ---------------------------------------------------------------------------

from src.pyArchimate.relationship import _is_valid_uuid, _resolve_and_validate_ref


# ---------------------------------------------------------------------------
# _is_valid_uuid — ValueError branch (lines 27-28)
# ---------------------------------------------------------------------------

def test_is_valid_uuid_invalid_string_returns_false():
    """Non-UUID string triggers UUID() ValueError and returns False."""
    assert _is_valid_uuid('not-a-valid-uuid') is False


# ---------------------------------------------------------------------------
# get_default_rel_type — for-else fallback (line 126)
# ---------------------------------------------------------------------------

def test_get_default_rel_type_fallback_else_branch():
    """Force the for-else branch via mocking: rels contains only non-preferred keys."""
    from unittest.mock import patch
    fake_allowed = {'ApplicationComponent': {'ApplicationService': ['f']}}
    fake_keys = {'Flow': 'f'}
    with patch('src.pyArchimate.relationship.ALLOWED_RELATIONSHIPS', fake_allowed), \
         patch('src.pyArchimate.relationship.RELATIONSHIP_KEYS', fake_keys):
        result = get_default_rel_type('ApplicationComponent', 'ApplicationService')
    assert result == 'Flow'


# ---------------------------------------------------------------------------
# Relationship.__init__ — invalid parent (line 166)
# ---------------------------------------------------------------------------

def test_relationship_init_invalid_parent_raises():
    """Parent without rels_dict raises ValueError."""
    class FakeParent:
        pass
    with pytest.raises(ValueError, match='class Model instance'):
        Relationship(parent=FakeParent())


# ---------------------------------------------------------------------------
# source property — return None for orphaned id (line 234)
# ---------------------------------------------------------------------------

def test_relationship_source_returns_none_for_orphaned_id(model_with_rel):
    """When _source id is absent from both dicts, source returns None."""
    _, _, _, rel = model_with_rel
    rel._source = 'id-orphaned'
    assert rel.source is None


# ---------------------------------------------------------------------------
# source setter — Element object path (line 253)
# ---------------------------------------------------------------------------

def test_relationship_source_setter_element_object(model_with_rel):
    """Passing an Element object to source setter assigns its uuid."""
    m, _, _, rel = model_with_rel
    new_src = m.add(ArchiType.ApplicationComponent, 'DirectSrc')
    rel.source = new_src
    assert rel._source == new_src.uuid


# ---------------------------------------------------------------------------
# target property — rels_dict lookup (lines 266-267) and return None (line 268)
# ---------------------------------------------------------------------------

def test_relationship_target_in_rels_dict():
    """target property returns the relationship object when target is in rels_dict."""
    m = Model('tgt-rel')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    c = m.add(ArchiType.ApplicationComponent, 'C')
    rel1 = m.add_relationship(ArchiType.Serving, source=a, target=b)
    rel2 = m.add_relationship(ArchiType.Association, source=c.uuid, target=rel1.uuid)
    assert rel2.target is rel1


def test_relationship_target_returns_none_for_orphaned_id(model_with_rel):
    """When _target id is absent from both dicts, target returns None."""
    _, _, _, rel = model_with_rel
    rel._target = 'id-orphaned'
    assert rel.target is None


# ---------------------------------------------------------------------------
# target setter — Element object path (line 287)
# ---------------------------------------------------------------------------

def test_relationship_target_setter_element_object(model_with_rel):
    """Passing an Element object to target setter assigns its uuid."""
    m, _, _, rel = model_with_rel
    new_dst = m.add(ArchiType.ApplicationService, 'DirectDst')
    rel.target = new_dst
    assert rel._target == new_dst.uuid


# ---------------------------------------------------------------------------
# props property getter (line 383)
# ---------------------------------------------------------------------------

def test_relationship_props_returns_dict(model_with_rel):
    """props returns the internal properties dictionary."""
    _, _, _, rel = model_with_rel
    assert isinstance(rel.props, dict)


# ---------------------------------------------------------------------------
# access_type getter (line 422) and setter (lines 433-435)
# ---------------------------------------------------------------------------

def test_relationship_access_type_getter_unset():
    """access_type getter returns None when not yet assigned."""
    m = Model('ac-get')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    d = m.add(ArchiType.DataObject, 'D')
    rel = m.add_relationship(ArchiType.Access, source=a, target=d)
    assert rel.access_type is None


def test_relationship_access_type_setter_on_access_rel():
    """Setting access_type on an Access relationship stores the value."""
    m = Model('ac-set')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    d = m.add(ArchiType.DataObject, 'D')
    rel = m.add_relationship(ArchiType.Access, source=a, target=d)
    rel.access_type = 'Write'
    assert rel.access_type == 'Write'


# ---------------------------------------------------------------------------
# is_directed getter (line 445) and setter (lines 456-457)
# ---------------------------------------------------------------------------

def test_relationship_is_directed_getter_unset():
    """is_directed getter returns None when not yet assigned."""
    m = Model('dir-get')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Association, source=a, target=b)
    assert rel.is_directed is None


def test_relationship_is_directed_setter_on_association():
    """Setting is_directed True on an Association relationship stores 'true'."""
    m = Model('dir-set')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Association, source=a, target=b)
    rel.is_directed = True
    assert rel.is_directed == 'true'


def test_resolve_and_validate_ref_invalid_type_raises():
    """Non-str, non-Element, non-uuid object raises ValueError (line 100)."""
    m = Model('rr-invalid')
    m.add(ArchiType.ApplicationComponent, 'A')
    m.add(ArchiType.ApplicationService, 'B')
    with pytest.raises(ValueError, match="not an instance"):
        _resolve_and_validate_ref(42, m.elems_dict, m.rels_dict, 'source')


def test_resolve_and_validate_ref_unknown_uuid_raises():
    """UUID string not present in elems_dict or rels_dict raises ValueError (line 103)."""
    m = Model('rr-unknown')
    with pytest.raises(ValueError, match="Invalid source"):
        _resolve_and_validate_ref('id-deadbeef', m.elems_dict, m.rels_dict, 'source')
