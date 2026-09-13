# Quickstart: Validating Derived Relationships

## Prerequisites

- Repo dependencies installed: `poetry install`
- A `.archimate` or OpenGroup `.xml` model file to test against (or build one in-memory, as below)

## Scenario 1 — Scan for duplicate relationships (User Story 1)

```python
from pyArchimate import Model

model = Model()
a = model.add("ApplicationCollaboration", name="A")
b = model.add("ApplicationEvent", name="B")
c = model.add("BusinessEvent", name="C")

model.add_relationship("Assignment", a, b)
model.add_relationship("Realization", b, c)
# This one duplicates what the chain above already implies:
duplicate = model.add_relationship("Realization", a, c)

findings = model.check_derivable_duplicates()

assert len(findings) == 1
assert findings[0].relationship is duplicate
assert len(findings[0].implying_chains) == 1
```

**Expected outcome**: exactly one `DuplicateFinding`, citing the Assignment→Realization chain through B.

## Scenario 2 — Query the implied relationship on demand (User Story 2)

```python
from pyArchimate import Model

model = Model()
a = model.add("ApplicationCollaboration", name="A")
b = model.add("ApplicationEvent", name="B")
c = model.add("BusinessEvent", name="C")

model.add_relationship("Assignment", a, b)
model.add_relationship("Realization", b, c)
# No explicit relationship between A and C.

results = model.derive_relationship(a, c)

assert len(results) == 1
assert results[0].type == "Realization"
assert results[0].is_derived is True
assert "«derived»" in str(results[0])
```

**Expected outcome**: one `DerivedRelationship` between A and C, clearly marked as derived, with no relationship written to `model.rels_dict`.

## Scenario 3 — Verify no persistence occurs (SC-002)

```python
import filecmp
import shutil

from pyArchimate import Model

shutil.copy("tests/fixtures/sample.archimate", "/tmp/before.archimate")
model = Model()
model.read("tests/fixtures/sample.archimate")

model.check_derivable_duplicates()
some_elem_a, some_elem_b = list(model.elems_dict.values())[:2]
model.derive_relationship(some_elem_a, some_elem_b)

model.write("/tmp/after.archimate")
assert filecmp.cmp("/tmp/before.archimate", "/tmp/after.archimate", shallow=False)
```

**Expected outcome**: the exported file after running both derivation capabilities is byte-identical to the original — proving neither capability persisted anything.

## Scenario 4 — Out-of-scope relationship types are skipped (FR-008/FR-009)

```python
from pyArchimate import Model

model = Model()
a = model.add("ApplicationCollaboration", name="A")
b = model.add("ApplicationEvent", name="B")
c = model.add("BusinessEvent", name="C")

model.add_relationship("Assignment", a, b)
model.add_relationship("Association", b, c)  # out-of-scope leg type

results = model.derive_relationship(a, c)
assert results == []
```

**Expected outcome**: no derivation is produced when either leg of the chain uses a relationship type outside the seven supported types.

## Running these as real tests

The scenarios above are formalized in:
- `tests/unit/test_derivation.py` (rule-table and chain-walking unit coverage)
- `tests/integration/test_derivation_roundtrip.py` (Scenario 3's file-immutability check, and end-to-end duplicate/query scenarios against fixture models)

Run with:

```bash
poetry run pytest tests/unit/test_derivation.py tests/integration/test_derivation_roundtrip.py -v
```
