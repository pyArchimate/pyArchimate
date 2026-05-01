Feature: Visual Styling of Elements
  As an architect
  I want to customize the appearance of elements with colors and styles
  So that I can highlight important elements and improve diagram readability

  Scenario: Set fill color on an element
    Given I have a model with a BusinessProcess called "Important Process"
    When I set the fill color of "Important Process" to "#ff0000"
    Then the fill color of "Important Process" should be "#ff0000"

  Scenario: Set multiple visual properties
    Given I have a model with a BusinessFunction called "Styled Function"
    When I set the following visual properties:
      | Property      | Value      |
      | Fill Color    | #00ff00    |
      | Line Color    | #0000ff    |
      | Line Width    | 2.0        |
      | Transparency  | 0.8        |
    Then all visual properties should be set correctly
    And I can retrieve each property individually

  Scenario: Use named colors for fill
    Given I have a model with a BusinessService called "Service"
    When I set the fill color of "Service" to "red"
    Then the fill color should be converted to hex format "#ff0000"

  Scenario: Validate color and numeric ranges
    Given I have a model with a BusinessObject called "Object"
    When I try to set an invalid hex color "#xyz123"
    Then it should fail with a color validation error
    And when I try to set transparency to "1.5"
    Then it should fail with a range validation error

  Scenario: Preserve visual styles in round-trip export/import
    Given I have a model with a BusinessProcess called "Styled Process"
    And I set visual properties: fill="#ffeb3b", line="#ff6f00", width=2.0, transparency=0.9
    When I export the model to XML
    And I import the model from XML
    Then all visual properties should be preserved exactly
    And the imported element should match the original styling
