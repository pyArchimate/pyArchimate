:orphan:

Diagrams
========

The files in ``docs/diagrams`` are PlantUML sources that document the architecture of
pyArchimate. They include both classic UML views (class, component, object, deployment, etc.)
and derived C4-style diagrams that illustrate how the project is composed.

Available diagrams:

The rendered PNG artifacts live next to the PlantUML sources (``docs/diagrams/*.png``) and are overwritten each time you run ``scripts/render_diagrams.sh``. Including them in the docs allows the website to display the diagrams without requiring a PlantUML renderer on the client side.

``context.puml`` / ``c4_context.puml``
  Context diagram showing how pyArchimate integrates with external tooling, developers, and
  the ArchiMate standard.

.. image:: diagrams/c4_context.png
   :alt: Context diagram showing the integration points with external tooling, developers, and the ArchiMate standard.
   :align: center

.. image:: diagrams/context.png
   :alt: Context diagram showing the integration points with external tooling, developers, and the ArchiMate standard.
   :align: center

``package.puml`` / ``c4_container.puml``
  Container diagram showing how pyArchimate integrates with external tooling, developers, and
  the ArchiMate standard.

.. image:: diagrams/c4_container.png
   :alt: Container diagram showing the deployment structure of pyArchimate.
   :align: center

.. image:: diagrams/package.png
   :alt: Package diagram showing the modular structure of the pyArchimate project.
   :align: center

``component.puml`` / ``c4_component.puml``
  Component diagrams that highlight the major modules such as the model core, readers, and writers.

.. image:: diagrams/c4_component.png
   :alt: Component diagram showing the major modules of pyArchimate.
   :align: center

.. image:: diagrams/component.png
   :alt: Component diagram showing the major modules of pyArchimate.
   :align: center

``deployment.puml`` / ``c4_deployment.puml``
  Deployment diagrams describing the runtime environment, processing steps, and how the PlantUML
  renderer/slim server might be hosted.

.. image:: diagrams/c4_deployment.png
   :alt: Deployment diagram showing the runtime environment and processing steps.
   :align: center

.. image:: diagrams/deployment.png
   :alt: Deployment diagram showing the runtime environment and processing steps.
   :align: center

``class.puml`` / ``object.puml`` / ``composite.puml``
  UML views that sketch the static structure of `Model`, `Element`, `Relationship`, and the associated
  helper utilities.

.. image:: diagrams/class.png
   :alt: Class diagram showing Model, Element, Relationship, View, Node, and Connection relationships.
   :align: center

.. image:: diagrams/object.png
   :alt: Object diagram showing the dynamic interactions between instances of the classes.
   :align: center

.. image:: diagrams/composite.png
   :alt: Composite structure diagram showing the internal structure of complex elements.
   :align: center

``state.puml``
  State diagram illustrating the `Model` lifecycle as it moves from empty through populated, view ready, serialized, and invalid states when validations fail.

.. image:: diagrams/state.png
   :alt: State diagram for Model lifecycle transitions.
   :align: center

``sequence.puml``
  Sequence diagram depicting how the CLI/script invokes `Model.read`, how readers populate `Elements`/`Relationships`, and how writers serialize the resulting model.

.. image:: diagrams/sequence.png
   :alt: Sequence diagram showing the reader/writer interactions during a Model read/write cycle.
   :align: center

``activity.puml``
  Activity diagram of view construction: creating models, adding elements/relationships, building views, and writing outputs.

.. image:: diagrams/activity.png
   :alt: Activity diagram describing the view construction workflow.
   :align: center

``communication.puml``
  Communication diagram showing runtime message paths between `Model`, `Element`, `Relationship`, `View`, `Node`, and `Connection` during CRUD operations.

.. image:: diagrams/communication.png
   :alt: Communication diagram showing the collaboration of Model, View, Node, and Connection.
   :align: center

Rendering
---------

To regenerate the PNG artifacts locate the PlantUML renderer and run the helper script:

```
./scripts/render_diagrams.sh
```

The script encodes every PlantUML source, hits `${PLANTUML_SERVER:-https://www.plantuml.com/plantuml}`, follows redirects, and retries slow transfers so the loop can finish. Set `PLANTUML_SERVER` if you want to target a different host (for example `export PLANTUML_SERVER=http://host.containers.internal:8080`), otherwise it defaults to the public PlantUML service.

If you add or refactor diagrams, update this document with a short explanation of the new view and add the source file to the script so it continues to be rendered automatically.
