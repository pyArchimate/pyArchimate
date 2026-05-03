# Feature Specification: Restructure Sphinx Documentation

**Feature Branch**: `010-restructure-sphinx-docs`  
**Created**: 2026-05-03  
**Status**: Draft  
**Input**: User description: "As a maintainer of pyArchimate library, I would like to cleanup and restructure the sphinx docs to reflect the actual architecture and capabilities of the library so that the API doc is clear and structured according to a basic/intermediate and advanced usage of it"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New User Learns Basic Concepts (Priority: P1)

A user new to pyArchimate needs to understand what the library does, its core concepts, and how to get started with simple tasks. They should find clear, practical examples without being overwhelmed by advanced features or architectural details.

**Why this priority**: P1 because new user onboarding directly impacts library adoption and reduces support burden.

**Independent Test**: Can be fully tested by a new developer following the "Getting Started" section and successfully creating a simple ArchiMate model within 10 minutes, demonstrating understanding of core concepts.

**Acceptance Scenarios**:

1. **Given** a user lands on the documentation homepage, **When** they click "Getting Started", **Then** they see a clear, step-by-step introduction to basic concepts (model, elements, relationships)
2. **Given** a new user wants to create a simple model, **When** they follow the basic usage example, **Then** they can create and export a model without needing to understand internal architecture
3. **Given** documentation is read by someone unfamiliar with ArchiMate, **When** they encounter domain terminology, **Then** each term is clearly defined with context

---

### User Story 2 - Intermediate User Understands Architecture and Customization (Priority: P2)

A user with basic familiarity wants to understand the library's internal architecture, extend it with custom elements/relationships, or integrate it into their own systems. Documentation should clearly map conceptual architecture to code structure.

**Why this priority**: P2 because it enables advanced use cases and contributions while basic onboarding (P1) is critical.

**Independent Test**: Can be fully tested by a developer following the "Architecture" and "Extending pyArchimate" sections to successfully create a custom element type and use it in a model.

**Acceptance Scenarios**:

1. **Given** a developer wants to understand how the library is organized, **When** they read the "Architecture Overview" section, **Then** they see the package structure explained in terms of responsibilities (readers, writers, model, validation)
2. **Given** a developer wants to add a custom element, **When** they follow the "Extending pyArchimate" guide, **Then** they understand the minimal steps needed and where to hook into the system
3. **Given** documentation references internal components, **When** they look up a component, **Then** they find its role in the overall architecture explained clearly

---

### User Story 3 - Advanced User Accesses Implementation Details (Priority: P3)

A developer or maintainer needs detailed API references, internal design decisions, performance characteristics, or implementation patterns for deep integration, optimization, or contribution. This information should be organized separately from introductory content.

**Why this priority**: P3 because it's needed only by power users and contributors, after basic and intermediate use cases are satisfied.

**Independent Test**: Can be fully tested by a contributor reading the advanced API reference and making a meaningful code contribution to the library based on documented design patterns.

**Acceptance Scenarios**:

1. **Given** a developer needs low-level API details, **When** they navigate to the full API reference, **Then** they find complete signatures, parameters, return types, and internal relationships clearly documented
2. **Given** a developer wants to understand internal design decisions, **When** they read the "Design Decisions" or similar section, **Then** they see rationale for architectural choices (e.g., why certain patterns were used)
3. **Given** documentation is read by a contributor, **When** they review the codebase, **Then** documented patterns match actual implementation

---

## Clarifications

### Session 2026-05-03

- Q: Navigation architecture for three skill tiers → A: Single merged documentation site with clearly labeled sections (Basic/Intermediate/Advanced) with visual dividers and sidebar navigation
- Q: API documentation generation approach → A: Hybrid approach using Sphinx autodoc for auto-generated signatures from docstrings, with manual enhancement for examples and design rationale
- Q: Accessibility standards → A: WCAG 2.1 Level AA compliance required
- Q: Deep-link landing in Advanced API without context → A: Add contextual "New to this topic?" note at the top of each Advanced API page linking to the relevant Intermediate guide
- Q: Code example validation mechanism → A: Sphinx doctest directives on Getting Started and round-trip examples only; remaining examples validated by review
- Q: Visual separation of tiers (badges, boxes, color coding) → A: Sphinx admonition boxes (`.. note::`) with tier labels ("ℹ️ Basic", "🔧 Intermediate", "⚙️ Advanced") at section start
- Q: Cross-tier linking strategy (Intermediate ↔ Advanced) → A: Asymmetric linking — Intermediate guides link to Advanced API in "See Also" at end; Advanced API links back to guides in "New to this topic?" at start

---

### Edge Cases

- What happens when users search for a specific class or function and land in advanced API documentation without context? → **Resolved**: Each Advanced API page includes a "New to this topic?" note linking to the relevant guide in the Intermediate tier.
- How does the documentation handle deprecated features or legacy compatibility layers?
- How are cross-references between basic and advanced sections organized to avoid circular navigation? → **Resolved**: Asymmetric linking — Intermediate guides link to Advanced in "See Also" (end); Advanced links back to guides in "New to this topic?" (start).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Documentation MUST be organized into three clearly distinct sections within a single Sphinx project: "Basic Usage", "Intermediate / Architecture", and "Advanced / API Reference", with visual dividers (Sphinx admonition boxes with tier labels at section start: "ℹ️ Basic", "🔧 Intermediate", "⚙️ Advanced") and sidebar navigation enabling readers to move between tiers without losing context
- **FR-002**: Documentation MUST provide a "Getting Started" section with a minimal working example that runs in under 2 minutes
- **FR-003**: Documentation MUST include an "Architecture Overview" section that maps the actual package structure (readers, writers, model, validation, etc.) to their responsibilities
- **FR-004**: Documentation MUST provide "Extending pyArchimate" guide with clear examples of adding custom elements, relationships, or writers
- **FR-005**: Documentation MUST include complete API reference for all public modules and classes using a hybrid approach: auto-generated signatures from docstrings via Sphinx autodoc, enhanced with manually written usage examples, design rationale, and integration patterns; each Advanced API page MUST include a contextual "New to this topic?" note linking to the relevant Intermediate guide
- **FR-006**: Documentation MUST explain core domain concepts (ArchiMate elements, relationships, metamodel) with clear definitions and visual aids where applicable
- **FR-007**: Documentation MUST include a search or index that helps users locate both concepts and specific APIs
- **FR-008**: Documentation MUST be organized by module/capability rather than by implementation file structure
- **FR-009**: All code examples in documentation MUST be valid, tested, and reflect current API (no outdated examples)

### Key Entities *(include if feature involves data)*

- **Documentation Section**: A logical grouping of content targeting a specific user skill level (Basic, Intermediate, Advanced)
- **API Reference**: Complete documentation of public classes, functions, and modules with parameters and return types
- **Code Example**: Tested, executable code snippet demonstrating a feature or pattern
- **Concept Definition**: Explanation of domain concepts (ArchiMate terminology, library patterns, design decisions)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New users can find and run a "Getting Started" example within 2 minutes of landing on documentation
- **SC-002**: Documentation structure visibly separates basic/intermediate/advanced content with clear navigation between levels
- **SC-003**: Every public API (module, class, function) in the library has documented signature, parameters, return type, and at least one usage example
- **SC-004**: Package structure documentation matches actual source directory layout and is understandable by a developer unfamiliar with the codebase
- **SC-005**: Code examples in Getting Started and round-trip sections are validated via Sphinx doctest; remaining examples are verified against the current release by review and reflect actual API behavior
- **SC-006**: Search or table of contents allows users to locate documentation by concept (e.g., "How to add a custom element?") or by API name (e.g., "ModelWriter class")
- **SC-007**: No broken internal links or references between documentation sections
- **SC-008**: Documentation meets WCAG 2.1 Level AA accessibility compliance for keyboard navigation, color contrast, semantic HTML, and alternative text for images/diagrams

## Assumptions

- **Documentation Tool**: Sphinx is the documentation system and will remain primary (no migration to alternative systems)
- **Scope of Restructuring**: This feature focuses on documentation organization, content, and navigation—not on changing underlying Sphinx configuration, theme, or deployment infrastructure (those are separate concerns)
- **API Stability**: Current public API is stable enough to document; private/internal APIs can be marked as "not part of public API"
- **Example Coverage**: Code examples will focus on common use cases; exhaustive coverage of every edge case is out of scope (but examples should be representative)
- **Audience Assumptions**: 
  - Basic users: Python developers new to ArchiMate and architecture modeling
  - Intermediate users: Python developers wanting to extend or integrate pyArchimate
  - Advanced users: Contributors and library maintainers
- **Existing Resources**: Current Sphinx build system, theme, and deployment process will be preserved; only content structure and organization change
- **Testing Approach**: Code examples will be validated via existing test suite where applicable; new dedicated tests for documentation examples are out of scope for this feature
- **Docstring Standards**: Existing public module and class docstrings follow a consistent format (e.g., Google, NumPy, or Sphinx style) suitable for autodoc extraction; if gaps exist, they will be filled during implementation
- **Accessibility Infrastructure**: The Sphinx theme and configured extensions will provide baseline WCAG 2.1 Level AA support; custom styling or JavaScript enhancements will comply with these standards
- **Navigation UI**: Sphinx theme or custom CSS can support visual tier indicators (badges, color coding, sidebar labels) without requiring custom JavaScript or external templating systems
