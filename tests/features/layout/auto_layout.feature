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

  Scenario: Hierarchical Layout for Organizational Models
    Given a view with parent-child relationships forming a hierarchy
    When hierarchical layout is applied
    Then elements are organized in layers
    And parent elements are positioned above children
    And elements maintain parent-child relationship structure

  Scenario: Hierarchical Layout Respects ArchiMate Layers
    Given a view with elements from Business, Application, and Technology layers
    When hierarchical layout is applied
    Then Business layer elements are positioned above Application layer
    And Application layer elements are positioned above Technology layer
    And ArchiMate layer boundaries are respected

  Scenario: Hierarchical Layout with Tree Structure
    Given a hierarchical view with one root element and multiple children
    When hierarchical layout is applied
    Then root element is at the top
    And child elements are arranged in the layer below root
    And all children are positioned consistently

  Scenario: Hierarchical Layout with Diamond DAG
    Given a view with diamond DAG structure (n1 -> [n2, n3] -> n4)
    When hierarchical layout is applied
    Then n1 is positioned at the top layer
    And n2 and n3 are in the middle layer
    And n4 is positioned at the bottom layer
    And edge crossings are minimized

  Scenario: Hierarchical Layout with Disconnected Components
    Given a view with multiple disconnected graph components
    When hierarchical layout is applied
    Then each component is laid out independently
    And all components are positioned on the canvas
    And all elements are processed

  Scenario: Hierarchical Layout Crossing Minimization
    Given a view with edges that could create crossings
    When hierarchical layout is applied
    Then edge crossing count is minimized
    And layout quality should be good

  Scenario: Hierarchical Layout Preserves Element Properties
    Given a hierarchical view with elements of different types
    When hierarchical layout is applied
    Then element types are preserved
    And element names are preserved
    And element documentation is preserved
    And only positions are modified
