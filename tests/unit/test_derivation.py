"""Unit tests for the derivation-rule table and chain-discovery logic (spec 015)."""

import itertools

import pytest

from src.pyArchimate import Model
from src.pyArchimate.derivation import (
    derive_between,
    derive_pair_type,
    find_chains,
    find_duplicate_relationships,
)

STRUCTURAL_ORDER = ["Composition", "Aggregation", "Assignment", "Realization", "Serving"]
DYNAMIC_TYPES = ["Triggering", "Flow"]
OUT_OF_SCOPE_TYPES = ["Access", "Influence", "Specialization", "Association"]


# --- T003: derive_pair_type rule-table coverage -----------------------------


@pytest.mark.parametrize("leg1_type,leg2_type", list(itertools.product(STRUCTURAL_ORDER, repeat=2)))
def test_derive_pair_type_structural_weakest_link(leg1_type, leg2_type):
    expected_index = max(STRUCTURAL_ORDER.index(leg1_type), STRUCTURAL_ORDER.index(leg2_type))
    expected = STRUCTURAL_ORDER[expected_index]
    assert derive_pair_type(leg1_type, leg2_type) == expected


@pytest.mark.parametrize("leg1_type,leg2_type", list(itertools.product(DYNAMIC_TYPES, repeat=2)))
def test_derive_pair_type_dynamic(leg1_type, leg2_type):
    expected = "Triggering" if leg1_type == leg2_type == "Triggering" else "Flow"
    assert derive_pair_type(leg1_type, leg2_type) == expected


@pytest.mark.parametrize("out_of_scope_type", OUT_OF_SCOPE_TYPES)
def test_derive_pair_type_out_of_scope_leg_yields_none(out_of_scope_type):
    assert derive_pair_type("Assignment", out_of_scope_type) is None
    assert derive_pair_type(out_of_scope_type, "Assignment") is None


def test_derive_pair_type_cross_subgroup_yields_none():
    assert derive_pair_type("Assignment", "Triggering") is None
    assert derive_pair_type("Flow", "Realization") is None


# --- T005: find_chains coverage --------------------------------------------


def _add_valid_chain(model):
    """A --Assignment--> B --Realization--> C (all valid ArchiMate combinations)."""
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationEvent", name="B")
    c = model.add("BusinessEvent", name="C")
    leg1 = model.add_relationship("Assignment", a, b)
    leg2 = model.add_relationship("Realization", b, c)
    return model, a, b, c, leg1, leg2


def test_find_chains_discovers_valid_two_step_chain():
    model, a, b, c, leg1, leg2 = _add_valid_chain(Model())
    chains = find_chains(model)
    assert len(chains) == 1
    assert chains[0].leg1 is leg1
    assert chains[0].leg2 is leg2
    assert chains[0].intermediate is b


def test_find_chains_excludes_self_referencing_cycle():
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationEvent", name="B")
    model.add_relationship("Assignment", a, b)
    model.add_relationship("Assignment", b, a)  # closes a cycle back to A
    chains = find_chains(model)
    assert chains == []


def test_find_chains_excludes_out_of_scope_leg_type():
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationEvent", name="B")
    c = model.add("BusinessEvent", name="C")
    model.add_relationship("Assignment", a, b)
    model.add_relationship("Association", b, c)
    chains = find_chains(model)
    assert chains == []


def test_find_chains_excludes_dangling_reference():
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationEvent", name="B")
    c = model.add("BusinessEvent", name="C")
    model.add_relationship("Assignment", a, b)
    model.add_relationship("Realization", b, c)
    del model.elems_dict[c.uuid]  # simulate a dangling reference
    chains = find_chains(model)
    assert chains == []


# --- T007: find_duplicate_relationships (User Story 1) ---------------------


def test_find_duplicate_relationships_flags_matching_explicit_relationship():
    model, a, b, c, leg1, leg2 = _add_valid_chain(Model())
    duplicate = model.add_relationship("Realization", a, c)

    findings = find_duplicate_relationships(model)

    assert len(findings) == 1
    assert findings[0].relationship is duplicate
    assert len(findings[0].implying_chains) == 1
    assert findings[0].implying_chains[0].leg1 is leg1
    assert findings[0].implying_chains[0].leg2 is leg2


def test_find_duplicate_relationships_no_explicit_relationship_no_finding():
    model, *_ = _add_valid_chain(Model())
    assert find_duplicate_relationships(model) == []


def test_find_duplicate_relationships_mismatched_type_not_flagged():
    model, a, b, c, *_ = _add_valid_chain(Model())
    model.add_relationship("Serving", a, c)  # does not match the implied "Realization"
    assert find_duplicate_relationships(model) == []


def test_find_duplicate_relationships_cross_subgroup_chain_not_flagged():
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationEvent", name="B")
    c = model.add("ApplicationCollaboration", name="C")
    model.add_relationship("Assignment", a, b)
    model.add_relationship("Triggering", b, c)
    assert find_duplicate_relationships(model) == []


def test_find_duplicate_relationships_empty_model_returns_empty():
    assert find_duplicate_relationships(Model()) == []


def test_find_duplicate_relationships_groups_multiple_implying_chains():
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b1 = model.add("ApplicationEvent", name="B1")
    b2 = model.add("ApplicationEvent", name="B2")
    c = model.add("BusinessEvent", name="C")
    model.add_relationship("Assignment", a, b1)
    model.add_relationship("Realization", b1, c)
    model.add_relationship("Assignment", a, b2)
    model.add_relationship("Realization", b2, c)
    duplicate = model.add_relationship("Realization", a, c)

    findings = find_duplicate_relationships(model)

    assert len(findings) == 1
    assert findings[0].relationship is duplicate
    assert len(findings[0].implying_chains) == 2


# --- T012: derive_between (User Story 2) ------------------------------------


def test_derive_between_returns_result_for_qualifying_chain():
    model, a, b, c, leg1, leg2 = _add_valid_chain(Model())
    results = derive_between(model, a, c)
    assert len(results) == 1
    assert results[0].type == "Realization"
    assert results[0].source is a
    assert results[0].target is c
    assert results[0].is_derived is True


def test_derive_between_no_qualifying_chain_returns_empty():
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    c = model.add("BusinessEvent", name="C")
    assert derive_between(model, a, c) == []


def test_derive_between_ignores_existing_explicit_relationship():
    model, a, b, c, *_ = _add_valid_chain(Model())
    model.add_relationship("Realization", a, c)
    results = derive_between(model, a, c)
    assert len(results) == 1
    assert results[0].type == "Realization"


def test_derive_between_multiple_chains_reported_independently():
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b1 = model.add("ApplicationEvent", name="B1")
    b2 = model.add("ApplicationEvent", name="B2")
    c = model.add("BusinessEvent", name="C")
    model.add_relationship("Assignment", a, b1)
    model.add_relationship("Realization", b1, c)
    model.add_relationship("Assignment", a, b2)
    model.add_relationship("Realization", b2, c)

    results = derive_between(model, a, c)
    assert len(results) == 2
    assert all(r.type == "Realization" for r in results)


def test_derive_between_cross_subgroup_chain_yields_no_result():
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationEvent", name="B")
    c = model.add("ApplicationCollaboration", name="C")
    model.add_relationship("Assignment", a, b)
    model.add_relationship("Triggering", b, c)
    assert derive_between(model, a, c) == []


def test_derive_between_unrelated_chain_elsewhere_does_not_match():
    model, a, b, c, leg1, leg2 = _add_valid_chain(Model())
    other = model.add("BusinessEvent", name="Other")
    assert derive_between(model, a, other) == []


def test_derive_between_raises_for_unresolvable_element():
    model, a, b, c, *_ = _add_valid_chain(Model())
    with pytest.raises(ValueError):
        derive_between(model, "id-does-not-exist", c)
    with pytest.raises(ValueError):
        derive_between(model, a, "id-does-not-exist")


# --- T017: derived-vs-explicit distinction (User Story 3) ------------------


def test_derived_relationship_str_always_marked():
    model, a, b, c, leg1, leg2 = _add_valid_chain(Model())
    results = derive_between(model, a, c)
    assert "«derived»" in str(results[0])


def test_derived_relationship_repr_always_marked():
    model, a, b, c, leg1, leg2 = _add_valid_chain(Model())
    results = derive_between(model, a, c)
    assert "«derived»" in repr(results[0])


def test_explicit_relationship_str_never_marked():
    model, a, b, c, leg1, leg2 = _add_valid_chain(Model())
    assert "«derived»" not in str(leg1)
    assert "«derived»" not in str(leg2)
