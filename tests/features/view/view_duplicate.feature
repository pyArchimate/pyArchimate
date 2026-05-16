Feature: View Duplication
  As a diagram designer
  I want to duplicate views to create variations
  So that I can reuse diagram layouts with different element sets

  Background:
    Given a model with 5 nodes and 4 connections in a view

  Scenario: Basic view duplication with default name
    Given a view named "Original" with 5 nodes and 4 connections
    When I duplicate the view without specifying a name
    Then a new view is created with name "Original (copy)"
    And the new view has 5 nodes
    And the new view has 4 connections
    And the original view is unchanged

  Scenario: View duplication with custom name
    Given a view named "OriginalDiagram" with 5 nodes and 4 connections
    When I duplicate the view with name "Variation"
    Then a new view is created with name "Variation"
    And the new view has 5 nodes and 4 connections
    And both views are registered in the model

  Scenario: Duplicated view independence
    Given a view with 3 nodes
    When I duplicate the view
    And modify a node position in the duplicate
    Then the original view's node position is unchanged
    And the duplicate has the modified position
