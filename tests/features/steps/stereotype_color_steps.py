"""BDD step definitions for stereotype-based color coding (017-stereotype-colors)."""

import tempfile
from typing import cast

from behave import given, then, when

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.view import View

_TYPE_MAP = {
    "Driver": ArchiType.Driver,
    "BusinessActor": ArchiType.BusinessActor,
    "ApplicationComponent": ArchiType.ApplicationComponent,
}


def _ensure_model(context):
    if not hasattr(context, "model"):
        context.model = Model("stereotype-color-test")
        context.view = cast(View, context.model.add(ArchiType.View, "V"))
        context.elements = {}
        context.nodes = {}
        context.profiles = {}


@given('a stereotype "{name}" with no color configured')
def step_stereotype_no_color(context, name):
    _ensure_model(context)
    context.profiles[name] = context.model.add_profile(name=name, concept=ArchiType.Driver)


@given('a stereotype "{name}" with color "{color}"')
def step_stereotype_with_color(context, name, color):
    _ensure_model(context)
    profile = context.model.add_profile(name=name, concept=ArchiType.Driver)
    profile.fill_color = color
    context.profiles[name] = profile


@given('elements "{name_a}" and "{name_b}" of type "{elem_type}" assigned the "{stereotype}" stereotype')
def step_two_elements_with_stereotype(context, name_a, name_b, elem_type, stereotype):
    _ensure_model(context)
    arch_type = _TYPE_MAP[elem_type]
    for name in (name_a, name_b):
        elem = context.model.add(arch_type, name)
        elem.set_profile(stereotype)
        context.elements[name] = elem
        context.nodes[name] = context.view.add(elem)


@given('an element "{name}" of type "{elem_type}" assigned the "{stereotype}" stereotype')
def step_one_element_with_stereotype(context, name, elem_type, stereotype):
    _ensure_model(context)
    elem = context.model.add(_TYPE_MAP[elem_type], name)
    elem.set_profile(stereotype)
    context.elements[name] = elem
    context.nodes[name] = context.view.add(elem)


@when('the modeler sets the "{stereotype}" stereotype\'s color to "{color}"')
def step_set_stereotype_color(context, stereotype, color):
    context.profiles[stereotype].fill_color = color


@when('the modeler clears the "{stereotype}" stereotype\'s color')
def step_clear_stereotype_color(context, stereotype):
    context.profiles[stereotype].fill_color = None


@when('a new element "{name}" of type "{elem_type}" is assigned the "{stereotype}" stereotype')
def step_new_element_assigned_stereotype(context, name, elem_type, stereotype):
    elem = context.model.add(_TYPE_MAP[elem_type], name)
    elem.set_profile(stereotype)
    context.elements[name] = elem
    context.nodes[name] = context.view.add(elem)


@then('elements "{name_a}" and "{name_b}" should have an effective fill color of "{color}"')
def step_assert_two_effective_colors(context, name_a, name_b, color):
    assert context.nodes[name_a].get_effective_fill_color() == color
    assert context.nodes[name_b].get_effective_fill_color() == color


@then('element "{name}" should have an effective fill color of "{color}"')
def step_assert_effective_color(context, name, color):
    assert context.nodes[name].get_effective_fill_color() == color


@then('element "{name}" should have no effective fill color')
def step_assert_no_effective_color(context, name):
    assert context.nodes[name].get_effective_fill_color() is None


@when('the modeler sets element "{name}"\'s own fill color to "{color}"')
@given('element "{name}"\'s own fill color is set to "{color}"')
def step_set_element_own_color(context, name, color):
    context.elements[name].set_fill_color(color)


@when('the modeler clears element "{name}"\'s own fill color')
def step_clear_element_own_color(context, name):
    context.elements[name].set_fill_color(None)


@when('the modeler reassigns element "{name}" to the "{stereotype}" stereotype')
def step_reassign_stereotype(context, name, stereotype):
    context.elements[name].set_profile(stereotype)


@given('an element "{name}" of type "{elem_type}" with no stereotype')
def step_element_no_stereotype(context, name, elem_type):
    _ensure_model(context)
    elem = context.model.add(_TYPE_MAP[elem_type], name)
    context.elements[name] = elem
    context.nodes[name] = context.view.add(elem)


@when("the view is exported to SVG with no display option set")
def step_export_svg_default(context):
    context.svg = context.view.to_svg()


@then('the exported SVG should label "{name}" with its stereotype')
def step_assert_svg_has_label(context, name):
    profile = context.elements[name].get_profile()
    assert profile is not None
    assert f"«{profile.name}»" in context.svg


@then('the exported SVG should not label "{name}" with a stereotype')
def step_assert_svg_has_no_label(context, name):
    profile = context.elements[name].get_profile()
    if profile is not None:
        assert f"«{profile.name}»" not in context.svg


@when('the modeler saves and reloads the model as "{fmt}"')
def step_save_and_reload(context, fmt):
    suffix = ".archimate" if fmt == "archimate" else ".xml"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        path = f.name
    context.model.write(path)

    name_to_uuid = {name: elem.uuid for name, elem in context.elements.items()}
    reloaded = Model("stereotype-color-test-reloaded")
    reloaded.read(path)

    context.model = reloaded
    context.elements = {name: reloaded.elems_dict[uuid] for name, uuid in name_to_uuid.items()}
    context.view = reloaded.views[0]
    context.nodes = {
        name: next(n for n in context.view.nodes if n.concept is not None and n.concept.uuid == elem.uuid)
        for name, elem in context.elements.items()
    }
