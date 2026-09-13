"""Integration tests proving derivation capabilities never persist anything (spec 015)."""

import hashlib
from pathlib import Path

from src.pyArchimate import Model

FIXTURE = Path(__file__).parent.parent / "fixtures" / "valid_model.archimate"


def _build_chain_model():
    """Build A --Assignment--> B --Realization--> C, with valid element types."""
    model = Model()
    a = model.add("ApplicationCollaboration", name="A")
    b = model.add("ApplicationEvent", name="B")
    c = model.add("BusinessEvent", name="C")
    leg1 = model.add_relationship("Assignment", a, b)
    leg2 = model.add_relationship("Realization", b, c)
    return model, a, b, c, leg1, leg2


def _snapshot(model):
    return (
        dict(model.rels_dict),
        dict(model.elems_dict),
        dict(model.conns_dict),
        dict(model.views_dict),
    )


# --- T010: scan does not modify the model (User Story 1, SC-002) -----------


def test_check_derivable_duplicates_does_not_modify_model():
    model, a, b, c, leg1, leg2 = _build_chain_model()
    model.add_relationship("Realization", a, c)  # a duplicate to be found

    before = _snapshot(model)
    findings = model.check_derivable_duplicates()
    after = _snapshot(model)

    assert len(findings) == 1
    assert before == after


# --- T015: query does not modify the model or fixture file (User Story 2, SC-002) --


def test_derive_relationship_does_not_modify_model():
    model, a, b, c, leg1, leg2 = _build_chain_model()

    before = _snapshot(model)
    results = model.derive_relationship(a, c)
    after = _snapshot(model)

    assert len(results) == 1
    assert before == after


def test_derivation_capabilities_never_touch_the_source_file():
    original_bytes = FIXTURE.read_bytes()
    original_hash = hashlib.sha256(original_bytes).hexdigest()

    model = Model()
    model.read(str(FIXTURE))

    model.check_derivable_duplicates()
    elems = list(model.elems_dict.values())
    if len(elems) >= 2:
        model.derive_relationship(elems[0], elems[1])

    after_hash = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert after_hash == original_hash
