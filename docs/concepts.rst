Core Concepts
=============

.. note::

   ℹ️ **Basic Usage** — Understand the fundamental building blocks of ArchiMate models.

The Three ArchiMate Layers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

ArchiMate is organized around three layers of architecture, each serving different stakeholders:

**Business Layer**
  Business processes and organization. Focus: Processes, roles, functions, interactions.

**Application Layer**
  Software systems and services. Focus: Applications, components, services.

**Technology Layer**
  Infrastructure and platforms. Focus: Infrastructure, devices, networks.

Elements
~~~~~~~~

An **Element** is a building block in your ArchiMate model. Each element has:

- A **name** identifying it uniquely
- An **element type** (see :py:class:`pyArchimate.ArchiType`)
- Optional **properties** for metadata
- Optional **visual styling** (colors, line styles)

PyArchimate defines all ArchiMate element types via the :py:class:`pyArchimate.ArchiType` enum. For example:

- ``ArchiType.BusinessProcess`` — a business-level process
- ``ArchiType.ApplicationService`` — an application-level service
- ``ArchiType.TechnologyService`` — a technology-level service

.. note::

   In pyArchimate, you access element types via ``ArchiType.<name>`` (e.g., ``ArchiType.BusinessRole``). All standard ArchiMate elements are supported. The library also provides a shim module ``pyArchimate.pyArchimate`` that re-exports common elements for convenience.

Relationships
~~~~~~~~~~~~~

A **Relationship** connects two elements, expressing how they interact or relate. Each relationship has:

- A **source** element
- A **target** element
- A **relationship type** (see :py:class:`pyArchimate.RelationType`)
- Optional **properties** (e.g., documentation)

Common relationship types include:

``ServesBy``
  Source serves the target.

``AssignedTo``
  Source is assigned to target.

``UsedBy``
  Source is used by target.

``TriggerBy``
  Source is triggered by target.

``Influences``
  Source influences the target (with optional strength: AND, OR, XOR).

``ComposedOf``
  Source is composed of the target (parent-child hierarchy).

``RealisedBy``
  Source is realised by target.

``AggregatedBy``
  Source is aggregated by target.

For a complete list and validation rules, see :py:func:`pyArchimate.check_valid_relationship`.

Views and Diagrams
~~~~~~~~~~~~~~~~~~

A **View** is a selective representation of your model, showing a subset of elements and relationships. Each view has:

- A **name** and optional **documentation**
- A set of **nodes** (visual representations of elements)
- A set of **connections** (visual representations of relationships)

Views allow you to focus on specific aspects of your architecture without overwhelming readers with the full model.

Viewpoints
~~~~~~~~~~

A **Viewpoint** is a standard perspective for a specific stakeholder group. ArchiMate defines 13 standard viewpoints, each with a specific purpose:

``Business Process Viewpoint``
  Shows business processes and how they relate. Audience: process stakeholders.

``Business Function Viewpoint``
  Displays business functions and their responsibilities. Audience: business analysts.

``Business Interaction Viewpoint``
  Represents interactions between business actors. Audience: cross-organization stakeholders.

``Application Structure Viewpoint``
  Shows application components and their relationships. Audience: application architects.

``Application Usage Viewpoint``
  Displays how applications are used by business processes. Audience: application stakeholders.

``Technology Structure Viewpoint``
  Shows infrastructure components and their relationships. Audience: infrastructure architects.

``Technology Usage Viewpoint``
  Displays how technology supports applications. Audience: technology stakeholders.

``Business Process Realization Viewpoint``
  Maps business processes to applications and technology. Audience: enterprise architects.

``Business Function Realization Viewpoint``
  Maps business functions to applications. Audience: architects.

``Service Realization Viewpoint``
  Shows how services are realized by applications and infrastructure. Audience: service architects.

``Implementation and Deployment Viewpoint``
  Shows implementation and deployment details. Audience: project managers, deployment engineers.

``Motivation Viewpoint``
  Displays business drivers, goals, and requirements. Audience: business strategists.

``Migration and Implementation Viewpoint``
  Shows migration paths and transformation details. Audience: transformation leads.

Each element type is valid in certain viewpoints. Viewpoints help organize and validate your model. For the full API reference and usage examples, see :doc:`api/viewpoints`.

Properties and Metadata
~~~~~~~~~~~~~~~~~~~~~~~

Both elements and relationships support **properties** — key-value pairs that store metadata beyond the standard attributes. Properties allow you to:

- Attach domain-specific information
- Track custom attributes (e.g., owner, cost, risk level)
- Preserve round-trip metadata during import/export

Set and retrieve properties using the element or relationship API:

.. code-block:: python

   # Set a property
   element.set_property("owner", "John Doe")
   element.set_property("cost", "100000")

   # Get a property
   owner = element.get_property("owner")

Hierarchies
~~~~~~~~~~~

Elements can be organized into **parent-child hierarchies** using composite relationships. This allows you to:

- Group related elements
- Represent sub-processes or sub-services
- Limit nesting depth (ArchiMate typically restricts to 5 levels)

For details on creating and querying hierarchies, see :doc:`guides/element-hierarchy`.

Visual Styling
~~~~~~~~~~~~~~

You can customize how elements appear in diagrams by setting:

- **Fill color** (hex or named)
- **Line color** (hex or named)
- **Line width** (stroke thickness)
- **Transparency** (alpha value)

Models can also define a **model-wide theme** (default visual style). For examples, see :doc:`guides/visual-styling`.

Junction Types
~~~~~~~~~~~~~~

**Junctions** are special elements used to represent logical operations (AND, OR, XOR) in ArchiMate models. Use them to show how multiple influences combine.

For details and examples, see :doc:`guides/junction-types`.
