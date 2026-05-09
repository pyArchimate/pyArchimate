Feature: Auto-Format Elements and Connections
  As an Enterprise Architect
  I want to automatically standardize element sizes and fonts in my diagrams
  So that my views have consistent, professional appearance without manual effort

  Background:
    Given I have a view with multiple elements of different sizes
    And the elements have inconsistent fonts

  @wip
  Scenario: Format Elements with Standard Sizes
    When I apply auto-format to the view
    Then all elements should have standardized sizes based on their ArchiMate type
    And ApplicationComponent elements should be 100x80 pixels
    And ApplicationService elements should be 120x60 pixels
    And DataObject elements should be 80x80 pixels

  @wip
  Scenario: Format Elements with Standard Fonts
    When I apply auto-format to the view
    Then all elements should have standardized fonts
    And font family should be Arial for all elements
    And font size should be 10pt for ApplicationComponent elements
    And font size should be 9pt for TechnologyNode elements
    And font weight should be bold for service-type elements
    And font weight should be normal for other elements

  @wip
  Scenario: Preserve Element Properties During Formatting
    Given an element with custom documentation and type information
    When I apply auto-format to the view
    Then the element's name should be preserved
    And the element's type should be preserved
    And the element's documentation should be preserved
    And only size and font properties should be standardized

  @wip
  Scenario: Exclude Specific Elements from Formatting
    Given a view with elements that should not be formatted
    When I apply auto-format with excluded_element_ids set
    Then the excluded elements should retain their original size
    And the excluded elements should retain their original fonts
    And other elements should be formatted normally

  @wip
  Scenario: Reduce Size Variance
    Given a view with highly inconsistent element sizes
    And element sizes vary from 50x40 to 300x200 pixels
    When I apply auto-format to the view
    Then size variance should be reduced by at least 80%
    And all elements of the same type should have identical sizes

  @wip
  Scenario: Apply Grid Alignment During Formatting
    Given elements with positions that are not grid-aligned
    When I apply auto-format with grid alignment enabled
    And grid size is 10 pixels
    Then elements should be snapped to the 10-pixel grid
    And position accuracy should be within ±5 pixels of grid points

  @wip
  Scenario: Format Business Layer Elements
    Given a view containing BusinessActor, BusinessRole, and BusinessProcess elements
    When I apply auto-format to the view
    Then BusinessActor elements should be 100x80 with 10pt font
    And BusinessRole elements should be 100x70 with 10pt font
    And BusinessProcess elements should be 120x80 with 10pt font

  @wip
  Scenario: Format Application Layer Elements
    Given a view containing ApplicationComponent, ApplicationService, and DataObject
    When I apply auto-format to the view
    Then ApplicationComponent elements should be 100x80
    And ApplicationService elements should be 120x60 with bold font
    And DataObject elements should be 80x80

  @wip
  Scenario: Format Technology Layer Elements
    Given a view containing TechnologyNode, TechnologyArtifact, and TechnologyService
    When I apply auto-format to the view
    Then TechnologyNode elements should be 100x80 with 9pt font
    And TechnologyArtifact elements should be 80x80 with 9pt font
    And TechnologyService elements should be 120x60 with bold 9pt font

  @wip
  Scenario: Format Unknown Element Types with Default Standards
    Given a view with unknown or custom element types
    When I apply auto-format to the view
    Then unknown elements should receive default standard size (100x80)
    And unknown elements should receive default font (Arial 10pt)

  @wip
  Scenario: Handle Empty Views Gracefully
    Given an empty view with no elements
    When I apply auto-format to the view
    Then the operation should succeed without errors
    And zero elements should be processed
    And the view should remain unchanged

  @wip
  Scenario: Report Formatting Statistics
    Given a view with 10 elements
    And 2 elements are marked as excluded
    When I apply auto-format to the view
    Then the result should report 8 elements formatted
    And the result should report 2 elements skipped
    And the result should report formatting time in milliseconds

  @wip
  Scenario: Format Does Not Reposition Elements
    Given a view with elements at specific positions
    When I apply auto-format to the view
    Then element positions should remain unchanged
    And only element sizes and fonts should change
    And connections should remain valid

  @wip
  Scenario: Format Supports Free and Grid Alignment Modes
    Given a view with scattered element positions
    When I apply auto-format with alignment="free"
    Then element positions should not change
    And elements should not be snapped to grid

    When I apply auto-format with alignment="grid" and grid_size=10
    Then element positions should be snapped to 10-pixel grid
    And elements should be aligned consistently

  @wip
  Scenario: Achieve Size Variance Reduction (SC-004)
    Given a view with element size variance of 5000 square pixels
    When I apply auto-format to the view
    Then size variance should be reduced to less than 1000 square pixels
    And this satisfies Success Criterion SC-004 (80% reduction)

  @wip
  Scenario: Format Mixed-Layer View
    Given a view with elements from Business, Application, and Technology layers
    When I apply auto-format to the view
    Then Business layer elements should use standard sizes and fonts
    And Application layer elements should use standard sizes and fonts
    And Technology layer elements should use smaller fonts (9pt)
    And layer boundaries should be visually distinguished through size standards
