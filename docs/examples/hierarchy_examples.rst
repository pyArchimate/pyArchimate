Hierarchy Code Examples
=======================

Complete working examples for element grouping and hierarchy queries.

Example 1: Simple Parent-Child
------------------------------

.. code-block:: python

   from pyArchimate import ArchiType
   from pyArchimate.model import Model

   model = Model('Simple Hierarchy')

   # Create elements
   process = model.add(ArchiType.BusinessProcess, 'Main Process')
   function = model.add(ArchiType.BusinessFunction, 'Sub Function')

   # Create relationship
   model.add_child(process.uuid, function.uuid)

   # Query
   parent = model.get_parent(function.uuid)
   assert parent == process

Example 2: Multi-Level Hierarchy
--------------------------------

.. code-block:: python

   # Create 3-level hierarchy
   enterprise = model.add(ArchiType.BusinessFunction, 'Enterprise')
   division = model.add(ArchiType.BusinessFunction, 'Sales Division')
   department = model.add(ArchiType.BusinessFunction, 'Sales Team')

   model.add_child(enterprise.uuid, division.uuid)
   model.add_child(division.uuid, department.uuid)

   # Query all ancestors
   ancestors = model.get_ancestors(department.uuid)
   # Result: [department, division, enterprise]

   # Check depth
   assert model.get_depth(department.uuid) == 2

Example 3: Sibling Queries
---------------------------

.. code-block:: python

   # Create parent with multiple children
   parent = model.add(ArchiType.BusinessFunction, 'Parent')
   child1 = model.add(ArchiType.BusinessFunction, 'Child 1')
   child2 = model.add(ArchiType.BusinessFunction, 'Child 2')
   child3 = model.add(ArchiType.BusinessFunction, 'Child 3')

   model.add_child(parent.uuid, child1.uuid)
   model.add_child(parent.uuid, child2.uuid)
   model.add_child(parent.uuid, child3.uuid)

   # Get siblings
   siblings = model.get_siblings(child1.uuid)
   assert len(siblings) == 2
   assert child2 in siblings and child3 in siblings

Example 4: Hierarchy Path Queries
---------------------------------

.. code-block:: python

   # Create hierarchy
   enterprise = model.add(ArchiType.BusinessFunction, 'Enterprise')
   sales = model.add(ArchiType.BusinessFunction, 'Sales')
   ops = model.add(ArchiType.BusinessFunction, 'Operations')
   sales_team = model.add(ArchiType.BusinessFunction, 'Sales Team')

   model.add_child(enterprise.uuid, sales.uuid)
   model.add_child(enterprise.uuid, ops.uuid)
   model.add_child(sales.uuid, sales_team.uuid)

   # Find by path
   results = model.find_by_hierarchy_path('/Enterprise')
   assert enterprise in results

   # Find children (wildcard)
   results = model.find_by_hierarchy_path('/Enterprise/*')
   assert len(results) == 2  # sales and ops

   # Find at specific depth
   results = model.find_by_hierarchy_path('/Enterprise/Sales/*')
   assert sales_team in results

Example 5: Complex Business Architecture
----------------------------------------

.. code-block:: python

   # Enterprise structure
   enterprise = model.add(ArchiType.BusinessFunction, 'Corporation')

   # Business units
   sales_div = model.add(ArchiType.BusinessFunction, 'Sales Division')
   ops_div = model.add(ArchiType.BusinessFunction, 'Operations Division')
   model.add_child(enterprise.uuid, sales_div.uuid)
   model.add_child(enterprise.uuid, ops_div.uuid)

   # Sales organization
   sales_team = model.add(ArchiType.BusinessFunction, 'Sales Team')
   cust_svc = model.add(ArchiType.BusinessFunction, 'Customer Service')
   model.add_child(sales_div.uuid, sales_team.uuid)
   model.add_child(sales_div.uuid, cust_svc.uuid)

   # Sales processes
   order_mgmt = model.add(ArchiType.BusinessProcess, 'Order Management')
   order_entry = model.add(ArchiType.BusinessProcess, 'Order Entry')
   model.add_child(sales_team.uuid, order_mgmt.uuid)
   model.add_child(order_mgmt.uuid, order_entry.uuid)

   # Queries
   assert len(model.get_root_elements()) == 1  # enterprise
   assert model.get_depth(order_entry.uuid) == 4
   descendants = model.get_descendants(sales_div.uuid)
   assert len(descendants) > 0

Example 6: Modifying Hierarchies
--------------------------------

.. code-block:: python

   # Create initial hierarchy
   parent1 = model.add(ArchiType.BusinessProcess, 'Parent 1')
   parent2 = model.add(ArchiType.BusinessProcess, 'Parent 2')
   child = model.add(ArchiType.BusinessProcess, 'Child')

   model.add_child(parent1.uuid, child.uuid)

   # Move child to parent2
   model.remove_child(parent1.uuid, child.uuid)
   model.add_child(parent2.uuid, child.uuid)

   assert model.get_parent(child.uuid) == parent2

Example 7: Root and Leaf Elements
---------------------------------

.. code-block:: python

   # Create hierarchy
   root = model.add(ArchiType.BusinessProcess, 'Root')
   branch = model.add(ArchiType.BusinessProcess, 'Branch')
   leaf = model.add(ArchiType.BusinessProcess, 'Leaf')

   model.add_child(root.uuid, branch.uuid)
   model.add_child(branch.uuid, leaf.uuid)

   # Query roots
   roots = model.get_root_elements()
   assert root in roots

   # Query leaves
   leaves = model.get_leaf_elements()
   assert leaf in leaves
   assert root not in leaves  # root has children

Example 8: Descendants Traversal
--------------------------------

.. code-block:: python

   # Create hierarchy
   parent = model.add(ArchiType.BusinessFunction, 'Parent')
   child1 = model.add(ArchiType.BusinessFunction, 'Child 1')
   child2 = model.add(ArchiType.BusinessFunction, 'Child 2')
   grandchild = model.add(ArchiType.BusinessFunction, 'Grandchild')

   model.add_child(parent.uuid, child1.uuid)
   model.add_child(parent.uuid, child2.uuid)
   model.add_child(child1.uuid, grandchild.uuid)

   # Get all descendants
   descendants = model.get_descendants(parent.uuid)
   assert len(descendants) == 3  # all children and grandchildren

   # Breadth-first order
   assert descendants[0] in [child1, child2]  # L1 before L2

See Also
--------

- :doc:`../guides/element-hierarchy`: Complete hierarchy guide
- :doc:`../api/model`: Model API reference
