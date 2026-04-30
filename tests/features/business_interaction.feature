Feature: Create and Manage BusinessInteraction Elements
  As a developer using pyArchimate
  I want to create, import, and export BusinessInteraction elements
  So that I can work with ArchiMate 3.x compliant business interaction concepts

  Background:
    Given I have a fresh pyArchimate model
    And BusinessInteraction is enabled in the schema

  Scenario: Create BusinessInteraction element successfully
    When I create a BusinessInteraction element named "Customer Service Interaction"
    Then the element is created without validation errors
    And the element type is BusinessInteraction
    And the element is stored in the model

  Scenario: Import BusinessInteraction from .archimate file
    Given I have an .archimate file containing a BusinessInteraction element
    When I import the file
    Then the BusinessInteraction element is parsed successfully
    And the element is available in the model
    And the element properties are preserved

  Scenario: Export BusinessInteraction to .archimate format
    Given I have a model with BusinessInteraction elements
    When I export to .archimate format
    Then the BusinessInteraction elements are written to the file
    And the exported file is valid ArchiMate XML
    And the BusinessInteraction element type is preserved

  Scenario: Export and reimport BusinessInteraction (round-trip)
    Given I create a BusinessInteraction element named "Test Interaction"
    When I export to .archimate format
    And I re-import the exported file
    Then the BusinessInteraction element is present in the reimported model
    And the element properties match the original
    And the element type remains BusinessInteraction

  Scenario: Import BusinessInteraction from OpenGroup exchange format
    Given I have an OpenGroup exchange file containing a BusinessInteraction element
    When I import the file
    Then the BusinessInteraction element is parsed successfully
    And the element is available in the model
    And the element properties are preserved

  Scenario: Export BusinessInteraction to OpenGroup exchange format
    Given I have a model with BusinessInteraction elements
    When I export to OpenGroup exchange format
    Then the BusinessInteraction elements are correctly mapped and written
    And the exported file is valid OpenGroup XML
    And the element type mapping is correct
