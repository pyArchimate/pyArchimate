from src.pyArchimate.pyArchimate import ArchiType, Model


def simple_archimate_model(name: str = 'unit model') -> Model:
    model = Model(name)
    a = model.add(ArchiType.ApplicationComponent, 'Component A')
    b = model.add(ArchiType.ApplicationService, 'Service B')
    model.add_relationship(source=a, target=b, rel_type=ArchiType.Flow, name='flows to')
    model.prop('team', 'pyarch')
    return model
