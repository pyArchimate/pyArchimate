
from pathlib import Path

import pytest

from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.readers.arisAMLreader import aris_reader


def test_aris_aml_reader(tmp_path: Path):
    fixtures_dir = Path(__file__).parent.with_name("fixtures")
    cadp_file = fixtures_dir / "aris.aml"
    if not cadp_file.exists():
        pytest.skip("aris.aml fixture is not present")

    output_file = tmp_path / "out.xml"

    model = Model("imported")
    model.read(str(cadp_file), reader=aris_reader)
    model.write(str(output_file))
    assert output_file.exists()
