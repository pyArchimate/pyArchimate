Feature: Viewpoint Round-Trip
  Scenario: Viewpoint assignment survives archi format round-trip
    Given I have a model with an element assigned to viewpoint "stakeholder"
    When I export the model to .archimate format and re-import it
    Then the re-imported element has viewpoint "stakeholder"

  Scenario: Viewpoint assignment survives OpenGroup format round-trip
    Given I have a model with an element assigned to viewpoint "capability"
    When I export the model to OpenGroup format and re-import it
    Then the re-imported element has viewpoint "capability"

  Scenario: Legacy file without viewpoints imports without error
    Given I have an .archimate file without viewpoint metadata
    When I import the legacy viewpoint file
    Then all elements are imported successfully with empty viewpoints lists

  Scenario: Primary view viewpoint survives round-trip
    Given I have a view with primary viewpoint "technology"
    When I export and re-import the model
    Then the view's primary viewpoint is still "technology"