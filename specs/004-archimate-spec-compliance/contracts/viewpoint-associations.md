# Contract: Viewpoint Associations and Assignments

**Version**: 1.0  
**Date**: 2026-05-01  
**Type**: Structural Metadata Contract  
**Status**: Complete (P2 Implementation)

## Overview

Defines the representation, storage, and serialization of ArchiMate 3.x viewpoint associations. Supports both view-level primary viewpoint assignments and element-level multi-viewpoint associations, with round-trip fidelity across .archimate and OpenGroup exchange formats.

---

## Canonical Representation

### View-Level: Primary Viewpoint

**Storage**: `View._primary_viewpoint` (single Optional[str] slug)  
**Format**: Canonical lowercase slug (e.g., 'stakeholder', 'technology')  
**Cardinality**: 0 or 1 per view  
**Serialization**:
- **.archimate format**: XML attribute `viewpoint="<slug>"` on `<view>` element
- **OpenGroup format**: Property element with `key="viewpoint"` and `value="<slug>"`

### Element-Level: Viewpoint Associations

**Storage**: `Element._viewpoints` (list[str] of canonical slug strings)  
**Format**: Canonical lowercase slugs, no duplicates  
**Cardinality**: 0..N per element  
**Serialization**:
- **.archimate format**: Multiple `<property key="viewpoint" value="<slug>"/>` child elements
- **OpenGroup format**: Multiple property elements (same pattern)

---

## Canonical Viewpoint Registry

### All 13 Standard ArchiMate 3.x Viewpoints

| Slug | Name | Category | Description |
|------|------|----------|-------------|
| `stakeholder` | Stakeholder Viewpoint | Motivation | Addresses stakeholder concerns and requirements |
| `capability` | Capability Viewpoint | Business | Shows capability maps and realisation |
| `organization` | Organization Viewpoint | Business | Shows the organizational structure |
| `actor` | Actor Cooperation Viewpoint | Business | Shows cooperation between business actors |
| `technology` | Technology Viewpoint | Technology | Shows the technology infrastructure and platforms |
| `physical` | Physical Viewpoint | Technology | Shows physical infrastructure and networks |
| `service` | Application Service Viewpoint | Application | Shows the application services and realisation |
| `implementation` | Implementation and Deployment Viewpoint | Implementation | Shows mapping of components to infrastructure |
| `migration` | Migration Viewpoint | Implementation | Shows transition between current and target states |
| `strategy` | Strategy Viewpoint | Motivation | Shows strategic goals, drivers, and principles |
| `business` | Business Process Viewpoint | Business | Shows business processes and their relationships |
| `application` | Application Cooperation Viewpoint | Application | Shows application component interactions |
| `infrastructure` | Infrastructure Viewpoint | Technology | Shows the hardware and communication infrastructure |

**Registry Location**: `src/pyArchimate/viewpoint_registry.py` (STANDARD_VIEWPOINTS constant)  
**Validation**: All slug assignments validated via `validate_viewpoint_slug()` function

---

## XML Serialization

### Element Viewpoint Associations (.archimate)

**Example**:

```xml
<element id="id-abc123" name="Customer Service" xsi:type="BusinessActor">
  <property key="viewpoint" value="stakeholder"/>
  <property key="viewpoint" value="capability"/>
  <documentation>Handles customer interactions</documentation>
</element>
```

**Rules**:
- Each viewpoint assignment is a separate `<property>` element
- Property `key` is always literal string `"viewpoint"`
- Property `value` is the canonical lowercase slug
- Order of properties is not significant

### View Primary Viewpoint (.archimate)

**Example**:

```xml
<view id="id-view456" name="Stakeholder Map" viewpoint="stakeholder">
  <node id="n1" elementRef="id-abc123" x="10" y="20" w="120" h="55"/>
</view>
```

**Rules**:
- `viewpoint` is an optional XML attribute on the `<view>` element
- Value is the canonical lowercase slug
- Only one primary viewpoint per view (0 or 1)

### OpenGroup Exchange Format

**Element Properties**:

```xml
<property name="viewpoint" value="stakeholder"/>
<property name="viewpoint" value="capability"/>
```

**View Properties**:

```xml
<property name="viewpoint" value="technology"/>
```

---

## Normalization and Import Logic

### Viewpoint Name Normalization

**Stage 1: Raw Input Normalization**

```python
# From _archireader_helpers.py line 181, 241
slug = (property_value or '').strip().lower()
```

**Transformations Applied**:
1. Strip leading/trailing whitespace
2. Convert to lowercase
3. Reject empty strings

**Examples**:
- `"Stakeholder"` → `"stakeholder"` ✅
- `"TECHNOLOGY"` → `"technology"` ✅
- `"  capability  "` → `"capability"` ✅
- `""` → rejected (not added to element)

### Unrecognized Viewpoint Handling

**Behavior** (per T085 implementation):

```python
# _archireader_helpers.py line 184-187
if get_viewpoint(slug) is not None:
    elem.assign_viewpoint(slug)
else:
    log.warning(f"Unknown viewpoint slug '{slug}' ignored during import")
```

**Rules**:
- Unrecognized slugs are logged as warnings (not fatal)
- Import continues successfully (backward compatible)
- Element/view is created without the unrecognized viewpoint
- File can be re-exported without data loss (unknown slugs not written back)

**Rationale**: Ensures forward compatibility when newer ArchiMate versions introduce new viewpoints

### Vendor-Specific Name Mapping (Not Yet Implemented)

**Potential Future Enhancement**:
If external tools (Archi, Sparx) encode viewpoints with non-canonical names, a mapping table could be added:

```python
_VENDOR_VIEWPOINT_MAPPINGS = {
    'stakeholder viewpoint': 'stakeholder',
    'Stakeholder Viewpoint': 'stakeholder',
    'STAKEHOLDER_VIEWPOINT': 'stakeholder',
    'stakeholder_view': 'stakeholder',
    # ... etc for other tools/formats
}
```

**Current Status**: Not implemented (deferred pending vendor samples)

---

## State Management

### Lifecycle: Element Viewpoint Assignment

1. **Assign** (`element.assign_viewpoint(slug)`):
   - Validate slug against registry (raises ValueError if unknown)
   - Add slug to `element._viewpoints` (idempotent; ignores duplicates)
   - Add element UUID to `model._viewpoint_elements[slug]` (for indexing)

2. **Query** (`element.viewpoints`):
   - Returns copy of `element._viewpoints` list (immutable to caller)

3. **Remove** (`element.remove_viewpoint(slug)`):
   - Remove slug from `element._viewpoints` (silent if not present)
   - Remove element UUID from `model._viewpoint_elements[slug]` (safe if missing)

4. **Delete Element**:
   - Cascading cleanup: remove element UUID from all `model._viewpoint_elements[*]` entries
   - (Handled in `Element.delete()`)

**Invariants**:
- Element cannot have the same viewpoint assigned twice
- Unknown viewpoints cannot be assigned (validation prevents)
- Removing non-existent viewpoint is safe (silent)
- Registry is immutable at runtime (no viewpoint deletion scenarios)

### Lifecycle: View Primary Viewpoint

1. **Set** (`view.set_primary_viewpoint(slug)`):
   - Validate slug against registry (raises ValueError if unknown)
   - Set `view._primary_viewpoint = slug`
   - Add mapping `model._viewpoint_views[view_uuid] = slug` (for indexing)

2. **Get** (`view.primary_viewpoint`):
   - Returns `view._primary_viewpoint` (None if not set)

3. **Query by Viewpoint**:
   - Lookup `model._viewpoint_views` to find all views with given viewpoint

4. **Delete View**:
   - Cascading cleanup: remove view UUID from `model._viewpoint_views`
   - (Handled in `View.delete()`)

**Invariants**:
- View has at most one primary viewpoint (0 or 1)
- Unknown viewpoints cannot be set (validation prevents)
- Primary viewpoint can be None (no required viewpoint)

---

## Round-Trip Fidelity

### Test Coverage

**Unit Tests** (test_element.py, test_view.py):
- T102: Element single/multi-assignment
- T103: View primary viewpoint get/set
- T104: Multi-assignment idempotency

**Integration Tests** (test_archimate_roundtrip.py):
- T106: .archimate format round-trip (element + view)
- T107: OpenGroup format round-trip (element + view)
- T108: Multi-assignment round-trip (2+ viewpoints preserved)
- T109: Backward compatibility (legacy files without viewpoints)

**BDD Acceptance Tests** (features/):
- viewpoint_assignment.feature (Scenarios 1-4)
- viewpoint_roundtrip.feature (Scenarios 1-4)

### Guarantees

✅ Element viewpoint assignments survive export/import (100% fidelity)  
✅ View primary viewpoint survives export/import (100% fidelity)  
✅ Multi-viewpoint assignment preserved without reordering issues  
✅ Legacy files (no viewpoints) import without error  
✅ Unknown viewpoints logged but don't break import

---

## Implementation Files

**Core Classes**:
- `src/pyArchimate/viewpoint.py` - Viewpoint dataclass
- `src/pyArchimate/viewpoint_registry.py` - Registry + validation
- `src/pyArchimate/element.py` - Element.assign_viewpoint(), remove_viewpoint(), viewpoints property (lines 390-414)
- `src/pyArchimate/view.py` - View.set_primary_viewpoint(), primary_viewpoint property (lines 1031-1042)
- `src/pyArchimate/model.py` - _viewpoint_elements, _viewpoint_views dicts + query methods (lines 204-205, 805-831)

**Readers**:
- `src/pyArchimate/readers/_archireader_helpers.py` - Extract viewpoint properties from elements/views (lines 180-187, 241-247)
- `src/pyArchimate/readers/archimateReader.py` - Import orchestration

**Writers**:
- `src/pyArchimate/writers/archiWriter.py` - Serialize viewpoint properties to XML (lines 92-94, 279-281)
- `src/pyArchimate/writers/archimateWriter.py` - OpenGroup export

**Tests**:
- `tests/unit/test_element.py` - Element viewpoint methods
- `tests/unit/test_view.py` - View primary viewpoint
- `tests/unit/test_viewpoint.py` - Registry validation
- `tests/integration/test_archimate_roundtrip.py` - Round-trip fidelity
- `tests/features/viewpoint_*.feature` - BDD scenarios

---

## Validation & Error Handling

### Valid Slug Format

**Pattern**: `^[a-z_]+$` (lowercase alphanumeric + underscore, no hyphens)  
**Examples**:
- ✅ `stakeholder`, `technology`, `business`, `actor`
- ❌ `Stakeholder`, `technology-view`, `123_tech`, `tech.view`

### Error Messages

**Invalid Slug Assignment**:

```
ValueError: Unknown viewpoint slug 'invalid'. Valid slugs: actor, application, business, capability,
    implementation, infrastructure, migration, organization, physical, service, stakeholder,
    strategy, technology
```

**Invalid Slug for View**:

```
ValueError: Unknown viewpoint slug 'my_custom_view'. Valid slugs: actor, application, business, ...
```

---

## Future Enhancements (Out of Scope for P2)

1. **Vendor-specific mappings**: Add fallback for tool-specific viewpoint names
2. **Custom viewpoints**: Allow extension registry for domain-specific viewpoints
3. **Perspective support** (P3): Separate concept for stakeholder-specific views overlaid on viewpoints
4. **Viewpoint restrictions**: Enforce constraints on which elements/relationships can appear in each viewpoint

---

## Compliance Notes

- **ArchiMate 3.x Spec**: Compliant with viewpoint definitions and standard set
- **OpenGroup Exchange Format**: Compatible with Property element representation
- **Backward Compatibility**: Files without viewpoint metadata import without error (elements have empty viewpoints)
- **Cross-Platform**: lxml and dict-based storage are platform-agnostic
