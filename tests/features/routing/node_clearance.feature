Feature: Node Clearance Zone (25px default)
  As a developer routing connections in PyArchimate
  I want routing to maintain a 25px clearance zone around nodes
  So that connections have proper spacing and readability

  @wip
  Scenario: Default node clearance is 25px
    Given a view with two nodes and a straight connection between them
    When auto_route is applied with default routing config
    Then all connection segments maintain at least 25px distance from node edges
    And no segments pass through the node clearance zone

  @wip
  Scenario: Custom node clearance value respected
    Given a view with two nodes and a potential direct connection
    When auto_route is applied with node_clearance=15
    Then all connection segments maintain at least 15px distance from node edges
    And segments may be closer than 25px but never closer than 15px

  @wip
  Scenario: Clearance zone prevents direct passage
    Given a view where a straight path would pass 20px from a node side
    When auto_route is applied with node_clearance=25
    Then the routed path detours around the node
    And all waypoints maintain 25px minimum distance from that node

  @wip
  Scenario: Multiple connections respect clearance zone
    Given a view with three nodes and multiple connections
    When auto_route is applied with default node_clearance=25
    Then each connection maintains 25px clearance from all nodes
    And no segments intersect the clearance zone of any node

  @wip
  Scenario: Clearance zone works with tight layouts
    Given a dense view with 10 nodes close together
    When auto_route is applied with node_clearance=25
    Then routing still completes successfully
    And all segments maintain the clearance zone
    And connections are properly separated

  @wip
  Scenario: Terminal attachment segments allowed at node boundary
    Given a connection that attaches to a node
    When auto_route is applied with node_clearance=25
    Then the final segment endpoint touches the node boundary
    And the segment approaching the node respects the 25px clearance zone