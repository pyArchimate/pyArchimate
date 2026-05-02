# Containment Tracking Design (T123)

**Date**: 2026-05-01  
**Status**: Complete  
**Based On**: T121 (Element audit) + T122 (Model audit)  
**Recommendation**: **Option C (Hybrid Approach)** ✅

---

## Executive Summary

Element grouping requires semantic parent-child relationships. This design specifies a hybrid storage approach where the Element stores its parent UUID and the Model maintains bidirectional mapping for efficient queries. This mirrors the successful P2 viewpoint pattern and avoids storing full object references.

---

## Storage Strategy: Hybrid Approach

### Element-Level Storage

**New Attribute**: `_parent_uuid: Optional[str]`

```python
# In Element.__init__() - line 114 (after self._viewpoints)
self._parent_uuid: Optional[str] = None  # UUID of parent element, or None if root
```

**Properties**: 
- Immutable parent UUID (no setter; mutations only via Model methods)
- None indicates root element (no parent)
- Must be a valid UUID that exists in Model.elems_dict

**Getter Method**:
```python
@property
def parent_uuid(self) -> Optional[str]:
    """Return the UUID of this element's parent (or None if root)."""
    return self._parent_uuid
```

### Model-Level Storage

**New Attributes** (in Model.__init__() - lines 207-208, after P2 viewpoint dicts):

```python
# Bidirectional hierarchy tracking (mirrors P2 viewpoint pattern)
self._element_hierarchy: dict[str, Optional[str]] = {}   # child_uuid → parent_uuid
self._element_children: dict[str, set[str]] = {}         # parent_uuid → set(child_uuids)
```

**Why Two Dicts?**
- `_element_hierarchy`: Fast parent lookup O(1) - "who is my parent?"
- `_element_children`: Fast child enumeration O(1) - "who are my children?"
- Bidirectional design enables efficient cycle detection and traversal

**Maintenance Invariants**:
1. If element E has parent P, then:
   - `_element_hierarchy[E.uuid] == P.uuid`
   - `P.uuid in _element_children[P.uuid]`
2. If entry in `_element_hierarchy`, entry in `_element_children` must exist (and vice versa)
3. Parent-child mapping must be 1:1 (each element has ≤1 parent)

---

## Design Invariants

### Acyclicity (Constraint 1)

**Rule**: No circular parent-child chains allowed (A→B→C→A is invalid)

**Check**: O(depth) traversal up to max depth
```python
def _has_ancestor_cycle(self, potential_ancestor_uuid: str, child_uuid: str) -> bool:
    """Check if potential_ancestor is an ancestor of child (creating cycle if A→C)."""
    current = self._element_hierarchy.get(child_uuid)
    visited = set()
    while current is not None:
        if current == potential_ancestor_uuid:
            return True  # Cycle detected
        if current in visited:
            break  # Prevent infinite loop on corrupted state
        visited.add(current)
        current = self._element_hierarchy.get(current)
    return False
```

**When to Check**: Before every add_child() call

**Error Message**: `"Cycle detected: adding {parent} as parent to {child} would create cycle"`

### Unique Parent (Constraint 2)

**Rule**: Each element has at most 1 parent

**Check**: Simple dict membership check
```python
# If _parent_uuid is set, element already has a parent
if element._parent_uuid is not None:
    raise ValueError(f"Element {element.uuid} already has parent {element._parent_uuid}")
```

**When to Check**: Before every add_child() call

**Error Message**: `"Element {child_uuid} already has parent {old_parent_uuid}"`

### Max Depth (Constraint 3)

**Rule**: Maximum 5 levels of nesting allowed
- Level 0: Root elements (no parent)
- Level 1: Direct children of roots
- Level 2: Grandchildren
- Level 3: Great-grandchildren
- Level 4: Great-great-grandchildren
- Level 5: Great-great-great-grandchildren

**Check**: O(depth) traversal from child to root
```python
def _get_depth(self, elem_uuid: str) -> int:
    """Get nesting depth of element (0 = root, 1 = direct child, ...)."""
    depth = 0
    current = self._element_hierarchy.get(elem_uuid)
    while current is not None:
        depth += 1
        if depth > MAX_DEPTH:
            raise ValueError(f"Max nesting depth {MAX_DEPTH} exceeded")
        current = self._element_hierarchy.get(current)
    return depth
```

**When to Check**: Before every add_child() call

**Error Message**: `"Max nesting depth 5 exceeded: child would be at level {depth + 1}"`

**Rationale**: Prevents pathological trees; ArchiMate models typically use 2-3 levels; 5 is generous

---

## Cycle Detection Algorithm

### Algorithm: Ancestor Walk

**Input**: `parent_uuid` (candidate parent), `child_uuid` (element to add as child)  
**Output**: boolean (True = cycle detected, False = safe)  
**Complexity**: O(depth) where depth ≤ 5

```python
def _would_create_cycle(self, parent_uuid: str, child_uuid: str) -> bool:
    """
    Check if adding parent→child link would create a cycle.
    
    Logic:
    1. Start at parent_uuid
    2. Walk up the tree (parent of parent of parent...)
    3. If we encounter child_uuid, then child is ancestor of parent → cycle
    4. If we reach root (None) or hit max depth, no cycle
    """
    visited = set()
    current = parent_uuid
    while current is not None:
        if current == child_uuid:
            # Child is already an ancestor of parent → cycle!
            return True
        if current in visited:
            # Protect against corrupted state with loops
            log.error(f"Corrupted hierarchy: cycle detected in existing tree at {current}")
            return True
        visited.add(current)
        current = self._element_hierarchy.get(current)
        if len(visited) > MAX_DEPTH:
            # Shouldn't reach here if invariants maintained
            log.error(f"Depth limit exceeded during cycle check; corrupted hierarchy?")
            return True
    return False
```

### Example: Cycle Detection in Action

```
Initial state: A→B→C (A is parent of B, B is parent of C)

Try: add_child(C, A)  # Make A a child of C (would create C→A→B→C cycle)

_would_create_cycle(parent=C, child=A):
  current = C
  visited = {C}
  current = hierarchy[C] = B
  visited = {C, B}
  current = hierarchy[B] = A ← This equals child_uuid!
  RETURN True  # Cycle detected!
```

---

## Query and Mutation Methods

### Mutation Methods (Public API)

**`add_child(parent_uuid: str, child_uuid: str) → None`**
```python
def add_child(self, parent_uuid: str, child_uuid: str) -> None:
    """
    Assign parent_uuid as the parent of child_uuid.
    
    Raises:
        ValueError: if child already has parent, or cycle would be created, or depth exceeded
        KeyError: if parent_uuid or child_uuid not in model
    """
    # Validate UUIDs exist
    if parent_uuid not in self.elems_dict:
        raise KeyError(f"Parent element {parent_uuid} not found")
    if child_uuid not in self.elems_dict:
        raise KeyError(f"Child element {child_uuid} not found")
    
    # Check child doesn't already have parent
    if self._element_hierarchy.get(child_uuid) is not None:
        raise ValueError(f"Element {child_uuid} already has parent")
    
    # Check for cycles
    if self._would_create_cycle(parent_uuid, child_uuid):
        raise ValueError(f"Adding {parent_uuid} as parent to {child_uuid} would create cycle")
    
    # Check max depth
    parent_depth = self._get_depth(parent_uuid)
    if parent_depth >= MAX_DEPTH:
        raise ValueError(f"Max nesting depth {MAX_DEPTH} exceeded")
    
    # All checks passed; update both dicts and element
    self._element_hierarchy[child_uuid] = parent_uuid
    self._element_children.setdefault(parent_uuid, set()).add(child_uuid)
    self.elems_dict[child_uuid]._parent_uuid = parent_uuid
```

**`remove_child(parent_uuid: str, child_uuid: str) → None`**
```python
def remove_child(self, parent_uuid: str, child_uuid: str) -> None:
    """
    Remove the parent-child relationship between parent and child.
    Child becomes a root element (parent_uuid = None).
    
    Raises:
        ValueError: if relationship doesn't exist
        KeyError: if parent_uuid or child_uuid not in model
    """
    if parent_uuid not in self.elems_dict or child_uuid not in self.elems_dict:
        raise KeyError("Parent or child element not found")
    
    if self._element_hierarchy.get(child_uuid) != parent_uuid:
        raise ValueError(f"{child_uuid} is not a child of {parent_uuid}")
    
    # Update both dicts and element
    del self._element_hierarchy[child_uuid]
    self._element_children.get(parent_uuid, set()).discard(child_uuid)
    self.elems_dict[child_uuid]._parent_uuid = None
    
    # Clean up empty sets
    if not self._element_children.get(parent_uuid):
        self._element_children.pop(parent_uuid, None)
```

### Query Methods (Public API)

**`get_parent(elem_uuid: str) → Optional[Element]`**
```python
def get_parent(self, elem_uuid: str) -> Optional[Element]:
    """Return the parent element of elem_uuid, or None if root."""
    parent_uuid = self._element_hierarchy.get(elem_uuid)
    return self.elems_dict[parent_uuid] if parent_uuid else None
```

**`get_children(elem_uuid: str) → list[Element]`**
```python
def get_children(self, elem_uuid: str) -> list[Element]:
    """Return all direct children of elem_uuid."""
    child_uuids = self._element_children.get(elem_uuid, set())
    return [self.elems_dict[uid] for uid in child_uuids if uid in self.elems_dict]
```

**`get_ancestors(elem_uuid: str) → list[Element]`**
```python
def get_ancestors(self, elem_uuid: str) -> list[Element]:
    """Return all ancestors from elem up to root (including elem)."""
    ancestors = []
    current = elem_uuid
    visited = set()
    while current is not None:
        if current in visited:
            break  # Protect against corruption
        visited.add(current)
        ancestors.append(self.elems_dict[current])
        current = self._element_hierarchy.get(current)
    return ancestors
```

**`get_descendants(elem_uuid: str) → list[Element]`**
```python
def get_descendants(elem_uuid: str) -> list[Element]:
    """Return all descendants of elem (breadth-first)."""
    from collections import deque
    descendants = []
    queue = deque([elem_uuid])
    visited = set()
    while queue:
        uid = queue.popleft()
        if uid in visited:
            continue
        visited.add(uid)
        descendants.append(self.elems_dict[uid])
        for child_uid in self._element_children.get(uid, set()):
            queue.append(child_uid)
    return descendants[1:]  # Exclude root element
```

**`get_depth(elem_uuid: str) → int`**
```python
def get_depth(self, elem_uuid: str) -> int:
    """Get nesting depth of element (0 = root)."""
    depth = 0
    current = self._element_hierarchy.get(elem_uuid)
    while current is not None:
        depth += 1
        current = self._element_hierarchy.get(current)
    return depth
```

### Internal Helper Methods (Private)

**`_would_create_cycle(parent_uuid, child_uuid) → bool`** (defined above)

**`_get_depth(elem_uuid) → int`** (defined above)

---

## Cascade Delete Behavior

**When element is deleted** (via `element.delete()`):

1. Element is removed from `elems_dict`
2. If element has a parent:
   - Remove from `_element_hierarchy[child_uuid]`
   - Remove from `_element_children[parent_uuid]`
3. If element has children:
   - For each child: set `_parent_uuid = None` (orphan them)
   - Remove all entries from `_element_hierarchy` for those children
   - Remove entries from `_element_children`

**Rationale**: Preserve orphaned children rather than recursively delete (non-destructive)

```python
# In Element.delete() - additional logic needed:
def delete(self) -> None:
    """...[existing docstring]..."""
    _id = self.uuid
    
    # ... [existing node/relationship deletion code] ...
    
    # NEW: Handle hierarchy
    # If this element has a parent, remove the parent-child relationship
    if self._parent_uuid is not None:
        self.parent._element_children.get(self._parent_uuid, set()).discard(_id)
        del self.parent._element_hierarchy[_id]
    
    # If this element has children, orphan them
    for child_uuid in self.parent._element_children.get(_id, set()).copy():
        child = self.parent.elems_dict[child_uuid]
        child._parent_uuid = None
        del self.parent._element_hierarchy[child_uuid]
    if _id in self.parent._element_children:
        del self.parent._element_children[_id]
    
    # ... [existing dict cleanup] ...
    if _id in self.parent.elems_dict:
        del self.parent.elems_dict[_id]
```

---

## XML Serialization

### Notation

**New XML Attribute on Element**:
```xml
<element id="id-abc123" name="Process A" xsi:type="archimate:BusinessProcess" parentId="id-parent456">
  <!-- properties, documentation, etc. -->
</element>
```

**Mapping**:
- `parentId` XML attribute ↔ Element._parent_uuid (in Python)
- If `parentId` is missing or empty → element is root

### Round-Trip Preservation

On **read** (archimateReader):
- Extract `parentId` from XML
- Store in Element._parent_uuid
- Build Model._element_hierarchy and Model._element_children from all parent-child pairs
- Validate: check for cycles, depth limits

On **write** (archiWriter):
- Output Element._parent_uuid as `parentId` XML attribute
- If None or empty: omit attribute

---

## Validation on Import

**When reading a file with hierarchy data**:

1. Load all elements first (no hierarchy)
2. For each element with parentId:
   - Verify parent exists in model
   - Attempt add_child(parent, child)
   - On validation error: log warning, skip relationship (model remains valid)
3. Report count of skipped relationships

**Rationale**: Don't fail entire import due to hierarchy issue; preserve data and warn

---

## Summary

| Aspect | Design Decision |
|--------|-----------------|
| **Storage** | Hybrid: Element stores `_parent_uuid`; Model stores bidirectional maps |
| **Uniqueness** | Each element has ≤1 parent (enforced) |
| **Cycles** | Prohibited; O(depth) check before mutation |
| **Max Depth** | 5 levels; checked before mutation |
| **Deletion** | Children orphaned (not recursively deleted) |
| **Queries** | O(1) parent lookup, O(n) child/descendant enumeration |
| **XML** | `parentId` attribute on element |
| **Import** | Non-strict: warn on violations, skip relationship, continue |

**Benefits**:
- ✅ Efficient O(1) parent lookup
- ✅ Efficient O(1) child enumeration
- ✅ Mirrors successful P2 viewpoint pattern
- ✅ Clear, enforceable invariants
- ✅ Non-destructive delete (preserves orphaned children)
- ✅ Cycle prevention
- ✅ Depth limiting prevents pathological trees

**Risks & Mitigations**:
- Risk: Corrupted hierarchy (e.g., missing entries)
  - Mitigation: visited set in traversals; depth check in cycle detection
- Risk: Orphaned children after delete
  - Mitigation: By design (non-destructive); user can manually re-parent if needed
- Risk: Circular import (malformed file)
  - Mitigation: Import validates and warns; model remains valid

