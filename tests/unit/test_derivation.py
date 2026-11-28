"""Unit tests for the derivation-rule table and chain-discovery logic (spec 015)."""

import itertools

import pytest

from src.pyArchimate import Model
from src.pyArchimate.derivation import (
    DEFAULT_MAX_CHAIN_LENGTH_CEILING,
    RelationshipChain,
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


@pytest.mark.parametrize(("leg1_type", "leg2_type"), list(itertools.product(STRUCTURAL_ORDER, repeat=2)))
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
    ("leg1_type", "leg2_type"),
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


# --- Issue #146: opt-in include_dependency scope ----------------------------
#
# Extends chaining eligibility to Access, Influence, and Association when
# include_dependency=True. Per ArchiMate 3.2 Appendix B.3 ("potential"
# derivation, not the "certain" B.2 rules above), the only derivation this
# opt-in scope actually produces is Influence-then-Realization -> Influence
# (the case GitHub issue #146 named). Access and Association are made
# eligible to participate in chains for completeness, but deliberately
# produce no derivation of their own: Access has direction/type variants
# with no documented "certain" derivation, and neither Influence nor
# Association has a formal strength ordering to resolve a DR2-style
# weakest-link rule, so no such rule is invented for them.


@pytest.mark.parametrize("structural_type", STRUCTURAL_ORDER)
def test_derive_pair_type_influence_then_structural_requires_opt_in(structural_type):
    assert derive_pair_type("Influence", structural_type) is None
    assert derive_pair_type("Influence", structural_type, include_dependency=False) is None


def test_derive_pair_type_influence_then_realization_opt_in():
    assert derive_pair_type("Influence", "Realization", include_dependency=True) == "Influence"


@pytest.mark.parametrize("structural_type", ["Composition", "Aggregation", "Assignment"])
def test_derive_pair_type_influence_then_other_structural_opt_in(structural_type):
    """The issue named Influence-then-Realization specifically; this module
    generalizes the opt-in rule to any structural second leg (DR7's
    Triggering-then-structural is the closest precedent for that shape)."""
    assert derive_pair_type("Influence", structural_type, include_dependency=True) == "Influence"


@pytest.mark.parametrize("out_of_scope_type", ["Access", "Association"])
def test_derive_pair_type_access_and_association_opt_in_yield_no_derivation(out_of_scope_type):
    """Included in the opt-in chaining scope, but intentionally produce no
    derived relationship of their own (see module docstring rationale)."""
    for structural_type in STRUCTURAL_ORDER:
        assert derive_pair_type(out_of_scope_type, structural_type, include_dependency=True) is None
        assert derive_pair_type(structural_type, out_of_scope_type, include_dependency=True) is None


def _add_influence_chain(model):
    """A --Influence--> B --Realization--> C."""
    a = model.add("Assessment", name="A")
    b = model.add("Requirement", name="B")
    c = model.add("Goal", name="C")
    leg1 = model.add_relationship("Influence", a, b)
    leg2 = model.add_relationship("Realization", b, c)
    return model, a, b, c, leg1, leg2


def test_find_chains_excludes_influence_leg_by_default():
    model, *_ = _add_influence_chain(Model())
    assert find_chains(model) == []


def test_find_chains_includes_influence_leg_when_opted_in():
    model, _, b, _, leg1, leg2 = _add_influence_chain(Model())
    chains = find_chains(model, include_dependency=True)
    assert len(chains) == 1
    assert chains[0].leg1 is leg1
    assert chains[0].leg2 is leg2
    assert chains[0].intermediate is b


def test_derive_between_influence_then_realization_requires_opt_in():
    model, a, _, c, *_ = _add_influence_chain(Model())
    assert derive_between(model, a, c) == []
    assert derive_between(model, a, c, include_dependency=False) == []


def test_derive_between_influence_then_realization_opted_in():
    model, a, _, c, *_ = _add_influence_chain(Model())
    results = derive_between(model, a, c, include_dependency=True)
    assert len(results) == 1
    assert results[0].type == "Influence"
    assert results[0].source is a
    assert results[0].target is c


def test_derive_between_opt_in_does_not_affect_existing_certain_rules():
    """Passing include_dependency=True must not change a DR2/DR3/DR5/DR7/DR8
    result - the opt-in only adds eligibility, never removes or overrides it."""
    model, a, _, c, _, _ = _add_valid_chain(Model())
    results = derive_between(model, a, c, include_dependency=True)
    assert len(results) == 1
    assert results[0].type == "Realization"


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


def test_find_chains_excludes_dangling_source_reference():
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationEvent", name="B")
    c = model.add("BusinessEvent", name="C")
    model.add_relationship("Assignment", a, b)
    model.add_relationship("Realization", b, c)
    del model.elems_dict[a.uuid]  # simulate a dangling source reference
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
    with pytest.raises(ValueError, match="Invalid source reference"):
        derive_between(model, "id-does-not-exist", c)
    with pytest.raises(ValueError, match="Invalid target reference"):
        derive_between(model, a, "id-does-not-exist")


# --- spec 016: N-hop chain generalization (Foundational) -------------------


def _add_three_step_chain(model):
    """A --Composition--> B --Aggregation--> C --Realization--> D."""
    a = model.add("ApplicationComponent", name="A")
    b = model.add("ApplicationComponent", name="B")
    c = model.add("ApplicationComponent", name="C")
    d = model.add("ApplicationComponent", name="D")
    leg1 = model.add_relationship("Composition", a, b)
    leg2 = model.add_relationship("Aggregation", b, c)
    leg3 = model.add_relationship("Realization", c, d)
    return model, a, b, c, d, leg1, leg2, leg3


def _add_four_step_chain(model):
    """A --Composition--> B --Aggregation--> C --Realization--> D --Serving--> E."""
    model, a, b, c, d, leg1, leg2, leg3 = _add_three_step_chain(model)
    e = model.add("ApplicationComponent", name="E")
    leg4 = model.add_relationship("Serving", d, e)
    return model, a, b, c, d, e, leg1, leg2, leg3, leg4


def test_relationship_chain_rejects_fewer_than_two_legs():
    """RelationshipChain.__post_init__ enforces its "at least two legs" invariant."""
    model = Model()
    a = model.add("ApplicationComponent", name="A")
    b = model.add("ApplicationComponent", name="B")
    leg1 = model.add_relationship("Composition", a, b)
    with pytest.raises(ValueError, match="at least two legs"):
        RelationshipChain(legs=[leg1])


def test_fold_chain_type_short_circuits_on_undefined_pair():
    """_fold_chain_type (FR-002/FR-003) folds left-to-right and returns None
    the moment an adjacent pair - original or already-folded - has no
    defined rule, rather than guessing or returning a partial result."""
    from src.pyArchimate.derivation import _fold_chain_type

    model = Model()
    a = model.add("ApplicationComponent", name="A")
    b = model.add("ApplicationComponent", name="B")
    c = model.add("ApplicationComponent", name="C")
    leg1 = model.add_relationship("Serving", a, b)  # dependency type
    leg2 = model.add_relationship("Flow", b, c)  # dynamic type, undefined pair with Serving
    assert _fold_chain_type([leg1, leg2]) is None


def test_relationship_chain_legs_field_holds_full_sequence():
    """RelationshipChain.legs generalizes the old leg1/leg2 pair (data-model.md)."""
    model, _, b, c, _d, leg1, leg2, leg3 = _add_three_step_chain(Model())
    chains = find_chains(model, max_chain_length=3)
    three_leg = [chain for chain in chains if len(chain.legs) == 3]
    assert len(three_leg) == 1
    chain = three_leg[0]
    assert chain.legs == [leg1, leg2, leg3]
    # Backward-compatible leg1/leg2 access for any chain (FR-010).
    assert chain.leg1 is leg1
    assert chain.leg2 is leg3
    assert chain.intermediate == [b, c]


def test_find_chains_discovers_three_step_chain():
    """find_chains discovers every qualifying chain up to max_chain_length,
    including shorter sub-chains (contracts/derivation-api.md) - here the
    3-leg A->B->C->D chain, alongside the 2-leg A->B->C and B->C->D chains."""
    model, _, _, _, _, leg1, leg2, leg3 = _add_three_step_chain(Model())
    chains = find_chains(model, max_chain_length=3)
    three_leg = [chain for chain in chains if len(chain.legs) == 3]
    assert len(three_leg) == 1
    assert three_leg[0].legs == [leg1, leg2, leg3]


def test_find_chains_discovers_four_step_chain():
    model, *_, leg1, leg2, leg3, leg4 = _add_four_step_chain(Model())
    chains = find_chains(model, max_chain_length=4)
    matching = [c for c in chains if len(c.legs) == 4]
    assert len(matching) == 1
    assert matching[0].legs == [leg1, leg2, leg3, leg4]


def test_find_chains_default_max_chain_length_matches_pre_feature_baseline():
    """FR-010/SC-003: no max_chain_length argument -> identical to the
    pre-this-feature two-step-only find_chains() behavior (both qualifying
    2-leg chains in this 3-step model, A->B->C and B->C->D)."""
    model, _a, b, _c, _, leg1, leg2, leg3 = _add_three_step_chain(Model())
    chains = find_chains(model)  # default max_chain_length=2
    assert {tuple(chain.legs) for chain in chains} == {(leg1, leg2), (leg2, leg3)}
    found = next(chain for chain in chains if chain.legs == [leg1, leg2])
    assert found.leg1 is leg1
    assert found.leg2 is leg2
    assert found.intermediate is b


def test_find_chains_rejects_chain_revisiting_an_element():
    """FR-004: generalizes the two-step A->B->A protection to any length -
    here a 4-element path A->B->C->B revisits B three hops apart."""
    model = Model()
    a = model.add("ApplicationComponent", name="A")
    b = model.add("ApplicationComponent", name="B")
    c = model.add("ApplicationComponent", name="C")
    model.add_relationship("Composition", a, b)
    model.add_relationship("Aggregation", b, c)
    model.add_relationship("Assignment", c, b)  # revisits B
    chains = find_chains(model, max_chain_length=3)
    assert all(len(chain.legs) < 3 for chain in chains), (
        "No 3-leg chain should be discovered when it revisits an element (A->B->C->B)"
    )


def test_find_chains_excludes_dangling_reference_at_third_hop():
    """FR-008: dangling-reference exclusion generalizes to any position in
    a chain of any length - here the element is removed from hop 3 of 4."""
    model, _a, _b, _c, d, leg1, leg2, leg3 = _add_three_step_chain(Model())
    del model.elems_dict[d.uuid]  # simulate a dangling reference at leg3's target
    chains = find_chains(model, max_chain_length=3)
    assert all(leg3 not in chain.legs for chain in chains), (
        "No chain may reference leg3, whose target is a dangling reference"
    )
    # The still-valid 2-leg prefix (A->B->C) must remain discoverable on its own.
    assert find_chains(model, max_chain_length=2) == [RelationshipChain(legs=[leg1, leg2])]


def test_max_chain_length_above_ceiling_requires_explicit_override():
    """FR-011: a documented default ceiling, explicitly overridable."""
    model, *_ = _add_three_step_chain(Model())
    with pytest.raises(ValueError, match="exceeds the default ceiling"):
        find_chains(model, max_chain_length=DEFAULT_MAX_CHAIN_LENGTH_CEILING + 1)
    # Explicit override succeeds (even though no chain that long exists here).
    find_chains(
        model,
        max_chain_length=DEFAULT_MAX_CHAIN_LENGTH_CEILING + 1,
        allow_exceeding_default_ceiling=True,
    )


# --- T010/T011: find_duplicate_relationships N-hop coverage (User Story 1) --


def test_find_duplicate_relationships_flags_three_step_chain_duplicate():
    model, a, _, _, d, leg1, leg2, leg3 = _add_three_step_chain(Model())
    duplicate = model.add_relationship("Realization", a, d)

    assert find_duplicate_relationships(model) == []  # default max_chain_length=2: not seen

    findings = find_duplicate_relationships(model, max_chain_length=3)
    assert len(findings) == 1
    assert findings[0].relationship is duplicate
    assert any(chain.legs == [leg1, leg2, leg3] for chain in findings[0].implying_chains)


def test_find_duplicate_relationships_flags_four_step_chain_duplicate():
    model, a, *_, e, leg1, leg2, leg3, leg4 = _add_four_step_chain(Model())
    duplicate = model.add_relationship("Serving", a, e)

    findings = find_duplicate_relationships(model, max_chain_length=4)
    matching = [f for f in findings if f.relationship is duplicate]
    assert len(matching) == 1
    assert any(chain.legs == [leg1, leg2, leg3, leg4] for chain in matching[0].implying_chains)


def test_find_duplicate_relationships_three_step_undefined_pair_not_flagged():
    """FR-003/SC-002: an undefined adjacent pair anywhere in the chain means
    no duplicate is reported at all - never a partial result."""
    model = Model()
    a = model.add("ApplicationComponent", name="A")
    b = model.add("ApplicationComponent", name="B")
    c = model.add("ApplicationComponent", name="C")
    d = model.add("ApplicationComponent", name="D")
    model.add_relationship("Composition", a, b)
    model.add_relationship("Flow", b, c)  # Flow+structural (DR6-shape) is undefined
    model.add_relationship("Flow", c, d)
    model.add_relationship("Flow", a, d)  # would-be duplicate, must not be flagged

    findings = find_duplicate_relationships(model, max_chain_length=3)
    assert findings == []


# --- T017-T020: derive_between N-hop coverage (User Story 2) ---------------


def test_derive_between_three_step_chain_folds_correctly():
    model, a, _, _, d, leg1, leg2, leg3 = _add_three_step_chain(Model())

    assert derive_between(model, a, d) == []  # default max_chain_length=2: unreachable

    results = derive_between(model, a, d, max_chain_length=3)
    assert len(results) == 1
    assert results[0].type == "Realization"
    assert results[0].chain.legs == [leg1, leg2, leg3]


def test_derive_between_three_step_chain_undefined_pair_yields_empty():
    model = Model()
    a = model.add("ApplicationComponent", name="A")
    b = model.add("ApplicationComponent", name="B")
    c = model.add("ApplicationComponent", name="C")
    d = model.add("ApplicationComponent", name="D")
    model.add_relationship("Composition", a, b)
    model.add_relationship("Flow", b, c)
    model.add_relationship("Flow", c, d)

    assert derive_between(model, a, d, max_chain_length=3) == []


def test_derive_between_two_and_three_step_chains_independent():
    """FR-007: when two elements are connected by both a qualifying 2-step
    chain and a separate qualifying 3-step chain, both results are reported
    independently, each citing its own chain."""
    model = Model()
    a = model.add("ApplicationComponent", name="A")
    b = model.add("ApplicationComponent", name="B")
    c = model.add("ApplicationComponent", name="C")
    d = model.add("ApplicationComponent", name="D")
    x = model.add("ApplicationComponent", name="X")
    leg1 = model.add_relationship("Composition", a, b)
    leg2 = model.add_relationship("Aggregation", b, c)
    leg3 = model.add_relationship("Realization", c, d)
    short_leg1 = model.add_relationship("Realization", a, x)
    short_leg2 = model.add_relationship("Serving", x, d)

    results = derive_between(model, a, d, max_chain_length=3)
    assert len(results) == 2
    chains_by_type = {result.type: result.chain.legs for result in results}
    assert chains_by_type == {
        "Realization": [leg1, leg2, leg3],
        "Serving": [short_leg1, short_leg2],
    }


def test_derive_between_three_step_chain_with_influence_opt_in():
    model = Model()
    a = model.add("Assessment", name="A")
    b = model.add("Requirement", name="B")
    c = model.add("Goal", name="C")
    d = model.add("ApplicationComponent", name="D")
    leg1 = model.add_relationship("Influence", a, b)
    leg2 = model.add_relationship("Realization", b, c)
    leg3 = model.add_relationship("Composition", c, d)

    assert derive_between(model, a, d, include_dependency=True) == []  # default max=2: unreachable

    results = derive_between(model, a, d, include_dependency=True, max_chain_length=3)
    assert len(results) == 1
    assert results[0].type == "Influence"
    assert results[0].chain.legs == [leg1, leg2, leg3]


# --- T026-T028: default-unchanged / ceiling-override regression (User Story 3) --


def test_default_settings_regression_matches_pre_feature_baseline():
    """SC-003: representative T001-baseline cases through the generalized
    module, default settings only, identical to pre-feature results."""
    model, a, _b, c, leg1, leg2 = _add_valid_chain(Model())
    assert find_chains(model) == [RelationshipChain(legs=[leg1, leg2])]
    results = derive_between(model, a, c)
    assert len(results) == 1
    assert results[0].type == "Realization"
    model.add_relationship("Realization", a, c)
    findings = find_duplicate_relationships(model)
    assert len(findings) == 1


def test_default_settings_do_not_see_longer_chain_until_opted_in():
    """A qualifying longer-than-two-step chain is invisible at default
    settings and only appears once max_chain_length is explicitly raised."""
    model, a, _, _, d, *_ = _add_three_step_chain(Model())
    model.add_relationship("Realization", a, d)

    assert model.check_derivable_duplicates() == []
    assert model.derive_relationship(a, d) == []

    assert len(model.check_derivable_duplicates(max_chain_length=3)) == 1
    assert len(model.derive_relationship(a, d, max_chain_length=3)) == 1


def test_max_chain_length_above_ceiling_requires_override_on_every_entry_point():
    """FR-011: the ceiling and its override apply uniformly to find_chains,
    derive_between, and find_duplicate_relationships."""
    model, a, _, _, d, *_ = _add_three_step_chain(Model())
    above_ceiling = DEFAULT_MAX_CHAIN_LENGTH_CEILING + 1

    with pytest.raises(ValueError, match="exceeds the default ceiling"):
        derive_between(model, a, d, max_chain_length=above_ceiling)
    with pytest.raises(ValueError, match="exceeds the default ceiling"):
        find_duplicate_relationships(model, max_chain_length=above_ceiling)

    derive_between(model, a, d, max_chain_length=above_ceiling, allow_exceeding_default_ceiling=True)
    find_duplicate_relationships(model, max_chain_length=above_ceiling, allow_exceeding_default_ceiling=True)


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
