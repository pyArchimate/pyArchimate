Feature: Post-L-Turn Minimum Segment Length (40px default)
  As a diagram layout engine
  I want segments following 90° bends to meet a minimum length
  So that turn segments in orthogonal paths are readable and distinct

  Background:
    Given default RoutingConfig with min_turn_segment=40

  Scenario: Default 40px post-turn segment enforcement
    Given a connection with an L-shaped path
    And the post-turn segment is only 10px
    When auto_route enforces minimum post-turn length
    Then the post-turn segment is extended to 40px

  Scenario: Terminal arrival segment is NOT extended
    Given a connection that terminates at a node
    And the final segment to the node is only 15px
    When auto_route enforces post-turn minimum segment length
    Then the terminal arrival segment remains unchanged (15px)

  Scenario: Custom 20px floor is respected
    Given RoutingConfig with min_turn_segment=20
    And a connection with a 10px post-turn segment
    When auto_route is applied
    Then the post-turn segment extends to 20px (not 40px)

  Scenario: Multiple L-turns enforced correctly
    Given a connection with three L-turns
    And all post-turn segments are 15px (too short)
    When auto_route is applied with default min_turn_segment=40
    Then the first and second L-turns have 40px post-turn segments
    And the third (terminal) L-turn remains unchanged
