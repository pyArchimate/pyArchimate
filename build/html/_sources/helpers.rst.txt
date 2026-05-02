Helpers
=======

Utility functions and logging configuration used by the core modules.

Diagram helpers
---------------

Thin wrappers that delegate node/connection creation to ``Model``/``View``
instances.

.. automodule:: pyArchimate.helpers.diagram
   :members:
   :undoc-members:
   :show-inheritance:

Property helpers
----------------

Wrappers that delegate ``embed_props`` / ``expand_props`` and validation
calls to the ``Model`` implementation.

.. automodule:: pyArchimate.helpers.properties
   :members:
   :undoc-members:
   :show-inheritance:

Logging helpers
---------------

Thin configuration layer around the standard :mod:`logging` module: sets a
consistent formatter and exposes ``log_set_level``, ``log_to_file``, and
``log_to_stderr``.

.. automodule:: pyArchimate.helpers.logging
   :members:
   :undoc-members:
   :show-inheritance:
