Visual Styling Code Examples
=============================

.. note::

   🔧 **Intermediate / Architecture** — Practical code examples for customizing element appearance.

Example 1: Using Hex and Named Colors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create elements with both hexadecimal and named color specifications:

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Color Examples")

   # Create elements with hex colors
   elem1 = model.add_element(
       name="Critical System",
       element_type=ArchiType.ApplicationService
   )
   elem1.set_fill_color("#FF5733")  # Bright red-orange (hex)
   elem1.set_line_color("#8B0000")  # Dark red (hex)
   elem1.set_line_width(2)

   # Create elements with named colors
   elem2 = model.add_element(
       name="Standard Service",
       element_type=ArchiType.ApplicationService
   )
   elem2.set_fill_color("lightblue")  # Named color (case-insensitive)
   elem2.set_line_color("darkblue")   # Named color

   # Create elements with transparency
   elem3 = model.add_element(
       name="Legacy Service",
       element_type=ArchiType.ApplicationService
   )
   elem3.set_fill_color("#CCCCCC")  # Gray
   elem3.set_transparency(0.7)      # 70% transparent (30% opaque)

   # Verify colors were set
   print(f"Elem1 fill: {elem1.get_fill_color()}")      # #FF5733
   print(f"Elem2 fill: {elem2.get_fill_color()}")      # lightblue
   print(f"Elem3 transparency: {elem3.get_transparency()}")  # 0.7

   model.write("colors.archimate")

Example 2: Bulk Styling with set_visual_style
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Apply consistent styling to multiple elements using style dictionaries:

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Bulk Styling Example")

   # Define a style template
   critical_style = {
       "fill_color": "#FFE6E6",  # Light red
       "line_color": "#CC0000",  # Bright red
       "line_width": 3,
       "transparency": 0.0       # Fully opaque
   }

   normal_style = {
       "fill_color": "#E6F2FF",  # Light blue
       "line_color": "#0066CC",  # Bright blue
       "line_width": 1,
       "transparency": 0.0
   }

   deprecated_style = {
       "fill_color": "#CCCCCC",  # Gray
       "line_color": "#666666",  # Darker gray
       "line_width": 1,
       "transparency": 0.5       # 50% transparent
   }

   # Create elements and apply styles based on category
   critical_system = model.add_element(
       name="Payment Gateway",
       element_type=ArchiType.ApplicationService
   )
   critical_system.set_visual_style(critical_style)

   normal_system = model.add_element(
       name="Logging Service",
       element_type=ArchiType.ApplicationService
   )
   normal_system.set_visual_style(normal_style)

   legacy_system = model.add_element(
       name="Legacy API",
       element_type=ArchiType.ApplicationService
   )
   legacy_system.set_visual_style(deprecated_style)

   # Verify styles
   payment_style = critical_system.get_visual_style()
   print(f"Payment Gateway style: {payment_style}")

   model.write("bulk_styled.archimate")

Example 3: Model-Wide Theme with Per-Element Overrides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set a default theme for the model and override for specific elements:

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Themed Model")

   # Define and set model-wide default theme
   default_theme = {
       "fill_color": "#F5F5F5",  # Light gray background
       "line_color": "#333333",  # Dark gray border
       "line_width": 1,
       "transparency": 0.0
   }

   model.set_default_theme(default_theme)

   # Create elements - they'll use the default theme
   process1 = model.add_element(
       name="Standard Process",
       element_type=ArchiType.BusinessProcess
   )

   process2 = model.add_element(
       name="Critical Process",
       element_type=ArchiType.BusinessProcess
   )

   # Override the critical process with custom styling
   override_style = {
       "fill_color": "#FFC0C0",  # Light pink
       "line_color": "#FF0000",  # Red
       "line_width": 2,
       "transparency": 0.0
   }
   process2.set_visual_style(override_style)

   # Add related elements
   service1 = model.add_element(
       name="Service A",
       element_type=ArchiType.ApplicationService
   )

   service2 = model.add_element(
       name="Critical Service",
       element_type=ArchiType.ApplicationService
   )
   service2.set_fill_color("#FF8888")  # Highlight with color

   # All elements now have styling - some from theme, some overridden
   model.write("themed.archimate")

Example 4: Round-Trip Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verify that styling is preserved when reading and writing models:

.. code-block:: python

   from pyArchimate import Model, ArchiType

   # Create and style a model
   model = Model(name="Styled Model")

   elem = model.add_element(
       name="Styled Element",
       element_type=ArchiType.BusinessProcess
   )
   elem.set_fill_color("#FF6B6B")
   elem.set_line_color("#C92A2A")
   elem.set_line_width(2)
   elem.set_transparency(0.2)

   # Save the model
   model.write("original.archimate")
   print("Saved original model with styling")

   # Read it back
   model2 = Model.read("original.archimate")
   elem2 = model2.get_element(elem.id)

   # Verify styling was preserved
   assert elem2.get_fill_color() == "#FF6B6B", "Fill color not preserved!"
   assert elem2.get_line_color() == "#C92A2A", "Line color not preserved!"
   assert elem2.get_line_width() == 2, "Line width not preserved!"
   assert elem2.get_transparency() == 0.2, "Transparency not preserved!"

   print("✓ All styling preserved in round-trip!")

   # Modify and save again
   elem2.set_fill_color("#4ECDC4")  # Teal
   model2.write("modified.archimate")

   # Read again to verify second round-trip
   model3 = Model.read("modified.archimate")
   elem3 = model3.get_element(elem.id)

   assert elem3.get_fill_color() == "#4ECDC4", "Updated color not preserved!"
   print("✓ Updated styling preserved in second round-trip!")

Styling Best Practices
~~~~~~~~~~~~~~~~~~~~~~

1. **Use consistent color schemes**: Define reusable style dictionaries for different element categories.

2. **Reserve strong colors for important elements**: Use bright colors (e.g., red) sparingly to highlight critical systems.

3. **Maintain visual hierarchy**: Use transparency and line width to show importance and relationships.

4. **Test round-trip preservation**: Always verify that styling survives export and re-import cycles.

5. **Consider accessibility**: Ensure color choices provide sufficient contrast for readability (especially for colorblind users).

Related Documentation
~~~~~~~~~~~~~~~~~~~~~

- :doc:`../guides/visual-styling` — Complete styling guide
- :doc:`../api/element` — Element API
- :doc:`../concepts` — Core concepts
