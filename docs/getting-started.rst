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

.. code-block:: python

   from pyArchimate import (
       Model,
       ArchiType,
       RelationType,
   )

   # Create a new model
   model = Model(name="My First Model")

   # Add some elements
   business = model.add_element(
       name="Business Process",
       element_type=ArchiType.BusinessProcess,
   )
   app = model.add_element(
       name="Application Service",
       element_type=ArchiType.ApplicationService,
   )

   # Create a relationship
   model.add_relationship(
       source=business,
       target=app,
       relationship_type=RelationType.ServesBy,
   )

   # Write to file
   model.write("my_model.archimate")
   print("Model saved to my_model.archimate")

What's Next?
~~~~~~~~~~~~

- **Learn Core Concepts**: Explore :doc:`concepts` to understand the building blocks of ArchiMate models (elements, relationships, layers, and viewpoints).

- **Follow the Tutorial**: Work through the interactive tutorial in :doc:`tutorial/tutorial` with step-by-step examples and best practices.

- **Understand the Architecture**: For information on how pyArchimate is structured internally, see :doc:`architecture`.

- **Browse the API Reference**: Once you're familiar with the basics, explore the full API in the :doc:`modules` section.
