Getting Started
===============

.. note::

   ℹ️ **Basic Usage** — Start here to create your first pyArchimate model in under 2 minutes.

Installation
~~~~~~~~~~~~

Install pyArchimate via pip:

.. code-block:: bash

   pip install pyArchimate

Minimal Working Example
~~~~~~~~~~~~~~~~~~~~~~~

Create your first ArchiMate model with this simple script:

.. testcode::

   from pyArchimate import Model, ArchiType

   # Create a new model
   model = Model(name="My First Model")

   # Add elements (using model.add: element_type, name)
   business = model.add(ArchiType.BusinessProcess, "Business Process")
   app = model.add(ArchiType.ApplicationService, "Application Service")

   # Create a relationship (rel_type as string, e.g. 'Serving')
   model.add_relationship("Serving", source=business, target=app)

   # Confirm the model has the expected elements
   print(f"Model '{model.name}' has {len(model.elements)} elements")

.. testoutput::

   Model 'My First Model' has 2 elements

What's Next?
~~~~~~~~~~~~

- **Learn Core Concepts**: Explore :doc:`concepts` to understand the building blocks of ArchiMate models (elements, relationships, layers, and viewpoints).

- **Follow the Tutorial**: Work through the interactive tutorial in :doc:`tutorial/tutorial` with step-by-step examples and best practices.

- **Understand the Architecture**: For information on how pyArchimate is structured internally, see :doc:`architecture`.

- **Browse the API Reference**: Once you're familiar with the basics, explore the full API in the :doc:`modules` section.
