# Research: View Auto-Layout and Auto-Format

**Phase 0 Output** | **Date**: 2026-05-03

## Overview

This document consolidates research and design decisions for the View Auto-Layout feature. All major clarifications from
the specification have been resolved; this document captures the reasoning and alternatives considered.

## 1. Layout Algorithm Selection

### Decision: Force-Directed (MVP) + Hierarchical (MVP)

Both algorithms will be implemented in MVP, with force-directed as the default for general-purpose layouts and
hierarchical for tree-like/organizational models.

**Rationale**:

- **Force-Directed**: Physics-based approach naturally minimizes overlaps, spreads elements evenly, and produces
  organic-looking layouts. Works well for general ArchiMate views with mixed relationships. Simple to implement using
  Spring-Embedder or similar physics simulation.
- **Hierarchical**: Optimal for layered structures; aligns perfectly with ArchiMate's Business→Application→Technology
  layering. Efficient O(n) algorithms exist (Sugiyama's method). Essential for organizational views.

**Alternatives Considered**:

- Grid-based layout: Too rigid for organic ArchiMate models; rejected due to poor fit for complex relationships.
- Genetic/evolutionary algorithms: Overkill for MVP; deferred to future optimization.
- Single algorithm only: Would fail to serve hierarchical use cases; force-directed alone insufficient for tree-like
  models.

**Implementation Approach**:

- Force-directed: Spring-Embedder physics simulation with adaptive iteration limits
- Hierarchical: Sugiyama's layered layout algorithm (layer assignment → crossing minimization → position assignment)

## 2. ArchiMate Layer Constraint Handling

### Decision: Mandatory for All Algorithms; Constraint Takes Priority Over Crossing Reduction

All layout algorithms (both force-directed and hierarchical) MUST enforce ArchiMate natural layering: Business
above/left of Application above/left of Technology. Layer boundaries take priority when they conflict with other
optimization objectives (e.g., crossing reduction).

**Rationale**:

- ArchiMate's layering is a semantic model property; violating it breaks diagram semantics.
- Mandatory enforcement ensures consistent, predictable output regardless of algorithm choice.
- Users expect layer-respecting layouts when working with ArchiMate models.
- Force-directed can be constrained by adding layer-based vertical/horizontal forces.

**Implementation Approach**:

- **Vertical ordering**: Assign y-coordinates constrained by layer; Business elements: y > Application elements: y >
  Technology elements: y
- **Horizontal ordering**: Assign x-coordinates constrained by layer; Business: x > Application: x > Technology: x
- **Force-directed constraint**: Add vertical (or horizontal) layer forces that override node-node repulsion when layer
  order is violated
- **Hierarchical integration**: Sugiyama layer assignment respects ArchiMate layer membership; nodes must be assigned to
  Sugiyama layers that preserve ArchiMate ordering

## 3. Connection Routing Strategy

### Decision: Orthogonal (0°, ±90°) Primary; ±45° Fallback for Excessive Crossings

All connections use orthogonal (rectilinear) routing by default. If orthogonal routing would create >10 unavoidable
crossings, the algorithm MAY use ±45° angles as a fallback.

**Rationale**:

- Orthogonal routing is standard in diagram tools (UML, ArchiMate editors); familiar to users.
- Rectilinear lines are easier to trace visually than diagonal routing.
- 45° fallback provides escape hatch for dense graphs without pure orthogonal solution.
- Crossing threshold (>10) is pragmatic; most practical diagrams achieve orthogonal without excessive crossings.

**Implementation Approach**:

- **Orthogonal algorithm**: Segment-based routing with waypoints (Manhattan distance path finding)
- **Crossing minimization**: Use barycentric method or genetic algorithm to reduce crossings after element positions are
  fixed
- **45° detection**: Count crossings after orthogonal attempt; if >10, switch to mixed 45°/90° routing
- **Label placement**: Position labels along connection segments where they don't overlap other connections or labels

## 4. Connection Label Placement

### Decision: Labels Positioned Along Connection Segments; No Overlap Allowed

Connection labels MUST NOT overlap with connection lines (including other connections' lines) or other labels. Labels
should be positioned along the connection segment, offset from the line.

**Rationale**:

- Overlapping labels obscure both the diagram and the label text; non-negotiable for readability.
- Offset positioning (label alongside connection, not on top) is standard practice.
- Label placement is a constraint satisfaction problem; solved via collision detection and adaptive repositioning.

**Implementation Approach**:

- Post-layout label placement: After connections are routed, determine label bounding boxes
- Collision detection: Check label bounds against all connection lines (polylines) and other labels
- Repositioning algorithm: Move label along connection (perpendicular offset) or to alternative position (e.g.,
  above/below connection) if collision detected
- Fallback: If no collision-free position found, truncate label or use abbreviation/abbreviation index

## 5. Element Formatting Standards

### Decision: Standardize by ArchiMate Type; Maintain User Customization

Auto-format standardizes element appearance (size, font, alignment) based on ArchiMate element type. Custom sizes and
fonts set by user are preserved if not flagged for auto-format.

**Rationale**:

- ArchiMate elements have conventional sizes (e.g., Business actors smaller than Application Services).
- Consistency improves diagram professionalism and reduces cognitive load.
- User overrides should be respected (may be intentional for emphasis).

**Implementation Approach**:

- Define size/font templates per ArchiMate element type (Business Actor, Application Component, etc.)
- Apply templates only if element size/font is "default" (not explicitly set by user)
- Preserve custom properties (color, line style, etc.) unless explicitly overridden by auto-format

## 6. Performance Strategy

### Decision: Adaptive Iteration Limits; Lazy Evaluation of Crossings

Layout algorithms use adaptive iteration limits based on element count to achieve <2s for 300 elements and <5s for 500
elements.

**Rationale**:

- Force-directed physics simulation is iterative; convergence depends on graph size.
- Fixed iteration limits risk poor layouts for small graphs (over-iteration) or incomplete layouts for large graphs (
  under-iteration).
- Lazy crossing evaluation (compute only when needed for 45° fallback decision) reduces overhead.

**Implementation Approach**:

- Estimate iteration budget: `max_iterations = 100 + element_count`; scale inversely with element density
- Monitor convergence: Stop early if node movement drops below threshold (e.g., <0.1px per iteration)
- Lazy crossing detection: Only compute crossing count if orthogonal routing produces visibly tangled layout
- Profile and tune iteration limits empirically with representative test graphs

## 7. Undo/Rollback Mechanism

### Decision: Leverage Existing View Transaction System; No New Transaction Layer

Undo/rollback uses the existing pyArchimate view transaction/history system. Layout generates a single transaction that
captures all position changes atomically.

**Rationale**:

- Avoids reimplementing transaction management; reuses battle-tested system.
- Single transaction = single undo step; users don't see individual element repositions.
- Consistent with existing pyArchimate undo/redo UX.

**Implementation Approach**:

- Capture pre-layout view state in a transaction context
- Perform layout (update element positions)
- Commit transaction; transaction system handles undo/redo

## 8. Configuration & Extensibility

### Decision: LayoutConfig Object; Extensible Algorithm Registry

Layout behavior is configurable via a LayoutConfig object (algorithm choice, spacing, margins, element exclusion,
routing style, layer enforcement). Algorithms are registered in a registry for extensibility.

**Rationale**:

- Centralized configuration improves API clarity and testability.
- Algorithm registry pattern allows future additions (grid layout, etc.) without modifying core code.
- Preserves MVP scope while allowing future customization.

**Implementation Approach**:

```python
class LayoutConfig:
    algorithm: str = "force_directed"  # or "hierarchical"
    spacing: float = 50  # pixels between elements
    margin: float = 20   # padding around canvas
    alignment: str = "grid"  # or "none"
    excluded_elements: Set[str] = set()  # element IDs to skip
    respect_layers: bool = True  # enforce ArchiMate layering
    routing_style: str = "orthogonal"  # or "mixed" (allows 45°)
    layer_priority: bool = True  # layers > crossing reduction

layout_registry = {
    "force_directed": ForceDirectedLayout,
    "hierarchical": HierarchicalLayout,
}
```

## 9. Testing Strategy

### Decision: TDD with Unit Tests, Integration Tests, BDD Scenarios

- **Unit tests**: Individual algorithms (force-directed, hierarchical, orthogonal routing, label placement)
- **Integration tests**: Round-trip fidelity (layout → export → import → verify)
- **BDD scenarios**: User-facing acceptance criteria (Given/When/Then format)

**Rationale**:

- Unit tests ensure algorithm correctness in isolation.
- Integration tests catch emergent issues (e.g., XML serialization bugs).
- BDD scenarios validate user-facing behavior and prevent regression.

**Test Coverage**:

- Edge cases: Single element, no connections, circular dependencies, mixed-layer elements
- Performance: Verify <2s for 300 elements, <5s for 500 elements
- Visual quality: Verify no overlaps, minimal crossings, readable labels

## 10. Documentation Deliverable (auto-layout-specifications.md)

### Decision: Technical Reference for Layout Rules & Algorithms

The `auto-layout-specifications.md` deliverable will be a technical reference documenting:

- Layout algorithm descriptions (force-directed, hierarchical)
- Connection routing rules (orthogonal, 45° fallback, crossing minimization)
- Label placement strategy
- ArchiMate layer constraint enforcement
- Configuration options and their effects
- Performance characteristics

**Purpose**: Serves as a design reference for implementers and a troubleshooting guide for users experiencing unexpected
layouts.

---

## Resolved Clarifications

All three clarifications from the specification have been addressed:

1. ✓ **45° angle fallback**: Allowed as last resort when orthogonal creates >10 crossings
2. ✓ **Connection label placement**: No overlaps allowed; labels positioned along segments with collision avoidance
3. ✓ **ArchiMate layer respecting**: Mandatory for all algorithms; constraints prioritized over crossing reduction

---

## 9. SVG Symbol Library Architecture

**Decision**: **Embedded SVG path definitions per element type**

**Rationale**:
- **Self-contained output**: No external font files or stylesheets; SVG is fully portable
- **Full visual fidelity**: Custom paths allow exact replication of ArchiMate symbol shapes
- **Reusability**: Define each symbol once in `<defs>`, reference via `<use>` elements throughout the diagram
- **Performance**: SVG `<use>` elements are efficient; no rendering overhead vs. rectangles

**Implementation**:
- Create `archimate_symbols.py` registry mapping element type → SVG path definition
- Store path data and viewBox dimensions for each of 30+ element types
- Support all 7 ArchiMate layers: Business, Application, Technology, Motivation, Implementation, Other, Junction

**Alternatives Considered**:
- **External icon font** (Material Design, FontAwesome): Requires font file inclusion; less accurate symbol reproduction
- **CSS+SVG hybrid** (symbol definitions in CSS): Complicates SVG output format; less portable
- **Unicode glyphs**: Limited character coverage; ArchiMate symbols not natively supported
- **Rasterized images (PNG/JPG)**: Large file size, quality issues at scale, breaks portability

**Symbol Grouping** (by layer):
- Business: Actor, Role, BusinessService, BusinessProcess, BusinessInteraction, BusinessObject, Contract, Location, Product
- Application: ApplicationComponent, ApplicationService, ApplicationInterface, ApplicationFunction, DataObject, ApplicationInteraction
- Technology: Node, Device, SystemSoftware, TechnologyService, TechnologyInterface, Path, CommunicationNetwork, Artifact, Equipment
- Motivation: Stakeholder, Driver, Assessment, Goal, Outcome, Principle, Requirement, Constraint
- Implementation: ImplementationEvent, DeliverableComponent, ImplementationComponent, Plateau
- Other: (Grouping, Location, Gap)
- Junction: AndJunction, OrJunction, XorJunction

---

## 10. ArchiMate Color Palette Strategy

**Decision**: **ArchiMate 3.x standard colors with per-element override support**

**Rationale**:
- **Standards compliance**: Use official ArchiMate 3.x specification color definitions
- **User familiarity**: Developers familiar with Archi tool will recognize colors immediately
- **Consistency**: Visual coherence across all exported diagrams
- **Flexibility**: Support per-element color overrides via `fill_color` / `line_color` properties

**Implementation**:
- Extract color palette from ArchiMate 3.x specification documents
- Create `color_palette.py` mapping:
  - Element type (e.g., "BusinessActor") → HEX color code (e.g., "#FFD700")
  - Support light/dark mode variants (future enhancement)
- Respect node property overrides: if `node.fill_color` is set, use that instead of standard

**Color Palette Structure**:
```python
ARCHIMATE_COLORS = {
    "BusinessActor": "#FFD700",           # Gold
    "BusinessRole": "#FFC700",            # Darker gold
    "BusinessProcess": "#FFE4B5",         # Moccasin
    "BusinessService": "#FFDB58",         # Light gold
    # ... etc for all 30+ types
}
```

**Alternatives Considered**:
- **Custom palette**: Optimized for web/SVG but diverges from industry standard
- **Monochrome rendering**: Loss of type differentiation; less visual appeal
- **User-defined themes**: More flexible but adds complexity; deferred to post-MVP

**Color Mapping Source**:
- ArchiMate 3.x specification (official)
- Archi tool default theme (reverse-engineered RGB values)
- Validation: Ensure colors have sufficient contrast (WCAG AA standard)

---

## 11. SVG Rendering with Symbols vs. Rectangles

**Decision**: **Replace rectangles with symbol rendering; maintain polyline clipping**

**Rationale**:
- **Visual parity with Archi**: User explicitly requested "similar to Architool" output
- **Symbol-aware clipping**: Polylines must clip at symbol boundaries, not rectangle bounds
- **Clean architecture**: Symbol definitions separated from rendering logic

**Implementation Changes**:
1. **Symbol Definition Lookup**: Given element type, retrieve SVG path and bounding box
2. **Symbol Rendering**: Instead of `<rect>`, use `<symbol>` + `<use>` structure:
   ```xml
   <defs>
     <symbol id="actor" viewBox="0 0 100 100">
       <path d="M 50 10 Q 70 30 70 50 Q 70 80 50 90 Q 30 80 30 50 Q 30 30 50 10 Z"/>
     </symbol>
   </defs>
   <use href="#actor" x="100" y="150" width="120" height="55"/>
   ```
3. **Polyline Clipping**: Use symbol's viewBox to compute intersection points (vs. rectangle geometry)
4. **Label Positioning**: Text rendered outside symbol (no change from current approach)

**Performance Impact**:
- **Symbol path parsing**: Negligible (done once per diagram)
- **Use element rendering**: Equivalent to rectangle rendering
- **Overall**: <5% performance impact; still well under 200ms for 500 elements

---

## 12. Element Name Label Placement with Symbols

**Decision**: **Separate `<text>` elements positioned relative to symbol bounds**

**Rationale**:
- **Readability**: Text outside symbol is always legible (no interference with shape)
- **Flexibility**: Accommodates variable-sized symbols
- **Matches Archi tool**: Consistent user experience

**Implementation**:
- Calculate symbol bounding box in SVG coordinates
- Position text element below/beside symbol (same as current rectangle approach)
- Adjust text wrapping width based on symbol bounds (not fixed rectangle)
- Maintain vertical centering relative to symbol height

---

## Next Steps (Phase 1)

- Update `data-model.md` with symbol registry schema (SymbolDefinition, ColorPalette)
- Update `contracts/svg-export.md` with symbol rendering specifications
- Update `quickstart.md` with symbol rendering examples
- Begin symbol library extraction and validation per Phase 6B enhancement tasks
