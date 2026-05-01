# Element Class Audit (T121)

**Date**: 2026-05-01  
**Status**: Complete  
**File Audited**: `/src/pyArchimate/element.py` (418 lines)

---

## Existing Attributes

All instance attributes are initialized in `__init__()` (lines 103-113):

| Attribute | Type | Purpose | Immutable? | Notes |
|-----------|------|---------|-----------|-------|
| `_uuid` | `str` | Unique element identifier (UUID v4, no dashes, id- prefix) | ✅ Yes | Generated via `set_id()` if not provided |
| `parent` | `Model` | Reference to parent Model object | ❌ No | Set via `__init__`, stored as cast to Model |
| `model` | `Model` | Alias for `parent` reference | ❌ No | Same as `parent`, kept for backward compat |
| `name` | `Optional[str]` | Human-readable element name | ❌ No | Can be None; no validation on assignment |
| `_type` | `Optional[str]` | ArchiMate concept type (e.g., 'BusinessProcess') | ❌ No | Has setter with validation (see below) |
| `desc` | `Optional[str]` | Element description text | ❌ No | Can be None; supports multi-line |
| `folder` | `Optional[str]` | Organizational folder path (e.g., "/Business/Processes") | ❌ No | Metadata only; no parent-child semantics |
| `_properties` | `dict[str, object]` | Key-value property storage | ❌ No | Empty dict on init; modified via `prop()` methods |
| `_profile` | `Optional[str]` | Profile UUID reference | ❌ No | Set via `set_profile()`, reset via `reset_profile()` |
| `junction_type` | `Optional[str]` | AND/OR/XOR junction semantics (P3 feature) | ❌ No | Initialized as None; used for gateways |
| `_viewpoints` | `list[str]` | Canonical ArchiMate viewpoint slug assignments (P2) | ❌ No | Empty list on init; modified via `assign_viewpoint()` / `remove_viewpoint()` |

---

## Existing Methods & Properties

### Lifecycle Methods

**`__init__(elem_type=None, name=None, uuid=None, desc=None, folder=None, parent=None, profile=None)`** (lines 92-113)
- Initializes all attributes
- Validates arguments (see Validation Rules below)
- Sets `_uuid` via `set_id(uuid)`
- Raises: `ArchimateConceptTypeError`, `ValueError`

**`delete()`** (lines 115-140)
- Removes element from parent model
- Deletes all visual nodes referencing this element
- Deletes all relationships (source or target) involving this element
- Removes element from parent's `elems_dict`
- Does NOT delete the Python instance itself

### Property Accessors

**`uuid` (property)** (lines 142-150)
- Returns: `str` (immutable identifier)
- Read-only

**`type` (property with setter)** (lines 152-176)
- Getter: Returns current ArchiMate type
- Setter: Validates new type before assignment; raises `ValueError` if invalid or Relationship type

**`profile_name` (property)** (lines 178-193)
- Returns: Name of associated profile or None
- Lookup: Searches `self.model.profiles` by `_profile` UUID

**`profile_id` (property)** (lines 195-209)
- Returns: UUID of associated profile or None
- Lookup: Searches `self.model.profiles` by `_profile` UUID

**`props` (property)** (lines 236-244)
- Returns: All properties as dict
- Returns: `dict[str, object]` (the full `_properties` dict)

**`viewpoints` (property, P2)** (lines 381-388)
- Returns: List of assigned viewpoint slug strings
- Returns: Copy of internal list (safe for mutation by caller)

### Property Management

**`prop(key, value=None)`** (lines 246-261)
- If `value is None`: Returns property value or None
- If `value` provided: Sets property and returns value

**`remove_prop(key)`** (lines 263-272)
- Removes property by key (silently ignores missing key)

### Profile Management

**`set_profile(profile_name)`** (lines 211-231)
- Finds existing profile by name in `self.model.profiles`
- If found: Sets `_profile` to that profile's UUID
- If not found: Creates new profile and sets `_profile` to new UUID

**`reset_profile()`** (lines 233-234)
- Sets `_profile` to None

### Relationship Querying

**`in_rels(rel_type=None)`** (lines 313-330)
- Returns: List of inbound relationships (where this element is target)
- Filter: Optional relationship type filtering

**`out_rels(rel_type=None)`** (lines 332-349)
- Returns: List of outbound relationships (where this element is source)
- Filter: Optional relationship type filtering

**`rels(rel_type=None)`** (lines 351-372)
- Returns: List of all relationships (inbound + outbound)
- Filter: Optional relationship type filtering

### Viewpoint Management (P2)

**`assign_viewpoint(viewpoint_id)`** (lines 390-403)
- Validates viewpoint slug via `validate_viewpoint_slug()`
- Appends to `_viewpoints` if not already present
- Updates parent's `_viewpoint_elements` reverse mapping
- Raises: `ValueError` if viewpoint_id unrecognized

**`remove_viewpoint(viewpoint_id)`** (lines 405-414)
- Removes viewpoint from `_viewpoints` (silently ignores unknown slugs)
- Updates parent's `_viewpoint_elements` reverse mapping via `discard()`

### Folder Management

**`remove_folder()`** (lines 374-379)
- Sets `folder` to None

### Merging (Internal)

**`merge(elem, merge_props=False)`** (lines 281-311)
- Merges another element into this one
- Type check: Raises if elem's type != self's type
- Optional property merging via `_merge_properties_and_desc()`
- Reassigns all node references to this element
- Reassigns all relationship references to this element
- Deletes the merged element

**`_merge_properties_and_desc(elem)`** (lines 274-279, private)
- Merges properties from another element (skips existing keys)
- Appends elem's description to self's description (with separator)

---

## Validation Rules

### In `__init__()` (lines 94-100)

1. **elem_type Validation** (lines 95-96)
   - Must not be None
   - Must be a valid attribute in `ArchiType` enum
   - Check: `hasattr(ArchiType, elem_type)`
   - Raises: `ArchimateConceptTypeError`

2. **elem_type Category Check** (lines 97-98)
   - elem_type must not be a Relationship type
   - Check: `ARCHI_CATEGORY[elem_type] != 'Relationship'`
   - Raises: `ArchimateConceptTypeError`

3. **parent Type Check** (lines 99-100)
   - If parent is not None, must have `elems_dict` attribute
   - Check: `hasattr(parent, "elems_dict")`
   - Raises: `ValueError`

### In `type` setter (lines 173-176)

1. **Type Validity**
   - New type must exist in `ARCHI_CATEGORY`
   - Must not be 'Relationship' type
   - Raises: `ValueError`

### In `assign_viewpoint()` (line 398)

1. **Viewpoint Slug Validation**
   - Validates via `validate_viewpoint_slug(viewpoint_id)` (external module)
   - Must be a canonical slug (e.g., 'stakeholder', 'business_process')
   - Raises: `ValueError` if unrecognized

---

## Key Design Notes

### Already Present from P2
- `junction_type` attribute (line 112) ✅ Already exists
- `_viewpoints` list (line 113) ✅ Already exists
- `assign_viewpoint()` method ✅ Already exists
- `remove_viewpoint()` method ✅ Already exists
- `viewpoints` property ✅ Already exists

### No Existing Parent-Child Tracking
- No `_parent_uuid` attribute
- No `_children_uuids` list
- No methods for adding/removing children
- **Implication**: Grouping will be new functionality (P3 feature)

### No Existing Visual Style Storage
- No `_visual_style` dict
- No color/width/transparency properties
- **Implication**: Visual properties will be new functionality (P3 feature)

### Folder is Metadata Only
- `folder` is a string path, not an Element reference
- No semantic parent-child relationship semantics
- Can coexist with future P3 grouping (parent UUID)

### Property Storage Pattern
- Properties stored in `_properties` dict (line 110)
- P2 viewpoint assignments stored in `_viewpoints` list (line 113)
- **Pattern used for P3**: Store visual properties in similar dict/list structure

---

## Summary

**Total Attributes**: 11 (1 immutable, 10 mutable)  
**Total Methods**: 17 public (4 properties, 13 methods)  
**Total Private Methods**: 1 (`_merge_properties_and_desc`)  
**Validation Rules**: 5 at init time + 2 in type setter + 1 in assign_viewpoint

**Ready for P3?** ✅ Yes
- Element class is well-structured
- No conflicts detected with planned P3 features
- Existing patterns (property dict, list-based association) can be reused
- Recommended approach: Add `_parent_uuid` attribute, `_visual_style` dict to Element; no major refactoring needed
