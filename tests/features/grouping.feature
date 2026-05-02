Feature: Element Grouping and Hierarchy Management
  As an architect
  I want to organize elements into hierarchical groups
  So that I can structure complex models into logical sub-components

  Scenario: Create a parent-child relationship
    Given I have a model with a BusinessProcess called "Main Process"
    And I have a model with a BusinessFunction called "Sub Function"
    When I add "Sub Function" as a child of "Main Process"
    Then "Sub Function" should have "Main Process" as its parent
    And "Main Process" should have "Sub Function" as a child

  Scenario: Create a multi-level hierarchy
    Given I have a model with a BusinessProcess called "Level 0"
    And I have a model with a BusinessProcess called "Level 1"
    And I have a model with a BusinessFunction called "Level 2"
    When I add "Level 1" as a child of "Level 0"
    And I add "Level 2" as a child of "Level 1"
    Then "Level 2" should have 2 ancestors
    And "Level 0" should have 1 descendant of depth 2

  Scenario: Prevent cycles in hierarchy
    Given I have a model with a BusinessProcess called "Element A"
    And I have a model with a BusinessProcess called "Element B"
    When I add "Element B" as a child of "Element A"
    Then adding "Element A" as a child of "Element B" should fail
    And the error should mention cycle detection

  Scenario: Remove parent-child relationship
    Given I have a model with a BusinessProcess called "Parent"
    And I have a model with a BusinessProcess called "Child"
    And "Child" is a child of "Parent"
    When I remove "Child" as a child of "Parent"
    Then "Child" should have no parent
    And "Parent" should have no children

  Scenario: Get all siblings of an element
    Given I have a model with a BusinessProcess called "Parent"
    And I have a model with 3 BusinessFunctions named "Child 1", "Child 2", "Child 3"
    When I add all BusinessFunction elements as children of "Parent"
    Then each child should have 2 siblings
    And the siblings of "Child 1" should be "Child 2" and "Child 3"

  Scenario: Query elements by hierarchy path
    Given I have a model with this hierarchy:
      | Parent | Child    | Grandchild |
      | Root   | Branch A | Leaf 1     |
      | Root   | Branch A | Leaf 2     |
      | Root   | Branch B | Leaf 3     |
    When I query for elements at path "/Root/Branch A"
    Then I should get the "Branch A" element
    And I query for elements at path "/Root/Branch A/*"
    Then I should get "Leaf 1" and "Leaf 2"

  Scenario: Orphan children when parent is deleted
    Given I have a model with a BusinessProcess called "Parent"
    And I have a model with 2 BusinessFunctions as children of "Parent"
    When I delete "Parent"
    Then the children should still exist in the model
    And all children should have no parent
