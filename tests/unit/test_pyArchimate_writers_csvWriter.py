from tests.unit._helpers import simple_archimate_model
from src.pyArchimate.writers.csvWriter import csv_writer


def test_csv_writer_generates_expected_files(tmp_path):
    model = simple_archimate_model()
    destination = tmp_path / 'export.csv'
    csv_writer(model, str(destination))
    for suffix in ('elements', 'relations', 'properties'):
        assert (tmp_path / f'export_{suffix}.csv').exists()
