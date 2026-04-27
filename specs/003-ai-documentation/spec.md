# Feature Specification: AI-Optimized Documentation

**Feature Branch**: `003-ai-documentation`  
**Created**: 2026-04-27  
**Status**: Draft  
**Input**: User description: "Create a baseline specification based on GitHub issue #27. The goal is to capture and integrate AI-generated documentation into the repository. Create a dedicated structured markdown file that covers the library's core purpose, architecture, and limitations. Ensure the documentation is optimized for AI consumption, linked from the README, and free of conversational artifacts. Develop a script to automate the generation of this documentation using AI tools, ensuring it can be easily updated as the library evolves. Include a tutorial for new users on how to utilize the library effectively, with examples and best practices."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Consumption of Library Context (Priority: P1)

An AI assistant (such as an LLM-based coding tool) queries the repository for context about pyArchimate. Instead of piecing together information from scattered files, it finds a single structured `AI.md` file that densely and precisely describes the library's purpose, object model, supported formats, and limitations — free of conversational filler.

**Why this priority**: This is the primary goal of the feature. Without a machine-readable reference document, AI tools produce lower-quality assistance when users ask about pyArchimate. This delivers immediate value to every AI-assisted contributor and user.

**Independent Test**: Can be fully tested by loading `AI.md` into an AI assistant and verifying it can accurately answer questions about the library's capabilities, object model, and limitations without needing to read source code.

**Acceptance Scenarios**:

1. **Given** the `AI.md` file exists in the repository root, **When** its contents are provided as context to an AI assistant, **Then** the assistant accurately describes the library's core concepts, supported formats, and key operations without hallucinating unsupported features.
2. **Given** `AI.md` exists, **When** a developer checks it into version control, **Then** it renders correctly as structured markdown with no rendering artefacts.
3. **Given** `AI.md` exists, **When** reviewed for conversational language, **Then** it contains no phrases such as "of course", "sure", "feel free to", or first-person narrative.

---

### User Story 2 - New User Tutorial (Priority: P2)

A developer new to pyArchimate opens the repository wanting to understand how to load, inspect, modify, and save an ArchiMate model. They follow a step-by-step tutorial with runnable code examples and arrive at working scripts within 30 minutes.

**Why this priority**: Onboarding friction is a major adoption barrier for library projects. A self-contained tutorial directly reduces time-to-first-success for new users.

**Independent Test**: Can be fully tested by following the tutorial from scratch on a clean Python environment and verifying every code snippet executes without errors and produces the documented output.

**Acceptance Scenarios**:

1. **Given** a user with no prior exposure to pyArchimate, **When** they follow the tutorial sequentially, **Then** they can read, inspect, modify, and save a model using only the tutorial's instructions.
2. **Given** the tutorial's code examples, **When** copied verbatim into a Python script and executed against the referenced test fixtures, **Then** all examples run without errors.
3. **Given** the tutorial, **When** reviewed for completeness, **Then** it covers at minimum: loading a file, listing elements, creating an element, adding a relationship, creating a view, and saving to a supported format.

---

### User Story 3 - Automated Documentation Regeneration (Priority: P3)

A maintainer runs a script that regenerates `AI.md` (and potentially the tutorial) by extracting current library information and passing it through an AI-assisted generation step. The script is idempotent and can be run as part of the release process.

**Why this priority**: Documentation drifts from code over time. An automated regeneration script ensures the documentation stays accurate as the library evolves, with minimal manual effort.

**Independent Test**: Can be fully tested by running the script against the current codebase and verifying the output file is updated, well-formed, and reflects the current public API surface.

**Acceptance Scenarios**:

1. **Given** the generation script exists, **When** run on the repository, **Then** it produces or updates `AI.md` within 5 minutes with no manual editing required.
2. **Given** a change to the library's public API, **When** the generation script is re-run, **Then** the updated `AI.md` reflects the change.
3. **Given** the script is run twice without any library changes, **Then** the resulting `AI.md` is identical on both runs (idempotent output structure).

---

### User Story 4 - README Discoverability (Priority: P4)

A user browsing the repository's `README.md` finds a clearly marked link to `AI.md` and the tutorial, allowing them to navigate directly to the appropriate depth of documentation for their needs.

**Why this priority**: Documentation that is not discoverable is not used. Linking from the README ensures visibility without restructuring the primary document.

**Independent Test**: Can be fully tested by opening the README, confirming the links to `AI.md` and the tutorial file exist and resolve correctly.

**Acceptance Scenarios**:

1. **Given** the README exists, **When** rendered on GitHub, **Then** it contains a working hyperlink to `AI.md` and to the tutorial document.
2. **Given** the link to `AI.md` in the README, **When** clicked, **Then** it navigates directly to the structured documentation file.

---

### Edge Cases

- What happens when the generation script is run on a repository with uncommitted changes to the public API — does it reflect staged or committed state?
- How does the tutorial behave if the user has an older version of the library installed that lacks a referenced feature?
- What happens when `AI.md` is regenerated and the diff is large — is there a review step or is it fully automated?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST contain a file `AI.md` at the root level that describes the library's core purpose, object model, supported formats, key operations, and known limitations.
- **FR-002**: `AI.md` MUST be written in structured markdown with no conversational language, filler phrases, or first-person narrative.
- **FR-003**: `AI.md` MUST be optimized for consumption by AI language models: dense, precise, consistently structured, and free of ambiguity.
- **FR-004**: `README.md` MUST include a link to `AI.md` and to the new user tutorial.
- **FR-005**: The repository MUST contain a new user tutorial document that covers loading, inspecting, modifying, and saving an ArchiMate model with complete, runnable code examples.
- **FR-006**: The tutorial MUST include best-practice guidance alongside the code examples (e.g., recommended patterns, common mistakes to avoid).
- **FR-007**: A generation script MUST exist that can produce or update `AI.md` using AI-assisted tooling, requiring only a single command invocation.
- **FR-008**: The generation script MUST be documented with instructions for maintainers on when and how to run it.
- **FR-009**: `AI.md` MUST be version-controlled alongside the source code so it is always available without running any tooling.
- **FR-010**: The generation script MUST NOT require credentials or API keys to be hard-coded; it MUST read them from environment variables or a standard configuration location.

### Key Entities

- **AI.md**: The primary machine-readable documentation file — structured reference covering purpose, object model, formats, operations, and limitations.
- **Tutorial document**: Step-by-step guide for new users with runnable examples and best-practice notes.
- **Generation script**: Executable script (shell or Python) that automates the creation/update of `AI.md`.
- **README.md**: Existing entry-point document, updated with navigation links to new artefacts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user with Python experience but no ArchiMate or pyArchimate knowledge can complete the tutorial and produce a working model file in under 30 minutes.
- **SC-002**: When `AI.md` is provided as context to an AI assistant, the assistant answers correctly on 90% or more of common questions about the library's capabilities and limitations (validated by a manual spot-check of 10 representative questions).
- **SC-003**: The generation script completes successfully in under 5 minutes on a standard developer workstation.
- **SC-004**: `AI.md` remains accurate (no stale information identified by manual review) for at least 3 months after a library release, measured by the absence of reported inaccuracies.
- **SC-005**: All code examples in the tutorial execute without errors against the current stable release of the library.
- **SC-006**: The README link to `AI.md` and the tutorial resolves correctly on the default branch on GitHub.

## Assumptions

- The `AI.md` file will initially be authored manually (or with AI assistance during this feature), with the generation script used for future updates rather than the initial creation.
- The tutorial will target Python developers who are familiar with the language but new to ArchiMate and the library; no prior ArchiMate knowledge is assumed.
- The generation script will use an external AI API (such as the Anthropic or OpenAI API) that the maintainer has access to; cost and rate limits are the maintainer's responsibility.
- The tutorial document will live under the `docs/` directory or as a standalone `TUTORIAL.md` at the repository root — the exact location is to be confirmed during planning.
- Existing Sphinx/ReadTheDocs documentation is out of scope for this feature; `AI.md` and the tutorial are supplementary, not replacements.
- The generation script is a developer/maintainer tool and does not need to run in CI by default, though it may be wired into an optional workflow in a follow-up.
- Mobile or web-based viewing of documentation is not a concern — GitHub markdown rendering is the primary target.
