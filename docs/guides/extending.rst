Extending pyArchimate
=====================

.. note::

   🔧 **Intermediate / Architecture** — Learn how to extend pyArchimate with custom readers, writers, properties, and profiles.

Introduction
~~~~~~~~~~~~

PyArchimate is designed as an extensible platform. Rather than modifying the core library, you can hook into extension points to:

- Add support for new file formats (custom readers)
- Export to new formats (custom writers)
- Extend models with domain-specific properties
- Integrate with your own workflows

This guide explains the patterns and APIs for each extension point.

Custom Readers
~~~~~~~~~~~~~~

**What is a reader?**

A reader is a class that parses a file in a specific format and returns a :py:class:`Model` instance. PyArchimate includes built-in readers for:

- ArchiMate XML format (.archimate files)
- OpenGroup XML exchange format

**How to create a custom reader**

Create a class with a ``read(filepath: str) -> Model`` method:

.. code-block:: python

   from pyArchimate import Model
   from pyArchimate.readers import MODEL_READER_REGISTRY

   class CSVReader:
       """Read a simple CSV format into a Model."""
       def read(self, filepath: str) -> Model:
           model = Model(name="From CSV")
           # Parse CSV and populate model
           with open(filepath) as f:
               for line in f:
                   # Parse line and add elements/relationships
                   pass
           return model

**How to register a custom reader**

Register your reader in the ``MODEL_READER_REGISTRY`` dictionary:

.. code-block:: python

   from pyArchimate.readers import MODEL_READER_REGISTRY

   MODEL_READER_REGISTRY['csv'] = CSVReader()

**Using your custom reader**

Once registered, you can read files using the extension key:

.. code-block:: python

   from pyArchimate import Model

   model = Model.read("mymodel.csv", reader_key="csv")

Custom Writers
~~~~~~~~~~~~~~

**What is a writer?**

A writer is a class that exports a :py:class:`Model` to a specific file format. PyArchimate includes built-in writers for:

- ArchiMate XML format (.archimate files)

**How to create a custom writer**

Create a class with a ``write(model: Model, filepath: str) -> None`` method:

.. code-block:: python

   from pyArchimate import Model

   class JSONWriter:
       """Write a Model to JSON format."""
       def write(self, model: Model, filepath: str) -> None:
           import json
           data = {
               "name": model.name,
               "elements": [
                   {"name": e.name, "type": e.element_type.value}
                   for e in model.elements
               ],
           }
           with open(filepath, 'w') as f:
               json.dump(data, f, indent=2)

**How to use a custom writer**

Pass your writer instance to the model's write method:

.. code-block:: python

   model = Model(name="My Model")
   # ... add elements ...

   writer = JSONWriter()
   writer.write(model, "output.json")

**Registering writers in the Writers enum** (optional)

If you want to standardize your writer as part of the library, you can extend the ``Writers`` enum and add it to the model's write workflow. Contact the pyArchimate maintainers for guidance on this advanced pattern.

Custom Properties and Profiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What are properties?**

Elements and relationships support arbitrary **properties** — key-value pairs for metadata beyond standard attributes. Properties allow you to attach domain-specific information without modifying the core model.

**How to set properties**

.. code-block:: python

   from pyArchimate import Model, ArchiType

   model = Model(name="My Model")
   element = model.add_element(
       name="Critical System",
       element_type=ArchiType.ApplicationService
   )

   # Set custom properties
   element.set_property("owner", "John Doe")
   element.set_property("cost", "500000")
   element.set_property("risk_level", "high")

**How to get properties**

.. code-block:: python

   owner = element.get_property("owner")
   cost = element.get_property("cost")

**How to preserve properties during round-trip**

When you read and write a model, properties are preserved in the native ArchiMate XML format. For custom formats, ensure your reader and writer handle the properties dictionary:

.. code-block:: python

   # In your custom reader
   element.set_property("custom_field", value)

   # In your custom writer
   for key, value in element.get_properties().items():
       # Serialize property to your format

Logging Integration
~~~~~~~~~~~~~~~~~~~

PyArchimate uses Python's standard ``logging`` module. To debug your extensions, configure logging:

.. code-block:: python

   import logging

   # Set pyArchimate's logger to DEBUG level
   logging.getLogger('pyArchimate').setLevel(logging.DEBUG)

   # Add a console handler to see log output
   handler = logging.StreamHandler()
   handler.setLevel(logging.DEBUG)
   formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
   handler.setFormatter(formatter)
   logging.getLogger('pyArchimate').addHandler(handler)

**Common logging points:**

- Model.read() logs the reader and file being loaded
- Model.write() logs the writer and file being written
- Element and relationship operations log validation results
- Readers/writers log parsing and serialization steps

Plugin Architecture Notes
~~~~~~~~~~~~~~~~~~~~~~~~~

**Current plugin model**

PyArchimate uses a registry-based plugin model:

- Readers are registered in ``MODEL_READER_REGISTRY`` (a dictionary)
- Writers are added as writer class instances
- Validation rules are defined in ``checker_rules.yml``

**Extending the validation layer**

To add custom validation rules, you can:

1. Modify ``checker_rules.yml`` (for changes to allowed element/relationship types in specific contexts)
2. Programmatically call validation functions and add your own checks

Example:

.. code-block:: python

   from pyArchimate import Model
   from pyArchimate.validation import check_valid_relationship

   model = Model.read("mymodel.archimate")

   # Add custom validation
   for relationship in model.relationships:
       if relationship.documentation is None:
           print(f"Warning: Relationship {relationship.id} has no documentation")

**Future plugin roadmap**

The pyArchimate team plans to support:

- Event hooks for model changes (e.g., on_element_added, on_write)
- Custom viewpoint definitions
- Plugin discovery and dynamic loading

Check the project repository for the latest information on upcoming plugin features.

See Also
~~~~~~~~

- :doc:`../architecture` — How pyArchimate is organized
- :doc:`element-hierarchy` — Working with hierarchies
- :doc:`visual-styling` — Customizing diagram appearance
- :doc:`../getting-started` — Quick start guide
