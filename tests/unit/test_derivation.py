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

STRUCTURAL_ORDER = ["Composition", "Aggregation", "Assignment", "Realization"]
DYNAMIC_TYPES = ["Triggering", "Flow"]
OUT_OF_SCOPE_TYPES = ["Access", "Influence", "Specialization", "Association"]


# --- T003: derive_pair_type rule-table coverage -----------------------------
#
# Verified against a primary copy of the ArchiMate 3.2 Specification,
# Appendix B.2 ("Derivation Rules for Valid Relationships"), DR2/DR3/DR5/
# DR7/DR8, rather than the secondary web sources research.md originally
# relied on. Two corrections from the original (unverified) implementation:
# Serving is a *dependency* relationship, not the "weakest structural" type,
# and dynamic-dynamic derivation is NOT a generic "Triggering-wins" rule -
# only Triggering+Triggering (DR8) is defined; Flow+Flow, Flow+Triggering,
# and Triggering+Flow have no "certain" derivation.


@pytest.mark.parametrize("leg1_type,leg2_type", list(itertools.product(STRUCTURAL_ORDER, repeat=2)))
def test_derive_pair_type_dr2_both_structural_weakest_link(leg1_type, leg2_type):
    """DR2 (p.128): two structural legs derive the weaker of the two."""
    expected_index = max(STRUCTURAL_ORDER.index(leg1_type), STRUCTURAL_ORDER.index(leg2_type))
    expected = STRUCTURAL_ORDER[expected_index]
    assert derive_pair_type(leg1_type, leg2_type) == expected


@pytest.mark.parametrize("structural_type", STRUCTURAL_ORDER)
def test_derive_pair_type_dr3_structural_then_serving(structural_type):
    """DR3 (p.129): structural then Serving derives Serving."""
    assert derive_pair_type(structural_type, "Serving") == "Serving"


@pytest.mark.parametrize("structural_type", STRUCTURAL_ORDER)
def test_derive_pair_type_serving_then_structural_yields_none(structural_type):
    """No DR covers Serving-then-structural (forward, in-line) - only the
    reverse order (DR3) and the "opposing" DR4 (out of scope here) exist."""
    assert derive_pair_type("Serving", structural_type) is None


@pytest.mark.parametrize("structural_type", STRUCTURAL_ORDER)
@pytest.mark.parametrize("dynamic_type", DYNAMIC_TYPES)
def test_derive_pair_type_dr5_structural_then_dynamic(structural_type, dynamic_type):
    """DR5 (p.130): structural then a dynamic relationship (Triggering or
    Flow) derives that same dynamic type."""
    assert derive_pair_type(structural_type, dynamic_type) == dynamic_type


@pytest.mark.parametrize("structural_type", STRUCTURAL_ORDER)
def test_derive_pair_type_dr7_triggering_then_structural(structural_type):
    """DR7 (p.130): Triggering then structural derives Triggering."""
    assert derive_pair_type("Triggering", structural_type) == "Triggering"


@pytest.mark.parametrize("structural_type", STRUCTURAL_ORDER)
def test_derive_pair_type_flow_then_structural_yields_none(structural_type):
    """Flow has no DR7-equivalent: Flow-then-structural (forward, in-line)
    is not a defined "certain" derivation - only the "opposing" DR6 covers
    Flow combined with a structural relationship, which is out of scope for
    this feature's chain shape."""
    assert derive_pair_type("Flow", structural_type) is None


def test_derive_pair_type_dr8_triggering_then_triggering():
    """DR8 (p.131): Triggering is transitive."""
    assert derive_pair_type("Triggering", "Triggering") == "Triggering"


@pytest.mark.parametrize(
    "leg1_type,leg2_type",
    [
        ("Flow", "Flow"),
        ("Flow", "Triggering"),
        ("Triggering", "Flow"),
        ("Serving", "Serving"),
        ("Serving", "Triggering"),
        ("Serving", "Flow"),
        ("Triggering", "Serving"),
        ("Flow", "Serving"),
    ],
)
def test_derive_pair_type_other_dynamic_and_dependency_combinations_yield_none(leg1_type, leg2_type):
    """None of these pairings has a "certain" (valid) derivation rule in
    ArchiMate 3.2 Appendix B.2 - they would only be reachable, if at all,
    via the lower-certainty "potential" rules in B.3, which are out of scope."""
    assert derive_pair_type(leg1_type, leg2_type) is None


@pytest.mark.parametrize("out_of_scope_type", OUT_OF_SCOPE_TYPES)
def test_derive_pair_type_out_of_scope_leg_yields_none(out_of_scope_type):
    assert derive_pair_type("Assignment", out_of_scope_type) is None
    assert derive_pair_type(out_of_scope_type, "Assignment") is None


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
    model, _, b, _, leg1, leg2 = _add_valid_chain(Model())
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
    model, a, _, c, leg1, leg2 = _add_valid_chain(Model())
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
    model, a, _, c, *_ = _add_valid_chain(Model())
    model.add_relationship("Serving", a, c)  # does not match the implied "Realization"
    assert find_duplicate_relationships(model) == []


def test_find_duplicate_relationships_undefined_pair_chain_not_flagged():
    """Flow-then-structural (forward) has no defined derivation (see
    test_derive_pair_type_flow_then_structural_yields_none), so such a chain
    never qualifies as implying anything to flag as a duplicate."""
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationCollaboration", name="B")
    c = model.add("ApplicationEvent", name="C")
    model.add_relationship("Flow", a, b)
    model.add_relationship("Assignment", b, c)
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
    model, a, _, c, _, _ = _add_valid_chain(Model())
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
    model, a, _, c, *_ = _add_valid_chain(Model())
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


def test_derive_between_undefined_pair_chain_yields_no_result():
    """Flow-then-structural (forward) has no defined derivation."""
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationCollaboration", name="B")
    c = model.add("ApplicationEvent", name="C")
    model.add_relationship("Flow", a, b)
    model.add_relationship("Assignment", b, c)
    assert derive_between(model, a, c) == []


def test_derive_between_structural_then_dynamic_derives_dynamic_type():
    """DR5: structural then Triggering (forward, in-line) does derive
    Triggering - this is the corrected behavior after verifying against the
    primary ArchiMate 3.2 specification; the two elements were previously,
    incorrectly, assumed to have no relationship implied between them."""
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationEvent", name="B")
    c = model.add("ApplicationCollaboration", name="C")
    model.add_relationship("Assignment", a, b)
    model.add_relationship("Triggering", b, c)
    results = derive_between(model, a, c)
    assert len(results) == 1
    assert results[0].type == "Triggering"


def test_derive_between_unrelated_chain_elsewhere_does_not_match():
    model, a, _, _, _, _ = _add_valid_chain(Model())
    other = model.add("BusinessEvent", name="Other")
    assert derive_between(model, a, other) == []


def test_derive_between_raises_for_unresolvable_element():
    model, a, _, c, *_ = _add_valid_chain(Model())
    with pytest.raises(ValueError):
        derive_between(model, "id-does-not-exist", c)
    with pytest.raises(ValueError):
        derive_between(model, a, "id-does-not-exist")


# --- T017: derived-vs-explicit distinction (User Story 3) ------------------


def test_derived_relationship_str_always_marked():
    model, a, _, c, _, _ = _add_valid_chain(Model())
    results = derive_between(model, a, c)
    assert "«derived»" in str(results[0])


def test_derived_relationship_repr_always_marked():
    model, a, _, c, _, _ = _add_valid_chain(Model())
    results = derive_between(model, a, c)
    assert "«derived»" in repr(results[0])


def test_explicit_relationship_str_never_marked():
    _, _, _, _, leg1, leg2 = _add_valid_chain(Model())
    assert "«derived»" not in str(leg1)
    assert "«derived»" not in str(leg2)
