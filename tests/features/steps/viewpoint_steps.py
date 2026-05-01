"""BDD step definitions for viewpoint feature files."""
import os
import tempfile

from behave import given, then, when

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.writers.archimateWriter import archimate_writer


@given('I have a pyArchimate model')
def step_have_model(context):
    context.model = Model(name='Test')


@given('I have a model with an element')
def step_have_model_with_element(context):
    context.model = Model(name='Test')
    context.elem = context.model.add(ArchiType.BusinessActor, 'Test Actor')


@given('I have a model with a view')
def step_have_model_with_view(context):
    context.model = Model(name='Test')
    context.view = context.model.add(ArchiType.View, 'Test View')


@when('I call model.get_viewpoints()')
def step_call_get_viewpoints(context):
    context.result = context.model.get_viewpoints()


@then('I receive a list of {count:d} viewpoints')
def step_receive_viewpoints(context, count):
    assert len(context.result) == count


@then('each viewpoint has an id, name, and description')
def step_viewpoint_has_fields(context):
    for vp in context.result:
        assert vp.id
        assert vp.name
        assert vp.description


@when('I assign the viewpoint "{slug}" to the element')
def step_assign_viewpoint(context, slug):
    context.elem.assign_viewpoint(slug)


@then('element.viewpoints contains "{slug}"')
def step_element_has_viewpoint(context, slug):
    assert slug in context.elem.viewpoints


@when('I assign viewpoints "{slug1}" and "{slug2}" to the element')
def step_assign_two_viewpoints(context, slug1, slug2):
    context.elem.assign_viewpoint(slug1)
    context.elem.assign_viewpoint(slug2)


@then('element.viewpoints contains both "{slug1}" and "{slug2}"')
def step_element_has_both_viewpoints(context, slug1, slug2):
    assert slug1 in context.elem.viewpoints
    assert slug2 in context.elem.viewpoints


@given('I have an element with viewpoint "{slug}"')
def step_element_with_viewpoint(context, slug):
    context.model = Model(name='Test')
    context.elem = context.model.add(ArchiType.BusinessActor, 'Test Actor')
    context.elem.assign_viewpoint(slug)


@when('I remove the viewpoint "{slug}" from the element')
def step_remove_viewpoint(context, slug):
    context.elem.remove_viewpoint(slug)


@then('element.viewpoints does not contain "{slug}"')
def step_element_lacks_viewpoint(context, slug):
    assert slug not in context.elem.viewpoints


@when('I set the primary viewpoint of the view to "{slug}"')
def step_set_primary_viewpoint(context, slug):
    context.view.set_primary_viewpoint(slug)


@then('view.primary_viewpoint equals "{slug}"')
def step_view_primary_viewpoint(context, slug):
    assert context.view.primary_viewpoint == slug


@given('I have a model with two elements')
def step_model_two_elements(context):
    context.model = Model(name='Test')
    context.elem_a = context.model.add(ArchiType.BusinessActor, 'Actor A')
    context.elem_b = context.model.add(ArchiType.BusinessActor, 'Actor B')


@given('element A is assigned to viewpoint "{slug}"')
def step_elem_a_assigned(context, slug):
    context.elem_a.assign_viewpoint(slug)


@given('element B is assigned to viewpoint "{slug}"')
def step_elem_b_assigned(context, slug):
    context.elem_b.assign_viewpoint(slug)


@when('I call model.get_elements_by_viewpoint("{slug}")')
def step_filter_elements(context, slug):
    context.result = context.model.get_elements_by_viewpoint(slug)


@then('only element A is returned')
def step_only_a_returned(context):
    assert context.elem_a in context.result
    assert context.elem_b not in context.result


@given('I have a model with two views')
def step_model_two_views(context):
    context.model = Model(name='Test')
    context.view_a = context.model.add(ArchiType.View, 'View A')
    context.view_b = context.model.add(ArchiType.View, 'View B')


@given('view A has primary viewpoint "{slug}"')
def step_view_a_vp(context, slug):
    context.view_a.set_primary_viewpoint(slug)


@given('view B has primary viewpoint "{slug}"')
def step_view_b_vp(context, slug):
    context.view_b.set_primary_viewpoint(slug)


@when('I call model.get_views_by_viewpoint("{slug}")')
def step_filter_views(context, slug):
    context.result = context.model.get_views_by_viewpoint(slug)


@then('only view A is returned')
def step_only_view_a(context):
    assert context.view_a in context.result
    assert context.view_b not in context.result


@when('I assign an invalid viewpoint slug "{slug}" to the element')
def step_assign_invalid(context, slug):
    try:
        context.elem.assign_viewpoint(slug)
        context.error = None
    except ValueError as e:
        context.error = e


@then('a ValueError is raised')
def step_value_error_raised(context):
    assert context.error is not None
    assert isinstance(context.error, ValueError)


# ---------------------------------------------------------------------------
# Round-trip steps
# ---------------------------------------------------------------------------

@given('I have a model with an element assigned to viewpoint "{slug}"')
def step_model_element_with_viewpoint(context, slug):
    context.model = Model(name='VP RT Test')
    context.elem = context.model.add(ArchiType.BusinessActor, 'Test Actor')
    context.elem.assign_viewpoint(slug)
    context.viewpoint_slug = slug


@when('I export the model to .archimate format and re-import it')
def step_export_reimport_archi(context):
    with tempfile.NamedTemporaryFile(suffix='.archimate', delete=False) as f:
        context.tmp_path = f.name
    context.model.write(context.tmp_path)
    context.model2 = Model(name='Reload')
    context.model2.read(context.tmp_path)
    os.unlink(context.tmp_path)


@then('the re-imported element has viewpoint "{slug}"')
def step_reimported_has_viewpoint(context, slug):
    actors = [e for e in context.model2.elements if e.name == 'Test Actor']
    assert len(actors) == 1
    assert slug in actors[0].viewpoints


@when('I export the model to OpenGroup format and re-import it')
def step_export_reimport_opengroup(context):
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as f:
        context.tmp_path = f.name
    archimate_writer(context.model, context.tmp_path)
    context.model2 = Model(name='Reload')
    context.model2.read(context.tmp_path)
    os.unlink(context.tmp_path)


@given('I have an .archimate file without viewpoint metadata')
def step_legacy_archimate_file(context):
    context.fixture_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'fixtures',
        'viewpoint_v3', 'no_viewpoint.archimate'
    )
    # Resolve to absolute path
    context.fixture_path = os.path.abspath(context.fixture_path)


@when('I import the legacy viewpoint file')
def step_import_legacy_file(context):
    context.model = Model(name='Imported')
    context.model.read(context.fixture_path)


@then('all elements are imported successfully with empty viewpoints lists')
def step_imported_elements_empty_viewpoints(context):
    elems = context.model.elements
    assert len(elems) > 0
    for e in elems:
        assert e.viewpoints == []


@given('I have a view with primary viewpoint "{slug}"')
def step_view_with_primary_viewpoint(context, slug):
    context.model = Model(name='VP View RT Test')
    context.actor = context.model.add(ArchiType.BusinessActor, 'Actor')
    context.view = context.model.add(ArchiType.View, 'Test View')
    context.view.set_primary_viewpoint(slug)
    context.viewpoint_slug = slug


@when('I export and re-import the model')
def step_export_reimport_model(context):
    with tempfile.NamedTemporaryFile(suffix='.archimate', delete=False) as f:
        context.tmp_path = f.name
    context.model.write(context.tmp_path)
    context.model2 = Model(name='Reload')
    context.model2.read(context.tmp_path)
    os.unlink(context.tmp_path)


@then("the view's primary viewpoint is still \"{slug}\"")
def step_view_primary_still(context, slug):
    views = context.model2.find_views('Test View')
    assert len(views) == 1
    assert views[0].primary_viewpoint == slug
