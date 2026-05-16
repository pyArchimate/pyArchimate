"""BDD step definitions for view duplication."""

from behave import given, when, then
from tests._helpers import model_with_views, simple_archimate_model


@given(u'a model with 5 nodes and 4 connections in a view')
def step_model_with_nodes_and_connections(context):
    """Create a model with a view containing 5 nodes and 4 connections."""
    context.model = model_with_views()
    context.view = context.model.views[0]

    # Add 5 nodes
    context.nodes = []
    for i in range(5):
        node = context.view.add(
            ref=context.model.add(concept_type='BusinessActor', name=f'Element {i}').uuid,
            x=i * 150,
            y=0,
            w=100,
            h=50
        )
        context.nodes.append(node)

    # Add 4 connections between consecutive nodes
    context.connections = []
    for i in range(4):
        conn = context.view.add_connection(
            ref=context.model.add_relationship(
                rel_type='Association',
                source=context.model.elems_dict[context.nodes[i].ref],
                target=context.model.elems_dict[context.nodes[i + 1].ref]
            ).uuid,
            source=context.nodes[i],
            target=context.nodes[i + 1]
        )
        context.connections.append(conn)


@given(u'a view named "{view_name}" with 5 nodes and 4 connections')
def step_view_with_name_and_content(context, view_name):
    """Replace the background model with a fresh one named as requested."""
    # Create a fresh model to override the background (using simple model to avoid pre-existing nodes)
    from src.pyArchimate.view import View
    context.model = simple_archimate_model()
    context.view = View(name=view_name, parent=context.model)
    context.model.views_dict[context.view.uuid] = context.view
    context.original_view = context.view

    # Add 5 nodes
    context.nodes = []
    for i in range(5):
        node = context.original_view.add(
            ref=context.model.add(concept_type='BusinessActor', name=f'Elem{view_name}_{i}').uuid,
            x=i * 150,
            y=0,
            w=100,
            h=50
        )
        context.nodes.append(node)

    # Add 4 connections
    context.connections = []
    for i in range(4):
        conn = context.original_view.add_connection(
            ref=context.model.add_relationship(
                rel_type='Association',
                source=context.model.elems_dict[context.nodes[i].ref],
                target=context.model.elems_dict[context.nodes[i + 1].ref]
            ).uuid,
            source=context.nodes[i],
            target=context.nodes[i + 1]
        )
        context.connections.append(conn)


@given(u'a view with 3 nodes')
def step_view_with_3_nodes(context):
    """Create a fresh view with 3 nodes, overriding the background."""
    # Create a fresh model for this specific scenario (using simple model to avoid pre-existing nodes)
    from src.pyArchimate.view import View
    context.model = simple_archimate_model()
    context.view = View(name="TestView", parent=context.model)
    context.model.views_dict[context.view.uuid] = context.view

    # Store original node positions for verification
    context.original_node_positions = []

    # Add 3 nodes
    context.nodes = []
    for i in range(3):
        node = context.view.add(
            ref=context.model.add(concept_type='BusinessActor', name=f'Element {i}').uuid,
            x=i * 150,
            y=0,
            w=100,
            h=50
        )
        context.nodes.append(node)
        context.original_node_positions.append((node.x, node.y))


@when(u'I duplicate the view without specifying a name')
def step_duplicate_view_without_name(context):
    """Duplicate the view using default naming."""
    context.original_name = context.original_view.name
    context.duplicated_view = context.original_view.duplicate()


@when(u'I duplicate the view with name "{new_name}"')
def step_duplicate_view_with_name(context, new_name):
    """Duplicate the view with a specific name."""
    context.original_name = context.original_view.name
    context.duplicated_view = context.original_view.duplicate(name=new_name)


@when(u'I duplicate the view')
def step_duplicate_view(context):
    """Duplicate the current view."""
    context.original_name = context.view.name
    context.duplicated_view = context.view.duplicate()


@when(u'modify a node position in the duplicate')
def step_modify_node_position(context):
    """Modify a node position in the duplicated view."""
    if context.duplicated_view.nodes:
        # Move the first node to a different position
        context.modified_node = context.duplicated_view.nodes[0]
        context.original_x = context.modified_node.x
        context.original_y = context.modified_node.y
        context.modified_node.x = context.original_x + 100
        context.modified_node.y = context.original_y + 100


@then(u'a new view is created with name "{expected_name}"')
def step_new_view_created_with_name(context, expected_name):
    """Verify that a new view was created with the expected name."""
    assert hasattr(context, 'duplicated_view'), "No duplicated view found"
    assert context.duplicated_view.name == expected_name, \
        f"Expected name '{expected_name}', got '{context.duplicated_view.name}'"


@then(u'the new view has 5 nodes')
def step_new_view_has_5_nodes(context):
    """Verify the duplicated view has 5 nodes."""
    assert len(context.duplicated_view.nodes) == 5, \
        f"Expected 5 nodes, got {len(context.duplicated_view.nodes)}"


@then(u'the new view has 4 connections')
def step_new_view_has_4_connections(context):
    """Verify the duplicated view has 4 connections."""
    assert len(context.duplicated_view.conns) == 4, \
        f"Expected 4 connections, got {len(context.duplicated_view.conns)}"


@then(u'the new view has 5 nodes and 4 connections')
def step_new_view_has_nodes_and_connections(context):
    """Verify the duplicated view has 5 nodes and 4 connections."""
    assert len(context.duplicated_view.nodes) == 5, \
        f"Expected 5 nodes, got {len(context.duplicated_view.nodes)}"
    assert len(context.duplicated_view.conns) == 4, \
        f"Expected 4 connections, got {len(context.duplicated_view.conns)}"


@then(u'both views are registered in the model')
def step_both_views_registered(context):
    """Verify both the original and duplicated views are registered in the model."""
    assert context.original_view in context.model.views, "Original view not in model"
    assert context.duplicated_view in context.model.views, "Duplicated view not in model"
    assert len(context.model.views) >= 2, f"Expected at least 2 views, got {len(context.model.views)}"


@then(u'the original view is unchanged')
def step_original_view_unchanged(context):
    """Verify the original view is unchanged after duplication."""
    assert context.original_view.name == context.original_name, \
        "Original view name was changed"
    assert len(context.original_view.nodes) == 5, \
        f"Original view nodes changed to {len(context.original_view.nodes)}"
    assert len(context.original_view.conns) == 4, \
        f"Original view connections changed to {len(context.original_view.conns)}"


@then(u"the original view's node position is unchanged")
def step_original_node_position_unchanged(context):
    """Verify the original view's nodes were not modified."""
    for i, node in enumerate(context.view.nodes):
        orig_x, orig_y = context.original_node_positions[i]
        assert node.x == orig_x, \
            f"Original node {i} x position changed from {orig_x} to {node.x}"
        assert node.y == orig_y, \
            f"Original node {i} y position changed from {orig_y} to {node.y}"


@then(u'the duplicate has the modified position')
def step_duplicate_has_modified_position(context):
    """Verify the modified node in the duplicate has the new position."""
    assert context.modified_node.x == context.original_x + 100, \
        f"Expected x={context.original_x + 100}, got {context.modified_node.x}"
    assert context.modified_node.y == context.original_y + 100, \
        f"Expected y={context.original_y + 100}, got {context.modified_node.y}"
