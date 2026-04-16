from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model
from src.pyArchimate.writers.csvWriter import csv_writer
from tests._helpers import simple_archimate_model


def test_csv_writer_generates_expected_files(tmp_path):
    model = simple_archimate_model()
    destination = tmp_path / 'export.csv'
    csv_writer(model, str(destination))
    for suffix in ('elements', 'relations', 'properties'):
        assert (tmp_path / f'export_{suffix}.csv').exists()


def test_csv_writer_with_relationship_properties(tmp_path):
    """Covers the relationship-properties loop in csvWriter (lines 59-62)."""
    m = Model('csv-props')
    a = m.add(ArchiType.ApplicationComponent, 'A')
    b = m.add(ArchiType.ApplicationService, 'B')
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b)
    rel.prop('priority', 'high')
    destination = tmp_path / 'props.csv'
    csv_writer(m, str(destination))
    props_file = tmp_path / 'props_properties.csv'
    assert props_file.exists()
