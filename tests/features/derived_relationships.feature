# Traceability (spec: specs/015-derived-relationships/spec.md, GitHub issue #140)
#   US1 acceptance scenario 1 -> FR-002, FR-003 -> Scenario: Explicit duplicate of an implied chain is reported
#   US1 acceptance scenario 2 -> FR-002           -> Scenario: Chain with no matching explicit relationship is not flagged
#   US1 acceptance scenario 3 -> FR-002           -> Scenario: Explicit relationship of a different type is not flagged
#   US1 acceptance scenario 4 -> FR-002, FR-004   -> Scenario: Model with no relationship chains yields an empty report
#   US2 acceptance scenario 1 -> FR-005           -> Scenario: Single qualifying chain yields the implied relationship
#   US2 acceptance scenario 2 -> FR-005           -> Scenario: No qualifying chain yields no derivation
#   US2 acceptance scenario 3 -> FR-005, FR-006   -> Scenario: Existing explicit relationship does not suppress the chain-implied result
#   US2 acceptance scenario 4 -> FR-006, SC-002   -> Scenario: Derivation query never modifies the model or view file on disk
#   US3 acceptance scenario 1 -> FR-007           -> Scenario: A derived relationship is marked as derived
#   US3 acceptance scenario 2 -> FR-007           -> Scenario: An explicit relationship carries no derived marking
#   Edge case (self-referencing cycle)            -> FR-009 -> Scenario: A self-referencing chain does not produce a derived relationship
#   Edge case (two chains, different types)       -> FR-010 -> Scenario: Two qualifying chains implying different types are each reported independently
#   Edge case (out-of-scope leg type)             -> FR-008 -> Scenario: A chain with an out-of-scope relationship type is skipped
#   Edge case (dangling reference)                -> FR-011 -> Scenario: Relationships referencing missing elements are excluded from derivation
#   Edge case (duplicate reachable via >1 chain)   -> FR-003, FR-010 -> Scenario: A duplicate reachable via more than one chain is reported once citing all chains

Feature: Derived Relationships (Scan & Render-Time Computation)
  As a modeler (or a tool built on this library, such as a view renderer)
  I want to find explicit relationships that duplicate an implied chain, and query the relationship implied between two elements on demand
  So that duplicated relationships can be reviewed instead of drifting silently, and consumers can discover implied relationships without persisting them into the model

  Background:
    Given I have a fresh pyArchimate model for derivation testing

  # --- User Story 1 (P1): Find redundant explicit relationships that duplicate an implied chain ---

  @US1 @FR-002 @FR-003
  Scenario: Explicit duplicate of an implied chain is reported
    Given elements A, B, C where A relates to B and B relates to C forming a supported two-step chain
    And an explicit relationship of the chain-implied type already exists directly between A and C
    When the scan is run
    Then the report includes that explicit relationship
    And it is identified as duplicating the derivation
    And the report cites the two relationships that make up the implying chain

  @US1 @FR-002
  Scenario: Chain with no matching explicit relationship is not flagged
    Given elements A, B, C where A relates to B and B relates to C forming a supported two-step chain
    And no explicit relationship exists directly between A and C
    When the scan is run
    Then the report does not flag anything for the pair (A, C)

  @US1 @FR-002
  Scenario: Explicit relationship of a different type is not flagged
    Given elements A, B, C where A relates to B and B relates to C forming a supported two-step chain
    And an explicit direct relationship between A and C whose type does not match what the chain would imply
    When the scan is run
    Then the report does not flag that relationship as a duplicate

  @US1 @FR-002 @FR-004
  Scenario: Model with no relationship chains yields an empty report
    Given a model with no relationship chains at all
    When the scan is run
    Then the report is empty
    And the scan completes without error

  # --- User Story 2 (P1): Compute the implied relationship between two elements on demand ---

  @US2 @FR-005
  Scenario: Single qualifying chain yields the implied relationship
    Given two elements connected by a single supported two-step chain and no explicit relationship between them
    When the derived relationship is requested for that pair
    Then the result identifies the implied relationship type
    And the result references the chain that produced it

  @US2 @FR-005
  Scenario: No qualifying chain yields no derivation
    Given two elements with no qualifying chain between them
    When the derived relationship is requested for that pair
    Then the result indicates no derivation applies

  @US2 @FR-005 @FR-006
  Scenario: Existing explicit relationship does not suppress the chain-implied result
    Given two elements already connected by an explicit relationship
    And those same two elements are also connected by a qualifying chain
    When the derived relationship is requested for that pair
    Then the query still returns the additional chain-implied result independently of the explicit relationship

  @US2 @FR-006 @SC-002
  Scenario: Derivation query never modifies the model or view file on disk
    Given a model file and a view file saved to disk
    When the scan is run
    And the derived relationship is requested for two elements in that model
    Then the source model file and any view file involved are unmodified on disk

  # --- User Story 3 (P2): Distinguish a derived relationship from a modeled one wherever it is shown ---

  @US3 @FR-007
  Scenario: A derived relationship is marked as derived
    Given a derived relationship produced by the on-demand query
    When it is included in an output consumed by a user
    Then it is marked as derived
    And it cannot be mistaken for an explicit relationship in that same output

  @US3 @FR-007
  Scenario: An explicit relationship carries no derived marking
    Given an explicit, modeled relationship
    When it is included in the same output
    Then it carries no "derived" marking

  # --- Edge Cases ---

  @edge @FR-009
  Scenario: A self-referencing chain does not produce a derived relationship
    Given elements A and B where A relates to B and B relates back to A
    When the scan is run
    Then the derivation does not produce a self-referencing derived relationship from that cycle

  @edge @FR-010
  Scenario: Two qualifying chains implying different types are each reported independently
    Given two elements connected via two different intermediate elements whose chains imply different relationship types
    When the derived relationship is requested for that pair
    Then each qualifying chain is evaluated and reported independently
    And the results are not reconciled or ranked against each other

  @edge @FR-008
  Scenario: A chain with an out-of-scope relationship type is skipped
    Given a chain where one leg uses a relationship type outside the supported subset
    When the derived relationship is requested for that pair
    Then that chain is skipped for derivation and no result is produced for it

  @edge @FR-011
  Scenario: Relationships referencing missing elements are excluded from derivation
    Given a chain whose relationship references an element no longer present in the model
    When the scan is run
    Then that relationship is excluded from chain construction and does not participate in derivation

  @edge @FR-003 @FR-010
  Scenario: A duplicate reachable via more than one chain is reported once citing all chains
    Given an explicit relationship between A and C that is reachable via more than one qualifying chain
    When the scan is run
    Then the report includes the explicit relationship exactly once
    And it cites all qualifying chains that imply it
