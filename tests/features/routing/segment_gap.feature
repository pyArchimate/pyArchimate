@wip
Feature: Parallel Segment Gap (20px default)
  As a diagram layout engine
  I want parallel collinear segments to be separated by at least 20px (default)
  So that connection paths are readable and distinct

  Background:
    Given default RoutingConfig with min_segment_gap=20.0

  Scenario: Default 20px separation enforced
    Given a view with two connections routing through the same corridor
    When auto_route is applied with default RoutingConfig
    Then all collinear parallel segments are separated by >= 20px

  Scenario: Custom 5px gap is respected
    Given a view with two connections in the same corridor
    When auto_route is applied with RoutingConfig(min_segment_gap=5.0)
    Then collinear parallel segments are separated by >= 5px

  Scenario: Three overlapping segments are evenly spaced
    Given a view with three connections sharing a corridor
    When auto_route is applied with default min_segment_gap=20.0
    Then the three segments are evenly distributed with >= 20px between each
