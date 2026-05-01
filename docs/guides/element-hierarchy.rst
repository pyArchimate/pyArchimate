Element Hierarchy & Grouping Guide
===================================

This guide explains how to organize ArchiMate elements into parent-child hierarchies for modeling complex enterprise architectures with logical grouping.

Core Concepts
-------------

**Hierarchy**: A tree structure where elements can have a single parent and multiple children.

**Parent-Child Relationship**: A containment relationship where a parent element groups one or more child elements.

**Root Elements**: Elements with no parent (top level of hierarchy).

**Leaf Elements**: Elements with no children (bottom level).

**Depth**: Number of levels from root (root = depth 0).

**Siblings**: Elements that share the same parent.

Creating Hierarchies
--------------------

Basic Parent-Child Relationship
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To organize elements into a hierarchy, use ``Model.add_child()``:

.. code-block:: python

   from pyArchimate import ArchiType
   from pyArchimate.model import Model

   # Create elements
   model = Model('Enterprise Architecture')

   process = model.add(ArchiType.BusinessProcess, 'Order Management')
   func = model.add(ArchiType.BusinessFunction, 'Order Entry')
   service = model.add(ArchiType.BusinessService, 'Form Service')

   # Create relationships
   model.add_child(process.uuid, func.uuid)
   model.add_child(func.uuid, service.uuid)

   # Result:
   # Order Management (root)
   #   └─ Order Entry
   #      └─ Form Service

Multi-Level Hierarchies
~~~~~~~~~~~~~~~~~~~~~~~

Create deeper hierarchies by nesting multiple levels:

.. code-block:: python

   # 3-level hierarchy
   enterprise = model.add(ArchiType.BusinessFunction, 'Enterprise')
   division = model.add(ArchiType.BusinessFunction, 'Sales Division')
   department = model.add(ArchiType.BusinessFunction, 'Sales Team')

   model.add_child(enterprise.uuid, division.uuid)
   model.add_child(division.uuid, department.uuid)

   # Verify depth
   depth = model.get_depth(department.uuid)
   assert depth == 2  # Root is depth 0, so this is level 2

Maximum Nesting Depth
~~~~~~~~~~~~~~~~~~~~~

The default maximum nesting depth is 5 levels. If you try to create a deeper hierarchy, an error occurs:

.. code-block:: python

   # This will raise ValueError if depth > 5
   try:
       model.add_child(deep_parent.uuid, another_child.uuid)
   except ValueError as e:
       print(f"Max depth exceeded: {e}")

Querying Hierarchies
--------------------

Get Parent
~~~~~~~~~~

Find the parent of an element:

.. code-block:: python

   parent = model.get_parent(func.uuid)
   if parent:
       print(f"Parent: {parent.name}")
   else:
       print("Element is at root level")

Get Children
~~~~~~~~~~~~

Find all direct children of an element:

.. code-block:: python

   children = model.get_children(process.uuid)
   for child in children:
       print(f"Child: {child.name}")

Get All Ancestors
~~~~~~~~~~~~~~~~~

Get complete chain from element to root:

.. code-block:: python

   ancestors = model.get_ancestors(service.uuid)
   # Returns: [service, func, process] (from leaf to root)

   for ancestor in ancestors:
       print(f"{ancestor.name}")

Get All Descendants
~~~~~~~~~~~~~~~~~~~

Get all elements under an element at any depth:

.. code-block:: python

   descendants = model.get_descendants(process.uuid)
   # Returns all elements under process (breadth-first order)

   print(f"Found {len(descendants)} descendants")

Get Siblings
~~~~~~~~~~~~

Find all elements with the same parent:

.. code-block:: python

   # Create multiple children
   func1 = model.add(ArchiType.BusinessFunction, 'Order Entry')
   func2 = model.add(ArchiType.BusinessFunction, 'Order Review')
   func3 = model.add(ArchiType.BusinessFunction, 'Order Fulfillment')

   model.add_child(process.uuid, func1.uuid)
   model.add_child(process.uuid, func2.uuid)
   model.add_child(process.uuid, func3.uuid)

   # Get siblings of func1
   siblings = model.get_siblings(func1.uuid)
   # Returns: [func2, func3] (excludes func1 itself)

   for sibling in siblings:
       print(f"Sibling: {sibling.name}")

Hierarchy Path Queries
~~~~~~~~~~~~~~~~~~~~~~

Query elements by their path in the hierarchy:

.. code-block:: python

   # Exact path (single level)
   results = model.find_by_hierarchy_path('/Order Management')

   # Multi-level path
   results = model.find_by_hierarchy_path('/Order Management/Order Entry')

   # Get all children (wildcard)
   results = model.find_by_hierarchy_path('/Order Management/*')
   # Returns: [Order Entry, Order Review, Order Fulfillment]

   # Get all descendants at specific depth
   results = model.find_by_hierarchy_path('/Order Management/Order Entry/*')
   # Returns all services under Order Entry

Root and Leaf Elements
~~~~~~~~~~~~~~~~~~~~~~

Find top-level and bottom-level elements:

.. code-block:: python

   # Get all root elements (no parent)
   roots = model.get_root_elements()

   # Get all leaf elements (no children)
   leaves = model.get_leaf_elements()

Modifying Hierarchies
---------------------

Removing Relationships
~~~~~~~~~~~~~~~~~~~~~~

Orphan a child by removing its parent relationship:

.. code-block:: python

   # Remove func from process
   model.remove_child(process.uuid, func.uuid)

   # func is now orphaned (no parent)
   assert model.get_parent(func.uuid) is None

   # func still exists in model but is no longer grouped

Moving Elements
~~~~~~~~~~~~~~~

To "move" an element in hierarchy, remove it from old parent and add to new parent:

.. code-block:: python

   # Move func from process1 to process2
   model.remove_child(process1.uuid, func.uuid)
   model.add_child(process2.uuid, func.uuid)

   # func is now under process2 instead of process1

Deleting Elements
~~~~~~~~~~~~~~~~~

When an element is deleted, its children are orphaned (not deleted):

.. code-block:: python

   # Delete process
   process.delete()

   # func still exists but has no parent
   assert model.get_parent(func.uuid) is None
   assert func.uuid in model.elems_dict  # Still in model

Cycle Detection
---------------

The hierarchy system automatically prevents cycles:

.. code-block:: python

   # Create a relationship
   model.add_child(parent.uuid, child.uuid)

   # Try to create cycle (child as parent of original parent)
   try:
       model.add_child(child.uuid, parent.uuid)
   except ValueError as e:
       print(f"Cycle prevented: {e}")

This ensures the hierarchy always forms a valid tree structure.

Depth Calculation
-----------------

Get the nesting depth of any element:

.. code-block:: python

   # Root element
   process = model.add(ArchiType.BusinessProcess, 'Process')
   assert model.get_depth(process.uuid) == 0

   # First level child
   func = model.add(ArchiType.BusinessFunction, 'Function')
   model.add_child(process.uuid, func.uuid)
   assert model.get_depth(func.uuid) == 1

   # Second level child
   service = model.add(ArchiType.BusinessService, 'Service')
   model.add_child(func.uuid, service.uuid)
   assert model.get_depth(service.uuid) == 2

Real-World Example
------------------

Complete example showing typical enterprise architecture hierarchy:

.. code-block:: python

   from pyArchimate import ArchiType
   from pyArchimate.model import Model

   # Create model
   model = Model('Enterprise Architecture')

   # L0: Enterprise organization
   enterprise = model.add(ArchiType.BusinessFunction, 'Enterprise')

   # L1: Business units
   sales = model.add(ArchiType.BusinessFunction, 'Sales Division')
   ops = model.add(ArchiType.BusinessFunction, 'Operations Division')
   model.add_child(enterprise.uuid, sales.uuid)
   model.add_child(enterprise.uuid, ops.uuid)

   # L2: Departments
   sales_team = model.add(ArchiType.BusinessFunction, 'Sales Team')
   customer_svc = model.add(ArchiType.BusinessFunction, 'Customer Service')
   model.add_child(sales.uuid, sales_team.uuid)
   model.add_child(sales.uuid, customer_svc.uuid)

   # L3: Teams and processes
   order_entry = model.add(ArchiType.BusinessProcess, 'Order Entry')
   order_mgmt = model.add(ArchiType.BusinessProcess, 'Order Management')
   model.add_child(sales_team.uuid, order_entry.uuid)
   model.add_child(sales_team.uuid, order_mgmt.uuid)

   # Query the hierarchy
   print(f"Total elements: {len(model.elems_dict)}")
   print(f"Root elements: {len(model.get_root_elements())}")
   print(f"Leaf elements: {len(model.get_leaf_elements())}")

   # Find specific paths
   results = model.find_by_hierarchy_path('/Enterprise/Sales Division/*')
   print(f"Sales Division has {len(results)} direct children")

   # Explore descendants
   descendants = model.get_descendants(sales.uuid)
   print(f"Sales Division has {len(descendants)} descendants total")

Round-Trip Preservation
-----------------------

All hierarchy relationships are preserved when exporting and importing:

.. code-block:: python

   # Create and organize model
   process = model.add(ArchiType.BusinessProcess, 'Process')
   func = model.add(ArchiType.BusinessFunction, 'Function')
   model.add_child(process.uuid, func.uuid)

   # Export to XML
   model.write('model.archimate')

   # Import in new session
   m2 = Model('reloaded')
   m2.read('model.archimate')

   # Verify hierarchy is preserved
   process2 = m2.elems_dict[process.uuid]
   func2 = m2.elems_dict[func.uuid]
   assert m2.get_parent(func2.uuid) == process2

Best Practices
--------------

1. **Start with clear organization**: Define your hierarchy based on actual enterprise structure
2. **Use meaningful names**: Names should reflect the organization level and purpose
3. **Respect depth limits**: Keep hierarchies ≤5 levels for clarity and performance
4. **Avoid wide-shallow trees**: Prefer deeper, narrower hierarchies for better navigation
5. **Use types consistently**: Keep elements of same type at same hierarchy level
6. **Document structure**: Add descriptions to explain hierarchy rationale

Performance Considerations
--------------------------

- **add_child()**: O(depth) - performs cycle detection
- **get_parent()**: O(1) - instant lookup
- **get_children()**: O(n) - linear in number of children
- **get_ancestors()**: O(depth) - limited to max depth 5
- **get_descendants()**: O(m) - linear in number of descendants
- **get_siblings()**: O(n) - linear in number of siblings

All operations are optimized and perform well even on large models (1000+ elements).

See Also
--------

- :doc:`../api/model`: Complete Model API reference
- :doc:`../examples/hierarchy_examples`: Code examples for hierarchies
