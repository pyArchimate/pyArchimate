
from pathlib import Path

import pytest

from src.pyArchimate.pyArchimate import Model, Writers


def test_archi_writer(tmp_path: Path):
    fixtures_dir = Path(__file__).parent.with_name("fixtures")
    archimate_file = fixtures_dir / "myModel.archimate"
    if not archimate_file.exists():
        pytest.skip("myModel.archimate fixture is not present")

    output_archimate = tmp_path / "out.archimate"
    output_xml = tmp_path / "out.xml"

    model = Model("fixture")
    model.read(str(archimate_file))
    model.write(str(output_archimate), writer=Writers.archi)
    model.write(str(output_xml), writer=Writers.archimate)
    assert output_archimate.exists()
    assert output_xml.exists()
