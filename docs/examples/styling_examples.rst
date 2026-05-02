Visual Styling Code Examples
=============================

Complete working examples for element visual customization.

Example 1: Basic Color Setup
----------------------------

.. code-block:: python

   from pyArchimate import ArchiType
   from pyArchimate.model import Model

   model = Model('Styled Architecture')

   # Create element
   process = model.add(ArchiType.BusinessProcess, 'Process')

   # Set color
   process.set_fill_color('#ff0000')  # Red

   # Retrieve color
   color = process.get_fill_color()
   assert color == '#ff0000'

Example 2: Named Colors
-----------------------

.. code-block:: python

   # Use named colors (auto-converted to hex)
   elem1 = model.add(ArchiType.BusinessProcess, 'Critical')
   elem1.set_fill_color('red')

   elem2 = model.add(ArchiType.BusinessProcess, 'Healthy')
   elem2.set_fill_color('green')

   elem3 = model.add(ArchiType.BusinessProcess, 'Warning')
   elem3.set_fill_color('orange')

   # All stored as hex internally
   assert elem1.get_fill_color() == '#ff0000'
   assert elem2.get_fill_color() == '#008000'

Example 3: Complete Styling
---------------------------

.. code-block:: python

   # Set all style properties
   elem = model.add(ArchiType.BusinessProcess, 'Process')

   elem.set_fill_color('#ffeb3b')      # Yellow fill
   elem.set_line_color('#ff6f00')      # Orange border
   elem.set_line_width(2.0)            # 2px border
   elem.set_transparency(0.8)          # 80% opaque

   # Verify all properties
   style = elem.get_visual_style()
   assert style['fillColor'] == '#ffeb3b'
   assert style['lineColor'] == '#ff6f00'
   assert style['lineWidth'] == 2.0
   assert style['transparency'] == 0.8

Example 4: Bulk Style Operations
--------------------------------

.. code-block:: python

   # Set multiple properties at once
   elem = model.add(ArchiType.BusinessProcess, 'Process')

   elem.set_visual_style(
       fill_color='#ffeb3b',
       line_color='#ff6f00',
       line_width=2.0,
       transparency=0.9
   )

   # Get all properties
   style = elem.get_visual_style()
   assert len(style) == 4

Example 5: Conditional Styling
------------------------------

.. code-block:: python

   # Style based on element type
   critical_process = model.add(ArchiType.BusinessProcess, 'Critical')
   standard_process = model.add(ArchiType.BusinessProcess, 'Standard')
   optional_process = model.add(ArchiType.BusinessProcess, 'Optional')

   # Color code by importance
   critical_process.set_fill_color('red')
   critical_process.set_line_width(3.0)

   standard_process.set_fill_color('green')
   standard_process.set_line_width(1.0)

   optional_process.set_fill_color('gray')
   optional_process.set_line_width(1.0)

Example 6: Hierarchy Styling
----------------------------

.. code-block:: python

   # Create styled hierarchy
   parent = model.add(ArchiType.BusinessFunction, 'Department')
   parent.set_fill_color('#e8f4f8')  # Light blue
   parent.set_transparency(0.95)

   child1 = model.add(ArchiType.BusinessFunction, 'Team 1')
   child1.set_fill_color('#b3e5fc')  # Medium blue
   child1.set_transparency(0.9)

   child2 = model.add(ArchiType.BusinessFunction, 'Team 2')
   child2.set_fill_color('#b3e5fc')
   child2.set_transparency(0.9)

   model.add_child(parent.uuid, child1.uuid)
   model.add_child(parent.uuid, child2.uuid)

   # Different colors for different hierarchy levels

Example 7: Resetting Styles
----------------------------

.. code-block:: python

   # Create and style element
   elem = model.add(ArchiType.BusinessProcess, 'Process')
   elem.set_fill_color('red')
   elem.set_transparency(0.5)

   # Reset all styles
   elem.reset_visual_style()

   # All properties now None
   assert elem.get_fill_color() is None
   assert elem.get_transparency() is None

Example 8: Partial Styling
--------------------------

.. code-block:: python

   # Set only some properties
   elem = model.add(ArchiType.BusinessProcess, 'Process')

   # Only set fill color
   elem.set_fill_color('#ff0000')

   # Get style (only fillColor set)
   style = elem.get_visual_style()
   assert 'fillColor' in style
   assert 'lineColor' not in style
   assert 'lineWidth' not in style

   # Add line color later
   elem.set_line_color('blue')
   style = elem.get_visual_style()
   assert 'lineColor' in style

Example 9: Round-Trip Preservation
---------------------------------

.. code-block:: python

   # Create and style element
   elem1 = model.add(ArchiType.BusinessProcess, 'Process')
   elem1.set_fill_color('#ffeb3b')
   elem1.set_line_color('#ff6f00')
   elem1.set_transparency(0.8)

   # Export
   model.write('model.archimate')

   # Re-import
   m2 = Model('reloaded')
   m2.read('model.archimate')

   # Verify styles preserved
   elem2 = m2.elems_dict[elem1.uuid]
   assert elem2.get_fill_color() == '#ffeb3b'
   assert elem2.get_line_color() == '#ff6f00'
   assert elem2.get_transparency() == 0.8

Example 10: Multiple Elements Styling
------------------------------------

.. code-block:: python

   # Create multiple elements with consistent styling
   processes = []
   for i in range(5):
       proc = model.add(ArchiType.BusinessProcess, f'Process {i+1}')
       proc.set_fill_color('#e3f2fd')  # Light blue
       proc.set_line_color('#1976d2')  # Dark blue
       proc.set_line_width(1.5)
       processes.append(proc)

   # Verify all styled
   for proc in processes:
       assert proc.get_fill_color() == '#e3f2fd'
       assert proc.get_line_width() == 1.5

See Also
--------

- :doc:`../guides/visual-styling`: Complete styling guide
- :doc:`../api/element`: Element API reference
