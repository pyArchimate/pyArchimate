Hierarchy Code Examples
=======================

.. note::

   🔧 **Intermediate / Architecture** — Practical code examples for working with element hierarchies.

Example 1: Three-Level Process Hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a simple three-level hierarchy of business processes:

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Order Processing Hierarchy")

   # Level 1: Top-level process
   order_mgmt = model.add_element(
       name="Order Management",
       element_type=ArchiType.BusinessProcess
   )

   # Level 2: Sub-processes
   receive_order = model.add_element(
       name="Receive Order",
       element_type=ArchiType.BusinessProcess
   )
   validate_order = model.add_element(
       name="Validate Order",
       element_type=ArchiType.BusinessProcess
   )
   fulfill_order = model.add_element(
       name="Fulfill Order",
       element_type=ArchiType.BusinessProcess
   )

   # Create parent-child relationships (level 2)
   model.add_child(parent=order_mgmt, child=receive_order)
   model.add_child(parent=order_mgmt, child=validate_order)
   model.add_child(parent=order_mgmt, child=fulfill_order)

   # Level 3: Sub-sub-processes
   check_payment = model.add_element(
       name="Check Payment",
       element_type=ArchiType.BusinessProcess
   )
   check_stock = model.add_element(
       name="Check Stock",
       element_type=ArchiType.BusinessProcess
   )

   # Create parent-child relationships (level 3)
   model.add_child(parent=validate_order, child=check_payment)
   model.add_child(parent=validate_order, child=check_stock)

   # Verify structure
   print(f"Order Management has {len(order_mgmt.get_children())} direct children")
   print(f"Order Management has {len(order_mgmt.get_descendants())} total descendants")
   print(f"Validate Order has depth {validate_order.get_depth()}")

   # Save the model
   model.write("order_hierarchy.archimate")

Example 2: Path Wildcard Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find elements using hierarchy path patterns with wildcards:

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Service Architecture")

   # Create a multi-level service hierarchy
   payment_service = model.add_element(
       name="Payment Service",
       element_type=ArchiType.ApplicationService
   )

   payment_processing = model.add_element(
       name="Payment Processing",
       element_type=ArchiType.ApplicationService
   )
   fraud_check = model.add_element(
       name="Fraud Check",
       element_type=ArchiType.ApplicationService
   )

   model.add_child(parent=payment_service, child=payment_processing)
   model.add_child(parent=payment_service, child=fraud_check)

   # Level 3
   auth = model.add_element(
       name="Authorization",
       element_type=ArchiType.ApplicationService
   )
   capture = model.add_element(
       name="Capture",
       element_type=ArchiType.ApplicationService
   )

   model.add_child(parent=payment_processing, child=auth)
   model.add_child(parent=payment_processing, child=capture)

   # Query examples
   # Find all direct children of Payment Service
   results = model.find_by_hierarchy_path("Payment Service/*")
   print(f"Direct children: {[e.name for e in results]}")

   # Find all descendants matching a pattern
   results = model.find_by_hierarchy_path("Payment Service/*/Auth*")
   print(f"Authorization descendants: {[e.name for e in results]}")

   # Find all at a specific depth
   results = model.find_by_hierarchy_path("*/Processing/*")
   print(f"Depth 2 descendants: {[e.name for e in results]}")

Example 3: Walking a Subtree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recursively traverse a hierarchy to process all descendants:

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Organization Structure")

   # Create an organizational hierarchy
   company = model.add_element(
       name="Company",
       element_type=ArchiType.BusinessActor
   )

   engineering = model.add_element(
       name="Engineering",
       element_type=ArchiType.BusinessActor
   )
   backend = model.add_element(
       name="Backend Team",
       element_type=ArchiType.BusinessActor
   )

   model.add_child(parent=company, child=engineering)
   model.add_child(parent=engineering, child=backend)

   def print_hierarchy(element, indent=0):
       """Recursively print element hierarchy."""
       print("  " * indent + f"- {element.name}")
       for child in element.get_children():
           print_hierarchy(child, indent + 1)

   # Print the entire organizational hierarchy
   print_hierarchy(company)

   # Calculate total span of control
   def count_all_descendants(element):
       """Count all descendants including self."""
       total = 1
       for child in element.get_children():
           total += count_all_descendants(child)
       return total

   span = count_all_descendants(company)
   print(f"Total organizational units: {span}")

Example 4: Detecting Cycles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement cycle detection to ensure hierarchies are acyclic (no circular references):

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Acyclic Hierarchy Check")

   # Create some elements
   a = model.add_element(name="A", element_type=ArchiType.BusinessProcess)
   b = model.add_element(name="B", element_type=ArchiType.BusinessProcess)
   c = model.add_element(name="C", element_type=ArchiType.BusinessProcess)

   # Create a valid hierarchy
   model.add_child(parent=a, child=b)
   model.add_child(parent=b, child=c)

   def has_cycle(element, visited=None, rec_stack=None):
       """Check if adding a relationship would create a cycle."""
       if visited is None:
           visited = set()
       if rec_stack is None:
           rec_stack = set()

       visited.add(element.id)
       rec_stack.add(element.id)

       for child in element.get_children():
           if child.id not in visited:
               if has_cycle(child, visited, rec_stack):
                   return True
           elif child.id in rec_stack:
               return True

       rec_stack.remove(element.id)
       return False

   # Check for cycles
   print(f"Hierarchy has cycle: {has_cycle(a)}")

   # Try to detect if we could add a reverse relationship (which would create a cycle)
   def can_add_relationship(parent, child):
       """Check if adding parent->child relationship is safe."""
       # Check if child is already an ancestor of parent
       ancestors = parent.get_ancestors()
       return child not in ancestors

   print(f"Can add C->A? {can_add_relationship(c, a)}")  # False (would create cycle)
   print(f"Can add C->B? {can_add_relationship(c, b)}")  # False (would create cycle)

   # Add a safe new element
   d = model.add_element(name="D", element_type=ArchiType.BusinessProcess)
   print(f"Can add D as child of C? {can_add_relationship(d, c)}")  # True (safe)

Related Documentation
~~~~~~~~~~~~~~~~~~~~~

- :doc:`../guides/element-hierarchy` — Guide to hierarchies
- :doc:`../api/model` — Model and Element API
- :doc:`../concepts` — Core concepts
