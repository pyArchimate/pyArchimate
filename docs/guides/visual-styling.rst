Visual Styling Guide
====================

Customize element appearance with colors, line width, and transparency.

Basic Color Customization
-------------------------

.. code-block:: python

   # Set fill color (background)
   elem.set_fill_color('#ff0000')  # Red
   elem.set_fill_color('red')      # Named color

   # Set line color (border)
   elem.set_line_color('#0066cc')  # Blue

   # Get colors
   fill = elem.get_fill_color()
   line = elem.get_line_color()

Supported Named Colors
~~~~~~~~~~~~~~~~~~~~~~

red, green, blue, yellow, orange, purple, pink, brown, gray, white, black

Line Width & Transparency
-------------------------

.. code-block:: python

   # Set line width (pixels)
   elem.set_line_width(2.0)

   # Set transparency (0.0=transparent, 1.0=opaque)
   elem.set_transparency(0.8)

   # Get values
   width = elem.get_line_width()
   alpha = elem.get_transparency()

Bulk Style Operations
---------------------

.. code-block:: python

   # Set multiple properties at once
   elem.set_visual_style(
       fill_color='#ffeb3b',
       line_color='#ff6f00',
       line_width=2.0,
       transparency=0.9
   )

   # Get all properties
   style = elem.get_visual_style()
   # Returns dict: {'fillColor': '#ffeb3b', ...}

   # Reset to defaults
   elem.reset_visual_style()

Color Format
~~~~~~~~~~~~

**Hex Colors**: #RRGGBB format (case-insensitive)
- #ff0000 = red
- #00ff00 = green
- #0000ff = blue

**Named Colors**: Common color names
- 'red', 'blue', 'green', etc.

All named colors are automatically converted to hex on storage.

Validation
----------

- Fill/Line colors: Must be valid hex or known named color
- Line width: Must be ≥ 0.0
- Transparency: Must be 0.0-1.0

Invalid values raise ValueError.

Round-Trip Preservation
-----------------------

All visual properties are preserved in XML export/import:

.. code-block:: python

   elem.set_fill_color('#ff0000')
   elem.set_transparency(0.8)

   model.write('model.archimate')
   m2 = Model('reloaded')
   m2.read('model.archimate')

   # Properties preserved
   elem2 = m2.elems_dict[elem.uuid]
   assert elem2.get_fill_color() == '#ff0000'
   assert elem2.get_transparency() == 0.8

Real-World Example
------------------

Highlight critical processes:

.. code-block:: python

   critical_process = model.add(ArchiType.BusinessProcess, 'Critical')
   critical_process.set_fill_color('#ff0000')  # Red
   critical_process.set_transparency(0.9)

   standard_process = model.add(ArchiType.BusinessProcess, 'Standard')
   standard_process.set_fill_color('#00ff00')  # Green

See Also
--------

- :doc:`../api/element`: Element API reference
- :doc:`../examples/styling_examples`: Code examples
