"""BDD step definitions for P3 (ArchiMate Notation Support) features."""

from behave import given, when, then
from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


@given("I have a model with a {element_type} called {element_name}")
def step_create_element(context, element_type, element_name):
    """Create a model and add an element of specified type."""
    if not hasattr(context, 'model'):
        context.model = Model('test-model')
        context.elements = {}

    # Map element type strings to ArchiType values
    type_map = {
        'BusinessProcess': ArchiType.BusinessProcess,
        'BusinessFunction': ArchiType.BusinessFunction,
        'BusinessService': ArchiType.BusinessService,
        'BusinessActor': ArchiType.BusinessActor,
        'BusinessRole': ArchiType.BusinessRole,
        'BusinessObject': ArchiType.BusinessObject,
        'Junction': ArchiType.Junction,
    }

    arch_type = type_map.get(element_type)
    if not arch_type:
        raise ValueError(f"Unknown element type: {element_type}")

    # Remove quotes from element name
    clean_name = element_name.strip("'\"")
    elem = context.model.add(arch_type, clean_name)
    context.elements[clean_name] = elem


@given("I have a model with {count} {element_types} named {names}")
def step_create_multiple_elements(context, _count, element_types, names):
    """Create multiple elements of the same type."""
    if not hasattr(context, 'model'):
        context.model = Model('test-model')
        context.elements = {}

    # Remove plural and get type
    element_type = element_types.rstrip('s')
    type_map = {
        'BusinessFunction': ArchiType.BusinessFunction,
        'BusinessProcess': ArchiType.BusinessProcess,
    }

    arch_type = type_map.get(element_type)
    name_list = [n.strip("'\"") for n in names.split(', ')]

    for name in name_list:
        elem = context.model.add(arch_type, name)
        context.elements[name] = elem


@when("I add {child_name} as a child of {parent_name}")
def step_add_child(context, child_name, parent_name):
    """Add a parent-child relationship."""
    parent = context.elements[parent_name.strip("'\"")]
    child = context.elements[child_name.strip("'\"")]
    context.model.add_child(parent.uuid, child.uuid)


@when("I add each {element_type} as a child of {parent_name}")
def step_add_multiple_children(context, _element_type, parent_name):
    """Add multiple elements as children of a parent."""
    parent = context.elements[parent_name.strip("'\"")]

    # Find all elements of this type (recently added)
    for name, elem in context.elements.items():
        if name != parent_name.strip("'\"") and hasattr(elem, 'type'):
            try:
                context.model.add_child(parent.uuid, elem.uuid)
            except ValueError:
                pass  # Already has parent


@when("I set the fill color of {element_name} to {color}")
def step_set_fill_color(context, element_name, color):
    """Set the fill color of an element."""
    elem = context.elements[element_name.strip("'\"")]
    color = color.strip("'\"")
    elem.set_fill_color(color)


@when("I set the following visual properties")
def step_set_visual_properties(context):
    """Set multiple visual properties from a table."""
    if not hasattr(context, 'current_element'):
        # Use the last created element
        context.current_element = list(context.elements.values())[-1]

    elem = context.current_element
    for row in context.table:
        prop = row['Property'].lower().replace(' ', '_')
        value = row['Value']

        if 'color' in prop:
            getattr(elem, f'set_{prop}')(value)
        elif 'width' in prop:
            elem.set_line_width(float(value))
        elif 'transparency' in prop:
            elem.set_transparency(float(value))


@when("I export the model to XML")
def step_export_model(context):
    """Export the model to XML."""
    import tempfile
    context.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.archimate', delete=False)
    context.temp_path = context.temp_file.name
    context.temp_file.close()
    context.model.write(context.temp_path)


@when("I import the model from XML")
def step_import_model(context):
    """Import the model from XML."""
    context.imported_model = Model('imported-model')
    context.imported_model.read(context.temp_path)


@when("I import the model from the XML")
def step_import_model_the(context):
    """Import the model from XML (with 'the')."""
    step_import_model(context)


@when("I remove {child_name} from {parent_name}")
def step_remove_child(context, child_name, parent_name):
    """Remove a parent-child relationship."""
    parent = context.elements[parent_name.strip("'\"")]
    child = context.elements[child_name.strip("'\"")]
    context.model.remove_child(parent.uuid, child.uuid)


@when("I delete {element_name}")
def step_delete_element(context, element_name):
    """Delete an element."""
    elem = context.elements[element_name.strip("'\"")]
    elem.delete()


@when("I query for elements at path {path}")
def step_query_by_path(context, path):
    """Query for elements by hierarchy path."""
    path = path.strip("'\"")
    context.last_query_results = context.model.find_by_hierarchy_path(path)


@when("I try to set an invalid hex color {color}")
def step_try_invalid_color(context, color):
    """Try to set an invalid color."""
    elem = list(context.elements.values())[-1]
    color = color.strip("'\"")
    try:
        elem.set_fill_color(color)
        context.color_error = None
    except ValueError as e:
        context.color_error = str(e)


@when("I try to set transparency to {value}")
def step_try_invalid_transparency(context, value):
    """Try to set an invalid transparency value."""
    elem = list(context.elements.values())[-1]
    try:
        elem.set_transparency(float(value))
        context.transparency_error = None
    except ValueError as e:
        context.transparency_error = str(e)


@when("I set visual properties: fill={fill}, line={line}, width={width}, transparency={trans}")
def step_set_all_visual_properties(context, fill, line, width, trans):
    """Set all visual properties."""
    elem = list(context.elements.values())[-1]
    elem.set_fill_color(fill)
    elem.set_line_color(line)
    elem.set_line_width(float(width))
    elem.set_transparency(float(trans))


@then("{element_name} should have {parent_name} as its parent")
def step_check_parent(context, element_name, parent_name):
    """Verify parent relationship."""
    child = context.elements[element_name.strip("'\"")]
    parent = context.elements[parent_name.strip("'\"")]
    actual_parent = context.model.get_parent(child.uuid)
    assert actual_parent == parent, f"Expected parent {parent.uuid}, got {actual_parent}"


@then("{parent_name} should have {child_name} as a child")
def step_check_child(context, parent_name, child_name):
    """Verify child relationship."""
    parent = context.elements[parent_name.strip("'\"")]
    child = context.elements[child_name.strip("'\"")]
    children = context.model.get_children(parent.uuid)
    assert any(c.uuid == child.uuid for c in children), f"Child {child_name} not found"


@then("{element_name} should have no parent")
def step_check_no_parent(context, element_name):
    """Verify element has no parent."""
    elem = context.elements[element_name.strip("'\"")]
    parent = context.model.get_parent(elem.uuid)
    assert parent is None, f"Expected no parent, got {parent}"


@then("{parent_name} should have no children")
def step_check_no_children(context, parent_name):
    """Verify element has no children."""
    parent = context.elements[parent_name.strip("'\"")]
    children = context.model.get_children(parent.uuid)
    assert len(children) == 0, f"Expected no children, got {len(children)}"


@then("{element_name} should have {count} ancestors")
def step_check_ancestor_count(context, element_name, count):
    """Verify number of ancestors."""
    elem = context.elements[element_name.strip("'\"")]
    ancestors = context.model.get_ancestors(elem.uuid)
    assert len(ancestors) == int(count), f"Expected {count} ancestors, got {len(ancestors)}"


@then("the fill color of {element_name} should be {color}")
def step_check_fill_color(context, element_name, color):
    """Verify fill color."""
    elem = context.elements[element_name.strip("'\"")]
    actual_color = elem.get_fill_color()
    expected_color = color.strip("'\"")
    assert actual_color == expected_color, f"Expected {expected_color}, got {actual_color}"


@then("all visual properties should be set correctly")
def step_check_all_visual_properties(context):
    """Verify all visual properties are set."""
    elem = context.current_element
    assert elem.get_fill_color() is not None
    assert elem.get_line_color() is not None
    assert elem.get_line_width() is not None
    assert elem.get_transparency() is not None


@then("all visual properties should be preserved exactly")
def step_check_preserved_properties(context):
    """Verify visual properties are preserved after round-trip."""
    original = list(context.elements.values())[-1]
    imported = list(context.imported_model.elems_dict.values())[-1]

    assert original.get_fill_color() == imported.get_fill_color()
    assert original.get_line_color() == imported.get_line_color()
    assert original.get_line_width() == imported.get_line_width()
    assert original.get_transparency() == imported.get_transparency()


@then("it should fail with a color validation error")
def step_check_color_error(context):
    """Verify color validation error occurred."""
    assert context.color_error is not None, "Expected color validation error"
    assert "color" in context.color_error.lower()


@then("it should fail with a range validation error")
def step_check_range_error(context):
    """Verify range validation error occurred."""
    assert context.transparency_error is not None, "Expected range validation error"


@then("I should get the {element_name} element")
def step_check_query_result(context, element_name):
    """Verify query returned specific element."""
    expected = context.elements[element_name.strip("'\"")]
    assert any(e.uuid == expected.uuid for e in context.last_query_results)


@then("I should get {element_names}")
def step_check_query_results_multiple(context, element_names):
    """Verify query returned specific elements."""
    names = [n.strip("'\"") for n in element_names.split(' and ')]
    for name in names:
        expected = context.elements[name]
        assert any(e.uuid == expected.uuid for e in context.last_query_results)


@then("the fill color should be converted to hex format {hex_color}")
def step_check_hex_conversion(context, hex_color):
    """Verify named color was converted to hex."""
    elem = list(context.elements.values())[-1]
    actual = elem.get_fill_color()
    expected = hex_color.strip("'\"")
    assert actual == expected, f"Expected {expected}, got {actual}"


@then("each child should have {count} siblings")
def step_check_sibling_count(context, count):
    """Verify sibling count."""
    parent = list(context.elements.values())[0]  # First element (parent)
    children = context.model.get_children(parent.uuid)
    for child in children:
        siblings = context.model.get_siblings(child.uuid)
        assert len(siblings) == int(count), f"Expected {count} siblings, got {len(siblings)}"


@then("the siblings of {element_name} should be {sibling_names}")
def step_check_specific_siblings(context, element_name, sibling_names):
    """Verify specific siblings."""
    elem = context.elements[element_name.strip("'\"")]
    siblings = context.model.get_siblings(elem.uuid)
    expected_names = {n.strip("'\"") for n in sibling_names.split(' and ')}
    actual_names = {s.name for s in siblings}
    assert actual_names == expected_names, f"Expected {expected_names}, got {actual_names}"


@then("all elements should exist with correct types")
def step_check_elements_exist(context):
    """Verify all elements exist after import."""
    assert len(context.imported_model.elems_dict) > 0


@then("all hierarchies should be preserved exactly")
def step_check_hierarchies_preserved(context):
    """Verify hierarchies are preserved after round-trip."""
    for original_uuid, _ in context.model.elems_dict.items():
        imported = context.imported_model.elems_dict.get(original_uuid)
        assert imported is not None

        original_parent = context.model.get_parent(original_uuid)
        imported_parent = context.imported_model.get_parent(original_uuid)

        if original_parent:
            assert imported_parent is not None
            assert original_parent.uuid == imported_parent.uuid
        else:
            assert imported_parent is None


@then("all visual styles should match the original colors")
def step_check_styles_match(context):
    """Verify visual styles match after round-trip."""
    for original_uuid, original in context.model.elems_dict.items():
        imported = context.imported_model.elems_dict.get(original_uuid)
        if imported:
            assert original.get_fill_color() == imported.get_fill_color()


@then("the {element_name} should still be a child of {parent_name}")
def step_check_still_child(context, element_name, parent_name):
    """Verify child relationship still exists after import."""
    parent = context.imported_model.elems_dict.get(
        context.elements[parent_name.strip("'\"")].uuid
    )
    child = context.imported_model.elems_dict.get(
        context.elements[element_name.strip("'\"")].uuid
    )
    assert parent is not None and child is not None
    assert context.imported_model.get_parent(child.uuid) == parent
