from typing import cast

from src.pyArchimate.pyArchimate import ArchiType, Model, Point
from src.pyArchimate.view import View


def simple_archimate_model(name: str = 'unit model') -> Model:
    model = Model(name)
    a = model.add(ArchiType.ApplicationComponent, 'Component A')
    b = model.add(ArchiType.ApplicationService, 'Service B')
    model.add_relationship(source=a, target=b, rel_type=ArchiType.Flow, name='flows to')
    model.prop('team', 'pyarch')
    return model


def model_with_views(name: str = 'view model') -> Model:
    """A model with diverse elements, relationships, and a richly styled view.

    Designed to maximise code-path coverage in both writers (archimateWriter
    and archiWriter) by exercising: element properties, typed relationships
    (Access / Influence / Association), relationship properties and folders,
    Container and Label nodes, node styling, and connections with line colour
    and bendpoints.
    """
    model = Model(name)
    model.desc = 'test description'

    # Elements — one with properties; include Junction and Physical types for writer branches
    a = model.add(ArchiType.ApplicationComponent, 'Component A', desc='comp desc')
    a.prop('owner', 'team-a')
    b = model.add(ArchiType.ApplicationService, 'Service B')
    c = model.add(ArchiType.ApplicationFunction, 'Function C')
    junc = model.add(ArchiType.Junction)  # covers archimateWriter "Junction → Other" branch
    junc.junction_type = 'or'
    model.add(ArchiType.Equipment, 'ADevice')  # Physical type → covers "Physical → Technology" branch

    # Serving relationship (already present before)
    rel = model.add_relationship(source=a, target=b, rel_type=ArchiType.Serving, name='serves')
    rel.desc = 'rel desc'
    rel.prop('priority', 'high')
    rel.folder = '/Relations'

    # Access relationship with access_type
    data = model.add(ArchiType.DataObject, 'DataObj')
    access_rel = model.add_relationship(source=a, target=data, rel_type=ArchiType.Access)
    access_rel.access_type = 'Read'

    # Influence relationship with strength
    inf_rel = model.add_relationship(source=b, target=c, rel_type=ArchiType.Influence)
    inf_rel.influence_strength = '5'

    # Association with is_directed
    assoc_rel = model.add_relationship(source=a, target=c, rel_type=ArchiType.Association)
    assoc_rel.is_directed = True

    # View with folder
    view = cast(View, model.add(ArchiType.View, 'Overview'))
    view.desc = 'view desc'
    view.prop('owner', 'test')
    view.folder = '/Views/App'

    # Element nodes
    na = view.add(ref=a.uuid, x=10, y=10, w=120, h=55)
    nb = view.add(ref=b.uuid, x=200, y=10, w=120, h=55)

    # Style node-a to exercise color/font code paths
    na.fill_color = '#FF0000'
    na.line_color = '#000000'
    na.font_name = 'Arial'
    na.font_size = 10
    na.font_color = '#333333'
    na.opacity = 80
    na.lc_opacity = 90
    na.label_expression = '{name}'
    na.text_alignment = '2'
    na.text_position = '2'

    # Container node (non-Element)
    container = view.add(ref=None, node_type='Container', label='My Group')
    container.x = 400
    container.y = 10
    container.w = 200
    container.h = 150

    # Label node
    label_node = view.add(ref=None, node_type='Label', label='A note')
    label_node.x = 10
    label_node.y = 100
    label_node.w = 120
    label_node.h = 40

    # Connection with line_color and a bendpoint
    conn = view.add_connection(ref=rel.uuid, source=na, target=nb)
    conn.line_color = '#0000FF'
    conn.add_bendpoint(Point(110, 50))

    return model
