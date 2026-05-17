# Contract: Element Grouping API

**Version**: 1.0  
**Status**: Design Complete (Phase 1)  
**Target**: Phase 2 Implementation

---

## Overview

The Element Grouping API enables semantic parent-child containment relationships between elements in a pyArchimate model.

---

## API Endpoints (Python Method Contract)

### Mutation: Add Child

**Method**: `Model.add_child(parent_uuid: str, child_uuid: str) → None`

**Purpose**: Assign parent_uuid as the parent of child_uuid

**Input**:
| Parameter | Type | Required | Validation |
|-----------|------|----------|-----------|
| parent_uuid | str | Yes | Must exist in model.elems_dict |
| child_uuid | str | Yes | Must exist in model.elems_dict |

**Preconditions**:
- Both UUIDs exist in model
- child_uuid does not already have a parent
- Adding parent→child would not create a cycle
- Parent not at max depth (4 levels deep)

**Postconditions**:
- `Element._parent_uuid[child_uuid] = parent_uuid`
- `Model._element_hierarchy[child_uuid] = parent_uuid`
- `Model._element_children[parent_uuid].add(child_uuid)`

**Errors**:
- `KeyError`: Parent or child UUID not in model
  - Message: `"Parent element {uuid} not found"` or `"Child element {uuid} not found"`
- `ValueError`: Child already has parent
  - Message: `"Element {child_uuid} already has parent {old_parent_uuid}"`
- `ValueError`: Cycle would be created
  - Message: `"Cycle detected: adding {parent_uuid} as parent to {child_uuid} would create cycle"`
- `ValueError`: Max depth exceeded
  - Message: `"Max nesting depth 5 exceeded: child would be at level {depth + 1}"`

**Example**:

```python
model = Model('MyModel')
parent = model.add(ArchiType.BusinessProcess, 'Parent Process')
child = model.add(ArchiType.BusinessFunction, 'Child Function')

model.add_child(parent.uuid, child.uuid)
# Now: child.parent_uuid == parent.uuid
```

**Test Cases** (TDD - write tests before implementation):
- ✅ Valid add_child (different types)
- ✅ Valid add_child (same type)
- ✅ Error: parent UUID not found
- ✅ Error: child UUID not found
- ✅ Error: child already has parent
- ✅ Error: self-reference (A as parent of A)
- ✅ Error: cycle A→B, B→C, try C→A
- ✅ Error: depth exceeded (5 levels max)
- ✅ Add multiple children to same parent
- ✅ Verify bidirectional maps updated

---

### Mutation: Remove Child

**Method**: `Model.remove_child(parent_uuid: str, child_uuid: str) → None`

**Purpose**: Remove parent-child relationship; child becomes root

**Input**:
| Parameter | Type | Required | Validation |
|-----------|------|----------|-----------|
| parent_uuid | str | Yes | Must exist in model.elems_dict |
| child_uuid | str | Yes | Must exist in model.elems_dict |

**Preconditions**:
- Both UUIDs exist in model
- child_uuid is actually a child of parent_uuid

**Postconditions**:
- `Element._parent_uuid[child_uuid] = None`
- `child_uuid` removed from `Model._element_hierarchy`
- `child_uuid` removed from `Model._element_children[parent_uuid]`

**Errors**:
- `KeyError`: Parent or child UUID not in model
- `ValueError`: Relationship doesn't exist
  - Message: `"{child_uuid} is not a child of {parent_uuid}"`

**Example**:

```python
model.remove_child(parent.uuid, child.uuid)
# Now: child.parent_uuid == None (child becomes root)
```

**Test Cases**:
- ✅ Valid remove_child
- ✅ Error: parent UUID not found
- ✅ Error: child UUID not found
- ✅ Error: not actually a child
- ✅ Verify maps cleaned up
- ✅ Verify Element._parent_uuid set to None

---

### Query: Get Parent

**Method**: `Model.get_parent(elem_uuid: str) → Optional[Element]`

**Purpose**: Return parent element or None if root

**Input**:
| Parameter | Type | Required |
|-----------|------|----------|
| elem_uuid | str | Yes |

**Returns**:
- Parent Element object, or None if root

**Complexity**: O(1) dict lookup

**Example**:

```python
parent = model.get_parent(child.uuid)
# Returns: parent Element or None
```

**Test Cases**:
- ✅ Get parent of child
- ✅ Get parent of root (None)
- ✅ Get parent of orphaned element (None)
- ✅ Invalid UUID (KeyError or None)

---

### Query: Get Children

**Method**: `Model.get_children(elem_uuid: str) → list[Element]`

**Purpose**: Return all direct children

**Input**:
| Parameter | Type | Required |
|-----------|------|----------|
| elem_uuid | str | Yes |

**Returns**:
- List of Element objects (direct children only)
- Empty list if no children

**Complexity**: O(n) where n = number of children (usually small)

**Example**:

```python
children = model.get_children(parent.uuid)
# Returns: [child1, child2, ...] or []
```

**Test Cases**:
- ✅ Get children of parent with 0 children
- ✅ Get children of parent with 1 child
- ✅ Get children of parent with N children
- ✅ Order preservation (implementation-dependent)

---

### Query: Get Ancestors

**Method**: `Model.get_ancestors(elem_uuid: str) → list[Element]`

**Purpose**: Return all ancestors from elem to root (inclusive)

**Input**:
| Parameter | Type | Required |
|-----------|------|----------|
| elem_uuid | str | Yes |

**Returns**:
- List of Elements: [elem, parent, grandparent, ..., root]
- Single-element list if elem is root

**Complexity**: O(depth), max depth 5

**Example**:

```python
# Hierarchy: Root → P1 → P2 → P3
ancestors = model.get_ancestors(p3.uuid)
# Returns: [p3, p2, p1, root]
```

**Test Cases**:
- ✅ Ancestors of root element
- ✅ Ancestors of direct child
- ✅ Ancestors of deeply nested element
- ✅ Order: elem first, then parents up

---

### Query: Get Descendants

**Method**: `Model.get_descendants(elem_uuid: str) → list[Element]`

**Purpose**: Return all descendants (breadth-first traversal)

**Input**:
| Parameter | Type | Required |
|-----------|------|----------|
| elem_uuid | str | Yes |

**Returns**:
- List of Elements (excludes elem_uuid)
- Breadth-first order
- Empty list if no descendants

**Complexity**: O(subtree_size)

**Example**:

```python
# Hierarchy: Parent → [Child1, Child2] → [GrandChild1, GrandChild2]
descendants = model.get_descendants(parent.uuid)
# Returns: [child1, child2, grandchild1, grandchild2]
```

**Test Cases**:
- ✅ Descendants of leaf element
- ✅ Descendants of single-level parent
- ✅ Descendants of multi-level parent
- ✅ Order verification (breadth-first)

---

### Query: Get Depth

**Method**: `Model.get_depth(elem_uuid: str) → int`

**Purpose**: Return nesting depth (0 = root)

**Input**:
| Parameter | Type | Required |
|-----------|------|----------|
| elem_uuid | str | Yes |

**Returns**:
- Integer depth: 0 (root), 1 (direct child), 2 (grandchild), ...

**Complexity**: O(depth), max 5

**Example**:

```python
# Hierarchy: Root → P1 → P2
depth = model.get_depth(p2.uuid)
# Returns: 2
```

**Test Cases**:
- ✅ Depth of root element
- ✅ Depth of direct child
- ✅ Depth of deeply nested element
- ✅ Depth of max-level element

---

### Query: Get Root Elements

**Method**: `Model.get_root_elements() → list[Element]`

**Purpose**: Return all elements with no parent

**Returns**:
- List of Elements with `parent_uuid = None`

**Complexity**: O(n) where n = total elements

**Example**:

```python
roots = model.get_root_elements()
# Returns: [proc1, proc2, ...] all with parent_uuid = None
```

---

### Query: Get Leaf Elements

**Method**: `Model.get_leaf_elements() → list[Element]`

**Purpose**: Return all elements with no children

**Returns**:
- List of Elements with no children

**Complexity**: O(n) where n = total elements

**Example**:

```python
leaves = model.get_leaf_elements()
# Returns: [leaf1, leaf2, ...] all with no children
```

---

## State Invariants

**Invariant 1: Acyclic**
- No element is ancestor of itself
- Enforced: Cycle detection in `add_child()`

**Invariant 2: Unique Parent**
- Each element has ≤1 parent
- Enforced: Check before `add_child()`

**Invariant 3: Max Depth**
- No element deeper than 5 levels
- Enforced: Depth check in `add_child()`

**Invariant 4: Bidirectional Consistency**
- If `child in _element_hierarchy`, then `child in _element_children[parent]`
- Enforced: Updated together in mutations

**Invariant 5: Element Sync**
- `Element._parent_uuid == _element_hierarchy.get(element.uuid)`
- Enforced: Updated together in mutations

---

## XML Serialization Contract

### Write (Export)

```xml
<element id="id-func123"
         name="Validate Order"
         xsi:type="archimate:BusinessFunction"
         parentId="id-proc001">
  <documentation>Validates order details</documentation>
</element>
```

- `parentId` attribute: Element._parent_uuid (omitted if None)

### Read (Import)
- Extract `parentId` attribute
- After all elements loaded, call `model.add_child(parent_uuid, child_uuid)` for each pair
- On error: Log warning, skip relationship (model remains valid)

---

## Performance Targets

| Operation | Target | Method |
|-----------|--------|--------|
| add_child() | <1ms | Hash table ops |
| remove_child() | <1ms | Hash table ops |
| get_parent() | <1ms | Hash table lookup |
| get_children() | <10ms | Set enumeration |
| get_depth() | <1ms | O(5) max walk |
| get_descendants() | <100ms | O(n) BFS on 1000-element tree |
| Cycle detection | <1ms | O(5) max walk |

---

## Backward Compatibility

- ✅ No Element.__init__() signature change
- ✅ No Model API breaking changes
- ✅ Existing queries unaffected
- ✅ Element.delete() behavior expanded (non-breaking)

---

**Contract Status**: Ready for Phase 2 Implementation
