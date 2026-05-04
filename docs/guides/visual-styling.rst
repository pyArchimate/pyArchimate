Visual Styling
==============

.. note::

   🔧 **Intermediate / Architecture** — Customize the appearance of elements and diagrams through colors, line styles, and themes.

Color Model
~~~~~~~~~~~

PyArchimate supports two color specification formats:

**Hexadecimal colors**

Standard 6-digit hex color codes (RGB):

.. code-block:: python

   fill_color = "#FF5733"  # Bright orange-red
   line_color = "#2E86AB"  # Dark blue

**Named colors**

English color names (case-insensitive):

.. code-block:: python

   fill_color = "red"
   line_color = "blue"
   line_color = "DarkGreen"

Supported named colors include: red, blue, green, yellow, orange, purple, pink, brown, gray, white, black, and many more.

Per-Element Styling
~~~~~~~~~~~~~~~~~~~

You can customize the appearance of individual elements by setting their visual properties.

**Setting fill color**

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Styled Model")
   element = model.add_element(
       name="Important Process",
       element_type=ArchiType.BusinessProcess
   )

   # Set hex color
   element.set_fill_color("#FFD700")  # Gold

   # Or use a named color
   element.set_fill_color("gold")

**Getting fill color**

.. code-block:: python

   color = element.get_fill_color()  # Returns "#FFD700" or "gold"

**Setting line color and width**

.. code-block:: python

   element.set_line_color("#000000")  # Black
   element.set_line_width(3)  # 3-point width

**Setting transparency**

.. code-block:: python

   element.set_transparency(0.5)  # 50% transparent (alpha = 0.5)
   element.set_transparency(0.0)  # Fully opaque
   element.set_transparency(1.0)  # Fully transparent

**Getting visual properties**

.. code-block:: python

   fill = element.get_fill_color()
   line = element.get_line_color()
   width = element.get_line_width()
   alpha = element.get_transparency()

Bulk Styling
~~~~~~~~~~~~

**Apply the same style to multiple elements**

Use ``set_visual_style`` to apply a complete style dictionary:

.. code-block:: python

   style = {
       "fill_color": "#E8F4F8",
       "line_color": "#2E86AB",
       "line_width": 2,
       "transparency": 0.1
   }

   # Apply to multiple elements
   for element in model.elements:
       if element.element_type == ArchiType.ApplicationService:
           element.set_visual_style(style)

**Get all visual properties**

.. code-block:: python

   visual_properties = element.get_visual_style()
   # Returns: {"fill_color": "...", "line_color": "...", ...}

Model-Wide Themes
~~~~~~~~~~~~~~~~~

Set a **default theme** for the entire model. This serves as the base style for all elements, which you can then override on a per-element basis.

**Setting a default theme**

.. code-block:: python

   model = Model(name="Themed Model")

   default_theme = {
       "fill_color": "#FFFFFF",   # White background
       "line_color": "#333333",   # Dark gray border
       "line_width": 1,
       "transparency": 0.0
   }

   model.set_default_theme(default_theme)

**Overriding theme for specific elements**

.. code-block:: python

   # Most elements use the default theme
   regular_element = model.add_element(
       name="Regular",
       element_type=ArchiType.BusinessProcess
   )

   # But you can override for emphasis
   important_element = model.add_element(
       name="Critical System",
       element_type=ArchiType.ApplicationService
   )
   important_element.set_fill_color("#FF6B6B")  # Red to highlight importance
   important_element.set_line_width(3)

Round-Trip Preservation
~~~~~~~~~~~~~~~~~~~~~~~

When you read and write a model, all visual styling is preserved:

.. code-block:: python

   # Read a model with styling
   model = Model.read("styled.archimate")

   # Modify the model
   element = model.get_element("some_id")
   element.set_fill_color("#00FF00")

   # Write back - all styling (original + new) is preserved
   model.write("modified.archimate")

Visual styling survives export and re-import cycles in all supported formats.

Practical Example: Coloring by Layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's a practical example of styling elements based on their layer:

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Layered Styling")

   # Define color scheme by layer
   layer_colors = {
       "business": "#FFE6CC",     # Light orange for Business
       "application": "#CCE5FF",  # Light blue for Application
       "technology": "#E6CCFF"    # Light purple for Technology
   }

   # Add elements with layer-based styling
   business_process = model.add_element(
       name="Handle Order",
       element_type=ArchiType.BusinessProcess
   )
   business_process.set_fill_color(layer_colors["business"])

   app_service = model.add_element(
       name="Order Service",
       element_type=ArchiType.ApplicationService
   )
   app_service.set_fill_color(layer_colors["application"])

   tech_service = model.add_element(
       name="API Gateway",
       element_type=ArchiType.TechnologyService
   )
   tech_service.set_fill_color(layer_colors["technology"])

   # Write styled model
   model.write("layered.archimate")

Troubleshooting
~~~~~~~~~~~~~~~

**Invalid color format**

If you use an invalid color format (e.g., wrong hex syntax), the styling function will raise an error. Always use:

- Hex: ``#RRGGBB`` (6 digits)
- Named: English color name (case-insensitive)

**Styling not visible in diagrams**

If styling doesn't appear in exported diagrams:

1. Ensure you saved the model after styling (``model.write()``)
2. Check that your diagram tool respects custom styling (some tools may use predefined colors)
3. Verify the transparency value (0.0 = opaque, 1.0 = invisible)

See Also
~~~~~~~~

- :doc:`../concepts` — Introduction to elements
- :doc:`../architecture` — How pyArchimate organizes packages
- :doc:`../api/element` — Full Element API reference
- :doc:`../examples/styling_examples` — Code examples
