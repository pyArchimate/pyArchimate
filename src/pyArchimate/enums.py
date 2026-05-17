"""
Enumerations for Archimate model and visualization.

This module contains all enumeration types used throughout the pyArchimate library,
including element types, relationship types, and UI-related enumerations.

No external pyArchimate imports - this is a Layer 1 base module.
"""

from enum import Enum


class Writers(Enum):
    """
    Enumeration for Writers drivers
    """

    archi = 0
    csv = 1
    archimate = 2


class Readers(Enum):
    """
    Enumeration for Readers drivers

    Note: ARIS format (aris = 1) is deprecated and will be removed in a future version.
    Use archi (Archi native) or archimate (OpenGroup Exchange format) instead.
    """

    archi = 0
    aris = 1  # DEPRECATED: ARIS format support will be removed
    archimate = 2


class AccessType(str, Enum):
    """
    Enumeration of Access Relationship types
    """

    Access = "Access"
    Read = "Read"
    Write = "Write"
    ReadWrite = "ReadWrite"


class TextPosition(str, Enum):
    """
    Enumaration for Text vertical position
    """

    Top = "0"
    Middle = "1"
    Bottom = "2"


class TextAlignment(str, Enum):
    """
    Enumeration for text horizontal position
    """

    Left = "0"
    Center = "1"
    Right = "2"


class ArchiType(str, Enum):
    """Enumeration of ArchiMate element and relationship types.

    Members cover all ArchiMate 3.x layers: Strategy, Motivation, Business,
    Application, Technology, Physical, and Implementation & Migration.

    Business layer elements include: BusinessActor, BusinessRole,
    BusinessCollaboration, BusinessInterface, BusinessProcess,
    BusinessFunction, BusinessInteraction, BusinessEvent, BusinessService,
    BusinessObject, Contract, Representation, and Product.
    """

    # Business Layer
    BusinessActor = "BusinessActor"
    BusinessRole = "BusinessRole"
    BusinessCollaboration = "BusinessCollaboration"
    BusinessInterface = "BusinessInterface"
    BusinessProcess = "BusinessProcess"
    BusinessFunction = "BusinessFunction"
    BusinessInteraction = "BusinessInteraction"
    BusinessEvent = "BusinessEvent"
    BusinessService = "BusinessService"
    BusinessObject = "BusinessObject"
    Contract = "Contract"
    Representation = "Representation"
    Product = "Product"

    # Application Layer

    ApplicationComponent = "ApplicationComponent"
    ApplicationInterface = "ApplicationInterface"
    ApplicationInteraction = "ApplicationInteraction"
    ApplicationCollaboration = "ApplicationCollaboration"
    ApplicationFunction = "ApplicationFunction"
    ApplicationProcess = "ApplicationProcess"
    ApplicationEvent = "ApplicationEvent"
    ApplicationService = "ApplicationService"
    DataObject = "DataObject"

    # Technology layer

    Node = "Node"
    Device = "Device"
    Path = "Path"
    CommunicationNetwork = "CommunicationNetwork"
    SystemSoftware = "SystemSoftware"
    TechnologyCollaboration = "TechnologyCollaboration"
    TechnologyInterface = "TechnologyInterface"
    TechnologyFunction = "TechnologyFunction"
    TechnologyProcess = "TechnologyProcess"
    TechnologyInteraction = "TechnologyInteraction"
    TechnologyEvent = "TechnologyEvent"
    TechnologyService = "TechnologyService"
    Artifact = "Artifact"

    # Physical elements

    Equipment = "Equipment"
    Facility = "Facility"
    DistributionNetwork = "DistributionNetwork"
    Material = "Material"

    #  Motivation

    Stakeholder = "Stakeholder"
    Driver = "Driver"
    Assessment = "Assessment"
    Goal = "Goal"
    Outcome = "Outcome"
    Principle = "Principle"
    Requirement = "Requirement"
    Constraint = "Constraint"
    Meaning = "Meaning"
    Value = "Value"

    # Strategy

    Resource = "Resource"
    Capability = "Capability"
    CourseOfAction = "CourseOfAction"
    ValueStream = "ValueStream"

    # Implementation & Migration

    WorkPackage = "WorkPackage"
    Deliverable = "Deliverable"
    ImplementationEvent = "ImplementationEvent"
    Plateau = "Plateau"
    Gap = "Gap"

    # Other

    Grouping = "Grouping"
    Location = "Location"

    # Junction

    Junction = "Junction"
    OrJunction = "OrJunction"
    AndJunction = "AndJunction"

    # Relationships

    Association = "Association"
    Assignment = "Assignment"
    Realization = "Realization"
    Serving = "Serving"
    Composition = "Composition"
    Aggregation = "Aggregation"
    Access = "Access"
    Influence = "Influence"
    Triggering = "Triggering"
    Flow = "Flow"
    Specialization = "Specialization"

    # Special
    View = "View"
