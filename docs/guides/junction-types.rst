Junction Types
===============

.. note::

   🔧 **Intermediate / Architecture** — Understand and work with logical junctions (AND, OR, XOR) in ArchiMate models.

What Is a Junction?
~~~~~~~~~~~~~~~~~~~

A **junction** is a special element in ArchiMate used to represent logical operations combining multiple influences or relationships. Junctions clarify how multiple flows (processes, relationships, influences) combine.

Rather than drawing multiple individual connections, junctions allow you to explicitly show:

- **AND**: All incoming influences must be satisfied
- **OR**: Any one of the incoming influences is sufficient
- **XOR**: Exactly one of the incoming influences applies

Junctions are represented as diamond-shaped symbols in diagrams.

Supported Junction Types
~~~~~~~~~~~~~~~~~~~~~~~~

ArchiMate defines three junction types:

``AND``
  All incoming influences must be satisfied. Used when all conditions must be met for the outgoing element to be active.

``OR``
  Any one of the incoming influences is sufficient. Used when any single condition is enough for the outgoing element to be active.

``XOR`` (Exclusive OR)
  Exactly one of the incoming influences applies. Used to show mutually exclusive alternatives.

Setting and Getting Junction Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Creating a junction element**

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="Junction Example")

   # Create a junction element
   junction = model.add_element(
       name="Approval Required",
       element_type=ArchiType.AndJunctionElement  # or OrJunctionElement, XorJunctionElement
   )

**Setting the junction type**

.. code-block:: python

   from pyArchimate import JunctionType

   junction.set_junction_type(JunctionType.AND)
   # or
   junction.set_junction_type(JunctionType.OR)
   # or
   junction.set_junction_type(JunctionType.XOR)

**Getting the junction type**

.. code-block:: python

   junction_type = junction.get_junction_type()
   if junction_type == JunctionType.AND:
       print("All conditions must be met")
   elif junction_type == JunctionType.OR:
       print("Any condition is sufficient")
   elif junction_type == JunctionType.XOR:
       print("Exactly one condition applies")

**Error handling**

Attempting to set an invalid junction type raises a ``ValueError``:

.. code-block:: python

   try:
       junction.set_junction_type("INVALID")  # ValueError
   except ValueError as e:
       print(f"Invalid junction type: {e}")

Typical Patterns
~~~~~~~~~~~~~~~~

**AND Junction: Multiple Approvals Required**

.. code-block:: python

   from pyArchimate import Model, ArchiType, RelationType, JunctionType

   model = Model(name="Multi-Approval Process")

   # Two independent approval steps
   manager_approval = model.add_element(
       name="Manager Approval",
       element_type=ArchiType.BusinessProcess
   )
   compliance_approval = model.add_element(
       name="Compliance Approval",
       element_type=ArchiType.BusinessProcess
   )

   # Both must succeed before the order is processed
   approval_junction = model.add_element(
       name="All Approvals Met",
       element_type=ArchiType.AndJunctionElement
   )
   approval_junction.set_junction_type(JunctionType.AND)

   # Order processing (requires both approvals)
   process_order = model.add_element(
       name="Process Order",
       element_type=ArchiType.BusinessProcess
   )

   # Relationships
   model.add_relationship(
       source=manager_approval,
       target=approval_junction,
       relationship_type=RelationType.Influences
   )
   model.add_relationship(
       source=compliance_approval,
       target=approval_junction,
       relationship_type=RelationType.Influences
   )
   model.add_relationship(
       source=approval_junction,
       target=process_order,
       relationship_type=RelationType.Influences
   )

**OR Junction: Any Channel Accepted**

.. code-block:: python

   # Customer can contact via phone, email, or chat
   phone_channel = model.add_element(
       name="Phone Support",
       element_type=ArchiType.ApplicationService
   )
   email_channel = model.add_element(
       name="Email Support",
       element_type=ArchiType.ApplicationService
   )
   chat_channel = model.add_element(
       name="Chat Support",
       element_type=ArchiType.ApplicationService
   )

   # Any one channel is sufficient for customer support
   contact_junction = model.add_element(
       name="Customer Can Contact",
       element_type=ArchiType.OrJunctionElement
   )
   contact_junction.set_junction_type(JunctionType.OR)

   support_service = model.add_element(
       name="Support Service",
       element_type=ArchiType.ApplicationService
   )

   # Any channel leads to support
   for channel in [phone_channel, email_channel, chat_channel]:
       model.add_relationship(
           source=channel,
           target=contact_junction,
           relationship_type=RelationType.Influences
       )
   model.add_relationship(
       source=contact_junction,
       target=support_service,
       relationship_type=RelationType.Influences
   )

**XOR Junction: Mutually Exclusive Paths**

.. code-block:: python

   # Process depends on payment method (credit card XOR bank transfer)
   credit_card_path = model.add_element(
       name="Credit Card Payment",
       element_type=ArchiType.ApplicationService
   )
   bank_transfer_path = model.add_element(
       name="Bank Transfer",
       element_type=ArchiType.ApplicationService
   )

   payment_choice = model.add_element(
       name="Choose Payment Method",
       element_type=ArchiType.XorJunctionElement
   )
   payment_choice.set_junction_type(JunctionType.XOR)

   process_payment = model.add_element(
       name="Process Payment",
       element_type=ArchiType.ApplicationService
   )

   # Exactly one payment method is chosen
   model.add_relationship(
       source=credit_card_path,
       target=payment_choice,
       relationship_type=RelationType.Influences
   )
   model.add_relationship(
       source=bank_transfer_path,
       target=payment_choice,
       relationship_type=RelationType.Influences
   )
   model.add_relationship(
       source=payment_choice,
       target=process_payment,
       relationship_type=RelationType.Influences
   )

Best Practices
~~~~~~~~~~~~~~

1. **Use junctions to simplify complex relationships**: Instead of drawing many individual relationships, use a junction to clarify the logical operation.

2. **Label junctions clearly**: Give junctions meaningful names (e.g., "All Approvals Met" instead of just "AND").

3. **Document the semantics**: If the AND/OR/XOR semantics are not obvious from context, add documentation to the junction element.

4. **Validate junction usage**: Ensure that the number of incoming and outgoing relationships makes logical sense for the junction type.

See Also
~~~~~~~~

- :doc:`../concepts` — Introduction to relationships and junctions
- :doc:`../architecture` — How pyArchimate organizes packages
- :doc:`../api/element` — Full Element API reference
- :doc:`../examples/styling_examples` — Code examples
