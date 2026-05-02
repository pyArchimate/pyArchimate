pyArchimate Package
===================

It enables to:

* Read or write a file in Archimate and Archi Tool xml formats
* Create new models
* Create, update and delete Archimate artefacts
* Create, update and delete diagrams
* Import files from ARIS AML format
* Export model's elements, properties & relationships to CSV

The following artefacts are implemented as per the metamodel:

* :doc:`model` – a set of architecture concepts and their visual representations
* :doc:`view` – a specific visualization of elements and their connections in a diagram
* :doc:`element` – architectural concepts of the Archimate language
* :doc:`relationship` – the concept expressing the relation between two Elements
* ``Node`` – the visual representation of an Element in a View (see :doc:`view`)
* ``Connection`` – the visual representation of a Relationship in a View (see :doc:`view`)

See :doc:`modules` for the full API reference.