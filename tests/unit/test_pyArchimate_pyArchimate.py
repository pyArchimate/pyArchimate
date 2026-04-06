from src.pyArchimate.pyArchimate import ArchiType, Model


def test_model_roundtrip_preserves_properties(tmp_path):
    model = Model('unit test')
    model.prop('custom', 'value')
    model.add(ArchiType.ApplicationComponent, 'UnitElement')
    destination = tmp_path / 'unit-model.archimate'
    model.write(str(destination))

    reloaded = Model('reload')
    reloaded.read(str(destination))
    assert reloaded.prop('custom') == 'value'
    assert any(elem.name == 'UnitElement' for elem in reloaded.elements)
