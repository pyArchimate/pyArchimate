Feature: Complete Model Round-Trip with All P3 Features
  As an architect
  I want to export complex models with all features and re-import them
  So that I can ensure complete fidelity of grouping, styling, and junctions

  Scenario: Complex model with hierarchies and visual styles
    Given I create a complex model with:
      | Type              | Name             | Parent              | Fill Color | Line Color |
      | BusinessProcess   | Main Process     | (root)              | #e8f4f8    | #0066cc    |
      | BusinessFunction  | Function 1       | Main Process        | #b3e5fc    | #0066cc    |
      | BusinessService   | Service A        | Function 1          | #b3e5fc    | #0066cc    |
      | BusinessProcess   | Parallel Process | (root)              | #f1f8e9    | #558b2f    |
      | BusinessActor     | Executive        | (root)              | #ff6b6b    | #d32f2f    |
      | BusinessRole      | CEO              | Executive           | #ff8787    | #d32f2f    |
    When I export the model to XML
    And I import the model from the XML
    Then all elements should exist with correct types
    And all hierarchies should be preserved exactly
    And all visual styles should match the original colors
    And the CEO should still be a child of Executive

  Scenario: Model with junction types and properties
    Given I create a model with decision points:
      | Type     | Name         | Junction Type | Property Key | Property Value |
      | Junction | AND Decision | and           | condition    | all-must-pass  |
      | Junction | OR Decision  | or            | condition    | any-can-pass   |
      | Junction | XOR Decision | xor           | condition    | one-must-pass  |
    When I export and import the model
    Then all junction types should be preserved
    And all junction properties should be restored
    And AND Decision should still have junction_type="and"

  Scenario: Mixed hierarchy with relationships and styling
    Given I create a multi-level business architecture:
      | Process          | Function     | Service      | Styling                      |
      | Order Management | Order Entry  | Form Service | fill=#fff3e0, line=#f57c00  |
      | Order Management | Order Review | Check Svc    | fill=#f3e5f5, line=#6a1b9a  |
      | Order Management | Fulfillment  | Ship Svc     | fill=#e8f5e9, line=#2e7d32  |
    And relationships between services:
      | Source       | Target       | Type | Description              |
      | Form Service | Check Svc    | Flow | Validation               |
      | Check Svc    | Ship Svc     | Flow | Approved orders go here  |
    When I export and import the complete model
    Then the 3-level hierarchy should be preserved
    And all 2 relationships should exist between services
    And all visual styling should match original colors
    And deep queries (path: /Order Management/Fulfillment/*) should return Ship Svc
