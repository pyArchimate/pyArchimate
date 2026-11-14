# Traceability (spec: specs/016-derivation-n-hop/spec.md, GitHub issue #173)
#   US1 acceptance scenario 1/3 -> FR-005          -> Scenario: Duplicate implied by a three-step chain is reported when opted in
#   US2 acceptance scenario 1   -> FR-006          -> Scenario: Querying two elements connected only by a three-step chain returns the implied relationship
#   US3 acceptance scenario 2   -> FR-010, FR-011  -> Scenario: Exceeding the default chain-length ceiling requires an explicit override

Feature: N-Hop Derivation (chains of any length, not just two steps)
  As a modeler (or a tool built on this library)
  I want the duplicate scan and on-demand derivation query to fold relationship chains of any length, not just exactly two steps
  So that longer-chain duplicates and implied relationships are not silently missed, while every existing caller keeps seeing identical results unless it explicitly opts in

  Background:
    Given I have a fresh pyArchimate model for derivation testing

  # --- User Story 1 (P1): Find redundant explicit relationships duplicating a longer implied chain ---

  @US1 @FR-005
  Scenario: Duplicate implied by a three-step chain is reported when opted in
    Given elements A, B, C, D where A relates to B, B relates to C, and C relates to D forming a supported three-step chain
    And an explicit relationship of the chain-implied type already exists directly between A and D
    When the scan is run with max_chain_length 3
    Then the report includes that explicit relationship
    And the report cites the three relationships that make up the implying chain
    When the scan is run
    Then the report is empty

  # --- User Story 2 (P2): Query the relationship implied between two elements connected only by a longer chain ---

  @US2 @FR-006
  Scenario: Querying two elements connected only by a three-step chain returns the implied relationship
    Given two elements connected only by a supported three-step chain
    When the derived relationship is requested for that pair with max_chain_length 3
    Then the result identifies the implied relationship type
    And the result references the full three-leg chain
    When the derived relationship is requested for that pair
    Then the result indicates no derivation applies

  # --- User Story 3 (P3): Existing callers see unchanged behavior unless they opt in ---

  @US3 @FR-010
  Scenario: A longer-than-two-step chain is invisible until max_chain_length is explicitly raised
    Given elements A, B, C, D where A relates to B, B relates to C, and C relates to D forming a supported three-step chain
    And an explicit relationship of the chain-implied type already exists directly between A and D
    When the scan is run
    Then the report is empty
    When the scan is run with max_chain_length 3
    Then the report includes that explicit relationship

  @US3 @FR-011
  Scenario: Exceeding the default chain-length ceiling requires an explicit override
    Given elements A, B, C, D where A relates to B, B relates to C, and C relates to D forming a supported three-step chain
    When the scan is run with a max_chain_length above the default ceiling and no override
    Then a ValueError is raised for exceeding the chain-length ceiling
    When the scan is run with a max_chain_length above the default ceiling and the override given
    Then the scan completes without error
