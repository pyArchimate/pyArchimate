Viewpoints API
==============

.. note::

   ⚙️ **Advanced / API Reference** — Complete reference for working with ArchiMate viewpoints and viewpoint-related APIs.

Overview
~~~~~~~~

Viewpoints are standard perspectives on an ArchiMate model, each targeting a specific stakeholder group. PyArchimate provides tools to:

- Retrieve available viewpoints for a model
- Query which elements are valid in a specific viewpoint
- Assign elements to viewpoints
- Filter model views by viewpoint

The two main modules for viewpoint operations are:

- :py:mod:`pyArchimate.viewpoint` — Core viewpoint definitions and utilities
- :py:mod:`pyArchimate.viewpoint_registry` — Registry of all standard ArchiMate viewpoints

Standard Viewpoints
~~~~~~~~~~~~~~~~~~~

ArchiMate defines 13 standard viewpoints. Each viewpoint focuses on a specific architectural perspective:

**Business Layer Viewpoints**

``Business Process Viewpoint``
  Shows business processes and how they relate. Audience: business analysts, process owners.

``Business Function Viewpoint``
  Displays business functions and their responsibilities. Audience: business strategists.

``Business Interaction Viewpoint``
  Represents interactions between business actors. Audience: organization stakeholders.

**Application Layer Viewpoints**

``Application Structure Viewpoint``
  Shows application components and their relationships. Audience: application architects.

``Application Usage Viewpoint``
  Displays how applications are used by business processes. Audience: application users, business analysts.

**Technology Layer Viewpoints**

``Technology Structure Viewpoint``
  Shows infrastructure components and their relationships. Audience: infrastructure architects.

``Technology Usage Viewpoint``
  Displays how technology supports applications. Audience: infrastructure operators.

**Cross-Layer Viewpoints**

``Business Process Realization Viewpoint``
  Maps business processes to applications and technology. Audience: enterprise architects.

``Business Function Realization Viewpoint``
  Maps business functions to applications. Audience: business and application architects.

``Service Realization Viewpoint``
  Shows how services are realized by applications and infrastructure. Audience: service architects.

**Stakeholder-Specific Viewpoints**

``Implementation and Deployment Viewpoint``
  Shows implementation and deployment details. Audience: project managers, deployment engineers.

``Motivation Viewpoint``
  Displays business drivers, goals, and requirements. Audience: business strategists, stakeholders.

**Migration and Implementation Viewpoint**

``Migration and Implementation Viewpoint``
  Shows migration paths and transformation details. Audience: program managers, transformation leads.

API Reference
~~~~~~~~~~~~~

.. automodule:: pyArchimate.viewpoint
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: pyArchimate.viewpoint_registry
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
~~~~~~~~~~~~~~

**Get all viewpoints for a model**

.. code-block:: python

   from pyArchimate import Model

   model = Model.read("mymodel.archimate")

   # Get all available viewpoints
   viewpoints = model.get_viewpoints()
   for viewpoint in viewpoints:
       print(f"Viewpoint: {viewpoint.name} ({viewpoint.slug})")

**Get elements valid in a viewpoint**

.. code-block:: python

   from pyArchimate.viewpoint_registry import VIEWPOINTS

   # Access Business Process viewpoint
   bp_viewpoint = VIEWPOINTS['business-process']

   # Get elements that are valid in this viewpoint
   valid_elements = bp_viewpoint.get_valid_elements()
   print(f"Valid elements: {[e.name for e in valid_elements]}")

**Assign an element to a viewpoint**

.. code-block:: python

   element = model.get_element("elem_id")

   # Assign to Business Process viewpoint
   element.assign_viewpoint('business-process')

**Filter elements by viewpoint**

.. code-block:: python

   # Get all elements valid in Technology Structure viewpoint
   tech_elements = model.get_elements_by_viewpoint('technology-structure')

   print(f"Technology elements: {[e.name for e in tech_elements]}")

**Validate element in viewpoint**

.. code-block:: python

   from pyArchimate import ArchiType
   from pyArchimate.viewpoint_registry import is_valid_in_viewpoint

   # Check if BusinessProcess is valid in Business Process viewpoint
   valid = is_valid_in_viewpoint(
       ArchiType.BusinessProcess,
       'business-process'
   )
   print(f"Valid: {valid}")

New to This Topic?
~~~~~~~~~~~~~~~~~~

If you're new to viewpoints, start with:

- :doc:`../concepts` — Introduction to viewpoints and their role in ArchiMate
- :doc:`../guides/element-hierarchy` — Understanding element organization
- :doc:`../getting-started` — Getting started with pyArchimate

See Also
~~~~~~~~

- :doc:`element` — Element API reference
- :doc:`model` — Model API reference
- :doc:`../architecture` — Package structure and architecture
