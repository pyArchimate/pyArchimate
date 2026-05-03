Element Hierarchies
===================

.. note::

   🔧 **Intermediate / Architecture** — Learn how to organize elements into parent-child hierarchies and query relationships within them.

What Is a Hierarchy?
~~~~~~~~~~~~~~~~~~~~

A **hierarchy** (or **composite structure**) is a parent-child relationship between elements of the same type. Hierarchies allow you to:

- Organize complex systems into sub-systems
- Represent nested processes or services
- Group related elements for readability

For example, a business process can have sub-processes, which can have further sub-processes (up to a typical depth limit of 5 levels in ArchiMate).

The relationship type for parent-child composition is ``RelationType.ComposedOf``.

Creating Hierarchies
~~~~~~~~~~~~~~~~~~~~

**Adding a child element**

Use the ``add_child`` method on an element:

.. code-block:: python

   from pyArchimate import Model, ArchiType, RelationType

   model = Model(name="Processes")

   # Create a parent process
   parent = model.add_element(
       name="Order Management",
       element_type=ArchiType.BusinessProcess
   )

   # Add a child process
   child = model.add_element(
       name="Receive Order",
       element_type=ArchiType.BusinessProcess
   )

   # Create the parent-child relationship
   model.add_child(parent=parent, child=child)

**Maximum nesting depth**

ArchiMate typically restricts hierarchy depth to 5 levels. When adding a child, check that the nesting depth doesn't exceed this limit:

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Nested Processes")
   elements = []

   # Create 5-level deep hierarchy
   for i in range(5):
       elem = model.add_element(
           name=f"Level {i}",
           element_type=ArchiType.BusinessProcess
       )
       elements.append(elem)
       if i > 0:
           model.add_child(parent=elements[i-1], child=elem)

   # Attempting to add a 6th level child should be validated
   level6 = model.add_element(
       name="Level 6",
       element_type=ArchiType.BusinessProcess
   )
   # Check depth before adding
   if elements[-1].get_depth() < 5:
       model.add_child(parent=elements[-1], child=level6)

Querying Hierarchies
~~~~~~~~~~~~~~~~~~~~

**Get parent**

Retrieve the parent of an element:

.. code-block:: python

   child_elem = model.get_element("child_id")
   parent = child_elem.get_parent()

**Get children**

Retrieve direct children of an element:

.. code-block:: python

   parent_elem = model.get_element("parent_id")
   children = parent_elem.get_children()

**Get ancestors**

Retrieve all ancestors up the hierarchy:

.. code-block:: python

   elem = model.get_element("some_id")
   ancestors = elem.get_ancestors()  # [parent, grandparent, ...]

**Get descendants**

Retrieve all descendants down the hierarchy:

.. code-block:: python

   elem = model.get_element("root_id")
   descendants = elem.get_descendants()  # All children, grandchildren, etc.

**Get depth**

Get the depth of an element in the hierarchy (root level = 0):

.. code-block:: python

   elem = model.get_element("some_id")
   depth = elem.get_depth()

**Find by hierarchy path**

Query elements using a path-like syntax with wildcards:

.. code-block:: python

   # Find all processes at depth 2
   results = model.find_by_hierarchy_path("Level 0/Level 1/*")

   # Find elements matching a pattern
   results = model.find_by_hierarchy_path("*/Receive*")

Removing Hierarchies
~~~~~~~~~~~~~~~~~~~~

**Remove a child**

Remove a parent-child relationship:

.. code-block:: python

   parent = model.get_element("parent_id")
   child = model.get_element("child_id")
   model.remove_child(parent=parent, child=child)

**Orphaning behavior**

When you remove a parent-child relationship, the child element remains in the model but loses its parent (becomes an "orphan"):

.. code-block:: python

   model.remove_child(parent=parent, child=child)
   assert child.get_parent() is None  # Child is now orphaned
   assert child in model.elements  # But still exists in the model

Round-Trip Preservation
~~~~~~~~~~~~~~~~~~~~~~~

When you read and write a model, hierarchies are preserved in all supported formats:

.. code-block:: python

   # Read a model with hierarchies
   model = Model.read("original.archimate")

   # Modify the model
   # ...

   # Write back - hierarchies are preserved
   model.write("modified.archimate")

The ``ComposedOf`` relationship type is preserved during round-trip, ensuring your hierarchy structure survives export and re-import cycles.

Practical Example: Decomposing a Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's a practical example of building a multi-level service decomposition:

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Service Decomposition")

   # Create the top-level service
   payment_service = model.add_element(
       name="Payment Service",
       element_type=ArchiType.ApplicationService
   )

   # Add sub-services (level 2)
   payment_processing = model.add_element(
       name="Payment Processing",
       element_type=ArchiType.ApplicationService
   )
   fraud_detection = model.add_element(
       name="Fraud Detection",
       element_type=ArchiType.ApplicationService
   )

   model.add_child(parent=payment_service, child=payment_processing)
   model.add_child(parent=payment_service, child=fraud_detection)

   # Add sub-sub-services (level 3)
   card_auth = model.add_element(
       name="Card Authorization",
       element_type=ArchiType.ApplicationService
   )
   model.add_child(parent=payment_processing, child=card_auth)

   # Query the hierarchy
   print(f"Payment Service has {len(payment_service.get_children())} direct children")
   print(f"Payment Service has {len(payment_service.get_descendants())} total descendants")

   # Write to file (hierarchy preserved)
   model.write("service_hierarchy.archimate")

See Also
~~~~~~~~

- :doc:`../concepts` — Introduction to elements and relationships
- :doc:`../architecture` — How pyArchimate organizes packages
- :doc:`../api/model` — Full Model and Element API reference
- :doc:`../examples/hierarchy_examples` — Code examples
