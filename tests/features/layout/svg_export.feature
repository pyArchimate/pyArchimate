Feature: Export View as SVG Diagram

    As a developer using the pyArchimate library
    I want to export views as SVG diagrams
    So that I can inspect, share, and validate layouts without requiring the Archi desktop tool

    Scenario: Export a view with nodes to SVG string
        Given a view with 3 elements positioned in a grid
        When I export the view to SVG
        Then the SVG string contains valid XML with <svg> root element
        And the SVG contains one rectangle for each element
        And each rectangle has the correct position and size
        And each element name is rendered as text inside the rectangle

    Scenario: Export a view with connections to SVG
        Given a view with 2 connected elements
        When I export the view to SVG
        Then the SVG contains one polyline for each connection
        And each polyline is routed through stored bendpoints
        And each polyline is clipped at the node boundary edges
        And each connection has an arrowhead at the target end

    Scenario: SVG labels show short relationship type names
        Given a view with a "ServesRelationship" connection
        When I export the view to SVG
        Then the SVG contains a label "Serves" (without "Relationship" suffix)
        And the label is positioned on the longest segment of the connection
        And the label has a white background rectangle

    Scenario: Export view with word-wrapped element names
        Given a view with an element named "A Very Long Element Name That Should Wrap"
        When I export the view to SVG
        Then the element name is word-wrapped inside the rectangle
        And all wrapped lines are vertically centered

    Scenario: Export view to file
        Given a view with at least one element
        When I export the view to SVG with filepath "/tmp/test.svg"
        Then the SVG is written to the specified file
        And the file contains valid SVG XML with <?xml declaration
        And I can read the SVG string from the returned value

    Scenario: Export empty view
        Given an empty view with no elements
        When I export the view to SVG
        Then the SVG string is valid XML
        And the SVG contains no rectangles (no elements to render)
        And the SVG contains no polylines (no connections to render)

    Scenario: Export view respects node sizes
        Given a view with nodes of varying sizes (100x50, 120x60, 80x40)
        When I export the view to SVG
        Then each rectangle has the correct width and height attributes
        And smaller nodes have proportionally smaller rectangles
        And larger nodes have proportionally larger rectangles

    Scenario: SVG export with complex connection routing
        Given a view with elements in multiple rows and columns
        And connections with bendpoints routing through gap zones
        When I export the view to SVG
        Then each connection polyline passes through all bendpoints
        And polylines do not pass through node interiors
        And connection endpoints are clipped at node boundaries

    Scenario: Export view with Realization relationships
        Given a view with 2 elements connected by a "RealizationRelationship"
        When I export the view to SVG
        Then the connection polyline has a dashed stroke pattern (5,5)
        And the connection has a hollow arrow marker at the end
        And the connection stroke color is the standard gray (#4A4A4A)
        And the connection is labeled "Realization"

    Scenario: Export view with Serving relationships
        Given a view with 2 elements connected by a "ServingRelationship"
        When I export the view to SVG
        Then the connection polyline has a solid stroke (no dashes)
        And the connection has a filled arrow marker at the end
        And the connection stroke color is the standard teal (#4ECDC4)
        And the connection is labeled "Serving"

    Scenario: Export view with mixed ArchiMate relationship types
        Given a view with elements connected by multiple relationship types
        And connections include: Realization, Serving, Access, and Implementation
        When I export the view to SVG
        Then each connection renders with its distinct style
        And Realization connections use dashed lines with hollow arrows
        And Serving connections use solid lines with filled arrows
        And Access connections use dotted lines (2,4 pattern)
        And Implementation connections use dashed lines (5,5) with hollow arrows
        And each relationship type has a distinct stroke color

    Scenario: Export view with relationship color override
        Given a view with 2 elements connected by a "ServingRelationship"
        And the relationship has a stroke_color override to "#FF0000" (red)
        When I export the view to SVG
        Then the connection stroke color is the override color (#FF0000)
        And the connection still has a filled arrow marker
        And the connection is still labeled "Serving"
        And the dashed/solid pattern follows the Serving style

    Scenario: Export view with overlapping relationships
        Given a view with 3 elements arranged in a triangle
        And connections between all pairs (3 total relationships)
        And relationships may overlap visually
        When I export the view to SVG
        Then all 3 relationship polylines are rendered
        And each relationship is visible and not obscured by other elements
        And relationships are rendered before elements (proper layering)
        And relationship labels are rendered on top
        And relationship stroke opacity is 0.8 for visual hierarchy

    Scenario: Export view with Aggregation and Composition relationships
        Given a view with parent element and child elements
        And relationships: Aggregation (hollow diamond start), Composition (filled diamond start)
        When I export the view to SVG
        Then Aggregation relationships have a hollow diamond marker at the start
        And Composition relationships have a filled diamond marker at the start
        And both have filled arrow markers at the end
        And the stroke color distinguishes them (both gray, same line style)
