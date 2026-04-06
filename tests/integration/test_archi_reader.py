
from pathlib import Path

import pytest

from src.pyArchimate.pyArchimate import Model, Readers, Writers


def test_archi_reader(tmp_path: Path):
    fixtures_dir = Path(__file__).resolve().parent / "fixtures"
    input_file = fixtures_dir / "test.archimate"
    if not input_file.exists():
        pytest.skip("test.archimate fixture is not present")

    output_archimate = tmp_path / "out.archimate"
    output_xml = tmp_path / "out.xml"

    model = Model("test")
    model.read(str(input_file), reader=Readers.archi)
    model.check_invalid_conn()
    model.check_invalid_nodes()
    model.write(str(output_archimate), writer=Writers.archi)
    model.write(str(output_xml), writer=Writers.archimate)
    assert output_archimate.exists()
    assert output_xml.exists()
