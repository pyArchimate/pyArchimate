Feature: Viewpoint Filtering
  Scenario: Filter elements by viewpoint
    Given I have a model with two elements
    And element A is assigned to viewpoint "stakeholder"
    And element B is assigned to viewpoint "capability"
    When I call model.get_elements_by_viewpoint("stakeholder")
    Then only element A is returned

  Scenario: Filter views by viewpoint
    Given I have a model with two views
    And view A has primary viewpoint "technology"
    And view B has primary viewpoint "capability"
    When I call model.get_views_by_viewpoint("technology")
    Then only view A is returned

  Scenario: Invalid viewpoint slug raises ValueError
    Given I have a model with an element
    When I assign an invalid viewpoint slug "unknown_vp" to the element
    Then a ValueError is raised
