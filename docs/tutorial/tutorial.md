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
print(f"Model Type: {model.type}")   # Model
print(f"Model Name: {model.name}")   # e-commerce platform
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

print(f"Number of elements: {len(model.elements)}")       # 3
print(f"Number of relationships: {len(model.relationships)}")  # 1
print(f"Relationship type: {rel.type}")                  # Serving
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

app_components = [
    e for e in model.elements if e.type == "ApplicationComponent"]
print(f"Number of elements: {len(model.elements)}")  # 3
print(f"Number of application components: {len(app_components)}")  # 2
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

print(f"Number of nodes in view: {len(view.nodes)}")  # 2
print(f"Number of connections in view: {len(view.conns)}")  # 1
```

**Best practice:** Keep each view focused on a single concern or audience.
Elements live once in the model layer; add the same element to multiple views
rather than creating duplicates.

---

## 6. Saving and Loading a Model

`model.write()` persists to Archi format (`.archimate`) by default.
`model.read()` loads any supported format.

```python
from pyArchimate import Model, ArchiType

model = Model("roundtrip demo")
model.add(ArchiType.ApplicationComponent, "Inventory Service")
model.add(ArchiType.ApplicationService, "Check Stock")

model.write("demo.archimate")

reloaded = Model("reloaded")
reloaded.read("demo.archimate")
print(f"Number of elements after reload: {len(reloaded.elements)}")  # 2
for elem in reloaded.elements:
    print(f"  {elem.type}: {elem.name}")
# ApplicationComponent: Inventory Service
# ApplicationService: Check Stock
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
print(f"Found element: {by_name[0].name}")  # Auth Service

outbound = model.find_relationships(ArchiType.Serving, app, direction="out")
print(f"Number of outbound Serving relationships: {len(outbound)}")  # 1
```

---

## 8. Relationship Type Validation

`check_valid_relationship()` tests whether a relationship type is permitted
between two element types under the ArchiMate rules. `get_default_rel_type()`
returns the most appropriate relationship type for a given source/target pair.
`model.check_invalid_conn()` audits every connection in the model at once.

```python
from pyArchimate import (
    Model, ArchiType,
    check_valid_relationship, get_default_rel_type,
    ArchimateRelationshipError,
)

# Query the default relationship between two element types
default = get_default_rel_type("ApplicationComponent", "ApplicationService")
print(f"The default relationship between 'ApplicationComponent' and 'ApplicationService' is: '{default}'")  # Serving

# Validate a specific combination (returns silently if valid)
check_valid_relationship(
    "Serving", "ApplicationComponent", "ApplicationService")

# Invalid combination raises (or logs) an error
try:
    check_valid_relationship(
        "Composition", "ApplicationService", "BusinessActor", raise_flg=True
    )
except ArchimateRelationshipError as exc:
    print(exc)  # Invalid Relationship type ...

# Validate all connections in a model at once
model = Model("validation demo")
app = model.add(ArchiType.ApplicationComponent, "Order Service")
svc = model.add(ArchiType.ApplicationService, "Place Order")
rel = model.add_relationship(ArchiType.Serving, source=app, target=svc)
view = model.add(ArchiType.View, "App Layer")
node_app = view.add(app, x=0, y=0, w=120, h=55)
node_svc = view.add(svc, x=200, y=0, w=120, h=55)
view.add_connection(rel, source=node_app, target=node_svc)

invalid_conns = model.check_invalid_conn()
print(f"Number of invalid connections: {len(invalid_conns)}")  # 0
```

---

## 9. Element and Relationship Properties

Arbitrary key/value metadata can be attached to any element, relationship, or
view with `prop()`. `props` returns the full dictionary. `remove_prop()` deletes
a key. The `desc` attribute holds free-text documentation.

```python
from pyArchimate import Model, ArchiType

model = Model("properties demo")
app = model.add(ArchiType.ApplicationComponent, "Payment Service")

# Set a description
app.desc = "Handles payment processing for the checkout flow."

# Set and read properties
app.prop("team", "Payments")
app.prop("tier", "critical")
print(f"Team property: {app.prop('team')}")   # Payments
print(f"All properties: {app.props}")          # {'team': 'Payments', 'tier': 'critical'}

# Remove a property
app.remove_prop("tier")
print(f"Properties after 'tier' removal: {app.props}")  # {'team': 'Payments'}

# Relationships support the same interface
svc = model.add(ArchiType.ApplicationService, "Charge Card")
rel = model.add_relationship(ArchiType.Serving, source=app, target=svc)
rel.desc = "Exposes the charge-card capability as a service."
rel.prop("sla", "99.9%")
print(f"SLA property: {rel.prop('sla')}")    # 99.9%
```

---

## 10. Exporting to Different Formats

`model.write()` accepts a `writer` argument from the `Writers` enum to select
the output format. The default is `Writers.archimate` (Archi tool `.archimate`).
Use `Writers.csv` for spreadsheet export or `Writers.archi` for the OpenGroup
XML exchange format.

```python
from pyArchimate import Model, ArchiType, Writers

model = Model("export demo")
model.add(ArchiType.ApplicationComponent, "Auth Service")
model.add(ArchiType.ApplicationService, "Authenticate")

# Default: Archi tool format
model.write("export_demo.archimate")

# OpenGroup XML exchange format
model.write("export_demo.xml", writer=Writers.archi)

# CSV (useful for spreadsheet analysis)
model.write("export_demo.csv", writer=Writers.csv)
```

---

## Intermediate

---

## 11. Merging Models

`model.merge()` loads a second file into an existing model, combining elements
and relationships. Elements with the same UUID are deduplicated; new ones are
added. Only formats that support merge (Archi and OpenGroup XML) are accepted.

```python
from pyArchimate import Model, ArchiType

# Build and save a base model
base = Model("base")
base.add(ArchiType.ApplicationComponent, "Auth Service")
base.write("base.archimate")

# Build and save an extension model
ext = Model("extension")
ext.add(ArchiType.ApplicationComponent, "Payment Service")
ext.write("extension.archimate")

# Merge extension into base
base.merge("extension.archimate")
print(f"Number of elements after merge: {len(base.elements)}")  # 2
```

---

## 12. Filtering Elements, Relationships, and Views

`filter_elements()`, `filter_relationships()`, and `filter_views()` accept a
predicate function and return matching objects. Use these when `find_elements()`
is too narrow — for example to match on properties, descriptions, or computed
attributes.

```python
from pyArchimate import Model, ArchiType

model = Model("filter demo")
auth = model.add(ArchiType.ApplicationComponent, "Auth Service")
pay  = model.add(ArchiType.ApplicationComponent, "Payment Service")
svc  = model.add(ArchiType.ApplicationService,  "Authenticate")
auth.prop("team", "identity")
pay.prop("team", "payments")

# Filter elements whose name contains "Service"
services = model.filter_elements(lambda e: "Service" in e.name)
print(f"Number of elements with 'Service' in name: {len(services)}")  # 3

# Filter by a custom property value
identity_team = model.filter_elements(lambda e: e.prop("team") == "identity")
print(f"Identity team element: {identity_team[0].name}")  # Auth Service

# Filter relationships by source type
model.add_relationship(ArchiType.Serving, source=auth, target=svc)
app_rels = model.filter_relationships(
    lambda r: r.source.type == "ApplicationComponent"
)
print(f"Number of relationships from ApplicationComponent: {len(app_rels)}")  # 1
```

---

## 13. Idempotent Element and Relationship Creation

`model.get_or_create_element()` returns an existing element or creates one if
`create_elem=True`. The equivalent `get_or_create_relationship()` does the same
for relationships. These are the right primitives for scripts that may run more
than once against the same model file.

```python
from pyArchimate import Model, ArchiType

model = Model("idempotent demo")

# First call creates the element; second call returns the same object
svc1 = model.get_or_create_element("ApplicationComponent", "Order Service", create_elem=True)
svc2 = model.get_or_create_element("ApplicationComponent", "Order Service", create_elem=True)
print(f"Same element returned? {svc1.uuid == svc2.uuid}")  # True
print(f"Number of elements: {len(model.elements)}")  # 1

# Same pattern for relationships
app = model.add(ArchiType.ApplicationComponent, "Auth Service")
ep  = model.add(ArchiType.ApplicationService,  "Login")
rel1 = model.get_or_create_relationship("Serving", None, app, ep, create_rel=True)
rel2 = model.get_or_create_relationship("Serving", None, app, ep, create_rel=True)
print(f"Same relationship returned? {rel1.uuid == rel2.uuid}")  # True
print(f"Number of relationships: {len(model.relationships)}")  # 1
```

---

## 14. Styling Nodes

Each `Node` exposes `fill_color` and `line_color` as hex strings (`#RRGGBB`).
`model.default_theme()` applies the standard ArchiMate or ARIS color palette
to every node in the model at once.

```python
from pyArchimate import Model, ArchiType

model = Model("styling demo")
app = model.add(ArchiType.ApplicationComponent, "Payment Service")
svc = model.add(ArchiType.ApplicationService, "Charge Card")
rel = model.add_relationship(ArchiType.Serving, source=app, target=svc)

view = model.add(ArchiType.View, "App Layer")
node_app = view.add(app, x=0,   y=0, w=140, h=60)
node_svc = view.add(svc, x=200, y=0, w=140, h=60)
view.add_connection(rel, source=node_app, target=node_svc)

# Apply the built-in ArchiMate color theme to all nodes
model.default_theme("archi")
print(f"Default fill color for ApplicationComponent: {node_app.fill_color}")

# Override a single node's color
node_svc.fill_color = "#cce5ff"
print(f"Custom fill color: {node_svc.fill_color}")  # #cce5ff
```

---

## 15. Nested Nodes (Containment)

A node can contain other nodes, representing structural nesting in a view.
Call `node.add()` on a parent node instead of `view.add()`. Use
`node.resize()` to automatically expand the parent to fit its children.

```python
from pyArchimate import Model, ArchiType

model = Model("nesting demo")
cluster = model.add(ArchiType.ApplicationComponent, "E-Commerce Platform")
auth    = model.add(ArchiType.ApplicationComponent, "Auth Service")
pay     = model.add(ArchiType.ApplicationComponent, "Payment Service")

view        = model.add(ArchiType.View, "Platform View")
node_cluster = view.add(cluster, x=0, y=0, w=400, h=200)

# Add children inside the parent node
node_auth = node_cluster.add(auth, x=20,  y=40, w=120, h=55)
node_pay  = node_cluster.add(pay,  x=180, y=40, w=120, h=55)

# Auto-resize the parent to fit its children with default padding
node_cluster.resize()

print(f"Number of child nodes: {len(node_cluster.nodes)}")  # 2
print(f"Parent expanded to fit children? {node_cluster.w > 120}")  # True
```

---

## Advanced

---

## 16. Connection Routing (Bendpoints)

Connections between nodes follow a straight line by default. Add `Point`
bendpoints to route connections around obstacles. The `l_shape()` and
`s_shape()` helpers add one or two bendpoints automatically.

```python
from pyArchimate import Model, ArchiType
from pyArchimate.view import Point

model = Model("bendpoint demo")
app = model.add(ArchiType.ApplicationComponent, "Order Service")
db  = model.add(ArchiType.ApplicationComponent, "Database")
rel = model.add_relationship(ArchiType.Association, source=app, target=db)

view     = model.add(ArchiType.View, "Routing Demo")
node_app = view.add(app, x=0,   y=0,   w=120, h=55)
node_db  = view.add(db,  x=300, y=200, w=120, h=55)
conn     = view.add_connection(rel, source=node_app, target=node_db)

# Route as an L-shape (one bendpoint)
conn.l_shape()
print(f"Number of bendpoints (L-shape): {len(conn.get_all_bendpoints())}")  # 1

# Route as an S-shape (two bendpoints)
conn.s_shape()
print(f"Number of bendpoints (S-shape): {len(conn.get_all_bendpoints())}")  # 2

# Manual bendpoint
conn.remove_all_bendpoints()
conn.add_bendpoint(Point(150, 50))
print(f"First bendpoint x-coordinate: {conn.get_bendpoint(0).x}")  # 150
```

---

## 17. Distributing Connections

When a node has many connections their endpoints can overlap. Call
`node.distribute_connections()` to spread them evenly along each edge of
the node, reducing visual clutter.

```python
from pyArchimate import Model, ArchiType

model = Model("distribute demo")
hub  = model.add(ArchiType.ApplicationComponent, "API Gateway")
svc1 = model.add(ArchiType.ApplicationService,  "Auth")
svc2 = model.add(ArchiType.ApplicationService,  "Search")
svc3 = model.add(ArchiType.ApplicationService,  "Orders")

rel1 = model.add_relationship(ArchiType.Serving, source=hub, target=svc1)
rel2 = model.add_relationship(ArchiType.Serving, source=hub, target=svc2)
rel3 = model.add_relationship(ArchiType.Serving, source=hub, target=svc3)

view     = model.add(ArchiType.View, "Gateway View")
node_hub = view.add(hub,  x=160, y=100, w=120, h=55)
ns1      = view.add(svc1, x=0,   y=250, w=120, h=55)
ns2      = view.add(svc2, x=160, y=250, w=120, h=55)
ns3      = view.add(svc3, x=320, y=250, w=120, h=55)
view.add_connection(rel1, source=node_hub, target=ns1)
view.add_connection(rel2, source=node_hub, target=ns2)
view.add_connection(rel3, source=node_hub, target=ns3)

# Spread connection endpoints evenly along the hub node's edges
node_hub.distribute_connections()
print(f"Number of outgoing connections from hub: {len(node_hub.out_conns())}")  # 3
```

---

## 18. Embedding Properties in Descriptions

Some external tools (such as ARIS) do not support ArchiMate concept properties.
`model.embed_props()` serialises all properties into each element's `desc`
field as a JSON tag so they survive a round-trip through tools that strip
the properties section. `model.expand_props()` reverses this on reload.

```python
from pyArchimate import Model, ArchiType

model = Model("embed demo")
app = model.add(ArchiType.ApplicationComponent, "Inventory Service")
app.prop("owner", "supply-chain-team")
app.prop("sla",   "99.5%")

# Embed properties into desc before exporting to a property-unaware tool
model.embed_props()
print(f"Properties serialised in desc? {'owner' in (app.desc or '')}")  # True
print(f"Properties dict after embed: {app.props}")  # {}

# Restore properties from desc after reloading
model.expand_props()
print(f"Owner property after expand: {app.prop('owner')}")  # supply-chain-team
```

---

## 19. Logging

pyArchimate logs diagnostics via Python's standard `logging` module. Use the
helpers to redirect output or adjust verbosity without configuring the logging
module directly.

```python
from pyArchimate import log_set_level, log_to_stderr
import logging

# Show all debug messages
log_set_level(logging.DEBUG)

# Send log output to stderr (useful in scripts that pipe stdout)
log_to_stderr()
```

---

## Next Steps

- Read the [API reference](https://pyarchimate.readthedocs.io/) for a complete API and concept reference.
- Browse the [ArchiMate 3.2 specification](https://pubs.opengroup.org/architecture/archimate3-doc/)
  for the full element and relationship catalogue.
