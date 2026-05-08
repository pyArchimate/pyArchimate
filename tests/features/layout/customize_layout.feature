Feature: Customize Layout Behavior
  As a developer
  I want to customize auto-layout behavior with advanced configuration options
  So that I can adapt layout to domain-specific preferences and constraints

  Scenario: Apply layout with custom spacing
    Given a view with 5 scattered elements
    When I apply layout with spacing=150
    Then layout should complete successfully
    And elements should have at least 150 pixels spacing between them

  Scenario: Exclude specific elements from layout
    Given a view with 5 elements
    And element 0 is locked in place at position (100, 100)
    When I apply layout with excluded_element_ids=[0]
    Then layout should complete successfully
    And element 0 should remain at position (100, 100)
    And other elements should be repositioned

  Scenario: Apply grid-based alignment
    Given a view with 3 elements at arbitrary positions
    When I apply format with alignment="grid" and grid_size=50
    Then format should complete successfully
    And all elements should snap to 50-pixel grid

  Scenario: Apply size constraints to elements
    Given a view with elements of varying sizes (50-300 width)
    When I apply format with node_size_constraints={min_width: 100, max_width: 200}
    Then all elements should have width between 100 and 200

  Scenario: Use soft layer priority
    Given a view with mixed Business/Application/Technology elements
    When I apply layout with layer_priority="soft"
    Then layout should complete successfully
    And layer boundaries may be violated if necessary for layout quality

  Scenario: Use mandatory layer priority
    Given a view with mixed Business/Application/Technology elements
    When I apply layout with layer_priority="mandatory"
    Then layout should complete successfully
    And Business layer elements should be above Application elements
    And Application elements should be above Technology elements

  Scenario: Apply orthogonal routing style
    Given a view with 4 connected elements
    When I apply layout with routing_style="orthogonal"
    Then connections should use only 0° and 90° angles
    And connections should not have 45° segments

  Scenario: Apply mixed-45 routing style
    Given a view with 4 connected elements at diagonal distances
    When I apply layout with routing_style="mixed_45"
    Then layout should complete successfully
    And connections may use 45° angles when beneficial

  Scenario: Combine multiple customization options
    Given a view with 6 elements and 8 connections
    When I apply layout with:
      | parameter            | value                                                    |
      | algorithm            | hierarchical                                            |
      | spacing              | 100                                                      |
      | margin               | 30                                                       |
      | alignment            | grid                                                     |
      | grid_size            | 25                                                       |
      | routing_style        | orthogonal                                               |
      | layer_priority       | mandatory                                                |
      | excluded_element_ids | [0]                                                      |
      | node_size_constraints| {min_width: 80, max_width: 200}                         |
    Then layout should complete successfully in under 2 seconds
    And all configuration options should be respected
    And element 0 should not be moved
    And other elements should be in hierarchical layout
    And grid alignment should be applied
    And layer boundaries should be enforced

  Scenario: Invalid spacing value rejected
    Given invalid configuration with spacing=0
    When I create layout configuration
    Then validation should fail with error "spacing must be positive"

  Scenario: Conflicting constraints validated
    Given invalid size constraints with min_width=300 and max_width=100
    When I create layout configuration
    Then validation should fail with error "min cannot exceed max"

  Scenario: Format respects excluded elements
    Given a view with 4 elements
    And elements 1 and 3 are marked as excluded
    When I apply format with excluded_element_ids=[1, 3]
    Then elements 1 and 3 should not be formatted
    And elements 0 and 2 should be formatted with standard dimensions

  Scenario: Combined layout and format preserves config
    Given a view with 5 elements
    When I apply layout and then format with same configuration
    Then both operations should respect the configuration parameters
    And final layout should be consistent with applied constraints
