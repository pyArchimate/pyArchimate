Feature: Auto-Layout Messy Diagram
  As a developer using pyArchimate
  I want to auto-layout a view with overlapping elements
  So that all elements are visible and properly organized

  Scenario: Layout a view with scattered elements
    Given a view with 10 scattered elements
    When auto-layout is applied
    Then all elements are non-overlapping
    And all elements remain visible
    And element properties are preserved

  Scenario: Layout respects element relationships
    Given a view with elements connected by relationships
    When auto-layout is applied
    Then connections remain valid
    And element relationships are maintained

  Scenario: Layout completes within performance target
    Given a view with 300 elements
    When auto-layout is applied
    Then layout completes in less than 2 seconds
    And all elements are positioned
