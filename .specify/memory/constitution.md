<!--
  Sync Impact Report:
  - Version change: v1.1.0 -> v1.1.1
  - List of modified principles:
    - VII. System Integrity & Accuracy (Clarified focus)
    - VIII. Durability & Interoperability (Clarified focus)
    - IX. Cross-Platform Consistency (Clarified wording)
  - Added sections:
    - VII. System Integrity & Accuracy (Faithful Outcomes)
    - VIII. Durability & Interoperability (Preserving Continuity)
    - IX. Cross-Platform Consistency (Universal Accessibility)
  - Removed sections: None
  - Templates requiring updates:
    - .specify/templates/plan-template.md (updated)
    - .specify/templates/spec-template.md (updated)
    - .specify/templates/tasks-template.md (updated)
  - Follow-up TODOs: None
-->

# SpecKit Constitution

## Detailed References (Deeper Detail)

This document is complemented by several other key files. Consult the following living documents when you need deeper implementation or operational detail:

* **`specs/TECHNICAL.md`**: This file provides Implementation-level guidance, coding standards, process expectations, detailed guidelines, best practices, and preferred standards that dictate how all requirements (functional and non-functional) should be implemented.
* **`specs/NONFUNCTIONALS.md`**: This file contains the abstracted, high-level non-functional solution specific requirements, quality attribute requirements such as performance, reliability, security, and compliance, derived from the feature specification and other sources. These define what the system must achieve in terms of quality attributes.
* **`specs/PROJECT_CONSTITUTION.md`**: This document outlines additional principles specific to the project's domain, complementing the core SpecKit guidelines.
* **`specs/PROJECT_SPECIFICATION.md`**: This document outlines the business requirements of the solution. Business and domain requirements derived from user needs. View it as a historical reference that should be used as input when deriving user stories, requirements, and acceptance criteria for new specs.

Mark those files as for deeper detail and link back here whenever you need quick orientation.

## Core Principles

### I. Code Quality (Excellence through Clarity)

Logic must be self-documenting, modular, and adhere to SOLID principles. We prioritize readability over cleverness. Every function must have a clear purpose and minimal side effects.

- **Rules**: No "magic numbers," use descriptive naming, keep functions under 30 lines where possible. For detailed guidance on code structure and naming, refer to `specs/TECHNICAL.md`'s "Code Style" and "File Structure" sections.
- **Rationale**: Maintainability is the primary constraint for long-term project health. We adhere to the **DRY (Don't Repeat Yourself)** principle to minimize redundancy and improve consistency.

### II. Testing Standards (Verified Correctness)

Automated tests are non-negotiable. Every feature must include unit and integration tests. Test coverage MUST prioritize critical paths and edge cases. We follow the Red-Green-Refactor cycle, embracing **Test-Driven Development (TDD)** principles.

* **Rules**:
  * 100% coverage on core business logic; tests must be isolated and reproducible.
  * Implementation should begin by writing tests first, checking the tests fail, stubbing out the code, confirming the tests pass, and then beginning implementation.
  * For detailed testing practices and framework choices, see `specs/TECHNICAL.md`'s "Patterns and Practices > Testing" section.
* **Rationale**: Tests provide the confidence to refactor and ensure regressions are caught early.

### III. User Experience Consistency (Unified Interface)

Interfaces MUST follow established patterns to ensure predictability. Whether CLI or GUI, the user's mental model MUST be respected. Error messages must be actionable and clear.

- **Rules**: Use consistent command structures for CLI; provide helpful error messages with resolution steps. For comprehensive guidance on API design principles that ensure consistency, refer to `specs/TECHNICAL.md`.
- **Rationale**: Consistency reduces cognitive load and improves user trust and efficiency.

### IV. Performance Requirements (Efficiency by Design)

System responsiveness is a first-class citizen. Code must be optimized for resource efficiency. Any operation exceeding 200ms must be asynchronous or justified.

- **Rules**: Profile critical paths; avoid premature optimization but maintain O(n) awareness. Performance considerations are further detailed in `specs/TECHNICAL.md`'s "Performance" section.
- **Rationale**: Performance is a feature; a slow system is a broken system for the user.

### V. Security Practices (Proactive Defense)

Security is paramount throughout the development lifecycle. We adhere to secure coding practices, referencing established guidelines such as **OWASP**, **CWE**, **CERT Secure Coding Standards**, etc.

- **Rules**: Never commit sensitive information; validate all user inputs; use environment variables for configuration. Detailed security guidelines are available in `specs/TECHNICAL.md`'s "Security" section.
- **Rationale**: Protecting data and systems from threats is a fundamental responsibility.

### VI. State Management and Workflow Integrity (Predictable Evolution)

Logic must define clear lifecycles and state transitions for key entities to ensure predictable evolution and auditable workflows. Data integrity must be maintained through controlled state changes, preventing invalid transitions.

- **Rules**: Document entity lifecycles and state transition rules. Implement these rules rigorously. Refer to `specs/TECHNICAL.md` for detailed patterns on implementing state management and workflow control.
- **Rationale**: Robust state management and enforced workflows enhance system predictability, reliability, audibility, and maintainability, crucial for governance and complex processes.

### VII. System Integrity & Accuracy (Faithful Outcomes)

Every outward behavior, calculation, and state transition must be accurate and reproducible. Silent deviations erode trust and obscure maintenance risks, so we treat integrity as a first-class requirement.

- **Rules**: Definitions, constraints, derived data, and published results must pass validation checks before release. Any change that affects state or outputs must be traceable through logging or metadata that explains why it occurred.
- **Rationale**: Confidence in the platform stems from predictable, trustworthy outcomes. Inaccuracies amplify over time and create cascading fixes.

### VIII. Durability & Interoperability (Preserving Continuity)

Project artifacts, data, and integrations must survive upgrades and align with other systems without degrading intent or context. Durability ensures teams can evolve the product without losing institutional knowledge.

- **Rules**: Introducing new formats or integrations requires defined migration/mapping paths for existing data and behaviors. Export/import routines must preserve semantics, metadata, and links across environments. Automated checks should detect semantic drift after upgrades.
- **Rationale**: Losing context or breaking interoperability forces costly rewrites and undermines the value of historical decisions.

### IX. Cross-Platform Consistency (Universal Accessibility)

The product must deliver reliable, equivalent functionality across the platforms we support. Differences in environments (hardware, OS, display, accessibility) should not manifest as inconsistent behavior or data fidelity gaps.

- **Rules**: UI components, rendering paths, and performance expectations should be verified across platforms. Platform-specific integrations must degrade gracefully and protect data integrity.
- **Rationale**: Consistent behavior keeps users productive and minimizes confusion when switching devices or sharing outputs. Refer to `specs/PROJECT_CONSTITUTION.md` for any domain-specific addenda.

## Development Workflow

Our workflow is designed to ensure that every change is intentional and verified. It follows a sequence of:

1. **Specify**: Define requirements and user stories in a feature spec.
2. **Plan**: Research technical approaches, map out tasks, and generate design artifacts.
3. **Implement**: Execute tasks following the Red-Green-Refactor cycle.
4. **Verify**: Pass all quality gates before merging.
    For more on our patterns and practices, see `specs/TECHNICAL.md`.

## Quality Gates

Before any feature is considered "Done," it must pass these gates:

* **Linting & Formatting**: Must pass all project-standard style checks, as detailed in `specs/TECHNICAL.md`.
* **Test Suite Pass**: All new and existing tests must pass without failure after the implementation of every user story, adhering to the standards in `specs/TECHNICAL.md`.
* **Documentation**: READMEs, specs, and inline comments must be updated.
* **Constitution Check**: Implementation must be reviewed against these core principles.

## Governance

This constitution is the supreme guide for SpecKit development.

- **Amendments**: Proposed via PR; requires explanation of why the change improves project governance.
- **Versioning**: Follows semantic versioning.
- **Compliance**: All contributors must adhere to these principles; deviations must be justified in the `plan.md` complexity tracking section.

**Version**: 1.1.1 | **Ratified**: 2026-02-18 | **Last Amended**: 2026-04-01
