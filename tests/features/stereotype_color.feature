Feature: Stereotype-Based Color Coding
  As a modeler
  I want to configure a default fill color on a stereotype
  So that every element carrying that stereotype renders consistently without per-element styling

  Scenario: Define a default color per stereotype
    Given a stereotype "Threat" with no color configured
    And elements "D1" and "D2" of type "Driver" assigned the "Threat" stereotype
    When the modeler sets the "Threat" stereotype's color to "#E8453C"
    Then elements "D1" and "D2" should have an effective fill color of "#e8453c"

  Scenario: New element automatically picks up a configured stereotype color
    Given a stereotype "Risk" with color "#F2A900"
    When a new element "R1" of type "Driver" is assigned the "Risk" stereotype
    Then element "R1" should have an effective fill color of "#f2a900"

  Scenario: Clearing a stereotype's color reverts its elements to no fill color
    Given a stereotype "Threat" with color "#E8453C"
    And an element "D1" of type "Driver" assigned the "Threat" stereotype
    When the modeler clears the "Threat" stereotype's color
    Then element "D1" should have no effective fill color

  Scenario: An element's own explicit color overrides its stereotype's color
    Given a stereotype "Risk" with color "#F2A900"
    And an element "D1" of type "Driver" assigned the "Risk" stereotype
    When the modeler sets element "D1"'s own fill color to "#8B0000"
    Then element "D1" should have an effective fill color of "#8b0000"

  Scenario: Clearing an element's own color falls back to its stereotype's color
    Given a stereotype "Risk" with color "#F2A900"
    And an element "D1" of type "Driver" assigned the "Risk" stereotype
    And element "D1"'s own fill color is set to "#8B0000"
    When the modeler clears element "D1"'s own fill color
    Then element "D1" should have an effective fill color of "#f2a900"

  Scenario: Reassigning an element's stereotype updates its resolved color
    Given a stereotype "Threat" with color "#E8453C"
    And a stereotype "Risk" with color "#F2A900"
    And an element "D1" of type "Driver" assigned the "Threat" stereotype
    When the modeler reassigns element "D1" to the "Risk" stereotype
    Then element "D1" should have an effective fill color of "#f2a900"

  Scenario: Stereotype colors survive save and reload
    Given a stereotype "Threat" with color "#E8453C"
    And an element "D1" of type "Driver" assigned the "Threat" stereotype
    When the modeler saves and reloads the model as "archimate"
    Then element "D1" should have an effective fill color of "#e8453c"

  Scenario: Automatically label non-standard stereotypes
    Given an element "App1" of type "ApplicationComponent" assigned the "Risk" stereotype
    And an element "App2" of type "ApplicationComponent" with no stereotype
    When the view is exported to SVG with no display option set
    Then the exported SVG should label "App1" with its stereotype
    And the exported SVG should not label "App2" with a stereotype
