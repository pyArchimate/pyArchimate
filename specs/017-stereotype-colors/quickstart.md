# Quickstart: Validating Stereotype-Based Color Coding

Prerequisites: this feature implemented per `plan.md`/`data-model.md`/`contracts/public-api.md`; a Python environment with pyArchimate installed in editable mode (`poetry install`).

## 1. User Story 1 — Default color per stereotype

```python
from pyArchimate import Model, ArchiType

model = Model("ERM Demo")
threat = model.add_profile(name="Threat", concept="Driver")
threat.fill_color = "#E8453C"

e1 = model.add(ArchiType.Driver, "Inadequate power supply", profile="Threat")
e2 = model.add(ArchiType.Driver, "Unionized labor force", profile="Threat")

view = model.add(ArchiType.View, "Risk View")
n1 = view.add(e1, x=0, y=0, w=120, h=55)
n2 = view.add(e2, x=200, y=0, w=120, h=55)

assert n1.get_effective_fill_color() == "#e8453c"
assert n2.get_effective_fill_color() == "#e8453c"

threat.fill_color = None
assert n1.get_effective_fill_color() is None   # falls back to theme default when exported
```

**Expected outcome**: both elements resolve to the stereotype's color with zero per-element styling calls; clearing the stereotype's color removes it for both at once (spec Acceptance Scenarios 1–3 of User Story 1).

## 2. User Story 2 — Explicit override

```python
e1.set_fill_color("#8B0000")
assert n1.get_effective_fill_color() == "#8b0000"   # explicit element color wins over the stereotype

e1.set_fill_color(None)
threat.fill_color = "#F2A900"
assert n1.get_effective_fill_color() == "#f2a900"   # falls back to stereotype color again
```

**Expected outcome**: matches User Story 2's acceptance scenarios — explicit color always wins; removing it restores the stereotype fallback.

## 3. User Story 3 — Round-trip persistence

```python
from pyArchimate import Writers

model.write("/tmp/erm-demo.archimate")                      # Archi-native format (default writer)
reloaded = Model("reloaded")
reloaded.read("/tmp/erm-demo.archimate")
assert reloaded.get_profile("Threat").fill_color == "#f2a900"

model.write("/tmp/erm-demo.xml", writer=Writers.archi)      # OpenGroup Exchange XML format
reloaded2 = Model("reloaded-xml")
reloaded2.read("/tmp/erm-demo.xml")
assert reloaded2.get_profile("Threat").fill_color == "#f2a900"
```

**Expected outcome**: the stereotype's color survives a full save/reload round trip in both formats (SC-003). Run this against an existing pre-feature fixture file too (any `.archimate`/exchange XML file from the existing `tests/integration` fixtures) and confirm it still loads without error, with every profile's `fill_color` reading `None` (SC-005, FR-014).

## 4. User Story 4 — Automatic non-standard stereotype labels

```python
svg = view.to_svg()                 # default options — no show_stereotypes passed
assert "«Threat»" in svg            # e1/e2 carry a non-standard stereotype ("Threat" != "Driver")

plain = model.add(ArchiType.Driver, "Plain driver, no stereotype")
view.add(plain, x=0, y=200, w=120, h=55)
svg2 = view.to_svg()
assert "«" not in svg2.split("Plain driver")[1].split("</g>")[0]   # no label for the unstereotyped element
```

**Expected outcome**: matches User Story 4's acceptance scenarios — the label appears automatically for the non-standard "Threat" stereotype, with no `show_stereotypes` flag passed, and does not appear for an element with no stereotype.

## 5. Full regression check

Run the project's standard gates before considering this feature done (per the constitution's Quality Gates):

```bash
poetry run ruff check .
poetry run pyright
poetry run mypy src/pyArchimate
poetry run pytest tests/unit tests/integration
poetry run behave tests/features
```

All of the above must pass, including every pre-existing round-trip and SVG export test, to confirm this feature introduced no regression (Constitution VIII, Durability & Interoperability).
