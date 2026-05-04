Enumerations
============

All enumeration types used throughout pyArchimate are defined here, including
element/relationship types (``ArchiType``), I/O driver selectors (``Readers``,
``Writers``), and UI-related enumerations (``TextAlignment``,
``TextPosition``, ``AccessType``).

.. note::

   **Deprecated enum value**: ``Readers.aris`` (value ``1``) is deprecated and will be removed
   in a future version. Use ``Readers.archi`` (Archi native format) or ``Readers.archimate``
   (OpenGroup Exchange format) instead.

   .. deprecated:: 1.4.0

      ``Readers.aris`` — ARIS format reader support is deprecated. Migrate to
      ``Readers.archi`` or ``Readers.archimate``.

Module contents
---------------

.. automodule:: pyArchimate.enums
   :members:
   :undoc-members:
   :show-inheritance:
