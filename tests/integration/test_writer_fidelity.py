"""Round-trip writer fidelity tests (T002).

Each test loads a fixture file into a model, then writes it twice with the
same writer and asserts that both outputs produce identical canonical XML
(modulo auto-generated folder IDs which archi_writer regenerates on every
call by design).  This confirms each writer is semantically deterministic —
the key invariant to protect during S3776 refactoring.
"""

import pathlib

import pytest
from lxml import etree

from src.pyArchimate.model import Model
from src.pyArchimate.writers.archiWriter import archi_writer
from src.pyArchimate.writers.archimateWriter import archimate_writer

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures"


def _strip_folder_ids(root: etree._Element) -> None:
    """Remove auto-generated id attributes from <folder> elements in-place.

    archi_writer calls set_id() for each top-level folder, so folder IDs
    differ between calls even for the same model.  Stripping them allows a
    meaningful structural comparison.
    """
    for el in root.iter("folder"):
        el.attrib.pop("id", None)


def _canonical_from_file(path: str, strip_folder_ids: bool = False) -> bytes:
    with open(path, "rb") as fh:
        tree = etree.fromstring(fh.read())
    if strip_folder_ids:
        _strip_folder_ids(tree)
    return etree.tostring(tree, method="c14n")


def _load(fixture: str) -> Model:
    model = Model("fidelity")
    model.read(str(FIXTURES / fixture))
    return model


# ---------------------------------------------------------------------------
# archi_writer — same model, two writes, must match (folder IDs excluded)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fixture", ["myModel.archimate", "test.archimate"])
def test_archi_writer_is_deterministic(fixture, tmp_path):
    model = _load(fixture)
    out1 = str(tmp_path / "a1.archimate")
    out2 = str(tmp_path / "a2.archimate")
    archi_writer(model, out1)
    archi_writer(model, out2)
    assert _canonical_from_file(out1, strip_folder_ids=True) == _canonical_from_file(out2, strip_folder_ids=True), (
        f"archi_writer produced different output on two writes for {fixture}"
    )


# ---------------------------------------------------------------------------
# archimate_writer — same model, two writes, must match
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fixture", ["myModel.archimate", "test.archimate"])
def test_archimate_writer_is_deterministic(fixture, tmp_path):
    model = _load(fixture)
    out1 = str(tmp_path / "x1.xml")
    out2 = str(tmp_path / "x2.xml")
    archimate_writer(model, out1)
    archimate_writer(model, out2)
    assert _canonical_from_file(out1) == _canonical_from_file(out2), (
        f"archimate_writer produced different output on two writes for {fixture}"
    )
