Feature: Viewpoint Assignment
  Scenario: Developer calls get_viewpoints() and sees all 13 standard viewpoints
    Given I have a pyArchimate model
    When I call model.get_viewpoints()
    Then I receive a list of 13 viewpoints
    And each viewpoint has an id, name, and description

  Scenario: Assign a single viewpoint to an element
    Given I have a model with an element
    When I assign the viewpoint "stakeholder" to the element
    Then element.viewpoints contains "stakeholder"

  Scenario: Assign multiple viewpoints to an element
    Given I have a model with an element
    When I assign viewpoints "stakeholder" and "capability" to the element
    Then element.viewpoints contains both "stakeholder" and "capability"

  Scenario: Remove a viewpoint from an element
    Given I have an element with viewpoint "stakeholder"
    When I remove the viewpoint "stakeholder" from the element
    Then element.viewpoints does not contain "stakeholder"

  Scenario: Set primary viewpoint on a view
    Given I have a model with a view
    When I set the primary viewpoint of the view to "technology"
    Then view.primary_viewpoint equals "technology"
