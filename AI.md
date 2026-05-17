# pyArchimate AI Reference

Machine-readable reference for the `pyArchimate` Python library. Intended for AI-assisted tooling,
documentation generation, and developer onboarding. No conversational language.

---

## Summary

A **Python-based engine for creating and manipulating enterprise architecture models using ArchiMate**,
enabling automation, integration, and "architecture-as-code" workflows.

It bridges the gap between **enterprise architecture modeling** and **modern software engineering
practices**, making architecture **scriptable, testable, and version-controlled**.

---

## Overview

**pyArchimate** is a lightweight Python library for **programmatically creating, manipulating,
and persisting enterprise architecture models** using the **ArchiMate standard** (The Open Group).

It acts as an **"Architecture-as-Code" toolkit**, enabling developers and architects to build,
modify, and manage ArchiMate models using Python instead of GUI-based tools.

The library provides a **structured object model aligned with the ArchiMate metamodel**, allowing
users to represent architectural concepts (elements, relationships, views) and serialize them into
standard **ArchiMate XML files**.

---

## Core Purpose

pyArchimate is intended to:

- Automate creation and maintenance of enterprise architecture models
- Enable integration of architecture modelling into **CI/CD pipelines or scripts**
- Provide a programmable alternative to tools like Archi
- Support **model transformation, validation, and generation workflows**
- Facilitate **Architecture-as-Code practices**

---

## Conceptual Model (Metamodel Support)

Key ArchiMate concepts implemented as Python objects:

### Model

Root container for all architectural data. Holds elements, relationships, and views.
Represents the full enterprise architecture.

### View (Diagram)

Visual representation of part of the model. Contains nodes and connections.
Used to communicate architecture to stakeholders.

### Element

Core building blocks (e.g., Business Actor, Application Component).
Represent structural or behavioural concepts.

### Relationship

Defines how elements interact (e.g., association, flow, assignment).

### Node

Visual instance of an element within a view.

### Connection

Visual representation of a relationship between nodes.

---

## Key Features & Functionality

### File Handling & Persistence

- Read existing ArchiMate models from XML
- Write/export models to ArchiMate-compliant XML
- Round-trip editing (load → modify → save)

### Model Creation & Management

- Create models from scratch programmatically
- Define architecture layers and structures
- Maintain centralised architecture repositories in code

### CRUD Operations on Architecture Artefacts

- Create, update, and delete elements, relationships, and views/diagrams
- Enables full lifecycle management of architecture components

### Diagram (View) Management

- Create and manage diagrams programmatically
- Add/remove nodes and connections
- Control layout structure (logical positioning; limited styling)

### Metamodel Compliance

- Enforces ArchiMate structure and relationship rules
- Ensures models remain valid and interoperable

### Separation of Logical vs Visual Layers

- Logical layer: elements and relationships
- Visual layer: nodes and connections in views
- Allows reuse of elements across multiple diagrams

### Automation & Scripting

- Integrate with Python scripts for bulk model generation, migration, and refactoring
- Useful for DevOps pipelines and model synchronization with codebases

### Extensibility

- Python-native; easy to extend or wrap
- Composable with data pipelines, APIs, and other modelling or visualization tools

### Lightweight Design

- Minimal overhead; easy installation (`pip install pyArchimate`)
- Suitable for embedding in larger systems

### Cross-Tool Compatibility

- Outputs standard ArchiMate XML
- Compatible with Archi and other EA platforms supporting ArchiMate

### Properties & Metadata

- Attach arbitrary key/value metadata to elements, relationships, and views via `prop(key, value)`
- Access all properties with `props` (returns dict); remove with `remove_prop(key)`
- Free-text documentation via the `desc` attribute on elements and relationships
- `embed_props()` / `expand_props()` for round-tripping properties through tools that strip them

### Search & Filter

- `find_elements(name, elem_type)` — exact match by name and/or type
- `find_relationships(rel_type, elem, direction)` — directional relationship lookup
- `filter_elements(predicate)` / `filter_relationships(predicate)` / `filter_views(predicate)` — lambda filtering

### Validation

- `check_valid_relationship(rel_type, source_type, target_type)` — validate against ArchiMate rules
- `get_default_rel_type(source_type, target_type)` — return preferred valid relationship type
- `model.check_invalid_conn()` — return list of broken connection IDs in the model

### Idempotent Operations

- `get_or_create_element(elem_type, name, create_elem=False)` — safe for re-entrant scripts
- `get_or_create_relationship(rel_type, name, source, target, create_rel=False)` — same for relationships

### Model Merging

- `model.merge(file_path)` — combine a second model file into this one; deduplicates by UUID

### Element Visual Styling

- `element.set_fill_color(color)` / `element.get_fill_color()` — hex (`#RRGGBB`) or named color, or `None` for default
- `element.set_line_color(color)` / `element.get_line_color()` — border colour
- `element.set_line_width(width)` / `element.get_line_width()` — border width in pixels (≥ 0)
- `element.set_transparency(alpha)` / `element.get_transparency()` — opacity `0.0` (transparent) to `1.0` (opaque)
- `element.set_visual_style(fill_color, line_color, line_width, transparency)` — set all style properties at once
- `element.reset_visual_style()` — revert all visual overrides to defaults
- All visual properties are preserved during XML export/import round-trips

### Node Styling

- `node.fill_color` / `node.line_color` — hex colour strings (`#RRGGBB`)
- `model.default_theme(theme)` — apply built-in ArchiMate or ARIS colour palette to all nodes

### Element Hierarchy

- `model.add_child(parent_uuid, child_uuid)` — create parent-child relationship between two elements
- `model.remove_child(parent_uuid, child_uuid)` — orphan a child element (leaves it in the model)
- `model.get_parent(elem_uuid)` — return parent Element or `None` if root
- `model.get_children(elem_uuid)` — list of direct child Elements
- `model.get_ancestors(elem_uuid)` — list of ancestors `[parent, grandparent, ..., root]`
- `model.get_descendants(elem_uuid)` — breadth-first list of all descendants
- `model.get_siblings(elem_uuid)` — elements sharing the same parent
- `model.get_root_elements()` — elements with no parent
- `model.get_leaf_elements()` — elements with no children
- `model.get_depth(elem_uuid)` — nesting depth (0 = root)
- `model.find_by_hierarchy_path(path)` — path query e.g. `'/Parent/Child'`; supports wildcard `'*'` at any level
- Cycle detection prevents invalid hierarchies; max depth configurable via `MAX_DEPTH`
- Hierarchy is preserved across XML export/import round-trips

### Junction Type Semantics

- `element.set_junction_type(type_str)` — set junction semantics: `'and'`, `'or'`, or `'xor'`
- `element.get_junction_type()` — return current junction type or `None`
- Types are validated on set and preserved in round-trip exports

### Viewpoint Support

- `element.assign_viewpoint(viewpoint_id)` — assign a canonical ArchiMate 3.x viewpoint slug to an element
- `element.remove_viewpoint(viewpoint_id)` — remove a viewpoint assignment
- `element.viewpoints` — list of assigned viewpoint slugs
- `view.set_primary_viewpoint(viewpoint_id)` — set the primary viewpoint for a view
- `view.primary_viewpoint` — read the primary viewpoint slug
- `model.get_viewpoints()` — return all 13 standard ArchiMate 3.x `Viewpoint` objects
- `model.get_elements_by_viewpoint(viewpoint_id)` — elements assigned to a viewpoint
- `model.get_views_by_viewpoint(viewpoint_id)` — views whose primary viewpoint matches
- All viewpoint slugs are validated against the standard registry

### Nested Nodes & Layout

- `node.add(elem, x, y, w, h)` — add a child node inside a parent (containment/grouping)
- `node.resize()` — auto-expand parent to fit children
- `node.distribute_connections()` — spread connection endpoints evenly along node edges

### Connection Routing

- `conn.l_shape()` / `conn.s_shape()` — route as L or S shape with auto-placed bendpoints
- `conn.add_bendpoint(Point)` / `conn.remove_all_bendpoints()` — manual waypoint control

### View Auto-Layout

- `auto_layout(view, config)` — reposition all nodes in ArchiMate layer order on a coarse grid; does **not** modify connections; returns `LayoutResult`
- `auto_route(view, config)` — recompute all connection paths as obstacle-avoiding orthogonal polylines using BFS; does **not** modify node positions; returns `LayoutResult` (includes `node_moves` if `allow_node_move=True`)
- `apply_layout(view, config)` — convenience wrapper: calls `auto_layout` then `auto_route`; returns combined `LayoutResult`
- `apply_format(view, config)` — standardize element sizes (120×55), fonts (Segoe UI 9pt), and optional grid alignment without repositioning; returns `LayoutResult`
- `undo_layout(view)` — revert the last layout/format operation (stub; full transaction rollback planned); returns `LayoutResult`
- Import from `pyArchimate.view.layout`
- Layer direction: `"vertical"` (Business top, Application middle, Technology bottom) or `"horizontal"` (layers stacked left-to-right)
- `auto_route` uses multi-pass conflict resolution; escalating crossing penalties re-route connections that pass through node bounding boxes or cross each other twice
- Connection routing: obstacle map inflates each node by `node_clearance` (default 25 px), then BFS finds shortest orthogonal corridor

### SVG Export

- `view.to_svg(filepath=None)` — render a view to a self-contained SVG string; optionally write to file
- Renders full ArchiMate-compliant element symbols with layer-specific icons (Business, Application, Technology, Motivation, Strategy, Physical, Implementation layers)
- Applies ArchiMate colour palette by element layer; respects per-node `fill_color` overrides
- Relationship-specific line styles and arrowhead markers: filled/hollow triangles, diamonds (Composition/Aggregation), open arrows (Access), dashed lines (Influence, Realization)
- Preserves stored bendpoints from the model; connection endpoints clipped orthogonally at element boundaries
- Renders relationship type labels on connections; Influence relationships include strength annotation
- Supports special element types: Or/And Junctions (circle), Grouping (dashed L-border with tab label), Group (solid grey)
- Containment relationships (Composition/Aggregation where target is a visual child) suppressed as redundant with container boundaries
- No external tools required; suitable for CI pipelines and automated reporting

---

## Typical Use Cases

### Architecture-as-Code

Define enterprise architecture in Python, version-control with Git, and automate updates.

### Model Generation

Generate diagrams from infrastructure definitions, cloud configurations,
or microservice architecture inventories.

### Model Transformation

Convert or refactor existing models; apply bulk updates across large architectures.

### DevOps Integration

Embed architecture validation in pipelines; ensure architecture consistency with deployments.

### Analysis & Reporting

Extract relationships and dependencies; build custom analytics or reports on architecture data.

---

## Strengths

- Programmatic control over architecture models
- Strong alignment with ArchiMate standard
- Lightweight and easy to integrate
- Enables automation — a major gap in traditional EA tools

---

## Limitations (Important Context)

- No built-in graphical editor (code-first only)
- Layout automation available but no GUI-based constraint editor; algorithmic layout via `auto_layout()` (layer-ordered grid) and `auto_route()` (BFS obstacle-avoiding orthogonal routing), or the combined `apply_layout()` convenience function
- Requires understanding of ArchiMate concepts
- SVG export available via `view.to_svg()`; full interactive editing still requires external tools (e.g., Archi)
- Not fully conformant to the complete ArchiMate 3.x specification (see Non-Conformances below; major gaps closed in v1.3.0)

---

## API Reference

### Writers (enum)

| Value | Format |
|---|---|
| `Writers.archi` | Archi tool `.archimate` XML (default) |
| `Writers.archimate` | OpenGroup ArchiMate Exchange XML |
| `Writers.csv` | CSV spreadsheet |

### Readers (enum)

| Value | Format |
|---|---|
| `Readers.archi` | Archi native `.archimate` XML (default) |
| `Readers.archimate` | OpenGroup ArchiMate Exchange XML |
| `Readers.aris` | **Deprecated** — ARIS AML format; will be removed in a future version |

### Model (API)

| Method / Property | Description |
|---|---|
| `Model(name)` | Create a new empty model |
| `add(concept_type, name)` | Add element or view; returns created object |
| `add_relationship(rel_type, source, target)` | Add typed relationship between two elements |
| `read(file_path)` | Load model from file (auto-detects format) |
| `write(file_path, writer)` | Persist model; `writer` selects output format |
| `merge(file_path)` | Merge a second model file in; deduplicates by UUID |
| `find_elements(name, elem_type)` | Find elements by name and/or type string |
| `find_relationships(rel_type, elem, direction)` | Find relationships for an element |
| `filter_elements(predicate)` | Filter elements with a lambda predicate |
| `filter_relationships(predicate)` | Filter relationships with a lambda predicate |
| `filter_views(predicate)` | Filter views with a lambda predicate |
| `get_or_create_element(elem_type, name, create_elem)` | Idempotent element lookup or creation |
| `get_or_create_relationship(rel_type, name, src, tgt, create_rel)` | Idempotent relationship lookup or creation |
| `add_child(parent_uuid, child_uuid)` | Create parent-child relationship between two elements |
| `remove_child(parent_uuid, child_uuid)` | Orphan a child (keeps it in the model) |
| `get_parent(elem_uuid)` | Parent element or `None` if root |
| `get_children(elem_uuid)` | Direct child elements |
| `get_ancestors(elem_uuid)` | All ancestors from parent to root |
| `get_descendants(elem_uuid)` | All descendants in breadth-first order |
| `get_siblings(elem_uuid)` | Elements sharing the same parent |
| `get_root_elements()` | Elements with no parent |
| `get_leaf_elements()` | Elements with no children |
| `get_depth(elem_uuid)` | Nesting depth (0 = root) |
| `find_by_hierarchy_path(path)` | Path query e.g. `'/A/B'`; supports `'*'` wildcard |
| `get_viewpoints()` | All 13 standard ArchiMate 3.x Viewpoint objects |
| `get_elements_by_viewpoint(viewpoint_id)` | Elements assigned to a viewpoint slug |
| `get_views_by_viewpoint(viewpoint_id)` | Views whose primary viewpoint matches slug |
| `check_invalid_conn()` | Return list of connection IDs with broken references |
| `check_invalid_nodes()` | Return list of node IDs referencing unknown elements |
| `embed_props(remove_props)` | Serialise all properties into `desc` fields as JSON |
| `expand_props(clean_doc)` | Restore properties from embedded JSON in `desc` fields |
| `default_theme(theme)` | Apply colour theme (`"archi"` or `"aris"`) to all nodes |
| `elements` | All elements in the model |
| `relationships` | All relationships in the model |
| `views` | All views in the model |

### Element (API)

| Method / Property | Description |
|---|---|
| `name` | Element name (read/write) |
| `type` | ArchiMate type string (read/write) |
| `desc` | Free-text documentation string |
| `uuid` | Unique identifier |
| `parent_uuid` | Parent element UUID or `None` if root |
| `viewpoints` | List of assigned canonical viewpoint slugs |
| `prop(key, value)` | Get (`value=None`) or set a metadata property |
| `props` | All properties as a `dict` |
| `remove_prop(key)` | Delete a property by key |
| `remove_folder()` | Remove this element's folder assignment |
| `assign_viewpoint(viewpoint_id)` | Assign a canonical ArchiMate 3.x viewpoint slug |
| `remove_viewpoint(viewpoint_id)` | Remove a viewpoint assignment |
| `set_fill_color(color)` | Fill colour: hex `#RRGGBB`, named color, or `None` |
| `get_fill_color()` | Current fill colour or `None` |
| `set_line_color(color)` | Border colour: hex `#RRGGBB`, named color, or `None` |
| `get_line_color()` | Current border colour or `None` |
| `set_line_width(width)` | Border width in pixels (≥ 0) or `None` for default |
| `get_line_width()` | Current border width or `None` |
| `set_transparency(alpha)` | Opacity `0.0`–`1.0` or `None` for default |
| `get_transparency()` | Current opacity or `None` |
| `set_visual_style(...)` | Set fill_color, line_color, line_width, transparency at once |
| `get_visual_style()` | Dict of all set visual style properties |
| `reset_visual_style()` | Revert all visual overrides to defaults |
| `set_junction_type(type_str)` | Junction semantics: `'and'`, `'or'`, `'xor'`, or `None` |
| `get_junction_type()` | Current junction type or `None` |

### Relationship (API)

| Method / Property | Description |
|---|---|
| `type` | Relationship type string (read/write) |
| `source` | Source element |
| `target` | Target element |
| `desc` | Free-text documentation string |
| `uuid` | Unique identifier |
| `prop(key, value)` | Get or set a metadata property |
| `props` | All properties as a `dict` |
| `remove_prop(key)` | Delete a property by key |
| `access_type` | For Access relationships: `"Read"`, `"Write"`, `"ReadWrite"` |
| `influence_strength` | For Influence: `0–10`, `"+"`, `"++"`, `"-"`, `"--"` |
| `is_directed` | For Association: `True` if directed |

### View (API)

| Method / Property | Description |
|---|---|
| `add(elem, x, y, w, h)` | Add a node for an element at given coordinates |
| `add_connection(rel, source, target)` | Add a connection for a relationship between nodes |
| `get_or_create_node(elem, elem_type, ...)` | Return existing node or create one if requested |
| `get_or_create_connection(rel, source, target, ...)` | Return existing connection or create one if requested |
| `set_primary_viewpoint(viewpoint_id)` | Set canonical ArchiMate 3.x viewpoint slug for this view |
| `primary_viewpoint` | Current primary viewpoint slug or `None` |
| `duplicate(name)` | Deep-copy this view into the same model; `name` defaults to `"<original> (copy)"` if omitted; returns new `View` |
| `delete()` | Remove this view and all its nodes and connections |
| `to_svg(filepath)` | Export view to SVG string; optionally write to file if `filepath` given |
| `prop(key, value)` | Get or set a view-level property |
| `remove_prop(key)` | Delete a property by key |
| `remove_folder()` | Remove this view's folder assignment |
| `nodes` | All nodes in the view |
| `conns` | All connections in the view |
| `name` | View name |

### Node (API)

| Method / Property | Description |
|---|---|
| `add(elem, x, y, w, h)` | Add a child node nested inside this node |
| `nodes` | Child nodes |
| `resize(max_in_row, ...)` | Auto-expand to fit children |
| `distribute_connections()` | Spread connection endpoints evenly along edges |
| `move(new_parent)` | Reparent node to a different Node or View within the same diagram |
| `delete(recurse, delete_from_model)` | Delete node and its connections; optionally cascade to children or remove backing element |
| `out_conns(rel_type)` | Outgoing connections, optionally filtered by type |
| `in_conns(rel_type)` | Incoming connections, optionally filtered by type |
| `fill_color` | Fill colour as `#RRGGBB` |
| `line_color` | Border colour as `#RRGGBB` |
| `x`, `y`, `w`, `h` | Position and dimensions |
| `concept` | Underlying element or relationship |

### Connection (API)

| Method / Property | Description |
|---|---|
| `l_shape()` | Route as L-shape with one auto bendpoint |
| `s_shape()` | Route as S-shape with two auto bendpoints |
| `add_bendpoint(Point)` | Append a waypoint to the connection path |
| `set_bendpoint(bp, index)` | Replace waypoint at index |
| `remove_all_bendpoints()` | Clear all waypoints |
| `get_all_bendpoints()` | Return list of all waypoints |
| `get_bendpoint(index)` | Return waypoint at index |
| `line_color` | Connection colour as `#RRGGBB` |
| `source` | Source node |
| `target` | Target node |

### Module-level Functions

| Function | Description |
|---|---|
| `check_valid_relationship(rel_type, src_type, tgt_type, raise_flg)` | Validate rel type against ArchiMate rules |
| `get_default_rel_type(source_type, target_type)` | Return preferred valid relationship type |
| `parse_bool(value)` | Parse XML boolean string per W3C xsd:boolean (`"true"`, `"1"` → `True`; everything else → `False`) |
| `extract_images_from_archimate(element)` | Extract base64-encoded image data from an Archi XML element |
| `compare_image_data(data1, data2)` | Byte-for-byte comparison of two base64 image data strings |
| `log_set_level(level)` | Set logging verbosity (standard `logging` levels) |
| `log_to_file(path)` | Redirect log output to a file |
| `log_to_stderr()` | Redirect log output to stderr |

### Layout Functions (`pyArchimate.view.layout`)

| Function | Description |
|---|---|
| `auto_layout(view, config)` | Reposition all nodes in layer order on a coarse grid; does not touch connections; accepts `LayoutConfig`; returns `LayoutResult` |
| `auto_route(view, config)` | Recompute all connection paths as obstacle-avoiding orthogonal polylines; does not move nodes; accepts `RoutingConfig`; returns `LayoutResult` |
| `apply_layout(view, config)` | Convenience wrapper: runs `auto_layout` then `auto_route`; accepts `LayoutConfig`; returns combined `LayoutResult` |
| `apply_format(view, config)` | Standardize element sizes/fonts without repositioning; returns `LayoutResult` |
| `undo_layout(view)` | Revert the last layout/format operation (stub; transaction rollback planned); returns `LayoutResult` |

### LayoutConfig (dataclass)

All fields are optional; defaults shown below.

| Field | Default | Description |
|---|---|---|
| `algorithm` | `"force_directed"` | `"force_directed"` or `"hierarchical"` |
| `spacing` | `50.0` | Minimum pixels between elements |
| `margin` | `20.0` | Pixels around canvas edges |
| `alignment` | `"free"` | `"free"` or `"grid"` (snap to grid) |
| `grid_size` | `240.0` | Coarse grid cell size in pixels (approx. node width + gap); used by `auto_layout` for node placement |
| `routing_style` | `"orthogonal"` | `"orthogonal"` (0°/90°) or `"mixed_45"` (±45°) |
| `layer_priority` | `"mandatory"` | `"mandatory"` (enforce ArchiMate layers) or `"soft"` |
| `layer_direction` | `"vertical"` | `"vertical"` (Business top → Technology bottom) or `"horizontal"` (Business left → Technology right) |
| `high_degree_threshold` | `5` | Nodes with ≥ this many connections get 1-cell isolation padding to reduce routing bottlenecks |
| `excluded_element_ids` | `[]` | Element IDs excluded from repositioning |
| `node_size_constraints` | `{}` | Dict with `min_width`, `max_width`, `min_height`, `max_height` |

### RoutingConfig (dataclass)

All fields are optional; used by `auto_route`. Defaults shown below.

| Field | Default | Description |
|---|---|---|
| `node_clearance` | `25` | Avoidance zone inflated around each node side (px) |
| `min_segment_gap` | `20.0` | Minimum separation between collinear segments of different connections (px) |
| `min_turn_segment` | `40` | Minimum segment length after each L-turn (px) |
| `corner_clearance_pct` | `0.10` | Fraction of edge length reserved at each corner (0 < pct ≤ 0.50) |
| `corner_clearance_min` | `4.0` | Absolute floor for corner clearance (px) |
| `crossing_penalty` | `3.0` | BFS cost weight when crossing an already-routed segment |
| `max_routing_passes` | `3` | Maximum re-routing passes for conflict resolution |
| `allow_node_move` | `False` | Last-resort: shift a blocking node ≤ `max_node_displacement` cells to open a corridor |
| `max_node_displacement` | `1` | Max cells a node may be shifted per move |

### LayoutResult (dataclass)

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | `True` if layout completed without error |
| `view_id` | `str` | UUID of the laid-out view |
| `algorithm_used` | `str` | Algorithm name or `"format"` / `"undo"` / `"auto_layout"` / `"auto_route"` |
| `elements_processed` | `int` | Number of nodes repositioned or formatted |
| `connections_processed` | `int` | Number of connections routed |
| `layout_time_ms` | `float` | Wall-clock time for the operation |
| `quality_metrics` | `dict` | Algorithm-specific metrics (crossing count, variance, etc.) |
| `error_message` | `str \| None` | Error description if `success=False` |
| `warnings` | `list[str]` | Non-fatal warnings (e.g. connections skipped due to no valid path) |
| `node_moves` | `list[NodeMove]` | Records of nodes shifted by routing-driven node-move fallback (when `allow_node_move=True`) |

---

## Non-Conformances

Known deviations from the ArchiMate 3.x standard and Archi tool compatibility gaps.

### ArchiMate 3.x Conformance Gaps

| Gap | Status | Impact |
|-----|--------|--------|
| Viewpoints not first-class; stored as generic `View` | Partially resolved (v1.3.0) — canonical viewpoint slugs supported via `set_primary_viewpoint` and `assign_viewpoint`; full viewpoint content rule enforcement not yet implemented | Viewpoint-constrained element validation not enforced |

### Archi Import/Export Compatibility Gaps

| Gap | Status | Impact |
|-----|--------|--------|
| Model version hard-coded to `4.9.0` on export | Open | Source document version not preserved |
| Folder taxonomy rebuilt on export | Open | Exact folder structure not round-tripped |
| Only four node kinds recognised; unknown kinds dropped | Open | Non-standard nodes silently lost on import |

### Resolved (since v1.3.0)

| Gap | Fixed in | Details |
|-----|----------|---------|
| `BusinessInteraction` not in `checker_rules.yml` | v1.3.0 | Now enabled; `BusinessInteraction` elements can be created and imported |
| Reader reads `modifier`; writer emits `influenceStrength` | v1.3.0 | Reader normalises both field names; round-trip fidelity restored |
| Relationship docs parsed with `e.text` instead of `doc.text` | v1.3.0 | `_archireader_helpers.py` now extracts documentation correctly |
| `bool("false")` always `True` for `nameVisible` | v1.3.1 | Replaced with `parse_bool()` (W3C xsd:boolean semantics) |
| Bendpoint coordinates written as floats in OpenGroup XML | v1.9.0 | Archi requires integer coordinates; bendpoints round-tripped as integers (regression from v1.8.x re-fixed) |
| Connection endpoints not clipped at element boundary in SVG | v1.9.0 | Orthogonal clip applied at source/target boundary including when bendpoints present; basic case first fixed in v1.8.0 |
