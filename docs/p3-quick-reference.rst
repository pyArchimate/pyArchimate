P3 Quick Reference - Element Hierarchy & Styling
=================================================

Quick lookup for P3 features: element grouping, visual styling, and junction types.

Hierarchy Methods
-----------------

**Creating Relationships:**

- ``model.add_child(parent_uuid, child_uuid)`` - Create parent-child relationship
- ``model.remove_child(parent_uuid, child_uuid)`` - Remove relationship

**Basic Queries:**

- ``model.get_parent(elem_uuid)`` → parent Element or None
- ``model.get_children(elem_uuid)`` → list[Element]
- ``model.get_ancestors(elem_uuid)`` → list[Element] (elem to root)
- ``model.get_descendants(elem_uuid)`` → list[Element] (all under elem)
- ``model.get_depth(elem_uuid)`` → int

**Root & Leaf:**

- ``model.get_root_elements()`` → list[Element]
- ``model.get_leaf_elements()`` → list[Element]

**Advanced Queries:**

- ``model.get_siblings(elem_uuid)`` → list[Element]
- ``model.find_by_hierarchy_path(path)`` → list[Element]

Visual Styling Methods
----------------------

**Fill & Line Colors:**

- ``elem.set_fill_color(color)`` - Set background color (hex or named)
- ``elem.get_fill_color()`` → hex color or None
- ``elem.set_line_color(color)`` - Set border color
- ``elem.get_line_color()`` → hex color or None

**Line Width & Transparency:**

- ``elem.set_line_width(pixels)`` - Set border width (≥0)
- ``elem.get_line_width()`` → float or None
- ``elem.set_transparency(alpha)`` - Set opacity (0.0-1.0)
- ``elem.get_transparency()`` → float or None

**Bulk Operations:**

- ``elem.set_visual_style(fill_color, line_color, line_width, transparency)``
- ``elem.get_visual_style()`` → dict[str, Any]
- ``elem.reset_visual_style()`` - Reset to defaults

Junction Type Methods
---------------------

- ``elem.set_junction_type(type)`` - Set to 'and', 'or', 'xor', or None
- ``elem.get_junction_type()`` → 'and'|'or'|'xor'|None

Common Patterns
---------------

**Create Hierarchy:**

.. code-block:: python

   parent = model.add(ArchiType.BusinessProcess, 'Parent')
   child = model.add(ArchiType.BusinessProcess, 'Child')
   model.add_child(parent.uuid, child.uuid)

**Style Element:**

.. code-block:: python

   elem.set_fill_color('#ff0000')      # Red fill
   elem.set_line_color('blue')         # Blue border
   elem.set_transparency(0.8)          # 80% opaque

**Query Hierarchy:**

.. code-block:: python

   siblings = model.get_siblings(elem.uuid)
   results = model.find_by_hierarchy_path('/Parent/Child/*')
   depth = model.get_depth(elem.uuid)

**Set Junction:**

.. code-block:: python

   junction = model.add(ArchiType.Junction, 'Decision')
   junction.set_junction_type('xor')   # Exclusive choice

Color Names
-----------

Supported: red, green, blue, yellow, orange, purple, pink, brown, gray, white, black

All converted to hex (#RRGGBB) internally.

Constraints
-----------

- **Max depth**: 5 levels
- **Single parent**: Each element has ≤1 parent
- **Cycles prevented**: Auto-validation prevents circular relationships
- **Transparency range**: 0.0 (transparent) to 1.0 (opaque)
- **Line width**: Must be ≥ 0.0 pixels

Performance
-----------

- ``add_child()``: O(depth)
- ``get_parent()``: O(1)
- ``get_children()``: O(n) where n = # children
- ``get_siblings()``: O(n) where n = # siblings
- ``find_by_hierarchy_path()``: O(m) where m = matching elements

All operations <10ms on 1000+ element models.

Full Documentation
------------------

- :doc:`guides/element-hierarchy` - Complete hierarchy guide
- :doc:`guides/visual-styling` - Styling guide
- :doc:`guides/junction-types` - Junction semantics
- :doc:`api/model` - Full Model API
- :doc:`api/element` - Full Element API

Examples
--------

- :doc:`examples/hierarchy_examples` - Working hierarchy code
- :doc:`examples/styling_examples` - Working styling code
