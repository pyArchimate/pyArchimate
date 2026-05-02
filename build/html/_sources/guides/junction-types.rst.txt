Junction Types Guide
====================

Junction elements represent decision points in processes with AND, OR, or XOR semantics.

Supported Junction Types
------------------------

**AND**: All inputs must be satisfied
- All incoming flows must be present
- Synchronization point

**OR**: At least one input must be satisfied
- Any incoming flow can trigger
- Convergence point

**XOR**: Exactly one input must be satisfied
- Exclusive choice/decision
- Mutual exclusion

Setting Junction Types
----------------------

.. code-block:: python

   from pyArchimate import ArchiType
   from pyArchimate.model import Model

   model = Model('Process')

   # Create junction
   decision = model.add(ArchiType.Junction, 'Approve/Reject')

   # Set junction type
   decision.set_junction_type('xor')  # XOR junction

   # Get junction type
   jtype = decision.get_junction_type()
   # Returns: 'xor'

   # Clear junction type
   decision.set_junction_type(None)

Validation
~~~~~~~~~~

- Only valid values: 'and', 'or', 'xor'
- Case-insensitive (stored as lowercase)
- Invalid values raise ValueError

Process Flow Example
--------------------

.. code-block:: python

   # Main process
   order = model.add(ArchiType.BusinessProcess, 'Order Processing')
   entry = model.add(ArchiType.BusinessFunction, 'Order Entry')
   review = model.add(ArchiType.BusinessFunction, 'Order Review')
   approve = model.add(ArchiType.BusinessFunction, 'Approval')
   fulfill = model.add(ArchiType.BusinessFunction, 'Fulfillment')
   reject = model.add(ArchiType.BusinessFunction, 'Rejection')

   # Create decision point
   decision = model.add(ArchiType.Junction, 'Approve/Reject')
   decision.set_junction_type('xor')

   # Build process flow
   model.add_child(order.uuid, entry.uuid)
   model.add_child(order.uuid, review.uuid)
   model.add_child(order.uuid, decision.uuid)
   model.add_child(order.uuid, fulfill.uuid)
   model.add_child(order.uuid, reject.uuid)

Real-World Scenarios
--------------------

**AND Junction - Synchronization**
Multiple processes must complete before continuing:

.. code-block:: python

   sync = model.add(ArchiType.Junction, 'Synchronize')
   sync.set_junction_type('and')
   # All parallel flows must complete

**OR Junction - Convergence**
Any of multiple flows can proceed:

.. code-block:: python

   merge = model.add(ArchiType.Junction, 'Merge')
   merge.set_junction_type('or')
   # Any flow can trigger next step

**XOR Junction - Decision**
Exactly one path based on condition:

.. code-block:: python

   decision = model.add(ArchiType.Junction, 'Quality Check')
   decision.set_junction_type('xor')
   # Pass or Fail path, not both

Round-Trip Preservation
-----------------------

Junction types are preserved in XML export/import:

.. code-block:: python

   decision.set_junction_type('xor')
   model.write('model.archimate')

   m2 = Model('reloaded')
   m2.read('model.archimate')

   decision2 = m2.elems_dict[decision.uuid]
   assert decision2.get_junction_type() == 'xor'

Best Practices
--------------

1. **Use junctions for decision logic**, not just grouping
2. **Document junction conditions** in element description
3. **Keep junction semantics clear** in naming
4. **Use XOR for mutual exclusion** paths
5. **Use AND for synchronization** points

See Also
--------

- :doc:`../api/element`: Element API reference
- :doc:`element-hierarchy`: Hierarchy organization guide
