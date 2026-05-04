# P3 Phase 1: Foundation & Design Execution Guide

**Date**: 2026-05-01  
**Branch**: `005-archimate-notation-support`  
**Phase**: 1 of 8  
**Timeline**: 2-3 days  
**Status**: Starting Now

---

## Overview

Phase 1 focuses on **research, auditing, design documentation, and test fixture preparation**. No implementation code is written in this phase—it's purely planning and design.

**Deliverables by end of Phase 1**:
- [ ] Detailed audit of Element and Model classes
- [ ] Design document for containment tracking and visual style storage
- [ ] Test fixtures with real Archi sample files
- [ ] P3 design document finalized

---

## Tasks (7 Total)

### T121: Audit Element Class ⭐ START HERE

**Goal**: Document all existing attributes, public API, and validation rules

**What to Do**:
1. Read `/src/pyArchimate/element.py` completely
2. List all instance attributes (lines 92-114):
   - `_uuid`, `parent`, `model`, `name`, `_type`, `desc`, `folder`, `_properties`, `_profile`, `junction_type`, `_viewpoints`
3. List all public methods and properties
4. Document validation in `__init__` (ARCHI_CATEGORY checks, parent type checks)
5. Note: `junction_type` already exists (line 112) ✅
6. Create audit document: `/docs/P3_AUDIT_ELEMENT_CLASS.md`

**Expected Output**:

```markdown
# Element Class Audit (T121)

## Existing Attributes
- _uuid: str (generated, immutable)
- parent: Model reference
- name: Optional[str]
- _type: Optional[str] (elem_type)
- junction_type: Optional[str] = None
- _viewpoints: list[str] (from P2)
- ... (full list)

## Existing Methods
- __init__(), delete(), uuid property, ...

## Validation Rules
- elem_type must exist in ArchiType enum
- elem_type must exist in ARCHI_CATEGORY
- ARCHI_CATEGORY[elem_type] != 'Relationship'
- parent must be Model instance
```

**Estimated Time**: 1-2 hours

---

### T122: Audit Model Class

**Goal**: Understand element storage, querying, and current structure

**What to Do**:
1. Read `/src/pyArchimate/model.py` (focus on `__init__` and key methods)
2. Document storage structures:
   - `elems_dict: dict[str, Element]` (UUID → Element mapping)
   - `rels_dict: dict[str, Relationship]` (relationships)
   - `_viewpoint_elements: dict[str, set[str]]` (from P2, UUID sets per viewpoint)
   - `_viewpoint_views: dict[str, str]` (from P2, view UUID → viewpoint)
3. Note existing query methods
4. Check for any conflicts with planned hierarchy tracking
5. Create audit document: `/docs/P3_AUDIT_MODEL_CLASS.md`

**Expected Output**:

```markdown
# Model Class Audit (T122)

## Existing Storage
- elems_dict: Maps element UUID → Element object
- rels_dict: Maps relationship UUID → Relationship object
- _viewpoint_elements: Maps viewpoint slug → set of element UUIDs
- _viewpoint_views: Maps view UUID → primary viewpoint slug

## Existing Query Methods
- get_elements(), get_relationships(), get_views()
- get_viewpoints(), get_elements_by_viewpoint(), get_views_by_viewpoint()

## Constraints & Considerations
- No existing parent-child tracking
- No existing visual style storage on Element
- P2 viewpoint tracking pattern can be reused for hierarchy
```

**Estimated Time**: 1-2 hours

---

### T123: Design Containment Tracking

**Goal**: Finalize design for element parent-child relationships

**What to Do**:
1. Based on T121 & T122 audit, design the storage mechanism:
   - **Option A**: Add to Element directly (`_parent_uuid`, `_children_uuids`)
   - **Option B**: Store in Model (`_element_hierarchy: dict[str, Optional[str]]`)
   - **Option C**: Hybrid (Element stores parent; Model stores reverse mapping for queries)
  
2. Recommendation: **Option C (Hybrid)**
   - Element stores `_parent_uuid: Optional[str]`
   - Model maintains `_element_hierarchy: dict[str, Optional[str]]` (child → parent)
   - Model maintains `_element_children: dict[str, set[str]]` (parent → children)
  
3. Design cycle detection algorithm:
  
   ```
def add_child(parent, child):
     if child == parent: raise ValueError("Self-reference")
     if parent in get_ancestors(child): raise ValueError("Cycle detected")
     # ... proceed with add

   ```
  
4. Design max depth enforcement (5 levels)

5. Create design document: `/docs/P3_DESIGN_CONTAINMENT.md`

**Expected Output**:

```markdown
# Containment Tracking Design (T123)

## Storage Strategy: Hybrid Approach
- Element._parent_uuid: Optional[str]
- Model._element_hierarchy: dict[child_uuid → parent_uuid]
- Model._element_children: dict[parent_uuid → set(child_uuids)]

## Invariants
- Acyclic: No A→B→A chains allowed
- Max depth: 5 levels
- Unique parent: Each element has at most 1 parent

## Cycle Detection
- O(depth) algorithm using visited set traversal
- Called in add_child() before mutation

## Cascade Delete
- Deleting element removes from _element_hierarchy and _element_children
- Children orphaned (parent set to None)
```

**Estimated Time**: 1-2 hours

---

### T124: Design Visual Style Storage

**Goal**: Choose storage approach for fill_color, line_color, line_width, transparency

**What to Do**:
1. Compare approaches:
   - **Option A**: Property dict (`Element._visual_style = {fill_color, line_color, ...}`)
   - **Option B**: Dataclass (`Element._visual_style: VisualStyle(fill_color=..., ...)`)
   - **Option C**: Individual attributes (`Element.fill_color`, `Element.line_color`, ...)

2. Recommendation: **Option A (Property Dict)**
   - Mirrors P2 viewpoint approach (property-based storage)
   - Easy to serialize (property keys match XML attribute names)
   - Flexible for future additions (new properties without code changes)
  
3. Design color validation:
   - Accept: hex (#RRGGBB), named colors (red, blue, etc.), None
   - Normalize to lowercase hex
   - Standard palette defaults
  
4. Design getter/setter methods:
  
   ```python
   def set_visual_style(fill_color=None, line_color=None, line_width=None, transparency=None)
def get_visual_style() -> dict

   ```

5. Create design document: `/docs/P3_DESIGN_VISUAL_STYLE.md`

**Expected Output**:

```markdown
# Visual Style Storage Design (T124)

## Storage: Property Dict Approach
- Element._visual_style: dict = {
    'fill_color': '#0066FF',
    'line_color': '#000000',
    'line_width': 2.0,
    'transparency': 0.8
  }

## Color Validation
- Hex: #RRGGBB (normalized to lowercase)
- Named: 'red', 'blue', etc. (converted to hex)
- None: Use defaults from standard palette

## Standard Palette (ArchiMate defaults)
- Business: #FFFFB5
- Application: #B5FFFF
- Technology: #C9E7B7
- Motivation: #CCCCFF
- Implementation: #FFE0E0
- Relationship: #DDDDDD

## Serialization
- Property dict → <property> XML elements (mirrors P2 approach)
- fill_color → key='fillColor'
- line_color → key='lineColor'
```

**Estimated Time**: 1 hour

---

### T125: Verify Folder Concept

**Goal**: Confirm folders don't conflict with element grouping

**What to Do**:
1. Research folder usage in codebase:
   - Search for `folder` attribute usage in element.py
   - Check how folders are stored in model.py
   - Confirm folders are metadata (string path), not Element objects
  
2. Understand distinction:
   - **Folder**: Metadata for organization (e.g., "/Business/Processes")
   - **Grouping**: Semantic parent-child relationships (element containment)
  
3. Confirm no conflicts:
   - Folder path is independent of parent UUID
   - Grouping doesn't change folder structure
   - Both can coexist
  
4. Create design document: `/docs/P3_FOLDER_VS_GROUPING.md`

**Expected Output**:

```markdown
# Folder vs Grouping Design (T125)

## Folder (Metadata)
- String path: "/Business/Processes/Order"
- Used for model organization
- Does not affect element relationships

## Grouping (Semantic)
- Parent UUID: element._parent_uuid
- Enables hierarchical containment
- Affects relationship validation (future)

## Coexistence
- Folder path and parent UUID are independent
- Element can have both folder="/Path" and parent_uuid="id-xyz"
- No conflicts
```

**Estimated Time**: 1 hour

---

### T126: Create Comprehensive P3 Design Document

**Goal**: Consolidate all design decisions into one master document

**What to Do**:
1. Gather outputs from T121-T125
2. Consolidate into `/docs/P3_DESIGN_MASTER.md`:
   - Element audit findings
   - Model audit findings
   - Containment tracking design
   - Visual style storage design
   - Folder vs grouping clarification
   - Architecture decisions (why these choices)
   - Implementation constraints and invariants
  
3. Add sections:
   - **Data Model**: Final class additions and signatures
   - **XML Serialization**: How nested elements and properties map to XML
   - **Validation Rules**: Cycle detection, depth limits, color validation
   - **Testing Strategy**: What to test in later phases
   - **Risk Mitigation**: Potential pitfalls and how to avoid

**Expected Output**: Comprehensive 10-15 page design document

**Estimated Time**: 2-3 hours

---

### T127: Create Test Fixtures

**Goal**: Build sample .archimate files for testing grouped elements, junctions, visual properties

**What to Do**:
1. Create directory: `/tests/fixtures/p3_notation/`
2. Build sample files (using real Archi structure):
   - `grouped_elements.archimate`: 3-level nesting (Process → Function → Function)
   - `junctions_and_flow.archimate`: AND/OR/XOR junctions with relationships
   - `styled_elements.archimate`: Elements with custom fill/line colors
   - `combined_features.archimate`: All three features together

3. Use existing sample as template: `/tests/fixtures/myModel.archimate`
4. Manually create or use test utilities to generate XML
5. Verify files parse correctly: `python -m pyArchimate.readers.archiReader <file>`

**Expected Output**: 4 valid .archimate files in `/tests/fixtures/p3_notation/`

**Estimated Time**: 2-3 hours

---

## Daily Checklist

### Day 1 (Today): T121-T123
- [ ] T121: Audit Element class (1-2 hours)
- [ ] T122: Audit Model class (1-2 hours)
- [ ] T123: Design containment tracking (1-2 hours)
- **Total**: 3-6 hours

### Day 2: T124-T126
- [ ] T124: Design visual style storage (1 hour)
- [ ] T125: Verify folder concept (1 hour)
- [ ] T126: Create master design document (2-3 hours)
- **Total**: 4-5 hours

### Day 3: T127 + Review
- [ ] T127: Create test fixtures (2-3 hours)
- [ ] Review all design documents
- [ ] Prepare for Phase 2 kickoff
- **Total**: 3-4 hours

---

## Success Criteria for Phase 1

✅ **All 7 tasks complete**:
- [ ] T121: Element audit document created
- [ ] T122: Model audit document created
- [ ] T123: Containment design document created
- [ ] T124: Visual style design document created
- [ ] T125: Folder vs grouping clarification created
- [ ] T126: Comprehensive master design document created
- [ ] T127: 4 test fixture files created and validated

✅ **Design validated**:
- [ ] Architecture has no conflicts with existing code
- [ ] Cycle detection algorithm clear and implementable
- [ ] Color validation rules complete
- [ ] Serialization strategy (nested XML + properties) confirmed

✅ **Ready for Phase 2**:
- [ ] All design documents reviewed and approved
- [ ] Test fixtures available for integration testing
- [ ] Team alignment on approach

---

## Resources

**Reference Documents**:
- `/specs/004-archimate-spec-compliance/P3_NOTATION_SPEC.md` — Feature specification
- `/specs/004-archimate-spec-compliance/P3_TASKS.md` — Full task list
- `/src/pyArchimate/element.py` — Element class to audit
- `/src/pyArchimate/model.py` — Model class to audit
- `/tests/fixtures/myModel.archimate` — Template for test fixtures

**Guidelines**:
- Keep design documents concise but complete (2-5 pages each)
- Use code examples where helpful
- Document invariants and constraints clearly
- Get feedback on design before Phase 2 begins

---

## Next Phase Preview

Once Phase 1 is complete, Phase 2 will implement:
- [ ] T128-T137: Element grouping core classes (10 tasks)
  - Add parent/children attributes
  - Implement add_child/remove_child
  - Implement traversal methods
  - Add unit tests

**Phase 2 Timeline**: 3-4 days (immediately after Phase 1)

---

## Questions?

If you encounter questions during Phase 1:
1. Check the design documents from T121-T125
2. Refer to `/specs/004-archimate-spec-compliance/P3_NOTATION_SPEC.md`
3. Look at P2 implementation (viewpoints) for pattern examples
4. Reach out for clarification

**Good luck with Phase 1!** 🚀

---

**Phase 1 Start**: 2026-05-01  
**Phase 1 Target End**: 2026-05-03 (2-3 days)  
**Phase 2 Start**: 2026-05-04
