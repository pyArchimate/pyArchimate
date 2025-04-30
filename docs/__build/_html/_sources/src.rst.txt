pyArchimate Package
===================

It enables to:

* Read or write a file in Archimate and Archi Tool xml formats
* create new models
* Create, update and delete Archimate artefacts
* Create, update and delete diagrams
* Import files from ARIS AML format
* Export model's elements, properties & relationships to CSV

The following artefacts are implemented as per the metamodel here below:

* Model: a set of architecture concepts that relate together and their visual representation in views
* View:  a specific visualization of element and their conns in a diagram
* Element: architectural concepts of Archimate language
* Relationship: the architectural concept expressing the relation between two Elements
* Node: the visual representation of an Element in a View
* Connection: the visual representation of a Relationship in a View

.. toctree::
   :maxdepth: 4

   pyArchimate
   archiReader
   archimateReader
   arisAMLReader
   archiWriter
   archimateWriter
   csvWriter