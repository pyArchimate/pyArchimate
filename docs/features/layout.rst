.. _layout-feature:

=========================
View Auto-Layout
=========================

Overview
========

The View Auto-Layout feature provides automatic graph layout algorithms for ArchiMate views, enabling diagram generation with minimal manual positioning. Two complementary algorithms are available:

- **Force-Directed Layout**: Physics-based simulation using spring-embedder algorithm for organic, aesthetically pleasing layouts
- **Hierarchical Layout**: Layer-based Sugiyama algorithm for structured, dependency-aware layouts

Quickstart
==========

Basic usage:

.. code-block:: python

    from pyArchimate.view.layout import apply_layout
    from pyArchimate.view.layout.core import LayoutConfig

    # Apply force-directed layout
    config = LayoutConfig(algorithm="force_directed", spacing=50)
    result = apply_layout(my_view, config)

    # Apply hierarchical layout
    config = LayoutConfig(algorithm="hierarchical", spacing=100)
    result = apply_layout(my_view, config)

    if result.success:
        print(f"Laid out {result.elements_processed} elements in {result.layout_time_ms}ms")

Algorithms
==========

Force-Directed Layout
---------------------

The force-directed layout uses a Spring-Embedder physics simulation:

- **Repulsive forces**: Nodes push each other away
- **Attractive forces**: Connected nodes pull toward each other
- **Damping**: Reduces oscillation and accelerates convergence
- **Early exit**: Stops iterations when all nodes move less than 0.01px

Configuration parameters:

- ``spacing``: Minimum space between elements (pixels)
- ``margin``: Margin around canvas edges
- ``layer_priority``: "mandatory" or "soft" for ArchiMate layer constraints

Performance: <5 seconds for 500 elements on modern hardware

Hierarchical Layout
-------------------

The hierarchical layout uses the Sugiyama layer-based algorithm:

- **Layer assignment**: Elements grouped by dependency depth
- **Crossing minimization**: Edge routing optimized to reduce crossing count
- **Node ordering**: Elements arranged within layers for visual clarity

Configuration parameters:

- ``spacing``: Vertical/horizontal gap between layers and elements
- ``margin``: Canvas margin
- ``layer_priority``: "mandatory" (enforce ArchiMate layers) or "soft" (use dependency levels)

Performance: <1 second for 500 elements

Auto-Format
===========

Elements can be automatically standardized:

.. code-block:: python

    from pyArchimate.view.layout import apply_format
    from pyArchimate.view.layout.core import LayoutConfig

    config = LayoutConfig(alignment="grid", grid_size=10)
    result = apply_format(my_view, config)

Features:

- **Standardized sizing**: All elements use ArchiMate standard dimensions (120×55 pixels)
- **Font normalization**: Segoe UI 9pt for all text
- **Grid alignment**: Optional snap-to-grid positioning
- **Element exclusion**: Specify elements to exclude from formatting

SVG Export
==========

Views can be exported to SVG with automatic symbol rendering:

.. code-block:: python

    svg_string = my_view.to_svg()
    my_view.to_svg(filepath="diagram.svg")

Features:

- **ArchiMate symbols**: Official symbol definitions for all element types
- **Standard colors**: ArchiMate-compliant color palette
- **Orthogonal routing**: Connections use horizontal/vertical segments
- **Relationship styling**: Official ArchiMate relationship rendering

Configuration Options
=====================

LayoutConfig parameters:

.. code-block:: python

    config = LayoutConfig(
        algorithm="force_directed",        # or "hierarchical"
        spacing=50,                        # Element spacing in pixels
        margin=20,                         # Canvas margin in pixels
        alignment="free",                  # or "grid" for grid snapping
        grid_size=10,                      # Grid cell size when alignment="grid"
        excluded_element_ids=[],           # Element IDs to exclude from repositioning
        routing_style="orthogonal",        # or "mixed_45" for diagonal segments
        layer_priority="mandatory",        # or "soft" for layer constraints
        node_size_constraints={}           # Optional min/max size constraints
    )

Edge Cases
==========

The layout algorithms handle several edge cases gracefully:

- **Single element**: No layout needed, element remains at original position
- **No connections**: Elements distributed across canvas using repulsion
- **Circular dependencies**: Detected and resolved using topological analysis
- **Disconnected components**: Each component laid out independently
- **Identical element sizes**: Variance tracking ensures consistent spacing

Error Handling
==============

Layout operations return a LayoutResult object:

.. code-block:: python

    result = apply_layout(view, config)

    if result.success:
        print(f"Success: {result.elements_processed} elements laid out")
    else:
        print(f"Error: {result.error_message}")
        print(f"Quality metrics: {result.quality_metrics}")

Common error scenarios:

- Invalid algorithm name → ValueError raised
- Invalid spacing/margin values → ValueError raised
- Invalid configuration → ValueError raised
- Layout timeout → operation completes with partial results

Undo/Rollback
=============

Layout operations can be undone:

.. code-block:: python

    from pyArchimate.view.layout import undo_layout

    # Apply layout
    result = apply_layout(view, config)

    # Undo to restore previous positions
    undo_result = undo_layout(view)

    if undo_result.success:
        print("Layout undone, original positions restored")

Performance Targets
===================

Benchmark results on modern hardware (Intel i7, 16GB RAM):

- Force-directed 100 elements: <500ms
- Force-directed 300 elements: <2 seconds
- Force-directed 500 elements: <5 seconds
- Hierarchical 300 elements: <1 second
- Hierarchical 500 elements: <1 second

SVG export overhead: <5% additional time

Advanced Topics
===============

Custom Element Sizing
---------------------

Override standard sizing for specific elements:

.. code-block:: python

    # Per-element override
    element.width = 150
    element.height = 80

    # Or use size constraints in config
    config = LayoutConfig(
        node_size_constraints={
            "min_width": 100,
            "max_width": 200,
            "min_height": 50,
            "max_height": 150
        }
    )

Element Exclusion
-----------------

Exclude specific elements from repositioning:

.. code-block:: python

    config = LayoutConfig(excluded_element_ids=[elem1.id, elem2.id])
    result = apply_layout(view, config)
    # elem1 and elem2 remain at original positions

Routing Styles
--------------

Two routing styles for connections:

- ``orthogonal``: Horizontal/vertical segments only (default, clean appearance)
- ``mixed_45``: Horizontal/vertical with optional ±45° angles (more direct paths)

.. code-block:: python

    config = LayoutConfig(routing_style="mixed_45")
    result = apply_layout(view, config)

Layer Constraints
-----------------

Two modes for enforcing ArchiMate layer hierarchy:

- ``mandatory``: Strictly enforce Business > Application > Technology > Motivation
- ``soft``: Prefer layer order but allow violations if needed for layout

.. code-block:: python

    config = LayoutConfig(layer_priority="soft")  # More flexible layout
    result = apply_layout(view, config)

Troubleshooting
===============

Layout appears too dense
------------------------

- Increase ``spacing`` parameter (default 50, try 75-100)
- Try hierarchical algorithm instead of force-directed

Elements are scattered too far
------------------------------

- Increase ``margin`` parameter (adds inward force near edges)
- Try smaller ``spacing`` value

Layout takes too long
---------------------

- Force-directed with 500+ elements may take 5-10 seconds
- Use hierarchical algorithm for faster results
- Reduce spacing to decrease force calculation iterations

Connections overlap too much
-----------------------------

- Increase ``spacing`` to create more room
- Try different routing style (``mixed_45``)
- Check if element exclusion is inadvertently skipping elements

See Also
========

- :doc:`/architecture` - Detailed technical architecture
- :doc:`/modules` - API reference documentation

