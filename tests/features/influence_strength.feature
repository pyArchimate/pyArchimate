Feature: Preserve Influence Strength in Round-Trip Operations
  As a developer using pyArchimate
  I want to preserve influence relationship strength metadata through export/import cycles
  So that relationship semantics are maintained when exchanging models with other tools

  Background:
    Given I have a fresh pyArchimate model
    And I have two elements for creating relationships

  Scenario: Create relationship with influence strength
    When I create an Influence relationship with strength "high"
    Then the relationship is created successfully
    And the influence strength is stored as "high"

  Scenario: Export influence strength to .archimate format
    Given I have a relationship with influence strength "medium"
    When I export to .archimate format
    Then the influenceStrength field is written to the relationship
    And the strength value "medium" is preserved in the XML

  Scenario: Import influence strength from .archimate format
    Given I have an .archimate file with an Influence relationship strength "low"
    When I import the file
    Then the relationship is parsed successfully
    And the influence strength is accessible as "low"

  Scenario: Round-trip influence strength (.archimate format)
    Given I create an Influence relationship with strength "high"
    When I export to .archimate format
    And I re-import the exported file
    Then the influence strength is preserved as "high"
    And the relationship strength matches the original

  Scenario: Round-trip influence strength (OpenGroup format)
    Given I create an Influence relationship with strength "medium"
    When I export to OpenGroup exchange format
    And I re-import the exported file
    Then the influence strength is preserved as "medium"
    And the relationship strength matches the original

  Scenario: Import legacy modifier field as influence strength
    Given I have an .archimate file using the legacy "modifier" field
    When I import the file
    Then the modifier value is mapped to influenceStrength
    And the relationship strength is accessible in the model
    And the strength value is preserved

  Scenario: Export as canonical influenceStrength field
    Given I import a file with legacy "modifier" field
    When I export the model to .archimate format
    Then the exported file uses "influenceStrength" (canonical field)
    And the strength value is preserved
    And the file is compatible with modern tools

  Scenario: Complete round-trip with multiple strength values
    Given I create an Influence relationship with strength "high"
    And I create another Influence relationship with strength "low"
    When I export to .archimate format
    And I re-import the exported file
    And I export again to OpenGroup format
    Then both relationships preserve their strength values correctly
    And the values remain consistent across all export/import cycles
