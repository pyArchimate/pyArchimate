from pathlib import Path

import pytest
from lxml import etree

from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.readers.archiReader import archi_reader

FIXTURES = Path(__file__).resolve().parents[1] / "integration" / "fixtures"


def test_archi_reader_parses_sample_file():
    fixture_file = FIXTURES / "test.archimate"
    if not fixture_file.exists():
        pytest.skip("test.archimate fixture is not present")
    root = etree.parse(str(fixture_file)).getroot()
    model = Model("archi-sample")
    archi_reader(model, root)
    assert model.name == "test"
    assert len(model.elements) > 0
