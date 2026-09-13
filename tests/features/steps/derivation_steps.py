"""Step definitions for Derived Relationships acceptance tests (spec 015, issue #140).

Drives the real Model API (Model.check_derivable_duplicates / Model.derive_relationship)
and the underlying src.pyArchimate.derivation helpers directly -- no mocking. Element and
relationship type combinations follow specs/015-derived-relationships/quickstart.md, which
lists the type pairs that are valid together in this library's metamodel.
"""

import filecmp
import tempfile
from pathlib import Path

from behave import given, then, when  # type: ignore[import-untyped]

from src.pyArchimate.derivation import DerivedRelationship
from src.pyArchimate.model import Model

_NO_FLAG_MSG = "Expected no duplicate finding for the pair (A, C)"


def _add_element(context, archetype: str, name: str):
    elem = context.model.add(archetype, name=name)
    context.elements[name] = elem
    return elem


def _add_rel(context, rel_type: str, source, target, name: str | None = None):
    rel = context.model.add_relationship(rel_type, source, target)
    context.relationships.append(rel)
    if name:
        context.named_relationships[name] = rel
    return rel


# ============================================================================
# Background
# ============================================================================


@given("I have a fresh pyArchimate model for derivation testing")
def step_fresh_model(context):
    context.model = Model("derived-relationships-test")
    context.elements = {}
    context.relationships = []
    context.named_relationships = {}


# ============================================================================
# User Story 1 - scan for duplicates
# ============================================================================


@given("elements A, B, C where A relates to B and B relates to C forming a supported two-step chain")
def step_two_step_chain(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    b = _add_element(context, "ApplicationEvent", "B")
    c = _add_element(context, "BusinessEvent", "C")
    context.chain_leg1 = _add_rel(context, "Assignment", a, b)
    context.chain_leg2 = _add_rel(context, "Realization", b, c)


@given("an explicit relationship of the chain-implied type already exists directly between A and C")
def step_explicit_duplicate(context):
    a, c = context.elements["A"], context.elements["C"]
    # The chain (Assignment, Realization) implies "Realization" between A and C.
    context.duplicate_rel = _add_rel(context, "Realization", a, c, name="duplicate")


@given("no explicit relationship exists directly between A and C")
def step_no_explicit_between_a_c(context):
    # Nothing to do: the chain fixture above adds no A-C relationship.
    pass


@given("an explicit direct relationship between A and C whose type does not match what the chain would imply")
def step_mismatched_type_between_a_c(context):
    a, c = context.elements["A"], context.elements["C"]
    # The chain implies "Realization"; use "Serving" so it does not match.
    context.mismatched_rel = _add_rel(context, "Serving", a, c, name="mismatched")


@given("a model with no relationship chains at all")
def step_no_chains_model(context):
    _add_element(context, "ApplicationCollaboration", "Lonely")


@when("the scan is run")
def step_run_scan(context):
    context.findings = context.model.check_derivable_duplicates()


@then("the report includes that explicit relationship")
def step_report_includes_duplicate(context):
    assert any(f.relationship is context.duplicate_rel for f in context.findings), (
        "Expected the scan report to include the explicit duplicate relationship"
    )


@then("it is identified as duplicating the derivation")
def step_identified_as_duplicate(context):
    matching = [f for f in context.findings if f.relationship is context.duplicate_rel]
    assert len(matching) == 1, "Expected exactly one finding for the duplicate relationship"
    assert len(matching[0].implying_chains) > 0, "Finding should cite at least one implying chain"


@then("the report cites the two relationships that make up the implying chain")
def step_report_cites_chain(context):
    matching = [f for f in context.findings if f.relationship is context.duplicate_rel][0]
    chain = matching.implying_chains[0]
    assert chain.leg1 is context.chain_leg1, "Chain's first leg should be the implying relationship"
    assert chain.leg2 is context.chain_leg2, "Chain's second leg should be the implying relationship"


@then("the report does not flag anything for the pair (A, C)")
def step_report_no_flag_for_pair(context):
    a, c = context.elements["A"], context.elements["C"]
    assert not any(f.relationship.source is a and f.relationship.target is c for f in context.findings), _NO_FLAG_MSG


@then("the report does not flag that relationship as a duplicate")
def step_report_not_flag_mismatched(context):
    assert not any(f.relationship is context.mismatched_rel for f in context.findings), _NO_FLAG_MSG


@then("the report is empty")
def step_report_empty(context):
    assert context.findings == [], f"Expected an empty report, got {context.findings}"


@then("the scan completes without error")
def step_scan_no_error(context):
    # Reaching this step without an exception already proves the scan completed.
    assert hasattr(context, "findings")


# ============================================================================
# User Story 2 - on-demand derivation query
# ============================================================================


@given("two elements connected by a single supported two-step chain and no explicit relationship between them")
def step_two_elems_single_chain(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    b = _add_element(context, "ApplicationEvent", "B")
    c = _add_element(context, "BusinessEvent", "C")
    context.chain_leg1 = _add_rel(context, "Assignment", a, b)
    context.chain_leg2 = _add_rel(context, "Realization", b, c)
    context.query_source, context.query_target = a, c


@given("two elements with no qualifying chain between them")
def step_two_elems_no_chain(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    c = _add_element(context, "BusinessEvent", "C")
    context.query_source, context.query_target = a, c


@given("two elements already connected by an explicit relationship")
def step_two_elems_explicit_rel(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    c = _add_element(context, "BusinessEvent", "C")
    context.explicit_rel = _add_rel(context, "Realization", a, c, name="explicit")
    context.query_source, context.query_target = a, c


@given("those same two elements are also connected by a qualifying chain")
def step_same_elems_also_chain(context):
    a, c = context.query_source, context.query_target
    b = _add_element(context, "ApplicationEvent", "B")
    context.chain_leg1 = _add_rel(context, "Assignment", a, b)
    context.chain_leg2 = _add_rel(context, "Realization", b, c)


@when("the derived relationship is requested for that pair")
def step_request_derivation(context):
    context.derivation_results = context.model.derive_relationship(context.query_source, context.query_target)


@then("the result identifies the implied relationship type")
def step_result_identifies_type(context):
    assert len(context.derivation_results) >= 1, "Expected at least one derived relationship result"
    assert context.derivation_results[0].type == "Realization"


@then("the result references the chain that produced it")
def step_result_references_chain(context):
    result = context.derivation_results[0]
    assert result.chain.leg1 is context.chain_leg1
    assert result.chain.leg2 is context.chain_leg2


@then("the result indicates no derivation applies")
def step_result_no_derivation(context):
    assert context.derivation_results == [], f"Expected no derivation results, got {context.derivation_results}"


@then("the query still returns the additional chain-implied result independently of the explicit relationship")
def step_query_returns_independent_result(context):
    assert len(context.derivation_results) == 1, "Expected one chain-implied result alongside the explicit relationship"
    assert context.derivation_results[0].type == "Realization"
    # The explicit relationship still exists untouched in the model, reported separately.
    assert context.explicit_rel.uuid in context.model.rels_dict


@given("a model file and a view file saved to disk")
def step_model_and_view_saved(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    b = _add_element(context, "ApplicationEvent", "B")
    c = _add_element(context, "BusinessEvent", "C")
    _add_rel(context, "Assignment", a, b)
    _add_rel(context, "Realization", b, c)

    from src.pyArchimate.view import View

    view = View(name="Derivation View", parent=context.model)
    context.model.views_dict[view.uuid] = view
    view.add(ref=a.uuid)
    view.add(ref=c.uuid)
    context.query_source, context.query_target = a, c

    tmp_dir = Path(tempfile.mkdtemp())
    context.model_file = tmp_dir / "model.archimate"
    context.model.write(str(context.model_file))
    context.before_snapshot = tmp_dir / "before.archimate"
    context.before_snapshot.write_bytes(context.model_file.read_bytes())


@when("the derived relationship is requested for two elements in that model")
def step_request_derivation_for_saved_model(context):
    context.derivation_results = context.model.derive_relationship(context.query_source, context.query_target)


@then("the source model file and any view file involved are unmodified on disk")
def step_file_unmodified(context):
    assert filecmp.cmp(str(context.before_snapshot), str(context.model_file), shallow=False), (
        "Model file on disk should be byte-identical after running the scan and derivation query"
    )


# ============================================================================
# User Story 3 - derived vs explicit distinction
# ============================================================================


@given("a derived relationship produced by the on-demand query")
def step_derived_rel_produced(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    b = _add_element(context, "ApplicationEvent", "B")
    c = _add_element(context, "BusinessEvent", "C")
    _add_rel(context, "Assignment", a, b)
    _add_rel(context, "Realization", b, c)
    results = context.model.derive_relationship(a, c)
    assert len(results) == 1
    context.output_item = results[0]


@given("an explicit, modeled relationship")
def step_explicit_modeled_rel(context):
    a = _add_element(context, "ApplicationCollaboration", "A2")
    c = _add_element(context, "BusinessEvent", "C2")
    context.output_item = _add_rel(context, "Serving", a, c, name="explicit-for-us3")


@when("it is included in an output consumed by a user")
@when("it is included in the same output")
def step_included_in_output(context):
    context.rendered_output = str(context.output_item)


@then("it is marked as derived")
def step_marked_as_derived(context):
    assert isinstance(context.output_item, DerivedRelationship)
    assert "«derived»" in context.rendered_output, f"Expected a derived marker in {context.rendered_output!r}"


@then("it cannot be mistaken for an explicit relationship in that same output")
def step_cannot_be_mistaken(context):
    assert context.output_item.is_derived is True
    # An explicit Relationship instance never carries this marker or attribute.
    assert not hasattr(context.output_item, "rels_dict")


@then('it carries no "derived" marking')
def step_no_derived_marking(context):
    assert "«derived»" not in context.rendered_output, (
        f"Explicit relationship output should carry no derived marker, got {context.rendered_output!r}"
    )
    assert not isinstance(context.output_item, DerivedRelationship)


# ============================================================================
# Edge cases
# ============================================================================


@given("elements A and B where A relates to B and B relates back to A")
def step_self_referencing_cycle(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    b = _add_element(context, "ApplicationEvent", "B")
    context.chain_leg1 = _add_rel(context, "Assignment", a, b)
    context.chain_leg2 = _add_rel(context, "Assignment", b, a)
    context.query_source, context.query_target = a, b


@then("the derivation does not produce a self-referencing derived relationship from that cycle")
def step_no_self_referencing_derivation(context):
    assert context.findings == [], "A self-referencing cycle must not produce any derivation-based finding"
    from src.pyArchimate.derivation import find_chains

    chains = find_chains(context.model)
    assert chains == [], "A self-referencing A->B->A cycle must not be discovered as a qualifying chain"


@given("two elements connected via two different intermediate elements whose chains imply different relationship types")
def step_two_chains_different_types(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    b1 = _add_element(context, "ApplicationEvent", "B1")
    b2 = _add_element(context, "ApplicationEvent", "B2")
    c = _add_element(context, "BusinessEvent", "C")
    # Chain 1: two structural legs (DR2, weakest-link) -> implies "Realization".
    context.chain1_leg1 = _add_rel(context, "Assignment", a, b1)
    context.chain1_leg2 = _add_rel(context, "Realization", b1, c)
    # Chain 2: structural then Serving (DR3) -> implies "Serving". Serving is
    # a *dependency* relationship (ArchiMate 3.2 Spec Section 5.2), not a
    # structural one, so it cannot appear as a leg in a DR2 chain the way an
    # earlier draft of this step assumed.
    context.chain2_leg1 = _add_rel(context, "Assignment", a, b2)
    context.chain2_leg2 = _add_rel(context, "Serving", b2, c)
    context.query_source, context.query_target = a, c


@then("each qualifying chain is evaluated and reported independently")
def step_each_chain_reported_independently(context):
    assert len(context.derivation_results) == 2, f"Expected two independent results, got {context.derivation_results}"
    types = {r.type for r in context.derivation_results}
    assert types == {"Realization", "Serving"}, f"Expected distinct implied types, got {types}"


@then("the results are not reconciled or ranked against each other")
def step_results_not_reconciled(context):
    # Both results must be present as separate entries -- neither is dropped or merged.
    assert len(context.derivation_results) == len({id(r) for r in context.derivation_results})


@given("a chain where one leg uses a relationship type outside the supported subset")
def step_chain_out_of_scope_leg(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    b = _add_element(context, "ApplicationEvent", "B")
    c = _add_element(context, "BusinessEvent", "C")
    _add_rel(context, "Assignment", a, b)
    _add_rel(context, "Association", b, c)  # out-of-scope leg type
    context.query_source, context.query_target = a, c


@then("that chain is skipped for derivation and no result is produced for it")
def step_chain_skipped(context):
    assert context.derivation_results == [], (
        f"Expected no derivation results when a leg is out-of-scope, got {context.derivation_results}"
    )


@given("a chain whose relationship references an element no longer present in the model")
def step_chain_dangling_reference(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    b = _add_element(context, "ApplicationEvent", "B")
    c = _add_element(context, "BusinessEvent", "C")
    _add_rel(context, "Assignment", a, b)
    _add_rel(context, "Realization", b, c)
    del context.model.elems_dict[c.uuid]  # simulate a dangling reference


@then("that relationship is excluded from chain construction and does not participate in derivation")
def step_relationship_excluded_dangling(context):
    from src.pyArchimate.derivation import find_chains

    assert find_chains(context.model) == [], "Chains referencing a missing element must be excluded"
    assert context.findings == [], "The scan must not report anything derived from a dangling reference"


@given("an explicit relationship between A and C that is reachable via more than one qualifying chain")
def step_duplicate_multiple_chains(context):
    a = _add_element(context, "ApplicationCollaboration", "A")
    b1 = _add_element(context, "ApplicationEvent", "B1")
    b2 = _add_element(context, "ApplicationEvent", "B2")
    c = _add_element(context, "BusinessEvent", "C")
    context.chain1_leg1 = _add_rel(context, "Assignment", a, b1)
    context.chain1_leg2 = _add_rel(context, "Realization", b1, c)
    context.chain2_leg1 = _add_rel(context, "Assignment", a, b2)
    context.chain2_leg2 = _add_rel(context, "Realization", b2, c)
    context.duplicate_rel = _add_rel(context, "Realization", a, c, name="duplicate")


@then("the report includes the explicit relationship exactly once")
def step_report_includes_once(context):
    matching = [f for f in context.findings if f.relationship is context.duplicate_rel]
    assert len(matching) == 1, f"Expected exactly one finding for the duplicate, got {len(matching)}"
    context.duplicate_finding = matching[0]


@then("it cites all qualifying chains that imply it")
def step_cites_all_chains(context):
    chains = context.duplicate_finding.implying_chains
    assert len(chains) == 2, f"Expected the finding to cite both implying chains, got {len(chains)}"
