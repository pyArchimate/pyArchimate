from lxml import etree

import pytest

from src.pyArchimate import Model
from src.pyArchimate.readers.arisAMLreader import _id_of, aris_reader


def test_id_of_generates_expected_prefix():
    assert _id_of('group.123') == 'id-123'
    assert _id_of('single') == 'id-single'


def test_aris_reader_handles_empty_tree():
    root = etree.Element('document')
    model = Model('empty')
    with pytest.raises(SystemExit) as exc:
        aris_reader(model, root)
    assert exc.value.code == 1
