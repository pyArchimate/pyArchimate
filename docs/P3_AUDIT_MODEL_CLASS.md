# Model Class Audit (T122)

**Date**: 2026-05-01  
**Status**: Complete  
**File Audited**: `/src/pyArchimate/model.py` (835 lines)

---

## Existing Storage Structures

All storage structures are initialized in `__init__()` (lines 188-206):

| Structure | Type | Purpose | Notes |
|-----------|------|---------|-------|
| `elems_dict` | `dict[str, Element]` | UUID → Element object mapping | All elements stored here; empty on init |
| `rels_dict` | `dict[str, Relationship]` | UUID → Relationship object mapping | All relationships stored here; empty on init |
| `nodes_dict` | `dict[str, Node]` | UUID → Node object mapping | Visual representation of elements in views; empty on init |
| `conns_dict` | `dict[str, Connection]` | UUID → Connection object mapping | Visual connections between nodes; empty on init |
| `views_dict` | `dict[str, View]` | UUID → View object mapping | All views (diagrams) stored here; empty on init |
| `labels_dict` | `dict[str, Any]` | UUID → Label object mapping | Visual labels in views; empty on init |
| `_viewpoint_elements` | `dict[str, set[str]]` | Viewpoint slug → set of element UUIDs (P2) | Maps viewpoint to assigned elements; empty on init |
| `_viewpoint_views` | `dict[str, str]` | View UUID → primary viewpoint slug (P2) | Maps view to its primary viewpoint; empty on init |
| `_properties` | `dict[str, object]` | Model-level properties (key → value) | Empty on init; mirrors Element pattern |
| `_profiles_dict` | `dict[str, Profile]` | UUID → Profile object mapping | Empty on init |
| `pdefs` | `dict[Any, Any]` | Unknown (line 194) | Empty on init; not documented |
| `orgs` | `defaultdict(list)` | Organization/folder structure | Maps org names to elements; defaultdict pattern |

**Key Insights**:
- Separation of concerns: Element/Relationship logic separate from visual layout (Node/Connection)
- P2 viewpoint tracking uses inverse mapping for efficient queries
- All storage is UUID-keyed for O(1) lookup

---

## Existing Query Methods

### Element Queries

**`find_elements(name=None, elem_type=None)` → list[Element]** (lines 503-521)
- Search by name, type, or both
- Returns all elements if no criteria provided

**`filter_elements(fct)` → list[Element]** (lines 492-501)
- Callback function filtering (lambda-based)
- Returns filtered list

**`get_or_create_element(elem_type, elem, create_elem=False)` → Optional[Element]** (lines 577-598)
- Finds element by name+type or creates if not found
- Returns None if not found and create_elem=False

### Relationship Queries

**`find_relationships(rel_type, elem, direction='both')` → list[Relationship]** (lines 523-542)
- Search by type, element, and direction (in_rels/out_rels/both)
- Uses internal `_matches_rel()` helper

**`filter_relationships(fct)` → list[Relationship]** (lines 544-553)
- Callback function filtering (lambda-based)
- Returns filtered list

**`get_or_create_relationship(...)` → Optional[Relationship]** (lines 600-654)
- Finds by type/name/source/target or creates
- Returns None if not found and create_rel=False

### View Queries

**`find_views(name)` → list[View]** (lines 566-575)
- Search by name only

**`filter_views(fct)` → list[View]** (lines 555-564)
- Callback function filtering (lambda-based)
- Returns filtered list

**`get_or_create_view(view, create_view=False)` → Optional[View]** (lines 656-677)
- Accepts string name or View object
- Creates view if create_view=True

### Viewpoint Queries (P2)

**`get_viewpoints()` → list[Viewpoint]** (lines 796-803)
- Returns all 13 standard ArchiMate viewpoints from registry
- Delegate to `viewpoint_registry.STANDARD_VIEWPOINTS`

**`get_elements_by_viewpoint(viewpoint_id)` → list[Element]** (lines 805-817)
- Returns elements assigned to given viewpoint slug
- Validates viewpoint via `validate_viewpoint_slug()`
- O(n) lookup where n = elements in viewpoint (efficient)
- Raises: `ValueError` if viewpoint_id invalid

**`get_views_by_viewpoint(viewpoint_id)` → list[View]** (lines 819-831)
- Returns views whose primary viewpoint matches slug
- Validates viewpoint via `validate_viewpoint_slug()`
- O(n) lookup where n = views (efficient)
- Raises: `ValueError` if viewpoint_id invalid

### List Properties (Convenience)

**`elements` (property)** → list[Element] (lines 375-383)
- Returns all elements as list

**`relationships` (property)** → list[Relationship] (lines 385-393)
- Returns all relationships as list

**`views` (property)** → list[View] (lines 365-373)
- Returns all views as list

**`nodes` (property)** → list[Node] (lines 395-402)
- Returns all nodes as list

**`conns` (property)** → list[Connection] (lines 404-411)
- Returns all connections as list

### Content Management

**`add(concept_type, name=None, uuid=None, desc=None, folder=None, profile=None)` → Element|View** (lines 207-232)
- Creates and stores new Element or View
- Returns created object
- Raises: `ArchimateConceptTypeError` on invalid type

**`add_relationship(rel_type, source, target, ...)` → Relationship** (lines 234-265)
- Creates and stores new Relationship
- Returns created object

**`add_profile(name=None, uuid=None, concept=None)` → Profile** (lines 300-319)
- Creates and stores new Profile
- Returns created object

**`get_profile(name)` → Optional[Profile]** (lines 321-325)
- Finds profile by name
- Returns None if not found

### Theme & Validation

**`default_theme(theme=DEFAULT_THEME)` → None** (lines 784-794)
- Sets default color theme for all nodes and connections

**`check_invalid_nodes()` → list[Node]** (lines 768-782)
- Returns orphaned nodes (referencing unknown elements)
- Logs errors for each invalid node

**`check_invalid_conn()` → list[Connection]** (lines 709-718)
- Returns invalid connections
- Delegates to `check_connection()` per connection

**`check_connection(c)` → bool** (lines 720-766)
- Validates single connection
- Checks: relationship existence, source/target nodes, concept references

### Properties & Import/Export

**`props` (property)** → dict (lines 327-335)
- Returns model-level properties dict

**`prop(key, value=None)` → Any** (lines 337-352)
- Get/set model property

**`remove_prop(key)` → None** (lines 354-363)
- Remove model property

**`read(file_path, *args, **kwargs)` → None** (lines 455-473)
- Reads .archimate file (auto-detects format)
- Supports: ARIS AML, Open Group Exchange, Archi Tool

**`write(file_path=None, writer=Writers.archimate)` → str** (lines 413-426)
- Writes model to file in specified format
- Returns serialized data

**`merge(file_path)` → None** (lines 475-490)
- Merges another .archimate file into this model
- Uses reader's merge flag

**`embed_props(remove_props=False)` → None** (lines 679-694)
- Embeds properties into descriptions as JSON
- Used for tools that don't support properties

**`expand_props(clean_doc=True)` → None** (lines 696-707)
- Expands embedded JSON properties back into property dicts
- Mirrors `embed_props()`

---

## Constraints & Considerations

### No Existing Parent-Child Tracking

✅ **Confirmed**: No `_element_hierarchy`, `_element_children`, or `_parent_uuid` tracking exists
- Implication: P3 parent-child hierarchy is entirely new functionality
- No conflicts with existing code

### Storage Invariants

1. **UUID Uniqueness**: All UUIDs must be unique within type (elems_dict, rels_dict, etc.)
2. **Referential Integrity**: Relationship.source/target must reference existing elements
3. **Node-Element Binding**: Nodes must reference existing elements via nodes_dict[id].ref
4. **View Consistency**: Connection source/target must be nodes in same view

### Query Patterns

1. **UUID Direct Lookup**: `elems_dict[uuid]` O(1)
2. **Callback Filtering**: `filter_elements(lambda x: ...)` O(n)
3. **Multi-criterion Search**: `find_elements(name, type)` O(n) with dual filtering
4. **Relationship Direction**: `find_relationships(type, elem, direction)` O(n) with enum-style direction

### P2 Viewpoint Integration Points

1. **Element assignment**: Model maintains `_viewpoint_elements` reverse mapping
2. **View association**: Model maintains `_viewpoint_views` mapping
3. **Query methods**: `get_elements_by_viewpoint()` and `get_views_by_viewpoint()` provided
4. **Validation**: Viewpoint slugs validated on assignment and query via `validate_viewpoint_slug()`

---

## Design Readiness for P3

### Compatibility Assessment

| P3 Feature | Current State | Conflict? | Action |
|-----------|---------------|-----------|--------|
| Element parent UUID | None | ✅ No | Add `_parent_uuid` to Element |
| Model hierarchy maps | None | ✅ No | Add `_element_hierarchy` and `_element_children` to Model |
| Visual style dict | None | ✅ No | Add `_visual_style` to Element |
| Cycle detection queries | None | ✅ No | Add helper methods to Model for ancestor queries |
| Max depth validation | None | ✅ No | Add depth calculation method to Model |

### Recommended Storage Pattern

**Mirror P2 viewpoint pattern**:
```python
# In Model.__init__:
self._element_hierarchy: dict[str, Optional[str]] = {}  # child_uuid → parent_uuid
self._element_children: dict[str, set[str]] = {}        # parent_uuid → set(child_uuids)

# Query pattern (efficient):
def get_children(self, parent_uuid: str) -> list[Element]:
    child_uuids = self._element_children.get(parent_uuid, set())
    return [self.elems_dict[uid] for uid in child_uuids if uid in self.elems_dict]

def get_parent(self, child_uuid: str) -> Optional[Element]:
    parent_uuid = self._element_hierarchy.get(child_uuid)
    return self.elems_dict[parent_uuid] if parent_uuid else None
```

### Query Methods Needed

1. **`add_child(parent_uuid, child_uuid)`** - Add parent-child relationship
2. **`remove_child(parent_uuid, child_uuid)`** - Remove relationship
3. **`get_children(parent_uuid)`** - Get all direct children
4. **`get_ancestors(elem_uuid)`** - Get all parents up the tree (for cycle detection)
5. **`get_depth(elem_uuid)`** - Calculate depth in hierarchy
6. **`is_ancestor(potential_ancestor, elem_uuid)`** - Check if A is ancestor of B

---

## Summary

**Total Storage Structures**: 12 (10 dict, 2 from P2)  
**Total Query Methods**: 18 public + 2 P2-specific  
**Total Creation Methods**: 3 (add, add_relationship, add_profile)  
**Total Management Methods**: 12 (embed, expand, validate, theme, etc.)

**Ready for P3?** ✅ Yes
- Storage structures are well-organized
- Query patterns established and reusable
- P2 viewpoint pattern provides excellent template for P3 hierarchy
- No conflicts detected
- Recommended approach: Add `_element_hierarchy` and `_element_children` dicts to Model; add helper query methods
