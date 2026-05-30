# Contract: Element Hierarchy and Grouping

**Version**: 1.0  
**Date**: 2026-05-30  
**Type**: Structural Metadata Contract  
**Status**: Complete (P3 Implementation)

## Overview

Defines how parent-child containment relationships between ArchiMate elements are stored, serialized, and queried. Grouping is semantic (model-level), distinct from visual grouping on diagrams. Children are orphaned (not deleted) when their parent is deleted.

---

## Canonical Representation

**Storage** (`Model`):
- `_element_hierarchy: dict[str, str | None]` — maps child UUID → parent UUID
- `_element_children: dict[str, set[str]]` — maps parent UUID → set of child UUIDs

**Storage** (`Element`):
- `_parent_uuid: str | None` — UUID of the immediate parent, or `None` for root elements

**Cardinality**: Each element has at most one parent (tree structure, not a DAG).  
**Depth limit**: `MAX_DEPTH = 5` (`constants.py:187`). Enforced in `add_child` via `_get_depth()` — a separate check from cycle detection.

---

## API

| Method | Location | Description |
|--------|----------|-------------|
| `model.add_child(parent_uuid, child_uuid)` | `model.py:1149` | Establish parent-child link; raises `ValueError` on cycle, double-parenting, or max depth |
| `model.remove_child(parent_uuid, child_uuid)` | `model.py:1171` | Orphan a child (clear parent reference) |
| `model.get_parent(elem_uuid)` | `model.py:1189` | Return parent `Element` or `None` |
| `model.get_children(elem_uuid)` | `model.py:1198` | Return list of immediate child `Element`s |
| `model.get_ancestors(elem_uuid)` | `model.py:1206` | Return ordered list from immediate parent to root |
| `model.get_descendants(elem_uuid)` | `model.py:1224` | Return all elements in subtree (breadth-first) |
| `model.get_root_elements()` | `model.py:1251` | Return elements with no parent |
| `model.get_leaf_elements()` | `model.py:1258` | Return elements with no children |

---

## XML Serialization

### `.archimate` format (Archi)

Parent UUID is written as a `parentId` attribute on the `<element>` tag:

```xml
<element id="parent-uuid-001" name="Business Process" xsi:type="BusinessProcess"/>
<element id="child-uuid-001" name="Sub-Function" xsi:type="BusinessFunction"
         parentId="parent-uuid-001"/>
<element id="child-uuid-002" name="Sub-Service" xsi:type="BusinessService"
         parentId="parent-uuid-001"/>
```

**Rules**:
- `parentId` attribute is omitted for root elements (no parent)
- Archi format written by `archiWriter.py:139`; read by `_archireader_helpers.py:291-294`

### OpenGroup exchange format

OpenGroup format (`archimateWriter.py`) also writes `parentId` as an element attribute (lines 146-148), using the same attribute name and value as the Archi format. Round-trip fidelity is guaranteed in **both** formats.

---

## Lifecycle and Invariants

1. **Add child**: `add_child(parent, child)` — child must not already have a parent; `_would_create_cycle()` checks ancestry; `_get_depth()` enforces max depth.
2. **Remove child**: `remove_child(parent, child)` — child's `_parent_uuid` becomes `None`; child remains in `model.elems_dict`.
3. **Delete parent**: Children are orphaned (`_parent_uuid` cleared); children are **not** deleted.
4. **Double-parenting**: Raises `ValueError` if child already has a parent.

---

## Round-Trip Fidelity

✅ Parent-child hierarchy survives export/import for both `.archimate` and OpenGroup formats  
✅ Root elements (no parent) imported without modification  
✅ Deleting a parent during round-trip correctly orphans children

**Test coverage**:
- `tests/unit/test_element_grouping.py` — unit tests for add/remove/query/cycle detection
- `tests/integration/test_round_trip_grouping.py` — round-trip fidelity
- `tests/features/grouping.feature` — BDD acceptance scenarios

---

## Implementation Files

- `src/pyArchimate/element.py` — `_parent_uuid` attribute (line 167)
- `src/pyArchimate/constants.py` — `MAX_DEPTH = 5` (line 187)
- `src/pyArchimate/model.py` — `_element_hierarchy`, `_element_children`, hierarchy methods (lines 288-289, 1149-1263)
- `src/pyArchimate/readers/_archireader_helpers.py` — `parentId` extraction (lines 291-294)
- `src/pyArchimate/writers/archiWriter.py` — `parentId` emission (line 139)
- `src/pyArchimate/writers/archimateWriter.py` — `parentId` emission (lines 146-148)

---

## Error Handling

**Cycle detected**:
```
ValueError: Cycle detected: cannot add <child_uuid> as child of <parent_uuid>
```

**Double-parenting**:
```
ValueError: Element <child_uuid> already has parent <existing_parent_uuid>
```

**Max depth exceeded**:
```
ValueError: Max nesting depth 5 exceeded
```

**UUID not found**:
```
KeyError: Parent element <parent_uuid> not found
KeyError: Child element <child_uuid> not found
```
