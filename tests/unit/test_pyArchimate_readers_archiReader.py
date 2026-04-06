from pathlib import Path

from lxml import etree

from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.readers.archiReader import archi_reader

TEST_ROOT = Path(__file__).resolve().parents[1]


def test_archi_reader_parses_sample_file():
    root = etree.parse(str(TEST_ROOT / 'test.archimate')).getroot()
    model = Model('archi-sample')
    archi_reader(model, root)
    assert model.name == 'test'
    assert len(model.elements) > 0
