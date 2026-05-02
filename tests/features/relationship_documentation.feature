Feature: Preserve Relationship Documentation in Round-Trip Operations
  As a developer using pyArchimate
  I want to preserve relationship documentation/description through import/export cycles
  So that relationship semantics and context are maintained when exchanging models

  Background:
    Given I have a fresh pyArchimate model
    And I have two elements for creating relationships

  Scenario: Import relationship with documentation
    Given I have an .archimate file with a documented relationship
    When I import the file
    Then the relationship is parsed successfully
    And the documentation text is accessible via the description field

  Scenario: Access documented relationship properties
    Given I have imported a relationship with documentation "Handles data flow between systems"
    When I access the relationship properties
    Then the description field contains "Handles data flow between systems"
    And the documentation is not truncated or modified

  Scenario: Export documented relationship to .archimate format
    Given I have a relationship with description "Processes read this data"
    When I export to .archimate format
    Then the documentation element is written to the XML
    And the text content is "Processes read this data"

  Scenario: Round-trip relationship documentation (.archimate)
    Given I have imported a relationship with documentation "Critical business process"
    When I export to .archimate format
    And I re-import the exported file
    Then the documentation text is preserved as "Critical business process"
    And the relationship description matches the original

  Scenario: Round-trip relationship documentation (OpenGroup)
    Given I have created a relationship with description "System integration point"
    When I export to OpenGroup exchange format
    And I re-import the exported file
    Then the documentation text is preserved as "System integration point"
    And the relationship description matches the original

  Scenario: Preserve empty documentation
    Given I have a relationship with empty documentation ""
    When I export and re-import the relationship
    Then the documentation remains empty ""
    And no errors are raised

  Scenario: Preserve long documentation text
    Given I have a relationship with a long description "This is a very long documentation string that contains multiple sentences and spans many characters to test handling of extended text content in relationship metadata"
    When I export and re-import the relationship
    Then the documentation is preserved exactly
    And the full text is accessible

  Scenario: Preserve Unicode characters in documentation
    Given I have a relationship with description "Handles 関系説明 interactions"
    When I export and re-import the relationship
    Then the Unicode characters are preserved exactly
    And the documentation reads "Handles 関系説明 interactions" (or equivalent encoding)

  Scenario: Preserve special XML characters in documentation
    Given I have a relationship with description 'Contains <tag> & "quoted" values'
    When I export and re-import the relationship
    Then the special characters are properly escaped and preserved
    And the documentation reads correctly after re-import

  Scenario: Multiple relationships with documentation
    Given I have three relationships with different documentation texts
    When I export to .archimate format
    And I re-import the exported file
    Then all three documentation texts are preserved correctly
    And each relationship retains its unique documentation
