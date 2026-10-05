"""Step definitions for the Composition/Aggregation conflict acceptance tests (issue #149).

Drives Model.check_conflicting_composition_aggregation directly -- no mocking.
"""

from behave import given, then, when  # type: ignore[import-untyped]

from src.pyArchimate.model import Model


@given("I have a fresh pyArchimate model for composition/aggregation conflict testing")
def step_fresh_model(context):
    context.model = Model("composition-aggregation-conflict-test")
    context.elements = {}
    context.named_relationships = {}


@given("elements A and B")
def step_elements_a_b(context):
    context.elements["A"] = context.model.add("ApplicationComponent", name="A")
    context.elements["B"] = context.model.add("ApplicationComponent", name="B")


@given("a Composition relationship from A to B")
def step_composition_a_to_b(context):
    rel = context.model.add_relationship("Composition", context.elements["A"], context.elements["B"])
    context.named_relationships["composition"] = rel


@given("an Aggregation relationship from A to B")
def step_aggregation_a_to_b(context):
    rel = context.model.add_relationship("Aggregation", context.elements["A"], context.elements["B"])
    context.named_relationships["aggregation"] = rel


@given("an Aggregation relationship from B to A")
def step_aggregation_b_to_a(context):
    rel = context.model.add_relationship("Aggregation", context.elements["B"], context.elements["A"])
    context.named_relationships["aggregation"] = rel


@when("the composition/aggregation conflict check is run")
def step_run_check(context):
    context.conflict_report = context.model.check_conflicting_composition_aggregation()


@then("the report flags one conflicting pair citing both relationships")
def step_report_flags_pair(context):
    assert len(context.conflict_report) == 1, f"expected exactly one conflict, got {context.conflict_report}"
    flagged = set(context.conflict_report[0])
    expected = {context.named_relationships["composition"].uuid, context.named_relationships["aggregation"].uuid}
    assert flagged == expected, f"expected {expected}, got {flagged}"


@then("the conflict report is empty")
def step_report_empty(context):
    assert context.conflict_report == [], f"expected no conflicts, got {context.conflict_report}"
