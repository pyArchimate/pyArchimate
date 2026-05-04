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
        Given a view with a "ServestRelationship" connection
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
