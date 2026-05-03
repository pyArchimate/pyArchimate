Element Class API Reference
============================

.. note::

   ⚙️ **New to this topic?** Start with :doc:`../guides/visual-styling` and :doc:`../guides/junction-types` to understand element styling and junction semantics before diving into the API details.

The ``Element`` class represents ArchiMate elements with support for element hierarchy (parent-child relationships), visual styling, and junction type semantics.

Visual Styling Methods
----------------------

Color Properties
~~~~~~~~~~~~~~~~

.. py:method:: set_fill_color(color: Optional[str]) -> None

   Set the fill/background color of this element.

   :param color: Hex color (#RRGGBB), named color (e.g., 'red', 'blue'), or None to use default
   :type color: Optional[str]
   :raises ValueError: If color format is invalid

   **Supported Named Colors:**
   red, green, blue, yellow, orange, purple, pink, brown, gray, white, black

   **Example:**

   .. code-block:: python

      elem = model.add(ArchiType.BusinessProcess, 'Process')
      elem.set_fill_color('#ff0000')  # Hex color
      elem.set_fill_color('red')      # Named color
      elem.set_fill_color(None)       # Reset to default

.. py:method:: get_fill_color() -> Optional[str]

   Get the fill color of this element.

   :return: Hex color (#rrggbb) or None if not set
   :rtype: Optional[str]

.. py:method:: set_line_color(color: Optional[str]) -> None

   Set the border/line color of this element.

   :param color: Hex color (#RRGGBB), named color, or None to use default
   :type color: Optional[str]
   :raises ValueError: If color format is invalid

   **Example:**

   .. code-block:: python

      elem.set_line_color('#0066cc')
      elem.set_line_color('blue')

.. py:method:: get_line_color() -> Optional[str]

   Get the line color of this element.

   :return: Hex color (#rrggbb) or None if not set
   :rtype: Optional[str]

Line Width Property
~~~~~~~~~~~~~~~~~~~

.. py:method:: set_line_width(width: Optional[float]) -> None

   Set the border/line width of this element in pixels.

   :param width: Width in pixels (≥ 0), or None to use default
   :type width: Optional[float]
   :raises ValueError: If width is negative
   :raises TypeError: If width is not numeric

   **Example:**

   .. code-block:: python

      elem.set_line_width(2.0)  # 2 pixel border
      elem.set_line_width(0.5)  # 0.5 pixel border
      elem.set_line_width(None) # Reset to default

.. py:method:: get_line_width() -> Optional[float]

   Get the line width of this element.

   :return: Width in pixels or None if not set
   :rtype: Optional[float]

Transparency Property
~~~~~~~~~~~~~~~~~~~~~

.. py:method:: set_transparency(alpha: Optional[float]) -> None

   Set the opacity/transparency of this element.

   :param alpha: Opacity 0.0 (fully transparent) to 1.0 (fully opaque), or None to use default
   :type alpha: Optional[float]
   :raises ValueError: If alpha is out of range
   :raises TypeError: If alpha is not numeric

   **Example:**

   .. code-block:: python

      elem.set_transparency(1.0)   # Fully opaque
      elem.set_transparency(0.5)   # 50% transparent
      elem.set_transparency(0.0)   # Fully transparent
      elem.set_transparency(None)  # Reset to default

.. py:method:: get_transparency() -> Optional[float]

   Get the transparency/opacity of this element.

   :return: Opacity 0.0-1.0 or None if not set
   :rtype: Optional[float]

Bulk Style Operations
~~~~~~~~~~~~~~~~~~~~~

.. py:method:: set_visual_style(fill_color: Optional[str] = None, line_color: Optional[str] = None, line_width: Optional[float] = None, transparency: Optional[float] = None) -> None

   Set multiple visual style properties at once.

   :param fill_color: Fill color (hex or named)
   :param line_color: Line color (hex or named)
   :param line_width: Line width in pixels (≥ 0)
   :param transparency: Opacity 0.0-1.0
   :raises ValueError: If any property is invalid

   **Example:**

   .. code-block:: python

      elem.set_visual_style(
          fill_color='#ffeb3b',
          line_color='#ff6f00',
          line_width=2.0,
          transparency=0.9
      )

.. py:method:: get_visual_style() -> dict[str, Any]

   Get all visual style properties as a dictionary.

   :return: Dictionary with fillColor, lineColor, lineWidth, transparency (only set values)
   :rtype: dict[str, Any]

   **Example:**

   .. code-block:: python

      style = elem.get_visual_style()
      # Returns: {'fillColor': '#ffeb3b', 'lineColor': '#ff6f00', 'lineWidth': 2.0, 'transparency': 0.9}

.. py:method:: reset_visual_style() -> None

   Reset all custom visual styles to defaults.

   **Example:**

   .. code-block:: python

      elem.reset_visual_style()  # Clear all custom styles

Junction Type Methods
---------------------

.. py:method:: set_junction_type(junction_type: Optional[str]) -> None

   Set the junction type for a Junction element.

   :param junction_type: Junction type ('and', 'or', 'xor') or None
   :type junction_type: Optional[str]
   :raises ValueError: If junction_type is not valid

   **Valid Junction Types:**
   - 'and': All inputs must be satisfied
   - 'or': At least one input must be satisfied
   - 'xor': Exactly one input must be satisfied

   **Example:**

   .. code-block:: python

      junction = model.add(ArchiType.Junction, 'Decision Point')
      junction.set_junction_type('and')
      junction.set_junction_type('xor')
      junction.set_junction_type(None)  # Clear junction type

.. py:method:: get_junction_type() -> Optional[str]

   Get the junction type for a Junction element.

   :return: Junction type ('and', 'or', 'xor') or None if not set
   :rtype: Optional[str]

   **Example:**

   .. code-block:: python

      jtype = junction.get_junction_type()
      if jtype == 'and':
          print("AND junction - all inputs required")

Hierarchy Methods
-----------------

Parent-Child Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Element class stores its parent UUID reference. Use Model methods for full hierarchy management:

- ``element._parent_uuid``: Internal reference to parent element UUID (read-only)

Use ``Model.add_child()`` to create relationships and ``Model.get_parent()`` to query.

See :doc:`../guides/element-hierarchy` for hierarchy usage guide.

Round-Trip Preservation
-----------------------

All visual properties and junction types are automatically preserved during XML export/import cycles:

.. code-block:: python

   # Create and style element
   elem = model.add(ArchiType.BusinessProcess, 'Process')
   elem.set_fill_color('#ff0000')
   elem.set_transparency(0.8)

   # Export to XML
   model.write('model.archimate')

   # Import from XML
   m2 = Model('reloaded')
   m2.read('model.archimate')

   # Properties are preserved exactly
   elem2 = m2.elems_dict[elem.uuid]
   assert elem2.get_fill_color() == '#ff0000'
   assert elem2.get_transparency() == 0.8

See Also
--------

- :doc:`../guides/visual-styling`: Complete guide for visual customization
- :doc:`../guides/junction-types`: Junction type semantics and usage
- :doc:`../examples/styling_examples`: Code examples for visual styling
