Architecture Overview
=====================

.. note::

   🔧 **Intermediate / Architecture** — Understand how pyArchimate is organized and where to hook in your own custom readers, writers, and validators.

Package Structure
~~~~~~~~~~~~~~~~~

PyArchimate is organized into functional packages, each with a specific responsibility:

``pyArchimate``
  **Main package**. Provides the public API through the shim module ``pyArchimate.pyArchimate``, which re-exports all commonly-used classes and enums.

``pyArchimate.model``
  **Core data structures**. Contains :py:class:`Model`, :py:class:`Element`, :py:class:`Relationship`, :py:class:`View`, :py:class:`Node`, and :py:class:`Connection` classes that form the in-memory representation of an ArchiMate model.

``pyArchimate.element`` / ``pyArchimate.relationship``
  **Type definitions**. :py:class:`ArchiType` and :py:class:`RelationType` enums define all supported element and relationship types per the ArchiMate specification.

``pyArchimate.readers``
  **Import implementations**. Contains reader classes for different file formats:

  - ``archimateReader`` — Native ArchiMate XML format (.archimate)
  - ``openGroupReader`` — OpenGroup XML exchange format
  - Custom readers can be registered for new formats

``pyArchimate.writers``
  **Export implementations**. Contains writer classes for different output formats:

  - ``archiWriter`` — Write to native ArchiMate XML format
  - ``archimateWriter`` — Alternative ArchiMate XML writer
  - Custom writers can be registered for new formats

``pyArchimate.validation``
  **Model validation**. Contains rules and validators for checking model consistency:

  - ``check_valid_relationship`` — Validate that a relationship type is allowed between two element types
  - ``checker_rules.yml`` — Configuration file defining what element types are valid in which layers and viewpoints

``pyArchimate.viewpoint``
  **Viewpoint definitions**. Contains standard ArchiMate viewpoint definitions (Business Process, Application Structure, Technology, etc.) and utilities for filtering elements by viewpoint.

``pyArchimate.helpers``
  **Utility functions**. Shared utilities for working with models, elements, and relationships (hierarchy operations, property management, etc.).

Layered Dependencies
~~~~~~~~~~~~~~~~~~~~

The architecture follows a layered dependency model:

1. **Core Layer**: ``model``, ``element``, ``relationship`` — fundamental data structures with no external dependencies beyond lxml for XML handling.

2. **Validation Layer**: ``validation`` — builds on core layer to enforce business rules and type constraints.

3. **Transformation Layer**: ``readers``, ``writers`` — builds on core layer to parse and generate file formats.

4. **Public API Layer**: ``pyArchimate`` (shim) — re-exports commonly-used classes and enums for convenience.

Each layer is independent, allowing you to:

- Use the core model in your own custom tools
- Replace the validation layer with custom rules
- Add new readers and writers without modifying existing code

Architecture Diagrams
~~~~~~~~~~~~~~~~~~~~~

The following diagrams illustrate pyArchimate's architecture from different perspectives:

.. include:: diagrams.rst

Extension Points
~~~~~~~~~~~~~~~~

PyArchimate is designed to be extended. The following sections explain where and how to add custom functionality.

**Custom Readers**

To add support for a new import format, create a reader class and register it in the ``MODEL_READER_REGISTRY``:

.. code-block:: python

   from pyArchimate.readers import MODEL_READER_REGISTRY

   class CustomReader:
       def read(self, filepath):
           # Parse file and return a Model instance
           pass

   MODEL_READER_REGISTRY['custom'] = CustomReader()

For detailed examples and patterns, see :doc:`guides/extending`.

**Custom Writers**

To add support for a new export format, extend the ``Writers`` enum and implement a writer class:

.. code-block:: python

   from pyArchimate.writers import Writers

   class CustomWriter:
       def write(self, model, filepath):
           # Serialize model to file
           pass

For detailed examples and patterns, see :doc:`guides/extending`.

**Custom Validation Rules**

You can extend model validation by adding custom rules to ``checker_rules.yml`` or by programmatically validating models using the public API.

For details, see :doc:`guides/extending`.

Related Documentation
~~~~~~~~~~~~~~~~~~~~~

- **Getting Started**: Quick setup and first example — :doc:`getting-started`
- **Core Concepts**: Elements, relationships, views, and viewpoints — :doc:`concepts`
- **Extending pyArchimate**: Custom readers, writers, and validators — :doc:`guides/extending`
- **Guides**:
  - :doc:`guides/element-hierarchy` — Organizing elements hierarchically
  - :doc:`guides/visual-styling` — Customizing diagram appearance
  - :doc:`guides/junction-types` — Logical junctions and operations
