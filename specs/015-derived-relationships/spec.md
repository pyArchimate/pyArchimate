# Feature Specification: Derived Relationships (Scan & Render-Time Computation)

**Feature Branch**: `015-derived-relationships`
**Created**: 2026-09-13
**Status**: Draft
**Input**: User description: "GitHub issue #140: Compute derived relationships at view-render time instead of persisting them in the model. Follow-up to #139. Without derivation support, a modeler either omits the useful direct A→C relationship implied by a chain A—r1→B—r2→C, or duplicates it explicitly (which drifts out of sync as the chain changes). Requested capabilities: (1) a scan/lint mode reporting explicit relationships that duplicate what the ArchiMate 3.2 §3.5 derivation rule already implies, so they can be reviewed/removed; (2) a render-time helper that computes the derived relationship between two unconnected elements per the same rule, without writing it back to the model. Scope is limited to the unambiguous subset of the derivation rule (Composition/Aggregation/Assignment/Realization/Serving/Triggering/Flow); Access/Influence/Specialization/Association are intentionally left to a human."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find redundant explicit relationships that duplicate an implied chain (Priority: P1)

A modeler has a model where a relationship chain (e.g., element A is Assigned to B, and B Realizes C) already implies a direct relationship between A and C per the ArchiMate derivation rule. Somewhere else in the model, an explicit relationship of that same implied type already exists directly between A and C, duplicating what the chain implies. The modeler wants a report of every such duplicate so they can review and decide whether to remove it, rather than discovering the drift by accident when the chain and the explicit relationship disagree.

**Why this priority**: This is the concrete pain point raised in the issue — duplicated relationships silently drift out of sync as chains change over time. Surfacing them is valuable on its own, independent of any rendering feature, and requires no changes to existing model files.

**Independent Test**: Can be fully tested by running the scan against a model file containing at least one duplicated relationship and a control model with none, and confirming the report lists exactly the duplicates and no false positives.

**Acceptance Scenarios**:

1. **Given** a model with elements A, B, C where A→B and B→C form a supported two-step chain, and an explicit relationship of the chain-implied type already exists directly between A and C, **When** the scan is run, **Then** the report includes that explicit relationship, identifies it as duplicating the derivation, and cites the two relationships that make up the implying chain.
2. **Given** a model with a chain A→B→C but no explicit relationship directly between A and C, **When** the scan is run, **Then** the report does not flag anything for the pair (A, C).
3. **Given** a model with an explicit direct relationship between A and C whose type does **not** match what the chain would imply, **When** the scan is run, **Then** the report does not flag that relationship as a duplicate.
4. **Given** a model with no relationship chains at all, **When** the scan is run, **Then** the report is empty and the scan completes without error.

---

### User Story 2 - Compute the implied relationship between two elements on demand (Priority: P1)

A modeler (or a tool building on this library, such as a view renderer) has two elements that have no explicit relationship between them, but are connected through one or more chains that imply a relationship per the derivation rule. They want to ask "what relationship is implied between these two elements, if any?" and get back the implied relationship type and the chain that produces it, without that answer being written into the model or the view file.

**Why this priority**: This is the second concrete deliverable in the issue and the foundation the render-time labeling story depends on. It must exist as a queryable capability before it can be surfaced visually.

**Independent Test**: Can be fully tested by calling the derivation query against a pair of elements known to be connected by a qualifying chain and a pair known not to be, and confirming the model file and any view file are byte-for-byte unchanged after the query.

**Acceptance Scenarios**:

1. **Given** two elements connected by a single supported two-step chain and no explicit relationship between them, **When** the derived relationship is requested for that pair, **Then** the result identifies the implied relationship type and references the chain that produced it.
2. **Given** two elements with no qualifying chain between them, **When** the derived relationship is requested, **Then** the result indicates no derivation applies.
3. **Given** two elements already connected by an explicit relationship, **When** the derived relationship is requested for that pair, **Then** the query still returns any additional chain-implied result independently of the explicit relationship (the two are reported separately, matching the read-only, non-persisting nature of this capability).
4. **Given** any successful or unsuccessful derivation query, **When** the query completes, **Then** the source model file and any view file involved are unmodified on disk.

---

### User Story 3 - Distinguish a derived relationship from a modeled one wherever it is shown (Priority: P2)

When a derived relationship is surfaced to a person — in a report, a rendered view, or any other output — it must be visually and textually distinguishable from an explicit, modeled relationship, so nobody mistakes an on-the-fly inference for something the modeler actually authored.

**Why this priority**: Builds directly on User Story 2's output; without a clear "derived" marker, users could confuse computed edges with real model content, undermining trust in the model's authored state. Lower priority than the two core computations because it is a presentation concern layered on top of them.

**Independent Test**: Can be fully tested by inspecting any output that includes a derived relationship and confirming it carries a distinct label/marker (e.g., "«derived»") that never appears on explicit relationships.

**Acceptance Scenarios**:

1. **Given** a derived relationship produced by User Story 2's capability, **When** it is included in any output consumed by a user, **Then** it is marked as derived and cannot be mistaken for an explicit relationship in that same output.
2. **Given** an explicit, modeled relationship included in the same output, **When** the output is produced, **Then** it carries no "derived" marking.

---

### Edge Cases

- What happens when the intermediate element in a chain is the same as one of the endpoints (e.g., A→B→A)? The derivation MUST NOT produce a self-referencing derived relationship from such a cycle.
- What happens when two elements are connected by more than one qualifying chain (e.g., via two different intermediate elements) and the chains imply different relationship types? Each qualifying chain is evaluated and reported independently; the feature does not attempt to reconcile or rank results across separate chains.
- What happens when a chain includes a relationship type outside the supported subset (Composition, Aggregation, Assignment, Realization, Serving, Triggering, Flow) — e.g., one leg of the chain is an Association? That chain MUST be skipped for derivation (no guess is made), consistent with the issue's explicit scope boundary.
- How does the scan behave on a model with relationships that reference elements not present in the model (dangling references)? Such relationships are excluded from chain construction and do not participate in derivation.
- What happens when the same duplicate is reachable via more than one qualifying chain? The scan reports the explicit relationship once, citing all qualifying chains that imply it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST identify, for any model, all two-step relationship chains (element A related to intermediate element B, B related to element C) where both legs use relationship types from the supported subset (Composition, Aggregation, Assignment, Realization, Serving, Triggering, Flow) and where the ArchiMate 3.2 §3.5 derivation rule yields a defined implied relationship type between A and C.
- **FR-002**: System MUST provide a scan capability that, given a model, reports every explicit relationship whose source, target, and type exactly match a relationship type implied by at least one qualifying chain found via FR-001.
- **FR-003**: Each reported duplicate MUST reference the specific chain (the two constituent relationships) that implies it, so a reviewer can locate and evaluate the underlying chain.
- **FR-004**: The scan MUST be read-only: it MUST NOT modify, remove, or annotate any relationship, element, or file as a side effect of running.
- **FR-005**: System MUST provide a query capability that, given two elements (with no requirement that a relationship already exists between them), returns the relationship type(s) implied by any qualifying chain(s) connecting them, or an explicit "no derivation" result when none exists.
- **FR-006**: The query capability in FR-005 MUST NOT write the computed result back to the source model or to any view file; results exist only for the duration of the caller's use.
- **FR-007**: Every derived relationship result exposed to a user-facing output (report, rendered view, or similar) MUST be labeled or marked in a way that distinguishes it from explicit, modeled relationships in that same output.
- **FR-008**: System MUST restrict automatic derivation to chains where both legs use one of the seven supported relationship types (Composition, Aggregation, Assignment, Realization, Serving, Triggering, Flow); chains involving Access, Influence, Specialization, or Association on either leg MUST be skipped rather than derived.
- **FR-009**: System MUST NOT produce a derived relationship from a chain whose intermediate element is also one of the chain's endpoints (i.e., no self-referencing derivations from A→B→A cycles).
- **FR-010**: When multiple qualifying chains connect the same pair of elements, System MUST evaluate and report each independently rather than merging or ranking them against each other.
- **FR-011**: System MUST exclude relationships that reference elements absent from the model from all chain construction and derivation.

### Key Entities

- **Relationship Chain**: An ordered pair of existing, explicit relationships sharing a common intermediate element (A→B, B→C), used as the input to the derivation rule.
- **Derived Relationship**: A relationship type, source, and target computed from a qualifying Relationship Chain per the ArchiMate 3.2 §3.5 rule; exists only transiently as a query/report result, never persisted.
- **Duplicate Finding**: A scan result pairing one explicit, modeled relationship with the Relationship Chain(s) that independently imply the same source/target/type.
- **Supported Relationship Type Set**: The seven relationship types (Composition, Aggregation, Assignment, Realization, Serving, Triggering, Flow) for which this feature performs automatic derivation; all other types are out of scope for automatic derivation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the scan against an existing model with known duplicated relationships identifies 100% of those duplicates with zero false positives, verified against a hand-curated test model.
- **SC-002**: Querying the derived relationship for any two elements never alters the source model file or any view file — verified by file-content comparison before and after the query across all test scenarios.
- **SC-003**: A user reviewing any output that mixes explicit and derived relationships can correctly identify which is which 100% of the time, based solely on the marking, without needing to consult the underlying model.
- **SC-004**: The scan and query capabilities correctly decline to derive a result for every chain that includes an out-of-scope relationship type (Access, Influence, Specialization, Association), verified against a test model exercising each excluded type.

## Assumptions

- The derivation rule referenced is the weakest-link combination rule defined in ArchiMate 3.2 §3.5, restricted to the seven relationship types the issue explicitly scoped in; the precise strength ordering among those types is treated as an implementation detail resolved during planning, not a business requirement to enumerate here.
- Only two-step chains (one intermediate element) are in scope for this feature; transitive derivation across three or more chained relationships is explicitly out of scope and may be considered as a future enhancement.
- The scan capability operates on a single model at a time; cross-model derivation is out of scope.
- "Render-time" in the issue title refers to any on-demand consumer of this library (a view renderer, a report generator, an interactive tool), not a specific rendering pipeline; this feature provides the underlying query capability that such consumers call, rather than mandating a specific visual output format itself.
- Existing model and view file formats, and existing validation/checker behavior, are unaffected by this feature — it adds new read-only capabilities and does not change what is considered valid or how existing files are read or written.
- **Open item**: the implemented strength ordering among the seven supported relationship types was cross-checked against two independent secondary sources during planning, not against a primary copy of the ArchiMate 3.2 specification (the Open Group's pages require authentication and could not be fetched in this environment). This is tracked as an explicit follow-up — see plan.md's Constitution Check (Principle VII) — rather than assumed settled; a reviewer with access to a licensed spec copy should confirm `src/pyArchimate/derivation.py`'s rule table before this ships to end users.
