# pyArchimate Tutorial

Minimum supported version: pyArchimate 1.0.x (Python 3.10+)

This tutorial covers the core operations of pyArchimate: creating, loading,
inspecting, modifying, and saving ArchiMate models.

Experienced ArchiMate users can skip straight to [Installation](#1-installation).

---

## ArchiMate Background

ArchiMate is an open enterprise architecture modelling language published by
The Open Group. It provides a standard notation for describing, analysing, and
visualising architectural structures and their relationships.

Three main layers:

| Layer | Purpose | Example elements |
|-------|---------|-----------------|
| Business | Processes, roles, information | BusinessActor, BusinessProcess |
| Application | Software components and services | ApplicationComponent, ApplicationService |
| Technology | Hardware, network, system software | Node, SystemSoftware, Path |

Core concepts:

- Element — a named architectural concept (actor, component, service, etc.)
- Relationship — a directed link between two elements
- View (Diagram) — a visual layout of selected elements and relationships

Common relationship types:

| Type | Meaning |
|------|---------|
| Serving | A provides a service to B |
| Composition | A is structurally composed of B (whole/part) |
| Realization | A realises B (implementation of a logical concept) |
| Assignment | An active element is assigned to a behaviour element |
| Association | Generic undirected or directed link |
| Flow | Information or control flow from A to B |
| Triggering | A causally triggers B |

References:

- [ArchiMate 3.2 Specification](https://pubs.opengroup.org/architecture/archimate3-doc/)
- [The Open Group ArchiMate Forum](https://www.opengroup.org/archimate-forum)

---

## 1. Installation

```text
pip install pyArchimate
```

Python 3.10 or later is required.

---

## 2. Creating a Model from Scratch

A `Model` is the root container for all elements, relationships, and views.

```python
from pyArchimate import Model, ArchiType

model = Model("e-commerce platform")
print(model.type)   # Model
print(model.name)   # e-commerce platform
```

---

## 3. Adding Elements and Relationships

Elements represent architectural concepts. Use `model.add()` with an `ArchiType`
and a name. Relationships are added with `model.add_relationship()`.

```python
from pyArchimate import Model, ArchiType

model = Model("e-commerce platform")

app = model.add(ArchiType.ApplicationComponent, "Order Service")
svc = model.add(ArchiType.ApplicationService, "Place Order")
actor = model.add(ArchiType.BusinessActor, "Customer")

rel = model.add_relationship(ArchiType.Serving, source=app, target=svc)

print(len(model.elements))       # 3
print(len(model.relationships))  # 1
print(rel.type)                  # Serving
```

**Best practice:** Use the most semantically precise relationship type.
Reserve `Association` for undirected or uncategorised links only.

---

## 4. Inspecting Model Contents

Iterate over `model.elements`, `model.relationships`, and `model.views` to
read model data.

```python
from pyArchimate import Model, ArchiType

model = Model("inspection demo")
model.add(ArchiType.ApplicationComponent, "Auth Service")
model.add(ArchiType.ApplicationComponent, "Payment Service")
model.add(ArchiType.ApplicationService, "Authenticate")

for elem in model.elements:
    print(f"{elem.type}: {elem.name}")

app_components = [e for e in model.elements if e.type == "ApplicationComponent"]
print(len(app_components))  # 2
```

---

## 5. Creating a View (Diagram)

A `View` holds `Node`s (visual representations of elements) and `Connection`s
(visual representations of relationships). Add a view with `ArchiType.View`.

```python
from pyArchimate import Model, ArchiType

model = Model("e-commerce platform")
app = model.add(ArchiType.ApplicationComponent, "Order Service")
svc = model.add(ArchiType.ApplicationService, "Place Order")
rel = model.add_relationship(ArchiType.Serving, source=app, target=svc)

view = model.add(ArchiType.View, "Application Layer")
node_app = view.add(app, x=0, y=0, w=120, h=55)
node_svc = view.add(svc, x=200, y=0, w=120, h=55)
conn = view.add_connection(rel, source=node_app, target=node_svc)

print(len(view.nodes))  # 2
print(len(view.conns))  # 1
```

**Best practice:** Keep each view focused on a single concern or audience.
Elements live once in the model layer; add the same element to multiple views
rather than creating duplicates.

---

## 6. Saving and Loading a Model

`model.write()` persists to Archi format (`.archimate`) by default.
`model.read()` loads any supported format.

```python
import os
import tempfile
from pyArchimate import Model, ArchiType

model = Model("roundtrip demo")
model.add(ArchiType.ApplicationComponent, "Inventory Service")
model.add(ArchiType.ApplicationService, "Check Stock")

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "demo.archimate")
    model.write(path)

    reloaded = Model("reloaded")
    reloaded.read(path)
    print(len(reloaded.elements))  # 2
    for elem in reloaded.elements:
        print(f"  {elem.type}: {elem.name}")
```

**Common mistake:** Do not reuse a `Model` instance for multiple `read()` calls.
Each load must start from a fresh `Model()` instance to avoid merging data.

---

## 7. Searching the Model

`find_elements()` searches by name or type. `find_relationships()` filters by
type and direction relative to a given element.

```python
from pyArchimate import Model, ArchiType

model = Model("search demo")
app = model.add(ArchiType.ApplicationComponent, "Auth Service")
svc = model.add(ArchiType.ApplicationService, "Authenticate")
model.add_relationship(ArchiType.Serving, source=app, target=svc)

by_name = model.find_elements(name="Auth Service")
print(by_name[0].name)  # Auth Service

outbound = model.find_relationships(ArchiType.Serving, app, direction="out")
print(len(outbound))  # 1
```

---

## Next Steps

- Read [AI.md](../AI.md) for a complete API and concept reference.
- Browse the [ArchiMate 3.2 specification](https://pubs.opengroup.org/architecture/archimate3-doc/)
  for the full element and relationship catalogue.
