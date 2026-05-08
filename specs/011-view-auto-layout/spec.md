# Feature Specification: View Auto-Layout and Auto-Format

**Feature Branch**: `011-view-auto-layout`  
**Created**: 2026-05-03  
**Status**: Draft  
**Input**: User description: "As a developer using the pyArchimate library, I want to have a new functionality in order to auto-format and auto-layout a view. before clarifying and making plans and tasks, I want to write a auto-layout-specifications.md documents containing the rules to apply when autoformatting"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Auto-Layout Messy Diagram (Priority: P1)

A developer has imported or manually created an ArchiMate view where elements are overlapping, scattered randomly, or poorly positioned. They want to automatically reorganize all elements into a clean, legible layout without manually dragging each element.

**Why this priority**: Core functionality—addressing the most common pain point of manual positioning. Delivers immediate value for any view with poor initial layout.

**Independent Test**: Can be fully tested by loading a view with overlapping/scattered elements, invoking auto-layout, and verifying that all elements are visible, non-overlapping, and logically positioned.

**Acceptance Scenarios**:

1. **Given** a view with overlapping elements, **When** auto-layout is applied, **Then** all elements are repositioned with no overlaps and adequate spacing
2. **Given** a view with elements scattered across the canvas, **When** auto-layout is applied, **Then** elements are organized into a coherent spatial structure (e.g., by hierarchy or relationship)
3. **Given** a view with elements at arbitrary positions, **When** auto-layout is applied, **Then** element relationships (connections) are respected and remain intact

---

### User Story 2 - Format Elements and Connections (Priority: P1)

A developer wants to standardize the visual appearance of elements and connections in a view—ensuring consistent sizing, alignment, font styles, and connection routing—without manually adjusting each element or connector.

**Why this priority**: Formatting directly impacts readability and professionalism. Automating this prevents visual inconsistencies and saves time.

**Independent Test**: Can be fully tested by applying auto-format to a view and verifying that all elements meet formatting standards (uniform sizing, aligned text) and connections are routed cleanly.

**Acceptance Scenarios**:

1. **Given** a view with elements of varying sizes, **When** auto-format is applied, **Then** elements are resized to standard dimensions based on their type
2. **Given** a view with inconsistent element alignment, **When** auto-format is applied, **Then** elements are aligned on a grid or according to layout rules
3. **Given** a view with overlapping or tangled connections, **When** auto-format is applied, **Then** connections are re-routed to minimize crossings and improve clarity

---

### User Story 3 - Apply Hierarchical Layout (Priority: P2)

A developer wants to organize elements in a view by their hierarchical relationships—grouping child elements near their parents, creating a top-down or layered visual structure that reflects the model's logical organization.

**Why this priority**: Hierarchical layout is valuable for large or complex diagrams where relationship structure directly improves understanding. Useful for models with clear parent-child relationships.

**Independent Test**: Can be fully tested by applying hierarchical layout to a view with layered relationships and verifying that child elements are positioned near parents in layers or grouped regions.

**Acceptance Scenarios**:

1. **Given** a view with parent and child elements, **When** hierarchical layout is applied, **Then** child elements are positioned in proximity to their parents
2. **Given** a view with multiple levels of relationships, **When** hierarchical layout is applied, **Then** elements are organized in layers or levels reflecting the hierarchy
3. **Given** a view with cross-relationships, **When** hierarchical layout is applied, **Then** connections between layers are visible and not obscured
4. **Given** a view with mixed ArchiMate layers (Business, Application, Technology), **When** hierarchical layout is applied, **Then** elements are positioned respecting layer boundaries (Business above/left of Application, Application above/left of Technology)

---

### User Story 4 - Customize Layout Behavior (Priority: P2)

A developer wants to configure or fine-tune auto-layout behavior—choosing different layout algorithms, adjusting spacing and margins, or excluding specific elements from auto-layout—to meet domain-specific or aesthetic preferences.

**Why this priority**: Customization enables the feature to adapt to various use cases and user preferences, increasing adoption. Out of scope for MVP but important for real-world usability.

**Independent Test**: Can be fully tested by configuring custom layout options and verifying that the layout respects the specified parameters (e.g., increased spacing, element exclusion).

**Acceptance Scenarios**:

1. **Given** a developer specifies a custom spacing value, **When** auto-layout is applied, **Then** spacing between elements matches the configured value
2. **Given** a developer excludes specific elements from layout, **When** auto-layout is applied, **Then** excluded elements retain their current position

---

### Edge Cases

- What happens when a view contains elements with no connections or relationships? (Elements should still be positioned in a coherent grid or pattern)
- How does auto-layout handle elements that are locked or marked as fixed? (Should respect locks and not reposition fixed elements)
- What happens if a view contains only a single element? (Element should remain visible; no repositioning necessary)
- How does the system handle views with circular dependencies or cyclical relationships? (Layout should still produce a readable result, possibly breaking cycles visually)
- What if elements have very different sizes? (Layout should accommodate size variations and maintain readable spacing)
- What happens when connection labels cannot fit without overlapping? (Labels should be repositioned or truncated gracefully; at minimum, label placement should not violate readability of connection lines)

## Clarifications

### Session 2026-05-03

- Q: Should ±45° angles be allowed as fallback when orthogonal routing creates excessive crossings? → A: Yes, allow 45° as fallback only when orthogonal routing would create excessive crossings (e.g., >10 crossings); this is not recommended but necessary in dense diagrams
- Q: Should connection labels be prevented from overlapping with other connections and labels? → A: Yes, connection labels MUST NOT overlap with other connection lines or other connection labels; labels should be positioned to maximize readability
- Q: Should ArchiMate layer respecting be mandatory for all layout algorithms? → A: Yes, mandatory for all algorithms (force-directed and hierarchical); Business layer above/left of Application layer, which is above/left of Technology layer; layer constraints take priority over other optimization objectives

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an auto-layout function that takes a view as input and repositions all elements to maximize readability and minimize overlaps
- **FR-002**: System MUST preserve all element properties (name, documentation, type) during auto-layout—only position and size are affected
- **FR-003**: System MUST preserve all connections and relationships during auto-layout—connections remain valid and linked to correct endpoints
- **FR-004**: System MUST provide auto-format capability that standardizes element appearance (size, font, alignment) according to ArchiMate conventions
- **FR-005**: System MUST ensure no elements overlap after auto-layout is applied (except where intentional grouping is used)
- **FR-006**: System MUST support both force-directed (physics-based) and hierarchical/layered layout algorithms, with force-directed as the default for general-purpose layouts and hierarchical for tree-like structures
- **FR-007**: System MUST implement connection routing that: (1) prevents connections from overlapping with each other or passing through elements, (2) uses orthogonal (0°, ±90°) routing by default with ±45° only as fallback for excessive crossings, (3) minimizes total connection crossings, and (4) equally distributes connection endpoints across node edges
- **FR-008**: System MUST provide advanced configuration options including: spacing, margin, alignment, element exclusion, algorithm selection, node size constraints, and connection routing style preferences
- **FR-011**: System MUST respect ArchiMate natural layering in all layout algorithms; elements must be organized according to their layer (Business, Application/Element, Technology) with Business layer positioned above or to the left of Application layer, which is above or to the left of Technology layer
- **FR-009**: System MUST validate that auto-layout completes within a reasonable timeframe for views with up to 500 elements
- **FR-010**: System MUST include undo/rollback capability so users can revert auto-layout if unsatisfied with results

### Key Entities

- **View**: Container holding elements and connections; target of auto-layout operation
- **Element**: Individual ArchiMate element (e.g., Application Component, Business Actor) with position, size, and visual properties
- **Connection**: Relationship or flow between elements, with orthogonal routing constraints (0°, ±90° primary; ±45° fallback), no overlaps with other connections, and equally-distributed endpoints on node edges
- **Layout Algorithm**: Algorithm determining element positioning (force-directed, hierarchical, grid-based, etc.)
- **Layout Configuration**: Parameters controlling layout behavior (spacing, margins, alignment rules, element exclusions)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Auto-layout completes in under 2 seconds for views with up to 300 elements
- **SC-002**: 100% of elements in the view are visible and non-overlapping after auto-layout (except where intentional grouping is applied)
- **SC-003**: 95% of user-applied layouts are visually acceptable on first try (subjective, measured via user feedback)
- **SC-004**: Auto-format reduces element size variance by 80% (measured by standard deviation of element dimensions)
- **SC-005**: Connection routing reduces average crossing count by at least 60% compared to manual or random layouts
- **SC-006**: Undo/rollback successfully restores the view to its previous state in 100% of test cases
- **SC-007**: Users report reduced time spent on manual positioning—baseline and target TBD based on user feedback
- **SC-008**: 100% of layouts respect ArchiMate layer boundaries; all Business layer elements are positioned above/left of Application layer, and Application layer elements are positioned above/left of Technology layer (verified by spatial position comparison)

## Connection Routing Rules *(mandatory)*

All connections between elements MUST adhere to the following routing constraints:

- **No overlaps**: Connections cannot overlap with each other or pass through other elements
- **Orthogonal primary**: Connections MUST use orthogonal (rectilinear) routing at 0°, ±90° angles as the default
- **45° fallback**: If orthogonal routing would create excessive crossings (e.g., >10 unavoidable crossings), the algorithm MAY use ±45° angles as a fallback, though this is not recommended and should be minimized
- **Minimum crossings**: The routing algorithm MUST minimize the total number of connection crossings; unavoidable crossings are acceptable but must be justified by layout quality constraints
- **Endpoint spreading**: Connection starting and ending points MUST be equally distributed across the edges of their respective nodes to avoid visual clustering and improve clarity
- **Label placement**: Connection labels MUST NOT overlap with other connection lines or other connection labels; labels should be positioned to maximize readability without obscuring the diagram

## ArchiMate Layer Constraints *(mandatory)*

All layout algorithms MUST respect the natural layering structure of ArchiMate:

- **Vertical layer ordering** (primary): Business layer elements MUST be positioned above Application/Element layer elements, which MUST be positioned above Technology layer elements
- **Horizontal layer ordering** (alternative): Business layer elements MUST be positioned to the left of Application/Element layer elements, which MUST be positioned to the left of Technology layer elements
- **Mixed-layer elements**: Elements that span multiple layers or have ambiguous layer assignments should be positioned in a zone that best represents their primary layer affiliation
- **Cross-layer relationships**: Connections between layers are expected and acceptable; layer positioning should not be violated to avoid cross-layer connections
- **Algorithm compliance**: Both force-directed and hierarchical layout algorithms MUST enforce layer boundaries; layer constraints take priority over other optimization objectives (e.g., crossing reduction) when conflicts occur

## Assumptions

- **Layout scope**: Auto-layout applies to elements and connections visible in the current view; relationships outside the view are not modified
- **Element types**: All ArchiMate element types are supported; layout algorithms apply uniformly across types
- **Connection model**: Connections are rendered as polylines with orthogonal (rectilinear) routing as primary strategy; see Connection Routing Rules section for detailed constraints
- **Undo/rollback**: Built on existing view transaction/history system; changes can be undone via standard undo mechanism
- **Performance target**: Layout algorithms must scale to at least 500 elements without hanging or timeout
- **User expertise**: Feature is used by developers familiar with ArchiMate; no requirement for novice-friendly wizards
- **Initial implementation**: MVP focuses on at least one stable layout algorithm (force-directed or hierarchical); additional algorithms in future releases
- **Exclusions**: Auto-layout does not modify element documentation, relationships to elements outside the view, or model integrity; it only adjusts visualization

## Deliverables

- **auto-layout-specifications.md**: Detailed technical specification of layout algorithms, rules, parameters, and behaviors
- **Feature implementation**: Auto-layout and auto-format functions integrated into the pyArchimate view API
- **Test suite**: Unit and integration tests validating layout correctness, performance, and edge cases
- **User documentation**: Guide for using auto-layout and auto-format with examples