# Traceability: GitHub issue #149
#   Composition and Aggregation are mutually exclusive ownership semantics between the
#   same element pair (ArchiMate 3.x Specification, Structural Relationships chapter).

Feature: Conflicting Composition and Aggregation between the same element pair
  As a modeler
  I want pyArchimate to flag a Composition and an Aggregation that exist directly between
  the same two elements
  So that I notice the semantic contradiction instead of it drifting silently into the model

  Background:
    Given I have a fresh pyArchimate model for composition/aggregation conflict testing

  Scenario: Composition and Aggregation between the same pair, same direction, is flagged
    Given elements A and B
    And a Composition relationship from A to B
    And an Aggregation relationship from A to B
    When the composition/aggregation conflict check is run
    Then the report flags one conflicting pair citing both relationships

  Scenario: Composition and Aggregation between the same pair, opposite direction, is flagged
    Given elements A and B
    And a Composition relationship from A to B
    And an Aggregation relationship from B to A
    When the composition/aggregation conflict check is run
    Then the report flags one conflicting pair citing both relationships

  Scenario: Composition alone between a pair is not flagged
    Given elements A and B
    And a Composition relationship from A to B
    When the composition/aggregation conflict check is run
    Then the conflict report is empty

  Scenario: Aggregation alone between a pair is not flagged
    Given elements A and B
    And an Aggregation relationship from A to B
    When the composition/aggregation conflict check is run
    Then the conflict report is empty

  Scenario: A model with no relationships yields an empty report
    When the composition/aggregation conflict check is run
    Then the conflict report is empty
