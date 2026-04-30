# Feature Specification: ArchiMate v3.x Specification Compliance

**Feature Branch**: `003-archimate-spec-compliance`  
**Created**: 2026-04-30  
**Status**: Draft  
**Input**: User description: "Make the pyArchimate library compliant with Archimate v3.x specification using the content @Archimategap.md for context"

## Clarifications

### Session 2026-04-30

- Q1: Feature scope and priority staging → A: P1 only (BusinessInteraction, influence strength, documentation)
- Q2: Out-of-scope requirements handling → C: Move P2/P3 to separate "Future Features" section
- Q3: Influence strength field naming → B: Use `influenceStrength` for both .archimate and OpenGroup formats
- Q4: FR-004 OpenGroup import coverage → B: Update T012 to explicitly test both .archimate and OpenGroup import formats; existing reader handles both once category mapping is enabled

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create BusinessInteraction Elements (Priority: P1)

A developer using pyArchimate needs to create, import, or export `BusinessInteraction` elements as defined in the ArchiMate 3.x specification. Currently, `BusinessInteraction` is recognized in `ArchiType` and referenced in relationship rules, but the element cannot be instantiated because it is commented out in `ARCHI_CATEGORY`, causing `Element.__init__` to fail validation.

**Why this priority**: Critical blocker. A core ArchiMate concept exists in the library but cannot be created, making the library non-compliant with the specification and breaking user workflows that require this element type.

**Independent Test**: Can be fully tested by creating a BusinessInteraction element, importing an .archimate file containing BusinessInteraction, and exporting a model with BusinessInteraction elements. The feature delivers immediate spec compliance for this concept.

**Acceptance Scenarios**:

1. **Given** a developer has imported pyArchimate, **When** they create `Element(name='X', elem_type=ArchiType.BusinessInteraction)`, **Then** the element is created successfully without validation errors
2. **Given** an .archimate file contains a BusinessInteraction element, **When** the file is imported, **Then** the element is parsed and available in the model
3. **Given** a model with BusinessInteraction elements, **When** the model is exported to .archimate format, **Then** the BusinessInteraction elements are preserved in the output
4. **Given** a model with BusinessInteraction elements, **When** the model is exported to OpenGroup exchange format, **Then** the BusinessInteraction elements are correctly mapped and preserved

---

### User Story 2 - Preserve Influence Strength in Round-Trip (Priority: P1)

A developer exports an ArchiMate model with influence relationships that have strength metadata, then imports it back. The metadata must survive the round-trip without loss or inconsistency. Currently, the reader path reads `modifier` for influence strength, but the writer emits `influenceStrength`, causing potential data loss or corruption.

**Why this priority**: Critical data fidelity issue. Relationship metadata is lost in round-trip operations, affecting data integrity and making the library unsuitable for reliable model exchange.

**Independent Test**: Can be fully tested by creating a model with influence relationships with specific strength values, exporting to .archimate format, re-importing the file, and verifying the strength metadata is preserved identically. Delivers complete round-trip fidelity.

**Acceptance Scenarios**:

1. **Given** a model with an influence relationship with strength value "high", **When** exported to OpenGroup format and re-imported, **Then** the strength value is preserved as "high"
2. **Given** a model with an influence relationship with custom strength modifier, **When** exported to .archimate format and re-imported, **Then** the modifier is preserved correctly
3. **Given** files created by external tools (e.g., Archi) with influence strength metadata, **When** imported into pyArchimate, **Then** the strength metadata is correctly interpreted and preserved on export

---

### User Story 3 - Preserve Relationship Documentation (Priority: P1)

A developer imports an Archi .archimate file containing relationships with documentation text. The documentation must be fully preserved and accessible. Currently, the Archi reader parser finds the `<documentation>` element but assigns the wrong value, potentially losing the documentation text.

**Why this priority**: Data loss bug affecting file fidelity. Documentation is critical metadata for enterprise architecture models, and losing it damages the value of imported files.

**Independent Test**: Can be fully tested by importing an .archimate file with documented relationships, verifying the documentation is accessible, and exporting/re-importing to confirm preservation. Delivers complete documentation fidelity.

**Acceptance Scenarios**:

1. **Given** an .archimate file with a relationship containing documentation, **When** imported, **Then** the documentation text is accessible via the relationship's description field
2. **Given** an imported relationship with documentation, **When** the model is exported to .archimate format, **Then** the documentation is preserved in the output
3. **Given** relationships with empty, long, and special-character documentation, **When** imported and exported, **Then** all documentation text is preserved exactly as provided

---

### Edge Cases

- What happens when importing files from Archi that use BusinessInteraction elements with no prior version support?
- How does the system handle models with mixed specification versions (some new ArchiMate 3.x concepts, some legacy)?
- What if documentation in relationships contains Unicode, XML special characters, or very long text?
- What if influence strength is specified in legacy Archi format (using `modifier` field)? System must map it to `influenceStrength` transparently.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST uncomment and enable `BusinessInteraction` in `ARCHI_CATEGORY` so that `Element.__init__` accepts it as a valid element type
- **FR-002**: System MUST allow creation of `Element` instances with `elem_type=ArchiType.BusinessInteraction` without validation errors
- **FR-003**: System MUST correctly parse and import `BusinessInteraction` elements from .archimate files
- **FR-004**: System MUST correctly parse and import `BusinessInteraction` elements from OpenGroup exchange format files (covered by existing OpenGroup reader once ARCHI_CATEGORY category mapping is enabled in FR-001)
- **FR-005**: System MUST correctly export `BusinessInteraction` elements to both .archimate and OpenGroup exchange formats with proper type mapping
- **FR-006**: System MUST read influence strength metadata consistently using the field name `influenceStrength` for both OpenGroup exchange format and .archimate format (mapping legacy `modifier` field to `influenceStrength` transparently during import)
- **FR-007**: System MUST write influence strength metadata using the field name `influenceStrength` for both OpenGroup and .archimate export formats
- **FR-008**: System MUST preserve influence strength values through complete round-trip operations (create → export → import → export)
- **FR-009**: System MUST correctly extract and preserve relationship documentation text from Archi .archimate files
- **FR-010**: System MUST store relationship documentation in the relationship description field where it can be accessed and modified
- **FR-011**: System MUST preserve relationship documentation through round-trip operations

### Key Entities

- **BusinessInteraction**: An ArchiMate element representing a business-level interaction concept, with relationships to other business elements
- **InfluenceRelationship**: A relationship with strength metadata indicating influence level between elements
- **DocumentedRelationship**: Any relationship that may have documentation text attached describing its purpose or semantics

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All P1 gaps identified in gap analysis are resolved (BusinessInteraction, influence strength round-trip fidelity, and relationship documentation preservation)
- **SC-002**: Round-trip fidelity tests for all relationship metadata pass 100% without data loss
- **SC-003**: Import of .archimate and OpenGroup exchange files with ArchiMate 3.x BusinessInteraction and influence strength features succeeds without validation errors
- **SC-004**: Documentation text is preserved for 100% of relationships in test files across round-trip operations
- **SC-005**: All existing tests continue to pass (no regression in current functionality)
- **SC-006**: New compliance tests demonstrate full ArchiMate 3.x spec alignment for P1 features

## Assumptions

- `Element.__init__` and related validation logic will be the primary point of change for enabling BusinessInteraction
- Relationship metadata storage uses existing Element/Relationship property mechanisms without requiring new field types
- The fix for documentation text involves correcting the assignment in the Archi reader helper without changing the overall parsing flow
- Files created by Archi and other compliant tools follow the ArchiMate 3.x schema closely enough that correct field name alignment will resolve round-trip issues
- Testing can validate compliance using existing test infrastructure and sample files from gap analysis

## Future Features (Out of Scope for v1)

The following user stories and requirements have been identified but are deferred to a future feature release:

### User Story 4 - Support ArchiMate Perspectives and Viewpoints (Priority: P2)

A developer using ArchiMate viewpoints (e.g., stakeholder view, capability view) in external models needs to import and work with viewpoint-aware models in pyArchimate. Currently, perspectives and viewpoints are not first-class concepts, limiting semantic fidelity and forcing workarounds.

**Deferred Requirements**:
- System MUST represent ArchiMate viewpoint concepts as first-class domain objects in the model
- System MUST correctly parse viewpoint definitions from exchange format files
- System MUST associate views and elements with their assigned viewpoints
- System MUST preserve viewpoint associations through export operations

### User Story 5 - Support Complete ArchiMate Notation (Priority: P3)

A developer creating complex architectural diagrams relies on ArchiMate notation elements such as grouped elements, junctions, and explicit visual semantics. While basic notation is preserved, some notation features are not fully modeled, limiting expressiveness.

**Deferred Requirements**:
- System MUST preserve complete ArchiMate notation including grouped elements, junctions, and other visual semantics
