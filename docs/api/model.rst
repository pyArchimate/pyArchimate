Model Class - P3 Hierarchy & Query API Reference
==================================================

The ``Model`` class provides comprehensive methods for managing element hierarchies, querying relationships, and organizing elements into parent-child structures with full round-trip XML preservation.

Hierarchy Management Methods
----------------------------

Creating Relationships
~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: add_child(parent_uuid: str, child_uuid: str) -> None

   Add a parent-child relationship between two elements.

   :param parent_uuid: UUID of parent element
   :param child_uuid: UUID of child element
   :raises KeyError: If parent or child UUID not in model
   :raises ValueError: If child already has parent, cycle would be created, or max depth exceeded

   **Features:**
   - Automatic cycle detection prevents invalid hierarchies
   - Max depth limit (default 5 levels) prevents pathological nesting
   - Synchronizes bidirectional maps (parent→children and child→parent)

   **Example:**

   .. code-block:: python

      process = model.add(ArchiType.BusinessProcess, 'Order Management')
      func = model.add(ArchiType.BusinessFunction, 'Order Entry')
      service = model.add(ArchiType.BusinessService, 'Form Service')

      # Create hierarchy
      model.add_child(process.uuid, func.uuid)
      model.add_child(func.uuid, service.uuid)

.. py:method:: remove_child(parent_uuid: str, child_uuid: str) -> None

   Remove a parent-child relationship (orphan the child).

   :param parent_uuid: UUID of parent element
   :param child_uuid: UUID of child element
   :raises KeyError: If parent or child UUID not in model
   :raises ValueError: If child is not actually a child of parent

   **Example:**

   .. code-block:: python

      model.remove_child(process.uuid, func.uuid)
      # func is now orphaned (no parent)

Basic Hierarchy Queries
-----------------------

.. py:method:: get_parent(elem_uuid: str) -> Optional[Element]

   Get the parent element of a given element.

   :param elem_uuid: Element UUID
   :return: Parent Element or None if root
   :rtype: Optional[Element]

   **Example:**

   .. code-block:: python

      parent = model.get_parent(func.uuid)
      if parent:
          print(f"Parent: {parent.name}")
      else:
          print("Element is at root level")

.. py:method:: get_children(elem_uuid: str) -> list[Element]

   Get all direct children of a given element.

   :param elem_uuid: Element UUID
   :return: List of child Elements (empty if no children)
   :rtype: list[Element]

   **Example:**

   .. code-block:: python

      children = model.get_children(process.uuid)
      for child in children:
          print(f"Child: {child.name}")

Root and Leaf Queries
~~~~~~~~~~~~~~~~~~~~~

.. py:method:: get_root_elements() -> list[Element]

   Get all root elements (elements with no parent).

   :return: List of root Elements
   :rtype: list[Element]

   **Example:**

   .. code-block:: python

      roots = model.get_root_elements()
      print(f"Found {len(roots)} root elements")

.. py:method:: get_leaf_elements() -> list[Element]

   Get all leaf elements (elements with no children).

   :return: List of leaf Elements
   :rtype: list[Element]

   **Example:**

   .. code-block:: python

      leaves = model.get_leaf_elements()
      for leaf in leaves:
          print(f"Leaf: {leaf.name}")

Ancestry and Depth Methods
----------------------------

.. py:method:: get_ancestors(elem_uuid: str) -> list[Element]

   Get all ancestors of an element from the element itself to the root.

   :param elem_uuid: Element UUID
   :return: List of Elements [elem, parent, grandparent, ..., root]
   :rtype: list[Element]

   **Example:**

   .. code-block:: python

      ancestors = model.get_ancestors(service.uuid)
      # Returns: [service, func, process]
      for ancestor in ancestors:
          print(f"Ancestor: {ancestor.name}")

.. py:method:: get_descendants(elem_uuid: str) -> list[Element]

   Get all descendants of an element in breadth-first order.

   :param elem_uuid: Element UUID
   :return: List of descendant Elements (excludes the element itself)
   :rtype: list[Element]

   **Example:**

   .. code-block:: python

      descendants = model.get_descendants(process.uuid)
      # Returns all elements under process at any depth
      for desc in descendants:
          print(f"Descendant: {desc.name}")

.. py:method:: get_depth(elem_uuid: str) -> int

   Get the nesting depth of an element (0 = root).

   :param elem_uuid: Element UUID
   :return: Depth level
   :rtype: int

   **Example:**

   .. code-block:: python

      depth = model.get_depth(service.uuid)
      if depth == 0:
          print("Root element")
      else:
          print(f"Depth: {depth}")

Advanced Query Methods
----------------------

Sibling Queries
~~~~~~~~~~~~~~~

.. py:method:: get_siblings(elem_uuid: str) -> list[Element]

   Get all sibling elements (elements with same parent).

   :param elem_uuid: UUID of element to find siblings for
   :return: List of sibling Elements (excludes elem_uuid itself)
   :rtype: list[Element]
   :raises KeyError: If element UUID not in model

   **Example:**

   .. code-block:: python

      # Create multiple functions under process
      func1 = model.add(ArchiType.BusinessFunction, 'Order Entry')
      func2 = model.add(ArchiType.BusinessFunction, 'Order Review')
      model.add_child(process.uuid, func1.uuid)
      model.add_child(process.uuid, func2.uuid)

      # Get siblings of func1
      siblings = model.get_siblings(func1.uuid)
      # Returns: [func2]

Path-Based Hierarchy Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: find_by_hierarchy_path(path: str) -> list[Element]

   Find elements by hierarchy path with wildcard support.

   :param path: Hierarchy path string starting with '/', levels separated by '/'
   :return: List of matching Elements
   :rtype: list[Element]

   **Path Format:**
   - Absolute paths: ``/Root``, ``/Parent/Child/Grandchild``
   - Wildcard suffix: ``/Parent/Child/*`` (matches all children of Child)
   - Wildcard in path: ``/Parent/*/Grandchild`` (matches any Child)

   **Examples:**

   .. code-block:: python

      # Get specific element by path
      results = model.find_by_hierarchy_path('/Order Management')
      # Returns: [order_management_elem]

      # Get all children at specific depth
      results = model.find_by_hierarchy_path('/Order Management/Order Entry')
      # Returns: [order_entry_elem]

      # Get all grandchildren (wildcard)
      results = model.find_by_hierarchy_path('/Order Management/*')
      # Returns: [func1, func2, func3, ...]

      # Get deep descendants (wildcard in middle)
      results = model.find_by_hierarchy_path('/Order Management/*/Services')
      # Returns all Services under any function in Order Management

Performance Characteristics
----------------------------

**Time Complexity:**

- ``add_child()``: O(depth) - performs cycle detection
- ``get_parent()``: O(1) - direct map lookup
- ``get_children()``: O(n) - where n = number of children
- ``get_ancestors()``: O(depth) - walks parent chain
- ``get_descendants()``: O(m) - where m = number of descendants (BFS)
- ``get_siblings()``: O(n) - where n = number of siblings
- ``find_by_hierarchy_path()``: O(m) - where m = elements matching path

**Performance on Large Models:**

- Cycle detection: <1ms (max depth 5)
- All queries: <10ms on 1000+ element models
- Memory: ~100 bytes per parent-child relationship

Round-Trip Preservation
-----------------------

All hierarchy relationships are automatically preserved during XML export/import:

.. code-block:: python

   # Create hierarchy
   process = model.add(ArchiType.BusinessProcess, 'Process')
   func = model.add(ArchiType.BusinessFunction, 'Function')
   model.add_child(process.uuid, func.uuid)

   # Export to XML
   model.write('model.archimate')

   # Import from XML
   m2 = Model('reloaded')
   m2.read('model.archimate')

   # Hierarchy is preserved exactly
   process2 = m2.elems_dict[process.uuid]
   func2 = m2.elems_dict[func.uuid]
   assert m2.get_parent(func2.uuid) == process2

Constraints and Limits
----------------------

**Depth Limit:** Maximum nesting depth is 5 levels (configurable)
- Prevents stack overflow on deep traversals
- Suitable for most enterprise architectures

**Single Parent:** Each element can have at most one parent
- Creates tree structures (not DAGs)
- Simplifies hierarchy management and visualization

**Cycle Prevention:** Automatic validation prevents circular relationships
- add_child() rejects any relationship that would create a cycle
- Ensures hierarchy validity at all times

See Also
--------

- :doc:`../guides/element-hierarchy`: Complete hierarchy usage guide
- :doc:`../examples/hierarchy_examples`: Working code examples
- :doc:`element`: Element class API reference
